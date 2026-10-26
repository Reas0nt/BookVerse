"""Generate the RF-08 progress report (Avance #3, week 9) as a Word document."""

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Twips

OUTPUT = "Informe_Avance3_RF08_Semana9.docx"
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


def code(text):
    par = p(after=2)
    add_run(par, text, font="Consolas", size=10)
    shade(par._p.get_or_add_pPr(), COLOR_CODE)


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


def table(widths, head, rows, center_cols=(), bold_last=False, row_fill=None):
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
        fill = row_fill or (COLOR_ZEBRA if i % 2 else "FFFFFF")
        for c, text in enumerate(row):
            fill_cell(cells[c], text, widths[c], fill,
                      bold=bold_last and c == len(row) - 1, center=c in center_cols)
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

add_page_number_footer("BookVerse - RF-08 - Avance #3 - Página ")

SCREENSHOT = "../semana11-evaluacion/capturas/historial_mantenimientos.png"

# ---------- Cover ----------

centered("Integración de Competencias 2", 16, bold=True, color=COLOR_TITLE, before=90, after=10)
centered("Actividad 2.4: Avance #3 (semana 9)", 14, color=COLOR_TITLE, after=30)
centered("Informe de avance RF-08", 22, bold=True, color=COLOR_HEADER, after=10)
centered("Historial de mantenimiento de equipos - Proyecto BookVerse", 13, after=60)
table([3000, 6026], ["Dato", "Detalle"], [
    ["Integrantes", ", ".join(MEMBERS)],
    ["Docente", "Manuel Merino"],
    ["Fecha", "Semana 9, octubre 2026"],
    ["Requerimiento", "RF-08: historial de mantenimiento de equipos"],
    ["Archivo complementario", "Historial_Mantenimiento_RF08_Semana9.xlsx"],
])
page_break()

# ---------- 1. Introduction ----------

h1("1. Introducción y objetivo")
p("El proyecto BookVerse requiere llevar un historial de todas las reparaciones y mantenimientos realizados a los equipos de oficina, de modo que cualquier persona autorizada pueda saber qué se hizo, cuándo, a qué equipo y con qué resultado. Esta necesidad corresponde al requerimiento RF-08.")
p("Objetivo general: organizar los requisitos para consultar el historial de mantenimiento de cada equipo, definir cómo se accede a cada entrada y documentar de forma completa cada servicio realizado.")
p("Objetivos específicos:")
for t in ["Identificar los requisitos funcionales y de datos necesarios para consultar el historial.",
          "Determinar los parámetros de búsqueda que permiten encontrar una entrada con facilidad: fecha, tipo de mantenimiento, número de serie y otros.",
          "Definir las vías de acceso a cada entrada y la información que se muestra de cada servicio.",
          "Documentar el historial con un formato uniforme y controlar la calidad de los datos registrados."]:
    bullet(t)
p("Este avance se entrega en dos formas complementarias: la planilla Historial_Mantenimiento_RF08_Semana9.xlsx y el sistema web de mantenimiento desarrollado por el grupo (opción /mantenimientos/), que implementa la misma consulta.")
note("Nota: los datos de las tablas de ejemplo y las filas amarillas de la planilla son ilustrativos y deben reemplazarse con datos reales del laboratorio. Solo los registros del equipo EQ-005 (máquina virtual del grupo) son reales.")

# ---------- 2. Requirements ----------

