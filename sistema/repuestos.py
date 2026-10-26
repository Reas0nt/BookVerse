"""Spare parts inventory (RF-09, course guideline): parts and stock movements."""
from datetime import date

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)

from .auth import admin_required, login_required
from .db import get_db
from .mantenimientos import parse_date

bp = Blueprint("repuestos", __name__, url_prefix="/repuestos")

PART_STATUSES = ("en buen estado", "en reparación", "fuera de servicio")
MOVEMENT_KINDS = ("ingreso", "salida")


def parse_quantity(raw, allow_zero=False):
    """Return a non-negative/positive int, or None when invalid."""
    raw = raw.strip()
    if not raw.isdigit():
        return None
    value = int(raw)
    return value if value > 0 or (allow_zero and value == 0) else None


@bp.route("/")
@login_required
def index():
    parts = get_db().execute("SELECT * FROM part ORDER BY type, name").fetchall()
    return render_template("repuestos/index.html", parts=parts, statuses=PART_STATUSES)


@bp.route("/nuevo", methods=("GET", "POST"))
@admin_required
def create():
    values = {}
    if request.method == "POST":
        values = {k: request.form.get(k, "").strip()
                  for k in ("type", "name", "quantity", "status")}
        errors = []
        if not values["type"]:
            errors.append("El tipo de repuesto es obligatorio.")
        if not values["name"]:
            errors.append("El nombre del repuesto es obligatorio.")
        quantity = parse_quantity(values["quantity"] or "0", allow_zero=True)
        if quantity is None:
            errors.append("La cantidad debe ser un número entero mayor o igual a cero.")
        if values["status"] not in PART_STATUSES:
            errors.append("Estado del repuesto no válido.")
        if not errors:
            db = get_db()
            db.execute("INSERT INTO part (type, name, quantity, status) VALUES (?, ?, ?, ?)",
                       (values["type"], values["name"], quantity, values["status"]))
            db.commit()
            flash("Repuesto registrado.", "success")
            return redirect(url_for("repuestos.index"))
        for message in errors:
            flash(message, "error")
    return render_template("repuestos/form.html", values=values, statuses=PART_STATUSES)


@bp.route("/<int:part_id>/estado", methods=("POST",))
@admin_required
def set_status(part_id):
    status = request.form.get("status", "")
    if status not in PART_STATUSES:
        flash("Estado del repuesto no válido.", "error")
    else:
        db = get_db()
        cur = db.execute("UPDATE part SET status = ? WHERE id = ?", (status, part_id))
        db.commit()
        flash("Estado actualizado." if cur.rowcount else "El repuesto no existe.",
              "success" if cur.rowcount else "error")
    return redirect(url_for("repuestos.index"))


@bp.route("/movimientos/nuevo", methods=("GET", "POST"))
@login_required
def movement():
    db = get_db()
    values = {"moved_on": date.today().isoformat()}
    if request.method == "POST":
        values = {k: request.form.get(k, "").strip()
                  for k in ("part_id", "kind", "quantity", "moved_on", "note")}
        errors = []
        part = None
        if values["part_id"].isdigit():
            part = db.execute("SELECT * FROM part WHERE id = ?", (values["part_id"],)).fetchone()
        if part is None:
            errors.append("Debe seleccionar un repuesto válido.")
        if values["kind"] not in MOVEMENT_KINDS:
            errors.append("Tipo de movimiento no válido.")
        quantity = parse_quantity(values["quantity"])
        if quantity is None:
            errors.append("La cantidad debe ser un número entero positivo.")
        moved = parse_date(values["moved_on"])
        if moved is None:
            errors.append("La fecha no es válida (use el formato AAAA-MM-DD).")
        elif moved > date.today():
            errors.append("La fecha del movimiento no puede ser futura.")
        if not errors:
            delta = quantity if values["kind"] == "ingreso" else -quantity
            # Guarded update keeps stock from ever going negative.
            cur = db.execute(
                "UPDATE part SET quantity = quantity + ? WHERE id = ? AND quantity + ? >= 0",
                (delta, part["id"], delta),
            )
            if cur.rowcount == 0:
                errors.append(f"Stock insuficiente: hay {part['quantity']} unidad(es) de "
                              f"'{part['name']}' y se intentó retirar {quantity}.")
            else:
                db.execute(
                    "INSERT INTO part_movement (part_id, technician_id, kind, quantity, moved_on,"
                    " note) VALUES (?, ?, ?, ?, ?, ?)",
                    (part["id"], g.user["id"], values["kind"], quantity, values["moved_on"],
                     values["note"]),
                )
                db.commit()
                flash("Movimiento registrado; el stock fue actualizado.", "success")
                return redirect(url_for("repuestos.index"))
        for message in errors:
            flash(message, "error")
    parts = db.execute("SELECT id, name, quantity FROM part ORDER BY name").fetchall()
    return render_template("repuestos/movement_form.html", values=values, parts=parts,
                           kinds=MOVEMENT_KINDS)


@bp.route("/movimientos")
@login_required
def movements():
    rows = get_db().execute(
        "SELECT pm.*, p.name AS part_name, u.full_name AS technician FROM part_movement pm"
        " JOIN part p ON p.id = pm.part_id JOIN user u ON u.id = pm.technician_id"
        " ORDER BY pm.moved_on DESC, pm.id DESC"
    ).fetchall()
    return render_template("repuestos/movements.html", rows=rows)
