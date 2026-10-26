import datetime as dt

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# Shared style (mirrors generar_excel_semana7.py)
font_titulo = Font(name="Segoe UI", size=14, bold=True, color="2C3E50")
font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
font_body = Font(name="Segoe UI", size=10, color="2C3E50")
font_banner = Font(name="Segoe UI", size=10, bold=True, color="7D6608")
fill_header = PatternFill(start_color="34495E", end_color="34495E", fill_type="solid")
fill_zebra = PatternFill(start_color="ECF0F1", end_color="ECF0F1", fill_type="solid")
fill_banner = PatternFill(start_color="FCF3CF", end_color="FCF3CF", fill_type="solid")
borde = Border(*(Side(style="thin", color="BDC3C7"),) * 4)
DATE_FMT = "DD-MM-YYYY"
BLANK_ROWS = 40  # empty formatted rows available after the examples
BANNER = "EJEMPLO - reemplazar con datos reales del laboratorio (las filas de muestra no son mediciones reales)"

d = lambda day, month: dt.date(2026, month, day)

INVENTARIO = (
    ["ID equipo", "Nombre / hostname", "Ubicación", "Usuario responsable", "Sistema operativo",
     "Versión SO", "CPU", "RAM"],
    [
        ["EQ-001", "PC-ADM-01", "Administración", "Bastián Andrade", "Windows 11 Pro", "23H2 (22631.4460)", "Intel Core i5-10400", "8 GB"],
        ["EQ-002", "PC-BIB-01", "Biblioteca", "María Ojeda", "Windows 10 Pro", "22H2 (19045.5011)", "Intel Core i3-9100", "8 GB"],
        ["EQ-003", "PC-LAB-01", "Laboratorio", "Maikol Ulloa", "Ubuntu", "24.04.3 LTS", "AMD Ryzen 5 3400G", "16 GB"],
        ["EQ-004", "NB-GER-01", "Gerencia", "Bastián Andrade", "Windows 11 Pro", "23H2 (22631.4460)", "Intel Core i7-1165G7", "16 GB"],
    ],
    [10, 20, 18, 22, 20, 20, 24, 10],
)

TIPOS = ["SO", "Ofimática", "Navegador", "Antivirus", "Utilitario"]
METODOS = ["Manual", "winget", "WSUS", "Windows Update", "apt", "Agente GLPI", "Otro"]
ESTADOS = ["Actualizado", "Pendiente", "Con error", "Obsoleto"]
SINO = ["Sí", "No"]

REGISTRO = (
    ["ID registro", "ID equipo", "Software", "Tipo", "Versión instalada", "Fecha última actualización",
     "Método", "Cambios relevantes", "Responsable", "Estado"],
    [
        ["REG-001", "EQ-001", "Windows 11 Pro", "SO", "23H2 (22631.4460)", d(8, 10), "Windows Update", "Actualización acumulativa mensual de seguridad", "Bastián Andrade", "Actualizado"],
        ["REG-002", "EQ-001", "Google Chrome", "Navegador", "141.0.7390.55", d(12, 10), "winget", "Parches de seguridad y correcciones de estabilidad", "Bastián Andrade", "Actualizado"],
        ["REG-003", "EQ-002", "LibreOffice", "Ofimática", "24.8.4", d(9, 10), "winget", "Correcciones de errores en Writer y Calc", "María Ojeda", "Actualizado"],
        ["REG-004", "EQ-003", "Ubuntu", "SO", "24.04.3 LTS", d(10, 10), "apt", "Actualización de paquetes del sistema y kernel", "Maikol Ulloa", "Actualizado"],
        ["REG-005", "EQ-004", "Microsoft 365 Apps", "Ofimática", "2508 (19127.20266)", d(14, 10), "Otro", "Actualización de canal mensual", "María Ojeda", "Pendiente"],
    ],
    [12, 11, 22, 14, 22, 18, 17, 44, 20, 14],
)

