# Etapa 3 - Avance #3 (RF-12, week 14)
Objective: deliver Avance #3: UML report diagram, data-flow architecture diagram, simple web app (HTML5/CSS3/JS) that stores sensor data and generates reports, and a Word report.
Branch: `feat/etapa3-avance3`. Delivery: ask-on-risk. Test runner: `node --test` for the web app's pure logic, if node is available; `venv/bin/python -m pytest -q` (46) for the stage 2 suite.

## Specs
Source: `etapa3/docs/Pauta_Avance3_Semana14.docx` and RF-12 in `etapa3/docs/Caso_Etapa3.docx`. Quotes are verbatim.
- S1 Organize the report elements: "Este paso incluye la identificación de los datos que se deben incluir en el informe y cómo estos datos deben ser presentados de acuerdo con los requerimientos de calidad."
- S2 UML report diagram: "crear un diagrama UML que represente la estructura del informe. Este diagrama debe incluir las clases o elementos relevantes que componen el informe y cómo se estructuran los datos que se incluirán en él. Deben definir las relaciones entre los distintos elementos que componen el informe".
- S3 Architecture diagram: "debe reflejar cómo cada parte del sistema obtiene la información necesaria para generar el informe, asegurando que los datos estén disponibles y se manejen correctamente a lo largo del proceso." (RF-12 also says "diagrama de flujo de datos".)
- S4 Web app: "programar una pagina web sencilla con HTML5, CSS3 y JavaScript. Implementando las funciones de almacenamiento de datos y generación de reportes de los diferentes sensores."
- S5 RF-12 behavior: "incluyendo condiciones promedio, alertas críticas y recomendaciones de ajuste". Normal flow: "El sistema procesa los datos. Calcula valores promedios y alertas. Generar un informe con los reportes." Alternate flow: "Si faltan datos críticos, se genera un informe parcial y se notifica." Exception: "Error en la generación del informe, se solicita reintento." Postcondition: "El informe queda disponible para descarga o visualización."
- S6 Quality validation: "El sistema debe ser capaz de generar un informe que cumpla con los estándares de calidad establecidos."
- S7 Closing questions: "¿Qué aprendiste de la actividad realizada?", "¿En qué ámbitos puedes utilizar o aplicar lo realizado en la actividad?", "¿Hubo algún término, definición o parte del proceso que necesites reforzar? ¿Cuál?"
- Constraints (carried from Avances 1-2): simple diagrams with good practices; consistent with the RF-10/RF-11 model (Sucursal, Sensor, Lectura, Umbral, Alerta); PlantUML through kroki; course artifacts in Spanish; cover date 17/11/2026. Assumption: the web app runs without a backend and stores data in the browser (localStorage), shaped like the RF-11 tables.

## Tasks
- T1 (S2, S3) Diagrams: `clases_rf12.puml`, `arquitectura_rf12.puml`, PNGs, `generar_diagramas.py`. Route: delegated, writer A, in parallel with T2 on a disjoint surface. Status: done. Commit: 32dd053.
- T2 (S4, S5, S6) Web app in `etapa3/semana14-avance3/webapp/` with tests for the report logic. Route: delegated, writer B, in parallel with T1. Status: done. Commit: dec9da0 (RED observed, 19/19 `node --test` GREEN).
- T3 (S1, S5-S7) Report `generar_informe_semana14.py` -> docx, S14 packaging, READMEs. Depends on T1 and T2. Route: delegated (context backstop). Status: done. Commit: `docs(etapa3): add avance 3 RF-12 report and packaging` (see git log). Evidence: report 13 pages, no empty pages; `empaquetar_entregables.py` OK (S14 entry); node 19 pass; pytest 46 passed. Closing questions are a DRAFT for the group (S7).

## Log
- L1 (2026-11-17) User: "'/home/rsntxft/Descargas/IEI-091_E3_S12_3_5 Pauta de actividad.docx' esta es la continuacion con la fecha de hoy 17/11/2026"
- L2 Branch created, guideline copied to `etapa3/docs/Pauta_Avance3_Semana14.docx`. Forecast is about 900 authored lines. Three commits, one per task.
- L3 T1 done (32dd053), T2 done (dec9da0): 19/19 web app tests GREEN after observed RED.
- L4 T3 screenshots: headless Firefox with a fresh profile on scratch copies of `webapp/` (under `mktemp -d -p ~/Escritorio`, deleted afterwards) with an injected script that stores simulated readings and submits the report form; `webapp/` itself unchanged. Captures: `01_pagina_principal.png`, `02_informe_completo.png` (COMPLETO, 14 critical alerts, 2 recommendations), `03_informe_parcial.png` (PARCIAL, only temperature).
- L5 T3 report: `generar_informe_semana14.py` -> `Informe_Avance3_RF12_Semana14.docx` (13 pages). S1 in section 3, S5 in sections 2 and 8, S6 in section 7, S7 in section 9 (DRAFT). Packaging S14 added, READMEs updated.
