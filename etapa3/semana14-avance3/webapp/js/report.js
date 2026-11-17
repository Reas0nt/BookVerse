/* Pure report logic (no DOM). Works as a browser global (BookVerse.report) and under Node. */
(function (root) {
  'use strict';

  var TYPES = ['temperatura', 'humedad', 'conteo'];
  var CRITICAL_TYPES = ['temperatura', 'humedad'];
  var LABELS = { temperatura: 'Temperatura', humedad: 'Humedad', conteo: 'Conteo de personas' };
  var ADVICE = {
    temperatura: { high: 'revisar climatización', low: 'revisar calefacción' },
    humedad: { high: 'revisar deshumidificación', low: 'revisar humidificación' },
    conteo: { high: 'revisar aforo y control de acceso', low: 'revisar afluencia de público' }
  };
  var DEFAULT_THRESHOLDS = {
    temperatura: { min: 18, max: 24 },
    humedad: { min: 40, max: 60 },
    conteo: { min: 0, max: 150 }
  };

  function round1(n) { return Math.round(n * 10) / 10; }

  function toTime(v) {
    var t = v instanceof Date ? v.getTime() : new Date(v).getTime();
    if (isNaN(t)) throw new Error('Fecha inválida: ' + v);
    return t;
  }

  function toIso(v) {
    if (v === undefined || v === null || v === '') return null;
    return v instanceof Date ? v.toISOString() : String(v);
  }

  function filterReadings(readings, opts) {
    var from = opts.from ? toTime(opts.from) : -Infinity;
    var to = opts.to ? toTime(opts.to) : Infinity;
    return readings.filter(function (x) {
      var t = toTime(x.fechaHora);
      if (!(t >= from && t < to)) return false; // half-open [from, to)
      return !opts.branch || x.sucursal === opts.branch;
    });
  }

  function buildReport(readings, thresholds, opts) {
    opts = opts || {};
    thresholds = thresholds || DEFAULT_THRESHOLDS;
    if (!Array.isArray(readings)) throw new Error('Las lecturas no son una lista válida');
    readings.forEach(function (x) {
      if (!x || TYPES.indexOf(x.sensorTipo) === -1 || typeof x.valor !== 'number' ||
          !isFinite(x.valor) || !x.fechaHora) {
        throw new Error('Lectura inválida en el almacenamiento');
      }
    });

    var inPeriod = filterReadings(readings, opts);
    var summaries = {};
    var alerts = [];
    var recs = [];
    var missing = [];

    TYPES.forEach(function (type) {
      var rows = inPeriod.filter(function (x) { return x.sensorTipo === type; });
      var th = thresholds[type] || DEFAULT_THRESHOLDS[type];
      if (rows.length === 0) {
        summaries[type] = { avg: null, min: null, max: null, count: 0 };
        if (CRITICAL_TYPES.indexOf(type) !== -1) missing.push(type);
        return;
      }
      var vals = rows.map(function (x) { return x.valor; });
      var sum = vals.reduce(function (a, b) { return a + b; }, 0);
      var avg = sum / vals.length;
      summaries[type] = {
        avg: round1(avg), min: round1(Math.min.apply(null, vals)),
        max: round1(Math.max.apply(null, vals)), count: vals.length
      };
      rows.slice().sort(function (a, b) { return toTime(a.fechaHora) - toTime(b.fechaHora); })
        .forEach(function (x) {
          if (x.valor > th.max) alerts.push({ type: type, value: x.valor, dateTime: x.fechaHora, limit: th.max });
          else if (x.valor < th.min) alerts.push({ type: type, value: x.valor, dateTime: x.fechaHora, limit: th.min });
        });
      if (avg > th.max) {
        recs.push(LABELS[type] + ' promedio sobre el máximo (' + round1(avg) + ' > ' + th.max + '): ' + ADVICE[type].high);
      } else if (avg < th.min) {
        recs.push(LABELS[type] + ' promedio bajo el mínimo (' + round1(avg) + ' < ' + th.min + '): ' + ADVICE[type].low);
      }
    });

    return {
      status: missing.length ? 'PARCIAL' : 'COMPLETO',
      generatedAt: toIso(opts.now) || new Date().toISOString(),
      period: { from: toIso(opts.from), to: toIso(opts.to), branch: opts.branch || null },
      summaries: summaries,
      criticalAlerts: alerts,
      recommendations: recs,
      missing: missing
    };
  }

  function toCSV(report) {
    var lines = ['tipo,promedio,minimo,maximo,cantidad'];
    TYPES.forEach(function (t) {
      var s = report.summaries[t];
      var f = function (v) { return v === null ? '' : v; };
      lines.push([t, f(s.avg), f(s.min), f(s.max), s.count].join(','));
    });
    lines.push('', 'alerta_tipo,valor,fecha_hora,limite');
    report.criticalAlerts.forEach(function (a) {
      lines.push([a.type, a.value, a.dateTime, a.limit].join(','));
    });
    return lines.join('\n');
  }

  var api = {
    TYPES: TYPES, CRITICAL_TYPES: CRITICAL_TYPES, LABELS: LABELS,
    DEFAULT_THRESHOLDS: DEFAULT_THRESHOLDS, buildReport: buildReport, toCSV: toCSV
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else { root.BookVerse = root.BookVerse || {}; root.BookVerse.report = api; }
})(typeof window !== 'undefined' ? window : this);
