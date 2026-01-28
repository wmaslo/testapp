# tests.py
# Hier sind alle Funktionen rund um Tests.
#
# Ein "Test" ist z.B. "Schularbeit 1" am Datum X.
# Ein Test hat viele Fragen -> das machen wir über die Tabelle test_questions (m:n)

import os           # Für EDITOR-Variable (z.B. nvim)
import subprocess   # Um nvim zu starten
import tempfile     # Für eine temporäre Datei zum Editieren

from datenbank import verbindung


def alle_tests():
    """
    Gibt alle Tests zurück.
    Rückgabe: Liste von (id, title, test_date)
    """

    conn = verbindung()   # DB öffnen
    cur = conn.cursor()   # Cursor holen

    cur.execute("SELECT id, title, test_date FROM tests ORDER BY id DESC;")
    daten = cur.fetchall()

    conn.close()          # DB wieder schließen
    return daten


def test_holen(test_id):
    """
    Holt einen Test aus der DB.
    Rückgabe: (id, title, test_date) oder None
    """

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, title, test_date FROM tests WHERE id = ? LIMIT 1;",
        (test_id,),
    )
    row = cur.fetchone()

    conn.close()
    return row


def test_anlegen(title, test_date):
    """
    Legt einen neuen Test an und gibt die neue Test-ID zurück.
    """

    title = title.strip()
    if title == "":
        return None

    # test_date darf leer sein -> dann speichern wir NULL
    if test_date is not None:
        test_date = test_date.strip()
        if test_date == "":
            test_date = None

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tests (title, test_date) VALUES (?, ?);",
        (title, test_date),
    )

    new_id = cur.lastrowid  # SQLite gibt uns die neue ID
    conn.commit()
    conn.close()

    return int(new_id)


def test_update(test_id, new_title, new_test_date):
    """
    Aktualisiert Titel und Datum eines Tests.
    """

    new_title = new_title.strip()
    if new_title == "":
        return False

    if new_test_date is not None:
        new_test_date = new_test_date.strip()
        if new_test_date == "":
            new_test_date = None

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        "UPDATE tests SET title = ?, test_date = ? WHERE id = ?;",
        (new_title, new_test_date, test_id),
    )

    conn.commit()
    conn.close()
    return True


def frage_zu_test(test_id, question_id):
    """
    Fügt eine Frage zu einem Test hinzu.

    Wichtig (für dumme):
    - In test_questions ist (test_id, question_id) PRIMARY KEY.
      Das heißt: dieselbe Frage kann nicht doppelt im selben Test sein.
    - Darum verwenden wir INSERT OR IGNORE:
      Wenn es schon existiert, passiert einfach nichts.
    """

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO test_questions (test_id, question_id) VALUES (?, ?);",
        (test_id, question_id),
    )

    conn.commit()
    conn.close()


def fragen_ids_von_test(test_id):
    """
    Gibt die Frage-IDs eines Tests zurück.
    Rückgabe: Liste [1, 5, 9, ...]
    """

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        "SELECT question_id FROM test_questions WHERE test_id = ? ORDER BY question_id;",
        (test_id,),
    )
    rows = cur.fetchall()

    conn.close()

    # rows sieht so aus: [(1,), (5,), (9,)]
    # darum bauen wir eine einfache Liste daraus
    return [int(r[0]) for r in rows]


