"""Generate the RF-09 progress report (Avance #4, week 10) as a Word document."""

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Twips

OUTPUT = "Informe_Avance4_RF09_Semana10.docx"
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

add_page_number_footer("BookVerse - RF-09 - Avance #4 - Página ")

SCREENSHOT = "../semana11-evaluacion/capturas/repuestos.png"

# ---------- Cover ----------

centered("Integración de Competencias 2", 16, bold=True, color=COLOR_TITLE, before=90, after=10)
centered("Actividad 2.5: Avance #4 (semana 10)", 14, color=COLOR_TITLE, after=30)
centered("Informe de avance RF-09", 22, bold=True, color=COLOR_HEADER, after=10)
centered("Control de inventario de piezas de repuesto - Proyecto BookVerse", 13, after=60)
table([3000, 6026], ["Dato", "Detalle"], [
    ["Integrantes", ", ".join(MEMBERS)],
    ["Docente", "Manuel Merino"],
    ["Fecha", "Semana 10, noviembre 2026"],
    ["Requerimiento", "RF-09: control de inventario de piezas de repuesto"],
    ["Archivo complementario", "Control_Inventario_Repuestos_RF09_Semana10.xlsx"],
])
page_break()

# ---------- 1. Introduction ----------

h1("1. Introducción y objetivo")
p("Para mantener la continuidad operacional de los equipos de oficina, el laboratorio necesita saber qué piezas de repuesto tiene, cuántas hay, en qué estado se encuentran y cuándo ingresaron o salieron. Esta actividad crea el documento de control de inventario que permite registrar y actualizar esos datos.")
p("Objetivo general: crear un documento de control de inventario de piezas de repuesto que registre ingresos, salidas y estado de cada pieza, y que mantenga la disponibilidad actualizada con cada movimiento.")
p("Objetivos específicos:")
for t in ["Diseñar un documento con los campos necesarios: tipo de pieza, cantidad, fecha de ingreso, salida y estado.",
          "Definir un procedimiento de registro de ingresos, salidas y cambios de estado.",
          "Garantizar que el inventario refleje con precisión la disponibilidad de cada pieza en todo momento.",
          "Dejar preparada la revisión conjunta con el docente."]:
    bullet(t)
note("Nota sobre el alcance: en el caso BookVerse (Etapa II), RF-09 se define como la validación del funcionamiento del software después del mantenimiento. La pauta de la semana 10, en cambio, solicita un control de inventario de piezas de repuesto. Este entregable sigue la pauta de la semana 10. El sistema web del grupo implementa ambas funciones: la validación del software en /validaciones/ y el inventario de repuestos en /repuestos/.")
note("Los datos de las tablas de ejemplo y las filas amarillas de la planilla son ilustrativos y deben reemplazarse con datos reales del laboratorio.")

# ---------- 2. Design ----------

h1("2. Diseño del documento de control")
p("El documento es el libro Control_Inventario_Repuestos_RF09_Semana10.xlsx, que tiene cuatro hojas.")
table([2300, 6726], ["Hoja", "Función"], [
    ["Catálogo de Piezas", "Lista las piezas que existen, con su tipo, estado, stock mínimo y ubicación."],
    ["Movimientos", "Registra cada ingreso y cada salida (una fila por movimiento). Es el único lugar donde se anotan las cantidades."],
    ["Inventario", "Muestra por pieza los ingresos, las salidas, el stock actual y una alerta. Todo se calcula con fórmulas."],
    ["Instrucciones", "Guía de llenado, reglas y respaldo."],
])
p()
h2("2.1 Campos del catálogo de piezas")
table([2400, 5126, 1500], ["Campo", "Descripción", "Obligatorio"], [
    ["Código", "Identificador único con formato PZ-NNN.", "Sí"],
    ["Tipo de pieza", "Lista: almacenamiento, memoria, fuente de poder, periféricos, impresión, red u otro.", "Sí"],
    ["Descripción", "Nombre y característica de la pieza (por ejemplo, RAM DDR4 8 GB).", "Sí"],
    ["Estado", "En buen estado, en reparación o fuera de servicio.", "Sí"],
    ["Fecha último cambio de estado", "Fecha en que se fijó el estado vigente, formato DD-MM-AAAA.", "Sí"],
    ["Stock mínimo", "Cantidad bajo la cual se debe reponer; número entero de 0 o más.", "Sí"],
    ["Ubicación", "Lugar donde se guarda la pieza.", "No"],
], center_cols=(2,))
p()
h2("2.2 Campos de movimientos")
table([2400, 5126, 1500], ["Campo", "Descripción", "Obligatorio"], [
    ["ID movimiento", "Identificador único correlativo con formato MOV-NNN.", "Sí"],
    ["Fecha", "Fecha del movimiento (fecha de ingreso o de salida), formato DD-MM-AAAA.", "Sí"],
    ["Código de pieza", "Pieza afectada, elegida de una lista que proviene del catálogo.", "Sí"],
    ["Tipo de movimiento", "Ingreso o salida.", "Sí"],
    ["Cantidad", "Número entero mayor que 0; la planilla rechaza otros valores.", "Sí"],
    ["Equipo destino", "Equipo que recibe la pieza en una salida (EQ-NNN); N/A en los ingresos.", "Sí"],
    ["Responsable", "Persona que realiza el movimiento.", "Sí"],
    ["Motivo", "Compra, donación, reemplazo, etc.; en las salidas se cita la entrada HM-NNN del historial del Avance 3 cuando existe.", "Sí"],
    ["Stock tras el movimiento", "Calculado automáticamente; permite detectar de inmediato una salida mayor al stock.", "Automático"],
], center_cols=(2,))
p()

