/* DOM wiring. Plain script (no modules) so index.html works from file://. */
(function () {
  'use strict';
  var R = window.BookVerse.report;
  var store = window.BookVerse.storage.createStorage(window.localStorage);
  var UNITS = { temperatura: '°C', humedad: '%', conteo: '' };
  var lastReport = null;

  function $(id) { return document.getElementById(id); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  // Local datetime string "YYYY-MM-DDTHH:MM:SS" (same shape as datetime-local input).
  function localIso(d) {
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + 'T' +
      pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
  }
  function normalizeDt(v) { return v && v.length === 16 ? v + ':00' : v; }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function notify(msg, kind) {
    var n = $('notice');
    n.textContent = msg;
    n.className = 'notice' + (kind ? ' ' + kind : '');
    n.hidden = false;
  }
  function safeReadings() {
    try { return store.getReadings(); } catch (e) { notify(e.message, 'error'); return []; }
  }

  function renderBranches(readings) {
    var names = [];
    readings.forEach(function (r) { if (names.indexOf(r.sucursal) === -1) names.push(r.sucursal); });
    $('lista-sucursales').innerHTML = names.map(function (n) { return '<option value="' + esc(n) + '">'; }).join('');
    var sel = $('i-sucursal'), prev = sel.value;
    sel.innerHTML = '<option value="">Todas</option>' +
      names.map(function (n) { return '<option>' + esc(n) + '</option>'; }).join('');
    sel.value = prev;
  }

  function renderTable() {
    var readings = safeReadings();
    var th;
    try { th = store.getThresholds(); } catch (e) { th = R.DEFAULT_THRESHOLDS; }
    var f = $('filtro-sensor').value;
    var rows = readings.filter(function (r) { return !f || r.sensorTipo === f; })
      .sort(function (a, b) { return a.fechaHora < b.fechaHora ? 1 : -1; });
    $('tbody-lecturas').innerHTML = rows.map(function (r) {
      var t = th[r.sensorTipo];
      var out = t && (r.valor < t.min || r.valor > t.max);
      return '<tr><td>' + esc(r.fechaHora.replace('T', ' ')) + '</td><td>' + esc(r.sucursal) + '</td><td>' +
        esc(R.LABELS[r.sensorTipo]) + '</td><td class="' + (out ? 'out' : '') + '">' + r.valor + ' ' +
        UNITS[r.sensorTipo] + (out ? ' (fuera de rango)' : '') + '</td></tr>';
    }).join('');
    $('contador').textContent = rows.length + ' lectura(s) mostrada(s) de ' + readings.length + ' almacenada(s).';
    renderBranches(readings);
  }

  function loadThresholds() {
    var th;
    try { th = store.getThresholds(); } catch (e) { th = R.DEFAULT_THRESHOLDS; }
    R.TYPES.forEach(function (t) {
      $('u-' + t + '-min').value = th[t].min;
      $('u-' + t + '-max').value = th[t].max;
    });
  }

  // 1. Register reading
  $('form-lectura').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var res = store.addReading({
      sucursal: $('f-sucursal').value, sensorTipo: $('f-sensor').value,
      valor: $('f-valor').value, fechaHora: normalizeDt($('f-fecha').value)
    });
    if (res.ok) { notify('Lectura guardada.'); $('f-valor').value = ''; renderTable(); }
    else notify(res.error, 'error');
  });

  // Simulation: hourly readings for the last 24 h, with some out-of-range temperatures.
  $('btn-simular').addEventListener('click', function () {
    var branch = $('f-sucursal').value.trim() || 'Sucursal Centro';
    var now = new Date(), added = 0;
    now.setMinutes(0, 0, 0);
    var spec = {
      temperatura: function (i) { return i % 6 === 0 ? 27 + Math.random() * 4 : 19 + Math.random() * 4; },
      humedad: function () { return 42 + Math.random() * 16; },
      conteo: function () { return Math.round(20 + Math.random() * 120); }
    };
    for (var h = 24; h >= 1; h--) {
      var dt = localIso(new Date(now.getTime() - h * 3600000));
      R.TYPES.forEach(function (t) {
        var v = Math.round(spec[t](h) * 10) / 10;
        if (store.addReading({ sucursal: branch, sensorTipo: t, valor: v, fechaHora: dt }).ok) added++;
      });
    }
    notify(added + ' lecturas simuladas para ' + branch + '.');
    renderTable();
  });

  // 2. Table
  $('filtro-sensor').addEventListener('change', renderTable);
  $('btn-borrar').addEventListener('click', function () {
    if (window.confirm('¿Borrar todas las lecturas almacenadas?')) {
      store.clearReadings();
      $('informe-salida').hidden = true; $('acciones-informe').hidden = true;
      notify('Lecturas eliminadas.'); renderTable();
    }
  });

  // 3. Thresholds
  $('form-umbrales').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var th = {};
    R.TYPES.forEach(function (t) { th[t] = { min: $('u-' + t + '-min').value, max: $('u-' + t + '-max').value }; });
    var res = store.setThresholds(th);
    if (res.ok) { notify('Umbrales guardados.'); renderTable(); } else notify(res.error, 'error');
  });

  // 4. Report
  function fmt(v, t) { return v === null ? '-' : v + (UNITS[t] ? ' ' + UNITS[t] : ''); }

  function renderReport(rep) {
    var p = rep.period;
    var html = '<h3>Informe de condiciones ambientales</h3>' +
      '<p><strong>Estado:</strong> <span class="badge ' + rep.status.toLowerCase() + '">' + rep.status + '</span></p>' +
      '<p><strong>Generado:</strong> ' + esc(rep.generatedAt.replace('T', ' ').slice(0, 19)) + '<br>' +
      '<strong>Sucursal:</strong> ' + esc(p.branch || 'Todas') + '<br>' +
      '<strong>Periodo:</strong> ' + esc((p.from || 'inicio').replace('T', ' ')) + ' a ' +
      esc((p.to || 'fin').replace('T', ' ')) + ' (hasta excluida)</p>';
    if (rep.missing.length) {
      html += '<p class="notice warn">Informe parcial: faltan datos críticos de ' +
        rep.missing.map(function (m) { return R.LABELS[m].toLowerCase(); }).join(', ') + '.</p>';
    }
    html += '<h3>Condiciones promedio</h3><table><thead><tr><th>Sensor</th><th>Promedio</th><th>Mínimo</th>' +
      '<th>Máximo</th><th>Lecturas</th></tr></thead><tbody>' +
      R.TYPES.map(function (t) {
        var s = rep.summaries[t];
        return '<tr><td>' + esc(R.LABELS[t]) + '</td><td>' + fmt(s.avg, t) + '</td><td>' + fmt(s.min, t) +
          '</td><td>' + fmt(s.max, t) + '</td><td>' + s.count + '</td></tr>';
      }).join('') + '</tbody></table>';
    html += '<h3>Alertas críticas (' + rep.criticalAlerts.length + ')</h3>';
    html += rep.criticalAlerts.length
      ? '<table><thead><tr><th>Sensor</th><th>Valor</th><th>Fecha y hora</th><th>Límite superado</th></tr></thead><tbody>' +
        rep.criticalAlerts.map(function (a) {
          return '<tr><td>' + esc(R.LABELS[a.type]) + '</td><td>' + a.value + '</td><td>' +
            esc(a.dateTime.replace('T', ' ')) + '</td><td>' + a.limit + '</td></tr>';
        }).join('') + '</tbody></table>'
      : '<p>Sin alertas críticas en el periodo.</p>';
    html += '<h3>Recomendaciones de ajuste</h3>';
    html += rep.recommendations.length
      ? '<ul>' + rep.recommendations.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>'
      : '<p>Sin ajustes recomendados.</p>';
    $('informe-salida').innerHTML = html;
    $('informe-salida').hidden = false;
    $('acciones-informe').hidden = false;
  }

  function generate() {
    $('error-informe').hidden = true;
    try {
      var from = normalizeDt($('i-desde').value), to = normalizeDt($('i-hasta').value);
      if (!from || !to) throw new Error('Indique el rango de fechas del informe.');
      if (from >= to) throw new Error('La fecha "Desde" debe ser anterior a "Hasta".');
      var rep = R.buildReport(store.getReadings(), store.getThresholds(), {
        from: from, to: to, branch: $('i-sucursal').value || null, now: localIso(new Date())
      });
      lastReport = rep;
      renderReport(rep);
      if (rep.status === 'PARCIAL') notify('Informe parcial: faltan datos críticos (' + rep.missing.join(', ') + ').', 'warn');
      else notify('Informe generado y disponible para descarga o impresión.');
    } catch (e) {
      lastReport = null;
      $('informe-salida').hidden = true; $('acciones-informe').hidden = true;
      $('error-texto').textContent = 'Error en la generación del informe: ' + e.message + ' Se solicita reintento.';
      $('error-informe').hidden = false;
    }
  }
  $('form-informe').addEventListener('submit', function (ev) { ev.preventDefault(); generate(); });
  $('btn-reintentar').addEventListener('click', generate);

  function download(name, text, mime) {
    var url = URL.createObjectURL(new Blob([text], { type: mime }));
    var a = document.createElement('a');
    a.href = url; a.download = name; document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
  }
  $('btn-csv').addEventListener('click', function () {
    if (lastReport) download('informe.csv', R.toCSV(lastReport), 'text/csv;charset=utf-8');
  });
  $('btn-json').addEventListener('click', function () {
    if (lastReport) download('informe.json', JSON.stringify(lastReport, null, 2), 'application/json');
  });
  $('btn-imprimir').addEventListener('click', function () { window.print(); });

  // Defaults: report range = last 24 h; reading date = now.
  var now = new Date();
  $('f-fecha').value = localIso(now);
  $('i-hasta').value = localIso(now).slice(0, 16);
  $('i-desde').value = localIso(new Date(now.getTime() - 24 * 3600000)).slice(0, 16);
  loadThresholds();
  renderTable();
})();
