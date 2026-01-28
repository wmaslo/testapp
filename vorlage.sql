-- vorlage.sql
-- Dieses SQL-Skript erstellt alle Tabellen, die wir brauchen.
-- Wir führen es EINMAL aus, um datenbank.db zu "befüllen" (Schema anlegen).

-- WICHTIG (für dumme):
-- SQLite hat Foreign Keys NICHT automatisch aktiv.
-- Darum werden wir später in Python pro Verbindung:
-- PRAGMA foreign_keys = ON;
-- setzen. Sonst kann SQLite Regeln ignorieren.

-- --------------------------------------------
-- 1) Kategorien
-- --------------------------------------------
-- Eine Kategorie ist z.B. "Grundlagen", "CAN-Bus", "Hydraulik", ...
-- Jede Kategorie bekommt eine eindeutige ID (Zahl).
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- automatische laufende Nummer: 1, 2, 3, ...
    name TEXT NOT NULL UNIQUE              -- Name muss vorhanden sein und darf nicht doppelt vorkommen
);

-- --------------------------------------------
-- 2) Fragen
-- --------------------------------------------
-- Eine Frage hat:
-- - Text (die Frage)
-- - Lösung (optional)
-- - category_id (zeigt auf categories.id)
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- eindeutige Frage-ID
    question_text TEXT NOT NULL,           -- der Fragetext darf nicht leer sein
    solution TEXT,                         -- Lösung kann leer sein (NULL oder "")
    category_id INTEGER NOT NULL,          -- muss zu einer existierenden Kategorie gehören

    -- Das ist die Verknüpfung zur Kategorie:
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- --------------------------------------------
-- 3) Tests
-- --------------------------------------------
-- Ein Test ist z.B. "Schularbeit 1" am Datum X.
CREATE TABLE IF NOT EXISTS tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- eindeutige Test-ID
    title TEXT NOT NULL,                   -- Titel muss vorhanden sein
    test_date TEXT                         -- Datum als Text (z.B. "2026-01-28"), kann leer sein
);

-- --------------------------------------------
-- 4) test_questions (Zuordnung Test <-> Fragen)
-- --------------------------------------------
-- Ein Test hat viele Fragen und eine Frage kann in vielen Tests vorkommen.
-- Das ist eine klassische m:n Beziehung.
CREATE TABLE IF NOT EXISTS test_questions (
    test_id INTEGER NOT NULL,              -- zeigt auf tests.id
    question_id INTEGER NOT NULL,          -- zeigt auf questions.id

    -- Wichtig (für dumme):
    -- PRIMARY KEY aus beiden Spalten bedeutet:
    -- dieselbe Frage kann im selben Test NICHT zweimal vorkommen.
    PRIMARY KEY (test_id, question_id),

    FOREIGN KEY (test_id) REFERENCES tests(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

