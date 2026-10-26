"""Generate the RF-09 spare parts inventory workbook (Avance #4, week 10)."""

import datetime as dt

import openpyxl
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.properties import PageSetupProperties

# Shared style (mirrors generar_excel_semana8.py)
font_titulo = Font(name="Segoe UI", size=14, bold=True, color="2C3E50")
font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
font_body = Font(name="Segoe UI", size=10, color="2C3E50")
font_banner = Font(name="Segoe UI", size=10, bold=True, color="7D6608")
fill_header = PatternFill(start_color="34495E", end_color="34495E", fill_type="solid")
fill_zebra = PatternFill(start_color="ECF0F1", end_color="ECF0F1", fill_type="solid")
fill_banner = PatternFill(start_color="FCF3CF", end_color="FCF3CF", fill_type="solid")
fill_real = PatternFill(start_color="E8F6EF", end_color="E8F6EF", fill_type="solid")
borde = Border(*(Side(style="thin", color="BDC3C7"),) * 4)
DATE_FMT = "DD-MM-YYYY"
BLANK_ROWS = 40  # empty formatted rows available after the examples
CATALOG_BLANK = 12
BANNER = "EJEMPLO - reemplazar con datos reales del laboratorio (las filas de muestra no son existencias reales)"

d = lambda day, month: dt.date(2026, month, day)

TIPOS_PIEZA = ["Almacenamiento", "Memoria", "Fuente de poder", "Periféricos", "Impresión", "Red", "Otro"]
ESTADOS = ["En buen estado", "En reparación", "Fuera de servicio"]
MOVIMIENTOS_TIPO = ["Ingreso", "Salida"]
EQUIPOS = ["EQ-001", "EQ-002", "EQ-003", "EQ-004", "EQ-005", "N/A"]

CATALOGO = (
    ["Código", "Tipo de pieza", "Descripción", "Estado", "Fecha último cambio de estado", "Stock mínimo", "Ubicación"],
    [
        ["PZ-001", "Almacenamiento", "Disco SSD 480 GB", "En buen estado", d(1, 10), 2, "Bodega del laboratorio"],
        ["PZ-002", "Memoria", "RAM DDR4 8 GB", "En buen estado", d(1, 10), 2, "Bodega del laboratorio"],
        ["PZ-003", "Memoria", "RAM DDR3 4 GB", "En reparación", d(8, 10), 1, "Bodega del laboratorio"],
        ["PZ-004", "Fuente de poder", "Fuente de poder 500 W", "Fuera de servicio", d(2, 10), 0, "Bodega del laboratorio"],
        ["PZ-005", "Impresión", "Cartucho de tóner negro", "En buen estado", d(1, 10), 2, "Administración"],
        ["PZ-006", "Periféricos", "Teclado USB", "En buen estado", d(1, 10), 1, "Bodega del laboratorio"],
        ["PZ-007", "Periféricos", "Mouse USB", "En buen estado", d(1, 10), 1, "Bodega del laboratorio"],
        ["PZ-008", "Red", "Cable de red Cat6 de 2 m", "En buen estado", d(1, 10), 3, "Bodega del laboratorio"],
    ],
    [11, 20, 30, 20, 22, 14, 26],
    set(),
)
CAT_FIRST = 4
CAT_LAST = 3 + len(CATALOGO[1]) + CATALOG_BLANK
CAT_CODE_RANGE = f"'Catálogo de Piezas'!$A${CAT_FIRST}:$A${CAT_LAST}"

