"""User-facing routes: landing, live map, booking, payment, ticket, SOS."""

import io
import math
import secrets
from datetime import datetime, timedelta

import qrcode
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, jsonify, send_file, abort)
from ..db import get_db, query, execute, execute_rowcount
from ..security import login_required, load_current_user

bp = Blueprint("main", __name__)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _levels():
    return query("SELECT id, code, name, floor_order FROM levels ORDER BY floor_order")


def _pricing_map():
    rows = query("SELECT vehicle_type, hourly_rate, charging_rate FROM pricing")
    return {r["vehicle_type"]: r for r in rows}


def _slots_for_level(level_id=None):
    sql = """SELECT s.*, l.code AS level_code FROM slots s
             JOIN levels l ON l.id = s.level_id
             WHERE s.is_active = 1"""
    params = ()
    if level_id:
        sql += " AND s.level_id = %s"
        params = (level_id,)
    sql += " ORDER BY l.floor_order, s.code"
    return query(sql, params)


def _live_status_map():
    """slot_id -> 'reserved' if an active/upcoming booking overlaps 'now'."""
    now = datetime.now()
    rows = query("""SELECT slot_id FROM bookings
                    WHERE status IN ('booked','active')
                      AND start_ts <= %s AND end_ts > %s""", (now, now))
    return {r["slot_id"] for r in rows}


def _fee_for(start, end, vehicle_type, charging=False):
    """Ceil to next hour with a 1-hour minimum."""
    secs = max(0, (end - start).total_seconds())
    hours = max(1, math.ceil(secs / 3600.0))
    rates = _pricing_map()
    row = rates.get(vehicle_type) or {"hourly_rate": 0, "charging_rate": 0}
    rate = float(row["hourly_rate"])
    charge_rate = float(row["charging_rate"]) if charging else 0.0
    base = hours * rate
    extra = hours * charge_rate
    return {"hours": hours, "rate": rate, "charge_rate": charge_rate,
            "base": base, "extra": extra, "total": base + extra}


