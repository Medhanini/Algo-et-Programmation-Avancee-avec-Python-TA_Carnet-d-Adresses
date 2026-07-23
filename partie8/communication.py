import os
import smtplib
import urllib.parse
from email.message import EmailMessage

SERVEUR_SMTP = os.environ.get("SMTP_SERVEUR", "smtp.gmail.com")
PORT_SMTP = int(os.environ.get("SMTP_PORT", "465"))
EXPEDITEUR = os.environ.get("SMTP_EXPEDITEUR")
MOT_DE_PASSE = os.environ.get("SMTP_MOT_DE_PASSE")

INDICATIF_PAR_DEFAUT = os.environ.get("WHATSAPP_INDICATIF", "33")

MODELES_MESSAGES = {
    "rendezvous": (
        "Confirmation de rendez-vous",
        "Bonjour {nom},\n\n"
        "Nous vous confirmons votre rendez-vous médical.\n"
        "Merci de vous présenter 10 minutes à l'avance avec votre carte vitale.\n\n"
        "Cordialement,\nLe cabinet médical",
    ),
    "resultats": (
        "Résultats d'analyses disponibles",
        "Bonjour {nom},\n\n"
        "Vos résultats d'analyses de laboratoire sont désormais disponibles.\n"
        "Merci de nous contacter pour les récupérer ou pour en discuter avec votre médecin.\n\n"
        "Cordialement,\nLe laboratoire",
    ),
}


def generer_message(cle_modele, nom_contact):
    if cle_modele not in MODELES_MESSAGES:
        raise ValueError(f"Modèle de message inconnu : '{cle_modele}'.")
    sujet, corps = MODELES_MESSAGES[cle_modele]
    return sujet, corps.format(nom=nom_contact)


def envoyer_email(destinataire, sujet, corps):
    if not EXPEDITEUR or not MOT_DE_PASSE:
        raise RuntimeError(
            "Configuration SMTP manquante : définissez les variables d'environnement "
            "SMTP_EXPEDITEUR et SMTP_MOT_DE_PASSE (ex: adresse Gmail + mot de passe d'application)."
        )

    message = EmailMessage()
    message["Subject"] = sujet
    message["From"] = EXPEDITEUR
    message["To"] = destinataire
    message.set_content(corps)

    with smtplib.SMTP_SSL(SERVEUR_SMTP, PORT_SMTP) as serveur:
        serveur.login(EXPEDITEUR, MOT_DE_PASSE)
        serveur.send_message(message)


def construire_lien_whatsapp(numero, message):
    numero = numero.strip()
    if numero.startswith("0"):
        numero_international = INDICATIF_PAR_DEFAUT + numero[1:]
    else:
        numero_international = numero.lstrip("+")

    texte_encode = urllib.parse.quote(message)
    return f"https://wa.me/{numero_international}?text={texte_encode}"
