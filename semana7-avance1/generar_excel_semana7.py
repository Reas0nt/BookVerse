"""Generate the Stage 2 planning workbook: Gantt chart, risk matrix and checklist."""

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUTPUT = "Planificacion_Y_Chequeo_BookVerse.xlsx"

# ---------- Styles ----------

FONT_NAME = "Segoe UI"
font_titulo = Font(name=FONT_NAME, size=14, bold=True, color="2C3E50")
font_subtitulo = Font(name=FONT_NAME, size=10, italic=True, color="7F8C8D")
font_header = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")
font_body = Font(name=FONT_NAME, size=10, color="2C3E50")
font_body_bold = Font(name=FONT_NAME, size=10, bold=True, color="2C3E50")
font_barra = Font(name=FONT_NAME, size=9, bold=True, color="FFFFFF")

borde = Border(**{side: Side(style="thin", color="BDC3C7") for side in ("left", "right", "top", "bottom")})


def fill(color):
    return PatternFill(start_color=color, end_color=color, fill_type="solid")


fill_header = fill("34495E")
fill_zebra = fill("ECF0F1")


def write_header(ws, row, headers, height=32):
    for col, text in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=text)
        cell.font = font_header
        cell.fill = fill_header
        cell.border = borde
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = height


def set_widths(ws, widths):
    for col, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(col)].width = width


def landscape_one_page(ws):
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True


# ---------- Data ----------

# Course weeks 7 to 11 map to project weeks 1 to 5
SEMANAS = [("Semana 1", "S7"), ("Semana 2", "S8"), ("Semana 3", "S9"), ("Semana 4", "S10"), ("Semana 5", "S11")]

COLORES_FASE = {
    "Planificación": "3498DB",
    "Instalación y configuración": "E67E22",
    "Documentación": "16A085",
    "Validación": "8E44AD",
    "Hito": "C0392B",
}

# (phase, task, owner, start week, end week) - weeks are 1-based
TAREAS = [
    ("Planificación", "Revisión del caso BookVerse y requerimientos RF-06 a RF-09", "Bastián Andrade", 1, 1),
    ("Planificación", "Cronograma, hitos, entregables y matriz de riesgos", "María Ojeda", 1, 1),
    ("Instalación y configuración", "Mantenimiento preventivo y correctivo de equipos de oficina (RF-06)", "Maikol Ulloa", 1, 1),
    ("Documentación", "Registro de cada intervención: tipo, fecha, acciones y observaciones (RF-06)", "Bastián Andrade", 1, 1),
    ("Hito", "Avance #1: planificación y registro de mantenimiento", "Equipo", 1, 1),

    ("Planificación", "Análisis y comparación de alternativas de actualización de software (RF-07)", "Bastián Andrade", 2, 2),
    ("Instalación y configuración", "Instalación y configuración de Windows 10 IoT LTSC en máquina virtual", "María Ojeda", 2, 2),
    ("Documentación", "Registro de versiones, fechas e historial de actualizaciones (RF-07)", "Maikol Ulloa", 2, 2),
    ("Hito", "Avance #2: registro de software y video de instalación", "Equipo", 2, 2),

    ("Planificación", "Definición de criterios de búsqueda del historial: fecha, tipo, equipo, N° de serie (RF-08)", "Maikol Ulloa", 3, 3),
    ("Documentación", "Historial de mantenimiento completo y acceso a cada entrada (RF-08)", "María Ojeda", 3, 3),
    ("Hito", "Avance #3: historial de mantenimiento consultable", "Equipo", 3, 3),

    ("Documentación", "Documento de control de inventario de piezas de repuesto (RF-09)", "Bastián Andrade", 4, 4),
    ("Documentación", "Registro de ingresos, salidas y estado de cada pieza (RF-09)", "Maikol Ulloa", 4, 4),
    ("Hito", "Avance #4: control de inventario de repuestos", "Equipo", 4, 4),

    ("Validación", "Pruebas integrales de equipos intervenidos y corrección de errores detectados", "María Ojeda", 3, 5),
    ("Documentación", "Presentación PPT: síntesis de documentos, video, conclusiones y mejoras", "Equipo", 5, 5),
    ("Hito", "Evaluación práctica Etapa II (entrega y presentación)", "Equipo", 5, 5),
]

# Probability and impact levels used to score each risk
NIVELES = {"Baja": 1, "Media": 2, "Alta": 3, "Bajo": 1, "Medio": 2, "Alto": 3}

