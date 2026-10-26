"""Build Excalidraw diagrams (.excalidraw) and render them to PNG.

Rendering: the .excalidraw JSON is posted to kroki.io (SVG with the embedded
Virgil font) and rasterized with headless Firefox. Requires internet + Firefox.

Usage: python semana11-evaluacion/generar_diagramas.py [name ...]
"""
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "diagramas"

BLUE, GREEN, YELLOW, RED, PURPLE = "#a5d8ff", "#b2f2bb", "#ffec99", "#ffc9c9", "#d0bfff"
INK = "#1e1e1e"
FONT_FACTOR = 0.58  # approximate Virgil glyph width / font size
LINE_HEIGHT = 1.25


class Diagram:
    """Declarative builder: box(), arrow(), label()."""

    def __init__(self):
        self.elements = []
        self._n = 0

    def _id(self, prefix):
        self._n += 1
        return f"{prefix}{self._n}"

    def _base(self, type_, x, y, w, h, **kw):
        el = {
            "id": self._id(type_[:3]), "type": type_, "x": x, "y": y,
            "width": w, "height": h, "angle": 0,
            "strokeColor": kw.get("stroke", INK),
            "backgroundColor": kw.get("fill", "transparent"),
            "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": kw.get("style", "solid"),
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": {"type": 3} if type_ == "rectangle" else None,
            "seed": 1000 + self._n * 37, "version": 1, "versionNonce": 1,
            "isDeleted": False, "boundElements": [], "updated": 1,
            "link": None, "locked": False,
        }
        self.elements.append(el)
        return el

    @staticmethod
    def measure(text, size):
        lines = text.split("\n")
        return (max(len(s) for s in lines) * size * FONT_FACTOR,
                len(lines) * size * LINE_HEIGHT)

    def _text(self, x, y, w, h, text, size, container=None, color=INK):
        tw, th = self.measure(text, size)
        el = self._base("text", x, y, w, h, stroke=color)
        el.update({
            "text": text, "originalText": text, "fontSize": size, "fontFamily": 1,
            "textAlign": "center", "verticalAlign": "middle",
            "containerId": container["id"] if container else None,
            "lineHeight": LINE_HEIGHT, "autoResize": False,
        })
        if container:
            container["boundElements"].append({"type": "text", "id": el["id"]})
        return el

    def box(self, x, y, w, h, text, fill=BLUE, size=22, shape="rectangle", title=None):
        """Shape with bound text. With `title`, draws a header band above the body.

        Returns a dict with the combined bounds used by arrow().
        """
        top = y
        if title:
            head_h = size * LINE_HEIGHT + 22
            head = self._base(shape, x, y, w, head_h, fill=fill)
            _, tth = self.measure(title, size + 2)
            self._text(x, y + (head_h - tth) / 2, w, tth, title, size + 2, head)
            top, h = y + head_h, h - head_h
            body_fill = "#ffffff"
        else:
            body_fill = fill
        body = self._base(shape, x, top, w, h, fill=body_fill)
        tw, th = self.measure(text, size)
        if tw > w - 16 or th > h - 8:
            print(f"  WARN text may overflow box: {text!r} ({tw:.0f}x{th:.0f} in {w}x{h})")
        self._text(x + 8, top + (h - th) / 2, w - 16, th, text, size, body)
        return {"id": body["id"], "el": body, "x": x, "y": y, "w": w, "h": (top - y) + h}

    def label(self, x, y, text, size=22, color=INK, w=None):
        tw, th = self.measure(text, size)
        w = w or tw
        return self._text(x, y, w, th, text, size, color=color)

    @staticmethod
    def _clip(a, b, gap):
        """Point on the border of rect `a` toward the center of rect `b`."""
        ax, ay = a["x"] + a["w"] / 2, a["y"] + a["h"] / 2
        bx, by = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
        dx, dy = bx - ax, by - ay
        sx = (a["w"] / 2 + gap) / abs(dx) if dx else float("inf")
        sy = (a["h"] / 2 + gap) / abs(dy) if dy else float("inf")
        s = min(sx, sy)
        return ax + dx * s, ay + dy * s

    def arrow(self, a, b, both=False, style="solid"):
        x1, y1 = self._clip(a, b, 6)
        x2, y2 = self._clip(b, a, 6)
        el = self._base("arrow", x1, y1, abs(x2 - x1), abs(y2 - y1), style=style)
        el.update({
            "points": [[0, 0], [x2 - x1, y2 - y1]],
            "startBinding": {"elementId": a["id"], "focus": 0, "gap": 4},
            "endBinding": {"elementId": b["id"], "focus": 0, "gap": 4},
            "startArrowhead": "arrow" if both else None, "endArrowhead": "arrow",
            "lastCommittedPoint": None, "elbowed": False,
        })
        for ref in (a, b):
            ref["el"]["boundElements"].append({"type": "arrow", "id": el["id"]})
        return el

    def save(self, path):
        data = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
                "elements": self.elements,
                "appState": {"viewBackgroundColor": "#ffffff"}, "files": {}}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- rendering
