"""Maintenance registration (RF-06) and history query (RF-08)."""
import sqlite3
from datetime import date

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)

from .auth import login_required
from .db import get_db

bp = Blueprint("mantenimientos", __name__, url_prefix="/mantenimientos")

MAINTENANCE_TYPES = ("preventivo", "correctivo")


def parse_date(value):
    """Parse an ISO date (YYYY-MM-DD); return None when invalid."""
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _validate(form):
    values = {k: form.get(k, "").strip() for k in
              ("equipment_id", "type", "performed_on", "description", "observations")}
    errors = []
    if not values["equipment_id"].isdigit():
        errors.append("Debe seleccionar un equipo.")
    if values["type"] not in MAINTENANCE_TYPES:
        errors.append("Tipo de mantenimiento no válido.")
    performed = parse_date(values["performed_on"])
    if performed is None:
        errors.append("La fecha no es válida (use el formato AAAA-MM-DD).")
    elif performed > date.today():
        errors.append("La fecha del mantenimiento no puede ser futura.")
    if not values["description"]:
        errors.append("La descripción es obligatoria.")
    return values, errors


@bp.route("/nuevo", methods=("GET", "POST"))
@login_required
def create():
    db = get_db()
    values = {"performed_on": date.today().isoformat()}
    if request.method == "POST":
        values, errors = _validate(request.form)
        if not errors and db.execute(
                "SELECT 1 FROM equipment WHERE id = ?", (values["equipment_id"],)).fetchone() is None:
            errors.append("El equipo no está registrado. Debe registrarse primero.")
        if not errors:
            db.execute(
                "INSERT INTO maintenance (equipment_id, technician_id, type, performed_on,"
                " description, observations) VALUES (?, ?, ?, ?, ?, ?)",
                (values["equipment_id"], g.user["id"], values["type"],
                 values["performed_on"], values["description"], values["observations"]),
            )
            db.commit()
            flash("Mantenimiento registrado correctamente.", "success")
            return redirect(url_for("mantenimientos.history"))
        for message in errors:
            flash(message, "error")
    equipment = db.execute("SELECT id, code, hostname FROM equipment ORDER BY code").fetchall()
    return render_template("mantenimientos/form.html", values=values, equipment=equipment,
                           types=MAINTENANCE_TYPES)


def _history_query(args):
    """Build the filtered history SQL; return (sql, params, errors)."""
    clauses, params, errors = [], [], []
    date_from, date_to = args.get("desde", "").strip(), args.get("hasta", "").strip()
    for raw, label, op in ((date_from, "desde", ">="), (date_to, "hasta", "<=")):
        if raw:
            if parse_date(raw) is None:
                errors.append(f"La fecha '{label}' no es válida.")
            else:
                clauses.append(f"m.performed_on {op} ?")
                params.append(raw)
    if date_from and date_to and not errors and date_from > date_to:
        errors.append("La fecha 'desde' no puede ser posterior a 'hasta'.")
    mtype = args.get("tipo", "").strip()
    if mtype:
        if mtype not in MAINTENANCE_TYPES:
            errors.append("Tipo de mantenimiento no válido.")
        else:
            clauses.append("m.type = ?")
            params.append(mtype)
    term = args.get("equipo", "").strip()
    if term:
        clauses.append("(e.code LIKE ? OR e.serial_number LIKE ?)")
        params.extend([f"%{term}%"] * 2)
    sql = (
        "SELECT m.id, m.type, m.performed_on, m.description, e.code, e.hostname,"
        " e.serial_number, u.full_name AS technician"
        " FROM maintenance m JOIN equipment e ON e.id = m.equipment_id"
        " JOIN user u ON u.id = m.technician_id"
    )
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY m.performed_on DESC, m.id DESC"
    return sql, params, errors


def _db_error():
    return render_template("mantenimientos/error.html"), 503


@bp.route("/")
@login_required
def history():
    sql, params, errors = _history_query(request.args)
    for message in errors:
        flash(message, "error")
    rows = []
    if not errors:
        try:
            rows = get_db().execute(sql, params).fetchall()
        except sqlite3.Error:
            return _db_error()
    return render_template("mantenimientos/history.html", rows=rows, filters=request.args,
                           types=MAINTENANCE_TYPES)


@bp.route("/<int:maintenance_id>")
@login_required
def detail(maintenance_id):
    try:
        row = get_db().execute(
            "SELECT m.*, e.code, e.hostname, e.type AS equipment_type, e.serial_number,"
            " u.full_name AS technician FROM maintenance m"
            " JOIN equipment e ON e.id = m.equipment_id"
            " JOIN user u ON u.id = m.technician_id WHERE m.id = ?",
            (maintenance_id,),
        ).fetchone()
    except sqlite3.Error:
        return _db_error()
    if row is None:
        return render_template("mantenimientos/error.html", not_found=True), 404
    return render_template("mantenimientos/detail.html", m=row)
