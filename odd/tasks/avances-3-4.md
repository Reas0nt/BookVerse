# Feature: avances-3-4

## Objective

Word report and Excel workbook for Avance #3 (week 9, RF-08 maintenance history query) and Avance #4 (week 10, RF-09 spare parts inventory control), following the same generator pattern as week 8.

## Problem / Why

Guidelines `docs/Pauta_Avance3_Semana9.docx` and `docs/Pauta_Avance4_Semana10.docx` require documents; the week 11 deck references them. Only the web system covers RF-08/RF-09 today.

## Scope

- `semana9-avance3/`: `generar_excel_semana9.py` → `Historial_Mantenimiento_RF08_Semana9.xlsx`; `generar_informe_semana9.py` → `Informe_Avance3_RF08_Semana9.docx`.
- `semana10-avance4/`: `generar_excel_semana10.py` → `Control_Inventario_Repuestos_RF09_Semana10.xlsx`; `generar_informe_semana10.py` → `Informe_Avance4_RF09_Semana10.docx`.
- Root README structure + regenerate commands.

Out of scope: refactoring week 7/8 generators; changing the web system.

## Constraints

- Python only (openpyxl, python-docx). Self-contained scripts, same visual style as week 8.
- Document text in neutral professional Spanish; code in English.
- Group: Bastián Andrade, María Ojeda, Maikol Ulloa. Teacher: Manuel Merino. Course: Integración de Competencias 2.
- Equipment IDs consistent with week 8 workbook (EQ-001..EQ-004) plus the real VM WIN10-BOOKVERSE. Illustrative data clearly marked; real facts (VM install, KVM fix) stated as real.

## TDD

- Mode: off (default). Checks: scripts run; docx text extraction review; render to PDF and visual check; xlsx formulas recalc in LibreOffice without errors; `venv/bin/python -m pytest sistema/tests -q` still passes.

## Delivery

- Branch `feat/avances-3-4`, no remote, work-unit commits. RDD global on.

## Tasks

- [x] T1 Avance 3 (RF-08): Excel history workbook + Word report. Route: delegated writer (writer trigger: 2+ non-trivial files).
- [x] T2 Avance 4 (RF-09): Excel inventory workbook (stock via formulas) + Word report. Route: delegated writer.
- [x] T3 README update. Route: same writer (mechanical).

## Acceptance criteria

- Every point of each guideline (development steps, teacher review, closing questions) has a section.
- Excel: dropdown validation, autofilter, frozen headers; week 10 stock computed by formulas from movements and exits larger than stock flagged.
- No placeholders left except group-owned drafts explicitly marked.

## Progress / Evidence

- T1: both scripts run from `semana9-avance3/`; xlsx renders in LibreOffice with no #NAME?/#VALUE!/#REF! and serial lookup resolves; docx 9 pages, tables checked visually, no leftover brackets; pytest 46 passed. EQ-005 entry dates (15/16-10-2026) are placeholders for the group to confirm.
- T2: both scripts run from `semana10-avance4/`; xlsx recalculated in LibreOffice (pdftotext: no #NAME?/#VALUE!/#REF!/Err; Inventario shows 2 Reponer, 0 ERROR; forced oversized salida test shows ERROR); docx 8 pages, tables checked visually; pytest 46 passed.
- T3: README structure rows and regenerate commands added; diff reviewed.

## Next step

User review; merge/push are user decisions.
