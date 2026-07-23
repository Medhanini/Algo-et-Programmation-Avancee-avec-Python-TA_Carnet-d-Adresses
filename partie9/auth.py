import hashlib
import os

from database import initialiser_base, obtenir_connexion

FICHIER_BD = "carnet.db"
ITERATIONS = 200_000


def _generer_sel():
    return os.urandom(16).hex()


def _hacher_mot_de_passe(mot_de_passe, sel):
    return hashlib.pbkdf2_hmac(
        "sha256",
        mot_de_passe.encode("utf-8"),
        bytes.fromhex(sel),
        ITERATIONS,
    ).hex()


def creer_admin(nom_utilisateur, mot_de_passe, fichier=FICHIER_BD):
    initialiser_base(fichier)
    sel = _generer_sel()
    hash_mot_de_passe = _hacher_mot_de_passe(mot_de_passe, sel)

    with obtenir_connexion(fichier) as connexion:
        existant = connexion.execute(
            "SELECT id FROM admins WHERE nom_utilisateur = ?", (nom_utilisateur,)
        ).fetchone()
        if existant is not None:
            raise ValueError(f"L'administrateur '{nom_utilisateur}' existe déjà.")

        connexion.execute(
            "INSERT INTO admins (nom_utilisateur, sel, hash) VALUES (?, ?, ?)",
            (nom_utilisateur, sel, hash_mot_de_passe),
        )


def verifier_identifiants(nom_utilisateur, mot_de_passe, fichier=FICHIER_BD):
    initialiser_base(fichier)
    with obtenir_connexion(fichier) as connexion:
        admin = connexion.execute(
            "SELECT sel, hash FROM admins WHERE nom_utilisateur = ?", (nom_utilisateur,)
        ).fetchone()

    if admin is None:
        return False
    return _hacher_mot_de_passe(mot_de_passe, admin["sel"]) == admin["hash"]


def initialiser_admin_par_defaut(fichier=FICHIER_BD):
    initialiser_base(fichier)
    with obtenir_connexion(fichier) as connexion:
        nombre_admins = connexion.execute("SELECT COUNT(*) FROM admins").fetchone()[0]

    if nombre_admins == 0:
        creer_admin("admin", "admin123", fichier)
