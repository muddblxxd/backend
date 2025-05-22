from copy import deepcopy
import time
from uuid import uuid4
from fastapi import FastAPI, Cookie, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

application = FastAPI()

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://localhost:8000"],
    allow_credentials=True
)

class InfosUtilisateur:
    def __init__(self, carte):
        self.derniere_vue = deepcopy(carte)
        self.dernier_temps_modif = 0

class Carte:
    def __init__(self, largeur: int, hauteur: int, delai_nanosec: int = 10e9):
        self.cles = set()
        self.largeur = largeur
        self.hauteur = hauteur
        self.donnees = [
            [(0, 0, 0) for _ in range(hauteur)]
            for _ in range(largeur)
        ]
        self.delai_nanosec = delai_nanosec
        self.utilisateurs: dict[str, InfosUtilisateur] = {}

    def creer_cle(self):
        cle = str(uuid4())
        self.cles.add(cle)
        return cle

    def cle_valide(self, cle: str):
        return cle in self.cles

    def creer_utilisateur(self):
        identifiant = str(uuid4())
        self.utilisateurs[identifiant] = InfosUtilisateur(self.donnees)
        return identifiant

    def utilisateur_valide(self, identifiant: str):
        return identifiant in self.utilisateurs

    def definir_pixel(self, x: int, y: int, r: int, v: int, b: int, identifiant: str):
        if not self.utilisateur_valide(identifiant):
            return {"erreur": "ID utilisateur invalide"}
        maintenant = time.time_ns()
        infos = self.utilisateurs[identifiant]
        if maintenant - infos.dernier_temps_modif < self.delai_nanosec:
            attente = int((self.delai_nanosec - (maintenant - infos.dernier_temps_modif)) / 1e9)
            return {"erreur": f"Attends {attente} s avant de remettre un pixel"}
        self.donnees[x][y] = (r, v, b)
        infos.dernier_temps_modif = maintenant
        return {"statut": "ok", "x": x, "y": y, "couleur": (r, v, b)}

# Dictionnaire global des cartes
cartes: dict[str, Carte] = {"1234": Carte(10, 10)}

@application.get("/api/v1/{nom_carte}/preinit")
async def preinitialisation(nom_carte: str):
    if nom_carte not in cartes:
        return {"erreur": "Carte inconnue"}

    cle = cartes[nom_carte].creer_cle()
    reponse = JSONResponse({"cle": cle})
    reponse.set_cookie("cle", cle, httponly=True, samesite="none", secure=True, max_age=3600)
    return reponse

@application.get("/api/v1/{nom_carte}/init")
async def initialisation(
    nom_carte: str,
    cle_query: str = Query(alias="key"),
    cle_cookie: str = Cookie(alias="key")
):
    if nom_carte not in cartes:
        return {"erreur": "Carte inconnue"}
    
    carte = cartes[nom_carte]

    if cle_query != cle_cookie:
        return {"erreur": "Les clés ne correspondent pas"}
    
    if not carte.cle_valide(cle_cookie):
        return {"erreur": "Clé invalide"}

    identifiant = carte.creer_utilisateur()
    reponse = JSONResponse({
        "id": identifiant,
        "largeur": carte.largeur,
        "hauteur": carte.hauteur,
        "donnees": carte.donnees
    })
    reponse.set_cookie("id", identifiant, httponly=True, samesite="none", secure=True, max_age=3600)
    return reponse

@application.get("/api/v1/{nom_carte}/deltas")
async def deltas(
    nom_carte: str,
    identifiant_query: str = Query(alias="id"),
    cle_cookie: str = Cookie(alias="key"),
    identifiant_cookie: str = Cookie(alias="id")
):
    if nom_carte not in cartes:
        return {"erreur": "Carte inconnue"}
    
    carte = cartes[nom_carte]

    if not carte.cle_valide(cle_cookie):
        return {"erreur": "Clé invalide"}
    
    if identifiant_query != identifiant_cookie:
        return {"erreur": "Les identifiants ne correspondent pas"}
    
    if not carte.utilisateur_valide(identifiant_query):
        return {"erreur": "Utilisateur inconnu"}

    infos = carte.utilisateurs[identifiant_query]
    ancienne_vue = infos.derniere_vue

    changements: list[tuple[int, int, int, int, int]] = []
    for y in range(carte.hauteur):
        for x in range(carte.largeur):
            if carte.donnees[x][y] != ancienne_vue[x][y]:
                changements.append((x, y, *carte.donnees[x][y]))
    
    infos.derniere_vue = deepcopy(carte.donnees)

    return {
        "id": identifiant_query,
        "largeur": carte.largeur,
        "hauteur": carte.hauteur,
        "changements": changements
    }

@application.post("/api/v1/{nom_carte}/definir_pixel")
async def definir_pixel(
    nom_carte: str,
    x: int = Query(...),
    y: int = Query(...),
    r: int = Query(...),
    v: int = Query(...),
    b: int = Query(...),
    cle_cookie: str = Cookie(alias="key"),
    identifiant_cookie: str = Cookie(alias="id")
):
    if nom_carte not in cartes:
        return {"erreur": "Carte inconnue"}

    carte = cartes[nom_carte]

    if not carte.cle_valide(cle_cookie):
        return {"erreur": "Clé invalide"}
    
    if not carte.utilisateur_valide(identifiant_cookie):
        return {"erreur": "ID utilisateur invalide"}
    
    if not (0 <= x < carte.largeur and 0 <= y < carte.hauteur):
        return {"erreur": "Coordonnées invalides"}
    
    resultat = carte.definir_pixel(x, y, r, v, b, identifiant_cookie)
    if "erreur" in resultat:
        return {"erreur": resultat["erreur"]}
    
    return resultat
