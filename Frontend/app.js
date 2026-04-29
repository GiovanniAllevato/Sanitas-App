const API_URL = "http://127.0.0.1:5000";

window.onload = function () {

    const token = localStorage.getItem("token");

    console.log("TOKEN INDEX:", token);

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    // Mostra il bottone Gestione Utenti solo agli admin
    if (localStorage.getItem("ruolo") === "admin") {
        const btn = document.getElementById("btnUtenti");
        if (btn) btn.style.display = "inline-block";
    }

    if (document.getElementById("tabellaPazienti")) {
        caricaPazienti();
    }

    if (document.getElementById("corpoMedici")) {
        caricaMedici();
    }

    if (document.getElementById("corpoVisite")) {
        caricaVisite();
        caricaPazientiSelect();
        caricaMediciSelect();
    }

};


function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}

function caricaPazienti() {
    authFetch(API_URL + "/pazienti") 
        .then(response => response.json())
        .then(pazienti => {
            const tabella = document.getElementById("corpoPazienti");
            tabella.innerHTML = "";

            pazienti.forEach(p => {
                const row = `
                    <tr>
                        <td>${p.nome}</td>
                        <td>${p.cognome}</td>
                        <td>
                            <button onclick="eliminaPaziente(${p.id})">Elimina</button> <button onclick="modificaPaziente(${p.id}, '${p.nome}', '${p.cognome}')">Modifica</button>
                        </td>
                    </tr>
                    `;
                    tabella.innerHTML += row;
            });
        });
    }

function aggiungiPaziente() {

    console.log("Funzione chiamata");

    const nome = document.getElementById("nome").value;
    const cognome = document.getElementById("cognome").value;

    authFetch(API_URL + "/pazienti", {

        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            nome: nome,
            cognome: cognome
        })

    })
        .then(response => response.json())
        .then(() => {

            alert("Paziente aggiunto con successo");

            // pulizia campi
            document.getElementById("nome").value = "";
            document.getElementById("cognome").value = "";

            caricaPazienti();

        })
        .catch(() =>  {
            alert("Errore durante l'inserimento");
        });
}

function modificaPaziente(id, nomeAttuale, cognomeAttuale) {
    const nuovoNome = prompt('Nuovo nome:', nomeAttuale);
    if (nuovoNome === null) return;
    const nuovoCognome = prompt('Nuovo cognome:', cognomeAttuale);
    if (nuovoCognome === null) return;

    authFetch(API_URL + "/pazienti/" + id, {
        method: 'PUT',
        body: JSON.stringify({ nome: nuovoNome, cognome: nuovoCognome })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.error);
        caricaPazienti(); // ricarica la tabella
    })
    .catch(() => alert('Errore nella modifica'));
}

function eliminaPaziente(id) {

    if (!confirm("Sei sicuro di voler eliminare questo paziente?")) {
        return;
    }

    authFetch(API_URL + "/pazienti/" + id, {

        method: "DELETE"

    })
        .then(response => response.json())
        .then(() => {

            alert("Paziente elimnato con successo");
            caricaPazienti();

        })
        .catch(() => {
            alert("Errore durante l'eliminazione");
        })
}

caricaPazienti();

function caricaMedici() {

    authFetch(API_URL + "/medici")
        .then(response => response.json())
        .then(data => {

            const corpo = document.getElementById("corpoMedici");
            corpo.innerHTML = "";

            data.forEach(medico => {

                const row = `
                    <tr>
                        <td>${medico.nome}</td>
                        <td>${medico.cognome}</td>
                        <td>${medico.specializzazione}</td>
                        <td>
                            <button onclick="eliminaMedico(${medico.id})">Elimina</button>
                            <button onclick="modificaMedico(${medico.id}, '${medico.nome}', '${medico.cognome}', '${medico.specializzazione}')">Modifica</button>
                        </td>
                    </tr>
                `;

                corpo.innerHTML += row;

            });
        });
}

caricaMedici();

function aggiungiMedico() {

    const nome = document.getElementById("nome").value;
    const cognome = document.getElementById("cognome").value;
    const specializzazione = document.getElementById("specializzazione").value;

    authFetch(API_URL + "/medici", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            nome: nome,
            cognome: cognome,
            specializzazione: specializzazione,
        })

    })
        .then(response => response.json())
        .then(() => {

            caricaMedici();

        });

}

function eliminaMedico(id) {

    authFetch(API_URL + "/medici/" + id, {

        method: "DELETE"

    })
    .then(response => response.json())
    .then(() => {

        alert("Medico eliminato");

        caricaMedici();

    });
}

