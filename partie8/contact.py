import re

CATEGORIES = ["Patient", "Client", "Fournisseur", "Laboratoire", "Entreprise"]
CATEGORIE_PAR_DEFAUT = "Patient"


class Contact:
    def __init__(self, nom, email, telephone, categorie=CATEGORIE_PAR_DEFAUT,
                 adresse="", fonction="", entreprise=""):
        self.nom = nom
        self.email = email
        self.telephone = telephone
        self.categorie = categorie or CATEGORIE_PAR_DEFAUT
        self.adresse = adresse
        self.fonction = fonction
        self.entreprise = entreprise

    @staticmethod
    def email_valide(email):
        motif = r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$"
        return re.match(motif, email) is not None

    @staticmethod
    def telephone_valide(telephone):
        motif = r"^0[1-9](\d{2}){4}$"
        return re.match(motif, telephone) is not None

    @staticmethod
    def categorie_valide(categorie):
        return categorie in CATEGORIES

    def __str__(self):
        details = f"{self.nom} | {self.email} | {self.telephone} | {self.categorie}"
        if self.entreprise:
            details += f" | {self.entreprise}"
        if self.fonction:
            details += f" ({self.fonction})"
        return details

    def __repr__(self):
        return (
            f"Contact(nom={self.nom!r}, email={self.email!r}, telephone={self.telephone!r}, "
            f"categorie={self.categorie!r}, adresse={self.adresse!r}, "
            f"fonction={self.fonction!r}, entreprise={self.entreprise!r})"
        )
