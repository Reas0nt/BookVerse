# BookVerse maintenance system

Small web app for registering and querying office equipment maintenance (Stage 2, RF-06 to RF-09).

Stack: Python 3.12, Flask, SQLite (single file, no server needed).

## Setup

From the repository root:

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Run

```bash
flask --app sistema init-db     # creates the database with example data
flask --app sistema run --port 5110   # http://127.0.0.1:5110
```

`init-db` deletes and recreates the database. Run it only the first time or to reset.

## Default users

| User | Password | Role |
|---|---|---|
| `admin` | `admin123` | administrador |
| `tecnico` | `tecnico123` | tecnico |

These are demo credentials. Change them, and set the `SECRET_KEY` environment variable, before using the app outside the lab.

## Requirements coverage

| Requirement | Page | What it does |
|---|---|---|
| Login (all RF) | `/login` | Authenticated access with two roles |
| Equipment | `/equipos/` | Equipment registry (code, hostname, type, location, serial number, status) |
| RF-06 | `/mantenimientos/nuevo` | Register preventive or corrective maintenance |
| RF-07 | `/software/`, `/software/actualizar` | Software catalog and update records; unregistered software shows a "must be registered" message |
| RF-08 | `/mantenimientos/` | History with filters (dates, type, equipment code or serial number) and detail per entry; database errors show a message |
| RF-09 (case) | `/validaciones/` | Validate software after maintenance; a failure flags the equipment for a new intervention |
| RF-09 (week 10 guideline) | `/repuestos/` | Spare parts with status, stock entries and exits; exits larger than stock are rejected |

Admin-only: software catalog, validations, creating parts and changing part status.

## Tests

```bash
python -m pytest sistema/tests -q
```

## Known limitations

This is a course prototype, not production software:

- No CSRF protection on forms.
- Default users and secret key are for demo use only.
- `init-db` is destructive (drops all data).
