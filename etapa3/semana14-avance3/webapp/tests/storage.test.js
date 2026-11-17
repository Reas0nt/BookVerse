'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { createStorage } = require('../js/storage.js');

function fakeBackend(initial = {}) {
  const m = { ...initial };
  return {
    getItem: (k) => (k in m ? m[k] : null),
    setItem: (k, v) => { m[k] = String(v); },
    removeItem: (k) => { delete m[k]; },
    _m: m,
  };
}
const ok = { sucursal: 'Centro', sensorTipo: 'temperatura', valor: 21.5, fechaHora: '2026-11-16T10:00:00' };

test('addReading stores a valid reading with sensorId', () => {
  const s = createStorage(fakeBackend());
  const res = s.addReading(ok);
  assert.equal(res.ok, true);
  const all = s.getReadings();
  assert.equal(all.length, 1);
  assert.equal(all[0].sensorId, 'Centro-temperatura');
});

test('rejects non numeric value and missing fields', () => {
  const s = createStorage(fakeBackend());
  assert.equal(s.addReading({ ...ok, valor: 'abc' }).ok, false);
  assert.equal(s.addReading({ ...ok, valor: '' }).ok, false);
  assert.equal(s.addReading({ ...ok, sucursal: '' }).ok, false);
  assert.equal(s.addReading({ ...ok, fechaHora: '' }).ok, false);
  assert.equal(s.addReading({ ...ok, sensorTipo: 'viento' }).ok, false);
  assert.equal(s.getReadings().length, 0);
});

test('rejects duplicate sensorId + fechaHora (RF-11 UNIQUE)', () => {
  const s = createStorage(fakeBackend());
  assert.equal(s.addReading(ok).ok, true);
  const dup = s.addReading({ ...ok, valor: 22 });
  assert.equal(dup.ok, false);
  assert.match(dup.error, /duplicad/i);
  assert.equal(s.getReadings().length, 1);
});

test('thresholds default, can be saved and validated', () => {
  const s = createStorage(fakeBackend());
  assert.equal(s.getThresholds().temperatura.max, 24);
  assert.equal(s.setThresholds({ temperatura: { min: 10, max: 5 } }).ok, false);
  assert.equal(s.setThresholds({ temperatura: { min: 15, max: 26 } }).ok, true);
  assert.equal(s.getThresholds().temperatura.max, 26);
});

test('clearReadings empties the table', () => {
  const s = createStorage(fakeBackend());
  s.addReading(ok);
  s.clearReadings();
  assert.equal(s.getReadings().length, 0);
});

test('corrupt storage throws a StorageError on read', () => {
  const s = createStorage(fakeBackend({ 'bookverse.lecturas': '{not json' }));
  assert.throws(() => s.getReadings(), /almacenamiento/i);
});

test('failing backend write returns ok:false instead of throwing', () => {
  const b = fakeBackend();
  b.setItem = () => { throw new Error('quota'); };
  const s = createStorage(b);
  assert.equal(s.addReading(ok).ok, false);
});
