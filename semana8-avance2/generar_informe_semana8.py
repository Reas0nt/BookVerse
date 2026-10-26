"""Generate the RF-07 progress report (Avance #2, week 8) as a Word document."""

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Twips

OUTPUT = "Informe_Avance2_RF07_Semana8.docx"
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
    return tbl


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

add_page_number_footer("BookVerse - RF-07 - Avance #2 - Página ")

# ---------- Cover ----------

centered("Integración de Competencias 2", 16, bold=True, color=COLOR_TITLE, before=90, after=10)
centered("Actividad 2.3: Avance #2 (semana 8)", 14, color=COLOR_TITLE, after=30)
centered("Informe de avance RF-07", 22, bold=True, color=COLOR_HEADER, after=10)
centered("Actualización y registro de software en equipos de oficina - Proyecto BookVerse", 13, after=60)
table([3000, 6026], ["Dato", "Detalle"], [
    ["Integrantes", ", ".join(MEMBERS)],
    ["Docente", "Manuel Merino"],
    ["Fecha", "Semana 8, octubre 2026"],
    ["Requerimiento", "RF-07: actualización y registro de software"],
    ["Archivo complementario", "Registro_Software_RF07_Semana8.xlsx"],
])
page_break()

# ---------- 1. Introduction ----------

h1("1. Introducción y objetivo")
p("El proyecto BookVerse requiere que los equipos de oficina cuenten con software actualizado y que la institución sepa, en todo momento, qué versión tiene instalada cada computador y cuándo fue actualizada por última vez. Esta necesidad corresponde al requerimiento RF-07.")
p("Objetivo general: analizar alternativas que faciliten la actualización y el registro de software en los equipos de oficina, y definir un formato de registro que conserve un historial exacto de versiones y fechas de actualización.")
p("Objetivos específicos:")
for t in ["Comparar alternativas de actualización y registro según facilidad de uso, compatibilidad con los equipos, efectividad en el seguimiento de versiones y costo.",
          "Definir un formato uniforme para documentar versión instalada y fecha de última actualización por equipo.",
          "Establecer un procedimiento de mantenimiento del historial que mantenga los datos consistentes, vigentes y accesibles.",
          "Documentar la instalación de un sistema operativo en una máquina virtual como evidencia práctica."]:
    bullet(t)
note("Nota: aún no se cuenta con el inventario real de los computadores del laboratorio. Los datos de las tablas de ejemplo y del archivo Excel son ilustrativos y deben reemplazarse con datos reales.")

# ---------- 2. Alternatives ----------

h1("2. Análisis de alternativas (RF-07)")
p("Se evaluaron seis alternativas. La descripción se basa en las funciones documentadas de cada herramienta; la valoración numérica corresponde a un juicio del grupo y no a una medición.")
for title, body in [
    ("A. Registro manual en planilla (Excel). ", "Una persona responsable digita en una planilla la versión y la fecha de cada actualización. No requiere instalación y funciona con cualquier sistema operativo, pero su exactitud depende de la disciplina de quien registra."),
    ("B. Windows Package Manager (winget) con script de exportación. ", "winget es la herramienta de línea de comandos de Microsoft para instalar y actualizar paquetes en Windows 10 y 11. El comando winget list muestra los programas instalados con su versión y winget upgrade indica cuáles tienen una versión más nueva disponible. Un script puede exportar esa salida a un archivo para alimentar el registro. Solo cubre programas reconocidos por sus repositorios y equipos Windows."),
    ("C. WSUS / Microsoft Intune. ", "WSUS (Windows Server Update Services) permite aprobar y distribuir actualizaciones de Microsoft desde un servidor propio. Intune es el servicio en la nube de Microsoft para administrar dispositivos y aplicaciones, y requiere licenciamiento. Ofrecen control centralizado, pero implican infraestructura o licencias y administración permanente, lo que resulta desproporcionado para una oficina pequeña."),
    ("D. GLPI con agente de inventario. ", "GLPI es una herramienta de gestión de activos y de servicios de TI de código abierto. Con su agente (GLPI Agent) instalado en cada equipo, se obtiene automáticamente un inventario de hardware, sistema operativo y software instalado, para Windows y Linux, centralizado en una base de datos. Requiere instalar y mantener un servidor web con base de datos. OCS Inventory es una alternativa similar."),
    ("E. Chocolatey / PDQ Deploy. ", "Chocolatey es un administrador de paquetes para Windows que permite instalar y actualizar software por línea de comandos; tiene edición gratuita y ediciones comerciales. PDQ Deploy es una herramienta de despliegue de software para Windows con versión gratuita limitada y versiones de pago. Facilitan la actualización, pero no son un registro histórico por sí solos."),
    ("F. Linux: apt con unattended-upgrades. ", "En Debian y Ubuntu, apt gestiona los paquetes y el paquete unattended-upgrades instala actualizaciones automáticamente. Las versiones se consultan con dpkg -l. Es gratuito y confiable en Linux, pero no cubre equipos Windows."),
]:
    rich([(title, True), body])

