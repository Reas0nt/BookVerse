# Feature: presentacion-s11

## Objective

PowerPoint deck for the week 11 practical evaluation (activity 2.6) that synthesizes the Stage 2 documents and evidence (activities 2.2 to 2.6), with Excalidraw diagrams.

## Problem / Why

`docs/Evaluacion_Practica_Semana11.docx` requires a PPT that includes: maintenance records (RF-06), software update document (RF-07), OS installation video, maintenance history document (RF-08), and conclusions and improvement opportunities. The rubric scores planning (milestones, deliverables, risks), installation/configuration (manuals, configuration, tests, reported actions) and validation (integral tests, errors found and fixed).

## Scope

- `semana11-evaluacion/generar_diagramas.py`: builds `.excalidraw` sources (editable at excalidraw.com) and renders PNGs (Kroki + headless Firefox).
- `semana11-evaluacion/generar_capturas.py`: screenshots of the web system pages (Flask test client + headless Firefox).
- `semana11-evaluacion/generar_presentacion.py`: builds `Presentacion_Evaluacion_S11_BookVerse.pptx` with python-pptx.
- Slide content in neutral professional Spanish; code in English.

Out of scope: recording the video, real lab inventory data, Avance 3/4 Word documents.

## Constraints

- Python only (project decision: no Node). python-pptx 1.0.2 added to requirements.
- Diagram rendering needs internet (kroki.io) and Firefox; generated PNGs are committed so the deck builds offline.
- Safe fonts: Cambria (headings), Calibri (body).

## TDD

- Mode: off (default). Checks: deck builds, `slide_text.py` content check, visual QA of every slide render, `venv/bin/python -m pytest sistema/tests -q` still passes.

## Delivery

- Branch `feat/presentacion-s11`, no remote, work-unit commits. RDD global on.

## Tasks

- [x] T1 Diagrams: process flow S7-S11, system architecture, data model, KVM error resolution (`.excalidraw` + `.png`). Route: delegated writer.
- [x] T2 System screenshots (login, history, maintenance form, spare parts). Route: delegated writer.
- [x] T3 Deck generator + PPTX with speaker notes, visual QA. Route: delegated writer.

## Acceptance criteria

- Every item required by the S11 guideline has its own slide.
- Rubric criteria (planning, installation/configuration, validation) are visibly covered.
- No text overflow in the renders; placeholders limited to video link and teacher name.

## Progress / Evidence

(Updated after each task.)

- T1: 4 diagrams (`proceso`, `arquitectura`, `modelo_datos`, `error_kvm`) generated as `.excalidraw` + `.png` via Kroki + headless Firefox; every PNG inspected visually, no overlaps or overflow.
- T2: 5 screenshots in `semana11-evaluacion/capturas/` (login, historial, registro, repuestos, actualizaciones) from Flask test client + headless Firefox; all inspected visually.
- T3: 18-slide deck with Spanish speaker notes built by `generar_presentacion.py`; `validate.py` passed, `slide_text.py` shows only the allowed placeholders, all 18 slide renders inspected; `pytest sistema/tests -q`: 46 passed. `python-pptx==1.0.2` added to requirements.txt. Added `carta_gantt.png` (rendered from the Excel workbook).

- RDD: assess 9cf4310..a39919b high (process spawning in generar_capturas.py); consent granted; 4-lens review approved and acknowledged. 14 advisory findings (fragile form prefill, unchecked sample data, temp dir/profile leaks, diagram source/PNG divergence, readability nits) kept as optional follow-ups.

## Next step

Review the deck, fill in the teacher name and the video link, and record the video.
