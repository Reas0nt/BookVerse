"""Generate the RF-10 progress report (Etapa 3, Avance #1, week 12) as a Word document."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Twips

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "Informe_Avance1_RF10_Semana12.docx"
FONT = "Calibri"
MEMBERS = ["Bastián Andrade", "María Ojeda", "Maikol Ulloa"]

COLOR_TITLE = "2C3E50"
COLOR_HEADER = "34495E"
COLOR_ZEBRA = "ECF0F1"
COLOR_BORDER = "BDC3C7"
COLOR_CODE = "F2F4F4"
COLOR_NOTE = "FCF3CF"

doc = Document()


# ---------- Helpers ----------

def shade(element, fill):
    """Apply a background color to a paragraph (pPr) or table cell (tcPr)."""
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    element.append(shd)


def add_run(par, text, bold=False, italic=False, font=None, size=None, color=None):
    run = par.add_run(text)
    run.bold = bold
    run.italic = italic
    if font:
        run.font.name = font
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    return run


def p(text="", bold=False, after=6):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(after)
    if text:
        add_run(par, text, bold=bold)
    return par


def rich(parts):
    """Paragraph from a list of strings or (text, bold) tuples."""
    par = p()
    for part in parts:
        text, bold = part if isinstance(part, tuple) else (part, False)
        add_run(par, text, bold=bold)
    return par


def h1(text):
    doc.add_heading(text, level=1)


def h2(text):
    doc.add_heading(text, level=2)


def bullet(parts):
    """Bulleted item; parts is a string or a list of (text, style) tuples."""
    par = doc.add_paragraph(style="List Bullet")
    par.paragraph_format.space_after = Pt(3)
    if isinstance(parts, str):
        add_run(par, parts)
    else:
        for text, style in parts:
            add_run(par, text, bold=(style == "bold"), font=("Consolas" if style == "code" else None))
    return par


def numbered(items):
    """Numbered list that always starts at 1."""
    for i, text in enumerate(items, start=1):
        par = doc.add_paragraph()
        fmt = par.paragraph_format
        fmt.left_indent = Cm(1.27)
        fmt.first_line_indent = Cm(-0.63)
        fmt.space_after = Pt(3)
        add_run(par, f"{i}.\t{text}")


def note(text):
    par = p(after=8)
    par.paragraph_format.space_before = Pt(3)
    add_run(par, text, italic=True)
    shade(par._p.get_or_add_pPr(), COLOR_NOTE)


def set_cell_borders(cell):
    borders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), COLOR_BORDER)
        borders.append(el)
    cell._tc.get_or_add_tcPr().append(borders)


def fill_cell(cell, text, width, fill, bold=False, color=None, center=False):
    cell.width = Twips(width)
    set_cell_borders(cell)
    shade(cell._tc.get_or_add_tcPr(), fill)
    par = cell.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
    add_run(par, str(text), bold=bold, color=color, size=10)


def table(widths, head, rows):
    """Table with dark header, zebra rows and light borders. Widths in twips."""
    tbl = doc.add_table(rows=1, cols=len(head))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    for col, width in zip(tbl.columns, widths):
        col.width = Twips(width)
    for c, text in enumerate(head):
        fill_cell(tbl.rows[0].cells[c], text, widths[c], COLOR_HEADER, bold=True, color="FFFFFF", center=True)
    for i, row in enumerate(rows):
        cells = tbl.add_row().cells
        fill = COLOR_ZEBRA if i % 2 else "FFFFFF"
        for c, text in enumerate(row):
            fill_cell(cells[c], text, widths[c], fill)
    for row in tbl.rows:  # keep each row on one page
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    return tbl


def picture(path, caption, width_cm=15):
    """Centered picture with an italic caption below."""
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_after = Pt(2)
    par.add_run().add_picture(path, width=Cm(width_cm))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(8)
    add_run(cap, caption, italic=True, size=9)


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def centered(text, size, bold=False, color=None, before=0, after=0):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(before)
    par.paragraph_format.space_after = Pt(after)
    add_run(par, text, bold=bold, size=size, color=color)


def add_page_number_footer(text):
    par = doc.sections[0].footer.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(par, text, size=9)
    run = add_run(par, "", size=9)
    for kind, value in (("begin", None), ("instr", "PAGE"), ("end", None)):
        if kind == "instr":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = value
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        run._r.append(el)


# ---------- Document setup ----------

section = doc.sections[0]
section.page_width, section.page_height = Cm(21), Cm(29.7)
for side in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
    setattr(section, side, Cm(2.54))

normal = doc.styles["Normal"]
normal.font.name = FONT
normal.font.size = Pt(11)
for name, size, color, before, after in (("Heading 1", 16, COLOR_TITLE, 18, 8),
                                         ("Heading 2", 13, COLOR_HEADER, 12, 6)):
    style = doc.styles[name]
    style.font.name = FONT
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor.from_string(color)
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)

add_page_number_footer("BookVerse - RF-10 - Etapa 3 Avance #1 - Página ")

DIAGRAM_CLASSES = str(HERE / "diagramas" / "clases_rf10.png")
DIAGRAM_ARCHITECTURE = str(HERE / "diagramas" / "arquitectura_rf10.png")

# ---------- Cover ----------

centered("Integración de Competencias 2", 16, bold=True, color=COLOR_TITLE, before=90, after=10)
centered("Etapa 3 - Avance #1 (semana 12)", 14, color=COLOR_TITLE, after=30)
centered("Informe de avance RF-10", 22, bold=True, color=COLOR_HEADER, after=10)
centered("Monitoreo de sensores ambientales en sucursales - Proyecto BookVerse", 13, after=60)
table([3000, 6026], ["Dato", "Detalle"], [
    ["Integrantes", ", ".join(MEMBERS)],
    ["Docente", "Manuel Merino"],
    ["Fecha", "Semana 12, noviembre 2026"],
    ["Requerimiento", "RF-10: monitoreo de sensores ambientales en sucursales"],
    ["Entregables", "Diagrama de clases UML y diagrama de arquitectura de alto nivel"],
])
page_break()

# ---------- 1. Introduction ----------

h1("1. Introducción y objetivo")
p("BookVerse es una cadena de librerías chilena que, en la Etapa 3, incorpora sensores IoT en sus sucursales para conocer en tiempo real la temperatura, la humedad y la cantidad de personas. La empresa utiliza MySQL como base de datos y busca contar con datos en tiempo real, alertas y ajuste proactivo de las condiciones en las bodegas. Esta necesidad corresponde al requerimiento RF-10.")
p("Objetivo general: diseñar un modelo UML orientado a un prototipo web que permita monitorear los sensores de las sucursales, y verificar que el diseño es coherente con el flujo de datos exigido por RF-10.")
p("Objetivos específicos:")
for t in ["Analizar el requerimiento RF-10: actor, precondiciones, flujos, excepciones y postcondiciones.",
          "Elaborar un diagrama de clases con los elementos clave del monitoreo de información y sus relaciones.",
          "Elaborar un diagrama de arquitectura de alto nivel con los componentes esenciales, sus interacciones y conexiones.",
          "Verificar que el diseño cubre cada flujo del requerimiento y compartirlo con el docente."]:
    bullet(t)

# ---------- 2. Requirement analysis ----------

h1("2. Análisis del requerimiento RF-10")
p("RF-10 se define en el caso de estudio de la Etapa 3 como sigue.")
table([2400, 6626], ["Elemento del caso", "Definición"], [
    ["Descripción", "Conexión y monitoreo en tiempo real de sensores de temperatura, humedad y conteo de personas en las sucursales."],
    ["Actor", "Técnico de mantenimiento."],
    ["Precondiciones", "Los sensores están instalados y configurados."],
    ["Flujo normal", "El sistema recibe los datos de los sensores, muestra los valores actualizados en pantalla y los almacena automáticamente."],
    ["Flujo alterno", "Si uno o más sensores dejan de enviar datos, se muestra una advertencia en pantalla."],
    ["Excepciones", "Si falla la conexión a internet, se genera un mensaje de advertencia."],
    ["Postcondiciones", "Los datos quedan almacenados para consultas y análisis posteriores."],
])
p()
h2("2.1 Necesidades de información identificadas")
for t in ["Identificar cada sensor, su tipo y su ubicación en la sucursal.",
          "Registrar cada lectura con su valor y fecha y hora.",
          "Definir umbrales por tipo de sensor para detectar valores fuera de rango (alertas proactivas).",
          "Detectar la ausencia de datos de un sensor mediante un tiempo de espera (timeout) desde la última lectura.",
          "Detectar la pérdida de conexión y advertirla al técnico.",
          "Guardar las lecturas y alertas en MySQL para su consulta posterior (base para RF-11)."]:
    bullet(t)

# ---------- 3. Technologies ----------

h1("3. Tecnologías IoT elegidas")
p("Se eligieron tecnologías de bajo costo, abiertas y compatibles con la pila ya utilizada en el sistema web de la Etapa 2 (Python, Flask).")
table([2200, 3300, 3526], ["Tecnología", "Rol en la solución", "Motivo de la elección"], [
    ["ESP32", "Microcontrolador con Wi-Fi instalado en cada sucursal; lee los sensores y publica los datos.", "Bajo costo, Wi-Fi integrado y amplia documentación."],
    ["DHT22", "Sensor de temperatura y humedad.", "Económico y suficiente en precisión para bodegas y salas."],
    ["Sensor IR/ToF", "Conteo de personas en accesos.", "Detecta el paso sin contacto ni cámaras."],
    ["MQTT (Mosquitto)", "Protocolo y broker de mensajería entre los nodos y el servidor.", "Liviano, publicación/suscripción y tolerante a redes inestables."],
    ["Flask (Python)", "Backend: recibe lecturas, genera alertas y envía datos al panel.", "Ya utilizado en el sistema de la Etapa 2."],
    ["SSE", "Canal de actualización en tiempo real hacia el navegador.", "Más simple que WebSocket para un flujo en un solo sentido."],
    ["MySQL", "Almacenamiento de lecturas, sensores, umbrales y alertas.", "Es la base de datos que utiliza la empresa según el caso."],
])
p()

# ---------- 4. Class diagram ----------

h1("4. Diagrama de clases")
p("El diagrama muestra solo las clases necesarias para el monitoreo de RF-10, orientado al prototipo web. Está escrito en PlantUML (archivo diagramas/clases_rf10.puml).")
picture(DIAGRAM_CLASSES, "Figura 1. Diagrama de clases UML del monitoreo de sensores (RF-10).", width_cm=16)
h2("4.1 Clases")
table([2400, 6626], ["Clase", "Responsabilidad"], [
    ["Sucursal", "Local de BookVerse donde se instalan los sensores y se definen los umbrales."],
    ["Sensor", "Dispositivo con tipo, ubicación y hora de su última lectura. estaActivo() indica si envió datos dentro del tiempo de espera (timeout)."],
    ["Lectura", "Valor medido por un sensor en una fecha y hora."],
    ["Umbral", "Rango permitido (mínimo y máximo) para un tipo de sensor en una sucursal."],
    ["Alerta", "Advertencia sobre un sensor: valor fuera de rango o sensor sin datos."],
    ["ServicioMonitoreo", "Recibe cada lectura, la compara con el umbral, la guarda y revisa periódicamente los sensores que dejaron de enviar datos."],
    ["RepositorioLecturas (interfaz)", "Define cómo se guardan las lecturas. La implementación con MySQL se diseña en RF-11."],
    ["PanelMonitoreo", "Pantalla web que muestra los valores en vivo y las advertencias."],
    ["TipoSensor, TipoAlerta", "Enumeraciones con los valores permitidos de tipo de sensor y tipo de alerta."],
])
p()
h2("4.2 Decisiones de diseño")
for parts in [
    [("Un solo Sensor con TipoSensor: ", "bold"), ("los tres sensores solo se diferencian por lo que miden, por eso se usa un atributo tipo en lugar de tres subclases.", "")],
    [("Estado calculado: ", "bold"), ("el sensor no guarda un estado; estaActivo() lo calcula desde la última lectura, así no hay datos que se desincronicen.", "")],
    [("Composición Sucursal - Sensor y Sucursal - Umbral: ", "bold"), ("sensores y umbrales pertenecen a una sucursal y no existen sin ella.", "")],
    [("Interfaz RepositorioLecturas: ", "bold"), ("el servicio no depende de MySQL directamente; la base de datos puede cambiar sin modificar el servicio.", "")],
    [("Pérdida de conexión en el panel: ", "bold"), ("si falla internet, el servidor no puede avisar; por eso es el panel web el que detecta que se cortó la conexión y muestra la advertencia.", "")],
]:
    bullet(parts)

# ---------- 5. Architecture diagram ----------

page_break()
h1("5. Diagrama de arquitectura de alto nivel")
p("El diagrama (archivo diagramas/arquitectura_rf10.puml) muestra los cinco componentes esenciales y los protocolos que los conectan.")
picture(DIAGRAM_ARCHITECTURE, "Figura 2. Arquitectura de alto nivel del monitoreo de sensores (RF-10).", width_cm=16)
h2("5.1 Componentes")
table([2600, 6426], ["Componente", "Función"], [
    ["Sensores en sucursal", "ESP32 con DHT22 (temperatura y humedad) y contador de personas; publica las lecturas por MQTT."],
    ["Broker MQTT (Mosquitto)", "Recibe los mensajes de todas las sucursales y los entrega al backend."],
    ["Backend Flask", "Recibe las lecturas, aplica umbrales, genera alertas, guarda los datos y los envía al panel."],
    ["MySQL", "Almacena lecturas y alertas para consultas posteriores."],
    ["Panel web", "Muestra los valores en vivo al técnico de mantenimiento y advierte si se pierde la conexión."],
])
p()
h2("5.2 Flujo de datos")
numbered([
    "El ESP32 lee los sensores y publica cada lectura en el broker MQTT.",
    "El backend recibe la lectura, la compara con el umbral y, si está fuera de rango, crea una alerta.",
    "El backend guarda la lectura y la alerta en MySQL.",
    "El backend envía los valores nuevos al panel web por SSE, que los muestra en vivo (flujo normal).",
    "Si un sensor deja de enviar datos, el backend crea la alerta SENSOR_SIN_DATOS y el panel la muestra (flujo alterno).",
    "Si se corta la conexión, el panel lo detecta y muestra una advertencia (excepción).",
])
p()

# ---------- 6. Verification ----------

h1("6. Verificación del diseño")
p("Se comprobó que cada paso del requerimiento RF-10 está cubierto por al menos una clase y un componente.")
table([2300, 2300, 2200, 2226], ["Elemento de RF-10", "Cómo se cubre", "Clases", "Componentes"], [
    ["Precondición: sensores instalados y configurados", "Cada sensor pertenece a una sucursal y tiene tipo y ubicación.", "Sucursal, Sensor", "Sensores en sucursal"],
    ["Flujo normal: recibir datos", "El servicio recibe cada lectura.", "ServicioMonitoreo, Lectura", "Broker MQTT, Backend Flask"],
    ["Flujo normal: mostrar valores", "El panel muestra los valores en vivo.", "PanelMonitoreo", "Panel web (SSE)"],
    ["Flujo normal: guardar automáticamente", "Cada lectura se guarda al recibirse.", "RepositorioLecturas", "Backend Flask, MySQL"],
    ["Flujo alterno: sensor sin datos", "Se revisa la última lectura de cada sensor y se crea una alerta.", "Sensor.estaActivo, ServicioMonitoreo.revisarSensoresSinDatos, Alerta", "Backend Flask, Panel web"],
    ["Excepción: falla la conexión", "El panel detecta el corte y muestra una advertencia.", "PanelMonitoreo.mostrarAdvertencia", "Panel web"],
    ["Postcondición: datos para análisis", "Las lecturas quedan guardadas.", "RepositorioLecturas, Lectura", "MySQL"],
    ["Necesidad del caso: alertas proactivas", "Valores fuera del umbral generan alertas.", "Umbral, Alerta", "Backend Flask"],
])
p()
p("Coherencia entre ambos diagramas: ServicioMonitoreo vive en el backend Flask, RepositorioLecturas en MySQL y PanelMonitoreo en el panel web; el flujo es el mismo en los dos modelos: sensor, broker, backend, base de datos y panel.")
note("Pendiente: compartir los diagramas con el docente y registrar sus observaciones.")

# ---------- 7. Next steps ----------

h1("7. Próximos pasos")
for t in ["Avance #2 (RF-11): modelar el almacenamiento de los datos de los sensores en MySQL (modelo de datos y arquitectura de módulos y base de datos).",
          "Construir el prototipo web: simulador de sensores que publique en MQTT, servicio de ingesta con Flask y panel con actualización en vivo.",
          "Definir los valores de los umbrales y el tiempo de espera sin datos junto con el técnico de mantenimiento.",
          "Incorporar las observaciones del docente al modelo antes de implementar."]:
    bullet(t)

# ---------- 8. Conclusion ----------

h1("8. Conclusión")
p("Se analizó RF-10 y se elaboraron un diagrama de clases y un diagrama de arquitectura que cubren el flujo normal, el flujo alterno y la excepción del requerimiento. La tabla de verificación muestra que cada paso tiene clases y componentes que lo respaldan, lo que deja una base coherente para el prototipo web.")

doc.save(OUTPUT)
print(f"[ÉXITO] Archivo '{OUTPUT.name}' generado correctamente.")