h2("2.1 Matriz comparativa")
p("Escala de 1 a 5, donde 5 es la mejor valoración. En costo, 5 corresponde a la alternativa más económica.")
alternatives = [
    ["A. Registro manual en planilla (Excel)", 4, 5, 2, 5],
    ["B. winget + script de exportación", 3, 3, 4, 5],
    ["C. WSUS / Microsoft Intune", 2, 3, 4, 2],
    ["D. GLPI + agente", 3, 5, 5, 4],
    ["E. Chocolatey / PDQ Deploy", 3, 3, 4, 3],
    ["F. Linux: apt + unattended-upgrades", 3, 2, 3, 5],
]
table([2626, 1200, 1800, 1700, 850, 850],
      ["Alternativa", "Facilidad de uso", "Compatibilidad", "Seguimiento de versiones", "Costo", "Total"],
      [row + [sum(row[1:])] for row in alternatives],
      center_cols=(1, 2, 3, 4, 5), bold_last=True)
p()
p('Los mismos puntajes figuran en la hoja "Comparativa Alternativas" del archivo Excel, donde el total se calcula con fórmulas.')

h2("2.2 Recomendación")
rich([("Se recomienda la alternativa D (GLPI con agente), ", True),
      "que obtiene el mayor puntaje (17 de 20). Es la única opción evaluada que obtiene versiones de forma automática en equipos Windows y Linux y las conserva en una base de datos consultable, lo que reduce el error humano en el seguimiento de versiones y apoya el historial exigido por RF-07. Su costo es bajo (software abierto), aunque requiere un servidor y tiempo de configuración."])
p("Como solución de respaldo y para el período inicial, se propone usar la planilla Excel entregada (alternativa A, 16 puntos) con el formato definido, y complementar con winget (alternativa B, 15 puntos) para obtener las versiones en los equipos Windows. De esta forma el grupo puede avanzar sin depender de contar con un servidor, y los campos de la planilla coinciden con los que luego se obtendrían desde GLPI.")

# ---------- 3. Software record ----------

h1("3. Registro de información del software")
p("El formato está implementado en el archivo Registro_Software_RF07_Semana8.xlsx, que contiene las hojas Inventario Equipos, Registro Software, Historial Actualizaciones, Comparativa Alternativas e Instrucciones.")

h2("3.1 Campos del registro")
table([2300, 6726], ["Campo", "Descripción"], [
    ["ID registro / ID equipo", "Identificadores únicos (REG-NNN, EQ-NNN) que vinculan el software con el equipo del inventario."],
    ["Software y tipo", "Nombre del programa y su categoría: SO, ofimática, navegador, antivirus o utilitario."],
    ["Versión instalada", "Versión tal como la informa el sistema o el programa, sin abreviar."],
    ["Fecha última actualización", "Formato DD-MM-AAAA."],
    ["Método", "Manual, winget, WSUS, Windows Update, apt, Agente GLPI u otro."],
    ["Cambios relevantes", "Resumen del cambio aplicado (seguridad, corrección de errores, nueva función)."],
    ["Responsable y estado", "Persona que realizó el registro; estado Actualizado, Pendiente, Con error u Obsoleto."],
])
p()

h2("3.2 Ejemplo de registro")
note("EJEMPLO - datos ilustrativos, no corresponden a equipos reales del laboratorio.")
table([1000, 1000, 1800, 1700, 1500, 2026], ["ID equipo", "Hostname", "Software", "Versión", "Fecha", "Método"], [
    ["EQ-001", "PC-ADM-01", "Windows 11 Pro", "23H2 (22631.4460)", "08-10-2026", "Windows Update"],
    ["EQ-001", "PC-ADM-01", "Google Chrome", "141.0.7390.55", "12-10-2026", "winget"],
    ["EQ-002", "PC-BIB-01", "LibreOffice", "24.8.4", "09-10-2026", "winget"],
    ["EQ-003", "PC-LAB-01", "Ubuntu", "24.04.3 LTS", "10-10-2026", "apt"],
], row_fill=COLOR_NOTE)
p()

