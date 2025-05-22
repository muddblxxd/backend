let fin = false;
let essaisRestants = 5;

async function demarrerPartie() {
    await fetch("http://127.0.0.1:8000/api/v1/motdevine/nouveau");
    document.getElementById("game").innerHTML = "";
    document.getElementById("message").textContent = "Devinez le mot de 5 lettres. Vous avez 5 essais.";
    essaisRestants = 5;
    fin = false;
}

async function envoyerEssai() {
    if (fin || essaisRestants <= 0) return;

    const input = document.getElementById("guessInput");
    const mot = input.value.trim().toUpperCase();

    if (mot.length !== 5) {
        document.getElementById("message").textContent = "Veuillez entrer un mot de 5 lettres.";
        return;
    }

    const res = await fetch(`http://127.0.0.1:8000/api/v1/motdevine/verifier?mot=${mot}`);
    const data = await res.json();

    if (data.erreur) {
        document.getElementById("message").textContent = data.erreur;
        return;
    }

    const ligne = document.createElement("div");
    for (const lettreInfo of data.mot_verifie) {
        const span = document.createElement("span");
        span.textContent = lettreInfo.lettre;
        span.className = `lettre ${lettreInfo.couleur}`; // .vert, .jaune, .gris
        span.style.margin = "5px";
        ligne.appendChild(span);
    }

    document.getElementById("game").appendChild(ligne);
    input.value = "";
    essaisRestants--;

    const gagne = data.mot_verifie.every(l => l.couleur === "vert");
    if (gagne) {
        document.getElementById("message").textContent = "Félicitations ! Vous avez trouvé le mot.";
        fin = true;
    } else if (essaisRestants <= 0) {
        document.getElementById("message").textContent = "Dommage, vous avez épuisé vos essais. Cliquez sur 'Nouvelle Partie' pour réessayer.";
        fin = true;
    }
}
