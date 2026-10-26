"""Generate the RF-08 maintenance history workbook (Avance #3, week 9)."""

import datetime as dt

import openpyxl
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.properties import PageSetupProperties

# Shared style (mirrors generar_excel_semana8.py)
font_titulo = Font(name="Segoe UI", size=14, bold=True, color="2C3E50")
font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
font_body = Font(name="Segoe UI", size=10, color="2C3E50")
font_bold = Font(name="Segoe UI", size=10, bold=True, color="2C3E50")
font_banner = Font(name="Segoe UI", size=10, bold=True, color="7D6608")
fill_header = PatternFill(start_color="34495E", end_color="34495E", fill_type="solid")
fill_zebra = PatternFill(start_color="ECF0F1", end_color="ECF0F1", fill_type="solid")
fill_banner = PatternFill(start_color="FCF3CF", end_color="FCF3CF", fill_type="solid")
fill_real = PatternFill(start_color="E8F6EF", end_color="E8F6EF", fill_type="solid")
borde = Border(*(Side(style="thin", color="BDC3C7"),) * 4)
DATE_FMT = "DD-MM-YYYY"
BLANK_ROWS = 40  # empty formatted rows available after the examples
EQUIPOS_BLANK = 15
BANNER = ("EJEMPLO - filas amarillas: datos de muestra, reemplazar con datos reales del laboratorio. "
          "Filas verdes: registros reales del equipo EQ-005 (confirmar fecha).")

d = lambda day, month: dt.date(2026, month, day)

TIPOS = ["Preventivo", "Correctivo"]
CATEGORIAS = ["Hardware", "Software", "Limpieza", "Configuración"]
RESULTADOS = ["Resuelto", "Pendiente", "Derivado"]
SINO = ["Sí", "No"]

EQUIPOS = (
    ["ID equipo", "Nombre / hostname", "Tipo", "Ubicación", "N° de serie", "Usuario responsable"],
    [
        ["EQ-001", "PC-ADM-01", "PC", "Administración", "SN-ADM-4F21A9", "Bastián Andrade"],
        ["EQ-002", "PC-BIB-01", "PC", "Biblioteca", "SN-BIB-7C03D2", "María Ojeda"],
        ["EQ-003", "PC-LAB-01", "PC", "Laboratorio", "SN-LAB-91B6E4", "Maikol Ulloa"],
        ["EQ-004", "NB-GER-01", "Notebook", "Gerencia", "SN-GER-2D88F0", "Bastián Andrade"],
        ["EQ-005", "WIN10-BOOKVERSE", "Máquina virtual", "Laboratorio (VirtualBox)", "VM-BV-0005", "Grupo BookVerse"],
    ],
    [11, 22, 18, 26, 20, 24],
    {4},  # zero-based indexes of real rows
)

EQ_FIRST = 4
EQ_LAST = 3 + len(EQUIPOS[1]) + EQUIPOS_BLANK
EQ_ID_RANGE = f"Equipos!$A${EQ_FIRST}:$A${EQ_LAST}"

