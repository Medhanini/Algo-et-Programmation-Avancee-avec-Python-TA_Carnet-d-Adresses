from contact import Contact
from address_book import AddressBook


def saisir_email():
    while True:
        email = input("Email : ").strip()
        if Contact.email_valide(email):
            return email
        print("Email invalide, veuillez réessayer.")


def saisir_telephone():
    while True:
        telephone = input("Téléphone (ex: 0612345678) : ").strip()
        if Contact.telephone_valide(telephone):
            return telephone
        print("Numéro de téléphone invalide, veuillez réessayer.")


def ajouter_contact(carnet):
    nom = input("Nom : ").strip()
    if not nom:
        print("Le nom ne peut pas être vide.")
        return
    email = saisir_email()
    telephone = saisir_telephone()
    try:
        carnet.ajouter_contact(Contact(nom, email, telephone))
        print(f"Contact '{nom}' ajouté avec succès.")
    except ValueError as e:
        print(f"Erreur : {e}")


def supprimer_contact(carnet):
    nom = input("Nom du contact à supprimer : ").strip()
    if carnet.supprimer_contact(nom):
        print(f"Contact '{nom}' supprimé.")
    else:
        print(f"Aucun contact nommé '{nom}' n'a été trouvé.")


def modifier_contact(carnet):
    nom = input("Nom du contact à modifier : ").strip()
    if carnet.rechercher_par_nom(nom) is None:
        print(f"Aucun contact nommé '{nom}' n'a été trouvé.")
        return

    print("Laissez vide pour ne pas modifier le champ.")
    email = input("Nouvel email : ").strip()
    if email and not Contact.email_valide(email):
        print("Email invalide, modification de l'email annulée.")
        email = None

    telephone = input("Nouveau téléphone : ").strip()
    if telephone and not Contact.telephone_valide(telephone):
        print("Téléphone invalide, modification du téléphone annulée.")
        telephone = None

    try:
        carnet.modifier_contact(nom, email or None, telephone or None)
        print(f"Contact '{nom}' mis à jour.")
    except ValueError as e:
        print(f"Erreur : {e}")


def rechercher_contact(carnet):
    nom = input("Nom à rechercher : ").strip()
    contact = carnet.rechercher_par_nom(nom)
    if contact:
        print(contact)
    else:
        print(f"Aucun contact nommé '{nom}' n'a été trouvé.")


def lister_contacts(carnet):
    contacts = carnet.lister_contacts()
    if not contacts:
        print("Le carnet d'adresses est vide.")
        return
    print(f"--- {len(contacts)} contact(s) ---")
    for contact in contacts:
        print(contact)


def afficher_menu():
    print("\n=== Carnet d'adresses ===")
    print("1. Ajouter un contact")
    print("2. Supprimer un contact")
    print("3. Modifier un contact")
    print("4. Rechercher un contact")
    print("5. Lister tous les contacts")
    print("6. Quitter")


def main():
    carnet = AddressBook()
    actions = {
        "1": ajouter_contact,
        "2": supprimer_contact,
        "3": modifier_contact,
        "4": rechercher_contact,
        "5": lister_contacts,
    }

    while True:
        afficher_menu()
        choix = input("Votre choix : ").strip()

        if choix == "6":
            print("Au revoir !")
            break

        action = actions.get(choix)
        if action:
            action(carnet)
        else:
            print("Choix invalide, veuillez réessayer.")


if __name__ == "__main__":
    main()
