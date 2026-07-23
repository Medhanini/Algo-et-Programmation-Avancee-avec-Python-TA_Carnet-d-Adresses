import tkinter as tk
from tkinter import messagebox

import auth

TENTATIVES_MAX = 3


class FenetreConnexion:
    def __init__(self, racine, on_succes):
        self.racine = racine
        self.on_succes = on_succes
        self.tentatives = 0

        auth.initialiser_admin_par_defaut()

        self.racine.title("Connexion administrateur")
        self.racine.geometry("300x180")
        self.racine.resizable(False, False)

        cadre = tk.Frame(self.racine, padx=20, pady=20)
        cadre.pack(expand=True)

        tk.Label(cadre, text="Connexion administrateur", font=("Helvetica", 12, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 15)
        )

        tk.Label(cadre, text="Utilisateur :").grid(row=1, column=0, sticky="e", pady=5)
        self.entree_utilisateur = tk.Entry(cadre)
        self.entree_utilisateur.grid(row=1, column=1, pady=5)

        tk.Label(cadre, text="Mot de passe :").grid(row=2, column=0, sticky="e", pady=5)
        self.entree_mot_de_passe = tk.Entry(cadre, show="*")
        self.entree_mot_de_passe.grid(row=2, column=1, pady=5)

        tk.Button(cadre, text="Se connecter", command=self.se_connecter).grid(
            row=3, column=0, columnspan=2, pady=(15, 0)
        )

        self.entree_utilisateur.focus()
        self.racine.bind("<Return>", lambda event: self.se_connecter())

    def se_connecter(self):
        nom_utilisateur = self.entree_utilisateur.get().strip()
        mot_de_passe = self.entree_mot_de_passe.get()

        if auth.verifier_identifiants(nom_utilisateur, mot_de_passe):
            self.on_succes()
            return

        self.tentatives += 1
        self.entree_mot_de_passe.delete(0, tk.END)

        if self.tentatives >= TENTATIVES_MAX:
            messagebox.showerror("Accès refusé", "Nombre maximal de tentatives atteint.")
            self.racine.destroy()
        else:
            restantes = TENTATIVES_MAX - self.tentatives
            messagebox.showerror("Erreur", f"Identifiants invalides ({restantes} tentative(s) restante(s)).")