HISTORIAL = (
    ["ID entrada", "Fecha", "ID equipo", "N° de serie (automático)", "Tipo", "Categoría",
     "Descripción de la intervención", "Repuestos usados", "Resultado / estado", "Técnico", "Verificado por"],
    [
        ["HM-001", d(5, 10), "EQ-001", None, "Preventivo", "Limpieza", "Limpieza interna y cambio de pasta térmica por temperatura elevada en uso continuo.", "Ninguno", "Resuelto", "Bastián Andrade", "María Ojeda"],
        ["HM-002", d(6, 10), "EQ-002", None, "Correctivo", "Hardware", "Reemplazo de módulo de memoria defectuoso que causaba reinicios aleatorios; se ejecutó prueba de memoria posterior.", "RAM DDR4 8 GB (PZ-002) x1", "Resuelto", "María Ojeda", "Maikol Ulloa"],
        ["HM-003", d(7, 10), "EQ-003", None, "Correctivo", "Hardware", "Reemplazo de disco con errores de lectura; clonación e instalación del sistema en la unidad nueva.", "Disco SSD 480 GB (PZ-001) x1", "Resuelto", "Maikol Ulloa", "Bastián Andrade"],
        ["HM-004", d(8, 10), "EQ-004", None, "Preventivo", "Software", "Actualización de BIOS y controladores del fabricante.", "Ninguno", "Resuelto", "Bastián Andrade", "María Ojeda"],
        ["HM-005", d(9, 10), "EQ-001", None, "Correctivo", "Configuración", "Reconfiguración de la impresora de red tras cambio de dirección IP.", "Ninguno", "Resuelto", "Bastián Andrade", "Maikol Ulloa"],
        ["HM-006", d(12, 10), "EQ-002", None, "Preventivo", "Limpieza", "Limpieza de teclado, pantalla y ventilación.", "Ninguno", "Resuelto", "María Ojeda", "Bastián Andrade"],
        ["HM-007", d(13, 10), "EQ-003", None, "Correctivo", "Hardware", "Fuente de poder con ruido anormal; se diagnosticó el reemplazo y se espera disponibilidad del repuesto.", "Ninguno (a la espera de repuesto)", "Pendiente", "Maikol Ulloa", "Pendiente"],
        ["HM-008", d(14, 10), "EQ-004", None, "Correctivo", "Software", "Error de activación de Microsoft 365 Apps; se deriva al proveedor de licencias.", "Ninguno", "Derivado", "María Ojeda", "Bastián Andrade"],
        ["HM-009", d(15, 10), "EQ-005", None, "Preventivo", "Configuración", "REAL: instalación y configuración inicial de Windows 10 IoT Enterprise LTSC 2021 (21H2, compilación 19044) en una máquina virtual VirtualBox (Avance 2, semana 8).", "Ninguno", "Resuelto", "Grupo BookVerse", "Grupo BookVerse"],
        ["HM-010", d(16, 10), "EQ-005", None, "Correctivo", "Configuración", "REAL: la máquina virtual no iniciaba (VERR_VMX_IN_VMX_ROOT_MODE) porque el módulo KVM del anfitrión retenía VT-x. Se descargaron kvm_intel y kvm (modprobe -r) y se fijó kvm.enable_virt_at_load=0 de forma permanente.", "Ninguno", "Resuelto", "Grupo BookVerse", "Grupo BookVerse"],
    ],
    [11, 13, 11, 20, 13, 15, 60, 30, 16, 20, 18],
    {8, 9},
)

CRITERIOS_HEAD = ["Criterio", "Campo de la hoja Historial Mantenimiento", "Cómo se aplica en la planilla (Excel)",
                  "Cómo se aplica en el sistema web (/mantenimientos/)", "Ejemplo"]
CRITERIOS = [
    ["Fecha (rango)", "Fecha", "Autofiltro de Fecha > Filtros de fecha > Entre... (o Ordenar de más reciente a más antiguo).", "Campos Desde y Hasta (formato AAAA-MM-DD).", "Del 05-10-2026 al 09-10-2026: HM-001 a HM-005."],
    ["Tipo de mantenimiento", "Tipo", "Autofiltro de Tipo: marcar Preventivo o Correctivo.", "Lista desplegable Tipo.", "Correctivo: HM-002, HM-003, HM-005, HM-007, HM-008, HM-010."],
    ["N° de serie", "N° de serie (automático)", "Autofiltro de N° de serie > Filtros de texto > Contiene...", "Campo Equipo (acepta código o N° de serie, coincidencia parcial).", "SN-LAB-91B6E4: HM-003 y HM-007."],
    ["ID de equipo", "ID equipo", "Autofiltro de ID equipo: marcar el equipo.", "Campo Equipo (código del equipo).", "EQ-005: HM-009 y HM-010."],
    ["Categoría", "Categoría", "Autofiltro de Categoría: Hardware, Software, Limpieza o Configuración.", "No disponible como filtro; se ve en el detalle de cada entrada. Usar la planilla.", "Hardware: HM-002, HM-003, HM-007."],
    ["Resultado / estado", "Resultado / estado", "Autofiltro de Resultado / estado: Resuelto, Pendiente o Derivado.", "No disponible como filtro; usar la planilla.", "Pendiente: HM-007."],
    ["Técnico", "Técnico", "Autofiltro de Técnico.", "No disponible como filtro; el técnico aparece en la lista y en el detalle.", "María Ojeda: HM-002, HM-006, HM-008."],
    ["ID de entrada", "ID entrada", "Ctrl+B (Buscar) o autofiltro de ID entrada.", "Abrir la entrada desde el historial (vista de detalle).", "HM-010."],
]