h1("2. Requisitos para consultar el historial (RF-08)")
p("Los requisitos se derivan del caso BookVerse (Etapa II), donde RF-08 se define como sigue.")
table([2400, 6626], ["Elemento del caso", "Definición"], [
    ["Descripción", "Lleva un historial de todas las reparaciones y mantenimientos realizados a los equipos de oficina."],
    ["Actor", "Administrador de mantenimiento."],
    ["Precondiciones", "Los mantenimientos deben estar registrados en el sistema."],
    ["Flujo normal", "El administrador consulta el historial y el sistema muestra los registros."],
    ["Flujo alterno", "Si no hay registros, se muestra un mensaje indicando que no hay mantenimientos realizados."],
    ["Excepciones", "Si el sistema no puede acceder a la base de datos, se genera un mensaje de error."],
    ["Postcondiciones", "El historial queda disponible para futuras consultas."],
])
p()
h2("2.1 Requisitos funcionales")
for t in ["Consultar el historial completo de mantenimientos preventivos y correctivos de todos los equipos.",
          "Filtrar el historial por fecha, tipo de mantenimiento, número de serie e identificador del equipo.",
          "Visualizar, por cada entrada, la fecha, el tipo, el equipo, el técnico y los detalles de la intervención.",
          "Informar con un mensaje claro cuando la consulta no entrega registros: no hay mantenimientos realizados.",
          "Informar un error cuando no se puede acceder a los datos (en el sistema web, un mensaje de error de base de datos; en la planilla, archivo no disponible o dañado, para lo cual se usa la copia de respaldo)."]:
    bullet(t)
h2("2.2 Requisitos de datos")
for t in ["Cada entrada debe estar asociada a un equipo registrado en el inventario (ID de equipo y número de serie).",
          "Cada entrada debe tener un identificador único y correlativo (HM-NNN) que no se reutiliza.",
          "Los datos deben ser completos, con formato uniforme (fechas DD-MM-AAAA, valores de listas controladas) y verificados por una segunda persona.",
          "El historial es de solo adición: las entradas registradas no se modifican ni se eliminan.",
          "Debe existir una copia de respaldo para poder consultar el historial ante una falla de acceso."]:
    bullet(t)

# ---------- 3. Search criteria ----------

h1("3. Parámetros y criterios de búsqueda")
p("Los criterios se eligieron para responder las preguntas más frecuentes de quien consulta: qué se hizo en un período, qué equipo intervino, qué tipo de trabajo fue y en qué estado quedó.")
table([1900, 1500, 2800, 2826], ["Criterio", "Campo", "En la planilla (Excel)", "En el sistema web"], [
    ["Fecha (rango)", "Fecha", "Autofiltro de fecha: Entre...", "Campos Desde y Hasta"],
    ["Tipo de mantenimiento", "Tipo", "Autofiltro: Preventivo / Correctivo", "Lista desplegable Tipo"],
    ["N° de serie", "N° de serie", "Autofiltro de texto: Contiene...", "Campo Código o N° de serie"],
    ["ID de equipo", "ID equipo", "Autofiltro: marcar el equipo", "Campo Código o N° de serie"],
    ["Categoría", "Categoría", "Autofiltro: hardware, software, limpieza, configuración", "No es filtro; se ve en el detalle"],
    ["Resultado / estado", "Resultado / estado", "Autofiltro: Resuelto, Pendiente, Derivado", "No es filtro; se usa la planilla"],
    ["Técnico", "Técnico", "Autofiltro de técnico", "Se muestra en la lista y el detalle"],
    ["ID de entrada", "ID entrada", "Buscar (Ctrl+B) o autofiltro", "Abrir con Ver detalle"],
])
p()
p('La hoja "Criterios de Búsqueda" del archivo Excel contiene esta misma tabla con un ejemplo por criterio. Los filtros se pueden combinar: por ejemplo, correctivos de un equipo en un rango de fechas.')

# ---------- 4. Access ----------

h1("4. Acceso a las entradas de mantenimiento")
p("Se definieron dos vías de acceso. Ambas presentan los mismos datos de cada servicio.")
h2("4.1 Planilla Excel")
numbered(["Abrir el archivo y entrar a la hoja Historial Mantenimiento; la fila de encabezado está inmovilizada para mantenerse visible.",
          "Usar la flecha del encabezado de la columna deseada (Fecha, Tipo, N° de serie, etc.) y aplicar el filtro.",
          "Ordenar por fecha, de más reciente a más antigua, con el mismo menú.",
          "Leer en la misma fila todos los datos del servicio: fecha, equipo, N° de serie, tipo, categoría, descripción de la intervención, repuestos usados, resultado, técnico y verificador.",
          "Para volver a ver todo el historial, borrar los filtros."])
