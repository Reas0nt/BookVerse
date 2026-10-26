"""SQLite access helpers and the init-db CLI command."""
import sqlite3

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash

SEED_USERS = [
    ("admin", "admin123", "Administrador BookVerse", "administrador"),
    ("tecnico", "tecnico123", "Tecnico BookVerse", "tecnico"),
]

SEED_EQUIPMENT = [
    ("EQ-001", "BV-CAJA-01", "PC", "Sucursal Centro - Caja", "SN-PC-0001", "operativo"),
    ("EQ-002", "BV-BODEGA-01", "Notebook", "Bodega central", "SN-NB-0002", "operativo"),
    ("EQ-003", "BV-IMP-01", "Impresora", "Sucursal Centro - Administracion", "SN-IM-0003", "operativo"),
]

SEED_SOFTWARE = [
    ("Windows 11", "23H2", "Sistema operativo de los equipos de oficina"),
    ("Microsoft Office", "2021", "Suite ofimática"),
    ("Antivirus ESET", "17.0", "Protección antimalware"),
    ("Google Chrome", "126.0", "Navegador web"),
]

SEED_PARTS = [
    ("Almacenamiento", "Disco SSD 480 GB", 5, "en buen estado"),
    ("Memoria", "RAM DDR4 8 GB", 8, "en buen estado"),
    ("Impresión", "Cartucho de tóner negro", 3, "en buen estado"),
]


def get_db():
    """Return the per-request connection, creating it on first use."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the schema and load seed data."""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
    for username, password, full_name, role in SEED_USERS:
        db.execute(
            "INSERT INTO user (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(password), full_name, role),
        )
    db.executemany(
        "INSERT INTO equipment (code, hostname, type, location, serial_number, status)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        SEED_EQUIPMENT,
    )
    db.executemany(
        "INSERT INTO software (name, current_version, description) VALUES (?, ?, ?)",
        SEED_SOFTWARE,
    )
    db.executemany(
        "INSERT INTO part (type, name, quantity, status) VALUES (?, ?, ?, ?)", SEED_PARTS
    )
    db.commit()


@click.command("init-db")
def init_db_command():
    """Reset the database and load seed data."""
    init_db()
    click.echo("Base de datos inicializada.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
