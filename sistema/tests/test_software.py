from sistema.db import get_db


def update_data(**overrides):
    data = {"software_name": "Google Chrome", "equipment_id": 1, "previous_version": "126.0",
            "new_version": "127.0", "updated_on": "2026-05-05", "method": "manual",
            "changes": "Parches de seguridad"}
    data.update(overrides)
    return data


def test_software_pages_require_login(client):
    for path in ("/software/", "/software/actualizar", "/software/actualizaciones"):
        assert client.get(path).status_code == 302


def test_register_software_update(client, auth, app):
    auth.login_tecnico()
    response = client.post("/software/actualizar", data=update_data(), follow_redirects=True)
    html = response.get_data(as_text=True)
    assert "Actualización de software registrada" in html
    assert "126.0" in html and "127.0" in html
    with app.app_context():
        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM software_update").fetchone()[0] == 1
        version = db.execute(
            "SELECT current_version FROM software WHERE name = 'Google Chrome'").fetchone()[0]
    assert version == "127.0"


def test_update_unregistered_software_shows_register_first_message(client, auth, app):
    auth.login_tecnico()
    response = client.post("/software/actualizar", data=update_data(software_name="Photoshop"))
    html = response.get_data(as_text=True)
    assert "no está en el listado de aplicaciones" in html
    assert "Debe registrarse primero" in html
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM software_update").fetchone()[0] == 0


def test_update_validates_input(client, auth):
    auth.login_tecnico()
    html = client.post("/software/actualizar", data=update_data(
        equipment_id="", previous_version="", new_version="", updated_on="mañana",
        method="telepatia")).get_data(as_text=True)
    for text in ("equipo válido", "versión anterior es obligatoria", "versión nueva es obligatoria",
                 "La fecha no es válida", "Método de actualización no válido"):
        assert text in html


def test_update_rejects_same_version(client, auth):
    auth.login_tecnico()
    html = client.post("/software/actualizar", data=update_data(new_version="126.0")
                       ).get_data(as_text=True)
    assert "debe ser distinta" in html


def test_tecnico_cannot_manage_catalog(client, auth):
    auth.login_tecnico()
    assert client.get("/software/nuevo").status_code == 403
    assert client.post("/software/nuevo", data={"name": "X", "current_version": "1"}).status_code == 403


def test_admin_registers_software_then_update_works(client, auth, app):
    auth.login_admin()
    response = client.post("/software/nuevo", data={
        "name": "Photoshop", "current_version": "25.0", "description": "Diseño"},
        follow_redirects=True)
    assert "Software registrado en el listado" in response.get_data(as_text=True)
    response = client.post("/software/actualizar", data=update_data(
        software_name="photoshop", previous_version="25.0", new_version="26.0"),
        follow_redirects=True)
    assert "Actualización de software registrada" in response.get_data(as_text=True)


def test_admin_catalog_validation_and_duplicates(client, auth):
    auth.login_admin()
    html = client.post("/software/nuevo", data={"name": "", "current_version": ""}
                       ).get_data(as_text=True)
    assert "nombre del software es obligatorio" in html and "versión actual es obligatoria" in html
    html = client.post("/software/nuevo", data={"name": "Google Chrome", "current_version": "1"}
                       ).get_data(as_text=True)
    assert "Ya existe un software con ese nombre" in html
