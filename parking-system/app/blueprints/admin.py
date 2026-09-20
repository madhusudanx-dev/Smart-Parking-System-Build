"""Admin routes. Every view requires role == 'admin' via @admin_required."""

import csv
import io
import math
from datetime import datetime, timedelta

from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, jsonify, Response, abort)
from ..db import get_db, query, execute, execute_rowcount
from ..security import admin_required, load_current_user

bp = Blueprint("admin", __name__)


# ---------------------------------------------------------------------------
# overview
# ---------------------------------------------------------------------------

@bp.route("/")
@admin_required
def overview():
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(days=1)

    totals = query("""SELECT
        SUM(slot_type='standard') AS std,
        SUM(slot_type='ev')       AS ev,
        SUM(slot_type='women')    AS women,
        COUNT(*)                  AS total,
        SUM(status='occupied')    AS occupied
        FROM slots WHERE is_active = 1""", one=True) or {}

    entries_today = query("""SELECT COUNT(*) c FROM parking_sessions
                             WHERE entry_ts >= %s AND entry_ts < %s""",
                          (start, end), one=True)["c"]
    exits_today = query("""SELECT COUNT(*) c FROM parking_sessions
                           WHERE exit_ts >= %s AND exit_ts < %s""",
                        (start, end), one=True)["c"]
    revenue_today = query("""SELECT COALESCE(SUM(amount),0) s FROM payments
                             WHERE status='paid' AND created_at >= %s
                               AND created_at < %s""",
                          (start, end), one=True)["s"]
    open_sos = query("SELECT COUNT(*) c FROM sos_alerts WHERE status='open'",
                     one=True)["c"]

    series = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        ds = datetime.combine(d, datetime.min.time())
        de = ds + timedelta(days=1)
        r = query("""SELECT COALESCE(SUM(amount),0) s FROM payments
                     WHERE status='paid' AND created_at >= %s AND created_at < %s""",
                  (ds, de), one=True)["s"]
        series.append({"day": d.strftime("%a"), "revenue": float(r or 0)})

    return render_template("admin/overview.html",
                           totals=totals, entries_today=entries_today,
                           exits_today=exits_today, revenue_today=revenue_today,
                           open_sos=open_sos, series=series)


# ---------------------------------------------------------------------------
# slot manager
# ---------------------------------------------------------------------------

