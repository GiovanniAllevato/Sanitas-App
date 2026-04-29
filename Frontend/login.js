const API_URL = "http://127.0.0.1:5000";

window.onload = function () {
    const token = localStorage.getItem("token");

    console.log("TOKEN LOGIN:", token);

    if (token) {
        window.location.href = "index.html";
    }
};

function login() {

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
        .then(response => {
            console.log("RESPONSE:", response);
            return response.json();
        })
        .then(data => {
            console.log("DATA:", data);

            if (data.token) {
                localStorage.setItem("token", data.token);
                localStorage.setItem("ruolo", data.ruolo);
                window.location.href = "index.html";
            } else {
                document.getElementById("errore").innerText = data.error || "Login fallito";
            }
        })
        .catch(error => {
            console.error("ERRORE:", error);
            document.getElementById("errore").innerText = "Errore di connessione";
        });

}