HISTORIAL = (
    ["ID historial", "Fecha", "ID equipo", "Software", "Versión anterior", "Versión nueva",
     "Motivo / cambio", "Responsable", "Verificado"],
    [
        ["HIS-001", d(8, 10), "EQ-001", "Windows 11 Pro", "23H2 (22631.4317)", "23H2 (22631.4460)", "Actualización acumulativa de seguridad", "Bastián Andrade", "Sí"],
        ["HIS-002", d(9, 10), "EQ-002", "LibreOffice", "24.8.2", "24.8.4", "Corrección de errores", "María Ojeda", "Sí"],
        ["HIS-003", d(10, 10), "EQ-003", "Ubuntu", "24.04.2 LTS", "24.04.3 LTS", "Actualización de paquetes del sistema", "Maikol Ulloa", "Sí"],
        ["HIS-004", d(12, 10), "EQ-001", "Google Chrome", "140.0.7339.208", "141.0.7390.55", "Parche de seguridad", "Bastián Andrade", "Sí"],
        ["HIS-005", d(14, 10), "EQ-004", "Microsoft 365 Apps", "2507 (19029.20208)", "2508 (19127.20266)", "Actualización de canal mensual", "María Ojeda", "No"],
    ],
    [13, 14, 11, 22, 22, 22, 40, 20, 12],
)

# Scores 1-5 (5 = best). Costo: 5 = lowest cost.
COMPARATIVA_HEAD = ["Alternativa", "Facilidad de uso", "Compatibilidad con los equipos",
                    "Efectividad en seguimiento de versiones", "Costo (5 = más económico)", "Total (máx. 20)", "Justificación"]
COMPARATIVA = [
    ["A. Registro manual en planilla (Excel)", 4, 5, 2, 5, "Sin instalación y válido para cualquier SO, pero depende de la digitación y puede quedar desactualizado."],
    ["B. Windows Package Manager (winget) + script de exportación", 3, 3, 4, 5, "Gratuito; `winget list` y `winget upgrade` entregan versiones, pero solo en Windows 10/11 y requiere scripting."],
    ["C. WSUS / Microsoft Intune", 2, 3, 4, 2, "Gestión centralizada en entornos Windows; exige servidor o licenciamiento y mayor administración para una oficina pequeña."],
    ["D. GLPI + agente (inventario open source)", 3, 5, 5, 4, "Inventario automático de SO y software en Windows y Linux, con historial; requiere instalar y mantener el servidor."],
    ["E. Chocolatey / PDQ Deploy", 3, 3, 4, 3, "Despliegue y actualización de paquetes en Windows; algunas funciones avanzadas son de pago."],
    ["F. Linux: apt + unattended-upgrades", 3, 2, 3, 5, "Actualización automática en Debian/Ubuntu; no cubre los equipos Windows y el registro requiere `dpkg -l`."],
]

INSTRUCCIONES = [
    ("Propósito", "Este libro registra la versión instalada y la fecha de actualización del software por equipo (RF-07) y mantiene un historial exacto de cada cambio."),
    ("Filas de ejemplo", "Las filas con fondo amarillo y la leyenda EJEMPLO son datos de muestra. Reemplácelas con los datos reales del laboratorio antes de entregar."),
    ("Formato de fecha", "Use DD-MM-AAAA (por ejemplo, 08-10-2026). No escriba la fecha como texto libre."),
    ("Nombre de versión", "Copie la versión tal como la informa el programa o el sistema (por ejemplo, 23H2 (22631.4460), 24.8.4, 141.0.7390.55). No abrevie ni agregue la palabra 'versión'."),
    ("ID de equipo", "Use el formato EQ-NNN (EQ-001, EQ-002...). El ID debe existir previamente en la hoja Inventario Equipos."),
    ("ID de registro e historial", "Use REG-NNN en Registro Software y HIS-NNN en Historial Actualizaciones. No reutilice ni renumere identificadores."),
    ("Una fila por actualización", "Cada actualización genera una fila nueva en Historial Actualizaciones, con versión anterior y versión nueva."),
    ("Nunca sobrescribir el historial", "El historial es de solo adición (append-only): no se editan ni se eliminan filas. Un error se corrige con una fila nueva que lo aclare en 'Motivo / cambio'."),
    ("Registro Software", "Muestra el estado vigente por equipo y programa. Se actualiza solo después de registrar la fila correspondiente en el historial."),
    ("Verificado", "Marque 'Sí' únicamente cuando otra persona o un comando (winver, winget list, dpkg -l) confirmó la versión nueva."),
    ("Listas desplegables", "Tipo, Método, Estado y Verificado usan listas desplegables; elija un valor de la lista."),
    ("Respaldo", "Guarde una copia fechada del archivo después de cada sesión de registro."),
]


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