def test_anzeigen(test_id):
    """
    Gibt einen Test inkl. Fragen aus (für CLI-Ausgabe).
    Rückgabe:
      - test_row: (id, title, test_date) oder None
      - questions: Liste von (id, question_text, solution)
    """

    test_row = test_holen(test_id)
    if test_row is None:
        return None, []

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT q.id, q.question_text, q.solution
        FROM test_questions tq
        JOIN questions q ON q.id = tq.question_id
        WHERE tq.test_id = ?
        ORDER BY q.id;
        """,
        (test_id,),
    )

    questions = cur.fetchall()
    conn.close()

    return test_row, questions


def _parse_id_liste(raw):
    """
    Hilfsfunktion: macht aus "1 3 5" oder "1,3,5" eine Liste [1,3,5]
    - entfernt Duplikate
    - behält Reihenfolge
    """

    raw = raw.replace(",", " ")
    ids = []

    for part in raw.split():
        if part.isdigit():
            ids.append(int(part))

    seen = set()
    out = []
    for x in ids:
        if x not in seen:
            seen.add(x)
            out.append(x)

    return out


def test_fragen_setzen(test_id, neue_frage_ids):
    """
    Setzt die Fragen eines Tests EXAKT auf die übergebene Liste.
    Das heißt:
    - Fragen, die fehlen -> werden hinzugefügt
    - Fragen, die zu viel sind -> werden entfernt
    """

    # 1) Aktueller Zustand
    aktuell = set(fragen_ids_von_test(test_id))
    neu = set(neue_frage_ids)

    # 2) Was muss dazu?
    hinzufuegen = neu - aktuell

    # 3) Was muss weg?
    entfernen = aktuell - neu

    # 4) Änderungen durchführen
    # Hinzufügen
    for qid in hinzufuegen:
        frage_zu_test(test_id, qid)

    # Entfernen
    conn = verbindung()
    cur = conn.cursor()

    for qid in entfernen:
        cur.execute(
            "DELETE FROM test_questions WHERE test_id = ? AND question_id = ?;",
            (test_id, qid),
        )

    conn.commit()
    conn.close()


def test_bearbeiten_mit_editor(test_id):
    """
    Öffnet nvim (oder $EDITOR) mit einer temporären Datei, um den Test zu bearbeiten.

    Wir editieren:
      title: <Titel>
      date: <YYYY-MM-DD>   (optional)
      questions: 1 3 5     (Liste von Frage-IDs, optional)

    Danach wird:
    - tests.title / tests.test_date aktualisiert
    - test_questions passend gesetzt (exakt)

    Rückgabe: True wenn gespeichert, False sonst.
    """

    row = test_holen(test_id)
    if row is None:
        print("Diese Test-ID gibt es nicht.")
        return False

    _, title, test_date = row
    test_date = test_date or ""  # falls NULL in DB

    frage_ids = fragen_ids_von_test(test_id)

    header = (
        f"# Test bearbeiten (ID {test_id})\n"
        "# Format:\n"
        "#   title: <Titel>\n"
        "#   date: <YYYY-MM-DD>     (optional)\n"
        "#   questions: <IDs>       (z.B. 1 3 5, optional)\n"
        "# Zeilen mit # werden ignoriert.\n"
        "#\n"
    )

    initial = (
        f"title: {str(title).strip()}\n"
        f"date: {str(test_date).strip()}\n"
        f"questions: {' '.join(str(x) for x in frage_ids)}\n"
    )

    editor = os.getenv("EDITOR", "nvim")

    # Temp-Datei anlegen
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=f"_test_{test_id}.txt") as tf:
        tf.write(header)
        tf.write(initial)
        filename = tf.name

    try:
        # Editor öffnen
        result = subprocess.run([editor, filename])
        if result.returncode != 0:
            print("Editor wurde abgebrochen. Keine Änderungen übernommen.")
            return False

        # Datei einlesen
        with open(filename, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

        # Kommentarzeilen rausfiltern
        lines = []
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            lines.append(line)

        # Schlüssel:Wert auslesen
        data = {}
        for line in lines:
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            data[key.strip().lower()] = val.strip()

        new_title = data.get("title", "").strip()
        new_date = data.get("date", "").strip()
        new_q_raw = data.get("questions", "").strip()

        if new_title == "":
            print("Fehler: title darf nicht leer sein.")
            return False

        if new_date == "":
            new_date = None  # leer -> NULL

        neue_frage_ids = _parse_id_liste(new_q_raw) if new_q_raw else []

        # Speichern in DB
        test_update(test_id, new_title, new_date)
        test_fragen_setzen(test_id, neue_frage_ids)

        print("✅ Test gespeichert.")
        return True

    finally:
        # Temp-Datei löschen
        try:
            os.remove(filename)
        except OSError:
            pass

