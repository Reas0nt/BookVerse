"""Build the week 11 evaluation deck (python-pptx).

Usage (from the repo root): venv/bin/python semana11-evaluacion/generar_presentacion.py
Inputs: diagramas/*.png and capturas/*.png (see generar_diagramas.py and
generar_capturas.py). Output: Presentacion_Evaluacion_S11_BookVerse.pptx
"""
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

BASE = Path(__file__).resolve().parent
OUT = BASE / "Presentacion_Evaluacion_S11_BookVerse.pptx"
DIAG, CAP = BASE / "diagramas", BASE / "capturas"

BERRY, INK, AMBER = "6D2E46", "2B2D42", "F2A541"
TINT, WHITE, MUTED, LINE = "F4EEF1", "FFFFFF", "5B5D6E", "D9CBD2"
HEAD, BODY = "Cambria", "Calibri"
SW, SH = 13.333, 7.5
MX = 0.6                      # side margin
CW = SW - 2 * MX              # content width
TOP = 1.75                    # content top
BOTTOM = 7.0                  # content bottom


def rgb(hex_):
    return RGBColor.from_string(hex_)


# ------------------------------------------------------------------ helpers
def style_runs(paragraph, runs, size, color, bold, font):
    for item in runs:
        text, opts = (item, {}) if isinstance(item, str) else item
        run = paragraph.add_run()
        run.text = text
        f = run.font
        f.name = opts.get("font", font)
        f.size = Pt(opts.get("size", size))
        f.bold = opts.get("bold", bold)
        f.italic = opts.get("italic", False)
        f.color.rgb = rgb(opts.get("color", color))