# ---------- 3. Procedure ----------

h1("3. Registro de ingresos, salidas y estado")
h2("3.1 Procedimiento")
numbered(["Si la pieza no existe, agregarla primero en Catálogo de Piezas con su código, tipo, descripción, estado, fecha, stock mínimo y ubicación.",
          "Para un ingreso, agregar una fila nueva en Movimientos con tipo Ingreso, la cantidad recibida, el responsable y el motivo.",
          "Para una salida, revisar primero el stock actual de la pieza en la hoja Inventario; la cantidad a retirar no puede superarlo.",
          "Agregar una fila nueva en Movimientos con tipo Salida, la cantidad, el equipo destino y el motivo, citando la entrada del historial de mantenimiento si corresponde.",
          "Verificar en la hoja Inventario que el stock actual y la alerta se actualizaron.",
          "Si cambia el estado de una pieza, editar el estado en el catálogo con la fecha del cambio y, si cambia la cantidad utilizable, dejar un movimiento con el motivo.",
          "Guardar una copia de respaldo fechada del archivo."])
h2("3.2 Estados de las piezas")
table([2200, 4826, 2000], ["Estado", "Significado", "Uso permitido"], [
    ["En buen estado", "La pieza funciona y está disponible.", "Puede salir hacia un equipo."],
    ["En reparación", "La pieza falló y está en proceso de reparación o revisión.", "No se instala hasta volver a buen estado."],
    ["Fuera de servicio", "La pieza no se puede reparar o fue dada de baja.", "No se instala; se retira del stock utilizable."],
])
p()

# ---------- 4. Keeping inventory updated ----------

h1("4. Mantenimiento del inventario actualizado")
h2("4.1 Cálculo del stock por fórmulas")
p("La hoja Inventario no contiene valores escritos a mano. Para cada pieza del catálogo se calcula:")
for t in ["Ingresos: suma de las cantidades de los movimientos de tipo Ingreso de esa pieza (función SUMIFS).",
          "Salidas: suma de las cantidades de los movimientos de tipo Salida de esa pieza (función SUMIFS).",
          "Stock actual: ingresos menos salidas.",
          "Alerta: ERROR si el stock es negativo; No disponible si la pieza está en reparación o fuera de servicio, porque esas unidades no se pueden usar; Reponer si el stock es igual o menor al mínimo; y OK en los demás casos."]:
    bullet(t)
p("Como son fórmulas, cada movimiento nuevo actualiza el inventario al instante, y una pieza nueva del catálogo aparece sola en la hoja. Las alertas tienen color: verde para OK, amarillo para Reponer, gris para No disponible y rojo para ERROR.")
h2("4.2 Reglas de consistencia")
for t in ["Nunca se registra una salida mayor que el stock disponible; si ocurre, la planilla muestra ERROR en el inventario y un stock negativo en el movimiento.",
          "Los movimientos son de solo adición (append-only): no se editan ni se eliminan. Un error se corrige con un movimiento contrario que lo explique.",
          "Los movimientos se registran en orden cronológico.",
          "El código de pieza, el tipo de movimiento y el equipo destino se eligen de listas desplegables.",
          "Respaldo: una copia fechada después de cada sesión, guardada en una ubicación distinta al archivo de trabajo."]:
    bullet(t)
h2("4.3 Sistema web de mantenimiento")
p("El sistema web del grupo implementa el mismo control en la opción Repuestos (ruta /repuestos/). Muestra el tipo, nombre, stock y estado de cada repuesto, y permite registrar movimientos, ver el historial de movimientos, agregar repuestos y cambiar el estado. Al registrar un movimiento actualiza el stock en el mismo momento y, si se intenta retirar más unidades de las disponibles, rechaza la operación con el mensaje de stock insuficiente, de modo que el stock nunca queda en negativo.")
picture(SCREENSHOT, "Figura 1. Inventario de repuestos del sistema web con stock y estado por pieza (datos de demostración del sistema).", width_cm=12)

# ---------- 5. Examples ----------

