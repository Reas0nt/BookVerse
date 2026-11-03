"""Generate the RF-10 progress report (Etapa 3, Avance #1, week 12) as a Word document."""

from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
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


def new_section(landscape):
    """Start a new page section in landscape or portrait (footer is inherited)."""
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = (Cm(29.7), Cm(21)) if landscape else (Cm(21), Cm(29.7))
    return sec


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
for t in ["Identificar cada sensor, su tipo, su ubicación en la sucursal y su estado.",
          "Registrar cada lectura con su valor, unidad y fecha y hora.",
          "Definir umbrales por tipo de sensor para detectar valores fuera de rango (alertas proactivas).",
          "Detectar la ausencia de datos de un sensor mediante un tiempo de espera (timeout) desde la última lectura.",
          "Detectar la pérdida de conexión y advertirla al técnico.",
          "Persistir las lecturas y alertas en MySQL para su consulta posterior (base para RF-11)."]:
    bullet(t)

# ---------- 3. Technologies ----------

h1("3. Tecnologías IoT elegidas")
p("Se eligieron tecnologías de bajo costo, abiertas y compatibles con la pila ya utilizada en el sistema web de la Etapa 2 (Python, Flask).")
table([2200, 3300, 3526], ["Tecnología", "Rol en la solución", "Motivo de la elección"], [
    ["ESP32", "Microcontrolador con Wi-Fi instalado en cada sucursal; lee los sensores y publica los datos.", "Bajo costo, Wi-Fi integrado y amplia documentación."],
    ["DHT22", "Sensor de temperatura y humedad.", "Económico y suficiente en precisión para bodegas y salas."],
    ["Sensor IR/ToF", "Conteo de personas en accesos.", "Detecta el paso sin contacto ni cámaras."],
    ["MQTT (Mosquitto)", "Protocolo y broker de mensajería entre los nodos y el servidor.", "Liviano, publicación/suscripción y tolerante a redes inestables."],
    ["Flask (Python)", "Backend: ingesta, servicio de monitoreo y alertas, API REST y SSE.", "Ya utilizado en el sistema de la Etapa 2."],
    ["SSE", "Canal de actualización en tiempo real hacia el navegador.", "Más simple que WebSocket para un flujo en un solo sentido."],
    ["MySQL", "Almacenamiento de lecturas, sensores, umbrales y alertas.", "Es la base de datos que utiliza la empresa según el caso."],
])
p()

# ---------- 4. Class diagram ----------

new_section(landscape=True)
h1("4. Diagrama de clases")
p("El diagrama representa los elementos clave del monitoreo de información. Está escrito en PlantUML (archivo diagramas/clases_rf10.puml, versión en alta resolución en diagramas/clases_rf10.png) y orientado al prototipo web.")
picture(DIAGRAM_CLASSES, "Figura 1. Diagrama de clases UML del monitoreo de sensores (RF-10).", width_cm=21)
new_section(landscape=False)
h2("4.1 Clases y enumeraciones")
table([2400, 6626], ["Clase", "Responsabilidad"], [
    ["Sucursal", "Local de BookVerse donde se instalan los sensores; agrupa sensores y umbrales."],
    ["Sensor (abstracta)", "Dispositivo con identificador, tipo, ubicación, estado y marca de la última lectura. Registra lecturas y determina si está inactivo según un timeout."],
    ["SensorTemperatura, SensorHumedad, SensorConteoPersonas", "Especializaciones de Sensor, cada una con su unidad de medida (°C, %HR, personas)."],
    ["Lectura", "Dato medido por un sensor: valor, unidad y fecha y hora."],
    ["Umbral", "Rango permitido (mínimo y máximo) por tipo de sensor; indica si un valor está fuera de rango."],
    ["Alerta", "Advertencia con tipo (FUERA_DE_RANGO, SENSOR_SIN_DATOS, SIN_CONEXION), severidad, estado y mensaje; puede reconocerse y resolverse."],
    ["MonitorService", "Servicio central: recibe lecturas, verifica sensores inactivos (flujo alterno), detecta la pérdida de conexión (excepción) y entrega los últimos valores."],
    ["LecturaRepository (interfaz) y LecturaMySQLRepository", "Persistencia de lecturas; implementa el almacenamiento automático en MySQL y la consulta por sensor y rango de fechas."],
    ["PanelMonitoreo", "Interfaz web que actualiza los valores en pantalla y muestra las advertencias."],
    ["TecnicoMantenimiento", "Actor que consulta el panel y reconoce alertas."],
    ["TipoSensor, EstadoSensor, TipoAlerta, Severidad, EstadoAlerta", "Enumeraciones que acotan los valores permitidos."],
])
p()
h2("4.2 Relaciones")
for parts in [
    [("Herencia: ", "bold"), ("SensorTemperatura, SensorHumedad y SensorConteoPersonas heredan de Sensor.", "")],
    [("Composición Sucursal - Sensor (1 a 1..*): ", "bold"), ("una sucursal instala uno o más sensores; el sensor no existe sin su sucursal.", "")],
    [("Agregación Sensor - Lectura (1 a 0..*): ", "bold"), ("un sensor genera muchas lecturas a lo largo del tiempo.", "")],
    [("Agregación Sucursal - Umbral (1 a 0..*): ", "bold"), ("cada sucursal configura los rangos aceptables.", "")],
    [("Asociación MonitorService - Alerta (1 a 0..*): ", "bold"), ("el servicio genera alertas; cada alerta apunta a un sensor de origen (0..1, porque SIN_CONEXION no pertenece a un sensor concreto).", "")],
    [("Dependencias de MonitorService: ", "bold"), ("supervisa Sensor, compara con Umbral y guarda lecturas mediante LecturaRepository, lo que desacopla el servicio de MySQL.", "")],
    [("Realización: ", "bold"), ("LecturaMySQLRepository implementa LecturaRepository.", "")],
    [("PanelMonitoreo y TecnicoMantenimiento: ", "bold"), ("el panel consulta al servicio y muestra alertas; uno o más técnicos usan el panel y monitorean una o más sucursales.", "")],
]:
    bullet(parts)

