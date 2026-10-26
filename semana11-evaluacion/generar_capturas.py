"""Capture screenshots of the BookVerse web system for the presentation.

Loads realistic sample data into a temporary database through the Flask test
client, saves each page as HTML and screenshots it with headless Firefox.

Usage (from the repo root): venv/bin/python semana11-evaluacion/generar_capturas.py
"""
import re
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sistema import create_app  # noqa: E402
from sistema.db import init_db  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent / "capturas"
CSS_URI = (ROOT / "sistema" / "static" / "style.css").as_uri()
# (file name, url, logged in, viewport height)
PAGES = [
    ("login", "/login", False, 800),
    ("historial_mantenimientos", "/mantenimientos/", True, 800),
    ("registro_mantenimiento", "/mantenimientos/nuevo", True, 800),
    ("repuestos", "/repuestos/", True, 1000),
    ("actualizaciones_software", "/software/actualizaciones", True, 800),
]


def prefill_form(html):
    """Fill the empty maintenance form so the screenshot shows realistic input."""
    html = html.replace('<option value="2" >', '<option value="2" selected>', 1)
    html = html.replace('<option value="correctivo" >', '<option value="correctivo" selected>', 1)
    html = html.replace('required></textarea>',
                        'required>Reemplazo de disco SSD con sectores dañados.</textarea>', 1)
    return html.replace('rows="3"></textarea>',
                        'rows="3">Se restauró el respaldo del usuario.</textarea>', 1)


def days_ago(n):
    return (date.today() - timedelta(days=n)).isoformat()


def load_sample_data(client):
    client.post("/login", data={"username": "admin", "password": "admin123"})
    maintenances = [
        {"equipment_id": "1", "type": "preventivo", "performed_on": days_ago(21),
         "description": "Limpieza interna, revisión de ventiladores y cambio de pasta térmica.",
         "observations": "Sin hallazgos adicionales."},
        {"equipment_id": "2", "type": "correctivo", "performed_on": days_ago(12),
         "description": "Reemplazo de disco SSD con sectores dañados y reinstalación del sistema.",
         "observations": "Se restauró el respaldo del usuario."},
        {"equipment_id": "3", "type": "correctivo", "performed_on": days_ago(5),
         "description": "Cambio de cartucho de tóner y limpieza del rodillo de arrastre.",
         "observations": "Impresión de prueba correcta."},
    ]
    for data in maintenances:
        client.post("/mantenimientos/nuevo", data=data)
    client.post("/software/actualizar", data={
        "software_name": "Google Chrome", "equipment_id": "1", "previous_version": "125.0",
        "new_version": "126.0", "updated_on": days_ago(7), "method": "manual",
        "changes": "Actualización de seguridad del navegador."})
    client.post("/software/actualizar", data={
        "software_name": "Antivirus ESET", "equipment_id": "2", "previous_version": "16.2",
        "new_version": "17.0", "updated_on": days_ago(3), "method": "remota",
        "changes": "Nueva versión del motor de detección."})
    client.post("/repuestos/movimientos/nuevo", data={
        "part_id": "1", "kind": "salida", "quantity": "1", "moved_on": days_ago(12),
        "note": "Reemplazo de disco en EQ-002."})
    client.post("/repuestos/movimientos/nuevo", data={
        "part_id": "3", "kind": "ingreso", "quantity": "2", "moved_on": days_ago(4),
        "note": "Compra de tóner."})
    client.post("/repuestos/1/estado", data={"status": "en buen estado"})
    client.post("/repuestos/nuevo", data={
        "type": "Memoria", "name": "RAM DDR3 4 GB", "quantity": "2", "status": "en reparación"})
    client.post("/repuestos/nuevo", data={
        "type": "Energía", "name": "Fuente de poder 500 W", "quantity": "1",
        "status": "fuera de servicio"})


def screenshot(html, png, height=800):
    profile = tempfile.mkdtemp()
    subprocess.run(
        ["timeout", "60", "firefox", "--headless", "--no-remote", "--profile", profile,
         "--screenshot", str(png), f"--window-size=1280,{height}", html.as_uri()],
        check=True, capture_output=True)
    trim_bottom(png)


def trim_bottom(png, pad=32):
    """Crop the empty page background below the last piece of content."""
    from PIL import Image, ImageChops
    img = Image.open(png).convert("RGB")
    bg = Image.new("RGB", img.size, img.getpixel((5, img.height - 5)))
    bbox = ImageChops.difference(img, bg).getbbox()
    if bbox:
        img.crop((0, 0, img.width, min(img.height, bbox[3] + pad))).save(png)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        app = create_app({"DATABASE": str(tmp / "capturas.db"), "TESTING": True})
        with app.app_context():
            init_db()
        admin = app.test_client()
        load_sample_data(admin)
        admin.get("/")  # consume the flash messages left by the sample data
        anonymous = app.test_client()
        for name, url, logged, height in PAGES:
            resp = (admin if logged else anonymous).get(url)
            assert resp.status_code == 200, (url, resp.status_code)
            html = re.sub(r'href="[^"]*style\.css[^"]*"', f'href="{CSS_URI}"',
                          resp.get_data(as_text=True))
            if name == "registro_mantenimiento":
                html = prefill_form(html)
            page = tmp / f"{name}.html"
            page.write_text(html, encoding="utf-8")
            screenshot(page, OUT_DIR / f"{name}.png", height)
            print("Captured", name)


if __name__ == "__main__":
    main()
