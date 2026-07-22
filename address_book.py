import csv
import os

from contact import Contact


class AddressBook:
    CHAMPS = ["nom", "email", "telephone"]

    def __init__(self, fichier="contacts.csv"):
        self.fichier = fichier
        if not os.path.exists(self.fichier):
            with open(self.fichier, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.CHAMPS)
                writer.writeheader()

    def _lire_tout(self):
        contacts = []
        with open(self.fichier, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for ligne in reader:
                contacts.append(Contact(ligne["nom"], ligne["email"], ligne["telephone"]))
        return contacts

    def _ecrire_tout(self, contacts):
        with open(self.fichier, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.CHAMPS)
            writer.writeheader()
            for contact in contacts:
                writer.writerow({"nom": contact.nom, "email": contact.email, "telephone": contact.telephone})

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

        with open(self.fichier, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.CHAMPS)
            writer.writerow({"nom": contact.nom, "email": contact.email, "telephone": contact.telephone})

    def supprimer_contact(self, nom):
        contacts = self._lire_tout()
        contact = next((c for c in contacts if c.nom.lower() == nom.lower()), None)
        if contact is None:
            return False
        contacts.remove(contact)
        self._ecrire_tout(contacts)
        return True

    def modifier_contact(self, nom, email=None, telephone=None):
        contacts = self._lire_tout()
        contact = next((c for c in contacts if c.nom.lower() == nom.lower()), None)
        if contact is None:
            return False
        if email:
            if not Contact.email_valide(email):
                raise ValueError(f"Email invalide : '{email}'.")
            autre = next((c for c in contacts if c.email.lower() == email.lower() and c is not contact), None)
            if autre is not None:
                raise ValueError(f"Un contact avec l'email '{email}' existe déjà.")
            contact.email = email
        if telephone:
            if not Contact.telephone_valide(telephone):
                raise ValueError(f"Téléphone invalide : '{telephone}'.")
            autre = next((c for c in contacts if c.telephone == telephone and c is not contact), None)
            if autre is not None:
                raise ValueError(f"Un contact avec le téléphone '{telephone}' existe déjà.")
            contact.telephone = telephone
        self._ecrire_tout(contacts)
        return True

    def rechercher_par_nom(self, nom):
        for contact in self._lire_tout():
            if contact.nom.lower() == nom.lower():
                return contact
        return None

    def rechercher_par_email(self, email):
        email = email.strip().lower()

        for contact in self._lire_tout():
            if contact.email.strip().lower() == email:
                return contact

        return None

    def rechercher_par_telephone(self, telephone):
        for contact in self._lire_tout():
            if contact.telephone == telephone:
                return contact
        return None

    def lister_contacts(self):
        return sorted(self._lire_tout(), key=lambda c: c.nom.lower())

    def __len__(self):
        return len(self._lire_tout())