# ---------- 5. Architecture diagram ----------

h1("5. Diagrama de arquitectura de alto nivel")
p("El diagrama (archivo diagramas/arquitectura_rf10.puml) muestra los componentes esenciales, cómo se conectan y los protocolos utilizados.")
picture(DIAGRAM_ARCHITECTURE, "Figura 2. Arquitectura de alto nivel del monitoreo de sensores (RF-10).", width_cm=16)
h2("5.1 Componentes")
table([2600, 6426], ["Componente", "Función"], [
    ["Nodo ESP32 con DHT22 y sensor IR/ToF", "Mide temperatura, humedad y paso de personas; el firmware publica las lecturas y un heartbeat periódico."],
    ["Broker MQTT (Mosquitto)", "Recibe los mensajes de todas las sucursales y los entrega a los suscriptores."],
    ["Ingesta (suscriptor MQTT)", "Se suscribe al broker, valida las lecturas y las entrega al servicio de monitoreo."],
    ["Servicio de monitoreo y alertas", "Aplica umbrales, controla el timeout de heartbeat de cada sensor y el estado de la conexión, genera alertas, guarda los datos en MySQL y publica novedades hacia el canal en tiempo real."],
    ["API REST", "Entrega historial y estado actual al panel."],
    ["Stream SSE", "Envía en vivo valores y alertas nuevos al navegador."],
    ["MySQL", "Almacena lecturas, sensores, umbrales y alertas."],
    ["Panel web de monitoreo", "Muestra valores actualizados y advertencias al técnico de mantenimiento."],
])
p()
h2("5.2 Flujo de datos paso a paso")
numbered([
    "Los sensores DHT22 e IR/ToF entregan su medición al firmware del ESP32 (I2C/GPIO).",
    "El ESP32 publica la lectura y un heartbeat en el broker MQTT mediante Wi-Fi.",
    "La ingesta, suscrita al broker, recibe el mensaje, lo valida y lo entrega al servicio de monitoreo junto con la marca de último dato del sensor.",
    "El servicio compara el valor con el umbral y, si corresponde, genera una alerta FUERA_DE_RANGO.",
    "El servicio almacena la lectura (y la alerta) en MySQL mediante SQL, sin intervención del usuario.",
    "El servicio publica los valores y alertas nuevos en el stream SSE, que actualiza el panel web en vivo (flujo normal).",
    "Si un sensor no envía datos tras el timeout, el servicio de monitoreo lo marca SIN_DATOS y genera la alerta SENSOR_SIN_DATOS, que se muestra en el panel (flujo alterno).",
    "Si la conexión falla, el servicio de monitoreo genera la alerta SIN_CONEXION y el panel muestra la advertencia (excepción).",
    "El técnico consulta el historial y el estado por HTTP/REST; los datos permanecen en MySQL para análisis posteriores.",
])
p()

# ---------- 6. Verification ----------

