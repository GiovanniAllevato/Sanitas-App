from flask import Flask, request, jsonify
import sqlite3
from flasgger import Swagger
from flask_cors import CORS
from functools import wraps
import sys
import jwt
from datetime import datetime, timedelta

print("PYTHON IN USO:", sys.executable)

app = Flask(__name__)
Swagger(app)
CORS(app)
app.config["SECRET_KEY"] = "sanitas_secret_key_2026"


def init_db():
    conn = sqlite3.connect("pazienti.db")
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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split(" ")
            if len(parts) == 2:
                token = parts[1]

        if not token:
            return jsonify({"error": "Token mancante"}), 401

        try:
            jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token scaduto"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token non valido"}), 401

        return f(*args, **kwargs)

    return decorated


def ruolo_richiesto(*ruoli_ammessi):
    """Decoratore che verifica che l'utente abbia uno dei ruoli specificati."""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            try:
                payload = jwt.decode(
                    token, app.config["SECRET_KEY"], algorithms=["HS256"]
                )
            except:
                return jsonify({"error": "Token non valido"}), 401
            if payload.get("ruolo") not in ruoli_ammessi:
                return jsonify({"error": "Accesso negato: permessi insufficienti"}), 403
            return f(*args, **kwargs)

        return decorated

    return decorator


def get_db_connection():
    conn = sqlite3.connect("pazienti.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
@token_required
def home():
    return "API clinica attiva"


@app.route("/pazienti", methods=["GET"])
@token_required
def get_pazienti():
    conn = get_db_connection()
    pazienti = conn.execute("SELECT * FROM pazienti").fetchall()
    conn.close()

    return jsonify([dict(p) for p in pazienti])


@app.route("/pazienti", methods=["POST"])
@token_required
def add_paziente():
    """
    Aggiungere un nuovo paziente
    ---
    tags:
        - Pazienti
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
                nome:
                    type: string
                    example: Mario
                cognome:
                    type: string
                    example: Rossi
    responses:
        200:
            description: Paziente aggiunto con successo
    """
    data = request.json

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO pazienti (nome, cognome) VALUES (?, ?)",
        (data["nome"], data["cognome"]),
    )
    conn.commit()
    conn.close()

    return jsonify({"messaggio": "Paziente aggiunto"}), 201


@app.route("/pazienti/<int:id>", methods=["DELETE"])
@token_required
def elimina_paziente(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM pazienti WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"messaggio": "Paziene eliminato"}), 200


