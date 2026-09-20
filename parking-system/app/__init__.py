"""
Application factory.

create_app() wires together configuration, the database, CSRF protection,
blueprints, template helpers and error pages.
"""

import os
from datetime import datetime

from flask import Flask, render_template, g, session
from dotenv import load_dotenv

from . import db
from .security import init_csrf, csrf_token, load_current_user


def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-secret-change-me"),
        DB_HOST=os.getenv("DB_HOST", "127.0.0.1"),
        DB_PORT=os.getenv("DB_PORT", "3306"),
        DB_USER=os.getenv("DB_USER", "root"),
        DB_PASSWORD=os.getenv("DB_PASSWORD", ""),
        DB_NAME=os.getenv("DB_NAME", "smart_parking"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        JSON_SORT_KEYS=False,
    )

    # ---- database lifecycle -------------------------------------------------
    app.teardown_appcontext(db.close_db)

    # ---- security -----------------------------------------------------------
    init_csrf(app)

    # ---- blueprints ---------------------------------------------------------
    from .blueprints.auth import bp as auth_bp
    from .blueprints.main import bp as main_bp
    from .blueprints.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # ---- template helpers ---------------------------------------------------
    @app.context_processor
    def inject_globals():
        return {
            "csrf_token": csrf_token,
            "current_user": load_current_user(),
            "now": datetime.now(),
        }

    @app.template_filter("inr")
    def inr(value):
        """Format a number as Indian rupees, e.g. 1,20,000.00"""
        try:
            value = float(value or 0)
        except (TypeError, ValueError):
            value = 0.0
        whole, frac = divmod(round(value, 2), 1)
        whole = int(whole)
        s = str(whole)
        if len(s) > 3:
            head, tail = s[:-3], s[-3:]
            parts = []
            while len(head) > 2:
                parts.insert(0, head[-2:])
                head = head[:-2]
            if head:
                parts.insert(0, head)
            s = ",".join(parts) + "," + tail
        return f"\u20b9{s}.{int(round(frac * 100)):02d}"

    @app.template_filter("dt")
    def dt(value, fmt="%d %b %Y, %I:%M %p"):
        if not value:
            return "\u2014"
        if isinstance(value, str):
            return value
        return value.strftime(fmt)

    @app.template_filter("time_only")
    def time_only(value):
        if not value:
            return "\u2014"
        return value.strftime("%I:%M %p").lstrip("0")

    # ---- error pages --------------------------------------------------------
    @app.errorhandler(400)
    def err_400(e):
        return render_template("errors/error.html", code=400,
                               title="That did not go through",
                               message=str(e.description)), 400

    @app.errorhandler(403)
    def err_403(e):
        return render_template("errors/error.html", code=403,
                               title="You do not have access to this page",
                               message="This area is for parking staff accounts only."), 403

    @app.errorhandler(404)
    def err_404(e):
        return render_template("errors/error.html", code=404,
                               title="We could not find that page",
                               message="The link may be old, or the slot may have been removed."), 404

    @app.errorhandler(500)
    def err_500(e):
        return render_template("errors/error.html", code=500,
                               title="Something went wrong on our side",
                               message="Please try again in a moment."), 500

    return app