MOVIMIENTOS = (
    ["ID movimiento", "Fecha", "Código de pieza", "Tipo de movimiento", "Cantidad", "Equipo destino",
     "Responsable", "Motivo", "Stock tras el movimiento (automático)"],
    [
        ["MOV-001", d(1, 10), "PZ-001", "Ingreso", 4, "N/A", "Bastián Andrade", "Compra inicial de repuestos del laboratorio", None],
        ["MOV-002", d(1, 10), "PZ-002", "Ingreso", 3, "N/A", "Bastián Andrade", "Compra inicial de repuestos del laboratorio", None],
        ["MOV-003", d(1, 10), "PZ-003", "Ingreso", 2, "N/A", "María Ojeda", "Donación de equipos dados de baja", None],
        ["MOV-004", d(2, 10), "PZ-004", "Ingreso", 1, "N/A", "María Ojeda", "Unidad recibida con falla; queda fuera de servicio", None],
        ["MOV-005", d(1, 10), "PZ-005", "Ingreso", 5, "N/A", "Maikol Ulloa", "Compra de insumos de impresión", None],
        ["MOV-006", d(1, 10), "PZ-006", "Ingreso", 2, "N/A", "Maikol Ulloa", "Compra inicial de periféricos", None],
        ["MOV-007", d(1, 10), "PZ-007", "Ingreso", 3, "N/A", "Maikol Ulloa", "Compra inicial de periféricos", None],
        ["MOV-008", d(2, 10), "PZ-008", "Ingreso", 6, "N/A", "Bastián Andrade", "Compra de cables de red", None],
        ["MOV-009", d(6, 10), "PZ-002", "Salida", 1, "EQ-002", "María Ojeda", "Reemplazo de RAM defectuosa (entrada HM-002 del historial)", None],
        ["MOV-010", d(7, 10), "PZ-001", "Salida", 1, "EQ-003", "Maikol Ulloa", "Reemplazo de disco con errores (entrada HM-003 del historial)", None],
        ["MOV-011", d(9, 10), "PZ-008", "Salida", 4, "EQ-001", "Bastián Andrade", "Renovación del cableado del puesto de Administración", None],
        ["MOV-012", d(12, 10), "PZ-005", "Salida", 2, "EQ-001", "Bastián Andrade", "Cambio de tóner de la impresora de red", None],
        ["MOV-013", d(14, 10), "PZ-007", "Salida", 1, "EQ-002", "María Ojeda", "Reemplazo de mouse dañado en Biblioteca", None],
        ["MOV-014", d(15, 10), "PZ-001", "Ingreso", 2, "N/A", "Bastián Andrade", "Reposición de discos tras el reemplazo de MOV-010", None],
    ],
    [14, 13, 16, 18, 11, 15, 20, 52, 22],
    set(),
)
MOV_FIRST = 4
MOV_LAST = 3 + len(MOVIMIENTOS[1]) + BLANK_ROWS
INV_ROWS = len(CATALOGO[1]) + CATALOG_BLANK  # one inventory row per catalog row

INVENTARIO_HEAD = ["Código", "Tipo de pieza", "Descripción", "Estado", "Ingresos", "Salidas",
                   "Stock actual", "Stock mínimo", "Alerta"]