@app.route("/pazienti/<int:id>", methods=["PUT"])
@token_required
def update_paziente(id):
    data = request.get_json()
    nome = data.get("nome")
    cognome = data.get("cognome")

    if not nome or not cognome:
        return jsonify({"error": "Campi obbligatori mancanti"}), 400

    conn = get_db_connection()
    paziente = conn.execute("SELECT id FROM pazienti WHERE id = ?", (id,)).fetchone()
    if paziente is None:
        conn.close()
        return jsonify({"error": "Paziente non trovato"}), 404

    conn.execute(
        "UPDATE pazienti SET nome = ?, cognome = ? WHERE id = ?", (nome, cognome, id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Paziente aggiornato con successo"}), 200


@app.route("/login", methods=["POST"])
def login():
    """
    Login utente
    ---
    tags:
      - Autenticazione
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: password
    responses:
      200:
        description: Login riuscito
      401:
        description: Credenziali non valide
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM utenti WHERE username = ? AND password = ?", (username, password)
    ).fetchone()
    conn.close()

    if user is None:
        return jsonify({"error": "Credenziali non valide"}), 401

    token = jwt.encode(
        {
            "sub": username,
            "ruolo": user["ruolo"],
            "exp": datetime.utcnow() + timedelta(hours=1),
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    return jsonify({"token": token, "ruolo": user["ruolo"]})


@app.route("/medici", methods=["POST"])
@token_required
def add_medico():
    """
    Aggiungere un nuovo medico
    ---
    tags:
        - Medici
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
                nome:
                    type: string
                    example: Luca
                cognome:
                    type: string
                    example: Bianchi
    responses:
        200:
            description: Medico aggiunto con successo
    """
    dati = request.get_json()

    nome = dati.get("nome")
    cognome = dati.get("cognome")
    specializzazione = dati.get("specializzazione")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO medici (nome, cognome, specializzazione) VALUES (?, ?, ?)",
        (nome, cognome, specializzazione),
    )

    conn.commit()
    conn.close()

    return jsonify({"messaggio": "Medico aggiunto"}), 201


@app.route("/medici", methods=["GET"])
@token_required
def get_medici():

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    medici = cursor.execute("SELECT * FROM medici").fetchall()

    conn.close()

    return jsonify([dict(m) for m in medici])


@app.route("/medici/<int:id>", methods=["DELETE"])
@token_required
def elimina_medici(id):

    conn = get_db_connection()

    conn.execute("DELETE FROM medici WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"messaggio": "Medico eliminato"}), 200


@app.route("/medici/<int:id>", methods=["PUT"])
@token_required
def update_medico(id):
    data = request.get_json()
    nome = data.get("nome")
    cognome = data.get("cognome")
    specializzazione = data.get("specializzazione")

    if not nome or not cognome or not specializzazione:
        return jsonify({"error": "Campi obbligatori mancanti"}), 400

    conn = get_db_connection()
    medico = conn.execute("SELECT id FROM medici WHERE id = ?", (id,)).fetchone()
    if medico is None:
        conn.close()
        return jsonify({"error": "Medico non trovato"}), 404

    conn.execute(
        "UPDATE medici SET nome = ?, cognome = ?, specializzazione = ? WHERE id = ?",
        (nome, cognome, specializzazione, id),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Medico aggiornato con successo"}), 200


@app.route("/visite", methods=["POST"])
@token_required
def add_visita():
    """
    Registra una nuova visita
    ---
    tags:
        - Visite
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
                paziente_id:
                    type: integer
                    example: 1
                medico_id:
                    type: integer
                    example: 1
                data_visita:
                    type: string
                    example: 2026-04-01
                diagnosi:
                    type: string
                    example: Controllo cardiologico
    responses:
        200:
            description: Visita registrata con successo
        404:
            description: Paziente o medico non trovato
    """

    dati = request.get_json()

    paziente_id = dati.get("paziente_id")
    medico_id = dati.get("medico_id")
    data_visita = dati.get("data_visita")
    diagnosi = dati.get("diagnosi")

    conn = get_db_connection()
    cursor = conn.cursor()

    # controllo paziente
    cursor.execute("SELECT id FROM pazienti WHERE id = ?", (paziente_id,))
    paziente = cursor.fetchone()

    # controllo medico
    cursor.execute("SELECT id FROM medici WHERE id = ?", (medico_id,))
    medico = cursor.fetchone()

    if not paziente:
        conn.close()
        return jsonify({"errore": "Paziente non trovato"}), 404

    if not medico:
        conn.close()
        return jsonify({"errore": "Medico non trovato"}), 404

    # inserimento visita
    cursor.execute(
        "INSERT INTO visite(paziente_id, medico_id, data_visita, diagnosi) VALUES (?,?,?,?)",
        (paziente_id, medico_id, data_visita, diagnosi),
    )

    conn.commit()
    conn.close()

    return jsonify({"messaggio": "Visita registrata"}), 201


@app.route("/visite", methods=["GET"])
@token_required
def get_visite():
    """
    Restituisce la lista delle visite
    ---
    tags:
        - Visite
    responses:
        200:
            description: Lista delle visite
    """

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    visite = cursor.execute(
        """
    SELECT
        visite.id,
        visite.paziente_id,
        visite.medico_id,
        pazienti.nome || ' ' || pazienti.cognome AS paziente,
        medici.nome || ' ' || medici.cognome AS medico,
        visite.data_visita,
        visite.diagnosi
    FROM visite
    JOIN pazienti ON visite.paziente_id = pazienti.id
    JOIN medici ON visite.medico_id = medici.id
    ORDER BY data_visita DESC
    """
    ).fetchall()

    conn.close()

    return jsonify([dict(v) for v in visite])


@app.route("/visite/<int:id>", methods=["DELETE"])
@token_required
def elimina_visita(id):

    conn = get_db_connection()

    conn.execute("DELETE FROM visite WHERE id =?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"messaggio": "Visita eliminata"})


@app.route("/visite/<int:id>", methods=["PUT"])
@token_required
def update_visita(id):
    data = request.get_json()
    paziente_id = data.get("paziente_id")
    medico_id = data.get("medico_id")
    data_visita = data.get("data_visita")
    diagnosi = data.get("diagnosi")

    if not all([paziente_id, medico_id, data_visita, diagnosi]):
        return jsonify({"error": "Campi obbligatori mancanti"}), 400

    conn = get_db_connection()
    visita = conn.execute("SELECT id FROM visite WHERE id = ?", (id,)).fetchone()
    if visita is None:
        conn.close()
        return jsonify({"error": "Visita non trovata"}), 404

    conn.execute(
        "UPDATE visite SET paziente_id = ?, medico_id = ?, data_visita = ?, diagnosi = ? WHERE id = ?",
        (paziente_id, medico_id, data_visita, diagnosi, id),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Visita aggiornata con successo"}), 200


@app.route("/utenti", methods=["GET"])
@token_required
@ruolo_richiesto("admin")
def get_utenti():
    conn = get_db_connection()
    utenti = conn.execute("SELECT id, username, ruolo FROM utenti").fetchall()
    conn.close()
    return jsonify([dict(u) for u in utenti]), 200


@app.route("/utenti", methods=["POST"])
@token_required
@ruolo_richiesto("admin")
def crea_utente():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    ruolo = data.get("ruolo", "medico")  # default: medico

    if ruolo not in ("admin", "medico", "receptionist"):
        return jsonify({"error": "Ruolo non valido"}), 400
    if not username or not password:
        return jsonify({"error": "Campi obbligatori mancanti"}), 400

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO utenti (username, password, ruolo) VALUES (?, ?, ?)",
            (username, password, ruolo),
        )
        conn.commit()
    except Exception:
        conn.close()
        return jsonify({"error": "Username già esistente"}), 409
    conn.close()
    return jsonify({"message": "Utente creato con successo"}), 201


@app.route("/utenti/<int:id>", methods=["DELETE"])
@token_required
@ruolo_richiesto("admin")
def elimina_utente(id):
    conn = get_db_connection()
    utente = conn.execute("SELECT id FROM utenti WHERE id = ?", (id,)).fetchone()
    if utente is None:
        conn.close()
        return jsonify({"error": "Utente non trovato"}), 404
    conn.execute("DELETE FROM utenti WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Utente eliminato con successo"}), 200


print("\nAPI disponibili:\n")

for rule in app.url_map.iter_rules():
    print(f"{rule.methods} {rule}")

if __name__ == "__main__":
    app.run(debug=False)
