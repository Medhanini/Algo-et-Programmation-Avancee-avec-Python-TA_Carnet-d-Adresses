import hashlib
import json
import os

FICHIER_ADMINS = "admins.json"
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


def _charger_admins():
    if not os.path.exists(FICHIER_ADMINS):
        return {}
    with open(FICHIER_ADMINS, "r", encoding="utf-8") as f:
        return json.load(f)


def _sauvegarder_admins(admins):
    with open(FICHIER_ADMINS, "w", encoding="utf-8") as f:
        json.dump(admins, f, indent=2)


def creer_admin(nom_utilisateur, mot_de_passe):
    admins = _charger_admins()
    if nom_utilisateur in admins:
        raise ValueError(f"L'administrateur '{nom_utilisateur}' existe déjà.")

    sel = _generer_sel()
    admins[nom_utilisateur] = {
        "sel": sel,
        "hash": _hacher_mot_de_passe(mot_de_passe, sel),
    }
    _sauvegarder_admins(admins)


def verifier_identifiants(nom_utilisateur, mot_de_passe):
    admins = _charger_admins()
    admin = admins.get(nom_utilisateur)
    if admin is None:
        return False
    return _hacher_mot_de_passe(mot_de_passe, admin["sel"]) == admin["hash"]


def initialiser_admin_par_defaut():
    admins = _charger_admins()
    if not admins:
        creer_admin("admin", "admin123")