page_break()
h1("6. Verificación del diseño")
p("Se comprobó que cada paso del requerimiento RF-10 está cubierto por al menos una clase y un componente.")
table([2300, 2300, 2200, 2226], ["Elemento de RF-10", "Cómo se cubre", "Clases", "Componentes"], [
    ["Precondición: sensores instalados y configurados", "Los sensores existen asociados a una sucursal, con tipo y ubicación.", "Sucursal, Sensor y subclases, Umbral", "Nodo ESP32, sensores"],
    ["Flujo normal: recibir datos", "El servicio recibe y valida cada lectura.", "MonitorService, Lectura, Sensor", "Broker MQTT, Ingesta"],
    ["Flujo normal: mostrar valores actualizados", "El panel actualiza los valores en vivo.", "PanelMonitoreo, MonitorService", "Stream SSE, Panel web"],
    ["Flujo normal: almacenar automáticamente", "Cada lectura se guarda al recibirse.", "LecturaRepository, LecturaMySQLRepository", "Servicio de monitoreo, MySQL"],
    ["Flujo alterno: sensor deja de enviar datos", "El timeout desde la última lectura marca el sensor y genera una advertencia en pantalla.", "Sensor.estaInactivo, MonitorService.verificarSensoresInactivos, Alerta (SENSOR_SIN_DATOS)", "Servicio de monitoreo y alertas, SSE, Panel web"],
    ["Excepción: falla la conexión", "Se detecta la pérdida de conexión y se genera un mensaje de advertencia.", "MonitorService.detectarPerdidaConexion, Alerta (SIN_CONEXION)", "Servicio de monitoreo y alertas, Panel web"],
    ["Postcondición: datos para consultas y análisis", "Las lecturas se consultan por sensor y rango de fechas.", "LecturaRepository.consultarPorSensor", "MySQL, API REST"],
    ["Necesidad del caso: alertas proactivas", "Valores fuera del umbral generan alertas.", "Umbral, Alerta (FUERA_DE_RANGO)", "Servicio de monitoreo y alertas"],
])
p()
p("Coherencia entre ambos diagramas: cada clase de servicio tiene su componente (MonitorService y el servicio de monitoreo y alertas, LecturaRepository y MySQL, PanelMonitoreo y el panel web), y el flujo de datos es el mismo en los dos modelos: sensor, broker, backend, base de datos y panel.")
note("Pendiente: compartir los diagramas con el docente y registrar sus observaciones.")

# ---------- 7. Next steps ----------

h1("7. Próximos pasos")
for t in ["Avance #2 (RF-11): modelar el almacenamiento de los datos de los sensores en MySQL (modelo de datos y arquitectura de módulos y base de datos).",
          "Construir el prototipo web: simulador de sensores que publique en MQTT, servicio de ingesta con Flask y panel con actualización en vivo.",
          "Definir los valores de los umbrales y el timeout de heartbeat junto con el técnico de mantenimiento.",
          "Incorporar las observaciones del docente al modelo antes de implementar."]:
    bullet(t)

# ---------- 8. Closing questions ----------

h1("8. Preguntas de cierre")
note("Borrador para que el grupo lo ajuste con sus propias palabras y experiencias.")
rich([("¿Qué aprendimos de la actividad realizada?", True)])
p("Aprendimos a traducir un requerimiento en dos vistas complementarias: el diagrama de clases, que define qué información se monitorea y cómo se relaciona, y el diagrama de arquitectura, que define cómo viajan los datos desde el sensor hasta la pantalla. También comprendimos que los flujos alternos y las excepciones, como la falta de datos o la pérdida de conexión, deben modelarse desde el inicio.")
rich([("¿En qué ámbitos podemos utilizar o aplicar lo realizado?", True)])
p("Podemos aplicarlo en el monitoreo de bodegas, cámaras de frío, salas de servidores o aulas, en sistemas de aforo en comercios y, en general, en cualquier proyecto de IoT que combine sensores, mensajería, base de datos y un panel web.")
rich([("¿Hubo algún término, definición o parte del proceso que necesitemos reforzar?", True)])
p("Nos gustaría reforzar los conceptos de mensajería MQTT (calidad de servicio y mensajes retenidos), la diferencia entre SSE y WebSocket, y el uso correcto de las relaciones de agregación y composición en UML.")

# ---------- 9. Conclusion ----------

h1("9. Conclusión")
p("Se analizó RF-10 y se elaboraron un diagrama de clases y un diagrama de arquitectura que cubren el flujo normal, el flujo alterno y la excepción del requerimiento. La tabla de verificación muestra que cada paso tiene clases y componentes que lo respaldan, lo que deja una base coherente para el prototipo web.")

doc.save(OUTPUT)
print(f"[ÉXITO] Archivo '{OUTPUT.name}' generado correctamente.")