INSTRUCCIONES = [
    ("Propósito", "Este libro mantiene el historial de reparaciones y mantenimientos de los equipos de oficina y permite consultarlo por fecha, tipo, número de serie y otros criterios (RF-08)."),
    ("Filas de ejemplo", "Las filas amarillas con la leyenda EJEMPLO son datos de muestra. Las filas verdes (equipo EQ-005) son registros reales de la máquina virtual del grupo; confirme sus fechas. Reemplace los ejemplos con datos reales del laboratorio antes de entregar."),
    ("Hojas del libro", "Equipos (inventario con N° de serie), Historial Mantenimiento (una fila por intervención), Criterios de Búsqueda e Instrucciones."),
    ("Cómo buscar con el autofiltro", "1) Abra la hoja Historial Mantenimiento. 2) Presione la flecha del encabezado de la columna por la que desea buscar (Fecha, Tipo, N° de serie, etc.). 3) Marque los valores o use Filtros de texto / Filtros de fecha. 4) Para ver todo de nuevo, use Datos > Borrar filtros."),
    ("Cómo ordenar por fecha", "Presione la flecha de la columna Fecha y elija Ordenar de más reciente a más antiguo (o al revés). Ordene solo con el autofiltro para que las filas se mantengan completas."),
    ("Cómo agregar una entrada", "Escriba una fila nueva en la primera fila vacía. ID entrada con formato HM-NNN correlativo; Fecha en formato DD-MM-AAAA; ID equipo se elige de la lista (debe existir en la hoja Equipos). El N° de serie se completa solo."),
    ("N° de serie automático", "La columna N° de serie se calcula con una fórmula a partir del ID equipo; no se digita. Si aparece EQUIPO NO REGISTRADO, registre primero el equipo en la hoja Equipos."),
    ("Campos obligatorios", "ID entrada, Fecha, ID equipo, Tipo, Categoría, Descripción, Resultado / estado y Técnico. Repuestos usados se escribe Ninguno cuando no corresponde."),
    ("Repuestos usados", "Indique nombre, código de pieza (PZ-NNN) y cantidad, por ejemplo: RAM DDR4 8 GB (PZ-002) x1. El código permite cruzar la entrada con el control de inventario del Avance 4."),
    ("Verificado por", "Escriba el nombre de una persona distinta del técnico que revisó la entrada. Si aún no se revisa, escriba Pendiente."),
    ("Nunca sobrescribir ni eliminar", "El historial es de solo adición (append-only): no se editan ni se eliminan filas ya registradas. Un error se corrige con una fila nueva que lo aclare en la descripción. Un estado Pendiente se cierra con una entrada nueva."),
    ("Listas desplegables", "Tipo, Categoría, Resultado / estado y el ID equipo usan listas desplegables; elija un valor de la lista."),
    ("Sin registros", "Si un filtro no devuelve filas, significa que no hay mantenimientos que cumplan el criterio (equivale al mensaje del sistema web: no hay mantenimientos realizados)."),
    ("Respaldo", "Guarde una copia fechada del archivo después de cada sesión de registro."),
]


def print_setup(ws):
    """Landscape, one page wide, so the sheet prints without cut columns."""
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0


def title(ws, text, ncols, with_banner=True):
    ws["A1"] = text
    ws["A1"].font = font_titulo
    if with_banner:
        ws["A2"] = BANNER
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
        ws["A2"].font = font_banner
        ws["A2"].fill = fill_banner
        ws["A2"].alignment = Alignment(horizontal="left", vertical="center")


def header(ws, row, heads):
    for i, h in enumerate(heads, start=1):
        c = ws.cell(row=row, column=i, value=h)
        c.font, c.fill, c.border = font_header, fill_header, borde
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def data_sheet(wb, name, ttl, spec, blank, date_cols=(), dropdowns=None, formulas=None):
    """Data sheet with dropdowns, date validation, autofilter and frozen header.

    formulas maps a column number to a function(row) returning a formula string; the
    formula is written in every row, examples and blanks alike.
    dropdowns values are either a list of options or a range string starting with '='.
    """
    heads, rows, widths, real = spec
    ws = wb.create_sheet(name)
    n = len(heads)
    title(ws, ttl, n)
    header(ws, 3, heads)
    last = 3 + len(rows) + blank
    for r in range(4, last + 1):
        ex = r - 4 < len(rows)
        for c in range(1, n + 1):
            value = rows[r - 4][c - 1] if ex else None
            if formulas and c in formulas:
                value = formulas[c](r)
            cell = ws.cell(row=r, column=c, value=value)
            cell.font, cell.border = font_body, borde
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if ex:
                cell.fill = fill_real if (r - 4) in real else fill_banner
            elif r % 2 == 0:
                cell.fill = fill_zebra
            if c in date_cols:
                cell.number_format = DATE_FMT
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[3].height = 32
    ws.freeze_panes = "A4"
    print_setup(ws)
    ws.auto_filter.ref = f"A3:{get_column_letter(n)}{last}"
    for col, opts in (dropdowns or {}).items():
        formula = opts if isinstance(opts, str) else '"' + ",".join(opts) + '"'
        dv = DataValidation(type="list", formula1=formula, allow_blank=True)
        dv.error, dv.errorTitle = "Seleccione un valor de la lista.", "Valor no válido"
        ws.add_data_validation(dv)
        dv.add(f"{col}4:{col}{last}")
    for col in (get_column_letter(c) for c in date_cols):
        dv = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True)
        dv.error, dv.errorTitle = "Ingrese una fecha válida (DD-MM-AAAA).", "Fecha no válida"
        ws.add_data_validation(dv)
        dv.add(f"{col}4:{col}{last}")
    return ws, last


