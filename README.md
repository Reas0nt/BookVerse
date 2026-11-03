# BookVerse - Integración de Competencias II

Deliverables for the BookVerse case.

| Stage | Topic | Location |
|---|---|---|
| Etapa 2 (finished) | Office equipment maintenance, RF-06 to RF-09 | Repository root (folders below) |
| Etapa 3 (in progress) | Emerging technologies: IoT sensors, RF-10 to RF-13 | [`etapa3/`](etapa3/README.md) |

## Etapa 2 structure

| Folder | Content |
|---|---|
| `docs/` | Case study and activity guidelines provided by the course |
| `semana7-avance1/` | Avance #1 (RF-06): Gantt chart and checklist |
| `semana8-avance2/` | Avance #2 (RF-07): progress report and software registry |
| `semana9-avance3/` | Avance #3 (RF-08): maintenance history workbook and report |
| `semana10-avance4/` | Avance #4 (RF-09): spare parts inventory workbook and report |
| `semana11-evaluacion/` | Week 11 practical evaluation: presentation deck, Excalidraw diagrams and system screenshots |
| `sistema/` | Web app covering RF-06 to RF-09 (see [sistema/README.md](sistema/README.md)) |

Each `generar_*.py` script builds the `.docx` / `.xlsx` file next to it.

## Requirements

- Python 3.10 or newer

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt       # add -dev to also install test tools
```

## Regenerate the files

Run each script from its own folder:

```bash
cd semana7-avance1 && python generar_excel_semana7.py && cd ..
cd semana8-avance2 && python generar_excel_semana8.py && python generar_informe_semana8.py && cd ..
cd semana9-avance3 && python generar_excel_semana9.py && python generar_informe_semana9.py && cd ..
cd semana10-avance4 && python generar_excel_semana10.py && python generar_informe_semana10.py && cd ..
python semana11-evaluacion/generar_presentacion.py   # diagrams/screenshots are pre-rendered; regenerating them needs internet (kroki.io) and Firefox
```

## Package the deliverables

```bash
python empaquetar_entregables.py
```

Builds `entregables/` (not tracked by git) with every deliverable ordered by week, a PDF copy of each Word/PowerPoint file (needs LibreOffice), the Excalidraw diagrams, the video link and a zip of the web system.

Edit the data inside the script, then regenerate. Manual edits made directly in the `.docx` or `.xlsx` files are lost the next time the script runs.
