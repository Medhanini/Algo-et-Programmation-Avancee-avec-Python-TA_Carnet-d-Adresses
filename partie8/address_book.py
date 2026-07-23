import csv

from contact import CATEGORIE_PAR_DEFAUT, Contact
from database import initialiser_base, obtenir_connexion

CHAMPS = ["nom", "email", "telephone", "categorie", "adresse", "fonction", "entreprise"]


class AddressBook:
    def __init__(self, fichier="carnet.db"):
        self.fichier = fichier
        initialiser_base(self.fichier)

    def _connexion(self):
        return obtenir_connexion(self.fichier)

    @staticmethod
    def _vers_contact(ligne):
        return Contact(
            ligne["nom"],
            ligne["email"],
            ligne["telephone"],
            categorie=ligne["categorie"],
            adresse=ligne["adresse"],
            fonction=ligne["fonction"],
            entreprise=ligne["entreprise"],
        )

    def ajouter_contact(self, contact):
        if not Contact.email_valide(contact.email):
            raise ValueError(f"Email invalide : '{contact.email}'.")
        if not Contact.telephone_valide(contact.telephone):
            raise ValueError(f"Téléphone invalide : '{contact.telephone}'.")
        if not Contact.categorie_valide(contact.categorie):
            raise ValueError(f"Catégorie invalide : '{contact.categorie}'.")
        if self.rechercher_par_nom(contact.nom) is not None:
            raise ValueError(f"Un contact nommé '{contact.nom}' existe déjà.")
        if self.rechercher_par_email(contact.email) is not None:
            raise ValueError(f"Un contact avec l'email '{contact.email}' existe déjà.")
        if self.rechercher_par_telephone(contact.telephone) is not None:
            raise ValueError(f"Un contact avec le téléphone '{contact.telephone}' existe déjà.")

        with self._connexion() as connexion:
            connexion.execute(
                """
                INSERT INTO contacts (nom, email, telephone, categorie, adresse, fonction, entreprise)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contact.nom,
                    contact.email,
                    contact.telephone,
                    contact.categorie,
                    contact.adresse,
                    contact.fonction,
                    contact.entreprise,
                ),
            )

    def supprimer_contact(self, nom):
        with self._connexion() as connexion:
            curseur = connexion.execute(
                "DELETE FROM contacts WHERE LOWER(nom) = LOWER(?)", (nom,)
            )
            return curseur.rowcount > 0

    def modifier_contact(self, nom, email=None, telephone=None, categorie=None,
                          adresse=None, fonction=None, entreprise=None):
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

        if categorie and not Contact.categorie_valide(categorie):
            raise ValueError(f"Catégorie invalide : '{categorie}'.")

        with self._connexion() as connexion:
            if email:
                connexion.execute("UPDATE contacts SET email = ? WHERE LOWER(nom) = LOWER(?)", (email, nom))
            if telephone:
                connexion.execute("UPDATE contacts SET telephone = ? WHERE LOWER(nom) = LOWER(?)", (telephone, nom))
            if categorie:
                connexion.execute("UPDATE contacts SET categorie = ? WHERE LOWER(nom) = LOWER(?)", (categorie, nom))
            if adresse is not None:
                connexion.execute("UPDATE contacts SET adresse = ? WHERE LOWER(nom) = LOWER(?)", (adresse, nom))
            if fonction is not None:
                connexion.execute("UPDATE contacts SET fonction = ? WHERE LOWER(nom) = LOWER(?)", (fonction, nom))
            if entreprise is not None:
                connexion.execute("UPDATE contacts SET entreprise = ? WHERE LOWER(nom) = LOWER(?)", (entreprise, nom))
        return True

    def rechercher_par_nom(self, nom):
        with self._connexion() as connexion:
            ligne = connexion.execute(
                "SELECT * FROM contacts WHERE LOWER(nom) = LOWER(?)", (nom,)
            ).fetchone()
        return self._vers_contact(ligne) if ligne else None

    def rechercher_par_email(self, email):
        with self._connexion() as connexion:
            ligne = connexion.execute(
                "SELECT * FROM contacts WHERE LOWER(email) = LOWER(?)", (email.strip(),)
            ).fetchone()
        return self._vers_contact(ligne) if ligne else None

    def rechercher_par_telephone(self, telephone):
        with self._connexion() as connexion:
            ligne = connexion.execute(
                "SELECT * FROM contacts WHERE telephone = ?", (telephone,)
            ).fetchone()
        return self._vers_contact(ligne) if ligne else None

    def rechercher(self, terme, categorie=None):
        motif = f"%{terme.strip()}%"
        requete = """
            SELECT * FROM contacts
            WHERE (nom LIKE ? OR email LIKE ? OR telephone LIKE ? OR entreprise LIKE ?)
        """
        parametres = [motif, motif, motif, motif]
        if categorie:
            requete += " AND categorie = ?"
            parametres.append(categorie)
        requete += " ORDER BY LOWER(nom)"

        with self._connexion() as connexion:
            lignes = connexion.execute(requete, parametres).fetchall()
        return [self._vers_contact(ligne) for ligne in lignes]

    def lister_contacts(self, categorie=None):
        requete = "SELECT * FROM contacts"
        parametres = []
        if categorie:
            requete += " WHERE categorie = ?"
            parametres.append(categorie)
        requete += " ORDER BY LOWER(nom)"

        with self._connexion() as connexion:
            lignes = connexion.execute(requete, parametres).fetchall()
        return [self._vers_contact(ligne) for ligne in lignes]

    def exporter_csv(self, fichier_csv="contacts_export.csv"):
        contacts = self.lister_contacts()
        with open(fichier_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CHAMPS)
            writer.writeheader()
            for contact in contacts:
                writer.writerow({champ: getattr(contact, champ) for champ in CHAMPS})
        return fichier_csv

    def __len__(self):
        with self._connexion() as connexion:
            return connexion.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