# (risk, affected phase, probability, impact, response type, response strategy, owner)
RIESGOS = [
    ("El hipervisor KVM del sistema anfitrión ocupa VT-x e impide iniciar la máquina virtual en VirtualBox",
     "Instalación y configuración", "Alta", "Alto", "Mitigar",
     "Descargar los módulos KVM y configurar kvm.enable_virt_at_load=0; probar el arranque de la VM antes de grabar el video.",
     "María Ojeda"),
    ("Espacio insuficiente en el disco del anfitrión para la máquina virtual",
     "Instalación y configuración", "Alta", "Alto", "Evitar",
     "Verificar al menos 40 GB libres antes de crear la VM; usar disco virtual dinámico y liberar espacio.",
     "María Ojeda"),
    ("Imagen ISO corrupta o incompatible con la versión de VirtualBox",
     "Instalación y configuración", "Baja", "Alto", "Mitigar",
     "Descargar desde la fuente oficial, verificar el hash SHA256 y mantener una copia de respaldo de la ISO.",
     "Bastián Andrade"),
    ("Corte de energía o falla durante una actualización que deja el sistema inestable",
     "Instalación y configuración", "Media", "Alto", "Mitigar",
     "Crear una instantánea (snapshot) de la VM antes de cada actualización y restaurarla si falla.",
     "Maikol Ulloa"),
    ("Recursos insuficientes (RAM/CPU) que vuelven lenta la VM durante la instalación",
     "Instalación y configuración", "Media", "Medio", "Mitigar",
     "Asignar 4 GB de RAM y 2 CPU; cerrar aplicaciones del anfitrión durante la instalación.",
     "María Ojeda"),
    ("Herramienta de actualización no disponible en el SO (winget no viene incluido en LTSC)",
     "Instalación y configuración", "Alta", "Bajo", "Aceptar",
     "Registrar versiones con Windows Update y de forma manual; instalar winget desde el repositorio oficial si se requiere.",
     "Bastián Andrade"),
    ("Pérdida o daño de los archivos de registro (Excel, informes)",
     "Documentación", "Media", "Alto", "Mitigar",
     "Copia de respaldo fechada después de cada sesión en una ubicación distinta; los scripts permiten regenerar los archivos.",
     "Maikol Ulloa"),
    ("Datos de inventario o historial incompletos o inconsistentes",
     "Documentación", "Alta", "Medio", "Mitigar",
     "Usar la plantilla con campos obligatorios y listas desplegables; una segunda persona verifica cada registro.",
     "Bastián Andrade"),
    ("Errores no detectados en el software después de la intervención",
     "Validación", "Media", "Alto", "Mitigar",
     "Aplicar una lista de pruebas por equipo (arranque, red, actualizaciones, aplicaciones) y registrar el resultado.",
     "María Ojeda"),
    ("Ausencia de un integrante en una semana con entrega",
     "Planificación", "Media", "Medio", "Mitigar",
     "Tareas documentadas en la Gantt con responsable suplente; avances compartidos en la carpeta del grupo.",
     "Equipo"),
    ("Retraso en los entregables semanales",
     "Planificación", "Media", "Alto", "Mitigar",
     "Un hito por semana revisado con el docente; dejar el último día de cada semana como holgura.",
     "Equipo"),
]

CHEQUEO = [
    ["[ ]", "Planificación", "Verificar requisitos de hardware y software en equipos de oficina.", "Inventario de equipos validado."],
    ["[ ]", "Planificación", "Definir plan de mantenimiento preventivo y correctivo (RF-06).", "Documento de alcance aprobado."],
    ["[ ]", "Planificación", "Descargar imagen ISO oficial de Windows y instaladores base.", "Instaladores íntegros y verificados."],
    ["[ ]", "Instalación", "Preparar medio de instalación (USB booteable / Máquina Virtual).", "Medio listo para arranque."],
    ["[ ]", "Instalación", "Configurar opciones de arranque, particionado y ejecución del asistente.", "SO instalado sin errores críticos."],
    ["[ ]", "Configuración", "Configurar ajustes de red, controladores (drivers) y seguridad.", "Conectividad y seguridad activas."],
    ["[ ]", "Configuración", "Instalar y actualizar software de oficina y herramientas (RF-07).", "Aplicaciones operativas."],
    ["[ ]", "Validación", "Ejecutar pruebas de rendimiento y funcionalidad post-intervención.", "Equipos estables y funcionales."],
    ["[ ]", "Validación", "Verificar que el software opera correctamente sin fallas (RF-09).", "Validación técnica superada."],
    ["[ ]", "Validación", "Registrar formalmente el historial de mantenimiento en el sistema (RF-08).", "Historial guardado en BD."],
    ["[ ]", "Validación", "Generar reporte final y entregar evidencia en video al Aula Virtual.", "Entregable subido con éxito."],
]


# ---------- Sheets ----------

