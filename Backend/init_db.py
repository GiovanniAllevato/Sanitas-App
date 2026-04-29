import sqlite3

conn = sqlite3.connect("pazienti.db")


def init_db():
    conn.execute(
        """CREATE TABLE IF NOT EXISTS pazienti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cognome TEXT NOT NULL
    )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS medici (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cognome TEXT NOT NULL,
        specializzazione TEXT NOT NULL
    )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS visite (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paziente_id INTEGER NOT NULL,
        medico_id INTEGER NOT NULL,
        data_visita TEXT NOT NULL,
        diagnosi TEXT NOT NULL,
        FOREIGN KEY (paziente_id) REFERENCES pazienti(id),
        FOREIGN KEY (medico_id) REFERENCES medici(id)
    )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS utenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        ruolo TEXT NOT NULL DEFAULT 'medico'
    )"""
    )
    existing = conn.execute("SELECT id FROM utenti WHERE username = 'admin'").fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO utenti (username, password, ruolo) VALUES (?, ?, ?)",
            ("admin", "password", "admin"),
        )
    conn.commit()
    conn.close()


init_db()
print("Database clinica creato con successo")
