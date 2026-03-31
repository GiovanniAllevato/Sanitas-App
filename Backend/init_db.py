import sqlite3

conn = sqlite3.connect("pazienti.db")
cursor = conn.cursor()

# Tabella utenti (login)
cursor.execute("""
CREATE TABLE IF NOT EXISTS utenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
""")

# Tabella pazienti
cursor.execute("""
CREATE TABLE IF NOT EXISTS pazienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    data_nascita TEXT
)
""")

# Tabella medici
cursor.execute("""
CREATE TABLE IF NOT EXISTS medici (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    specializzazione TEXT
)
""")

# Tabella visite
cursor.execute("""
CREATE TABLE IF NOT EXISTS visite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paziente_id INTEGER,
    medico_id INTEGER,
    data_visita TEXT,
    diagnosi TEXT,
    FOREIGN KEY (paziente_id) REFERENCES pazienti(id),
    FOREIGN KEY (medico_id) REFERENCES medici(id)
)
""")

# Creazione utente admin
cursor.execute("""
INSERT INTO utenti (username, password)
VALUES ('admin', 'admin123')
""")

conn.commit()
conn.close()

print("Database clinica creato con successo")