INSTRUCCIONES = [
    ("Propósito", "Este libro controla las piezas de repuesto del laboratorio (RF-09, semana 10): qué piezas existen, cuántas hay, en qué estado están y qué ingresos y salidas se han registrado."),
    ("Filas de ejemplo", "Las filas con fondo amarillo y la leyenda EJEMPLO son datos de muestra. Reemplácelas con las piezas y movimientos reales del laboratorio antes de entregar."),
    ("Hojas del libro", "Catálogo de Piezas (qué piezas existen y su estado), Movimientos (cada ingreso y salida), Inventario (stock calculado por fórmulas) e Instrucciones."),
    ("Registrar una pieza nueva", "Agregue una fila en Catálogo de Piezas con código PZ-NNN, tipo, descripción, estado, fecha, stock mínimo y ubicación. La pieza aparece sola en Inventario y en la lista de Movimientos."),
    ("Registrar un ingreso", "En Movimientos, escriba una fila nueva: ID MOV-NNN correlativo, fecha DD-MM-AAAA, código de pieza (lista), tipo Ingreso, cantidad (número entero mayor que 0), equipo N/A, responsable y motivo (compra, donación, devolución)."),
    ("Registrar una salida", "En Movimientos, escriba una fila nueva con tipo Salida, la cantidad retirada y el equipo destino (lista EQ-NNN). En el motivo cite la entrada del historial de mantenimiento (HM-NNN) cuando exista."),
    ("Regla de stock", "Nunca registre una salida mayor que el stock disponible. Antes de registrarla, revise el stock actual de la pieza en la hoja Inventario. Si se excede, la columna Stock tras el movimiento y la alerta del Inventario muestran el error."),
    ("Orden de registro", "Registre los movimientos en orden cronológico para que el stock tras cada movimiento sea correcto."),
    ("Inventario en tiempo real", "Ingresos, salidas, stock actual y alerta de la hoja Inventario son fórmulas: se recalculan al guardar cada movimiento. No escriba valores a mano en esa hoja."),
    ("Alertas", "OK: stock por sobre el mínimo. Reponer: stock igual o menor al mínimo. ERROR: salida mayor al stock; revise los movimientos."),
    ("Estado de la pieza", "Valores: En buen estado, En reparación o Fuera de servicio. Para cambiarlo, edite el Estado en Catálogo de Piezas y actualice la fecha del último cambio. Si el cambio altera la cantidad utilizable, deje además un movimiento con el motivo (por ejemplo, Salida: baja por falla)."),
    ("Uso de piezas", "Solo las piezas En buen estado deben salir hacia un equipo. Las piezas En reparación o Fuera de servicio no se instalan."),
    ("Nunca sobrescribir movimientos", "Los movimientos son de solo adición (append-only): no se editan ni se eliminan filas. Un error se corrige con un movimiento contrario que lo aclare en el motivo."),
    ("Listas desplegables", "Tipo de pieza, Estado, Código de pieza, Tipo de movimiento y Equipo destino usan listas desplegables; elija un valor de la lista."),
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


def add_whole_number(ws, col, last, operator, value, message):
    dv = DataValidation(type="whole", operator=operator, formula1=str(value), allow_blank=True)
    dv.error, dv.errorTitle = message, "Cantidad no válida"
    ws.add_data_validation(dv)
    dv.add(f"{col}4:{col}{last}")


def main():
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    ws_c, cat_last = data_sheet(wb, "Catálogo de Piezas", "CATÁLOGO DE PIEZAS DE REPUESTO - BOOKVERSE (RF-09, SEMANA 10)",
                                CATALOGO, CATALOG_BLANK, date_cols=(5,),
                                dropdowns={"B": TIPOS_PIEZA, "D": ESTADOS})
    add_whole_number(ws_c, "F", cat_last, "greaterThanOrEqual", 0, "El stock mínimo debe ser un número entero de 0 o más.")

    # Running stock after each movement; negative means an exit larger than the available stock.
    running = lambda r: (
        f'=IF(OR(C{r}="",D{r}="",E{r}=""),"",'
        f'SUMIFS(E$4:E{r},C$4:C{r},C{r},D$4:D{r},"Ingreso")-SUMIFS(E$4:E{r},C$4:C{r},C{r},D$4:D{r},"Salida"))'
    )
    ws_m, mov_last = data_sheet(wb, "Movimientos", "MOVIMIENTOS DE REPUESTOS (SOLO ADICIÓN) - BOOKVERSE (RF-09, SEMANA 10)",
                                MOVIMIENTOS, BLANK_ROWS, date_cols=(2,),
                                dropdowns={"C": "=" + CAT_CODE_RANGE, "D": MOVIMIENTOS_TIPO, "F": EQUIPOS},
                                formulas={9: running})
    assert mov_last == MOV_LAST
    add_whole_number(ws_m, "E", mov_last, "greaterThan", 0, "La cantidad debe ser un número entero mayor que 0.")
    ws_m.conditional_formatting.add(
        f"I4:I{mov_last}",
        FormulaRule(formula=['AND(ISNUMBER(I4),I4<0)'], font=Font(bold=True, color="FFFFFF"),
                    fill=PatternFill(start_color="C0392B", end_color="C0392B", fill_type="solid")))

    # Inventory: every value is a formula over the catalog and the movements.
    wv = wb.create_sheet("Inventario")
    title(wv, "INVENTARIO ACTUAL DE REPUESTOS - BOOKVERSE (RF-09, SEMANA 10)", len(INVENTARIO_HEAD))
    wv["A2"] = "Calculado con fórmulas a partir de Catálogo de Piezas y Movimientos; no escribir valores en esta hoja. " + \
        "Los ejemplos de piezas y movimientos son ilustrativos."
    header(wv, 3, INVENTARIO_HEAD)
    cat = "'Catálogo de Piezas'"
    mv = lambda col: f"Movimientos!${col}${MOV_FIRST}:${col}${MOV_LAST}"
    inv_last = 3 + INV_ROWS
    for i in range(INV_ROWS):
        r, cr = 4 + i, CAT_FIRST + i
        vals = [
            f'=IF({cat}!A{cr}="","",{cat}!A{cr})',
            f'=IF($A{r}="","",{cat}!B{cr})',
            f'=IF($A{r}="","",{cat}!C{cr})',
            f'=IF($A{r}="","",{cat}!D{cr})',
            f'=IF($A{r}="","",SUMIFS({mv("E")},{mv("C")},$A{r},{mv("D")},"Ingreso"))',
            f'=IF($A{r}="","",SUMIFS({mv("E")},{mv("C")},$A{r},{mv("D")},"Salida"))',
            f'=IF($A{r}="","",E{r}-F{r})',
            f'=IF($A{r}="","",{cat}!F{cr})',
            f'=IF($A{r}="","",IF(G{r}<0,"ERROR: salida mayor al stock",IF(D{r}<>"En buen estado","No disponible",IF(G{r}<=H{r},"Reponer","OK"))))',
        ]
        for c, v in enumerate(vals, start=1):
            cell = wv.cell(row=r, column=c, value=v)
            cell.font, cell.border = font_body, borde
            cell.alignment = Alignment(vertical="top", wrap_text=True,
                                       horizontal="center" if c >= 5 else "left")
            if i < len(CATALOGO[1]):
                cell.fill = fill_banner
            elif r % 2 == 0:
                cell.fill = fill_zebra
    rng = f"I4:I{inv_last}"
    wv.conditional_formatting.add(rng, FormulaRule(formula=['I4="OK"'], font=Font(bold=True, color="1E8449"),
                                                  fill=PatternFill(start_color="D5F5E3", end_color="D5F5E3", fill_type="solid")))
    wv.conditional_formatting.add(rng, FormulaRule(formula=['I4="Reponer"'], font=Font(bold=True, color="9C5700"),
                                                  fill=PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")))
    wv.conditional_formatting.add(rng, FormulaRule(formula=['I4="No disponible"'], font=Font(bold=True, color="5D6D7E"),
                                                  fill=PatternFill(start_color="E5E8E8", end_color="E5E8E8", fill_type="solid")))
    wv.conditional_formatting.add(rng, FormulaRule(formula=['LEFT(I4,5)="ERROR"'], font=Font(bold=True, color="FFFFFF"),
                                                  fill=PatternFill(start_color="C0392B", end_color="C0392B", fill_type="solid")))
    wv.conditional_formatting.add(f"G4:G{inv_last}", CellIsRule(operator="lessThan", formula=["0"],
                                                                font=Font(bold=True, color="C0392B")))
    for i, w in enumerate([11, 20, 30, 20, 11, 11, 13, 14, 32], start=1):
        wv.column_dimensions[get_column_letter(i)].width = w
    wv.row_dimensions[3].height = 32
    wv.freeze_panes = "A4"
    wv.auto_filter.ref = f"A3:I{inv_last}"
    print_setup(wv)

    # Instructions
    wi = wb.create_sheet("Instrucciones")
    wi["A1"] = "INSTRUCCIONES DE LLENADO"
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

    nombre = "Control_Inventario_Repuestos_RF09_Semana10.xlsx"
    wb.save(nombre)
    print(f"[ÉXITO] Archivo '{nombre}' generado correctamente.")


if __name__ == "__main__":
    main()
