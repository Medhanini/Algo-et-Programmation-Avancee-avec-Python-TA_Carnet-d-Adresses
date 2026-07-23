from flask import Flask, flash, redirect, render_template, request, url_for

import communication
from address_book import AddressBook
from contact import CATEGORIES, Contact

app = Flask(__name__)
app.secret_key = "cle-secrete-dev-carnet-adresses"

carnet = AddressBook()


@app.route("/")
def index():
    terme = request.args.get("q", "").strip()
    categorie = request.args.get("categorie", "").strip()

    if terme:
        contacts = carnet.rechercher(terme, categorie=categorie or None)
    else:
        contacts = carnet.lister_contacts(categorie=categorie or None)

    return render_template(
        "index.html", contacts=contacts, terme=terme, categorie=categorie, categories=CATEGORIES
    )


def _valeurs_formulaire(form):
    return {
        "nom": form.get("nom", "").strip(),
        "email": form.get("email", "").strip(),
        "telephone": form.get("telephone", "").strip(),
        "categorie": form.get("categorie", "").strip(),
        "adresse": form.get("adresse", "").strip(),
        "fonction": form.get("fonction", "").strip(),
        "entreprise": form.get("entreprise", "").strip(),
    }


@app.route("/contacts/ajouter", methods=["GET", "POST"])
def ajouter_contact():
    if request.method == "POST":
        valeurs = _valeurs_formulaire(request.form)
        try:
            carnet.ajouter_contact(Contact(**valeurs))
            flash(f"Contact '{valeurs['nom']}' ajouté avec succès.", "succes")
            return redirect(url_for("index"))
        except ValueError as e:
            flash(str(e), "erreur")
            return render_template(
                "form.html", titre="Ajouter un contact", contact=None, valeurs=valeurs, categories=CATEGORIES
            )

    return render_template("form.html", titre="Ajouter un contact", contact=None, valeurs={}, categories=CATEGORIES)


@app.route("/contacts/<nom>/modifier", methods=["GET", "POST"])
def modifier_contact(nom):
    contact = carnet.rechercher_par_nom(nom)
    if contact is None:
        flash(f"Aucun contact nommé '{nom}' n'a été trouvé.", "erreur")
        return redirect(url_for("index"))

    if request.method == "POST":
        valeurs = _valeurs_formulaire(request.form)
        try:
            carnet.modifier_contact(
                nom,
                email=valeurs["email"] or None,
                telephone=valeurs["telephone"] or None,
                categorie=valeurs["categorie"] or None,
                adresse=valeurs["adresse"],
                fonction=valeurs["fonction"],
                entreprise=valeurs["entreprise"],
            )
            flash(f"Contact '{nom}' mis à jour.", "succes")
            return redirect(url_for("index"))
        except ValueError as e:
            flash(str(e), "erreur")
            valeurs["nom"] = nom
            return render_template(
                "form.html", titre=f"Modifier {nom}", contact=contact, valeurs=valeurs, categories=CATEGORIES
            )

    valeurs = {
        "nom": contact.nom,
        "email": contact.email,
        "telephone": contact.telephone,
        "categorie": contact.categorie,
        "adresse": contact.adresse,
        "fonction": contact.fonction,
        "entreprise": contact.entreprise,
    }
    return render_template(
        "form.html", titre=f"Modifier {nom}", contact=contact, valeurs=valeurs, categories=CATEGORIES
    )


@app.route("/contacts/<nom>/supprimer", methods=["POST"])
def supprimer_contact(nom):
    if carnet.supprimer_contact(nom):
        flash(f"Contact '{nom}' supprimé.", "succes")
    else:
        flash(f"Aucun contact nommé '{nom}' n'a été trouvé.", "erreur")
    return redirect(url_for("index"))


@app.route("/contacts/<nom>/contacter", methods=["GET", "POST"])
def contacter_contact(nom):
    contact = carnet.rechercher_par_nom(nom)
    if contact is None:
        flash(f"Aucun contact nommé '{nom}' n'a été trouvé.", "erreur")
        return redirect(url_for("index"))

    modele_choisi = request.values.get("modele", "rendezvous")
    sujet_defaut, corps_defaut = communication.generer_message(modele_choisi, contact.nom)

    if request.method == "POST":
        canal = request.form.get("canal")
        sujet = request.form.get("sujet", sujet_defaut)
        corps = request.form.get("corps", corps_defaut)

        if canal == "email":
            try:
                communication.envoyer_email(contact.email, sujet, corps)
                flash(f"Email envoyé à {contact.nom} ({contact.email}).", "succes")
                return redirect(url_for("index"))
            except (RuntimeError, OSError) as e:
                flash(f"Échec de l'envoi de l'email : {e}", "erreur")
        elif canal == "whatsapp":
            lien = communication.construire_lien_whatsapp(contact.telephone, corps)
            return redirect(lien)
        else:
            flash("Canal de communication invalide.", "erreur")

    return render_template(
        "contacter.html",
        contact=contact,
        modele_choisi=modele_choisi,
        modeles=communication.MODELES_MESSAGES,
        sujet=sujet_defaut,
        corps=corps_defaut,
    )


if __name__ == "__main__":
    app.run(debug=True)
