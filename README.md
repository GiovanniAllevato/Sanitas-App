# Sanitas App

Applicazione web full-stack API-based per la gestione digitale di pazienti, medici e visite in ambito sanitario.

Sviluppata come project work per il corso di Informatica per le Aziende Digitali (L-31) – Università Telematica Pegaso.

---

## Tecnologie utilizzate

| Componente | Tecnologie |
|---|---|
| Backend | Python 3, Flask, SQLite, PyJWT, Flasgger, Flask-CORS |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Versionamento | Git, GitHub |

---

## Struttura del progetto

Sanitas-App/
├── Backend/
│   ├── app.py          # Applicazione Flask – endpoint REST
│   ├── init_db.py      # Inizializzazione database SQLite
│   └── pazienti.db     # Database (generato automaticamente)
├── Frontend/
│   ├── index.html      # Dashboard principale
│   ├── login.html      # Pagina di login
│   ├── pazienti.html   # Gestione pazienti
│   ├── medici.html     # Gestione medici
│   ├── visite.html     # Gestione visite
│   ├── utenti.html     # Gestione utenti (solo admin)
│   ├── app.js          # Logica JavaScript condivisa
│   ├── login.js        # Logica login
│   └── style.css       # Stile dell'interfaccia
└── README.md

---

## Avvio del progetto

### Prerequisiti
- Python 3.x installato
- pip

### 1. Installare le dipendenze

```bash
cd Backend
pip install flask flask-cors flasgger pyjwt
```

### 2. Inizializzare il database

```bash
python init_db.py
```

Questo comando crea il file `pazienti.db` con le tabelle necessarie e inserisce l'utente admin di default.

### 3. Avviare il backend

```bash
python app.py
```

Il server Flask sarà disponibile su `http://127.0.0.1:5000`

### 4. Aprire il frontend

Aprire il file `Frontend/login.html` nel browser, oppure usare l'estensione **Live Server** di Visual Studio Code per servirlo localmente.

---

## Credenziali di default

| Campo | Valore |
|---|---|
| Username | `admin` |
| Password | `password` |

---

## Funzionalità principali

- Autenticazione con token JWT e gestione della sessione
- Gestione completa (CRUD) di pazienti, medici e visite
- Modifica dei record esistenti tramite endpoint PUT
- Gestione utenti con tre ruoli: **admin**, **medico**, **receptionist**
- Accesso agli endpoint di amministrazione riservato al ruolo admin
- Interfaccia aggiornata dinamicamente senza ricaricare la pagina
- Documentazione automatica delle API tramite Swagger (`http://127.0.0.1:5000/apidocs`)

---

## Documentazione API

La documentazione interattiva degli endpoint è disponibile all'indirizzo:

http://127.0.0.1:5000/apidocs

Generata automaticamente da Flasgger (Swagger UI).