function modificaMedico(id, nomeAttuale, cognomeAttuale, specializzazioneAttuale) {
    const nuovoNome = prompt('Nuovo nome:', nomeAttuale);
    if (nuovoNome === null) return;
    const nuovoCognome = prompt('Nuovo cognome:', cognomeAttuale);
    if (nuovoCognome === null) return;
    const nuovaSpecializzazione = prompt('Nuova specializzazione:', specializzazioneAttuale);
    if (nuovaSpecializzazione === null) return;

    authFetch(API_URL + "/medici/" + id, {
        method: 'PUT',
        body: JSON.stringify({
            nome: nuovoNome,
            cognome: nuovoCognome,
            specializzazione: nuovaSpecializzazione
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.error);
        caricaMedici();
    })
    .catch(() => alert('Errore nella modifica'));
}


function caricaVisite() {

    authFetch(API_URL + "/visite")
        .then(response => response.json())
        .then(data => {

            const corpo = document.getElementById("corpoVisite");

            corpo.innerHTML = "";

            data.forEach(visita => {

                const riga = document.createElement("tr");

                riga.innerHTML = `
                <td>${visita.paziente}</td>
                <td>${visita.medico}</td>
                <td>${visita.data_visita}</td>
                <td>${visita.diagnosi}</td>
                <td>
                    <button onclick="eliminaVisita(${visita.id})">Elimina</button>
                    <button onclick="modificaVisita(${visita.id}, ${visita.paziente_id}, ${visita.medico_id}, '${visita.data_visita}', '${visita.diagnosi}')">Modifica</button>
                </td>
                   ` ;

                corpo.appendChild(riga);

            });

        });

}

function caricaPazientiSelect() {

    authFetch(API_URL + "/pazienti")
        .then(response => response.json())
        .then(data => {

            const select = document.getElementById("pazienteSelect");

            select.innerHTML = '<option value="">-- Seleziona paziente --</option>';

            data.forEach(paziente => {

                const option = document.createElement("option");

                option.value = paziente.id;
                option.textContent = paziente.nome + " " + paziente.cognome;

                select.appendChild(option);

            })

        })

}

function caricaMediciSelect() {
    authFetch(API_URL + "/medici")
        .then(response => response.json())
        .then(data => {

            const select = document.getElementById("medicoSelect");

            select.innerHTML = '<option value="">-- Seleziona medico --</option>';

            data.forEach(medico => {

                const option = document.createElement("option");

                option.value = medico.id;

                option.textContent =
                    medico.nome + " " +
                    medico.cognome +
                    " (" + medico.specializzazione + ")";

                select.appendChild(option);

            })

        })

}

function aggiungiVisita() {

    const paziente_id = document.getElementById("pazienteSelect").value;
    const medico_id = document.getElementById("medicoSelect").value;
    const data_visita = document.getElementById("dataVisita").value;
    const diagnosi = document.getElementById("diagnosi").value;


    if (!paziente_id) {
        alert("Seleziona un paziente");
        return;
    }

    if (!medico_id) {
        alert("Seleziona un medico");
        return;
    }

    if (!data_visita) {
        alert("Inserisci una data");
        return;
    }

    if (!diagnosi || diagnosi.trim() === "") {
        alert("Inserisci una diagnosi");
        return;
    }


    authFetch(API_URL + "/visite", {

        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            paziente_id,
            medico_id,
            data_visita,
            diagnosi
        })

    })
    .then(response => response.json())
    .then(() => {

        alert("Visita registrata con successo");

        // pulizia campi
        document.getElementById("diagnosi").value = "";

        caricaVisite();

    })
    .catch(() => {
        alert("Errore durante il salvataggio");
    });
}

function eliminaVisita(id) {

    authFetch(API_URL + "/visite/" + id, {

        method: "DELETE"

    })
        .then(response => response.json())
        .then(() => {

            alert("Visita eliminata");

            caricaVisite();

        });

}

function modificaVisita(id, pazienteIdAttuale, medicoIdAttuale, dataAttuale, diagnosiAttuale) {
    const nuovaData = prompt('Nuova data visita (YYYY-MM-DD):', dataAttuale);
    if (nuovaData === null) return;
    const nuovaDiagnosi = prompt('Nuova diagnosi:', diagnosiAttuale);
    if (nuovaDiagnosi === null) return;

    // Per semplicità manteniamo paziente e medico invariati;
    // l'utente può cambiare solo data e diagnosi tramite prompt
    authFetch(API_URL + "/visite/" + id, {
        method: 'PUT',
        body: JSON.stringify({
            paziente_id: pazienteIdAttuale,
            medico_id: medicoIdAttuale,
            data_visita: nuovaData,
            diagnosi: nuovaDiagnosi
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.error);
        caricaVisite();
    })
    .catch(() => alert('Errore nella modifica'));
}


function getAuthHeaders() {
    const token = localStorage.getItem("token");

    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    };
}

function handleAuthError (response) {
    if (response.status === 401) {
        console.log("TOKEN NON VALIDO -> LOGOUT");
        localStorage.removeItem("token");
        window.location.href = "login.html";
    }
    return response;
}

function authFetch(url, options = {}) {
    return fetch(url, {
        ...options,
        headers: {
            ...getAuthHeaders(),
            ...(options.headers || {})
        }
    })
    .then(handleAuthError);
}
