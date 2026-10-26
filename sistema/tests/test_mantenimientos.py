import sqlite3

from sistema.db import get_db


def add_maintenance(client, equipment_id=1, mtype="preventivo", performed_on="2026-03-10",
                    description="Limpieza interna", observations="Sin novedades"):
    return client.post("/mantenimientos/nuevo", data={
        "equipment_id": equipment_id, "type": mtype, "performed_on": performed_on,
        "description": description, "observations": observations}, follow_redirects=True)


def test_register_requires_login(client):
    assert client.get("/mantenimientos/nuevo").status_code == 302
    assert client.post("/mantenimientos/nuevo", data={}).status_code == 302


def test_register_maintenance_saves_record(client, auth, app):
    auth.login_tecnico()
    response = add_maintenance(client)
    assert "Mantenimiento registrado correctamente" in response.get_data(as_text=True)
    with app.app_context():
        row = get_db().execute("SELECT * FROM maintenance").fetchone()
    assert row["type"] == "preventivo" and row["equipment_id"] == 1


def test_register_rejects_invalid_input(client, auth, app):
    auth.login_tecnico()
    response = client.post("/mantenimientos/nuevo", data={
        "equipment_id": "", "type": "otro", "performed_on": "31-02-2026", "description": ""})
    html = response.get_data(as_text=True)
    assert "Debe seleccionar un equipo" in html
    assert "Tipo de mantenimiento no válido" in html
    assert "La fecha no es válida" in html
    assert "La descripción es obligatoria" in html
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM maintenance").fetchone()[0] == 0


def test_register_rejects_future_date_and_unknown_equipment(client, auth):
    auth.login_tecnico()
    html = add_maintenance(client, performed_on="2999-01-01").get_data(as_text=True)
    assert "no puede ser futura" in html
    html = add_maintenance(client, equipment_id=999).get_data(as_text=True)
    assert "El equipo seleccionado no existe" in html


def seed_history(client):
    add_maintenance(client, 1, "preventivo", "2026-01-10", "Limpieza")
    add_maintenance(client, 2, "correctivo", "2026-02-15", "Cambio de disco")
    add_maintenance(client, 3, "preventivo", "2026-03-20", "Cambio de toner")


def test_history_requires_login(client):
    assert client.get("/mantenimientos/").status_code == 302


def test_history_lists_and_filters(client, auth):
    auth.login_admin()
    seed_history(client)
    html = client.get("/mantenimientos/").get_data(as_text=True)
    assert "EQ-001" in html and "EQ-002" in html and "EQ-003" in html

    html = client.get("/mantenimientos/?tipo=correctivo").get_data(as_text=True)
    assert "EQ-002" in html and "EQ-001" not in html

    html = client.get("/mantenimientos/?desde=2026-02-01&hasta=2026-03-01").get_data(as_text=True)
    assert "EQ-002" in html and "EQ-001" not in html and "EQ-003" not in html

    html = client.get("/mantenimientos/?equipo=EQ-003").get_data(as_text=True)
    assert "EQ-003" in html and "EQ-001" not in html

    html = client.get("/mantenimientos/?equipo=SN-NB-0002").get_data(as_text=True)
    assert "EQ-002" in html and "EQ-001" not in html


def test_history_empty_result_message(client, auth):
    auth.login_admin()
    html = client.get("/mantenimientos/?equipo=NOPE").get_data(as_text=True)
    assert "No se encontraron registros" in html


def test_history_rejects_invalid_filters(client, auth):
    auth.login_admin()
    html = client.get("/mantenimientos/?desde=xx&tipo=zzz").get_data(as_text=True)
    assert "no es válida" in html and "Tipo de mantenimiento no válido" in html
    html = client.get("/mantenimientos/?desde=2026-05-01&hasta=2026-01-01").get_data(as_text=True)
    assert "no puede ser posterior" in html


def test_detail_shows_all_fields(client, auth):
    auth.login_admin()
    add_maintenance(client, 1, "correctivo", "2026-04-02", "Reemplazo de fuente", "Ruido en ventilador")
    html = client.get("/mantenimientos/1").get_data(as_text=True)
    for text in ("2026-04-02", "Correctivo", "Reemplazo de fuente", "Ruido en ventilador",
                 "Administrador BookVerse", "EQ-001"):
        assert text in html


def test_detail_not_found(client, auth):
    auth.login_admin()
    assert client.get("/mantenimientos/999").status_code == 404


def test_history_database_error_shows_message(client, auth, monkeypatch):
    auth.login_admin()

    def broken_db():
        raise sqlite3.OperationalError("unable to open database file")

    monkeypatch.setattr("sistema.mantenimientos.get_db", broken_db)
    response = client.get("/mantenimientos/")
    assert response.status_code == 503
    assert "No fue posible acceder a la base de datos" in response.get_data(as_text=True)
