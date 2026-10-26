from sistema.db import get_db
from sistema.tests.test_mantenimientos import add_maintenance


def validate(client, equipment_id=1, result="OK", observations=""):
    return client.post("/validaciones/nueva", data={
        "equipment_id": equipment_id, "result": result, "observations": observations},
        follow_redirects=True)


def equipment_status(app, equipment_id=1):
    with app.app_context():
        return get_db().execute(
            "SELECT status FROM equipment WHERE id = ?", (equipment_id,)).fetchone()[0]


def test_tecnico_blocked_from_validations(client, auth):
    auth.login_tecnico()
    assert client.get("/validaciones/").status_code == 403
    assert client.get("/validaciones/nueva").status_code == 403
    assert client.post("/validaciones/nueva", data={"equipment_id": 1, "result": "OK"}).status_code == 403


def test_anonymous_redirected(client):
    assert client.get("/validaciones/").status_code == 302


def test_validation_requires_prior_maintenance(client, auth, app):
    auth.login_admin()
    html = validate(client).get_data(as_text=True)
    assert "no registra mantenimientos" in html
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM validation").fetchone()[0] == 0


def test_validation_ok_keeps_equipment_operational(client, auth, app):
    auth.login_admin()
    add_maintenance(client)
    html = validate(client, result="OK", observations="Todo funciona").get_data(as_text=True)
    assert "el equipo quedó operativo" in html
    assert equipment_status(app) == "operativo"


def test_validation_failure_flags_equipment_for_new_intervention(client, auth, app):
    auth.login_admin()
    add_maintenance(client)
    html = validate(client, result="Falla", observations="No enciende").get_data(as_text=True)
    assert "requiere nueva intervención" in html
    assert equipment_status(app) == "requiere nueva intervención"
    assert "EQ-001" in html  # listed among flagged equipment
    # a later successful validation clears the flag
    validate(client, result="OK")
    assert equipment_status(app) == "operativo"


def test_validation_failure_needs_observations_and_valid_result(client, auth, app):
    auth.login_admin()
    add_maintenance(client)
    assert "Debe indicar observaciones" in validate(client, result="Falla").get_data(as_text=True)
    assert "debe ser OK o Falla" in validate(client, result="Quizas").get_data(as_text=True)
    assert "equipo válido" in validate(client, equipment_id=999).get_data(as_text=True)
    assert equipment_status(app) == "operativo"
