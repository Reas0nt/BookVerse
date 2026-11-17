'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { buildReport, toCSV, DEFAULT_THRESHOLDS } = require('../js/report.js');

const TH = {
  temperatura: { min: 18, max: 24 },
  humedad: { min: 40, max: 60 },
  conteo: { min: 0, max: 150 },
};
const r = (tipo, valor, fechaHora, sucursal = 'Centro') => ({
  sucursal, sensorTipo: tipo, valor, fechaHora, sensorId: `${sucursal}-${tipo}`,
});
const P = { from: '2026-11-16T00:00:00', to: '2026-11-17T00:00:00', now: '2026-11-17T09:00:00' };

test('averages, min, max, count per type rounded to 1 decimal', () => {
  const rep = buildReport([
    r('temperatura', 20, '2026-11-16T01:00:00'),
    r('temperatura', 21, '2026-11-16T02:00:00'),
    r('temperatura', 22.34, '2026-11-16T03:00:00'),
    r('humedad', 50, '2026-11-16T01:00:00'),
  ], TH, P);
  assert.deepEqual(rep.summaries.temperatura, { avg: 21.1, min: 20, max: 22.3, count: 3 });
  assert.equal(rep.summaries.humedad.count, 1);
  assert.equal(rep.summaries.conteo.count, 0);
  assert.equal(rep.summaries.conteo.avg, null);
});

test('critical alert when outside threshold; none at inclusive boundaries', () => {
  const rep = buildReport([
    r('temperatura', 24, '2026-11-16T01:00:00'),
    r('temperatura', 18, '2026-11-16T02:00:00'),
    r('temperatura', 24.5, '2026-11-16T03:00:00'),
    r('temperatura', 17, '2026-11-16T04:00:00'),
    r('humedad', 50, '2026-11-16T01:00:00'),
  ], TH, P);
  assert.equal(rep.criticalAlerts.length, 2);
  assert.deepEqual(rep.criticalAlerts[0], {
    type: 'temperatura', value: 24.5, dateTime: '2026-11-16T03:00:00', limit: 24,
  });
  assert.equal(rep.criticalAlerts[1].limit, 18);
});

test('no alerts when all inside range', () => {
  const rep = buildReport([
    r('temperatura', 20, '2026-11-16T01:00:00'),
    r('humedad', 50, '2026-11-16T01:00:00'),
  ], TH, P);
  assert.equal(rep.criticalAlerts.length, 0);
  assert.equal(rep.recommendations.length, 0);
  assert.equal(rep.status, 'COMPLETO');
  assert.deepEqual(rep.missing, []);
});

test('recommendation when average is above max or below min', () => {
  const hot = buildReport([
    r('temperatura', 26, '2026-11-16T01:00:00'),
    r('temperatura', 28, '2026-11-16T02:00:00'),
    r('humedad', 30, '2026-11-16T01:00:00'),
  ], TH, P);
  assert.equal(hot.recommendations.length, 2);
  assert.match(hot.recommendations[0], /Temperatura promedio sobre el máximo/);
  assert.match(hot.recommendations[0], /climatización/);
  assert.match(hot.recommendations[1], /Humedad promedio bajo el mínimo/);
});

test('PARCIAL with missing list when a critical type has no readings', () => {
  const rep = buildReport([r('temperatura', 20, '2026-11-16T01:00:00')], TH, P);
  assert.equal(rep.status, 'PARCIAL');
  assert.deepEqual(rep.missing, ['humedad']);
});

test('conteo missing does not make the report PARCIAL', () => {
  const rep = buildReport([
    r('temperatura', 20, '2026-11-16T01:00:00'),
    r('humedad', 50, '2026-11-16T01:00:00'),
  ], TH, P);
  assert.equal(rep.status, 'COMPLETO');
});

test('period is half-open: from inclusive, to exclusive', () => {
  const rep = buildReport([
    r('temperatura', 20, '2026-11-16T00:00:00'),
    r('temperatura', 22, '2026-11-17T00:00:00'),
    r('temperatura', 21, '2026-11-15T23:59:59'),
    r('humedad', 50, '2026-11-16T10:00:00'),
  ], TH, P);
  assert.equal(rep.summaries.temperatura.count, 1);
  assert.equal(rep.summaries.temperatura.avg, 20);
});

test('branch filter and period metadata', () => {
  const rep = buildReport([
    r('temperatura', 20, '2026-11-16T01:00:00', 'Centro'),
    r('temperatura', 30, '2026-11-16T01:00:00', 'Norte'),
    r('humedad', 50, '2026-11-16T01:00:00', 'Centro'),
  ], TH, { ...P, branch: 'Centro' });
  assert.equal(rep.summaries.temperatura.count, 1);
  assert.deepEqual(rep.period, { from: P.from, to: P.to, branch: 'Centro' });
  assert.equal(rep.generatedAt, '2026-11-17T09:00:00');
});

test('empty input -> PARCIAL with all critical types missing', () => {
  const rep = buildReport([], TH, P);
  assert.equal(rep.status, 'PARCIAL');
  assert.deepEqual(rep.missing, ['temperatura', 'humedad']);
  assert.deepEqual(rep.criticalAlerts, []);
});

test('default thresholds are used when none given', () => {
  const rep = buildReport([r('temperatura', 30, '2026-11-16T01:00:00')], undefined, P);
  assert.equal(DEFAULT_THRESHOLDS.temperatura.max, 24);
  assert.equal(rep.criticalAlerts.length, 1);
});

test('throws on invalid input (retry flow trigger)', () => {
  assert.throws(() => buildReport('corrupt', TH, P));
  assert.throws(() => buildReport([{ sensorTipo: 'temperatura' }], TH, P));
});

test('toCSV header and rows', () => {
  const rep = buildReport([
    r('temperatura', 26, '2026-11-16T01:00:00'),
    r('humedad', 50, '2026-11-16T01:00:00'),
  ], TH, P);
  const lines = toCSV(rep).split('\n');
  assert.equal(lines[0], 'tipo,promedio,minimo,maximo,cantidad');
  assert.equal(lines[1], 'temperatura,26,26,26,1');
  assert.equal(lines[2], 'humedad,50,50,50,1');
  assert.equal(lines[3], 'conteo,,,,0');
  assert.ok(lines.includes('alerta_tipo,valor,fecha_hora,limite'));
  assert.ok(lines.includes('temperatura,26,2026-11-16T01:00:00,24'));
});