h2("3.3 Cómo obtener las versiones")
rich([("Windows:", True)])
for cmd, desc in [("winver", "muestra la edición y versión de Windows en una ventana."),
                  ("systeminfo", "entrega nombre y versión del SO, fecha de instalación, hardware y revisiones."),
                  ("winget list", "lista los programas instalados con su versión."),
                  ("Get-ComputerInfo", "en PowerShell, devuelve información detallada del sistema y su versión.")]:
    bullet([(cmd, "code"), (": " + desc, None)])
rich([("Linux:", True)])
for cmd, desc in [("lsb_release -a", "muestra la distribución y la versión."),
                  ("uname -r", "indica la versión del kernel."),
                  ("dpkg -l", "lista los paquetes instalados con su versión.")]:
    bullet([(cmd, "code"), (": " + desc, None)])

# ---------- 4. History ----------

h1("4. Mantenimiento del historial")
p("El historial garantiza que cada actualización quede registrada y que los datos sean consistentes, vigentes y accesibles.")
h2("4.1 Procedimiento")
numbered(["Antes de actualizar, anotar la versión actual con el comando correspondiente (versión anterior).",
          "Aplicar la actualización y volver a consultar la versión (versión nueva).",
          "Agregar una fila nueva en la hoja Historial Actualizaciones con fecha, equipo, software, versión anterior, versión nueva, motivo y responsable.",
          "Actualizar la fila vigente del equipo en la hoja Registro Software (versión, fecha, método, cambios y estado).",
          "Una segunda persona verifica el cambio y marca Verificado como Sí.",
          "Guardar una copia de respaldo fechada del archivo."])
h2("4.2 Reglas y controles de consistencia")
for t in ["Regla de solo adición (append-only): las filas del historial no se editan ni se eliminan. Un error se corrige con una fila nueva que lo explique.",
          "La versión nueva de la última fila del historial debe coincidir con la versión instalada en Registro Software.",
          "Cada ID de equipo debe existir en el inventario.",
          "Las fechas usan el formato DD-MM-AAAA y no pueden ser posteriores a la fecha de registro.",
          "Quien registra es el responsable asignado al equipo; otra persona del grupo verifica.",
          "Respaldo: una copia fechada después de cada sesión, almacenada en una ubicación distinta al archivo de trabajo (por ejemplo, la unidad compartida del grupo). Si se adopta GLPI, se respalda su base de datos."]:
    bullet(t)

# ---------- 5. Virtual machine ----------

h1("5. Instalación de un sistema operativo en una máquina virtual")
p("Se utilizó Oracle VirtualBox con Windows 10 IoT Enterprise LTSC 2021 (versión 21H2, compilación 19044), a partir de la imagen en-us_windows_10_iot_enterprise_ltsc_2021_x64_dvd_257ad90f.iso. Esta guía sirve también como guion para el video de máximo 5 minutos.")
p("Se eligió una edición LTSC (Long-Term Servicing Channel) porque recibe solo actualizaciones de seguridad y calidad, sin actualizaciones de funciones, y cuenta con un ciclo de soporte extendido. Esto la hace adecuada para equipos de oficina que deben mantenerse estables, como los de BookVerse.")

h2("5.1 Requisitos")
for t in ["Equipo anfitrión con virtualización (Intel VT-x o AMD-V) habilitada en la BIOS/UEFI, al menos 8 GB de RAM y 40 GB de disco libre.",
          "Oracle VirtualBox instalado, descargado desde el sitio oficial (virtualbox.org).",
          "Imagen ISO en-us_windows_10_iot_enterprise_ltsc_2021_x64_dvd_257ad90f.iso (Windows 10 IoT Enterprise LTSC 2021, 64 bits, instalador en inglés)."]:
    bullet(t)

h2("5.2 Pasos")
numbered(["Abrir VirtualBox y presionar Nueva. Asignar nombre (por ejemplo, WIN10-BOOKVERSE), seleccionar la ISO, tipo Microsoft Windows y versión Windows 10 (64-bit). Marcar Omitir instalación desatendida para realizar la instalación paso a paso.",
          "Asignar recursos: 4 GB de RAM (mínimo 2 GB) y 2 procesadores.",
          "Crear un disco virtual de 50 GB, de tamaño dinámico (Windows 10 de 64 bits requiere al menos 32 GB).",
          "Iniciar la máquina virtual. En la primera pantalla, mantener el idioma English, y seleccionar formato de hora y moneda Spanish (Chile) y teclado Latin American. Presionar Next e Install now.",
          "Si se solicita clave de producto, elegir I don't have a product key; la activación se realiza después con la licencia correspondiente. Aceptar los términos de licencia.",
          "Elegir Custom: Install Windows only (advanced), seleccionar el espacio no asignado del disco virtual y presionar Next.",
          "Esperar la copia de archivos y los reinicios automáticos. Al terminar, retirar la ISO desde Dispositivos > Unidades ópticas si vuelve a iniciar el instalador.",
          "En la configuración inicial, seleccionar región y teclado, elegir Domain join instead para crear una cuenta local, definir usuario, contraseña y preguntas de seguridad, y revisar las opciones de privacidad."])
