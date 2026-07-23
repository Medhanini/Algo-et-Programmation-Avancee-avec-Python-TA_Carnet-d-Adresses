import sqlite3

FICHIER_BD = "carnet.db"


def obtenir_connexion(fichier=FICHIER_BD):
    connexion = sqlite3.connect(fichier)
    connexion.row_factory = sqlite3.Row
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion


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
        connexion.execute(
            """
            CREATE TABLE IF NOT EXISTS rendezvous (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_contact TEXT NOT NULL,
                date_rdv TEXT NOT NULL,
                heure TEXT NOT NULL,
                UNIQUE(date_rdv, heure)
            )
            """
        )
    connexion.close()
