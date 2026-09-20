"""
Passwords, sessions, CSRF protection and role checks.

Everything here is deliberately small and explicit so it can be explained in a
viva without hand-waving.
"""

import functools
import hmac
import secrets

from flask import session, request, redirect, url_for, flash, abort, g
from werkzeug.security import generate_password_hash, check_password_hash

from .db import query


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

def hash_password(plain):
    """Hash a password with PBKDF2-SHA256. Never store the plain text."""
    return generate_password_hash(plain, method="pbkdf2:sha256")


def verify_password(stored_hash, plain):
    """Constant-time comparison handled internally by Werkzeug."""
    return check_password_hash(stored_hash, plain)


# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

def csrf_token():
    """Return (and lazily create) the CSRF token for this session."""
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def init_csrf(app):
    """Reject any state-changing request without a matching CSRF token."""

    @app.before_request
    def _verify_csrf():
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return
        sent = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
        good = session.get("_csrf")
        if not good or not sent or not hmac.compare_digest(str(sent), str(good)):
            abort(400, "Your session expired or the form was tampered with. "
                       "Please go back, refresh the page and try again.")


# ---------------------------------------------------------------------------
# Current user + access control
# ---------------------------------------------------------------------------

def load_current_user():
    """Load the signed-in user once per request and cache it on flask.g."""
    if "user" in g:
        return g.user
    uid = session.get("user_id")
    g.user = None
    if uid:
        g.user = query(
            """SELECT id, name, email, phone, role, wants_women_slots, created_at
               FROM users WHERE id = %s AND is_active = 1""",
            (uid,), one=True,
        )
        if g.user is None:
            session.clear()   # account was disabled or deleted
    return g.user


def login_required(view):
    """Any signed-in user."""

    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not load_current_user():
            flash("Please sign in to continue.", "info")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """Signed-in AND role == 'admin'. Applied to every admin route."""

    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        user = load_current_user()
        if not user:
            flash("Admin sign-in required.", "info")
            return redirect(url_for("auth.login", next=request.path))
        if user["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)

    return wrapped