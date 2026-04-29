import sqlite3

conn = sqlite3.connect("pazienti.db")
try:
    rows = conn.execute("SELECT * FROM utenti").fetchall()
    print("Utenti trovati:", rows)
except Exception as e:
    print("ERRORE:", e)
conn.close()