def render_png(excalidraw_path, png_path):
    req = urllib.request.Request(
        "https://kroki.io/excalidraw/svg", data=excalidraw_path.read_bytes(),
        headers={"Content-Type": "text/plain", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}, method="POST")
    svg = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    vb = re.search(r'viewBox="([\d.\s-]+)"', svg).group(1).split()
    w, h = (int(float(v)) for v in vb[2:4])
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "d.svg").write_text(svg, encoding="utf-8")
        (tmp / "d.html").write_text(
            '<html><body style="margin:0;background:#fff">'
            f'<img src="d.svg" style="width:{2 * w}px;height:{2 * h}px"></body></html>')
        profile = tempfile.mkdtemp(dir=tmp)
        subprocess.run(
            ["timeout", "60", "firefox", "--headless", "--no-remote", "--profile", profile,
             "--screenshot", str(png_path), f"--window-size={2 * w},{2 * h}",
             (tmp / "d.html").as_uri()],
            check=True, capture_output=True)


# ---------------------------------------------------------------- diagrams
def proceso():
    d = Diagram()
    bw, bh, gap = 250, 190, 40
    weeks = [
        ("S7 · Avance 1\nRF-06\nRegistro de\nmantenimiento", BLUE),
        ("S8 · Avance 2\nRF-07\nActualización de\nsoftware + VM", BLUE),
        ("S9 · Avance 3\nRF-08\nHistorial de\nmantenimiento", BLUE),
        ("S10 · Avance 4\nRF-09\nInventario de\nrepuestos", BLUE),
        ("S11\nEvaluación\npráctica", YELLOW),
    ]
    d.label(0, 0, "Proceso de trabajo de la Etapa II (semanas 7 a 11)", 28, w=5 * bw + 4 * gap)
    boxes = [d.box(i * (bw + gap), 60, bw, bh, t, c, 22) for i, (t, c) in enumerate(weeks)]
    for a, b in zip(boxes, boxes[1:]):
        d.arrow(a, b)
    total = 5 * bw + 4 * gap
    d.label(0, 60 + bh + 70, "Criterios de la rúbrica de evaluación", 28, w=total)
    cw, cg = 400, 55
    x0 = (total - (3 * cw + 2 * cg)) / 2
    crit = [("1. Planificación", GREEN), ("2. Instalación y\nconfiguración", GREEN),
            ("3. Validación", GREEN)]
    cb = [d.box(x0 + i * (cw + cg), 60 + bh + 125, cw, 110, t, c, 26)
          for i, (t, c) in enumerate(crit)]
    for a, b in zip(cb, cb[1:]):
        d.arrow(a, b)
    return d


def arquitectura():
    d = Diagram()
    d.label(0, 0, "Arquitectura del sistema web de apoyo", 28, w=1670)
    y0 = 90
    tec = d.box(0, y0, 250, 100, "Técnico", PURPLE, 24)
    adm = d.box(0, y0 + 160, 250, 100, "Administrador", PURPLE, 24)
    nav = d.box(340, y0 + 80, 220, 100, "Navegador\nweb", YELLOW, 24)
    # Flask container
    mw, mh, mg = 180, 90, 20
    fx, fw, fh = 650, 3 * mw + 4 * mg, 2 * mh + 2 * mg + 50
    frame = d.box(fx, y0 - 20, fw, fh + 40, "", BLUE, 22, title="Aplicación Flask")
    mods = ["auth", "equipos", "mantenimientos", "software", "validaciones", "repuestos"]
    for i, m in enumerate(mods):
        r, c = divmod(i, 3)
        d.box(fx + mg + c * (mw + mg), y0 + 50 + r * (mh + mg), mw, mh, m, GREEN, 20)
    db = d.box(1450, y0 + 80, 220, 100, "Base de datos\nSQLite", RED, 24)
    d.arrow(tec, nav)
    d.arrow(adm, nav)
    d.arrow(nav, frame, both=True)
    d.arrow(frame, db, both=True)
    d.label(0, y0 + fh + 40, "Python 3.12 · Flask · SQLite", 24, w=1670)
    return d


