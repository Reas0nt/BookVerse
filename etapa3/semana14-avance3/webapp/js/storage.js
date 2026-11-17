/* localStorage wrapper shaped like the RF-11 tables (lecturas, umbrales, alertas). */
(function (root) {
  'use strict';

  var isNode = typeof module !== 'undefined' && module.exports;
  var report = isNode ? require('./report.js') : root.BookVerse.report;
  var TYPES = report.TYPES;
  var KEYS = { lecturas: 'bookverse.lecturas', umbrales: 'bookverse.umbrales', alertas: 'bookverse.alertas' };

  function createStorage(backend) {
    function read(key, fallback) {
      try {
        var raw = backend.getItem(key);
        return raw === null || raw === undefined ? fallback : JSON.parse(raw);
      } catch (e) {
        throw new Error('Error de almacenamiento al leer "' + key + '": ' + e.message);
      }
    }
    function write(key, value) {
      try { backend.setItem(key, JSON.stringify(value)); return { ok: true }; }
      catch (e) { return { ok: false, error: 'No se pudo guardar en el almacenamiento: ' + e.message }; }
    }

    function getReadings() {
      var v = read(KEYS.lecturas, []);
      if (!Array.isArray(v)) throw new Error('Error de almacenamiento: tabla de lecturas corrupta');
      return v;
    }

    function validate(r) {
      if (!r || !r.sucursal || !String(r.sucursal).trim()) return 'La sucursal es obligatoria.';
      if (TYPES.indexOf(r.sensorTipo) === -1) return 'Tipo de sensor no válido.';
      if (r.valor === '' || r.valor === null || r.valor === undefined || !isFinite(Number(r.valor))) {
        return 'El valor debe ser numérico.';
      }
      if (!r.fechaHora || isNaN(new Date(r.fechaHora).getTime())) return 'La fecha y hora son obligatorias.';
      return null;
    }

    function addReading(r) {
      var err = validate(r);
      if (err) return { ok: false, error: err };
      var rec = {
        sucursal: String(r.sucursal).trim(), sensorTipo: r.sensorTipo,
        valor: Number(r.valor), fechaHora: r.fechaHora
      };
      rec.sensorId = rec.sucursal + '-' + rec.sensorTipo;
      var all = getReadings();
      var dup = all.some(function (x) { return x.sensorId === rec.sensorId && x.fechaHora === rec.fechaHora; });
      if (dup) return { ok: false, error: 'Lectura duplicada (mismo sensor y fecha-hora).' };
      all.push(rec);
      var w = write(KEYS.lecturas, all);
      return w.ok ? { ok: true, reading: rec } : w;
    }

    function clearReadings() {
      try { backend.removeItem(KEYS.lecturas); return { ok: true }; }
      catch (e) { return { ok: false, error: e.message }; }
    }

    function getThresholds() {
      var v = read(KEYS.umbrales, null);
      return v || JSON.parse(JSON.stringify(report.DEFAULT_THRESHOLDS));
    }

    function setThresholds(th) {
      var merged = getThresholds();
      for (var i = 0; i < TYPES.length; i++) {
        var t = TYPES[i];
        if (!th[t]) continue;
        var min = Number(th[t].min), max = Number(th[t].max);
        if (!isFinite(min) || !isFinite(max)) return { ok: false, error: 'Umbral no numérico en ' + t + '.' };
        if (min > max) return { ok: false, error: 'El mínimo no puede superar el máximo en ' + t + '.' };
        merged[t] = { min: min, max: max };
      }
      return write(KEYS.umbrales, merged);
    }

    function getAlerts() { return read(KEYS.alertas, []); }
    function saveAlerts(list) { return write(KEYS.alertas, list); }

    return {
      getReadings: getReadings, addReading: addReading, clearReadings: clearReadings,
      getThresholds: getThresholds, setThresholds: setThresholds,
      getAlerts: getAlerts, saveAlerts: saveAlerts
    };
  }

  var api = { createStorage: createStorage };
  if (isNode) module.exports = api;
  else { root.BookVerse = root.BookVerse || {}; root.BookVerse.storage = api; }
})(typeof window !== 'undefined' ? window : this);
