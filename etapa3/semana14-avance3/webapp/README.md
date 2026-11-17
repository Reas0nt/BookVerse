# Aplicación web BookVerse - Avance #3 (RF-12)

Página sencilla con HTML5, CSS3 y JavaScript sin dependencias. Guarda lecturas de sensores y genera informes.

## Cómo abrirla

Doble clic en `index.html` (funciona desde `file://`; usa scripts normales, sin módulos ES). Los datos se guardan en el `localStorage` del navegador, con la forma de las tablas RF-11 (`lecturas`, `umbrales`, `alertas`). No hay backend.

## Secciones

1. **Registrar lectura**: sucursal, sensor (temperatura, humedad, conteo de personas), valor y fecha-hora. Valida campos obligatorios, valor numérico y rechaza duplicados (sensor + fecha-hora, como la clave UNIQUE de RF-11). El botón "Simular lecturas" crea lecturas horarias de las últimas 24 h, con algunas temperaturas fuera de rango.
2. **Lecturas almacenadas**: tabla con filtro por sensor, marca de valores fuera de rango y "Borrar todo".
3. **Umbrales**: mínimo y máximo por tipo (por defecto 18-24 °C, 40-60 %, 0-150 personas).
4. **Generar informe**: sucursal y rango de fechas (desde incluida, hasta excluida, como los rangos semiabiertos de RF-11). Permite descargar CSV/JSON e imprimir o guardar como PDF (la hoja de estilos de impresión muestra solo el informe).

## Estructura

- `js/report.js`: lógica pura del informe (sin DOM): `buildReport`, `toCSV`.
- `js/storage.js`: envoltorio de `localStorage` con validación; acepta un backend inyectable.
- `js/app.js`: conexión con el DOM.
- `tests/`: pruebas con el runner de Node.

## Pruebas

```
node --test etapa3/semana14-avance3/webapp/tests/*.test.js
```

(Node 22 requiere el patrón `*.test.js`; pasar solo el directorio falla.)

## Relación con RF-12

| Flujo RF-12 | Implementación |
| --- | --- |
| Normal: procesa datos, calcula promedios y alertas, genera informe | `buildReport` calcula promedio/mín/máx por sensor, alertas críticas (valor fuera de umbral) y recomendaciones (promedio fuera de umbral) |
| Alterno: faltan datos críticos, informe parcial y notificación | Si temperatura o humedad no tienen lecturas en el periodo: estado `PARCIAL`, lista `missing` y aviso en pantalla |
| Excepción: error en la generación, se solicita reintento | Si la generación lanza un error (por ejemplo, almacenamiento corrupto) se muestra el error con botón "Reintentar" |
| Postcondición: informe disponible para descarga o visualización | Vista en pantalla, "Descargar CSV", "Descargar JSON" e "Imprimir / guardar PDF" |

## Criterios de calidad (S6)

- **Completitud**: resumen de los tres sensores, alertas y recomendaciones; faltantes críticos declarados.
- **Exactitud**: promedios, mínimos y máximos redondeados a 1 decimal; límites inclusivos dentro del rango (solo fuera de rango genera alerta).
- **Marcas de tiempo**: cada alerta y el informe llevan fecha-hora (`generatedAt`).
- **Periodo**: el informe indica sucursal y rango desde/hasta.
- **Estado**: `COMPLETO` o `PARCIAL` visible en el informe.