h1("5. Ejemplo de registros")
note("EJEMPLO - datos ilustrativos, no corresponden a existencias reales del laboratorio.")
h2("5.1 Movimientos de ejemplo")
table([1100, 1300, 1000, 1500, 1200, 2926], ["ID", "Fecha", "Pieza", "Movimiento", "Cantidad", "Motivo"], [
    ["MOV-002", "01-10-2026", "PZ-002", "Ingreso", "3", "Compra inicial de repuestos del laboratorio"],
    ["MOV-009", "06-10-2026", "PZ-002", "Salida", "1", "Reemplazo de RAM defectuosa en EQ-002 (entrada HM-002 del historial)"],
    ["MOV-001", "01-10-2026", "PZ-001", "Ingreso", "4", "Compra inicial de repuestos del laboratorio"],
    ["MOV-010", "07-10-2026", "PZ-001", "Salida", "1", "Reemplazo de disco en EQ-003 (entrada HM-003 del historial)"],
    ["MOV-014", "15-10-2026", "PZ-001", "Ingreso", "2", "Reposición de discos tras el reemplazo de MOV-010"],
    ["MOV-008", "02-10-2026", "PZ-008", "Ingreso", "6", "Compra de cables de red"],
    ["MOV-011", "09-10-2026", "PZ-008", "Salida", "4", "Renovación del cableado del puesto de Administración"],
], row_fill=COLOR_NOTE, center_cols=(4,))
p()
h2("5.2 Stock resultante")
p("Con esos movimientos, la hoja Inventario calcula lo siguiente (se incluyen las piezas que se muestran en la tabla anterior).")
table([1100, 2326, 1100, 1000, 1200, 1100, 1200], ["Pieza", "Descripción", "Ingresos", "Salidas", "Stock actual", "Mínimo", "Alerta"], [
    ["PZ-001", "Disco SSD 480 GB", "6", "1", "5", "2", "OK"],
    ["PZ-002", "RAM DDR4 8 GB", "3", "1", "2", "2", "Reponer"],
    ["PZ-008", "Cable de red Cat6 de 2 m", "6", "4", "2", "3", "Reponer"],
], row_fill=COLOR_NOTE, center_cols=(2, 3, 4, 5, 6))
p()
p("La pieza PZ-002 quedó con 2 unidades, igual a su mínimo, y PZ-008 con 2 unidades, bajo su mínimo de 3. Por eso la planilla las marca Reponer. Los movimientos MOV-009 y MOV-010 se relacionan con las entradas HM-002 y HM-003 del historial de mantenimiento del Avance 3, de modo que el uso de cada repuesto queda trazable entre ambos documentos.")

# ---------- 6. Teacher review ----------

h1("6. Revisión conjunta con docente")
p("Lista de verificación para completar al presentar el control de inventario y los registros.")
checklist = ["Documento de control creado con tipo de pieza, cantidad, fecha de ingreso, salida y estado",
             "Registro de ingresos y salidas funcionando",
             "Campo de estado con valores definidos",
             "Stock calculado por fórmulas y actualizado con cada movimiento",
             "Alerta de reposición y error por salida mayor al stock",
             "Información de piezas disponibles precisa según los movimientos",
             "Datos reales reemplazan los ejemplos",
             "Preguntas de cierre respondidas"]
table([4200, 1400, 3426], ["Ítem", "Completo (Sí/No)", "Observaciones"], [[item, "", ""] for item in checklist])
p()

# ---------- 7. Closing questions ----------

h1("7. Preguntas de cierre")
note("Borrador para que el grupo lo ajuste con sus propias palabras y experiencias.")
rich([("¿Qué aprendimos?", True)])
p("Aprendimos que un inventario confiable no se escribe a mano: el stock debe calcularse a partir de los movimientos para que siempre refleje la disponibilidad real. También aprendimos la importancia de registrar el estado de cada pieza, de impedir salidas mayores al stock y de relacionar los repuestos con las intervenciones de mantenimiento.")
rich([("¿En qué ámbitos podemos aplicarlo?", True)])
p("Podemos aplicarlo en la bodega de cualquier oficina o laboratorio, en el control de insumos de impresión, en el soporte técnico y en cualquier proceso donde se deba saber cuántas unidades hay disponibles y cuándo reponerlas.")
rich([("¿Qué término o parte del proceso nos gustaría reforzar?", True)])
p("Nos gustaría reforzar el cálculo de niveles de reposición (stock mínimo y punto de pedido) y el uso de fórmulas y validaciones avanzadas en hojas de cálculo.")

# ---------- 8. Conclusion ----------

h1("8. Conclusión")
p("Se creó un documento de control de inventario con catálogo de piezas, registro de movimientos e inventario calculado por fórmulas. El documento incluye los campos solicitados (tipo de pieza, cantidad, fecha de ingreso, salida y estado), mantiene la disponibilidad actualizada con cada ingreso y salida y alerta cuando conviene reponer o cuando se registra una salida mayor al stock. El sistema web del grupo aplica la misma regla de forma automática.")
p("Como siguientes pasos, el grupo debe reemplazar los datos de ejemplo por las piezas y movimientos reales del laboratorio y presentar el control de inventario al docente para su revisión.")

doc.save(OUTPUT)
print(f"[ÉXITO] Archivo '{OUTPUT}' generado correctamente.")
