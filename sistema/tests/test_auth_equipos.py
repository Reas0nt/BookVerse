from sistema.db import get_db


def test_anonymous_is_redirected_to_login(client):
    for path in ("/", "/equipos/", "/equipos/nuevo"):
        response = client.get(path)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_login_success_and_logout(client, auth):
    response = auth.login_tecnico()
    assert response.status_code == 302
    assert client.get("/").status_code == 200
    client.post("/logout")
    assert client.get("/").status_code == 302


def test_login_wrong_password_shows_error(client, auth):
    response = auth.login("tecnico", "mala-clave")
    assert response.status_code == 200
    assert "Usuario o contraseña incorrectos" in response.get_data(as_text=True)
    assert client.get("/equipos/").status_code == 302


def test_login_ignores_external_next(client):
    response = client.post("/login?next=//evil.example",
                           data={"username": "admin", "password": "admin123"})
    assert response.headers["Location"] == "/"


def test_passwords_are_hashed(app):
    with app.app_context():
        row = get_db().execute("SELECT password_hash FROM user WHERE username = 'admin'").fetchone()
    assert row["password_hash"] != "admin123"


def test_equipment_list_shows_seed_data(client, auth):
    auth.login_tecnico()
    html = client.get("/equipos/").get_data(as_text=True)
    assert "EQ-001" in html and "EQ-003" in html


def test_create_equipment(client, auth, app):
    auth.login_admin()
    response = client.post("/equipos/nuevo", data={
        "code": "EQ-010", "hostname": "BV-TEST", "type": "PC",
        "location": "Oficina", "serial_number": "SN-X"}, follow_redirects=True)
    assert "Equipo registrado" in response.get_data(as_text=True)
    with app.app_context():
        assert get_db().execute("SELECT 1 FROM equipment WHERE code = 'EQ-010'").fetchone()


def test_create_equipment_rejects_duplicate_code(client, auth):
    auth.login_admin()
    response = client.post("/equipos/nuevo", data={
        "code": "EQ-001", "hostname": "X", "type": "PC",
        "location": "Y", "serial_number": "Z"})
    assert "Ya existe un equipo con ese código" in response.get_data(as_text=True)


def test_create_equipment_validates_input(client, auth):
    auth.login_admin()
    response = client.post("/equipos/nuevo", data={
        "code": "ABC", "hostname": "", "type": "Toaster",
        "location": "Y", "serial_number": "Z"})
    html = response.get_data(as_text=True)
    assert "formato EQ-NNN" in html
    assert "Nombre de host es obligatorio" in html
    assert "Tipo de equipo no válido" in html


def test_technician_cannot_register_equipment(client, auth, app):
    auth.login_tecnico()
    assert client.get("/equipos/nuevo").status_code == 403
    response = client.post("/equipos/nuevo", data={
        "code": "EQ-011", "hostname": "BV-T", "type": "PC",
        "location": "Oficina", "serial_number": "SN-Y"})
    assert response.status_code == 403
    assert "Registrar equipo" not in client.get("/equipos/").get_data(as_text=True)
    with app.app_context():
        assert get_db().execute("SELECT 1 FROM equipment WHERE code = 'EQ-011'").fetchone() is None