def _parse_dt(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M")


def _walk_hint(slot_code, level_code):
    digits = "".join(c for c in slot_code if c.isdigit())
    try:
        num = int(digits or 0)
    except ValueError:
        num = 0
    if num <= 6:
        row_text = "first row after the boom barrier"
    elif num <= 12:
        row_text = "second row, past the EV bays"
    elif num <= 18:
        row_text = "third row, mid-lot"
    else:
        row_text = "last row, along the rear wall"
    level_txt = "on the ground floor" if level_code == "G" else f"in {level_code}"
    return (f"Enter at the main gate, keep left, and take the ramp {level_txt}. "
            f"Your bay is in the {row_text}, marked {slot_code}.")


# ---------------------------------------------------------------------------
# landing / public availability
# ---------------------------------------------------------------------------

@bp.route("/")
def index():
    total = query("SELECT COUNT(*) c FROM slots WHERE is_active=1", one=True)["c"]
    taken_ids = _live_status_map()
    occupied = query("SELECT COUNT(*) c FROM slots WHERE is_active=1 AND status='occupied'",
                     one=True)["c"]
    return render_template("main/index.html",
                           total=total,
                           occupied=occupied + len(taken_ids),
                           available=max(0, total - occupied - len(taken_ids)),
                           levels=_levels())


@bp.route("/availability")
def availability_public():
    return render_template("main/availability.html", levels=_levels())


# ---------------------------------------------------------------------------
# JSON API for the live map
# ---------------------------------------------------------------------------

@bp.route("/api/slots")
def api_slots():
    level_id = request.args.get("level_id", type=int)
    live = _live_status_map()
    rows = _slots_for_level(level_id)
    out = []
    for s in rows:
        status = s["status"]
        if status == "available" and s["id"] in live:
            status = "reserved"
        out.append({"id": s["id"], "code": s["code"], "level": s["level_code"],
                    "slot_type": s["slot_type"], "vehicle_type": s["vehicle_type"],
                    "pos_x": s["pos_x"], "pos_y": s["pos_y"],
                    "status": status, "note": s["note"]})
    return jsonify({"slots": out})


@bp.route("/api/fee-estimate", methods=["POST"])
@login_required
def api_fee_estimate():
    data = request.get_json(silent=True) or {}
    try:
        start = _parse_dt(data.get("start_ts"))
        end = _parse_dt(data.get("end_ts"))
    except (TypeError, ValueError):
        return jsonify({"error": "Please pick valid start and end times."}), 400
    if end <= start:
        return jsonify({"error": "End time must be after start time."}), 400
    fee = _fee_for(start, end, data.get("vehicle_type", "car"),
                   bool(data.get("charging")))
    return jsonify(fee)


# ---------------------------------------------------------------------------
# booking
# ---------------------------------------------------------------------------

@bp.route("/book")
@login_required
def book():
    return render_template("main/book.html", levels=_levels())


@bp.route("/book", methods=["POST"])
@login_required
def book_post():
    user = load_current_user()
    slot_id       = request.form.get("slot_id", type=int)
    vehicle_type  = request.form.get("vehicle_type") or "car"
    vehicle_plate = (request.form.get("vehicle_plate") or "").strip().upper()
    start_s       = request.form.get("start_ts")
    end_s         = request.form.get("end_ts")
    charger       = request.form.get("charger_type") or "none"
    charging      = bool(request.form.get("charging_addon"))

    errors = {}
    if not slot_id:
        errors["slot_id"] = "Pick a slot on the map."
    if vehicle_type not in ("car", "bike", "scooter", "ev_car"):
        errors["vehicle_type"] = "Unknown vehicle type."
    if len(vehicle_plate) < 6:
        errors["vehicle_plate"] = "Enter a valid number plate, e.g. KA-01-AB-1234."

    start = end = None
    try:
        start = _parse_dt(start_s)
        end = _parse_dt(end_s)
        if end <= start:
            raise ValueError
    except (TypeError, ValueError):
        errors["time"] = "Please pick valid start and end times."

    if start and end and (end - start).total_seconds() > 24 * 3600:
        errors["time"] = "Bookings are limited to 24 hours."

    if errors:
        for v in errors.values():
            flash(v, "err")
        return redirect(url_for("main.book"))

    slot = query("SELECT * FROM slots WHERE id=%s AND is_active=1",
                 (slot_id,), one=True)
    if not slot:
        flash("That slot is no longer available.", "err")
        return redirect(url_for("main.book"))

    if slot["slot_type"] == "ev":
        if charger not in ("ac", "dc"):
            charger = "ac"
    else:
        charger = "none"
        charging = False

    # ---- transaction: lock the slot's overlapping bookings, then insert ----
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""SELECT id FROM bookings
                           WHERE slot_id = %s
                             AND status IN ('booked','active')
                             AND start_ts < %s AND end_ts > %s
                           FOR UPDATE""", (slot_id, end, start))
            if cur.fetchone():
                db.rollback()
                flash("Someone just took that slot for those hours. "
                      "Please choose another.", "err")
                return redirect(url_for("main.book"))

            fee = _fee_for(start, end, vehicle_type, charging)
            reference = "SPK-" + str(secrets.randbelow(900000) + 100000)

            cur.execute("""INSERT INTO bookings
                (reference, user_id, slot_id, vehicle_plate, vehicle_type,
                 start_ts, end_ts, status, charger_type, charging_addon,
                 amount_estimate)
                VALUES (%s,%s,%s,%s,%s,%s,%s,'booked',%s,%s,%s)""",
                (reference, user["id"], slot_id, vehicle_plate, vehicle_type,
                 start, end, charger, 1 if charging else 0, fee["total"]))
            booking_id = cur.lastrowid
        db.commit()
    except Exception:
        db.rollback()
        raise

    flash(f"Your spot is held. Booking {reference} is waiting for payment.", "ok")
    return redirect(url_for("main.payment", booking_id=booking_id))


# ---------------------------------------------------------------------------
# payment
# ---------------------------------------------------------------------------

@bp.route("/payment/<int:booking_id>", methods=["GET", "POST"])
@login_required
def payment(booking_id):
    user = load_current_user()
    booking = query("""SELECT b.*, s.code AS slot_code, s.slot_type,
                              l.code AS level_code, l.name AS level_name
                       FROM bookings b
                       JOIN slots s ON s.id = b.slot_id
                       JOIN levels l ON l.id = s.level_id
                       WHERE b.id = %s AND b.user_id = %s""",
                    (booking_id, user["id"]), one=True)
    if not booking:
        abort(404)

    if request.method == "POST":
        method = request.form.get("method") or "upi"
        if method not in ("upi", "card", "exit"):
            method = "upi"
        txn = "TXN-" + secrets.token_hex(4).upper()
        status = "pending" if method == "exit" else "paid"
        execute("""INSERT INTO payments
                   (booking_id, amount, method, status, txn_ref)
                   VALUES (%s,%s,%s,%s,%s)""",
                (booking_id, booking["amount_estimate"], method, status, txn))
        return redirect(url_for("main.ticket", booking_id=booking_id))

    return render_template("main/payment.html", booking=booking)


# ---------------------------------------------------------------------------
# printable ticket
# ---------------------------------------------------------------------------

@bp.route("/ticket/<int:booking_id>")
@login_required
def ticket(booking_id):
    user = load_current_user()
    booking = query("""SELECT b.*, s.code AS slot_code, s.slot_type, s.note,
                              l.code AS level_code, l.name AS level_name
                       FROM bookings b
                       JOIN slots s ON s.id = b.slot_id
                       JOIN levels l ON l.id = s.level_id
                       WHERE b.id = %s AND b.user_id = %s""",
                    (booking_id, user["id"]), one=True)
    if not booking:
        abort(404)
    payment = query("""SELECT * FROM payments WHERE booking_id = %s
                       ORDER BY id DESC LIMIT 1""", (booking_id,), one=True)
    hint = _walk_hint(booking["slot_code"], booking["level_code"])
    return render_template("main/ticket.html",
                           booking=booking, payment=payment, hint=hint)


@bp.route("/ticket/<int:booking_id>/qr.png")
@login_required
def ticket_qr(booking_id):
    user = load_current_user()
    row = query("SELECT reference FROM bookings WHERE id=%s AND user_id=%s",
                (booking_id, user["id"]), one=True)
    if not row:
        abort(404)
    payload = (url_for("main.ticket", booking_id=booking_id, _external=True)
               + "?ref=" + row["reference"])
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


# ---------------------------------------------------------------------------
# my bookings
# ---------------------------------------------------------------------------

@bp.route("/bookings")
@login_required
def my_bookings():
    user = load_current_user()
    now = datetime.now()
    upcoming = query("""SELECT b.*, s.code AS slot_code, l.code AS level_code
                        FROM bookings b
                        JOIN slots s ON s.id = b.slot_id
                        JOIN levels l ON l.id = s.level_id
                        WHERE b.user_id = %s AND b.status = 'booked'
                          AND b.start_ts >= %s
                        ORDER BY b.start_ts ASC""", (user["id"], now))
    active = query("""SELECT b.*, s.code AS slot_code, l.code AS level_code
                      FROM bookings b
                      JOIN slots s ON s.id = b.slot_id
                      JOIN levels l ON l.id = s.level_id
                      WHERE b.user_id = %s AND b.status = 'active'
                      ORDER BY b.start_ts DESC""", (user["id"],))
    past = query("""SELECT b.*, s.code AS slot_code, l.code AS level_code
                    FROM bookings b
                    JOIN slots s ON s.id = b.slot_id
                    JOIN levels l ON l.id = s.level_id
                    WHERE b.user_id = %s AND b.status IN ('completed','cancelled')
                    ORDER BY b.start_ts DESC LIMIT 30""", (user["id"],))
    return render_template("main/my_bookings.html",
                           upcoming=upcoming, active=active, past=past)


@bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    user = load_current_user()
    db = get_db()
    with db.cursor() as cur:
        cur.execute("""SELECT status FROM bookings
                       WHERE id=%s AND user_id=%s FOR UPDATE""",
                    (booking_id, user["id"]))
        row = cur.fetchone()
        if not row or row["status"] != "booked":
            db.rollback()
            flash("That booking cannot be cancelled.", "err")
            return redirect(url_for("main.my_bookings"))
        cur.execute("UPDATE bookings SET status='cancelled' WHERE id=%s",
                    (booking_id,))
    db.commit()
    flash("Booking cancelled. The slot is free again.", "ok")
    return redirect(url_for("main.my_bookings"))


# ---------------------------------------------------------------------------
# where is my car
# ---------------------------------------------------------------------------

@bp.route("/where-is-my-car")
@login_required
def where_is_my_car():
    user = load_current_user()
    active = query("""SELECT b.*, s.code AS slot_code, s.note, s.slot_type,
                             l.code AS level_code, l.name AS level_name
                      FROM bookings b
                      JOIN slots s ON s.id = b.slot_id
                      JOIN levels l ON l.id = s.level_id
                      WHERE b.user_id = %s AND b.status = 'active'
                      ORDER BY b.start_ts DESC LIMIT 1""",
                    (user["id"],), one=True)
    hint = _walk_hint(active["slot_code"], active["level_code"]) if active else None
    return render_template("main/where_is_my_car.html", booking=active, hint=hint)


# ---------------------------------------------------------------------------
# SOS
# ---------------------------------------------------------------------------

@bp.route("/sos", methods=["POST"])
@login_required
def sos():
    user = load_current_user()
    slot_id    = request.form.get("slot_id", type=int)
    booking_id = request.form.get("booking_id", type=int)
    message    = (request.form.get("message") or "").strip()[:255] or None
    execute("""INSERT INTO sos_alerts (user_id, slot_id, booking_id, message)
               VALUES (%s,%s,%s,%s)""",
            (user["id"], slot_id, booking_id, message))
    flash("Your alert reached the security desk. Help is on the way. "
          "Please stay near the bay or the nearest lift lobby.", "ok")
    return redirect(request.referrer or url_for("main.index"))