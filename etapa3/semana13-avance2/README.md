# Avance #2 - Semana 13 (RF-11)

**Requirement:** RF-11 Almacenamiento y modelo de datos de sensores ambientales.
Store sensor readings in a queryable database (MySQL). Actor: database administrator.

**Flows:** receive data from the monitoring module, insert it, allow queries. If an insert fails, log the error and retry.

**Guideline:** `../docs/Pauta_Avance2_Semana13.docx`. Analyze RF-11 (focus on temperature variations), class diagram, architecture diagram, ER model (MER) and relational model, verify alignment with RF-11, answer the closing questions.

## Contents

| File | Content |
|---|---|
| `diagramas/clases_rf11.puml` / `.png` | Class diagram: capture, processing and storage (repository with retry, insertion error log) |
| `diagramas/arquitectura_rf11.puml` / `.png` | Architecture: sensors, MQTT, monitoring and storage modules, MySQL, queries |
| `diagramas/mer_rf11.puml` / `.png` | ER model (Chen notation) |
| `diagramas/relacional_rf11.puml` / `.png` | Relational model with PK, FK and MySQL types |
| `schema_rf11.sql` | MySQL 8 DDL matching the relational model, plus example queries |
| `generar_diagramas.py` | Renders the `.puml` files to PNG through kroki.io |
| `generar_informe_semana13.py` | Builds `Informe_Avance2_RF11_Semana13.docx` |

## Regenerate

Run from this folder with the project virtualenv. Rendering needs internet access (kroki.io).

```bash
../../venv/bin/python generar_diagramas.py
../../venv/bin/python generar_informe_semana13.py
```

Then package everything from the repository root: `venv/bin/python empaquetar_entregables.py`.
