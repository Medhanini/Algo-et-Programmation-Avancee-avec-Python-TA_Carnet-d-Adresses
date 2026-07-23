import sqlite3

from contact import CATEGORIE_PAR_DEFAUT

FICHIER_BD = "carnet.db"

COLONNES_SUPPLEMENTAIRES = {
    "categorie": f"TEXT NOT NULL DEFAULT '{CATEGORIE_PAR_DEFAUT}'",
    "adresse": "TEXT NOT NULL DEFAULT ''",
    "fonction": "TEXT NOT NULL DEFAULT ''",
    "entreprise": "TEXT NOT NULL DEFAULT ''",
}


def obtenir_connexion(fichier=FICHIER_BD):
    connexion = sqlite3.connect(fichier)
    connexion.row_factory = sqlite3.Row
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion


def _migrer_colonnes_contacts(connexion):
    colonnes_existantes = {
        ligne["name"] for ligne in connexion.execute("PRAGMA table_info(contacts)").fetchall()
    }
    for nom_colonne, definition in COLONNES_SUPPLEMENTAIRES.items():
        if nom_colonne not in colonnes_existantes:
            connexion.execute(f"ALTER TABLE contacts ADD COLUMN {nom_colonne} {definition}")


def initialiser_base(fichier=FICHIER_BD):
    connexion = obtenir_connexion(fichier)
    with connexion:
        connexion.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT NOT NULL,
                telephone TEXT NOT NULL
            )
            """
        )
        connexion.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_utilisateur TEXT NOT NULL UNIQUE,
                sel TEXT NOT NULL,
                hash TEXT NOT NULL
            )
            """
        )
        _migrer_colonnes_contacts(connexion)
    connexion.close()
