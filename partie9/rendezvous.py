from datetime import datetime, timedelta

from database import initialiser_base, obtenir_connexion

HEURE_OUVERTURE = "08:00"
HEURE_FERMETURE = "18:00"
DUREE_CRENEAU_MINUTES = 30


class GestionnaireRendezVous:
    def __init__(self, fichier="carnet.db"):
        self.fichier = fichier
        initialiser_base(self.fichier)

    def _connexion(self):
        return obtenir_connexion(self.fichier)

    @staticmethod
    def creneaux_journee():
        debut = datetime.strptime(HEURE_OUVERTURE, "%H:%M")
        fin = datetime.strptime(HEURE_FERMETURE, "%H:%M")
        creneaux = []
        while debut < fin:
            creneaux.append(debut.strftime("%H:%M"))
            debut += timedelta(minutes=DUREE_CRENEAU_MINUTES)
        return creneaux

    def creneaux_reserves(self, date_rdv):
        with self._connexion() as connexion:
            lignes = connexion.execute(
                "SELECT heure, nom_contact FROM rendezvous WHERE date_rdv = ?", (date_rdv,)
            ).fetchall()
        return {ligne["heure"]: ligne["nom_contact"] for ligne in lignes}

    def reserver(self, nom_contact, date_rdv, heure):
        if heure not in self.creneaux_journee():
            raise ValueError(f"Créneau invalide : '{heure}'.")
        if heure in self.creneaux_reserves(date_rdv):
            raise ValueError(f"Le créneau {heure} du {date_rdv} est déjà réservé.")

        with self._connexion() as connexion:
            connexion.execute(
                "INSERT INTO rendezvous (nom_contact, date_rdv, heure) VALUES (?, ?, ?)",
                (nom_contact, date_rdv, heure),
            )

    def annuler(self, date_rdv, heure):
        with self._connexion() as connexion:
            curseur = connexion.execute(
                "DELETE FROM rendezvous WHERE date_rdv = ? AND heure = ?", (date_rdv, heure)
            )
            return curseur.rowcount > 0

    def lister_rdv(self, date_rdv):
        with self._connexion() as connexion:
            lignes = connexion.execute(
                "SELECT heure, nom_contact FROM rendezvous WHERE date_rdv = ? ORDER BY heure", (date_rdv,)
            ).fetchall()
        return [(ligne["heure"], ligne["nom_contact"]) for ligne in lignes]