p("El N° de serie se obtiene automáticamente desde la hoja Equipos mediante una fórmula, por lo que no puede digitarse mal y permite buscar por número de serie.")
h2("4.2 Sistema web de mantenimiento")
p("La opción Historial del sistema web (ruta /mantenimientos/) lista las entradas ordenadas de la más reciente a la más antigua. Sobre la lista se ofrecen los filtros Desde, Hasta, Tipo y Código o N° de serie, que se combinan entre sí. Cada fila incluye el vínculo Ver detalle, que abre la entrada con descripción, observaciones, datos del equipo y técnico. Si no hay resultados se informa que no hay mantenimientos, y si la base de datos no responde se muestra un mensaje de error, como exige el caso.")
picture(SCREENSHOT, "Figura 1. Historial de mantenimientos del sistema web con filtros por fecha, tipo y código o N° de serie (datos de demostración del sistema).")

# ---------- 5. Documentation ----------

h1("5. Documentación completa del historial")
p("Cada servicio se registra como una fila de la hoja Historial Mantenimiento, con el siguiente formato.")
table([2000, 5426, 1600], ["Campo", "Descripción", "Obligatorio"], [
    ["ID entrada", "Identificador único correlativo con formato HM-NNN.", "Sí"],
    ["Fecha", "Fecha de la intervención, formato DD-MM-AAAA.", "Sí"],
    ["ID equipo", "Equipo intervenido, elegido de una lista que proviene de la hoja Equipos.", "Sí"],
    ["N° de serie", "Calculado automáticamente a partir del ID equipo.", "Automático"],
    ["Tipo", "Preventivo o correctivo.", "Sí"],
    ["Categoría", "Hardware, software, limpieza o configuración.", "Sí"],
    ["Descripción de la intervención", "Qué se hizo, el síntoma o motivo y las pruebas realizadas.", "Sí"],
    ["Repuestos usados", "Nombre, código de pieza (PZ-NNN) y cantidad; Ninguno si no corresponde.", "Sí"],
    ["Resultado / estado", "Resuelto, Pendiente o Derivado.", "Sí"],
    ["Técnico", "Persona que realizó la intervención.", "Sí"],
    ["Verificado por", "Persona distinta del técnico que revisó la entrada; Pendiente si aún no se revisa.", "Sí"],
], center_cols=(2,))
p()
h2("5.1 Ejemplo de entradas")
note("EJEMPLO - datos ilustrativos, no corresponden a mantenimientos reales del laboratorio.")
table([1000, 1300, 950, 1350, 2926, 1500], ["ID", "Fecha", "Equipo", "Tipo", "Intervención", "Resultado"], [
    ["HM-002", "06-10-2026", "EQ-002", "Correctivo", "Reemplazo de memoria RAM defectuosa (RAM DDR4 8 GB, PZ-002, x1).", "Resuelto"],
    ["HM-003", "07-10-2026", "EQ-003", "Correctivo", "Reemplazo de disco con errores de lectura (Disco SSD 480 GB, PZ-001, x1).", "Resuelto"],
    ["HM-006", "12-10-2026", "EQ-002", "Preventivo", "Limpieza de teclado, pantalla y ventilación.", "Resuelto"],
    ["HM-007", "13-10-2026", "EQ-003", "Correctivo", "Fuente de poder con ruido; a la espera de repuesto.", "Pendiente"],
], row_fill=COLOR_NOTE)
p()
h2("5.2 Registros reales del equipo EQ-005")
p("El equipo EQ-005 (WIN10-BOOKVERSE) es la máquina virtual VirtualBox con Windows 10 IoT Enterprise LTSC 2021 (versión 21H2, compilación 19044) creada por el grupo en el Avance 2. Sus dos entradas son reales:")
table([1000, 1300, 3126, 2200, 1400], ["ID", "Fecha", "Intervención", "Solución", "Resultado"], [
    ["HM-009", "13-10-2026", "Instalación y configuración inicial de Windows 10 IoT Enterprise LTSC 2021 en VirtualBox.", "Instalación guiada según el informe del Avance 2.", "Resuelto"],
    ["HM-010", "20-10-2026", "La máquina virtual no iniciaba (VERR_VMX_IN_VMX_ROOT_MODE) porque el módulo KVM del anfitrión retenía VT-x.", "Se descargaron kvm_intel y kvm y se fijó kvm.enable_virt_at_load=0.", "Resuelto"],
])
p()

