-- RF-11 - Storage of environmental sensor data (BookVerse, Etapa 3, Avance #2).
-- MySQL 8.0.16+ (CHECK constraints are only enforced from 8.0.16; older versions ignore them).
-- Matches diagramas/relacional_rf11.puml exactly. Safe to rerun: drops the tables first.

CREATE DATABASE IF NOT EXISTS bookverse_sensores
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE bookverse_sensores;

-- Drop in reverse dependency order so the script can be rerun.
DROP TABLE IF EXISTS error_insercion;
DROP TABLE IF EXISTS alerta;
DROP TABLE IF EXISTS lectura;
DROP TABLE IF EXISTS umbral;
DROP TABLE IF EXISTS sensor;
DROP TABLE IF EXISTS sucursal;

CREATE TABLE sucursal (
  id     INT          NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(80)  NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_sucursal_nombre (nombre)
) ENGINE=InnoDB;

CREATE TABLE sensor (
  id          VARCHAR(30) NOT NULL,
  sucursal_id INT         NOT NULL,
  tipo        ENUM('TEMPERATURA', 'HUMEDAD', 'CONTEO_PERSONAS') NOT NULL,
  ubicacion   VARCHAR(80) NOT NULL,
  PRIMARY KEY (id),
  KEY ix_sensor_sucursal (sucursal_id),
  CONSTRAINT fk_sensor_sucursal FOREIGN KEY (sucursal_id) REFERENCES sucursal (id)
) ENGINE=InnoDB;

CREATE TABLE umbral (
  id          INT          NOT NULL AUTO_INCREMENT,
  sucursal_id INT          NOT NULL,
  tipo        ENUM('TEMPERATURA', 'HUMEDAD', 'CONTEO_PERSONAS') NOT NULL,
  minimo      DECIMAL(8,2) NOT NULL,
  maximo      DECIMAL(8,2) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_umbral_sucursal_tipo (sucursal_id, tipo),
  CONSTRAINT fk_umbral_sucursal FOREIGN KEY (sucursal_id) REFERENCES sucursal (id),
  CONSTRAINT ck_umbral_rango CHECK (minimo < maximo)
) ENGINE=InnoDB;

CREATE TABLE lectura (
  id         BIGINT       NOT NULL AUTO_INCREMENT,
  sensor_id  VARCHAR(30)  NOT NULL,
  valor      DECIMAL(8,2) NOT NULL,
  fecha_hora DATETIME(3)  NOT NULL,
  PRIMARY KEY (id),
  -- One reading per sensor and instant: a retried insert cannot duplicate it.
  -- Retry pattern: INSERT ... ON DUPLICATE KEY UPDATE valor = VALUES(valor)  (or INSERT IGNORE).
  UNIQUE KEY uq_lectura_sensor_fecha (sensor_id, fecha_hora),
  CONSTRAINT fk_lectura_sensor FOREIGN KEY (sensor_id) REFERENCES sensor (id)
) ENGINE=InnoDB;

CREATE TABLE alerta (
  id         BIGINT       NOT NULL AUTO_INCREMENT,
  sensor_id  VARCHAR(30)  NOT NULL,
  lectura_id BIGINT       NULL,  -- NULL for SENSOR_SIN_DATOS (no reading caused it)
  tipo       ENUM('FUERA_DE_RANGO', 'SENSOR_SIN_DATOS') NOT NULL,
  mensaje    VARCHAR(200) NOT NULL,
  fecha_hora DATETIME(3)  NOT NULL,
  PRIMARY KEY (id),
  KEY ix_alerta_sensor_fecha (sensor_id, fecha_hora),
  KEY ix_alerta_lectura (lectura_id),
  CONSTRAINT fk_alerta_sensor  FOREIGN KEY (sensor_id)  REFERENCES sensor (id),
  CONSTRAINT fk_alerta_lectura FOREIGN KEY (lectura_id) REFERENCES lectura (id),
  -- An out-of-range alert must point to the reading that caused it.
  CONSTRAINT ck_alerta_lectura CHECK (tipo <> 'FUERA_DE_RANGO' OR lectura_id IS NOT NULL)
) ENGINE=InnoDB;

-- Log of failed inserts: written when a reading could not be stored after retrying.
-- Deliberately NO foreign key: the failed insert may have referenced an unknown or bad
-- sensor, and the error row must still be insertable. sensor_id is plain text here.
CREATE TABLE error_insercion (
  id                 BIGINT       NOT NULL AUTO_INCREMENT,
  sensor_id          VARCHAR(30)  NOT NULL,
  valor              DECIMAL(8,2) NOT NULL,
  fecha_hora_lectura DATETIME(3)  NOT NULL,
  mensaje            VARCHAR(200) NOT NULL,
  intentos           INT          NOT NULL,
  fecha_hora_error   DATETIME(3)  NOT NULL,
  PRIMARY KEY (id),
  KEY ix_error_sensor (sensor_id),
  CONSTRAINT ck_error_intentos CHECK (intentos >= 1)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- Example queries (step 3 of the normal flow: allow queries of stored data)
-- ---------------------------------------------------------------------------

-- 1. Readings of one sensor in a time range.
-- SELECT fecha_hora, valor
--   FROM lectura
--  WHERE sensor_id = 'T-BOD-01'
--    AND fecha_hora >= '2026-11-01 00:00:00' AND fecha_hora < '2026-11-02 00:00:00'
--  ORDER BY fecha_hora;

-- 2. Temperature readings outside the threshold of their branch.
-- SELECT l.fecha_hora, s.id AS sensor, l.valor, u.minimo, u.maximo
--   FROM lectura l
--   JOIN sensor  s ON s.id = l.sensor_id AND s.tipo = 'TEMPERATURA'
--   JOIN umbral  u ON u.sucursal_id = s.sucursal_id AND u.tipo = 'TEMPERATURA'
--  WHERE l.valor < u.minimo OR l.valor > u.maximo
--  ORDER BY l.fecha_hora;

-- 3. Average, minimum and maximum temperature per branch and day.
-- SELECT su.nombre, DATE(l.fecha_hora) AS dia,
--        ROUND(AVG(l.valor), 2) AS promedio, MIN(l.valor) AS minimo, MAX(l.valor) AS maximo
--   FROM lectura l
--   JOIN sensor   s  ON s.id = l.sensor_id AND s.tipo = 'TEMPERATURA'
--   JOIN sucursal su ON su.id = s.sucursal_id
--  GROUP BY su.nombre, DATE(l.fecha_hora)
--  ORDER BY dia, su.nombre;

-- 4. Last reading per sensor (replaces a stored "ultima lectura" column).
-- SELECT sensor_id, MAX(fecha_hora) AS ultima_lectura FROM lectura GROUP BY sensor_id;
