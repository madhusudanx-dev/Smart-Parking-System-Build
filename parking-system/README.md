# Smart Parking Slot System

A calm, frosted-glass web app where drivers check live parking availability,
reserve a slot, pay, and get a QR ticket. Admins run the lot from a dashboard.

Built for a **BCA final-year project**. Stack: **Flask · MySQL · vanilla JS · Bootstrap grid only.**

---

## 1. What you get

- Landing page with a live occupancy panel
- Live top-down floor plan (Ground + Basement 1), refreshed every 5 seconds
- Filters for slot type (Standard / EV / Women's Safety) and vehicle type
- Reserve a slot with a real, safe double-booking check (`SELECT … FOR UPDATE`)
- Simulated payment (UPI / card / pay-at-exit)
- Printable QR ticket with a written walking hint to the bay
- My bookings (upcoming / active / past) and cancel
- "Where is my car?" card with a plain-language hint and mini-map
- SOS button on Women's Safety slots and active tickets
- Admin dashboard: overview, slot manager, entry/exit desk, bookings, users,
  EV stations, Women's Safety zone monitor with live SOS feed, and reports
- CSV export + print view for reports

---

## 2. Prerequisites (Windows)

- **Python 3.10+** — https://www.python.org/downloads/
- **MySQL 8** via **XAMPP** or **MySQL Workbench**
- A modern browser (Chrome / Edge / Firefox)

---

## 3. Setup — step by step

### 3.1 Put the project in a folder

```text
C:\projects\parking-system\
```

### 3.2 Create a virtual environment

Open **PowerShell** or **cmd** in that folder:

```bat
python -m venv venv
venv\Scripts\activate
```

### 3.3 Install dependencies

```bat
pip install -r requirements.txt
```

### 3.4 Configure the `.env` file

Copy `.env.example` to `.env` and edit it:

```bat
copy .env.example .env
notepad .env
```

Fill in:

```ini
SECRET_KEY=some-long-random-string
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=smart_parking
FLASK_DEBUG=1
```

> With XAMPP, `DB_USER=root` and `DB_PASSWORD=` (blank) is the default.
> With MySQL Workbench, set the password you used during installation.

### 3.5 Make sure MySQL is running

- **XAMPP:** start **MySQL** from the XAMPP Control Panel.
- **MySQL Workbench:** MySQL server should already be running as a Windows service.

### 3.6 Create the database and demo data

```bat
python setup_db.py
```

You should see output ending with the demo logins. The script:

1. Runs `schema.sql` (drops and recreates the `smart_parking` database)
2. Runs `seed.sql` (one lot, two levels, 48 slots, 6 users, sample bookings)
3. Replaces the placeholder password hashes with real ones for `Password@123`

### 3.7 Run the app

```bat
python run.py
```

Open **http://127.0.0.1:5000/** in your browser.

---

## 4. Demo logins

Password for **every** demo account: `Password@123`

| Role  | Email                     | Notes                                    |
|-------|---------------------------|------------------------------------------|
| Admin | `admin@smartpark.in`      | Full admin dashboard                     |
| User  | `aarthi@example.com`      | Regular driver                           |
| User  | `rohan@example.com`       | Regular driver                           |
| User  | `meera@example.com`       | Women's Safety slots enabled             |
| User  | `karthik@example.com`     | Regular driver                           |
| User  | `sneha@example.com`       | EV driver, active charging session        |

---

## 5. Project structure

```
parking-system/
├── app/
│   ├── blueprints/     auth.py, main.py, admin.py
│   ├── static/         css/tokens.css, css/app.css, css/floorplan.css,
│   │                   js/app.js, js/icons.js, js/floorplan.js, js/sos.js
│   ├── templates/      base.html, macros.html, _navbar.html,
│   │                   auth/, main/, admin/, errors/
│   ├── __init__.py     Application factory
│   ├── db.py           PyMySQL helper layer (parameterised queries only)
│   └── security.py     Passwords, sessions, CSRF, role checks
├── docs/               ER diagram + DFDs in Mermaid, manual test checklist
├── .env.example
├── README.md
├── requirements.txt
├── run.py
├── schema.sql          Database schema
├── seed.sql            Demo data
└── setup_db.py         One-shot DB setup
```

---

## 6. Design system (short version)

- Palette in `app/static/css/tokens.css`. Nothing else hard-codes a hex.
- Frosted-glass surfaces, floating nav, glass cards, glass modals, glass toasts.
- Aurora background: 2–3 blurred blobs (indigo, orchid, lavender) plus a fine
  SVG film-grain overlay. Blobs drift slowly; drift is disabled under
  `prefers-reduced-motion`.
- Inter 400/500/600/700. Titles 36px on auth pages, 28px in-app.
- Slot states use a pastel tint plus an icon plus a text label — never colour alone.
- SOS coral `#E5484D` is the only saturated alert colour.

---

## 7. Common issues

| Symptom | Fix |
|---|---|
| `pymysql.err.OperationalError: (2003)` | MySQL is not running. Start it from XAMPP or Workbench. |
| `Access denied for user 'root'@'localhost'` | Wrong `DB_PASSWORD` in `.env`. |
| `Unknown database 'smart_parking'` | Run `python setup_db.py` again. |
| `ModuleNotFoundError: flask` | Activate the venv before `pip install -r requirements.txt`. |
| Port 5000 already in use | Change the port in `run.py`. |
| Blur looks washed out | Your browser may not support `backdrop-filter`. The fallback solid white glass is used automatically. |

---

## 8. How it was built (for the viva)

- **Flask blueprints** keep the three areas separate: `auth`, `main`, `admin`.
- **PyMySQL** with `%s` placeholders only — no string concatenation, so no SQL injection.
- **Werkzeug PBKDF2-SHA256** hashes for passwords.
- **Session-based auth** plus a **CSRF token** on every non-GET request,
  enforced by a `before_request` hook.
- **Role checks** on every admin route via the `@admin_required` decorator.
- **Double-booking prevention**: inside a single transaction, the code runs
  `SELECT … FOR UPDATE` on overlapping bookings for the chosen slot, and only
  inserts the new booking if there is no clash. The transaction is committed
  only after a successful insert.
- **Fee rules**: hours are computed as `ceil((end - start) / 3600s)` with a
  1-hour minimum, then multiplied by the per-vehicle hourly rate from the
  editable `pricing` table. EV charging adds the `charging_rate` per hour.
- **Live map**: `/api/slots` returns the current slot list as JSON and
  `floorplan.js` polls it every 5 seconds and repaints the SVG. The SVG uses
  `pos_x` / `pos_y` from the database, so admins can reposition bays.
- **QR ticket**: generated on the server with the `qrcode` library, embedded as
  a PNG that links back to the ticket page.

---

## 9. Assumptions

- One parking lot. Two levels (Ground, Basement 1). 48 slots.
- Payments are simulated. No real gateway.
- Social sign-in buttons are visual only — clicking shows a "not enabled in
  this demo" toast.
- Charging on EV slots uses a fixed per-hour add-on (₹12/hr) rather than metered
  kWh.
- The QR code contains a link back to the ticket page with the booking
  reference as a query parameter. There is no gate hardware in this demo.
- "Pay at exit" creates a `pending` payment that is settled by the admin at
  the desk when the vehicle exits.
- Menus, footers and page-level layouts reuse the aurora background, so a lot
  of the app feels like the same family — the layout blocks (hero, map-first,
  sidebar) vary page to page.
- Time zone is the server's local time.

---

## 10. Where to look in the code

| Feature | File |
|---|---|
| Design tokens | `app/static/css/tokens.css` |
| Glass surfaces + components | `app/static/css/app.css` |
| Floor-plan look | `app/static/css/floorplan.css` |
| Floor-plan behaviour | `app/static/js/floorplan.js` |
| Passwords, sessions, CSRF | `app/security.py` |
| DB helper | `app/db.py` |
| Booking transaction | `app/blueprints/main.py` → `book_post()` |
| Entry / exit + fee rules | `app/blueprints/admin.py` → `desk_exit()` |
| SOS pipeline | `app/blueprints/main.py` → `sos()` + `app/templates/admin/women_safety.html` |

---

## 11. Credits

Course: BCA final year.
Stack: Flask, MySQL, vanilla JS, Bootstrap grid, Inter, Chart.js, qrcode.
No frameworks beyond the ones listed in the brief.