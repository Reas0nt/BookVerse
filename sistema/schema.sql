DROP TABLE IF EXISTS part_movement;
DROP TABLE IF EXISTS part;
DROP TABLE IF EXISTS validation;
DROP TABLE IF EXISTS software_update;
DROP TABLE IF EXISTS software;
DROP TABLE IF EXISTS maintenance;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('administrador', 'tecnico'))
);

CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    hostname TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('PC', 'Notebook', 'Impresora', 'Otro')),
    location TEXT NOT NULL,
    serial_number TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'operativo'
);

CREATE TABLE maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL REFERENCES equipment (id),
    technician_id INTEGER NOT NULL REFERENCES user (id),
    type TEXT NOT NULL CHECK (type IN ('preventivo', 'correctivo')),
    performed_on TEXT NOT NULL,
    description TEXT NOT NULL,
    observations TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE software (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    current_version TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE software_update (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    software_id INTEGER NOT NULL REFERENCES software (id),
    equipment_id INTEGER NOT NULL REFERENCES equipment (id),
    technician_id INTEGER NOT NULL REFERENCES user (id),
    previous_version TEXT NOT NULL,
    new_version TEXT NOT NULL,
    updated_on TEXT NOT NULL,
    method TEXT NOT NULL CHECK (method IN ('manual', 'automatica', 'remota')),
    changes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE validation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL REFERENCES equipment (id),
    maintenance_id INTEGER NOT NULL REFERENCES maintenance (id),
    validated_by INTEGER NOT NULL REFERENCES user (id),
    result TEXT NOT NULL CHECK (result IN ('OK', 'Falla')),
    observations TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE part (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    status TEXT NOT NULL DEFAULT 'en buen estado'
        CHECK (status IN ('en buen estado', 'en reparación', 'fuera de servicio'))
);

CREATE TABLE part_movement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id INTEGER NOT NULL REFERENCES part (id),
    technician_id INTEGER NOT NULL REFERENCES user (id),
    kind TEXT NOT NULL CHECK (kind IN ('ingreso', 'salida')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    moved_on TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
