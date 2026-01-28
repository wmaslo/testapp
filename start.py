# start.py
# Das ist der Startpunkt vom Programm.
#
# Für dumme:
# - Wenn du "python start.py" ausführst, startet dieses Menü.
# - Das Menü ruft Funktionen aus kategorien.py / fragen.py / tests.py auf.

from kategorien import alle_kategorien, kategorie_anlegen, kategorie_name
from fragen import (
    fragen_von_kategorie,
    frage_anlegen,
    frage_bearbeiten_mit_editor,
)
from tests import (
    alle_tests,
    test_anlegen,
    test_bearbeiten_mit_editor,
    test_anzeigen,
    frage_zu_test,
)

def eingabe(text):
    """
    Eingabe lesen und kaputte Unicode-Zeichen ersetzen (damit SQLite nicht crasht).
    """
    s = input(text)
    s = s.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
    return s.strip()


def eingabe_int(text):
    """
    Wie eingabe(), aber zwingt den User eine Zahl einzugeben.
    """
    while True:
        raw = eingabe(text)
        if raw.isdigit():
            return int(raw)
        print("Bitte eine Zahl eingeben.")


def menu_anzeigen():
    """
    Zeigt das Menü an.
    """
    print(
        "\n=== TestApp (minimal) ===\n"
        "1) Kategorien anzeigen\n"
        "2) Kategorie anlegen\n"
        "3) Fragen einer Kategorie anzeigen\n"
        "4) Frage anlegen\n"
        "5) Frage bearbeiten (öffnet nvim)\n"
        "6) Tests anzeigen\n"
        "7) Test anlegen\n"
        "8) Test bearbeiten (öffnet nvim)\n"
        "9) Fragen zu Test hinzufügen\n"
        "10) Test anzeigen (mit Fragen)\n"
        "0) Ende\n"
    )


def aktion_kategorien_anzeigen():
    kats = alle_kategorien()
    if not kats:
        print("Keine Kategorien vorhanden.")
        return
    print("\nKategorien:")
    for cid, name in kats:
        print(f"  {cid}: {name}")


def aktion_kategorie_anlegen():
    name = eingabe("Name der neuen Kategorie: ")
    cid = kategorie_anlegen(name)
    if cid is None:
        print("Keine Kategorie angelegt.")
        return
    print(f"✅ Kategorie '{name}' hat ID {cid}")


def aktion_fragen_anzeigen():
    aktion_kategorien_anzeigen()
    cid = eingabe("Kategorie-ID (leer=Abbruch): ")
    if cid == "":
        return
    if not cid.isdigit():
        print("Ungültige ID.")
        return

    cid = int(cid)
    name = kategorie_name(cid)
    if name is None:
        print("Diese Kategorie-ID gibt es nicht.")
        return

    fragen = fragen_von_kategorie(cid)
    print(f"\nFragen in Kategorie '{name}':")
    if not fragen:
        print("  (keine)")
        return

    for qid, text in fragen:
        print(f"  {qid}: {text}")


def aktion_frage_anlegen():
    aktion_kategorien_anzeigen()
    cid = eingabe("Kategorie-ID für die Frage (leer=Abbruch): ")
    if cid == "":
        return
    if not cid.isdigit():
        print("Ungültige ID.")
        return
    cid = int(cid)

    if kategorie_name(cid) is None:
        print("Diese Kategorie-ID gibt es nicht.")
        return

    text = eingabe("Fragetext: ")
    loesung = eingabe("Lösung (optional): ")

    qid = frage_anlegen(text, loesung, cid)
    if qid is None:
        print("Keine Frage angelegt.")
        return

    print(f"✅ Frage angelegt, ID: {qid}")


def aktion_frage_bearbeiten():
    qid = eingabe("Frage-ID bearbeiten (leer=Abbruch): ")
    if qid == "":
        return
    if not qid.isdigit():
        print("Ungültige ID.")
        return
    frage_bearbeiten_mit_editor(int(qid))