# ---------- 6. Quality control ----------

h1("6. Control de calidad de los datos")
p("Para que cualquier persona obtenga información completa de cada intervención, se aplican los siguientes controles antes de dar una entrada por válida.")
table([3000, 6026], ["Control", "Cómo se aplica"], [
    ["El equipo existe", "El ID equipo se elige de una lista del inventario; si el equipo no está registrado, el N° de serie muestra EQUIPO NO REGISTRADO y la entrada no se da por válida."],
    ["Campos obligatorios completos", "Se revisa que ninguna entrada tenga vacíos en los campos obligatorios; Ninguno se usa cuando no hubo repuestos."],
    ["Formato de fecha", "La columna Fecha rechaza valores que no son fechas; se usa el formato DD-MM-AAAA."],
    ["Valores controlados", "Tipo, categoría y resultado usan listas desplegables para evitar variantes de escritura."],
    ["Verificación por una segunda persona", "El campo Verificado por lo completa alguien distinto del técnico; mientras no se verifique, queda como Pendiente."],
    ["Sin eliminaciones", "Las entradas son de solo adición. Un error se corrige con una entrada nueva que lo aclare."],
    ["Cobertura de servicios", "Cada servicio realizado debe tener su entrada; se compara el registro del técnico con el historial al cierre de cada semana."],
    ["Respaldo", "Se guarda una copia fechada del archivo después de cada sesión de registro."],
])
p()

# ---------- 7. Teacher review ----------

h1("7. Revisión conjunta con docente")
p("Lista de verificación para completar durante la revisión de accesibilidad y calidad de los datos.")
checklist = ["Requisitos para consultar el historial identificados",
             "Criterios de búsqueda definidos (fecha, tipo, N° de serie)",
             "Acceso a cada entrada definido (planilla y sistema web)",
             "Toda la información del servicio disponible para visualización",
             "Entradas documentadas con el formato establecido",
             "Todos los servicios realizados están registrados",
             "Datos reales reemplazan los ejemplos",
             "Mensajes de la consulta sin registros y de error",
             "Preguntas de cierre respondidas"]
table([4200, 1400, 3426], ["Ítem", "Completo (Sí/No)", "Observaciones"], [[item, "", ""] for item in checklist])
p()

# ---------- 8. Closing questions ----------

h1("8. Preguntas de cierre")
note("Borrador para que el grupo lo ajuste con sus propias palabras y experiencias.")
rich([("¿Qué aprendimos?", True)])
p("Aprendimos que un historial de mantenimiento solo es útil si cada entrada está completa y se puede encontrar con rapidez. Definir criterios de búsqueda como fecha, tipo y número de serie desde el inicio determina qué datos se deben registrar. También vimos la importancia de controlar la calidad de los datos mediante listas controladas, una segunda verificación y la regla de no eliminar entradas.")
rich([("¿En qué ámbitos podemos aplicarlo?", True)])
p("Podemos aplicarlo en el soporte técnico de cualquier oficina, colegio o pyme, en la gestión de activos de TI, en la toma de decisiones sobre renovación de equipos a partir de las fallas repetidas y en auditorías donde se debe demostrar el mantenimiento realizado.")
rich([("¿Qué término o parte del proceso nos gustaría reforzar?", True)])
p("Nos gustaría reforzar el diseño de consultas eficientes sobre bases de datos (índices y filtros combinados) y las buenas prácticas de trazabilidad y auditoría de registros.")

# ---------- 9. Conclusion ----------

h1("9. Conclusión")
p("Se organizaron los requisitos de RF-08, se definieron ocho criterios de búsqueda y dos vías de acceso al historial, y se documentó un formato uniforme que incluye la fecha, el tipo y los detalles de cada intervención. La planilla y el sistema web ofrecen la misma información, y los controles de calidad aseguran que los datos sean completos y verificables.")
p("Como siguientes pasos, el grupo debe reemplazar los datos de ejemplo por los mantenimientos reales del laboratorio y revisar el historial junto al docente.")

doc.save(OUTPUT)
print(f"[ÉXITO] Archivo '{OUTPUT}' generado correctamente.")
