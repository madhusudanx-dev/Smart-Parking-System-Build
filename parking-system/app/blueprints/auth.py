"""
Authentication blueprint: register, login, logout.

Design notes for the viva
-------------------------
* Passwords are hashed with PBKDF2-SHA256 (Werkzeug).
* The session only stores the user id; the full row is re-fetched on every
  request by load_current_user().
* Every POST is CSRF-protected by the before_request hook in app/security.py.
* Validation is run on the server; the client does friendly inline hints too.
"""

import re
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, g,
)

from ..db import query, execute
from ..security import hash_password, verify_password, load_current_user

bp = Blueprint("auth", __name__)

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")


def _clean(value):
    return (value or "").strip()


def _validate_register(form):
    """Return (data, errors). data is only trusted when errors is empty."""
    data = {
        "name":             _clean(form.get("name")),
        "email":            _clean(form.get("email")).lower(),
        "phone":            _clean(form.get("phone")),
        "password":         form.get("password") or "",
        "password_confirm": form.get("password_confirm") or "",
        "wants_women":      1 if form.get("wants_women") else 0,
    }
    errors = {}
    if len(data["name"]) < 2:
        errors["name"] = "Please tell us your name."
    if not EMAIL_RE.match(data["email"]):
        errors["email"] = "That email address does not look right."
    if data["phone"] and not PHONE_RE.match(data["phone"]):
        errors["phone"] = "Please enter a valid phone number."
    if len(data["password"]) < 8:
        errors["password"] = "Use at least 8 characters."
    if data["password"] != data["password_confirm"]:
        errors["password_confirm"] = "The two passwords do not match."
    return data, errors


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route("/register", methods=("GET", "POST"))
def register():
    if load_current_user():
        return redirect(url_for("main.index"))

    form_data = {}
    errors = {}

    if request.method == "POST":
        data, errors = _validate_register(request.form)
        form_data = data

        if not errors:
            existing = query(
                "SELECT id FROM users WHERE email = %s",
                (data["email"],), one=True,
            )
            if existing:
                errors["email"] = "An account with this email already exists."
            else:
                uid = execute(
                    """INSERT INTO users
                       (name, email, phone, password_hash, role, wants_women_slots)
                       VALUES (%s, %s, %s, %s, 'user', %s)""",
                    (data["name"], data["email"], data["phone"] or None,
                     hash_password(data["password"]), data["wants_women"]),
                )
                # Log the user in and send them home.
                session.clear()
                session["user_id"] = uid
                flash(f"Welcome aboard, {data['name'].split()[0]}. "
                      f"Your account is ready.", "ok")
                return redirect(url_for("main.index"))

        if errors:
            flash("Please check the highlighted fields below.", "err")

    return render_template(
        "auth/register.html",
        title="Create your account",
        form=form_data,
        errors=errors,
    )


@bp.route("/login", methods=("GET", "POST"))
def login():
    if load_current_user():
        return redirect(url_for("main.index"))

    email = ""
    errors = {}

    if request.method == "POST":
        email    = _clean(request.form.get("email")).lower()
        password = request.form.get("password") or ""

        if not email:
            errors["email"] = "Please enter your email."
        if not password:
            errors["password"] = "Please enter your password."

        if not errors:
            row = query(
                """SELECT id, name, password_hash, role, is_active
                   FROM users WHERE email = %s""",
                (email,), one=True,
            )
            if not row or not row["is_active"]:
                errors["email"] = "We could not find an account with that email."
            elif not verify_password(row["password_hash"], password):
                errors["password"] = "That password does not match."
            else:
                # Success: rotate session id to prevent fixation.
                session.clear()
                session["user_id"] = row["id"]
                flash(f"Welcome back, {row['name'].split()[0]}.", "ok")

                # Where to next?  Admin goes to the dashboard, users to home.
                target = request.args.get("next")
                if not target:
                    target = url_for("admin.overview") if row["role"] == "admin" \
                             else url_for("main.index")
                return redirect(target)

        if errors:
            flash("Sign-in failed. Please check your details.", "err")

    return render_template(
        "auth/login.html",
        title="Sign in",
        email=email,
        errors=errors,
    )


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    flash("You are signed out. See you soon.", "info")
    return redirect(url_for("auth.login"))