def aktion_tests_anzeigen():
    tests = alle_tests()
    if not tests:
        print("Keine Tests vorhanden.")
        return

    print("\nTests (neueste zuerst):")
    for tid, title, date in tests:
        d = date if date else "-"
        print(f"  {tid}: {title} ({d})")


def aktion_test_anlegen():
    title = eingabe("Test-Titel: ")
    date = eingabe("Test-Datum (YYYY-MM-DD, optional): ")
    if date == "":
        date = None

    tid = test_anlegen(title, date)
    if tid is None:
        print("Kein Test angelegt.")
        return

    print(f"✅ Test angelegt, ID: {tid}")


def aktion_test_bearbeiten():
    aktion_tests_anzeigen()
    tid = eingabe("Test-ID bearbeiten (leer=Abbruch): ")
    if tid == "":
        return
    if not tid.isdigit():
        print("Ungültige ID.")
        return
    test_bearbeiten_mit_editor(int(tid))


def aktion_fragen_zu_test():
    """
    Für dumme:
    - Du wählst einen Test
    - Du gibst Frage-IDs ein
    - Wir hängen diese Fragen an den Test an
    """

    aktion_tests_anzeigen()
    tid = eingabe("Test-ID auswählen (leer=Abbruch): ")
    if tid == "":
        return
    if not tid.isdigit():
        print("Ungültige ID.")
        return
    tid = int(tid)

    # Fragenliste anzeigen hilft beim Auswählen
    print("\nTipp: Zeige zuerst Fragen einer Kategorie (Menüpunkt 3).")

    raw = eingabe("Frage-IDs (z.B. 1 3 5 oder 1,3,5): ")
    raw = raw.replace(",", " ")
    parts = raw.split()

    if not parts:
        print("Keine IDs eingegeben.")
        return

    for p in parts:
        if not p.isdigit():
            print(f"Ungültige ID übersprungen: {p}")
            continue
        frage_zu_test(tid, int(p))

    print("✅ Fragen zum Test hinzugefügt.")


def aktion_test_anzeigen_mit_fragen():
    aktion_tests_anzeigen()
    tid = eingabe("Test-ID anzeigen (leer=Abbruch): ")
    if tid == "":
        return
    if not tid.isdigit():
        print("Ungültige ID.")
        return

    tid = int(tid)
    test_row, fragen = test_anzeigen(tid)

    if test_row is None:
        print("Test nicht gefunden.")
        return

    _, title, date = test_row
    d = date if date else "-"

    print(f"\nTest: {title} ({d})")
    print("Fragen:")

    if not fragen:
        print("  (keine)")
        return

    for qid, qtext, sol in fragen:
        print(f"  {qid}: {qtext}")
        # Lösung lassen wir absichtlich aus (kann man später aktivieren)
        # print(f"     Lösung: {sol}")


def main():
    """
    Hauptschleife vom Menü.
    """
    while True:
        menu_anzeigen()
        choice = eingabe("Auswahl: ")

        if choice == "0":
            print("Tschüss.")
            return

        elif choice == "1":
            aktion_kategorien_anzeigen()
        elif choice == "2":
            aktion_kategorie_anlegen()
        elif choice == "3":
            aktion_fragen_anzeigen()
        elif choice == "4":
            aktion_frage_anlegen()
        elif choice == "5":
            aktion_frage_bearbeiten()
        elif choice == "6":
            aktion_tests_anzeigen()
        elif choice == "7":
            aktion_test_anlegen()
        elif choice == "8":
            aktion_test_bearbeiten()
        elif choice == "9":
            aktion_fragen_zu_test()
        elif choice == "10":
            aktion_test_anzeigen_mit_fragen()
        else:
            print("Ungültige Auswahl.")


if __name__ == "__main__":
    # Für dumme:
    # Ctrl+C soll das Programm sauber beenden, ohne Traceback.
    try:
        main()
    except KeyboardInterrupt:
        print("\nAbbruch (Ctrl+C).")