def data_sheet(wb, name, ttl, spec, date_cols=(), dropdowns=None):
    heads, rows, widths = spec
    ws = wb.create_sheet(name)
    n = len(heads)
    title(ws, ttl, n)
    header(ws, 3, heads)
    last = 3 + len(rows) + BLANK_ROWS
    for r in range(4, last + 1):
        ex = r - 4 < len(rows)
        for c in range(1, n + 1):
            cell = ws.cell(row=r, column=c, value=rows[r - 4][c - 1] if ex else None)
            cell.font, cell.border = font_body, borde
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if ex:
                cell.fill = fill_banner
            elif r % 2 == 0:
                cell.fill = fill_zebra
            if c in date_cols:
                cell.number_format = DATE_FMT
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A4"
    ws.auto_filter.ref = f"A3:{get_column_letter(n)}{last}"
    for col, opts in (dropdowns or {}).items():
        dv = DataValidation(type="list", formula1='"' + ",".join(opts) + '"', allow_blank=True)
        dv.error, dv.errorTitle = "Seleccione un valor de la lista.", "Valor no válido"
        ws.add_data_validation(dv)
        dv.add(f"{col}4:{col}{last}")
    for col in (get_column_letter(c) for c in date_cols):
        dv = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True)
        dv.error, dv.errorTitle = "Ingrese una fecha válida (DD-MM-AAAA).", "Fecha no válida"
        ws.add_data_validation(dv)
        dv.add(f"{col}4:{col}{last}")
    return ws


def main():
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    data_sheet(wb, "Inventario Equipos", "INVENTARIO DE EQUIPOS - BOOKVERSE (RF-07, SEMANA 8)", INVENTARIO)
    data_sheet(wb, "Registro Software", "REGISTRO DE SOFTWARE INSTALADO - BOOKVERSE (RF-07, SEMANA 8)", REGISTRO,
               date_cols=(6,), dropdowns={"D": TIPOS, "G": METODOS, "J": ESTADOS})
    ws_h = data_sheet(wb, "Historial Actualizaciones", "HISTORIAL DE ACTUALIZACIONES (SOLO ADICIÓN) - BOOKVERSE (RF-07, SEMANA 8)",
                      HISTORIAL, date_cols=(2,), dropdowns={"I": SINO})

    # Comparison matrix with live totals
    ws = wb.create_sheet("Comparativa Alternativas")
    title(ws, "COMPARATIVA DE ALTERNATIVAS (puntaje 1 a 5; 5 = mejor)", len(COMPARATIVA_HEAD), with_banner=False)
    ws["A2"] = "Puntajes asignados por el grupo según análisis documental; coinciden con el informe Word. Ajustar si el grupo cambia sus criterios."
    ws["A2"].font = font_body
    header(ws, 3, COMPARATIVA_HEAD)
    for i, row in enumerate(COMPARATIVA):
        r = 4 + i
        vals = row[:5] + [f"=SUM(B{r}:E{r})", row[5]]
        for c, v in enumerate(vals, start=1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.font, cell.border = font_body, borde
            cell.alignment = Alignment(vertical="top", wrap_text=True,
                                       horizontal="center" if 2 <= c <= 6 else "left")
            if r % 2 == 0:
                cell.fill = fill_zebra
    last = 3 + len(COMPARATIVA)
    ws.cell(row=last + 2, column=1, value="Alternativa recomendada").font = Font(name="Segoe UI", size=10, bold=True, color="2C3E50")
    ws.cell(row=last + 2, column=2, value="D. GLPI + agente (mayor puntaje total), con la planilla de este libro como formato de respaldo y winget como apoyo.").font = font_body
    for i, w in enumerate([46, 14, 18, 20, 18, 14, 70], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[3].height = 48
    ws.freeze_panes = "A4"
    ws.auto_filter.ref = f"A3:G{last}"

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

    nombre = "Registro_Software_RF07_Semana8.xlsx"
    wb.save(nombre)
    print(f"[ÉXITO] Archivo '{nombre}' generado correctamente.")


if __name__ == "__main__":
    main()
