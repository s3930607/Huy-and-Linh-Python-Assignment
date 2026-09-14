CREATE TABLE IF NOT EXISTS Persona (
    PersonaID   INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    role        TEXT NOT NULL,
    age         INTEGER,
    goal        TEXT NOT NULL,
    frustration TEXT,
    tech_skill  TEXT
);

CREATE TABLE IF NOT EXISTS TeamMember (
    StudentID TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    role      TEXT,
    subtask   TEXT CHECK (subtask IN ('A', 'B'))
);

CREATE TABLE IF NOT EXISTS MissionStatement (
    id            INTEGER PRIMARY KEY,
    heading       TEXT NOT NULL,
    body          TEXT NOT NULL,
    display_order INTEGER DEFAULT 0
);
