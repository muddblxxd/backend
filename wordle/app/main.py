from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import random

application = FastAPI()

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre selon vos besoins en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Liste de mots possibles (5 lettres)
liste_mots = ["ARBRE", "MAISON", "CHIEN", "TABLE", "FLEUR", "LIVRE", "PORTE", "CHAIR", "VITES", "GLACE"]

# Mot choisi pour la partie en cours
mot_a_deviner = ""

@application.get("/api/v1/motdevine/nouveau")
async def demarrer_nouvelle_partie():
    global mot_a_deviner
    mot_a_deviner = random.choice(liste_mots)
    return {"message": "Nouvelle partie commencée."}

@application.get("/api/v1/motdevine/verifier")
async def verifier_mot(
    mot: str = Query(..., min_length=5, max_length=5)
):
    global mot_a_deviner
    mot = mot.upper()

    if not mot_a_deviner:
        return JSONResponse(
            status_code=400,
            content={"erreur": "Aucune partie en cours. Veuillez démarrer une nouvelle partie."}
        )

    resultat = []
    lettres_restantes = list(mot_a_deviner)

    # Première passe : lettres bien placées
    for i in range(5):
        if mot[i] == mot_a_deviner[i]:
            resultat.append({"lettre": mot[i], "couleur": "vert"})
            lettres_restantes[i] = None
        else:
            resultat.append({"lettre": mot[i], "couleur": "gris"})

    # Deuxième passe : lettres mal placées (présentes mais mal placées)
    for i in range(5):
        if resultat[i]["couleur"] == "gris" and mot[i] in lettres_restantes:
            resultat[i]["couleur"] = "jaune"
            lettres_restantes[lettres_restantes.index(mot[i])] = None

    return {"mot_verifie": resultat}
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import random

application = FastAPI()

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre selon vos besoins en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Liste de mots possibles (5 lettres)
liste_mots = ["ARBRE", "MAISON", "CHIEN", "TABLE", "FLEUR", "LIVRE", "PORTE", "CHAIR", "VITES", "GLACE"]

# Mot choisi pour la partie en cours
mot_a_deviner = ""

@application.get("/api/v1/motdevine/nouveau")
async def demarrer_nouvelle_partie():
    global mot_a_deviner
    mot_a_deviner = random.choice(liste_mots)
    return {"message": "Nouvelle partie commencée."}

@application.get("/api/v1/motdevine/verifier")
async def verifier_mot(
    mot: str = Query(..., min_length=5, max_length=5)
):
    global mot_a_deviner
    mot = mot.upper()

    if not mot_a_deviner:
        return JSONResponse(
            status_code=400,
            content={"erreur": "Aucune partie en cours. Veuillez démarrer une nouvelle partie."}
        )

    resultat = []
    lettres_restantes = list(mot_a_deviner)

    # Première passe : lettres bien placées
    for i in range(5):
        if mot[i] == mot_a_deviner[i]:
            resultat.append({"lettre": mot[i], "couleur": "vert"})
            lettres_restantes[i] = None
        else:
            resultat.append({"lettre": mot[i], "couleur": "gris"})

    # Deuxième passe : lettres mal placées (présentes mais mal placées)
    for i in range(5):
        if resultat[i]["couleur"] == "gris" and mot[i] in lettres_restantes:
            resultat[i]["couleur"] = "jaune"
            lettres_restantes[lettres_restantes.index(mot[i])] = None

    return {"mot_verifie": resultat}

