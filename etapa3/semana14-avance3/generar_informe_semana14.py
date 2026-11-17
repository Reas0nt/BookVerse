"""Generate the RF-12 progress report (Etapa 3, Avance #3, week 14) as a Word document."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Twips

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "Informe_Avance3_RF12_Semana14.docx"
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

add_page_number_footer("BookVerse - RF-12 - Etapa 3 Avance #3 - Página ")

DIAGRAMS = HERE / "diagramas"
SHOTS = HERE / "capturas"
DIAGRAM_CLASSES = str(DIAGRAMS / "clases_rf12.png")
DIAGRAM_ARCHITECTURE = str(DIAGRAMS / "arquitectura_rf12.png")
SHOT_MAIN = str(SHOTS / "01_pagina_principal.png")
SHOT_FULL = str(SHOTS / "02_informe_completo.png")
SHOT_PARTIAL = str(SHOTS / "03_informe_parcial.png")

# ---------- Cover ----------

centered("Integración de Competencias 2", 16, bold=True, color=COLOR_TITLE, before=90, after=10)
centered("Etapa 3 - Avance #3 (semana 14)", 14, color=COLOR_TITLE, after=30)
centered("Informe de avance RF-12", 22, bold=True, color=COLOR_HEADER, after=10)
centered("Generación de reportes operacionales con base en sensores - Proyecto BookVerse", 13, after=60)
table([3000, 6026], ["Dato", "Detalle"], [
    ["Integrantes", ", ".join(MEMBERS)],
    ["Docente", "Manuel Merino"],
    ["Fecha", "Semana 14, 17/11/2026"],
    ["Requerimiento", "RF-12: generación de reportes operacionales con base en sensores"],
    ["Entregables", "Organización de los elementos del informe, diagrama UML del informe, diagrama de arquitectura y flujo de datos, aplicación web con almacenamiento y generación de reportes"],
])
page_break()

# ---------- 1. Introduction ----------

h1("1. Introducción y objetivo")
p("En los avances anteriores se modeló el monitoreo de los sensores de las sucursales (RF-10) y su almacenamiento en una base de datos (RF-11). Este avance continúa con RF-12: usar esos datos para generar informes operacionales con las condiciones promedio, las alertas críticas y las recomendaciones de ajuste, de modo que el gerente de operaciones pueda tomar decisiones sobre las bodegas y las salas.")
p("Objetivo general: diseñar el informe de RF-12 y construir una aplicación web sencilla que almacene lecturas de sensores y genere el informe, verificando que cumple los criterios de calidad definidos.")
p("Objetivos específicos:")
for t in ["Identificar los datos que debe incluir el informe y cómo se presentan de acuerdo con los requerimientos de calidad.",
          "Elaborar un diagrama UML que represente la estructura del informe y las relaciones entre sus elementos.",
          "Elaborar un diagrama de arquitectura y flujo de datos que muestre cómo cada parte del sistema obtiene la información para generar el informe.",
          "Programar una página web con HTML5, CSS3 y JavaScript que almacene datos de sensores y genere los reportes.",
          "Validar la calidad del informe y responder las preguntas de cierre."]:
    bullet(t)

# ---------- 2. Requirement analysis ----------

h1("2. Análisis de RF-12")
table([2400, 6626], ["Elemento del caso", "Definición"], [
    ["Descripción", "Generación de reportes operacionales con base en sensores, incluyendo condiciones promedio, alertas críticas y recomendaciones de ajuste."],
    ["Actor", "Gerente de operaciones."],
    ["Precondición", "Existen datos de sensores almacenados (RF-11) para el periodo que se quiere informar."],
    ["Flujo normal", "1) El sistema procesa los datos. 2) Calcula valores promedio y alertas. 3) Genera un informe con los reportes."],
    ["Flujo alterno", "Si faltan datos críticos, se genera un informe parcial y se notifica."],
    ["Flujo de excepción", "Si hay un error en la generación del informe, se solicita reintento."],
    ["Postcondición", "El informe queda disponible para descarga o visualización."],
])
p()
p("En esta implementación se consideran datos críticos la temperatura y la humedad, porque son las variables que dañan los libros. El conteo de personas se informa, pero su ausencia no vuelve parcial el informe.")

# ---------- 3. Organization of the report ----------

h1("3. Organización de los elementos del informe")
p("Este paso identifica qué datos deben incluirse en el informe y cómo se presentan de acuerdo con los requerimientos de calidad.")
h2("3.1 Datos que incluye el informe")
table([2300, 3500, 3226], ["Elemento", "Contenido", "Presentación"], [
    ["Período y sucursal", "Fecha de inicio (incluida), fecha de término (excluida) y sucursal consultada (o todas).", "Encabezado del informe, antes de los datos."],
    ["Fecha de generación", "Fecha y hora en que se generó el informe.", "Encabezado, junto al período."],
    ["Estado", "COMPLETO o PARCIAL (y ERROR si falla la generación).", "Etiqueta de color junto al título."],
    ["Avisos", "Datos críticos que faltan y motivo del informe parcial.", "Recuadro destacado bajo el encabezado."],
    ["Resumen por tipo de sensor", "Promedio, mínimo, máximo y cantidad de lecturas de temperatura, humedad y conteo de personas.", "Tabla con una fila por sensor; valores con 1 decimal y unidad."],
    ["Alertas críticas", "Cada lectura fuera del umbral: sensor, valor, fecha y hora y límite superado.", "Tabla ordenada por fecha; el título muestra la cantidad."],
    ["Recomendaciones de ajuste", "Acción sugerida cuando el promedio de un sensor está fuera de su umbral (por ejemplo, revisar climatización).", "Lista de viñetas; si no hay ajustes, se indica expresamente."],
])
p()
h2("3.2 Presentación según los requerimientos de calidad")
for parts in [
    [("Orden de lectura: ", "bold"), ("primero el contexto (período, estado, avisos), luego los promedios, las alertas y al final las acciones, que es el orden en que el gerente toma decisiones.", "")],
    [("Un solo formato numérico: ", "bold"), ("valores redondeados a 1 decimal con su unidad (°C, %), para evitar interpretaciones distintas.", "")],
    [("Lo importante a la vista: ", "bold"), ("el estado y los avisos aparecen antes que las tablas, de modo que un informe parcial no se confunda con uno completo.", "")],
    [("Salida utilizable: ", "bold"), ("el mismo informe se ve en pantalla, se descarga en CSV o JSON y se imprime o guarda como PDF.", "")],
]:
    bullet(parts)

# ---------- 4. UML ----------

h1("4. Diagrama UML del informe")
p("El diagrama (archivo diagramas/clases_rf12.puml) representa la estructura del informe y las relaciones entre sus elementos. Reutiliza las clases del modelo de RF-10 y RF-11 (Sucursal, Alerta, Umbral y RepositorioLecturas).")
picture(DIAGRAM_CLASSES, "Figura 1. Diagrama UML del informe operacional (RF-12).", width_cm=16)
table([2900, 6126], ["Elemento", "Responsabilidad"], [
    ["Informe", "Clase central: período, fecha de generación, estado y avisos. Se compone de resúmenes, alertas y recomendaciones."],
    ["EstadoInforme", "Enumeración con los estados COMPLETO, PARCIAL y ERROR."],
    ["ResumenSensor", "Promedio, mínimo, máximo y cantidad de lecturas de un tipo de sensor."],
    ["AlertaCritica", "Mensaje y fecha y hora de una alerta incluida en el informe; se basa en una Alerta de RF-10."],
    ["Recomendacion", "Mensaje de ajuste con su prioridad."],
    ["GeneradorInforme", "Consulta las lecturas, las compara con los umbrales y crea el Informe para una sucursal y un período."],
    ["Exportador (interfaz)", "Descarga o imprime el informe."],
    ["Sucursal", "Cada informe corresponde a una sucursal."],
])
p()
p("Las relaciones de composición (Informe con ResumenSensor, AlertaCritica y Recomendacion) indican que esos elementos no existen fuera del informe. GeneradorInforme depende de la interfaz RepositorioLecturas de RF-11 y no de una base de datos concreta, por lo que la aplicación web puede usar el almacenamiento del navegador y el sistema final puede usar MySQL sin cambiar el generador.")

# ---------- 5. Architecture ----------

page_break()
h1("5. Diagrama de arquitectura y flujo de datos")
p("El diagrama (archivo diagramas/arquitectura_rf12.puml) muestra cómo cada parte del sistema obtiene la información necesaria para generar el informe.")
picture(DIAGRAM_ARCHITECTURE, "Figura 2. Arquitectura y flujo de datos del informe (RF-12).", width_cm=11)
table([2900, 6126], ["Parte del sistema", "De dónde obtiene sus datos"], [
    ["Sensores en sucursal", "Miden temperatura y aforo y publican cada lectura por MQTT."],
    ["Broker MQTT", "Recibe los mensajes de los sensores y los entrega al módulo de monitoreo."],
    ["Módulo de monitoreo (RF-10 / RF-11)", "Recibe los mensajes, evalúa las lecturas con los umbrales y guarda lecturas y alertas en MySQL."],
    ["MySQL", "Conserva lecturas, umbrales y alertas; es la única fuente de datos del informe."],
    ["Módulo de informes (RF-12)", "Consulta a MySQL las lecturas, umbrales y alertas del período, calcula los promedios, detecta las alertas críticas y genera las recomendaciones."],
    ["Panel web", "Recibe el informe ya generado y lo muestra al gerente."],
    ["Exportación", "Recibe el informe generado y lo entrega como archivo CSV o impresión PDF."],
    ["Prototipo HTML5 + CSS3 + JS", "Reemplaza a MySQL y al módulo de informes con datos guardados en localStorage y la misma lógica de cálculo."],
])
p()
p("Los datos se manejan en un solo sentido: del sensor a la base de datos, y de la base de datos al informe. El módulo de informes no modifica las lecturas; solo las consulta. Esto asegura que los datos estén disponibles y se mantengan consistentes. Las condiciones especiales (informe parcial y reintento) se manejan dentro del módulo de informes.")

# ---------- 6. Web app ----------

page_break()
h1("6. Aplicación web")
p("La aplicación (carpeta webapp/) es una página sencilla con HTML5, CSS3 y JavaScript, sin dependencias ni servidor. Implementa el almacenamiento de datos de los sensores y la generación de reportes.")
h2("6.1 Estructura")
table([2600, 6426], ["Archivo", "Contenido"], [
    ["index.html", "Estructura de la página: registrar lectura, lecturas almacenadas, umbrales y generar informe."],
    ["styles.css", "Estilos de pantalla y de impresión (al imprimir solo se muestra el informe)."],
    ["js/storage.js", "Almacenamiento en localStorage con validación de los datos."],
    ["js/report.js", "Lógica pura del informe: promedios, alertas, recomendaciones, estado y CSV."],
    ["js/app.js", "Conexión entre la página y la lógica: formularios, tablas, mensajes y descargas."],
    ["tests/", "Pruebas automáticas de storage.js y report.js con el ejecutor de Node."],
])
p()
h2("6.2 Almacenamiento")
p("Los datos se guardan en el localStorage del navegador, con la misma forma que las tablas de RF-11: lecturas, umbrales y alertas. Al registrar una lectura se valida que los campos estén completos y que el valor sea numérico. Como en la base de datos, una lectura repetida para el mismo sensor y la misma fecha y hora se rechaza (equivale a la restricción UNIQUE (sensor_id, fecha_hora) de RF-11). Si el almacenamiento falla o está dañado, la aplicación muestra el error en lugar de continuar con datos incorrectos.")
h2("6.3 Cómo ejecutarla")
numbered([
    "Abrir con doble clic el archivo etapa3/semana14-avance3/webapp/index.html en un navegador (funciona desde file://).",
    "Pulsar \"Simular lecturas (últimas 24 h)\" o registrar lecturas manualmente.",
    "En \"Generar informe\" elegir la sucursal y el rango de fechas, y pulsar \"Generar informe\".",
    "Descargar el informe en CSV o JSON, o imprimirlo o guardarlo como PDF.",
])
p()
h2("6.4 Capturas de pantalla")
picture(SHOT_MAIN, "Figura 3. Página principal de la aplicación, sin lecturas almacenadas.", width_cm=10.5)
picture(SHOT_FULL, "Figura 4. Informe COMPLETO con alertas críticas y recomendaciones (datos simulados).", width_cm=10.5)
picture(SHOT_PARTIAL, "Figura 5. Informe PARCIAL: solo hay datos de temperatura, por lo que se avisa que falta la humedad (datos simulados).", width_cm=10.5)
h2("6.5 Pruebas")
p("La lógica del informe y el almacenamiento tienen pruebas automáticas. Se ejecutan desde la raíz del repositorio con Node:")
par = p()
add_run(par, "node --test etapa3/semana14-avance3/webapp/tests/*.test.js", font="Consolas", size=10)
shade(par._p.get_or_add_pPr(), COLOR_CODE)
p("Resultado: 19 pruebas aprobadas, que cubren el cálculo de promedios, mínimos y máximos con redondeo, las alertas, las recomendaciones, el informe parcial, el período con límite superior excluido, la exportación CSV, el rechazo de lecturas duplicadas o inválidas y el error ante almacenamiento dañado.")

# ---------- 7. Quality ----------

h1("7. Validación de calidad")
p("El caso exige que el sistema genere un informe que cumpla los estándares de calidad establecidos. Se definieron los siguientes criterios y se indica cómo se cumple y verifica cada uno.")
table([1700, 3700, 3626], ["Criterio", "Cómo se cumple", "Cómo se verifica"], [
    ["Completitud", "El informe incluye resumen de los tres sensores, alertas críticas y recomendaciones; los datos críticos que faltan se declaran como aviso.", "Pruebas de report.js; capturas de los informes COMPLETO y PARCIAL."],
    ["Exactitud", "Promedio, mínimo y máximo se redondean a 1 decimal; solo un valor fuera del umbral genera alerta (los límites son inclusivos).", "Pruebas con valores conocidos, incluidos los límites del umbral."],
    ["Trazabilidad", "El informe indica sucursal, período (desde incluida, hasta excluida) y fecha y hora de generación; cada alerta lleva su fecha y hora.", "Revisión del encabezado del informe; prueba del período semiabierto."],
    ["Estado visible", "COMPLETO o PARCIAL se muestra junto al título, junto con un aviso destacado si faltan datos.", "Capturas (figuras 4 y 5); prueba del informe parcial."],
    ["Exportable", "El informe se puede descargar en CSV y JSON e imprimir o guardar como PDF.", "Prueba de la salida CSV; descarga manual de los archivos."],
    ["Tratamiento de errores", "Si la generación falla, se muestra el error y el botón Reintentar.", "Prueba con almacenamiento dañado."],
])
p()
p("Resultado: los criterios se cumplen en el prototipo. La exportación a PDF depende del navegador (imprimir) y se verificó de forma manual.")

# ---------- 8. Traceability ----------

h1("8. Trazabilidad de RF-12")
table([2300, 3300, 3426], ["Paso de RF-12", "Diagrama", "Aplicación web"], [
    ["Precondición: datos almacenados", "Arquitectura: MySQL; clase RepositorioLecturas", "js/storage.js (localStorage con la forma de RF-11)"],
    ["Flujo 1: procesar los datos", "Arquitectura: módulo de informes (consulta lecturas); GeneradorInforme", "report.js: filtro por sucursal y período"],
    ["Flujo 2: calcular promedios y alertas", "ResumenSensor, AlertaCritica, Recomendacion", "report.js: resumen, alertas críticas y recomendaciones"],
    ["Flujo 3: generar el informe", "Clase Informe; GeneradorInforme crea el Informe", "Botón \"Generar informe\" y vista del informe"],
    ["Alterno: faltan datos, informe parcial y aviso", "EstadoInforme.PARCIAL; avisos; nota de la arquitectura", "Estado PARCIAL y aviso en pantalla (figura 5)"],
    ["Excepción: error, solicitar reintento", "EstadoInforme.ERROR; nota de la arquitectura", "Mensaje de error y botón Reintentar"],
    ["Postcondición: descarga o visualización", "Exportador; panel web y exportación", "Vista en pantalla, CSV, JSON e impresión"],
])

# ---------- 9. Closing questions ----------

page_break()
h1("9. Preguntas de cierre")
note("Borrador para que el grupo lo ajuste con sus propias palabras y experiencias.")
rich([("¿Qué aprendimos de la actividad realizada?", True)])
p("Aprendimos a definir primero qué datos y qué presentación necesita el usuario del informe, y a reflejarlo en un diagrama de clases y en un diagrama de flujo de datos antes de programar. También vimos cómo separar la lógica del informe de la forma de guardar los datos, lo que permite probarla de forma automática y reutilizarla cuando se cambie localStorage por MySQL.")
rich([("¿En qué ámbitos podemos utilizar o aplicar lo realizado?", True)])
p("Podemos aplicarlo en informes de monitoreo de cualquier sistema con sensores (bodegas, cámaras de frío, invernaderos, salas de servidores), en paneles de indicadores y en aplicaciones web sencillas que guardan datos en el navegador.")
rich([("¿Hubo algún término, definición o parte del proceso que necesitemos reforzar?", True)])
p("Nos gustaría reforzar la definición de los estándares de calidad de un informe, la conexión de la aplicación web con la base de datos real y las pruebas automáticas de la interfaz.")

# ---------- 10. Conclusion ----------

h1("10. Conclusión")
p("Se organizaron los elementos del informe de RF-12, se elaboraron el diagrama UML y el diagrama de arquitectura y flujo de datos, y se construyó una aplicación web que almacena lecturas y genera el informe con promedios, alertas críticas, recomendaciones, informe parcial y reintento ante errores. El informe cumple los criterios de calidad definidos y queda listo para conectarse a la base de datos de RF-11.")

doc.save(OUTPUT)
print(f"[ÉXITO] Archivo '{OUTPUT.name}' generado correctamente.")
