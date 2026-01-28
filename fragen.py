# fragen.py
# Hier sind alle Funktionen rund um Fragen.
# Eine Frage gehört immer zu genau einer Kategorie (category_id).

import os           # Für EDITOR-Variable (z.B. nvim)
import subprocess   # Um nvim zu starten
import tempfile     # Für eine temporäre Datei zum Editieren

from datenbank import verbindung


def fragen_von_kategorie(category_id):
    """
    Gibt alle Fragen einer Kategorie zurück.
    Rückgabe: Liste von (id, question_text)
    """

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, question_text FROM questions WHERE category_id = ? ORDER BY id;",
        (category_id,),
    )
    daten = cur.fetchall()

    conn.close()
    return daten


def frage_holen(question_id):
    """
    Holt eine Frage aus der DB.
    Rückgabe: (id, question_text, solution, category_id) oder None
    """

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, question_text, solution, category_id FROM questions WHERE id = ? LIMIT 1;",
        (question_id,),
    )
    row = cur.fetchone()

    conn.close()
    return row  # row ist None, wenn es die ID nicht gibt


def frage_anlegen(question_text, solution, category_id):
    """
    Legt eine neue Frage an.
    Rückgabe: neue Frage-ID (int)
    """

    question_text = question_text.strip()
    solution = (solution or "").strip()

    if question_text == "":
        return None

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO questions (question_text, solution, category_id) VALUES (?, ?, ?);",
        (question_text, solution, category_id),
    )

    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return int(new_id)


def frage_update(question_id, new_question_text, new_solution):
    """
    Aktualisiert eine bestehende Frage (Text + Lösung).
    """

    new_question_text = new_question_text.strip()
    new_solution = (new_solution or "").strip()

    if new_question_text == "":
        return False

    conn = verbindung()
    cur = conn.cursor()

    cur.execute(
        "UPDATE questions SET question_text = ?, solution = ? WHERE id = ?;",
        (new_question_text, new_solution, question_id),
    )

    conn.commit()
    conn.close()
    return True


def _parse_editor_text(text):
    """
    Wir verwenden dieses einfache Format:

    <Frage>
    ---
    <Lösung>

    Zeilen, die mit # anfangen, werden ignoriert.
    """

    lines = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        lines.append(line)

    cleaned = "\n".join(lines).strip("\n")

    # Wir verlangen eine Trennlinie, damit wir Frage/Lösung sauber trennen können.
    if "\n---\n" not in cleaned:
        return None, None

    q_part, s_part = cleaned.split("\n---\n", 1)
    q = q_part.strip()
    s = s_part.strip()

    if q == "":
        return None, None

    return q, s


def frage_bearbeiten_mit_editor(question_id):
    """
    Öffnet nvim (oder $EDITOR) mit einer temporären Datei.
    Nach dem Speichern wird die Frage in der DB aktualisiert.

    Rückgabe:
    - True wenn gespeichert wurde
    - False bei Abbruch/Fehler
    """

    row = frage_holen(question_id)
    if row is None:
        print("Diese Frage-ID gibt es nicht.")
        return False

    _, qtext, sol, cat_id = row
    sol = sol or ""  # falls NULL in DB

    header = (
        f"# Frage bearbeiten (ID {question_id}, Kategorie {cat_id})\n"
        "# Format:\n"
        "#   <Frage>\n"
        "#   ---\n"
        "#   <Lösung>\n"
        "# Zeilen mit # werden ignoriert.\n"
        "#\n"
    )

    initial = f"{qtext.strip()}\n---\n{str(sol).strip()}\n"

    editor = os.getenv("EDITOR", "nvim")

    # Temporäre Datei anlegen
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=f"_frage_{question_id}.txt") as tf:
        tf.write(header)
        tf.write(initial)
        filename = tf.name

    try:
        # Editor öffnen (blockierend)
        result = subprocess.run([editor, filename])
        if result.returncode != 0:
            print("Editor wurde abgebrochen. Keine Änderungen übernommen.")
            return False

        # Datei nach dem Editieren wieder einlesen
        with open(filename, "r", encoding="utf-8", errors="replace") as f:
            new_text = f.read()

        new_q, new_s = _parse_editor_text(new_text)
        if new_q is None:
            print("Formatfehler: Trennlinie '---' fehlt oder Frage ist leer.")
            return False

        # Nur speichern, wenn sich wirklich etwas geändert hat
        if new_q.strip() == qtext.strip() and new_s.strip() == str(sol).strip():
            print("Keine Änderungen erkannt.")
            return False

        frage_update(question_id, new_q, new_s)
        print("✅ Frage gespeichert.")
        return True

    finally:
        # Temp-Datei löschen (egal ob Erfolg oder nicht)
        try:
            os.remove(filename)
        except OSError:
            pass

