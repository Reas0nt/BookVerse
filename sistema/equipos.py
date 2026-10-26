"""Equipment registry blueprint."""
import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .auth import admin_required, login_required
from .db import get_db

bp = Blueprint("equipos", __name__, url_prefix="/equipos")

EQUIPMENT_TYPES = ("PC", "Notebook", "Impresora", "Otro")


@bp.route("/")
@login_required
def index():
    equipment = get_db().execute("SELECT * FROM equipment ORDER BY code").fetchall()
    return render_template("equipos/index.html", equipment=equipment)


def _validate(form):
    """Return (cleaned values, list of error messages)."""
    values = {k: form.get(k, "").strip() for k in
              ("code", "hostname", "type", "location", "serial_number")}
    errors = []
    for field, label in (("code", "Código"), ("hostname", "Nombre de host"),
                         ("location", "Ubicación"), ("serial_number", "Número de serie")):
        if not values[field]:
            errors.append(f"{label} es obligatorio.")
    if values["type"] not in EQUIPMENT_TYPES:
        errors.append("Tipo de equipo no válido.")
    code = values["code"]
    if code and not (code.startswith("EQ-") and code[3:].isdigit() and len(code) == 6):
        errors.append("El código debe tener el formato EQ-NNN (por ejemplo, EQ-004).")
    return values, errors


@bp.route("/nuevo", methods=("GET", "POST"))
@admin_required
def create():
    values = {}
    if request.method == "POST":
        values, errors = _validate(request.form)
        if not errors:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO equipment (code, hostname, type, location, serial_number)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (values["code"], values["hostname"], values["type"],
                     values["location"], values["serial_number"]),
                )
                db.commit()
            except sqlite3.IntegrityError:
                errors.append("Ya existe un equipo con ese código.")
            else:
                flash("Equipo registrado.", "success")
                return redirect(url_for("equipos.index"))
        for message in errors:
            flash(message, "error")
    return render_template("equipos/form.html", values=values, types=EQUIPMENT_TYPES)