def add_text(slide, x, y, w, h, paras, name, size=16, color=INK, bold=False, font=BODY,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space_after=0, margin=0.0):
    """Text box. `paras` is a str or a list of paragraphs (str or list of runs)."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    box.name = name
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(margin)
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        style_runs(p, [para] if isinstance(para, str) else para, size, color, bold, font)
    return box


def add_shape(slide, kind, x, y, w, h, fill, name, line=None, radius=None, dash=False):
    shp = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.name = name
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(2 if dash else 1)
        if dash:
            from pptx.enum.dml import MSO_LINE
            shp.line.dash_style = MSO_LINE.DASH
    else:
        shp.line.fill.background()
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = radius
    return shp


def card(slide, x, y, w, h, name, fill=TINT, line=None, dash=False):
    return add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, name,
                     line=line, radius=0.06, dash=dash)


def num_circle(slide, x, y, d, label, name, size=20, fill=AMBER, color=INK):
    """Motif: amber numbered circle."""
    c = add_shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill, name)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    style_runs(p, [label], size, color, True, BODY)
    return c


def add_picture_fit(slide, path, x, y, w, h, name, border=True, align="center"):
    """Place an image inside the box (x, y, w, h) keeping its aspect ratio."""
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    px = x + (w - pw) / 2 if align == "center" else x
    py = y + (h - ph) / 2 if align == "center" else y
    pic = slide.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(pw), Inches(ph))
    pic.name = name
    if border:
        pic.line.color.rgb = rgb(LINE)
        pic.line.width = Pt(1)
    return pic, (px, py, pw, ph)


def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def new_slide(prs, number, title, bg=WHITE):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(bg)
    if title:
        num_circle(slide, MX, 0.55, 0.75, str(number), "Numero de diapositiva")
        add_text(slide, 1.6, 0.45, SW - 1.6 - MX, 0.95, title, "Titulo", size=36, bold=True,
                 font=HEAD, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    return slide


def stat(slide, x, y, w, h, number, label, name, fill=TINT, num_color=BERRY, label_color=INK,
         num_size=44):
    card(slide, x, y, w, h, name + " (tarjeta)", fill=fill)
    add_text(slide, x + 0.25, y, 1.6, h, number, name + " (cifra)", size=num_size, bold=True,
             font=HEAD, color=num_color, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, x + 1.45, y, w - 1.65, h, label, name + " (texto)", size=16,
             color=label_color, anchor=MSO_ANCHOR.MIDDLE)


# ------------------------------------------------------------------- slides
def slide_portada(prs):
    s = new_slide(prs, 1, None, bg=INK)
    add_shape(s, MSO_SHAPE.OVAL, 8.15, 0.95, 4.6, 4.6, BERRY, "Circulo principal")
    add_text(s, 8.15, 1.7, 4.6, 0.5, "SEMANA", "Etiqueta semana", size=20, bold=True,
             color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, 8.15, 2.1, 4.6, 1.9, "11", "Numero semana", size=120, bold=True, font=HEAD,
             color=AMBER, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 8.15, 4.0, 4.6, 0.5, "Evaluación práctica", "Etiqueta evaluacion", size=20,
             color=WHITE, align=PP_ALIGN.CENTER)
    add_shape(s, MSO_SHAPE.OVAL, 7.6, 5.0, 1.5, 1.5, AMBER, "Circulo acento")
    add_text(s, MX, 1.2, 7.0, 2.3, "BookVerse: mantención de equipos de oficina",
             "Titulo", size=44, bold=True, font=HEAD, color=WHITE, anchor=MSO_ANCHOR.TOP)
    add_text(s, MX, 3.7, 6.8, 1.0,
             "Integración de Competencias 2 · Etapa II · Evaluación práctica (semana 11)",
             "Subtitulo", size=20, color="E9D9E1")
    add_text(s, MX, 5.3, 6.8, 1.3,
             [[("Integrantes: ", {"bold": True, "color": AMBER}),
               "Bastián Andrade, María Ojeda, Maikol Ulloa"],
              [("Docente: ", {"bold": True, "color": AMBER}), "Manuel Merino"]],
             "Integrantes", size=16, color=WHITE, space_after=6)
    set_notes(s, "Buenas tardes. Somos el grupo BookVerse y presentamos la evaluación práctica de "
                 "la semana 11 de Integración de Competencias 2. Resumiremos el trabajo de la "
                 "Etapa II: planificación, instalación y configuración, y validación.")


def slide_contenido(prs):
    s = new_slide(prs, 2, "Contenido")
    items = [
        "Registro de mantenimientos preventivo y correctivo (RF-06)",
        "Actualización de software en equipos (RF-07)",
        "Instalación y configuración del sistema operativo (video)",
        "Historial de mantenimiento de equipos (RF-08)",
        "Conclusiones y oportunidades de mejora",
        "Sistema web de apoyo (RF-06 a RF-09)",
    ]
    cw, ch, gx, gy = (CW - 0.3) / 2, 1.4, 0.3, 0.25
    for i, text in enumerate(items):
        col, row = i % 2, i // 2
        x, y = MX + col * (cw + gx), TOP + row * (ch + gy)
        card(s, x, y, cw, ch, f"Tarjeta {i + 1}")
        num_circle(s, x + 0.3, y + (ch - 0.8) / 2, 0.8, str(i + 1), f"Numero {i + 1}", size=24)
        add_text(s, x + 1.4, y, cw - 1.7, ch, text, f"Texto {i + 1}", size=20,
                 anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s, "La guía de la evaluación pide cinco elementos: los registros de mantenimiento, "
                 "la actualización de software, el video de instalación del sistema operativo, el "
                 "historial de mantenimiento y las conclusiones. Agregamos un sexto punto con el "
                 "sistema web que desarrollamos para apoyar estos procesos.")


def slide_proceso(prs):
    s = new_slide(prs, 3, "Proceso de trabajo")
    add_picture_fit(s, DIAG / "proceso.png", MX, TOP, CW, 4.2, "Diagrama proceso", border=False)
    add_text(s, MX, 6.15, CW, 0.8,
             "Un avance por semana (S7 a S10) y la evaluación práctica en S11. La rúbrica "
             "evalúa tres criterios: planificación, instalación y configuración, y validación.",
             "Descripcion", size=16, color=MUTED)
    set_notes(s, "El trabajo se organizó en cuatro avances semanales, uno por requerimiento, y "
                 "cierra con esta evaluación. En la parte inferior vemos los tres criterios de la "
                 "rúbrica; los usaremos como hilo conductor de la presentación.")


def slide_planificacion(prs):
    s = new_slide(prs, 4, "Planificación del trabajo")
    gw = 9.1
    _, (px, py, pw, ph) = add_picture_fit(s, CAP / "carta_gantt.png", MX, TOP, gw, 4.6,
                                         "Carta Gantt", align="left")
    add_text(s, MX, py + ph + 0.15, gw, 0.4,
             "Carta Gantt de la Etapa II: tareas, responsables y un hito de entrega por semana.",
             "Pie Gantt", size=14, color=MUTED)
    sx, sw, sh, gap = MX + gw + 0.35, CW - gw - 0.35, 1.55, 0.3
    for i, (n, label) in enumerate([("5", "semanas de trabajo"),
                                    ("5", "hitos de entrega"),
                                    ("3", "integrantes")]):
        y = TOP + i * (sh + gap)
        card(s, sx, y, sw, sh, f"Dato {i + 1} (tarjeta)")
        add_text(s, sx + 0.2, y + 0.1, sw - 0.4, 0.8, n, f"Dato {i + 1} (cifra)", size=44,
                 bold=True, font=HEAD, color=BERRY)
        add_text(s, sx + 0.2, y + 0.95, sw - 0.4, 0.45, label, f"Dato {i + 1} (texto)", size=16)
    set_notes(s, "Planificamos cinco semanas, de la 7 a la 11, con un hito de entrega por semana y "
                 "responsables definidos para cada tarea. La carta Gantt separa las fases de "
                 "planificación, instalación y configuración, documentación y validación.")


def slide_riesgos(prs):
    s = new_slide(prs, 5, "Gestión de riesgos")
    lw = 3.2
    card(s, MX, TOP, lw, 5.25, "Panel riesgos", fill=BERRY)
    add_text(s, MX + 0.3, TOP + 0.5, lw - 0.6, 1.6, "11", "Cifra riesgos", size=96, bold=True,
             font=HEAD, color=AMBER)
    add_text(s, MX + 0.3, TOP + 2.3, lw - 0.6, 0.9, "riesgos identificados", "Texto riesgos",
             size=22, bold=True, color=WHITE)
    add_text(s, MX + 0.3, TOP + 3.3, lw - 0.6, 1.7,
             "Se evaluaron por probabilidad e impacto. Siete quedaron en nivel alto; aquí se "
             "muestran cuatro.", "Detalle riesgos", size=16, color="E9D9E1")
    risks = [
        ("R01", "KVM ocupa VT-x e impide iniciar la VM",
         "Mitigar: descargar los módulos KVM y configurar kvm.enable_virt_at_load=0."),
        ("R02", "Poco espacio en disco del anfitrión",
         "Evitar: verificar 40 GB libres antes de crear la VM y usar disco dinámico."),
        ("R04", "Corte de energía al actualizar",
         "Mitigar: crear una instantánea (snapshot) de la VM antes de cada actualización."),
        ("R11", "Retraso en los entregables",
         "Mitigar: un hito por semana revisado con el docente y un día de holgura."),
    ]
    gx, gy = 0.3, 0.3
    x0 = MX + lw + 0.35
    cw = (SW - MX - x0 - gx) / 2
    ch = (5.25 - gy) / 2
    for i, (rid, title, resp) in enumerate(risks):
        x, y = x0 + (i % 2) * (cw + gx), TOP + (i // 2) * (ch + gy)
        card(s, x, y, cw, ch, f"Riesgo {rid} (tarjeta)")
        num_circle(s, x + 0.25, y + 0.25, 0.75, rid, f"Riesgo {rid} (id)", size=16)
        add_text(s, x + 1.2, y + 0.2, cw - 1.45, 0.9, title, f"Riesgo {rid} (titulo)", size=18,
                 bold=True, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + 0.25, y + 1.2, cw - 0.5, ch - 1.35, resp, f"Riesgo {rid} (respuesta)",
                 size=16, color=MUTED)
    set_notes(s, "Identificamos once riesgos y los clasificamos por probabilidad e impacto. Cuatro "
                 "de los de nivel alto se muestran aquí con su estrategia de respuesta. El riesgo "
                 "R01, el conflicto de KVM, ocurrió realmente y lo veremos más adelante.")


def slide_rf06(prs):
    s = new_slide(prs, 6, "Registro de mantenimientos (RF-06)")
    rows = [("Tipo", "preventivo o correctivo"),
            ("Fecha", "no puede ser futura"),
            ("Acciones realizadas", "descripción de la intervención"),
            ("Observaciones", "hallazgos y pendientes"),
            ("Técnico", "usuario que registra el trabajo")]
    rh = 1.0
    for i, (label, desc) in enumerate(rows):
        y = TOP + i * rh
        num_circle(s, MX, y + 0.1, 0.7, str(i + 1), f"Campo {i + 1} (numero)")
        add_text(s, MX + 1.0, y, 4.6, 0.9,
                 [[(label, {"bold": True, "size": 20})], [(desc, {"color": MUTED})]],
                 f"Campo {i + 1} (texto)", size=16, anchor=MSO_ANCHOR.MIDDLE)
    ax, aw = 6.2, SW - MX - 6.2
    _, (px, py, pw, ph) = add_picture_fit(s, CAP / "registro_mantenimiento.png", ax, TOP, aw, 4.6,
                                         "Captura registro", align="left")
    add_text(s, ax, py + ph + 0.15, aw, 0.4, "Formulario del sistema: /mantenimientos/nuevo",
             "Pie captura", size=14, color=MUTED)
    set_notes(s, "El requerimiento RF-06 pide registrar cada mantenimiento preventivo o correctivo. "
                 "Cada registro guarda el tipo, la fecha, las acciones realizadas, las "
                 "observaciones y el técnico responsable. A la derecha vemos el formulario del "
                 "sistema web con un ejemplo.")


def slide_rf07_alternativas(prs):
    s = new_slide(prs, 7, "Actualización de software (RF-07)")
    cx, cwid = MX, 7.3
    add_text(s, cx, TOP - 0.05, cwid, 0.45, "Análisis de alternativas: puntaje total (máx. 20)",
             "Subtitulo grafico", size=20, bold=True)
    data = CategoryChartData()
    cats = ["A. Planilla Excel", "B. winget + script", "C. WSUS / Intune",
            "D. GLPI + agente", "E. Chocolatey / PDQ", "F. Linux: apt"]
    vals = [16, 15, 11, 17, 13, 13]
    data.categories = cats
    data.add_series("Puntaje total", vals)
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(cx), Inches(TOP + 0.5),
                            Inches(cwid), Inches(4.7), data)
    gf.name = "Grafico alternativas"
    chart = gf.chart
    chart.has_legend = False
    chart.has_title = False
    chart.font.size = Pt(14)
    chart.font.name = BODY
    chart.font.color.rgb = rgb(INK)
    plot = chart.plots[0]
    plot.gap_width = 45
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(14)
    dl.font.bold = True
    dl.font.color.rgb = rgb(INK)
    dl.number_format = "0"
    dl.number_format_is_linked = False
    series = plot.series[0]
    series.format.fill.solid()
    series.format.fill.fore_color.rgb = rgb("B7A0AC")
    for i, v in enumerate(vals):
        pt = series.points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(AMBER if cats[i].startswith("D") else "B7A0AC")
    cat = chart.category_axis
    cat.reverse_order = True
    cat.format.line.color.rgb = rgb(LINE)
    cat.tick_labels.font.size = Pt(14)
    cat.has_major_gridlines = False
    val = chart.value_axis
    val.minimum_scale, val.maximum_scale = 0, 20
    val.visible = False
    val.has_major_gridlines = False
    # recommendation panel
    rx = cx + cwid + 0.35
    rw = SW - MX - rx
    card(s, rx, TOP, rw, 5.25, "Panel recomendacion")
    num_circle(s, rx + 0.3, TOP + 0.3, 0.7, "D", "Letra recomendada", size=24)
    add_text(s, rx + 1.2, TOP + 0.3, rw - 1.5, 0.7, "Recomendación", "Titulo recomendacion",
             size=24, bold=True, font=HEAD, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, rx + 0.3, TOP + 1.3, rw - 0.6, 3.8,
             [[("GLPI con agente: ", {"bold": True}),
               "17 de 20 puntos. Obtiene versiones de forma automática en Windows y Linux."],
              [("Respaldo inicial: ", {"bold": True}),
               "planilla Excel (16 puntos) y winget (15 puntos) mientras no exista servidor."],
              [("Criterios: ", {"bold": True}),
               "facilidad de uso, compatibilidad, seguimiento de versiones y costo."]],
             "Texto recomendacion", size=16, space_after=10)
    set_notes(s, "Comparamos seis alternativas con cuatro criterios de uno a cinco puntos. GLPI con "
                 "agente obtuvo el mayor puntaje, 17 de 20, porque inventaría versiones de forma "
                 "automática. Como solución inicial usamos la planilla Excel y winget, que no "
                 "requieren servidor.")


def slide_rf07_registro(prs):
    s = new_slide(prs, 8, "Registro y historial de software")
    fields = [("ID de registro y de equipo", "identificadores únicos (REG-NNN, EQ-NNN)"),
              ("Software y tipo", "sistema operativo, ofimática, navegador, antivirus"),
              ("Versión instalada", "tal como la informa el sistema"),
              ("Fecha de última actualización", "formato DD-MM-AAAA"),
              ("Método", "manual, winget, Windows Update, agente GLPI"),
              ("Cambios relevantes", "resumen del cambio aplicado"),
              ("Responsable y estado", "Actualizado, Pendiente, Con error u Obsoleto")]
    rh = 0.75
    for i, (label, desc) in enumerate(fields):
        y = TOP + i * rh
        add_shape(s, MSO_SHAPE.OVAL, MX, y + 0.2, 0.28, 0.28, AMBER, f"Marca {i + 1}")
        add_text(s, MX + 0.5, y, 5.0, rh,
                 [[(label, {"bold": True})], [(desc, {"color": MUTED})]],
                 f"Campo {i + 1}", size=14, anchor=MSO_ANCHOR.MIDDLE)
    rx = 6.5
    rw = SW - MX - rx
    _, (px, py, pw, ph) = add_picture_fit(s, CAP / "actualizaciones_software.png", rx, TOP, rw,
                                         2.0, "Captura actualizaciones", align="left")
    add_text(s, rx, py + ph + 0.1, rw, 0.35, "Sistema web: /software/actualizaciones",
             "Pie captura", size=14, color=MUTED)
    ry = py + ph + 0.65
    card(s, rx, ry, rw, BOTTOM - ry, "Regla append-only (tarjeta)", fill=BERRY)
    add_text(s, rx + 0.3, ry + 0.2, rw - 0.6, BOTTOM - ry - 0.4,
             [[("Regla de solo adición (append-only)", {"bold": True, "size": 20,
                                                          "color": AMBER})],
              "Las filas del historial no se editan ni se eliminan. Un error se corrige con "
              "una fila nueva que lo explique."],
             "Regla append-only", size=16, color=WHITE, space_after=6,
             anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s, "Definimos un formato uniforme para registrar cada software por equipo: versión, "
                 "fecha, método, cambios y responsable. El historial es de solo adición, es decir, "
                 "nunca se borra una fila; los errores se corrigen agregando una fila nueva. "
                 "El sistema web aplica la misma lógica.")


def slide_vm(prs):
    s = new_slide(prs, 9, "Instalación del SO en máquina virtual")
    tw, th, gx, gy = 3.05, 1.5, 0.3, 0.25
    # (label, value, sub, col, row, colspan)
    tiles = [("Sistema operativo", "Windows 10 IoT Enterprise LTSC 2021",
              "versión 21H2 · compilación 19044", 0, 0, 2),
             ("Hipervisor", "Oracle VirtualBox", "", 0, 1, 1),
             ("Región y teclado", "Spanish (Chile)", "teclado Latin American", 1, 1, 1),
             ("Memoria y procesadores", "4 GB · 2 CPU", "", 0, 2, 1),
             ("Disco virtual", "50 GB", "tamaño dinámico", 1, 2, 1)]
    for i, (label, value, sub, col, row, span) in enumerate(tiles):
        x, y = MX + col * (tw + gx), TOP + row * (th + gy)
        w = tw * span + gx * (span - 1)
        card(s, x, y, w, th, f"Dato VM {i + 1} (tarjeta)")
        paras = [[(label, {"size": 14, "color": MUTED})], [(value, {"bold": True, "size": 20})]]
        if sub:
            paras.append([(sub, {"size": 14})])
        add_text(s, x + 0.25, y, w - 0.5, th, paras, f"Dato VM {i + 1} (texto)", size=16,
                 anchor=MSO_ANCHOR.MIDDLE)
    rx = MX + 2 * tw + gx + 0.4
    rw = SW - MX - rx
    card(s, rx, TOP, rw, 2.55, "Panel LTSC")
    num_circle(s, rx + 0.3, TOP + 0.3, 0.6, "?", "Icono LTSC", size=22)
    add_text(s, rx + 1.1, TOP + 0.3, rw - 1.4, 0.6, "¿Por qué LTSC?", "Titulo LTSC", size=22,
             bold=True, font=HEAD, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, rx + 0.3, TOP + 1.05, rw - 0.6, 1.4,
             "Recibe solo actualizaciones de seguridad y calidad, con soporte extendido. "
             "Es estable para equipos de oficina.", "Texto LTSC", size=16)
    vy = TOP + 2.55 + 0.25
    vh = (TOP + 2 * (th + gy) + th) - vy
    card(s, rx, vy, rw, vh, "Video (marcador)", fill=WHITE, line=AMBER, dash=True)
    add_text(s, rx + 0.3, vy + 0.15, rw - 0.6, vh - 0.3,
             [[("Video del proceso de instalación", {"bold": True, "size": 20})],
              [("Duración máxima: 5 minutos", {"color": MUTED})],
              [("youtu.be/8b-JuKKoMV4", {"bold": True, "color": BERRY, "size": 20})]],
             "Video enlace", size=16, space_after=6, anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s, "Instalamos Windows 10 IoT Enterprise LTSC 2021 en una máquina virtual de "
                 "VirtualBox con 4 GB de RAM, 2 procesadores y un disco dinámico de 50 GB. "
                 "Elegimos LTSC porque solo recibe actualizaciones de seguridad y calidad, lo que "
                 "da estabilidad a un equipo de oficina. Aquí se muestra el video del proceso.")


def slide_pruebas(prs):
    s = new_slide(prs, 10, "Validación y pruebas")
    rows = [("Arranque del sistema", "Reiniciar la máquina virtual",
             "Windows inicia sin errores hasta el escritorio"),
            ("Versión instalada", "winver", "Windows 10 IoT Enterprise LTSC, versión 21H2"),
            ("Nombre del equipo", "hostname", "WIN10-BOOKVERSE"),
            ("Cuenta de usuario", "whoami", "Usuario local creado en la instalación"),
            ("Conectividad de red", "ipconfig; ping -n 3 8.8.8.8",
             "Dirección IP asignada y 0 % de paquetes perdidos"),
            ("Actualizaciones", "Windows Update > Check for updates", "Sin actualizaciones pendientes"),
            ("Guest Additions", "Cambiar el tamaño de la ventana", "La resolución se ajusta automáticamente")]
    widths = [2.9, 3.9, CW - 6.8]
    rh = 0.58
    gf = s.shapes.add_table(len(rows) + 1, 3, Inches(MX), Inches(TOP), Inches(CW),
                            Inches(rh * (len(rows) + 1)))
    gf.name = "Tabla pruebas"
    tbl = gf.table
    for i, w in enumerate(widths):
        tbl.columns[i].width = Inches(w)
    for r in range(len(rows) + 1):
        tbl.rows[r].height = Inches(rh)
    header = ("Prueba", "Acción o comando", "Resultado esperado")
    for r in range(len(rows) + 1):
        for c in range(3):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.12)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            text = header[c] if r == 0 else rows[r - 1][c]
            cell.fill.fore_color.rgb = rgb(BERRY if r == 0 else (TINT if r % 2 == 0 else WHITE))
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            mono = r > 0 and c == 1 and not text[0].isupper()
            style_runs(p, [text], 14, WHITE if r == 0 else INK, r == 0 or c == 0,
                       "Consolas" if mono else BODY)
    ty = TOP + rh * (len(rows) + 1) + 0.3
    num_circle(s, MX, ty, 0.55, "7", "Cifra pruebas", size=20)
    add_text(s, MX + 0.8, ty, CW - 0.8, 0.55,
             "pruebas posteriores a la instalación; cada resultado se registra como OK o Falla.",
             "Nota pruebas", size=16, anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s, "Después de instalar ejecutamos siete pruebas: arranque, versión, nombre del "
                 "equipo, usuario, red, actualizaciones y Guest Additions. Cada prueba tiene un "
                 "resultado esperado y se anota como OK o Falla, lo que permite demostrar que el "
                 "equipo quedó operativo.")


def slide_error(prs):
    s = new_slide(prs, 11, "Errores detectados y corrección")
    add_picture_fit(s, DIAG / "error_kvm.png", MX, TOP, CW, 3.0, "Diagrama error KVM",
                    border=False)
    y = TOP + 3.25
    h = BOTTOM - y
    card(s, MX, y, CW, h, "Aprendizaje (tarjeta)", fill=BERRY)
    num_circle(s, MX + 0.35, y + (h - 0.8) / 2, 0.8, "R01", "Riesgo asociado", size=18)
    add_text(s, MX + 1.55, y, CW - 1.9, h,
             "El riesgo R01 de la matriz anticipó este error: su mitigación estaba definida "
             "antes de iniciar la instalación.", "Aprendizaje", size=20, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s, "Durante la preparación, la máquina virtual no iniciaba porque el módulo KVM del "
                 "equipo anfitrión ocupaba la virtualización por hardware. Descargamos los módulos "
                 "y configuramos el parámetro enable_virt_at_load en cero; así la VM inició "
                 "correctamente. Este caso muestra el valor de anticipar riesgos.")


def slide_historial(prs):
    s = new_slide(prs, 12, "Historial de mantenimiento (RF-08)")
    crit = [("Rango de fechas", "desde y hasta"),
            ("Tipo de mantenimiento", "preventivo o correctivo"),
            ("Equipo", "código o número de serie"),
            ("Detalle", "acceso a cada entrada del historial")]
    rh = 1.15
    for i, (label, desc) in enumerate(crit):
        y = TOP + i * rh
        num_circle(s, MX, y + 0.15, 0.7, str(i + 1), f"Criterio {i + 1} (numero)")
        add_text(s, MX + 1.0, y, 3.6, 1.0,
                 [[(label, {"bold": True, "size": 20})], [(desc, {"color": MUTED})]],
                 f"Criterio {i + 1} (texto)", size=16, anchor=MSO_ANCHOR.MIDDLE)
    rx = 5.5
    rw = SW - MX - rx
    _, (px, py, pw, ph) = add_picture_fit(s, CAP / "historial_mantenimientos.png", rx, TOP, rw,
                                         3.3, "Captura historial", align="left")
    add_text(s, rx, py + ph + 0.1, rw, 0.35, "Sistema web: /mantenimientos/",
             "Pie captura", size=14, color=MUTED)
    cy = py + ph + 0.65
    card(s, rx, cy, rw, 1.4, "Nota historial (tarjeta)")
    add_text(s, rx + 0.3, cy + 0.1, rw - 0.6, 1.2,
             "Los filtros se combinan y los resultados se ordenan del más reciente al más "
             "antiguo. Los datos mostrados son de ejemplo.", "Nota historial", size=16,
             anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s, "El historial permite consultar los mantenimientos por rango de fechas, tipo, "
                 "código del equipo o número de serie, y abrir el detalle de cada uno. Los datos "
                 "que se ven son de ejemplo, porque aún no contamos con el inventario real.")


def slide_repuestos(prs):
    s = new_slide(prs, 13, "Inventario de repuestos (RF-09)")
    lw = 4.8
    items = [("Ingresos y salidas", "cada movimiento queda registrado con fecha y técnico", 1.35),
             ("Estado del repuesto", None, 1.9),
             ("Stock nunca negativo", "una salida mayor al stock disponible se rechaza", 1.35)]
    y = TOP
    for i, (label, desc, h) in enumerate(items):
        num_circle(s, MX, y + 0.1, 0.7, str(i + 1), f"Punto {i + 1} (numero)")
        paras = [[(label, {"bold": True, "size": 20})]]
        if desc:
            paras.append([(desc, {"color": MUTED})])
        add_text(s, MX + 1.0, y, lw - 1.0, 0.95 if not desc else h - 0.15, paras,
                 f"Punto {i + 1} (texto)", size=16,
                 anchor=MSO_ANCHOR.MIDDLE if desc else MSO_ANCHOR.TOP)
        if not desc:
            for j, status in enumerate(["en buen estado", "en reparación", "fuera de servicio"]):
                cy = y + 0.5 + j * 0.45
                chip = card(s, MX + 1.0, cy, 2.6, 0.38, f"Estado {j + 1}", fill=TINT)
                tf = chip.text_frame
                tf.margin_top = tf.margin_bottom = 0
                tf.vertical_anchor = MSO_ANCHOR.MIDDLE
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.LEFT
                tf.margin_left = Inches(0.15)
                style_runs(p, [status], 14, INK, False, BODY)
        y += h
    rx = MX + lw + 0.3
    rw = SW - MX - rx
    _, (px, py, pw, ph) = add_picture_fit(s, CAP / "repuestos.png", rx, TOP, rw, 4.75,
                                         "Captura repuestos", align="left")
    add_text(s, rx, py + ph + 0.1, rw, 0.35, "Sistema web: /repuestos/", "Pie captura",
             size=14, color=MUTED)
    set_notes(s, "El inventario de repuestos registra ingresos y salidas, y el estado de cada "
                 "pieza: en buen estado, en reparación o fuera de servicio. El sistema impide que "
                 "el stock quede negativo, porque rechaza las salidas mayores a la existencia.")


def slide_sistema(prs):
    s = new_slide(prs, 14, "Sistema web de apoyo")
    add_picture_fit(s, DIAG / "arquitectura.png", MX, TOP, CW, 3.3, "Diagrama arquitectura",
                    border=False)
    stats = [("4", ["requerimientos", "(RF-06 a RF-09)"]), ("2", "roles: administrador y técnico"),
             ("46", "pruebas automatizadas")]
    gap = 0.3
    w = (CW - 2 * gap) / 3
    y = TOP + 3.65
    for i, (n, label) in enumerate(stats):
        stat(s, MX + i * (w + gap), y, w, BOTTOM - y, n, label, f"Dato sistema {i + 1}")
    set_notes(s, "Desarrollamos un sistema web con Python, Flask y SQLite que cubre los cuatro "
                 "requerimientos. Tiene dos roles, administrador y técnico, y cuenta con 46 "
                 "pruebas automatizadas que verifican su funcionamiento.")


def slide_modelo(prs):
    s = new_slide(prs, 15, "Modelo de datos")
    add_picture_fit(s, DIAG / "modelo_datos.png", MX, TOP, CW, BOTTOM - TOP, "Diagrama modelo",
                    border=False)
    set_notes(s, "El modelo tiene ocho tablas. Los mantenimientos, las actualizaciones de software "
                 "y las validaciones se vinculan a un equipo; los mantenimientos y los movimientos "
                 "de repuestos se vinculan al usuario que los registra. Así cada acción queda "
                 "trazable.")


def slide_conclusiones(prs):
    s = new_slide(prs, 16, "Conclusiones")
    items = [
        ("Trazabilidad", "El registro y el historial permiten saber qué se hizo, cuándo y quién "
                         "lo hizo en cada equipo."),
        ("Planificación", "La matriz de riesgos anticipó problemas reales, como el conflicto de "
                          "KVM, y su mitigación ya estaba definida."),
        ("Validación", "Las pruebas posteriores a la instalación y las 46 pruebas del sistema "
                       "respaldan que el resultado funciona."),
        ("Centralización", "El sistema web reúne los requerimientos RF-06 a RF-09 en un solo "
                           "lugar."),
    ]
    rh, gap = 1.15, 0.2
    for i, (head, text) in enumerate(items):
        y = TOP + i * (rh + gap)
        card(s, MX, y, CW, rh, f"Conclusion {i + 1} (tarjeta)")
        num_circle(s, MX + 0.3, y + (rh - 0.75) / 2, 0.75, str(i + 1), f"Conclusion {i + 1} (numero)",
                   size=22)
        add_text(s, MX + 1.4, y, 2.6, rh, head, f"Conclusion {i + 1} (titulo)", size=22,
                 bold=True, font=HEAD, color=BERRY, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, MX + 4.2, y, CW - 4.5, rh, text, f"Conclusion {i + 1} (texto)", size=16,
                 anchor=MSO_ANCHOR.MIDDLE)
    set_notes(s, "Como conclusiones: el registro y el historial dan trazabilidad; la planificación "
                 "con riesgos nos permitió resolver el error de KVM sin perder tiempo; las pruebas "
                 "validan el resultado; y el sistema web centraliza los cuatro requerimientos.")


def slide_mejoras(prs):
    s = new_slide(prs, 17, "Oportunidades de mejora")
    items = [
        ("Piloto de GLPI", "Instalar GLPI con agente para inventariar versiones de forma "
                           "automática."),
        ("Datos reales", "Reemplazar los datos de ejemplo por el inventario real del laboratorio."),
        ("Registro automático", "Registrar versiones con scripts de PowerShell y winget."),
        ("Migrar a MySQL", "Pasar de SQLite a MySQL, como indica el caso."),
        ("Más seguridad", "Agregar protección CSRF y reemplazar las credenciales de demostración."),
    ]
    gap = 0.28
    w = (CW - 4 * gap) / 5
    h = 4.6
    for i, (head, text) in enumerate(items):
        x = MX + i * (w + gap)
        card(s, x, TOP, w, h, f"Mejora {i + 1} (tarjeta)")
        num_circle(s, x + 0.25, TOP + 0.3, 0.7, str(i + 1), f"Mejora {i + 1} (numero)", size=22)
        add_text(s, x + 0.25, TOP + 1.3, w - 0.5, 0.9, head, f"Mejora {i + 1} (titulo)", size=20,
                 bold=True, font=HEAD, color=BERRY)
        add_text(s, x + 0.25, TOP + 2.3, w - 0.5, h - 2.5, text, f"Mejora {i + 1} (texto)", size=16)
    set_notes(s, "Identificamos cinco mejoras: probar GLPI con agente, cargar el inventario real, "
                 "automatizar el registro de versiones con PowerShell y winget, migrar la base de "
                 "datos a MySQL como pide el caso y reforzar la seguridad del sistema web.")


def slide_cierre(prs):
    s = new_slide(prs, 18, None, bg=BERRY)
    add_shape(s, MSO_SHAPE.OVAL, 8.6, 1.2, 3.8, 3.8, INK, "Circulo grande")
    add_shape(s, MSO_SHAPE.OVAL, 7.9, 4.3, 1.3, 1.3, AMBER, "Circulo acento")
    add_text(s, MX, 2.0, 7.0, 1.5, "Gracias", "Titulo", size=66, bold=True, font=HEAD,
             color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, MX, 3.6, 7.0, 0.9, "¿Preguntas?", "Preguntas", size=36, font=HEAD, color=AMBER)
    add_text(s, MX, 5.6, 7.0, 0.8,
             "Bastián Andrade · María Ojeda · Maikol Ulloa", "Integrantes", size=16,
             color="E9D9E1")
    set_notes(s, "Con esto concluimos la presentación. Agradecemos su atención y quedamos atentos "
                 "a las preguntas.")


def main():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)
    for build in (slide_portada, slide_contenido, slide_proceso, slide_planificacion,
                  slide_riesgos, slide_rf06, slide_rf07_alternativas, slide_rf07_registro,
                  slide_vm, slide_pruebas, slide_error, slide_historial, slide_repuestos,
                  slide_sistema, slide_modelo, slide_conclusiones, slide_mejoras, slide_cierre):
        build(prs)
    prs.core_properties.title = "BookVerse: evaluación práctica semana 11"
    prs.core_properties.author = "Bastián Andrade, María Ojeda, Maikol Ulloa"
    prs.save(OUT)
    print("Saved", OUT)


if __name__ == "__main__":
    main()
