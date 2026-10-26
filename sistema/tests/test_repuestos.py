from sistema.db import get_db


def movement(client, part_id=1, kind="ingreso", quantity="2", moved_on="2026-05-01", note=""):
    return client.post("/repuestos/movimientos/nuevo", data={
        "part_id": part_id, "kind": kind, "quantity": quantity,
        "moved_on": moved_on, "note": note}, follow_redirects=True)


def stock(app, part_id=1):
    with app.app_context():
        return get_db().execute("SELECT quantity FROM part WHERE id = ?", (part_id,)).fetchone()[0]


def test_inventory_requires_login(client):
    assert client.get("/repuestos/").status_code == 302
    assert client.get("/repuestos/movimientos/nuevo").status_code == 302


def test_inventory_lists_parts(client, auth):
    auth.login_tecnico()
    html = client.get("/repuestos/").get_data(as_text=True)
    assert "Disco SSD 480 GB" in html and "en buen estado" in html


def test_ingreso_increases_stock_immediately(client, auth, app):
    auth.login_tecnico()
    assert stock(app) == 5
    html = movement(client, kind="ingreso", quantity="3").get_data(as_text=True)
    assert "stock fue actualizado" in html
    assert stock(app) == 8
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM part_movement").fetchone()[0] == 1


def test_salida_decreases_stock_and_can_empty_it(client, auth, app):
    auth.login_tecnico()
    movement(client, kind="salida", quantity="2")
    assert stock(app) == 3
    movement(client, kind="salida", quantity="3")
    assert stock(app) == 0


def test_salida_larger_than_stock_is_rejected(client, auth, app):
    auth.login_tecnico()
    html = movement(client, kind="salida", quantity="6").get_data(as_text=True)
    assert "Stock insuficiente" in html
    assert stock(app) == 5
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM part_movement").fetchone()[0] == 0


def test_movement_validates_quantity_kind_date_and_part(client, auth, app):
    auth.login_tecnico()
    for qty in ("0", "-1", "abc", "1.5", ""):
        assert "entero positivo" in movement(client, quantity=qty).get_data(as_text=True)
    assert "Tipo de movimiento no válido" in movement(client, kind="robo").get_data(as_text=True)
    assert "La fecha no es válida" in movement(client, moved_on="ayer").get_data(as_text=True)
    assert "no puede ser futura" in movement(client, moved_on="2999-01-01").get_data(as_text=True)
    assert "repuesto válido" in movement(client, part_id=999).get_data(as_text=True)
    assert stock(app) == 5


def test_movements_list(client, auth):
    auth.login_tecnico()
    movement(client, kind="ingreso", quantity="1", note="Compra")
    html = client.get("/repuestos/movimientos").get_data(as_text=True)
    assert "Compra" in html and "Ingreso" in html


def test_tecnico_cannot_create_parts_or_change_status(client, auth):
    auth.login_tecnico()
    assert client.get("/repuestos/nuevo").status_code == 403
    assert client.post("/repuestos/1/estado", data={"status": "fuera de servicio"}).status_code == 403


def test_admin_creates_part_and_changes_status(client, auth, app):
    auth.login_admin()
    html = client.post("/repuestos/nuevo", data={
        "type": "Red", "name": "Switch 8 puertos", "quantity": "2", "status": "en reparación"},
        follow_redirects=True).get_data(as_text=True)
    assert "Repuesto registrado" in html and "Switch 8 puertos" in html
    client.post("/repuestos/1/estado", data={"status": "fuera de servicio"})
    with app.app_context():
        assert get_db().execute("SELECT status FROM part WHERE id = 1").fetchone()[0] == "fuera de servicio"


def test_admin_part_validation(client, auth):
    auth.login_admin()
    html = client.post("/repuestos/nuevo", data={
        "type": "", "name": "", "quantity": "-3", "status": "roto"}).get_data(as_text=True)
    for text in ("tipo de repuesto es obligatorio", "nombre del repuesto es obligatorio",
                 "mayor o igual a cero", "Estado del repuesto no válido"):
        assert text in html
