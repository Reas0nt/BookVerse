"""Generate the RF-11 progress report (Etapa 3, Avance #2, week 13) as a Word document."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Twips

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "Informe_Avance2_RF11_Semana13.docx"
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

add_page_number_footer("BookVerse - RF-11 - Etapa 3 Avance #2 - Página ")

DIAGRAMS = HERE / "diagramas"
DIAGRAM_CLASSES = str(DIAGRAMS / "clases_rf11.png")
DIAGRAM_ARCHITECTURE = str(DIAGRAMS / "arquitectura_rf11.png")
DIAGRAM_MER = str(DIAGRAMS / "mer_rf11.png")
DIAGRAM_RELATIONAL = str(DIAGRAMS / "relacional_rf11.png")

# ---------- Cover ----------

centered("Integración de Competencias 2", 16, bold=True, color=COLOR_TITLE, before=90, after=10)
centered("Etapa 3 - Avance #2 (semana 13)", 14, color=COLOR_TITLE, after=30)
centered("Informe de avance RF-11", 22, bold=True, color=COLOR_HEADER, after=10)
centered("Almacenamiento y modelo de datos de sensores ambientales - Proyecto BookVerse", 13, after=60)
table([3000, 6026], ["Dato", "Detalle"], [
    ["Integrantes", ", ".join(MEMBERS)],
    ["Docente", "Manuel Merino"],
    ["Fecha", "Semana 13, noviembre 2026"],
    ["Requerimiento", "RF-11: almacenamiento y modelo de datos de sensores ambientales en base de datos"],
    ["Entregables", "Diagrama de clases, diagrama de arquitectura, modelo entidad-relación (MER), modelo relacional y script SQL"],
])
page_break()

# ---------- 1. Introduction ----------

h1("1. Introducción y objetivo")
p("En el Avance #1 se modeló el monitoreo de los sensores de las sucursales (RF-10). Este avance continúa con RF-11: guardar los datos de los sensores en una base de datos consultable. BookVerse utiliza MySQL, por lo que el modelo se diseña para ese motor. Los datos de temperatura tienen un interés especial, porque sus variaciones permiten detectar problemas en las bodegas antes de que dañen los libros.")
p("Objetivo general: diseñar el modelo de datos de RF-11 y verificar que registra y permite consultar los datos de los sensores, en particular las variaciones de temperatura.")
p("Objetivos específicos:")
for t in ["Analizar RF-11 y cómo el sistema reacciona y registra los datos ante variaciones de temperatura.",
          "Elaborar un diagrama de clases con las clases principales de captura y procesamiento de datos.",
          "Elaborar un diagrama de arquitectura que muestre cómo los componentes gestionan y almacenan los datos en tiempo real.",
          "Elaborar el modelo entidad-relación (MER) y el modelo relacional con entidades, claves primarias y foráneas, relaciones y atributos.",
          "Verificar la alineación del diseño con RF-11 y responder las preguntas de cierre."]:
    bullet(t)

# ---------- 2. Requirement analysis ----------

h1("2. Análisis del requerimiento RF-11")
table([2400, 6626], ["Elemento del caso", "Definición"], [
    ["Descripción", "Almacenamiento y modelo de datos de sensores ambientales en una base de datos (MySQL según el caso)."],
    ["Actor", "Administrador de base de datos."],
    ["Precondiciones", "La base de datos está creada y es accesible."],
    ["Flujo normal", "1) Recibe los datos del módulo de monitoreo. 2) Los inserta en la base de datos. 3) Permite consultar los datos almacenados."],
    ["Flujo alterno / excepción", "Si un dato no se puede insertar, se registra un error y se reintenta."],
    ["Postcondiciones", "Los datos quedan registrados para análisis posteriores y para los reportes."],
])
p()
h2("2.1 Cómo se manejan las variaciones de temperatura")
p("Cada lectura de temperatura que llega desde el módulo de monitoreo sigue este recorrido:")
numbered([
    "El servicio recibe la lectura (sensor, valor y fecha y hora) y la compara con el umbral de temperatura de la sucursal.",
    "La lectura se guarda siempre, esté o no dentro del rango. Así queda el historial completo y se pueden analizar las variaciones en el tiempo.",
    "Si el valor está fuera del rango, se crea además una alerta FUERA_DE_RANGO asociada a esa lectura.",
    "Si la inserción falla, se registra el error y se reintenta hasta un máximo de intentos; si no se logra, queda el registro del error con el dato perdido.",
    "El administrador consulta después las lecturas por sensor y rango de fechas, las temperaturas fuera de umbral o los promedios por día y sucursal.",
])
p()
p("El umbral no se copia en cada lectura: se guarda una vez por sucursal y tipo de sensor. Si el umbral cambia, el historial de lecturas no se altera y solo cambia cómo se evalúan los datos nuevos.")

# ---------- 3. Class diagram ----------

h1("3. Diagrama de clases")
p("El diagrama (archivo diagramas/clases_rf11.puml) mantiene las clases del modelo de RF-10 y agrega las necesarias para guardar y consultar los datos: la interfaz RepositorioLecturas, su implementación RepositorioLecturasMySQL y la clase ErrorInsercion.")
picture(DIAGRAM_CLASSES, "Figura 1. Diagrama de clases del almacenamiento de datos de sensores (RF-11).", width_cm=16)
h2("3.1 Clases principales")
table([2900, 6126], ["Clase", "Responsabilidad"], [
    ["ServicioMonitoreo", "Recibe cada lectura, la evalúa con el umbral, crea la alerta si corresponde y delega el guardado en el repositorio."],
    ["RepositorioLecturas (interfaz)", "Define las operaciones de almacenamiento y consulta: guardar, buscarPorSensor y temperaturasFueraDeRango."],
    ["RepositorioLecturasMySQL", "Implementa la interfaz con MySQL. Si guardar() falla, reintenta hasta maxIntentos y registra el error."],
    ["ErrorInsercion", "Registro de un dato que no pudo insertarse: fecha y hora, mensaje e intentos realizados."],
    ["Lectura, Sensor", "Valor medido en una fecha y hora, y el dispositivo que lo mide."],
    ["Umbral, Alerta", "Rango permitido por tipo de sensor y sucursal, y la advertencia generada cuando se sale de él."],
    ["Sucursal", "Local donde están los sensores y se definen los umbrales."],
])
p()
h2("3.2 Decisiones de diseño")
for parts in [
    [("Interfaz y implementación: ", "bold"), ("el servicio depende de RepositorioLecturas y no de MySQL; el reintento y el registro de errores quedan dentro del repositorio.", "")],
    [("Consultas en la interfaz: ", "bold"), ("las tres operaciones corresponden al paso 3 del flujo normal (consultar) y a las variaciones de temperatura.", "")],
    [("Alerta ligada a la lectura: ", "bold"), ("una alerta FUERA_DE_RANGO apunta a la lectura que la originó (0..1, porque SENSOR_SIN_DATOS no tiene lectura).", "")],
    [("Última lectura calculada: ", "bold"), ("el atributo ultimaLectura de RF-10 no se almacena; se obtiene con la lectura más reciente del sensor.", "")],
]:
    bullet(parts)

# ---------- 4. Architecture ----------

page_break()
h1("4. Diagrama de arquitectura")
p("El diagrama (archivo diagramas/arquitectura_rf11.puml) muestra cómo viajan los datos desde el sensor hasta la base de datos y cómo se consultan.")
picture(DIAGRAM_ARCHITECTURE, "Figura 2. Arquitectura de almacenamiento de datos de sensores (RF-11).", width_cm=16)
h2("4.1 Componentes y flujo en tiempo real")
table([2900, 6126], ["Componente", "Función"], [
    ["Sensores en sucursal", "ESP32 con DHT22 y contador de personas; publican cada lectura por MQTT."],
    ["Broker MQTT (Mosquitto)", "Recibe los mensajes y los entrega al backend en cuanto llegan."],
    ["Módulo de monitoreo", "Compara cada lectura con el umbral y crea la alerta si la temperatura está fuera de rango."],
    ["Módulo de almacenamiento", "Inserta la lectura y la alerta en MySQL; si falla, registra el error y reintenta."],
    ["MySQL", "Guarda lecturas, alertas y errores de inserción."],
    ["Panel web / reportes (RF-12)", "Consultan los datos almacenados."],
    ["Administrador de base de datos", "Realiza consultas SQL directas sobre los datos."],
])
p()
p("Cada variación de temperatura recorre la cadena completa en tiempo real: sensor, broker, monitoreo (evaluación), almacenamiento (inserción) y MySQL, de modo que la alerta y la lectura quedan registradas en el mismo momento.")

# ---------- 5. MER ----------

page_break()
h1("5. Modelo entidad-relación (MER)")
p("El MER (archivo diagramas/mer_rf11.puml) usa notación de Chen: las entidades son rectángulos, las relaciones rombos y los atributos óvalos; los identificadores aparecen subrayados.")
picture(DIAGRAM_MER, "Figura 3. Modelo entidad-relación de RF-11.", width_cm=9)
table([3300, 1200, 4526], ["Relación", "Cardinalidad", "Significado"], [
    ["SUCURSAL TIENE SENSOR", "1 : N", "Una sucursal tiene varios sensores; cada sensor pertenece a una sucursal."],
    ["SUCURSAL DEFINE UMBRAL", "1 : N", "Una sucursal define un umbral por tipo de sensor."],
    ["SENSOR REGISTRA LECTURA", "1 : N", "Un sensor registra muchas lecturas en el tiempo."],
    ["SENSOR GENERA ALERTA", "1 : N", "Una alerta siempre es sobre un sensor."],
    ["LECTURA ORIGINA ALERTA", "1 : N", "Una lectura puede originar alertas; las de tipo SENSOR_SIN_DATOS no tienen lectura."],
    ["SENSOR FALLA_EN ERROR_INSERCION", "1 : N", "Un sensor puede tener varios datos que no se pudieron insertar."],
])

# ---------- 6. Relational model ----------

page_break()
h1("6. Modelo relacional")
p("Cada entidad del MER pasa a ser una tabla, y cada relación 1:N se convierte en una clave foránea en el lado N (archivo diagramas/relacional_rf11.puml).")
picture(DIAGRAM_RELATIONAL, "Figura 4. Modelo relacional de RF-11 (MySQL).", width_cm=9)
table([1700, 2000, 2500, 2826], ["Tabla", "Clave primaria", "Claves foráneas", "Atributos"], [
    ["sucursal", "id", "-", "nombre"],
    ["sensor", "id (código del sensor)", "sucursal_id -> sucursal", "tipo, ubicacion"],
    ["umbral", "id", "sucursal_id -> sucursal", "tipo, minimo, maximo (minimo < maximo; único por sucursal y tipo)"],
    ["lectura", "id", "sensor_id -> sensor", "valor, fecha_hora"],
    ["alerta", "id", "sensor_id -> sensor; lectura_id -> lectura (opcional)", "tipo, mensaje, fecha_hora"],
    ["error_insercion", "id", "sensor_id -> sensor", "valor, fecha_hora_lectura, mensaje, intentos, fecha_hora_error"],
])
p()
h2("6.1 Script SQL")
p("El archivo schema_rf11.sql crea la base de datos en MySQL 8 con el mismo modelo del diagrama. Sus decisiones principales:")
for t in ["Motor InnoDB y juego de caracteres utf8mb4, que garantizan integridad referencial y tildes correctas.",
          "Claves foráneas en todas las relaciones, para que no existan lecturas, alertas ni errores de sensores inexistentes.",
          "Índice (sensor_id, fecha_hora) en lectura, que acelera las consultas por sensor y rango de fechas.",
          "Restricción CHECK (minimo < maximo) en umbral y valores DECIMAL(8,2) para las mediciones.",
          "Tres consultas de ejemplo para el paso 3 del flujo: lecturas de un sensor en un rango, temperaturas fuera del umbral y promedio diario por sucursal."]:
    bullet(t)

# ---------- 7. Verification ----------

page_break()
h1("7. Verificación de alineación con RF-11")
table([2300, 2300, 2200, 2226], ["Elemento de RF-11", "Cómo se cubre", "Clases", "Componentes / tablas"], [
    ["Precondición: base de datos creada y accesible", "El script SQL crea la base y las tablas.", "RepositorioLecturasMySQL", "MySQL; schema_rf11.sql"],
    ["Flujo 1: recibir datos del monitoreo", "El servicio entrega cada lectura al repositorio.", "ServicioMonitoreo, RepositorioLecturas", "Módulo de monitoreo"],
    ["Flujo 2: insertar los datos", "guardar() inserta la lectura y la alerta.", "RepositorioLecturasMySQL, Lectura, Alerta", "Módulo de almacenamiento; lectura, alerta"],
    ["Flujo 3: consultar los datos", "Consultas por sensor, rango y fuera de umbral.", "RepositorioLecturas", "MySQL; índice de lectura"],
    ["Excepción: no se puede insertar", "Se registra el error y se reintenta hasta maxIntentos.", "ErrorInsercion, RepositorioLecturasMySQL", "Módulo de almacenamiento; error_insercion"],
    ["Postcondición: datos para análisis", "Historial completo de lecturas y alertas.", "Lectura, Alerta", "lectura, alerta"],
    ["Variaciones de temperatura", "Se guarda toda lectura; fuera de rango crea alerta ligada a la lectura.", "Umbral, Alerta", "umbral, alerta (lectura_id)"],
])
p()
p("Coherencia entre los modelos: cada clase del diagrama tiene su entidad en el MER y su tabla en el modelo relacional, y los componentes de la arquitectura corresponden a los módulos que usan esas clases.")
note("Pendiente: compartir los diagramas con el docente y registrar sus observaciones.")

# ---------- 8. Closing questions ----------

page_break()
h1("8. Preguntas de cierre")
note("Borrador para que el grupo lo ajuste con sus propias palabras y experiencias.")
rich([("¿Qué aprendimos de la actividad realizada?", True)])
p("Aprendimos a pasar de un modelo de clases a un modelo de datos: del MER, que describe entidades y relaciones sin depender del motor, al modelo relacional con claves primarias, claves foráneas y tipos de datos. También vimos que guardar todas las lecturas, y no solo las anormales, es lo que permite analizar las variaciones de temperatura, y que el manejo de errores de inserción debe diseñarse desde el modelo.")
rich([("¿En qué ámbitos podemos utilizar o aplicar lo realizado?", True)])
p("Podemos aplicarlo en el almacenamiento de datos de series de tiempo de cualquier sistema IoT (cámaras de frío, invernaderos, salas de servidores), en sistemas de reportes y análisis, y en el diseño de bases de datos relacionales para otros proyectos.")
rich([("¿Hubo algún término, definición o parte del proceso que necesitemos reforzar?", True)])
p("Nos gustaría reforzar la normalización, el diseño de índices para consultas sobre grandes volúmenes de lecturas y las estrategias de reintento (cuántos intentos y cuánto esperar entre ellos).")

# ---------- 9. Conclusion ----------

h1("9. Conclusión")
p("Se analizó RF-11 y se elaboraron el diagrama de clases, el diagrama de arquitectura, el MER, el modelo relacional y un script SQL para MySQL. El diseño cubre los tres pasos del flujo normal y la excepción de inserción fallida, y conserva el historial de temperaturas y sus alertas para el análisis de variaciones y los reportes de RF-12.")

doc.save(OUTPUT)
print(f"[ÉXITO] Archivo '{OUTPUT.name}' generado correctamente.")
