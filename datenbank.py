# datenbank.py
# Hier kommt ALLES rein, was mit der Datenbank zu tun hat.
# Der Rest vom Programm soll nur Funktionen aus dieser Datei benutzen.

import sqlite3  # Standard-Modul von Python für SQLite (keine Extra-Installation nötig)


DB_DATEI = "datenbank.db"
# Das ist einfach der Dateiname der SQLite-Datenbank.
# Weil alle Dateien im gleichen Ordner liegen, reicht der Name.
# Wichtig: SQLite erstellt diese Datei automatisch, wenn sie noch nicht existiert.


def verbindung():
    """
    Öffnet eine Verbindung zur SQLite-Datenbank und gibt sie zurück.

    Für dumme:
    - Eine Verbindung (conn) ist wie "ein offener Kanal" zur DB.
    - Solange die Verbindung offen ist, können wir SQL-Befehle ausführen.
    - Am Ende muss man die Verbindung wieder schließen: conn.close()
    """

    conn = sqlite3.connect(DB_DATEI)
    # Öffnet datenbank.db (oder erstellt sie, wenn sie nicht existiert)

    conn.execute("PRAGMA foreign_keys = ON;")
    # Für dumme:
    # SQLite ignoriert Foreign Keys oft standardmäßig.
    # Mit diesem Befehl stellen wir sicher, dass Regeln wie
    # "question.category_id muss in categories.id existieren" wirklich gelten.

    return conn
    # Wir geben die Verbindung zurück, damit andere Dateien damit arbeiten können.

