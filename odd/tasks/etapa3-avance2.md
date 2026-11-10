# Etapa 3 - Avance #2 (RF-11)

## Objective
Deliver Avance #2 of stage 3 (week 13): data model for RF-11 (storage of environmental sensor data in MySQL). Deliverables: UML class diagram, architecture diagram, ER model (MER), relational model, plus a Word report.

## Problem / why
The course guideline (`etapa3/docs/Pauta_Avance2_Semana13.docx`) asks the group to analyze RF-11, design the class and architecture diagrams, build the MER and relational model (entities, PK, FK, relationships, attributes), verify them against RF-11 (temperature variations in particular) and answer the closing questions.

## Scope
- `etapa3/semana13-avance2/`: PlantUML sources, rendered PNGs, MySQL DDL (`schema_rf11.sql`), generator scripts, Word report.
- `etapa3/README.md`, `etapa3/semana13-avance2/README.md`, root `empaquetar_entregables.py` (S13 entry).
- Out of scope: running prototype, RF-12/RF-13.

## Constraints
- Same conventions as Avance #1: python-docx generator, PlantUML rendered with kroki.io (stdlib urllib), simple diagrams with good practices.
- Consistent with the RF-10 model (Sucursal, Sensor, Lectura, Umbral, Alerta).
- Artifacts in Spanish (course deliverable), code/comments in English.

## TDD
Mode: off (no project TDD config). Checks: the generators run, the DDL loads in SQLite-compatible form or is reviewed by hand, outputs open, packaging succeeds, `pytest` stays green.

## Tasks
- [x] T1 (572bdd3) Diagrams + DDL: class, architecture, MER and relational PlantUML sources, PNGs, `schema_rf11.sql`. Route: delegated (writer trigger, 2+ non-trivial files).
- [x] T2 (12718ae) Report: `generar_informe_semana13.py` -> `Informe_Avance2_RF11_Semana13.docx`. Route: delegated (same writer).
- [x] T3 (b5e09eb) Packaging + docs: S13 in `empaquetar_entregables.py`, READMEs. Route: delegated (same writer).
- [x] T4 (5bbac46) Review follow-ups: error_insercion without FK, UNIQUE(sensor_id, fecha_hora) on lectura, CHECK on alerta, rerunnable DDL, half-open range query, class/MER/relational/report aligned, atomic PNG write. Route: delegated (single writer).

## Acceptance criteria
- The models cover the RF-11 flows: receive the reading, insert it, allow queries, and on a failed insert log the error and retry.
- The MER and the relational model have PKs, FKs, cardinalities and attributes, and match the DDL.
- Temperature variations are traceable through readings outside the threshold and the alerts they create.
- The report regenerates from the script and `python empaquetar_entregables.py` succeeds.

## Delivery
Strategy: ask-on-risk. Forecast about 500 authored lines, mostly generator and diagram sources.

## Progress
- T1 done: class, architecture, MER (Chen notation, accepted by kroki), relational diagrams + PNGs, `schema_rf11.sql` (sqlite-relaxed load OK, MySQL reviewed by hand). Route: delegated writer.
- T2 done: report 10 pages portrait (PDF checked in scratch, not committed, same as S12). MER and relational figures are 9 cm wide (not 16) so their tables stay on one page.
- T3 done: S13 entry in packager (packaging OK), READMEs updated, pytest 46 passed.
- Branch `feat/etapa3-avance2` created; guideline copied to `etapa3/docs/`.

## Next step
Group rewrites closing questions; share with teacher; push/PR is the user's decision.

## Review
RDD 4 lenses (lineage review-228a6af112c69ce8, base main..99fca08): approved, acknowledged (authority burned). Advisory only, follow-ups: error_insercion FK blocks logging when the sensor/insert fails (R3/R4), retry not idempotent (no unique key on lectura sensor_id+fecha_hora), alerta invariants unenforced, DDL not rerunnable, ErrorInsercion attributes drift between class diagram and DDL.
