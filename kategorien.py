# kategorien.py
# Hier sind alle Funktionen rund um Kategorien.
# "Kategorie" = Thema, z.B. "Grundlagen", "Elektrik", "Hydraulik", ...

import sqlite3  # Wir brauchen das für sqlite3.IntegrityError (wenn UNIQUE verletzt wird)

from datenbank import verbindung  # Unsere einfache DB-Verbindung


def alle_kategorien():
    """
    Gibt ALLE Kategorien zurück.
    Rückgabe: Liste von Tupeln: [(id, name), (id, name), ...]
    """

    conn = verbindung()      # DB öffnen
    cur = conn.cursor()      # Cursor = "Zeiger" für SQL-Befehle

    cur.execute("SELECT id, name FROM categories ORDER BY name;")  # SQL ausführen
    daten = cur.fetchall()   # Alle Zeilen holen

    conn.close()             # DB schließen (wichtig!)
    return daten


def kategorie_anlegen(name):
    """
    Legt eine neue Kategorie an.
    Wenn sie schon existiert, passiert nichts.

    Rückgabe:
    - id der Kategorie (egal ob neu oder schon vorhanden)
    """

    name = name.strip()  # Leerzeichen vorne/hinten weg
    if name == "":
        return None      # Keine leeren Kategorien

    conn = verbindung()
    cur = conn.cursor()

    try:
        # INSERT versucht einen neuen Datensatz zu speichern
        cur.execute("INSERT INTO categories (name) VALUES (?);", (name,))
        conn.commit()  # Speichern (sonst ist es nach dem Schließen weg)
    except sqlite3.IntegrityError:
        # UNIQUE wurde verletzt -> Kategorie existiert schon -> ist ok
        pass

    # Wir holen jetzt auf jeden Fall die ID der Kategorie
    cur.execute("SELECT id FROM categories WHERE name = ? LIMIT 1;", (name,))
    row = cur.fetchone()

    conn.close()

    if row is None:
        return None
    return int(row[0])


def kategorie_name(category_id):
    """
    Gibt den Namen einer Kategorie anhand der ID zurück.
    Wenn die ID nicht existiert, kommt None zurück.
    """

    conn = verbindung()
    cur = conn.cursor()

    cur.execute("SELECT name FROM categories WHERE id = ? LIMIT 1;", (category_id,))
    row = cur.fetchone()

    conn.close()

    if row is None:
        return None
    return row[0]

