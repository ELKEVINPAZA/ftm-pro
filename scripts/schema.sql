-- ============================================================
-- FOOTBALL TOURNAMENT MANAGER - DATABASE SCHEMA
-- ============================================================

PRAGMA foreign_keys = ON;

-- USERS & ROLES
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('admin','arbitro','delegado')),
    nombre_completo TEXT,
    email TEXT,
    activo INTEGER DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TOURNAMENTS
CREATE TABLE IF NOT EXISTS torneos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('liga','eliminacion','grupos_eliminacion')),
    fecha_inicio DATE,
    fecha_fin DATE,
    max_equipos INTEGER DEFAULT 16,
    pts_victoria INTEGER DEFAULT 3,
    pts_empate INTEGER DEFAULT 1,
    pts_derrota INTEGER DEFAULT 0,
    estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente','activo','finalizado')),
    reglas TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TEAMS
CREATE TABLE IF NOT EXISTS equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    torneo_id INTEGER,
    nombre TEXT NOT NULL,
    entrenador TEXT,
    ciudad TEXT,
    contacto TEXT,
    escudo TEXT,
    min_jugadores INTEGER DEFAULT 11,
    max_jugadores INTEGER DEFAULT 25,
    activo INTEGER DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id)
);

-- PLAYERS
CREATE TABLE IF NOT EXISTS jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipo_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    numero_camiseta INTEGER,
    posicion TEXT CHECK(posicion IN ('Portero','Defensa','Mediocampista','Delantero')),
    fecha_nacimiento DATE,
    foto TEXT,
    activo INTEGER DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipo_id) REFERENCES equipos(id)
);

-- REFEREES
CREATE TABLE IF NOT EXISTS arbitros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    licencia TEXT,
    telefono TEXT,
    activo INTEGER DEFAULT 1
);

-- MATCH DAYS / JORNADAS
CREATE TABLE IF NOT EXISTS jornadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    torneo_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    nombre TEXT,
    fecha DATE,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id)
);

-- MATCHES
CREATE TABLE IF NOT EXISTS partidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    torneo_id INTEGER NOT NULL,
    jornada_id INTEGER,
    equipo_local_id INTEGER NOT NULL,
    equipo_visitante_id INTEGER NOT NULL,
    arbitro_id INTEGER,
    fecha DATETIME,
    cancha TEXT,
    goles_local INTEGER DEFAULT 0,
    goles_visitante INTEGER DEFAULT 0,
    estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente','en_juego','finalizado','suspendido')),
    fase TEXT DEFAULT 'grupo',
    observaciones TEXT,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id),
    FOREIGN KEY (jornada_id) REFERENCES jornadas(id),
    FOREIGN KEY (equipo_local_id) REFERENCES equipos(id),
    FOREIGN KEY (equipo_visitante_id) REFERENCES equipos(id),
    FOREIGN KEY (arbitro_id) REFERENCES arbitros(id)
);

-- GOALS
CREATE TABLE IF NOT EXISTS goles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partido_id INTEGER NOT NULL,
    jugador_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    minuto INTEGER,
    tipo TEXT DEFAULT 'normal' CHECK(tipo IN ('normal','penal','autogol')),
    FOREIGN KEY (partido_id) REFERENCES partidos(id),
    FOREIGN KEY (jugador_id) REFERENCES jugadores(id),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id)
);

-- CARDS
CREATE TABLE IF NOT EXISTS tarjetas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partido_id INTEGER NOT NULL,
    jugador_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('amarilla','roja','doble_amarilla')),
    minuto INTEGER,
    motivo TEXT,
    FOREIGN KEY (partido_id) REFERENCES partidos(id),
    FOREIGN KEY (jugador_id) REFERENCES jugadores(id),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id)
);

-- SUBSTITUTIONS
CREATE TABLE IF NOT EXISTS sustituciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partido_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    jugador_sale_id INTEGER NOT NULL,
    jugador_entra_id INTEGER NOT NULL,
    minuto INTEGER,
    FOREIGN KEY (partido_id) REFERENCES partidos(id),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
    FOREIGN KEY (jugador_sale_id) REFERENCES jugadores(id),
    FOREIGN KEY (jugador_entra_id) REFERENCES jugadores(id)
);

-- STANDINGS VIEW (materialized via trigger or calculated on-the-fly)
CREATE TABLE IF NOT EXISTS tabla_posiciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    torneo_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    pj INTEGER DEFAULT 0,
    pg INTEGER DEFAULT 0,
    pe INTEGER DEFAULT 0,
    pp INTEGER DEFAULT 0,
    gf INTEGER DEFAULT 0,
    gc INTEGER DEFAULT 0,
    puntos INTEGER DEFAULT 0,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
    UNIQUE(torneo_id, equipo_id)
);

-- DEFAULT ADMIN USER (password: admin123)
INSERT OR IGNORE INTO usuarios (username, password_hash, rol, nombre_completo) 
VALUES ('admin', 'pbkdf2:sha256:260000$salt$hash_placeholder', 'admin', 'Administrador');

INSERT OR IGNORE INTO arbitros (nombre, apellido, licencia) VALUES ('Sin','Árbitro','N/A');
