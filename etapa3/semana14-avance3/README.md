# Avance #3 - Semana 14 (RF-12)

**Requirement:** RF-12 Generación de reportes operacionales con base en sensores.
Reports with average conditions, critical alerts and recommendations. Actor: operations manager.

**Guideline:** `../docs/Pauta_Avance3_Semana14.docx`. Organize the report elements (data and presentation by quality requirements), UML report diagram, architecture / data flow diagram, simple web page (HTML5, CSS3, JS) with data storage and report generation, closing questions.

**Flows:** process data, compute averages and alerts, generate the report. If critical data is missing, generate a partial report and notify. On failure, ask for a retry.

## Contents

| File | Content |
|---|---|
| `diagramas/clases_rf12.puml` / `.png` | UML report diagram: Informe, ResumenSensor, AlertaCritica, Recomendacion, GeneradorInforme |
| `diagramas/arquitectura_rf12.puml` / `.png` | Architecture and data flow: sensors, MQTT, monitoring, MySQL, report module, panel, export |
| `webapp/` | Web app (`index.html`, `styles.css`, `js/`, `tests/`); see `webapp/README.md` |
| `capturas/` | Screenshots of the web app (main page, COMPLETO report, PARCIAL report) |
| `generar_diagramas.py` | Renders the `.puml` files to PNG through kroki.io |
| `generar_informe_semana14.py` | Builds `Informe_Avance3_RF12_Semana14.docx` |

## Regenerate

Run from the repository root with the project virtualenv. Rendering diagrams needs internet access (kroki.io).

```bash
# Diagrams (PNG from .puml)
cd etapa3/semana14-avance3 && ../../venv/bin/python generar_diagramas.py
# Word report (uses diagramas/ and capturas/)
../../venv/bin/python generar_informe_semana14.py && cd ../..
# Web app tests (Node)
node --test etapa3/semana14-avance3/webapp/tests/*.test.js
# Open the web app: double click etapa3/semana14-avance3/webapp/index.html
```

The screenshots were taken with headless Firefox on a scratch copy of `webapp/` that loads simulated data (the app itself is unchanged).
