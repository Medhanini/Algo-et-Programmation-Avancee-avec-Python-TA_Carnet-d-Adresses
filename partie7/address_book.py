import csv

from contact import Contact
from database import initialiser_base, obtenir_connexion


class AddressBook:
    def __init__(self, fichier="carnet.db"):
        self.fichier = fichier
        initialiser_base(self.fichier)

    def _connexion(self):
        return obtenir_connexion(self.fichier)

    @staticmethod
    def _vers_contact(ligne):
        return Contact(ligne["nom"], ligne["email"], ligne["telephone"])

    def ajouter_contact(self, contact):
        if not Contact.email_valide(contact.email):
            raise ValueError(f"Email invalide : '{contact.email}'.")
        if not Contact.telephone_valide(contact.telephone):
            raise ValueError(f"Téléphone invalide : '{contact.telephone}'.")
        if self.rechercher_par_nom(contact.nom) is not None:
            raise ValueError(f"Un contact nommé '{contact.nom}' existe déjà.")
        if self.rechercher_par_email(contact.email) is not None:
            raise ValueError(f"Un contact avec l'email '{contact.email}' existe déjà.")
        if self.rechercher_par_telephone(contact.telephone) is not None:
            raise ValueError(f"Un contact avec le téléphone '{contact.telephone}' existe déjà.")

        with self._connexion() as connexion:
            connexion.execute(
                "INSERT INTO contacts (nom, email, telephone) VALUES (?, ?, ?)",
                (contact.nom, contact.email, contact.telephone),
            )

    def supprimer_contact(self, nom):
        with self._connexion() as connexion:
            curseur = connexion.execute(
                "DELETE FROM contacts WHERE LOWER(nom) = LOWER(?)", (nom,)
            )
            return curseur.rowcount > 0

    def modifier_contact(self, nom, email=None, telephone=None):
        contact_actuel = self.rechercher_par_nom(nom)
        if contact_actuel is None:
            return False

        if email:
            if not Contact.email_valide(email):
                raise ValueError(f"Email invalide : '{email}'.")
            autre = self.rechercher_par_email(email)
            if autre is not None and autre.nom.lower() != nom.lower():
                raise ValueError(f"Un contact avec l'email '{email}' existe déjà.")

        if telephone:
            if not Contact.telephone_valide(telephone):
                raise ValueError(f"Téléphone invalide : '{telephone}'.")
            autre = self.rechercher_par_telephone(telephone)
            if autre is not None and autre.nom.lower() != nom.lower():
                raise ValueError(f"Un contact avec le téléphone '{telephone}' existe déjà.")

        with self._connexion() as connexion:
            if email:
                connexion.execute(
                    "UPDATE contacts SET email = ? WHERE LOWER(nom) = LOWER(?)", (email, nom)
                )
            if telephone:
                connexion.execute(
                    "UPDATE contacts SET telephone = ? WHERE LOWER(nom) = LOWER(?)", (telephone, nom)
                )
        return True

    def rechercher_par_nom(self, nom):
        with self._connexion() as connexion:
            ligne = connexion.execute(
                "SELECT nom, email, telephone FROM contacts WHERE LOWER(nom) = LOWER(?)", (nom,)
            ).fetchone()
        return self._vers_contact(ligne) if ligne else None

    def rechercher_par_email(self, email):
        with self._connexion() as connexion:
            ligne = connexion.execute(
                "SELECT nom, email, telephone FROM contacts WHERE LOWER(email) = LOWER(?)",
                (email.strip(),),
            ).fetchone()
        return self._vers_contact(ligne) if ligne else None

    def rechercher_par_telephone(self, telephone):
        with self._connexion() as connexion:
            ligne = connexion.execute(
                "SELECT nom, email, telephone FROM contacts WHERE telephone = ?", (telephone,)
            ).fetchone()
        return self._vers_contact(ligne) if ligne else None

    def rechercher(self, terme):
        motif = f"%{terme.strip()}%"
        with self._connexion() as connexion:
            lignes = connexion.execute(
                """
                SELECT nom, email, telephone FROM contacts
                WHERE nom LIKE ? OR email LIKE ? OR telephone LIKE ?
                ORDER BY LOWER(nom)
                """,
                (motif, motif, motif),
            ).fetchall()
        return [self._vers_contact(ligne) for ligne in lignes]

    def lister_contacts(self):
        with self._connexion() as connexion:
            lignes = connexion.execute(
                "SELECT nom, email, telephone FROM contacts ORDER BY LOWER(nom)"
            ).fetchall()
        return [self._vers_contact(ligne) for ligne in lignes]

    def exporter_csv(self, fichier_csv="contacts_export.csv"):
        contacts = self.lister_contacts()
        with open(fichier_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["nom", "email", "telephone"])
            writer.writeheader()
            for contact in contacts:
                writer.writerow({"nom": contact.nom, "email": contact.email, "telephone": contact.telephone})
        return fichier_csv

    def __len__(self):
        with self._connexion() as connexion:
            return connexion.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
