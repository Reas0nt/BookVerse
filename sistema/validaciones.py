"""Post-maintenance validation (RF-09, case): admin-only."""
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)

from .auth import admin_required
from .db import get_db

bp = Blueprint("validaciones", __name__, url_prefix="/validaciones")

RESULTS = ("OK", "Falla")
STATUS_OK = "operativo"
STATUS_REINTERVENTION = "requiere nueva intervención"


@bp.route("/")
@admin_required
def index():
    rows = get_db().execute(
        "SELECT v.*, e.code, e.hostname, u.full_name AS validator, m.performed_on"
        " FROM validation v JOIN equipment e ON e.id = v.equipment_id"
        " JOIN user u ON u.id = v.validated_by JOIN maintenance m ON m.id = v.maintenance_id"
        " ORDER BY v.id DESC"
    ).fetchall()
    flagged = get_db().execute(
        "SELECT code, hostname FROM equipment WHERE status = ? ORDER BY code",
        (STATUS_REINTERVENTION,),
    ).fetchall()
    return render_template("validaciones/index.html", rows=rows, flagged=flagged)


@bp.route("/nueva", methods=("GET", "POST"))
@admin_required
def create():
    db = get_db()
    values = {}
    if request.method == "POST":
        values = {k: request.form.get(k, "").strip()
                  for k in ("equipment_id", "result", "observations")}
        errors, maintenance = [], None
        if not values["equipment_id"].isdigit() or db.execute(
                "SELECT 1 FROM equipment WHERE id = ?", (values["equipment_id"],)).fetchone() is None:
            errors.append("Debe seleccionar un equipo válido.")
        else:
            maintenance = db.execute(
                "SELECT id FROM maintenance WHERE equipment_id = ?"
                " ORDER BY performed_on DESC, id DESC LIMIT 1", (values["equipment_id"],)
            ).fetchone()
            if maintenance is None:
                errors.append("El equipo no registra mantenimientos: debe ser intervenido "
                              "antes de validar su funcionamiento.")
        if values["result"] not in RESULTS:
            errors.append("El resultado de la prueba debe ser OK o Falla.")
        if values["result"] == "Falla" and not values["observations"]:
            errors.append("Debe indicar observaciones cuando el resultado es Falla.")
        if not errors:
            db.execute(
                "INSERT INTO validation (equipment_id, maintenance_id, validated_by, result,"
                " observations) VALUES (?, ?, ?, ?, ?)",
                (values["equipment_id"], maintenance["id"], g.user["id"], values["result"],
                 values["observations"]),
            )
            new_status = STATUS_OK if values["result"] == "OK" else STATUS_REINTERVENTION
            db.execute("UPDATE equipment SET status = ? WHERE id = ?",
                       (new_status, values["equipment_id"]))
            db.commit()
            if values["result"] == "OK":
                flash("Validación registrada: el equipo quedó operativo.", "success")
            else:
                flash("Validación registrada: el equipo requiere nueva intervención.", "success")
            return redirect(url_for("validaciones.index"))
        for message in errors:
            flash(message, "error")
    equipment = db.execute("SELECT id, code, hostname, status FROM equipment ORDER BY code").fetchall()
    return render_template("validaciones/form.html", values=values, equipment=equipment,
                           results=RESULTS)
