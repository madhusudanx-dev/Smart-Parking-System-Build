"""
Thin MySQL helper layer.

We use PyMySQL (pure Python - works with XAMPP and MySQL Workbench on Windows).

Every single query in this project goes through query() or execute(), and every
query uses %s placeholders. We never build SQL by gluing strings together, which
keeps us safe from SQL injection.
"""

import pymysql
from pymysql.cursors import DictCursor
from flask import g, current_app


def connect():
    """Open a brand new MySQL connection using the app config."""
    return pymysql.connect(
        host=current_app.config["DB_HOST"],
        port=int(current_app.config["DB_PORT"]),
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        database=current_app.config["DB_NAME"],
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )


def get_db():
    """Return the connection for the current request, creating it if needed."""
    if "db" not in g:
        g.db = connect()
    return g.db


def close_db(exc=None):
    """Commit on success, roll back on error, then close. Wired to teardown."""
    conn = g.pop("db", None)
    if conn is None:
        return
    try:
        if exc is None:
            conn.commit()
        else:
            conn.rollback()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Small helpers so blueprints stay readable
# ---------------------------------------------------------------------------

def query(sql, params=None, one=False):
    """Run a SELECT. Returns a list of dicts, or a single dict when one=True."""
    with get_db().cursor() as cur:
        cur.execute(sql, params or ())
        rows = cur.fetchall()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, params=None):
    """Run an INSERT / UPDATE / DELETE. Returns lastrowid."""
    with get_db().cursor() as cur:
        cur.execute(sql, params or ())
        return cur.lastrowid


def execute_rowcount(sql, params=None):
    """Run an UPDATE / DELETE and return how many rows were touched."""
    with get_db().cursor() as cur:
        cur.execute(sql, params or ())
        return cur.rowcount