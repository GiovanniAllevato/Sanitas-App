from flask import Flask, request, jsonify
import sqlite3
from flasgger import Swagger
from flask_cors import CORS
from functools import wraps
import sys

print("PYTHON IN USO:", sys.executable)

app = Flask(__name__)
Swagger(app)
CORS(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        token = None
        
        # Legge header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']

            # Formato: Bearer Token
            parts = auth_header.split(" ")

            if len(parts) == 2:
                token = parts[1]
                
        # Se token mancante 
        if not token:
            return jsonify({"messaggio": "Token mancante"}), 401
        
        # Validazione semplice
        if token != "tokensanitas":
            return jsonify({"messaggio": "Token non valido"}), 401
        
        return f(*args, **kwargs)
    
    return decorated

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
        (data["nome"], data["cognome"])
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
              example: admin123
    responses:
      200:
        description: Login riuscito
      401:
        description: Credenziali non valide
    """

    print("DEBUG LOGIN ATTIVO")

    dati = request.get_json()
    print("DATI:", dati)

    username = dati.get("username")
    password = dati.get("password")

    print("USERNAME:", username)
    print("PASSWORD:", password)

    conn = get_db_connection()

    utente = conn.execute(
        "SELECT * FROM utenti WHERE username=? AND password=?",
        (username, password)
    ).fetchone()

    print("RISULTATO:", utente)

    conn.close()

    if utente:
        return jsonify({"success": True, "token": "tokensanitas"})
    else:
        return jsonify({"success": False}), 401
    
print("🔥 LOGIN NUOVO ATTIVO 🔥")

  
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
        (nome, cognome, specializzazione)
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
    
    conn.execute(
        "DELETE FROM medici WHERE id=?",
        (id,)
    )
    
    conn.commit()
    conn.close()

    return jsonify({"messaggio": "Medico eliminato"}), 200

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
        (paziente_id, medico_id, data_visita, diagnosi)
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
    
    visite = cursor.execute("""
    SELECT
        visite.id,
        pazienti.nome || ' ' || pazienti.cognome AS paziente,
        medici.nome || ' ' || medici.cognome AS medico,
        visite.data_visita,
        visite.diagnosi
    FROM visite
    JOIN pazienti ON visite.paziente_id = pazienti.id
    JOIN medici ON visite.medico_id = medici.id
    ORDER BY data_visita DESC
    """).fetchall()
                            
    conn.close()
    
    return jsonify([dict(v) for v in visite])

@app.route("/visite/<int:id>", methods=["DELETE"])
@token_required
def elimina_visita(id):
    
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM visite WHERE id =?",
        (id,)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({"messaggio": "Visita eliminata"})


print("\nAPI disponibili:\n")

for rule in app.url_map.iter_rules():   
    print(f"{rule.methods} {rule}")

if __name__ == "__main__":
    app.run(debug=False)
    
