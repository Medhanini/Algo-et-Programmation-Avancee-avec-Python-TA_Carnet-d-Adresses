import re


class Contact:
    def __init__(self, nom, email, telephone):
        self.nom = nom
        self.email = email
        self.telephone = telephone

    @staticmethod
    def email_valide(email):
        motif = r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$"
        return re.match(motif, email) is not None

    @staticmethod
    def telephone_valide(telephone):
        motif = r"^0[1-9](\d{2}){4}$"
        return re.match(motif, telephone) is not None

    def __str__(self):
        return f"{self.nom} | {self.email} | {self.telephone}"

    def __repr__(self):
        return f"Contact(nom={self.nom!r}, email={self.email!r}, telephone={self.telephone!r})"
