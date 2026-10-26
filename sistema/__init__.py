"""BookVerse office equipment maintenance system."""
import os

from flask import Flask, render_template

from . import auth, db, equipos, mantenimientos


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.path.join(app.instance_path, "sistema.db"),
    )
    if test_config is not None:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(equipos.bp)
    app.register_blueprint(mantenimientos.bp)

    @app.route("/")
    @auth.login_required
    def index():
        return render_template("index.html")

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    return app
