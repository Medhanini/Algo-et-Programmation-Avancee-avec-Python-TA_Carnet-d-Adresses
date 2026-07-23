from flask import Flask, flash, redirect, render_template, request, url_for

import communication
from address_book import AddressBook
from contact import Contact

app = Flask(__name__)
app.secret_key = "cle-secrete-dev-carnet-adresses"

carnet = AddressBook()


@app.route("/")
def index():
    terme = request.args.get("q", "").strip()
    contacts = carnet.rechercher(terme) if terme else carnet.lister_contacts()
    return render_template("index.html", contacts=contacts, terme=terme)


@app.route("/contacts/ajouter", methods=["GET", "POST"])
def ajouter_contact():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        telephone = request.form.get("telephone", "").strip()

        try:
            carnet.ajouter_contact(Contact(nom, email, telephone))
            flash(f"Contact '{nom}' ajouté avec succès.", "succes")
            return redirect(url_for("index"))
        except ValueError as e:
            flash(str(e), "erreur")
            return render_template("form.html", titre="Ajouter un contact", contact=None,
                                    valeurs={"nom": nom, "email": email, "telephone": telephone})

    return render_template("form.html", titre="Ajouter un contact", contact=None, valeurs={})


@app.route("/contacts/<nom>/modifier", methods=["GET", "POST"])
def modifier_contact(nom):
    contact = carnet.rechercher_par_nom(nom)
    if contact is None:
        flash(f"Aucun contact nommé '{nom}' n'a été trouvé.", "erreur")
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        telephone = request.form.get("telephone", "").strip()

        try:
            carnet.modifier_contact(nom, email or None, telephone or None)
            flash(f"Contact '{nom}' mis à jour.", "succes")
            return redirect(url_for("index"))
        except ValueError as e:
            flash(str(e), "erreur")
            return render_template(
                "form.html",
                titre=f"Modifier {nom}",
                contact=contact,
                valeurs={"nom": nom, "email": email, "telephone": telephone},
            )

    return render_template(
        "form.html",
        titre=f"Modifier {nom}",
        contact=contact,
        valeurs={"nom": contact.nom, "email": contact.email, "telephone": contact.telephone},
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