def main():
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    data_sheet(wb, "Equipos", "INVENTARIO DE EQUIPOS CON N° DE SERIE - BOOKVERSE (RF-08, SEMANA 9)",
               EQUIPOS, EQUIPOS_BLANK)

    serial_lookup = lambda r: (
        f'=IF(C{r}="","",IFERROR(INDEX(Equipos!$E${EQ_FIRST}:$E${EQ_LAST},'
        f'MATCH(C{r},Equipos!$A${EQ_FIRST}:$A${EQ_LAST},0)),"EQUIPO NO REGISTRADO"))'
    )
    ws, last = data_sheet(wb, "Historial Mantenimiento",
                          "HISTORIAL DE MANTENIMIENTO (SOLO ADICIÓN) - BOOKVERSE (RF-08, SEMANA 9)",
                          HISTORIAL, BLANK_ROWS, date_cols=(2,),
                          dropdowns={"C": "=" + EQ_ID_RANGE, "E": TIPOS, "F": CATEGORIAS, "I": RESULTADOS},
                          formulas={4: serial_lookup})
    ws.conditional_formatting.add(
        f"D4:D{last}",
        FormulaRule(formula=['D4="EQUIPO NO REGISTRADO"'], font=Font(bold=True, color="C0392B")))
    ws.conditional_formatting.add(
        f"I4:I{last}",
        FormulaRule(formula=['I4="Pendiente"'], font=Font(bold=True, color="B9770E")))

    # Search criteria
    wc = wb.create_sheet("Criterios de Búsqueda")
    title(wc, "CRITERIOS DE BÚSQUEDA DEL HISTORIAL (RF-08)", len(CRITERIOS_HEAD), with_banner=False)
    wc["A2"] = "Los ejemplos corresponden a las filas de muestra de la hoja Historial Mantenimiento."
    wc["A2"].font = font_body
    header(wc, 3, CRITERIOS_HEAD)
    for i, row in enumerate(CRITERIOS):
        r = 4 + i
        for c, val in enumerate(row, start=1):
            cell = wc.cell(row=r, column=c, value=val)
            cell.font, cell.border = (font_bold if c == 1 else font_body), borde
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if r % 2 == 0:
                cell.fill = fill_zebra
    for i, w in enumerate([22, 30, 48, 48, 40], start=1):
        wc.column_dimensions[get_column_letter(i)].width = w
    wc.row_dimensions[3].height = 36
    wc.freeze_panes = "A4"
    print_setup(wc)

    # Instructions
    wi = wb.create_sheet("Instrucciones")
    wi["A1"] = "INSTRUCCIONES DE LLENADO Y CONSULTA"
    wi["A1"].font = font_titulo
    header(wi, 3, ["Tema", "Indicación"])
    for i, (k, v) in enumerate(INSTRUCCIONES):
        r = 4 + i
        for c, val in enumerate((k, v), start=1):
            cell = wi.cell(row=r, column=c, value=val)
            cell.font, cell.border = font_body, borde
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if r % 2 == 0:
                cell.fill = fill_zebra
    wi.column_dimensions["A"].width = 32
    wi.column_dimensions["B"].width = 110
    print_setup(wi)

    nombre = "Historial_Mantenimiento_RF08_Semana9.xlsx"
    wb.save(nombre)
    print(f"[ÉXITO] Archivo '{nombre}' generado correctamente.")


if __name__ == "__main__":
    main()
