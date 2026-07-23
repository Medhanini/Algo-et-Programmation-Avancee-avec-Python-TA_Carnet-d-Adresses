from contact import Contact


class AddressBook:
    def __init__(self):
        self.contacts = []

    def ajouter_contact(self, contact):
        if self.rechercher_par_nom(contact.nom) is not None:
            raise ValueError(f"Un contact nommé '{contact.nom}' existe déjà.")
        self.contacts.append(contact)

    def supprimer_contact(self, nom):
        contact = self.rechercher_par_nom(nom)
        if contact is None:
            return False
        self.contacts.remove(contact)
        return True

    def modifier_contact(self, nom, email=None, telephone=None):
        contact = self.rechercher_par_nom(nom)
        if contact is None:
            return False
        if email:
            contact.email = email
        if telephone:
            contact.telephone = telephone
        return True

    def rechercher_par_nom(self, nom):
        for contact in self.contacts:
            if contact.nom.lower() == nom.lower():
                return contact
        return None

    def lister_contacts(self):
        return sorted(self.contacts, key=lambda c: c.nom.lower())

    def __len__(self):
        return len(self.contacts)