note("[Insertar capturas de pantalla]: configuración de la VM, asistente de instalación y escritorio de Windows.")

h2("5.3 Configuración posterior")
for label, body in [("Actualizar el sistema: ", "Settings > Update & Security > Windows Update > Check for updates. Instalar las actualizaciones y reiniciar."),
                    ("Asignar el nombre del equipo: ", 'en PowerShell como administrador, Rename-Computer -NewName "WIN10-BOOKVERSE" -Restart; verificar con hostname.'),
                    ("Verificar usuario y red: ", "whoami; ipconfig; ping -n 3 8.8.8.8 (adaptador en modo NAT o Adaptador puente)."),
                    ("Instalar Guest Additions: ", "Dispositivos > Insertar imagen de CD de los Guest Additions, ejecutar VBoxWindowsAdditions.exe desde la unidad de CD y reiniciar.")]:
    bullet([(label, "bold"), (body, None)])
note("Nota: las ediciones LTSC no incluyen Microsoft Store ni winget de forma predeterminada. Para usar winget en este equipo debe instalarse manualmente desde el repositorio oficial de Microsoft (github.com/microsoft/winget-cli); mientras tanto, el registro se realiza con Windows Update y de forma manual.")

h2("5.4 Registro de la versión instalada")
p("Obtener los datos con los comandos siguientes y registrarlos en las hojas Inventario Equipos, Registro Software y Historial Actualizaciones del Excel:")
for cmd in ["winver",
            'systeminfo | findstr /B /C:"OS Name" /C:"OS Version"',
            "Get-ComputerInfo -Property OsName, OsVersion, OsBuildNumber"]:
    code(cmd)
p()
note("[Insertar capturas de pantalla]: salida de los comandos y filas agregadas al registro.")

h2("5.5 Pruebas posteriores a la instalación")
p("Después de instalar y configurar el sistema se ejecutan las siguientes pruebas para asegurar que el equipo funciona correctamente. La columna Resultado se completa durante la prueba.")
table([2000, 3000, 2626, 1400], ["Prueba", "Acción o comando", "Resultado esperado", "Resultado"], [
    ["Arranque del sistema", "Reiniciar la máquina virtual", "Windows inicia sin errores hasta el escritorio", "[OK/Falla]"],
    ["Versión instalada", "winver", "Windows 10 IoT Enterprise LTSC, versión 21H2", "[OK/Falla]"],
    ["Nombre del equipo", "hostname", "WIN10-BOOKVERSE", "[OK/Falla]"],
    ["Cuenta de usuario", "whoami", "Usuario local creado en la instalación", "[OK/Falla]"],
    ["Conectividad de red", "ipconfig; ping -n 3 8.8.8.8", "Dirección IP asignada y 0% de paquetes perdidos", "[OK/Falla]"],
    ["Actualizaciones", "Windows Update > Check for updates", "Sin actualizaciones pendientes", "[OK/Falla]"],
    ["Guest Additions", "Cambiar el tamaño de la ventana de la VM", "La resolución se ajusta automáticamente", "[OK/Falla]"],
], center_cols=(3,))
p()

h2("5.6 Errores detectados y corrección")
p("Durante la preparación del entorno se registraron los errores encontrados, su causa y la solución aplicada.")
table([2100, 2500, 3026, 1400], ["Error", "Causa", "Solución aplicada", "Estado"], [
    ["La máquina virtual no inicia: \"VirtualBox can't operate in VMX root mode\" (VERR_VMX_IN_VMX_ROOT_MODE)",
     "En el equipo anfitrión (Linux, kernel 6.14) el módulo KVM toma la virtualización por hardware (VT-x) al cargarse, y VirtualBox 7.0 no puede usarla.",
     "Se descargaron los módulos KVM (sudo modprobe -r kvm_intel kvm) y se configuró options kvm enable_virt_at_load=0 en /etc/modprobe.d para que el cambio sea permanente. Luego la VM inició correctamente.",
     "Resuelto"],
])
p()

