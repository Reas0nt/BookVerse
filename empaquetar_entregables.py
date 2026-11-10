"""Collect every Stage 2 and Stage 3 deliverable into one folder, ordered by week.

Usage (from the repo root): venv/bin/python empaquetar_entregables.py

The output folder is rebuilt from scratch on every run and is not tracked by git.
If LibreOffice (soffice) is installed, a PDF copy of each Word/PowerPoint file is added.
"""

import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "entregables"
VIDEO_URL = "https://youtu.be/8b-JuKKoMV4"

# (destination folder, list of source files relative to the repo root)
DELIVERABLES = [
    ("S07_Avance1_RF06_Planificacion", [
        "semana7-avance1/Planificacion_Y_Chequeo_BookVerse.xlsx",
    ]),
    ("S08_Avance2_RF07_Software", [
        "semana8-avance2/Informe_Avance2_RF07_Semana8.docx",
        "semana8-avance2/Registro_Software_RF07_Semana8.xlsx",
    ]),
    ("S09_Avance3_RF08_Historial", [
        "semana9-avance3/Informe_Avance3_RF08_Semana9.docx",
        "semana9-avance3/Historial_Mantenimiento_RF08_Semana9.xlsx",
    ]),
    ("S10_Avance4_RF09_Repuestos", [
        "semana10-avance4/Informe_Avance4_RF09_Semana10.docx",
        "semana10-avance4/Control_Inventario_Repuestos_RF09_Semana10.xlsx",
    ]),
    ("S11_Evaluacion_Practica", [
        "semana11-evaluacion/Presentacion_Evaluacion_S11_BookVerse.pptx",
    ]),
    ("S12_Etapa3_Avance1_RF10_Monitoreo", [
        "etapa3/semana12-avance1/Informe_Avance1_RF10_Semana12.docx",
        "etapa3/semana12-avance1/diagramas/clases_rf10.png",
        "etapa3/semana12-avance1/diagramas/clases_rf10.puml",
        "etapa3/semana12-avance1/diagramas/arquitectura_rf10.png",
        "etapa3/semana12-avance1/diagramas/arquitectura_rf10.puml",
    ]),
    ("S13_Etapa3_Avance2_RF11_BaseDatos", [
        "etapa3/semana13-avance2/Informe_Avance2_RF11_Semana13.docx",
        "etapa3/semana13-avance2/schema_rf11.sql",
        "etapa3/semana13-avance2/diagramas/clases_rf11.png",
        "etapa3/semana13-avance2/diagramas/clases_rf11.puml",
        "etapa3/semana13-avance2/diagramas/arquitectura_rf11.png",
        "etapa3/semana13-avance2/diagramas/arquitectura_rf11.puml",
        "etapa3/semana13-avance2/diagramas/mer_rf11.png",
        "etapa3/semana13-avance2/diagramas/mer_rf11.puml",
        "etapa3/semana13-avance2/diagramas/relacional_rf11.png",
        "etapa3/semana13-avance2/diagramas/relacional_rf11.puml",
    ]),
]

SYSTEM_FILES = ["requirements.txt", "requirements-dev.txt"]
SYSTEM_SKIP = {"__pycache__", "instance", ".pytest_cache"}


def check_sources():
    """Fail before touching the output folder if any source file is missing."""
    required = [rel for _, files in DELIVERABLES for rel in files] + SYSTEM_FILES
    required += ["semana11-evaluacion/diagramas", "sistema/README.md"]
    missing = [rel for rel in required if not (ROOT / rel).exists()]
    if missing:
        raise SystemExit("[ERROR] Faltan archivos (ejecute sus scripts generadores primero):\n  "
                         + "\n  ".join(missing))


def copy_deliverables():
    for folder, files in DELIVERABLES:
        dest = OUT / folder
        dest.mkdir(parents=True)
        for rel in files:
            src = ROOT / rel
            shutil.copy2(src, dest / src.name)


def copy_diagrams_and_video():
    s11 = OUT / "S11_Evaluacion_Practica"
    shutil.copytree(ROOT / "semana11-evaluacion" / "diagramas", s11 / "Diagramas_Excalidraw")
    video = OUT / "S08_Avance2_RF07_Software" / "Video_Instalacion_SO.txt"
    video.write_text(
        "Video del proceso de instalación y configuración del sistema operativo\n"
        "Windows 10 IoT Enterprise LTSC 2021 en VirtualBox (máximo 5 minutos)\n\n"
        f"{VIDEO_URL}\n",
        encoding="utf-8",
    )


def zip_system():
    """Zip the web system source (no local database, caches or virtualenv)."""
    dest = OUT / "Sistema_Web_RF06_RF09"
    dest.mkdir()
    archive = dest / "sistema_bookverse.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted((ROOT / "sistema").rglob("*")):
            if path.is_file() and not SYSTEM_SKIP.intersection(path.relative_to(ROOT).parts):
                zf.write(path, path.relative_to(ROOT))
        for rel in SYSTEM_FILES:
            zf.write(ROOT / rel, rel)
    shutil.copy2(ROOT / "sistema" / "README.md", dest / "LEEME_sistema.md")


def export_pdfs():
    """Add a PDF copy of each .docx/.pptx when LibreOffice is available."""
    soffice = shutil.which("soffice")
    if soffice is None:
        print("[AVISO] LibreOffice no está instalado: se omiten las copias en PDF.")
        return
    for doc in sorted(OUT.rglob("*")):
        if doc.suffix in (".docx", ".pptx"):
            try:
                subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(doc.parent), str(doc)],
                               check=True, capture_output=True, timeout=180)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
                print(f"[AVISO] No se pudo crear el PDF de {doc.name}: {error}. "
                      "Cierre LibreOffice si está abierto y vuelva a ejecutar.")


def main():
    check_sources()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    copy_deliverables()
    copy_diagrams_and_video()
    zip_system()
    export_pdfs()
    files = sorted(p.relative_to(OUT) for p in OUT.rglob("*") if p.is_file())
    print(f"[ÉXITO] {len(files)} archivos en '{OUT.name}/':")
    for f in files:
        print(f"  {f}")


if __name__ == "__main__":
    main()
