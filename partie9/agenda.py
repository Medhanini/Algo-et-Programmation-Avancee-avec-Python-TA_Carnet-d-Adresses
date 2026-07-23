import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from rendezvous import GestionnaireRendezVous

COLONNES = 4


class FenetreAgenda(tk.Toplevel):
    def __init__(self, parent, carnet):
        super().__init__(parent)
        self.carnet = carnet
        self.gestionnaire = GestionnaireRendezVous()
        self.boutons_creneaux = {}

        self.title("Agenda des rendez-vous")
        self.geometry("480x480")

        self._construire_zone_selection()
        self._construire_zone_grille()

        self.charger_agenda()

    def _construire_zone_selection(self):
        cadre = tk.Frame(self, pady=10, padx=10)
        cadre.pack(side="top", fill="x")

        tk.Label(cadre, text="Contact :").grid(row=0, column=0, sticky="e", padx=5)
        noms_contacts = [contact.nom for contact in self.carnet.lister_contacts()]
        self.variable_contact = tk.StringVar(value=noms_contacts[0] if noms_contacts else "")
        self.menu_contact = ttk.Combobox(
            cadre, textvariable=self.variable_contact, values=noms_contacts, state="readonly"
        )
        self.menu_contact.grid(row=0, column=1, padx=5)

        tk.Label(cadre, text="Date (AAAA-MM-JJ) :").grid(row=1, column=0, sticky="e", padx=5, pady=(8, 0))
        self.variable_date = tk.StringVar(value=date.today().isoformat())
        tk.Entry(cadre, textvariable=self.variable_date).grid(row=1, column=1, padx=5, pady=(8, 0))

        tk.Button(cadre, text="Charger l'agenda", command=self.charger_agenda).grid(
            row=1, column=2, padx=5, pady=(8, 0)
        )

    def _construire_zone_grille(self):
        self.cadre_grille = tk.Frame(self, padx=10, pady=10)
        self.cadre_grille.pack(side="top", fill="both", expand=True)

    def charger_agenda(self):
        for widget in self.cadre_grille.winfo_children():
            widget.destroy()
        self.boutons_creneaux.clear()

        date_choisie = self.variable_date.get().strip()
        try:
            creneaux_reserves = self.gestionnaire.creneaux_reserves(date_choisie)
        except Exception:
            messagebox.showerror("Erreur", "Format de date invalide (attendu AAAA-MM-JJ).")
            return

        for index, heure in enumerate(self.gestionnaire.creneaux_journee()):
            ligne, colonne = divmod(index, COLONNES)
            contact_reservant = creneaux_reserves.get(heure)

            if contact_reservant:
                texte = f"{heure}\n{contact_reservant}"
                bouton = tk.Button(self.cadre_grille, text=texte, width=12, height=2, state="disabled")
            else:
                bouton = tk.Button(
                    self.cadre_grille,
                    text=heure,
                    width=12,
                    height=2,
                    command=lambda h=heure: self.reserver_creneau(h),
                )

            bouton.grid(row=ligne, column=colonne, padx=4, pady=4)
            self.boutons_creneaux[heure] = bouton

    def reserver_creneau(self, heure):
        nom_contact = self.variable_contact.get().strip()
        if not nom_contact:
            messagebox.showwarning("Attention", "Sélectionnez un contact avant de réserver un créneau.")
            return

        date_choisie = self.variable_date.get().strip()
        try:
            self.gestionnaire.reserver(nom_contact, date_choisie, heure)
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        messagebox.showinfo(
            "Rendez-vous confirmé", f"Rendez-vous réservé pour {nom_contact} le {date_choisie} à {heure}."
        )
        self.charger_agenda()