h2("5.7 Guion sugerido para el video (máximo 5 minutos)")
table([1500, 5526, 2000], ["Tiempo", "Contenido", "Responsable"], [
    ["0:00 - 0:30", "Presentación del grupo y objetivo de RF-07", "[Integrante]"],
    ["0:30 - 1:30", "Creación de la máquina virtual en VirtualBox", "[Integrante]"],
    ["1:30 - 3:00", "Instalación de Windows 10 IoT Enterprise LTSC 2021 (puede acelerarse en edición)", "[Integrante]"],
    ["3:00 - 4:00", "Windows Update, nombre del equipo, usuario, red y Guest Additions", "[Integrante]"],
    ["4:00 - 5:00", "Registro de la versión en el Excel y cierre", "[Integrante]"],
])
p()
p("Enlace al video: https://youtu.be/8b-JuKKoMV4", bold=True)

# ---------- 6. Teacher review ----------

page_break()
h1("6. Revisión conjunta con docente")
p("Lista de verificación para completar durante la revisión.")
checklist = ["Análisis de alternativas con matriz comparativa", "Recomendación justificada",
             "Formato de registro de software (Excel)", "Datos reales del laboratorio reemplazan los ejemplos",
             "Historial de actualizaciones con versión anterior y nueva",
             "Instalación del SO en máquina virtual (evidencia)", "Pruebas posteriores y errores corregidos documentados",
             "Video de máximo 5 minutos con enlace",
             "Preguntas de cierre respondidas"]
table([4200, 1400, 3426], ["Ítem", "Completo (Sí/No)", "Observaciones"], [[item, "", ""] for item in checklist])
p()

# ---------- 7. Closing questions ----------

h1("7. Preguntas de cierre")
note("Borrador para que el grupo lo ajuste con sus propias palabras y experiencias.")
rich([("¿Qué aprendimos?", True)])
p("Aprendimos que mantener el software actualizado no basta: también es necesario registrar qué versión tiene cada equipo y cuándo cambió, porque sin ese historial no se puede demostrar el estado de los equipos ni detectar los que quedaron atrasados. Comparamos alternativas manuales y automáticas y vimos que la automatización reduce errores, aunque exige más configuración. Además, practicamos la instalación de un sistema operativo en una máquina virtual y su registro en el inventario.")
rich([("¿En qué ámbitos podemos aplicarlo?", True)])
p("Podemos aplicarlo en la administración de equipos de cualquier oficina, colegio o pyme, en el soporte técnico, en la gestión de seguridad (por ejemplo, identificar equipos con versiones vulnerables) y en auditorías o procesos de control de activos de TI.")
rich([("¿Qué término o parte del proceso nos gustaría reforzar?", True)])
p("Nos gustaría reforzar el uso de herramientas de inventario como GLPI (instalación del servidor y del agente), la automatización con scripts de PowerShell y la diferencia entre actualizaciones de seguridad y de funciones. [El grupo debe confirmar o reemplazar este punto].")

# ---------- 8. Conclusion ----------

h1("8. Conclusión")
p("El análisis permitió comparar seis alternativas para actualizar y registrar software. Con los criterios definidos, GLPI con agente resultó la opción más completa (17 de 20), mientras que la planilla Excel y winget permiten avanzar de inmediato con bajo costo. Se definió un formato uniforme y un procedimiento de historial de solo adición que asegura trazabilidad de versiones y fechas, cumpliendo el propósito de RF-07.")
p("Como siguientes pasos, el grupo debe reemplazar los datos de ejemplo por el inventario real del laboratorio, completar la instalación del sistema operativo en la máquina virtual con su evidencia y video, y evaluar un piloto de GLPI.")

# ---------- 9. References ----------

h1("9. Referencias")
p("Manuales y documentación oficial consultados para la instalación y configuración:")
for ref in ["Oracle. VirtualBox User Manual. https://www.virtualbox.org/manual/",
            "Microsoft. Windows 10 IoT Enterprise (documentación). https://learn.microsoft.com/windows/iot/iot-enterprise/",
            "Microsoft. Minimum hardware requirements (Windows 10). https://learn.microsoft.com/windows-hardware/design/minimum/minimum-hardware-requirements-overview",
            "Microsoft. Windows Package Manager (winget). https://learn.microsoft.com/windows/package-manager/winget/",
            "GLPI Project. Documentación de GLPI. https://glpi-project.org/documentation/"]:
    bullet(ref)

doc.save(OUTPUT)
print(f"[ÉXITO] Archivo '{OUTPUT}' generado correctamente.")