def modelo_datos():
    d = Diagram()
    w, h, gx, gy = 370, 200, 100, 130
    d.label(0, 0, "Modelo de datos (schema.sql)", 28, w=4 * w + 3 * gx)

    def ent(col, row, title, fields, fill):
        return d.box(col * (w + gx), 60 + row * (h + gy), w, h, "\n".join(fields), fill, 20,
                     title=title)

    software = ent(0, 0, "software (software)", ["id", "name", "current_version"], GREEN)
    s_upd = ent(1, 0, "software_update", ["id", "software_id (FK)", "equipment_id (FK)",
                                          "previous_version → new_version"], GREEN)
    equip = ent(2, 0, "equipment (equipos)", ["id", "code", "hostname", "type",
                                              "serial_number"], BLUE)
    valid = ent(3, 0, "validation (validaciones)", ["id", "equipment_id (FK)",
                                                    "maintenance_id (FK)", "result: OK / Falla"],
                YELLOW)
    part = ent(0, 1, "part (repuestos)", ["id", "name", "quantity (≥ 0)", "status"], PURPLE)
    p_mov = ent(1, 1, "part_movement", ["id", "part_id (FK)", "technician_id (FK)",
                                        "kind: ingreso / salida"], PURPLE)
    user = ent(2, 1, "user (usuarios)", ["id", "username", "full_name",
                                         "role: administrador / tecnico"], RED)
    maint = ent(3, 1, "maintenance", ["id", "equipment_id (FK)", "technician_id (FK)",
                                      "type: preventivo / correctivo", "performed_on"], BLUE)
    for a, b in [(s_upd, software), (s_upd, equip), (valid, equip), (valid, maint),
                 (maint, equip), (maint, user), (p_mov, part), (p_mov, user)]:
        d.arrow(a, b)
    yb = 60 + 2 * h + gy + 40
    d.label(0, yb, "Flecha = clave foránea (FK) hacia la tabla referenciada.", 20,
            w=4 * w + 3 * gx)
    return d


def error_kvm():
    d = Diagram()
    bw, bh, gap = 340, 230, 70
    total = 4 * bw + 3 * gap
    d.label(0, 0, "Error detectado durante la instalación de la máquina virtual", 28, w=total)
    steps = [
        ("1. Problema", "La VM no inicia:\nVERR_VMX_IN_\nVMX_ROOT_MODE", RED),
        ("2. Causa", "El módulo KVM del\nanfitrión ocupa\nVT-x (kernel 6.14)", YELLOW),
        ("3. Solución", "modprobe -r\nkvm_intel kvm\n+ enable_virt_\nat_load=0", BLUE),
        ("4. Resultado", "La VM inicia\ncorrectamente", GREEN),
    ]
    boxes = []
    for i, (title, body, color) in enumerate(steps):
        x = i * (bw + gap)
        d.label(x, 70, title, 26, w=bw)
        boxes.append(d.box(x, 120, bw, bh, body, color, 26))
    for a, b in zip(boxes, boxes[1:]):
        d.arrow(a, b)
    return d


DIAGRAMS = {"proceso": proceso, "arquitectura": arquitectura,
            "modelo_datos": modelo_datos, "error_kvm": error_kvm}


def main(names):
    OUT_DIR.mkdir(exist_ok=True)
    for name in names or DIAGRAMS:
        print(f"Building {name}")
        src = OUT_DIR / f"{name}.excalidraw"
        DIAGRAMS[name]().save(src)
        render_png(src, OUT_DIR / f"{name}.png")


if __name__ == "__main__":
    main(sys.argv[1:])
