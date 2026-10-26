"""Software catalog (admin-managed) and software update records (RF-07)."""
import sqlite3
from datetime import date

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)

from .auth import admin_required, login_required
from .db import get_db
from .mantenimientos import parse_date

bp = Blueprint("software", __name__, url_prefix="/software")

UPDATE_METHODS = {"manual": "Manual", "automatica": "Automática", "remota": "Remota"}


@bp.route("/")
@login_required
def index():
    rows = get_db().execute("SELECT * FROM software ORDER BY name").fetchall()
    return render_template("software/index.html", software=rows)


@bp.route("/nuevo", methods=("GET", "POST"))
@admin_required
def create():
    values = {}
    if request.method == "POST":
        values = {k: request.form.get(k, "").strip()
                  for k in ("name", "current_version", "description")}
        errors = []
        if not values["name"]:
            errors.append("El nombre del software es obligatorio.")
        if not values["current_version"]:
            errors.append("La versión actual es obligatoria.")
        if not errors:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO software (name, current_version, description) VALUES (?, ?, ?)",
                    (values["name"], values["current_version"], values["description"]),
                )
                db.commit()
            except sqlite3.IntegrityError:
                errors.append("Ya existe un software con ese nombre.")
            else:
                flash("Software registrado en el listado de aplicaciones.", "success")
                return redirect(url_for("software.index"))
        for message in errors:
            flash(message, "error")
    return render_template("software/form.html", values=values)


def _validate_update(form, db):
    values = {k: form.get(k, "").strip() for k in
              ("software_name", "equipment_id", "previous_version", "new_version",
               "updated_on", "method", "changes")}
    errors, software = [], None
    if not values["software_name"]:
        errors.append("Debe indicar el software a actualizar.")
    else:
        software = db.execute(
            "SELECT * FROM software WHERE name = ? COLLATE NOCASE", (values["software_name"],)
        ).fetchone()
        if software is None:
            errors.append(
                f"El software '{values['software_name']}' no está en el listado de aplicaciones. "
                "Debe registrarse primero (solicite al administrador su alta)."
            )
    if not values["equipment_id"].isdigit() or db.execute(
            "SELECT 1 FROM equipment WHERE id = ?", (values["equipment_id"],)).fetchone() is None:
        errors.append("Debe seleccionar un equipo válido.")
    if not values["previous_version"]:
        errors.append("La versión anterior es obligatoria.")
    if not values["new_version"]:
        errors.append("La versión nueva es obligatoria.")
    if values["previous_version"] and values["previous_version"] == values["new_version"]:
        errors.append("La versión nueva debe ser distinta de la anterior.")
    updated = parse_date(values["updated_on"])
    if updated is None:
        errors.append("La fecha no es válida (use el formato AAAA-MM-DD).")
    elif updated > date.today():
        errors.append("La fecha de actualización no puede ser futura.")
    if values["method"] not in UPDATE_METHODS:
        errors.append("Método de actualización no válido.")
    return values, errors, software


@bp.route("/actualizar", methods=("GET", "POST"))
@login_required
def update():
    db = get_db()
    values = {"updated_on": date.today().isoformat()}
    if request.method == "POST":
        values, errors, software = _validate_update(request.form, db)
        if not errors:
            db.execute(
                "INSERT INTO software_update (software_id, equipment_id, technician_id,"
                " previous_version, new_version, updated_on, method, changes)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (software["id"], values["equipment_id"], g.user["id"], values["previous_version"],
                 values["new_version"], values["updated_on"], values["method"], values["changes"]),
            )
            db.execute("UPDATE software SET current_version = ? WHERE id = ?",
                       (values["new_version"], software["id"]))
            db.commit()
            flash("Actualización de software registrada.", "success")
            return redirect(url_for("software.updates"))
        for message in errors:
            flash(message, "error")
    return render_template(
        "software/update_form.html", values=values, methods=UPDATE_METHODS,
        software=db.execute("SELECT name, current_version FROM software ORDER BY name").fetchall(),
        equipment=db.execute("SELECT id, code, hostname FROM equipment ORDER BY code").fetchall(),
    )


@bp.route("/actualizaciones")
@login_required
def updates():
    rows = get_db().execute(
        "SELECT su.*, s.name AS software_name, e.code, u.full_name AS technician"
        " FROM software_update su JOIN software s ON s.id = su.software_id"
        " JOIN equipment e ON e.id = su.equipment_id JOIN user u ON u.id = su.technician_id"
        " ORDER BY su.updated_on DESC, su.id DESC"
    ).fetchall()
    return render_template("software/updates.html", rows=rows, methods=UPDATE_METHODS)
