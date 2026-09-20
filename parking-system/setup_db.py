"""
One-shot database setup for the Smart Parking Slot System.

What it does
------------
1. Runs schema.sql  (drops and recreates the smart_parking database)
2. Runs seed.sql    (demo lot, levels, 48 slots, users, bookings, payments...)
3. Replaces the placeholder password hashes in seed.sql with real Werkzeug
   PBKDF2 hashes for the demo password:  Password@123

Usage (from the project root, with your .env file present):
    python setup_db.py
"""

import os
import re
import sys

import pymysql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

HOST = os.getenv("DB_HOST", "127.0.0.1")
PORT = int(os.getenv("DB_PORT", "3306"))
USER = os.getenv("DB_USER", "root")
PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "smart_parking")

DEMO_PASSWORD = "Password@123"


def statements(sql_text):
    """Split a .sql file into individual statements, ignoring -- comments."""
    cleaned = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        cleaned.append(line)
    body = "\n".join(cleaned)
    for chunk in body.split(";"):
        chunk = chunk.strip()
        if chunk:
            yield chunk


def run_file(cursor, path):
    with open(path, "r", encoding="utf-8") as fh:
        sql = fh.read()
    count = 0
    for stmt in statements(sql):
        cursor.execute(stmt)
        count += 1
    return count


def main():
    if not os.path.exists("schema.sql") or not os.path.exists("seed.sql"):
        sys.exit("schema.sql and seed.sql must sit next to setup_db.py")

    # ---- 1. schema (connect without a database selected) -------------------
    print(f"Connecting to MySQL at {HOST}:{PORT} as {USER} ...")
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD,
                           charset="utf8mb4", autocommit=True)
    with conn.cursor() as cur:
        n = run_file(cur, "schema.sql")
    conn.close()
    print(f"  schema.sql applied ({n} statements). Database '{DB_NAME}' recreated.")

    # ---- 2. seed data ------------------------------------------------------
    conn = pymysql.connect(host=HOST, port=PORT, user=USER, password=PASSWORD,
                           database=DB_NAME, charset="utf8mb4", autocommit=True)
    with conn.cursor() as cur:
        n = run_file(cur, "seed.sql")
    print(f"  seed.sql applied ({n} statements).")

    # ---- 3. real password hashes ------------------------------------------
    pwd_hash = generate_password_hash(DEMO_PASSWORD, method="pbkdf2:sha256")
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET password_hash = %s WHERE password_hash = %s",
                    (pwd_hash, "RESET_ME"))
        updated = cur.rowcount
    print(f"  Set real password hashes for {updated} demo accounts.")

    # ---- 4. sanity check ---------------------------------------------------
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM slots")
        slots = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admins = cur.fetchone()[0]
    conn.close()

    print("\nDone.")
    print(f"  Slots in the lot : {slots}")
    print(f"  Admin accounts   : {admins}")
    print("\nDemo logins (password for all accounts: %s)" % DEMO_PASSWORD)
    print("  Admin : admin@smartpark.in")
    print("  User  : aarthi@example.com")
    print("  User  : meera@example.com   (Women's Safety slots enabled)")
    print("  User  : sneha@example.com   (EV driver)")
    print("\nNow run:  python run.py   and open http://127.0.0.1:5000")


if __name__ == "__main__":
    main()