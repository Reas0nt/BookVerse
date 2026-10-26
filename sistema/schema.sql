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