@bp.route("/slots", methods=["GET", "POST"])
@admin_required
def slots():
    if request.method == "POST":
        sid = request.form.get("id", type=int)
        data = {
            "level_id":     request.form.get("level_id", type=int),
            "code":         (request.form.get("code") or "").strip().upper(),
            "slot_type":    request.form.get("slot_type") or "standard",
            "vehicle_type": request.form.get("vehicle_type") or "car",
            "pos_x":        request.form.get("pos_x", type=int) or 0,
            "pos_y":        request.form.get("pos_y", type=int) or 0,
            "note":         (request.form.get("note") or "").strip() or None,
        }
        if not data["level_id"] or not data["code"]:
            flash("Level and slot code are required.", "err")
            return redirect(url_for("admin.slots"))

        if sid:
            execute("""UPDATE slots SET level_id=%s, code=%s, slot_type=%s,
                       vehicle_type=%s, pos_x=%s, pos_y=%s, note=%s
                       WHERE id=%s""",
                    (data["level_id"], data["code"], data["slot_type"],
                     data["vehicle_type"], data["pos_x"], data["pos_y"],
                     data["note"], sid))
            flash(f"Slot {data['code']} updated.", "ok")
        else:
            try:
                execute("""INSERT INTO slots (level_id, code, slot_type,
                           vehicle_type, pos_x, pos_y, note)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (data["level_id"], data["code"], data["slot_type"],
                         data["vehicle_type"], data["pos_x"], data["pos_y"],
                         data["note"]))
                flash(f"Slot {data['code']} added.", "ok")
            except Exception:
                flash("That slot code already exists for this level.", "err")
        return redirect(url_for("admin.slots"))

    levels = query("SELECT * FROM levels ORDER BY floor_order")
    all_slots = query("""SELECT s.*, l.code AS level_code FROM slots s
                         JOIN levels l ON l.id = s.level_id
                         ORDER BY l.floor_order, s.code""")
    return render_template("admin/slots.html", levels=levels, slots=all_slots)


@bp.route("/slots/<int:sid>/toggle", methods=["POST"])
@admin_required
def slot_toggle(sid):
    execute("UPDATE slots SET is_active = NOT is_active WHERE id=%s", (sid,))
    flash("Slot availability toggled.", "ok")
    return redirect(url_for("admin.slots"))


@bp.route("/slots/<int:sid>/delete", methods=["POST"])
@admin_required
def slot_delete(sid):
    execute_rowcount("DELETE FROM slots WHERE id=%s", (sid,))
    flash("Slot removed.", "ok")
    return redirect(url_for("admin.slots"))


# ---------------------------------------------------------------------------
# entry / exit desk
# ---------------------------------------------------------------------------

@bp.route("/desk")
@admin_required
def desk():
    inside = query("""SELECT ps.*, s.code AS slot_code, l.code AS level_code
                      FROM parking_sessions ps
                      JOIN slots s ON s.id = ps.slot_id
                      JOIN levels l ON l.id = s.level_id
                      WHERE ps.status = 'inside'
                      ORDER BY ps.entry_ts DESC""")
    recent = query("""SELECT ps.*, s.code AS slot_code FROM parking_sessions ps
                      JOIN slots s ON s.id = ps.slot_id
                      WHERE ps.status = 'exited'
                      ORDER BY ps.exit_ts DESC LIMIT 20""")
    return render_template("admin/desk.html", inside=inside, recent=recent)


@bp.route("/desk/entry", methods=["POST"])
@admin_required
def desk_entry():
    plate = (request.form.get("plate") or "").strip().upper()
    code = (request.form.get("slot_code") or "").strip().upper()
    if not plate or not code:
        flash("Number plate and slot code are required.", "err")
        return redirect(url_for("admin.desk"))
    slot = query("SELECT id FROM slots WHERE code=%s AND is_active=1",
                 (code,), one=True)
    if not slot:
        flash("No active slot with that code.", "err")
        return redirect(url_for("admin.desk"))

    bk = query("""SELECT id FROM bookings
                  WHERE vehicle_plate=%s AND slot_id=%s
                    AND status IN ('booked','active')
                  ORDER BY start_ts DESC LIMIT 1""",
               (plate, slot["id"]), one=True)

    execute("""INSERT INTO parking_sessions
               (booking_id, slot_id, vehicle_plate, entry_ts)
               VALUES (%s,%s,%s,%s)""",
            (bk["id"] if bk else None, slot["id"], plate, datetime.now()))
    execute("UPDATE slots SET status='occupied' WHERE id=%s", (slot["id"],))
    if bk:
        execute("UPDATE bookings SET status='active' WHERE id=%s", (bk["id"],))
    flash(f"Entry logged for {plate} at {code}.", "ok")
    return redirect(url_for("admin.desk"))


@bp.route("/desk/exit/<int:sid>", methods=["POST"])
@admin_required
def desk_exit(sid):
    sess = query("""SELECT ps.*, s.vehicle_type FROM parking_sessions ps
                    JOIN slots s ON s.id = ps.slot_id
                    WHERE ps.id = %s""", (sid,), one=True)
    if not sess:
        abort(404)
    now = datetime.now()
    secs = max(0, (now - sess["entry_ts"]).total_seconds())
    hours = max(1, math.ceil(secs / 3600.0))
    rate = query("""SELECT hourly_rate, charging_rate FROM pricing
                    WHERE vehicle_type = %s""",
                 (sess["vehicle_type"],), one=True) or {"hourly_rate": 30}

    amount = float(rate["hourly_rate"]) * hours
    if sess["booking_id"]:
        bk = query("SELECT charging_addon FROM bookings WHERE id=%s",
                   (sess["booking_id"],), one=True)
        if bk and bk["charging_addon"]:
            amount += float(rate.get("charging_rate") or 0) * hours

    execute("""UPDATE parking_sessions
               SET exit_ts=%s, billed_hours=%s, amount=%s, status='exited'
               WHERE id=%s""", (now, hours, amount, sid))
    execute("UPDATE slots SET status='available' WHERE id=%s", (sess["slot_id"],))
    if sess["booking_id"]:
        execute("UPDATE bookings SET status='completed' WHERE id=%s",
                (sess["booking_id"],))
        execute("""UPDATE payments SET amount=%s, status='paid'
                   WHERE booking_id=%s AND status='pending'""",
                (amount, sess["booking_id"]))
    flash(f"Exit logged. {hours} hour(s) \u2014 \u20b9{amount:.2f}.", "ok")
    return redirect(url_for("admin.desk"))


# ---------------------------------------------------------------------------
# bookings / users
# ---------------------------------------------------------------------------

@bp.route("/bookings")
@admin_required
def bookings():
    rows = query("""SELECT b.*, u.name AS user_name, s.code AS slot_code,
                           l.code AS level_code
                    FROM bookings b
                    JOIN users u ON u.id = b.user_id
                    JOIN slots s ON s.id = b.slot_id
                    JOIN levels l ON l.id = s.level_id
                    ORDER BY b.created_at DESC LIMIT 200""")
    return render_template("admin/bookings.html", bookings=rows)


@bp.route("/users")
@admin_required
def users():
    rows = query("""SELECT u.*,
                    (SELECT COUNT(*) FROM bookings WHERE user_id = u.id)
                       AS booking_count
                    FROM users u ORDER BY u.created_at DESC""")
    return render_template("admin/users.html", users=rows)


@bp.route("/users/<int:uid>/toggle", methods=["POST"])
@admin_required
def user_toggle(uid):
    me = load_current_user()
    if uid == me["id"]:
        flash("You cannot disable your own account.", "err")
        return redirect(url_for("admin.users"))
    execute("UPDATE users SET is_active = NOT is_active WHERE id=%s", (uid,))
    flash("User status updated.", "ok")
    return redirect(url_for("admin.users"))


# ---------------------------------------------------------------------------
# EV charging stations
# ---------------------------------------------------------------------------

@bp.route("/ev")
@admin_required
def ev():
    bays = query("""SELECT s.*, l.code AS level_code FROM slots s
                    JOIN levels l ON l.id = s.level_id
                    WHERE s.slot_type = 'ev'
                    ORDER BY s.code""")
    sessions = query("""SELECT e.*, s.code AS slot_code FROM ev_charging_sessions e
                        JOIN slots s ON s.id = e.slot_id
                        ORDER BY e.start_ts DESC LIMIT 50""")
    return render_template("admin/ev.html", bays=bays, sessions=sessions)


# ---------------------------------------------------------------------------
# Women's Safety zone monitor + SOS feed
# ---------------------------------------------------------------------------

@bp.route("/women-safety")
@admin_required
def women_safety():
    bays = query("""SELECT s.*, l.code AS level_code FROM slots s
                    JOIN levels l ON l.id = s.level_id
                    WHERE s.slot_type = 'women'
                    ORDER BY s.code""")
    alerts = query("""SELECT a.*, u.name AS user_name, u.phone,
                             s.code AS slot_code
                      FROM sos_alerts a
                      JOIN users u ON u.id = a.user_id
                      LEFT JOIN slots s ON s.id = a.slot_id
                      ORDER BY a.status ASC, a.created_at DESC LIMIT 100""")
    return render_template("admin/women_safety.html", bays=bays, alerts=alerts)


@bp.route("/sos/<int:aid>/resolve", methods=["POST"])
@admin_required
def sos_resolve(aid):
    me = load_current_user()
    execute("""UPDATE sos_alerts SET status='resolved', resolved_at=NOW(),
               resolved_by=%s WHERE id=%s""", (me["id"], aid))
    flash("Alert marked as resolved.", "ok")
    return redirect(url_for("admin.women_safety"))


@bp.route("/api/sos/open")
@admin_required
def api_sos_open():
    rows = query("""SELECT a.id, a.created_at, u.name AS user_name,
                           s.code AS slot_code FROM sos_alerts a
                    JOIN users u ON u.id = a.user_id
                    LEFT JOIN slots s ON s.id = a.slot_id
                    WHERE a.status = 'open' ORDER BY a.created_at DESC""")
    return jsonify({"count": len(rows), "alerts": [
        {"id": r["id"], "user": r["user_name"], "slot": r["slot_code"],
         "at": r["created_at"].strftime("%I:%M %p").lstrip("0")}
        for r in rows]})


# ---------------------------------------------------------------------------
# reports
# ---------------------------------------------------------------------------

def _report_rows(start, end):
    return query("""SELECT DATE(created_at) d, SUM(amount) revenue,
                           COUNT(*) txn
                    FROM payments
                    WHERE status='paid' AND created_at >= %s AND created_at < %s
                    GROUP BY DATE(created_at) ORDER BY d""", (start, end))


@bp.route("/reports")
@admin_required
def reports():
    return render_template("admin/reports.html")


@bp.route("/reports/data")
@admin_required
def reports_data():
    start_s = request.args.get("start")
    end_s = request.args.get("end")
    try:
        start = datetime.strptime(start_s, "%Y-%m-%d")
        end = datetime.strptime(end_s, "%Y-%m-%d") + timedelta(days=1)
    except (TypeError, ValueError):
        return jsonify({"error": "Bad dates"}), 400
    rows = _report_rows(start, end)
    peak = query("""SELECT HOUR(entry_ts) h, COUNT(*) c FROM parking_sessions
                    WHERE entry_ts >= %s AND entry_ts < %s
                    GROUP BY HOUR(entry_ts) ORDER BY c DESC LIMIT 5""",
                 (start, end))
    return jsonify({
        "series": [{"date": str(r["d"]), "revenue": float(r["revenue"]),
                    "txn": r["txn"]} for r in rows],
        "peak": [{"hour": r["h"], "count": r["c"]} for r in peak],
    })


@bp.route("/reports.csv")
@admin_required
def reports_csv():
    start_s = request.args.get("start")
    end_s = request.args.get("end")
    try:
        start = datetime.strptime(start_s, "%Y-%m-%d")
        end = datetime.strptime(end_s, "%Y-%m-%d") + timedelta(days=1)
    except (TypeError, ValueError):
        flash("Pick a valid date range.", "err")
        return redirect(url_for("admin.reports"))
    rows = _report_rows(start, end)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Date", "Revenue (INR)", "Transactions"])
    total = 0.0
    for r in rows:
        w.writerow([r["d"], f"{float(r['revenue']):.2f}", r["txn"]])
        total += float(r["revenue"])
    w.writerow(["TOTAL", f"{total:.2f}", ""])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition":
                             "attachment; filename=parking-report.csv"})