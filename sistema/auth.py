"""Authentication blueprint and access-control decorators."""
import functools

from flask import (Blueprint, abort, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint("auth", __name__)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username, full_name, role FROM user WHERE id = ?", (user_id,)
        ).fetchone()


def login_required(view):
    """Redirect anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped(**kwargs):
        if g.user is None:
            flash("Debe iniciar sesión para continuar.", "error")
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)
    return wrapped


def admin_required(view):
    """Allow only administrators; technicians receive 403."""
    @functools.wraps(view)
    @login_required
    def wrapped(**kwargs):
        if g.user["role"] != "administrador":
            abort(403)
        return view(**kwargs)
    return wrapped


def _safe_next(target):
    """Only allow local relative redirects after login."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return url_for("index")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Usuario o contraseña incorrectos.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(_safe_next(request.args.get("next")))
    return render_template("auth/login.html")


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("auth.login"))
