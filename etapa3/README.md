# BookVerse - Etapa 3: Exploración de Tecnologías Emergentes

Stage 3 continues the BookVerse case with IoT sensors in the branches: temperature, humidity and people counting (RF-10 to RF-13).
It is separate from Stage 2 (equipment maintenance, RF-06 to RF-09), which lives at the repository root.

## Activities

| Folder | Activity | Requirement | Deliverable | Guideline |
|---|---|---|---|---|
| `semana12-avance1/` | Avance #1 | RF-10 Sensor monitoring | UML class diagram + high-level architecture diagram | `docs/Pauta_Avance1_Semana12.docx` |
| `semana13-avance2/` | Avance #2 | RF-11 Sensor data storage | Class diagram, architecture diagram, ER model (MER), relational model + MySQL schema | `docs/Pauta_Avance2_Semana13.docx` |
| `semana14-avance3/` | Avance #3 | RF-12 Operational reports | UML report diagram, data flow diagram, web app, Word report (done) | `docs/Pauta_Avance3_Semana14.docx` |
| `semana15-avance4/` | Avance #4 | RF-13 Testing and adjustments | Test cases, results, observations and adjustments | Pending |
| `semana16-evaluacion/` | Final evaluation | RF-10 to RF-13 | Web prototype, metacognitive sheet, induction matrix | `docs/Rubrica_Etapa3.docx` |

Weeks 13 to 16 are inferred from the requirement order and the Stage 2 pattern (one RF per week, then an evaluation).
Confirm each one when its guideline is published.

## Course documents

| File | Content |
|---|---|
| `docs/Caso_Etapa3.docx` | Case study with RF-10 to RF-13 detail (actor, flows, exceptions) |
| `docs/Pauta_Avance1_Semana12.docx` | Avance #1 guideline (RF-10 UML model) |
| `docs/Pauta_Avance2_Semana13.docx` | Avance #2 guideline (RF-11 data model) |
| `docs/Pauta_Avance3_Semana14.docx` | Avance #3 guideline (RF-12 report design and web page) |
| `docs/Rubrica_Etapa3.docx` | Stage 3 rubric |

## How Stage 3 is graded

| Competency | Weight | Criteria |
|---|---|---|
| CE5N2 Specialty | 70% | Web prototype evaluation, prototype construction (connected to a database), functional tests |
| CSVN2 Values | 15% | Metacognitive sheet: institutional value (Fraternidad y Solidaridad / Excelencia y Esfuerzo) and moral act |
| CEMN2 Employability | 15% | Induction matrix: lifelong learning and innovation |

Each criterion scores 7 (Sobresaliente), 6 (Destacado), 5 (Competente) or 0 (Insuficiente).

## Regenerate

Run from the repository root with the project virtualenv. Diagram rendering needs internet access (kroki.io).

```bash
# Avance #1 (week 12): render the PlantUML diagrams, then build the Word report
cd etapa3/semana12-avance1
../../venv/bin/python generar_diagramas.py
../../venv/bin/python generar_informe_semana12.py
# Avance #2 (week 13): diagrams (class, architecture, MER, relational), then the report
cd ../semana13-avance2
../../venv/bin/python generar_diagramas.py
../../venv/bin/python generar_informe_semana13.py
# Avance #3 (week 14): diagrams, report, web app tests
cd ../semana14-avance3
../../venv/bin/python generar_diagramas.py
../../venv/bin/python generar_informe_semana14.py
cd ../..
node --test etapa3/semana14-avance3/webapp/tests/*.test.js

# Package every deliverable (Stage 2 and Stage 3) into entregables/ and entregables.zip
venv/bin/python empaquetar_entregables.py
```

PDF copies of the Word files are created when LibreOffice (`soffice`) is installed.