def hoja_gantt(ws):
    ws.title = "Carta Gantt"
    ws["A1"] = "CRONOGRAMA DE ACTIVIDADES - BOOKVERSE (ETAPA 2)"
    ws["A1"].font = font_titulo
    ws["A2"] = "Duración: 5 semanas (semanas 7 a 11 del curso)  |  Un hito de entrega por semana  |  Evaluación final: Semana 5 (S11)"
    ws["A2"].font = font_subtitulo

    fila_header = 4
    col_semana = 6
    write_header(ws, fila_header, ["N°", "Fase", "Tarea", "Responsable", "Duración"]
                 + [f"{nombre}\n({curso})" for nombre, curso in SEMANAS])

    for n, (fase, tarea, responsable, inicio, fin) in enumerate(TAREAS, start=1):
        fila = fila_header + n
        es_hito = fase == "Hito"
        duracion = "Hito" if es_hito else f"{fin - inicio + 1} sem"
        for col, valor in enumerate([n, fase, tarea, responsable, duracion], start=1):
            cell = ws.cell(row=fila, column=col, value=valor)
            cell.font = font_body_bold if es_hito else font_body
            cell.border = borde
            cell.alignment = Alignment(vertical="center", wrap_text=col in (2, 3),
                                       horizontal="center" if col in (1, 5) else "left")

        for semana in range(1, len(SEMANAS) + 1):
            cell = ws.cell(row=fila, column=col_semana + semana - 1)
            cell.border = borde
            if inicio <= semana <= fin:
                cell.fill = fill(COLORES_FASE[fase])
                if es_hito:
                    cell.value = "◆ Entrega"
                    cell.font = font_barra
                    cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[fila].height = 30

    fila_leyenda = fila_header + len(TAREAS) + 2
    ws.cell(row=fila_leyenda, column=2, value="Leyenda").font = font_body_bold
    for i, (fase, color) in enumerate(COLORES_FASE.items(), start=1):
        muestra = ws.cell(row=fila_leyenda + i, column=1)
        muestra.fill = fill(color)
        muestra.border = borde
        ws.cell(row=fila_leyenda + i, column=2, value=fase).font = font_body

    set_widths(ws, [6, 18, 52, 18, 10] + [12] * len(SEMANAS))
    ws.freeze_panes = ws.cell(row=fila_header + 1, column=col_semana)
    landscape_one_page(ws)


def nivel_riesgo(probabilidad, impacto):
    """Return (label, color) from probability x impact score (1 to 9)."""
    puntaje = NIVELES[probabilidad] * NIVELES[impacto]
    if puntaje >= 6:
        return "Alto", "E74C3C"
    if puntaje >= 3:
        return "Medio", "F39C12"
    return "Bajo", "27AE60"


def hoja_riesgos(ws):
    ws["A1"] = "MATRIZ DE RIESGOS - BOOKVERSE (ETAPA 2)"
    ws["A1"].font = font_titulo
    ws["A2"] = "Nivel = Probabilidad x Impacto (Baja/Bajo = 1, Media/Medio = 2, Alta/Alto = 3). Alto: 6 a 9, Medio: 3 a 4, Bajo: 1 a 2."
    ws["A2"].font = font_subtitulo

    fila_header = 4
    write_header(ws, fila_header, ["ID", "Riesgo", "Fase afectada", "Probabilidad", "Impacto",
                                   "Nivel", "Tipo de respuesta", "Estrategia de respuesta", "Responsable"])

    for n, (riesgo, fase, prob, impacto, tipo, estrategia, responsable) in enumerate(RIESGOS, start=1):
        fila = fila_header + n
        nivel, color = nivel_riesgo(prob, impacto)
        valores = [f"R{n:02d}", riesgo, fase, prob, impacto, nivel, tipo, estrategia, responsable]
        for col, valor in enumerate(valores, start=1):
            cell = ws.cell(row=fila, column=col, value=valor)
            cell.font = font_body
            cell.border = borde
            cell.alignment = Alignment(vertical="center", wrap_text=True,
                                       horizontal="center" if col in (1, 4, 5, 6, 7) else "left")
            if n % 2 == 0:
                cell.fill = fill_zebra
        nivel_cell = ws.cell(row=fila, column=6)
        nivel_cell.fill = fill(color)
        nivel_cell.font = font_barra
        ws.row_dimensions[fila].height = 45

    set_widths(ws, [6, 42, 18, 12, 10, 9, 12, 52, 16])
    ws.freeze_panes = ws.cell(row=fila_header + 1, column=3)
    landscape_one_page(ws)


def hoja_chequeo(ws):
    ws["A1"] = "LISTA DE CHEQUEO - PROCESO TÉCNICO BOOKVERSE"
    ws["A1"].font = font_titulo

    fila_header = 3
    write_header(ws, fila_header, ["Estado", "Fase del Proceso", "Descripción de la Actividad / Verificación", "Criterio de Éxito"], height=20)

    for n, datos in enumerate(CHEQUEO, start=1):
        fila = fila_header + n
        for col, valor in enumerate(datos, start=1):
            cell = ws.cell(row=fila, column=col, value=valor)
            cell.font = font_body
            cell.border = borde
            if col == 1:
                cell.alignment = Alignment(horizontal="center")
            if fila % 2 == 0:
                cell.fill = fill_zebra

    set_widths(ws, [10, 18, 72, 38])
    landscape_one_page(ws)


def main():
    wb = openpyxl.Workbook()
    hoja_gantt(wb.active)
    hoja_riesgos(wb.create_sheet("Matriz de Riesgos"))
    hoja_chequeo(wb.create_sheet("Lista de Chequeo"))
    wb.save(OUTPUT)
    print(f"[ÉXITO] Archivo '{OUTPUT}' generado correctamente.")


if __name__ == "__main__":
    main()
