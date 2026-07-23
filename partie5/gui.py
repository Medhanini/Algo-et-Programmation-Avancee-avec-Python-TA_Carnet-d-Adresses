import tkinter as tk
from tkinter import messagebox, simpledialog

from address_book import AddressBook
from contact import Contact
from login import FenetreConnexion


class CarnetAdressesApp:
    def __init__(self, racine):
        self.carnet = AddressBook()

        self.racine = racine
        self.racine.title("Carnet d'adresses")
        self.racine.geometry("400x450")

        self._construire_zone_titre()
        self._construire_zone_liste()
        self._construire_zone_boutons()

        self.rafraichir_liste()

    def _construire_zone_titre(self):
        cadre_titre = tk.Frame(self.racine, bg="#2c3e50", pady=10)
        cadre_titre.pack(side="top", fill="x")

        tk.Label(
            cadre_titre,
            text="Carnet d'adresses",
            font=("Helvetica", 16, "bold"),
            bg="#2c3e50",
            fg="white",
        ).pack()

        self.label_infos = tk.Label(cadre_titre, text="", bg="#2c3e50", fg="white")
        self.label_infos.pack()

    def _construire_zone_liste(self):
        cadre_liste = tk.Frame(self.racine, padx=10, pady=10)
        cadre_liste.pack(side="top", fill="both", expand=True)

        barre_defilement = tk.Scrollbar(cadre_liste)
        barre_defilement.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            cadre_liste,
            yscrollcommand=barre_defilement.set,
            font=("Courier", 10),
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        barre_defilement.config(command=self.listbox.yview)

    def _construire_zone_boutons(self):
        cadre_boutons = tk.Frame(self.racine, pady=10)
        cadre_boutons.pack(side="bottom", fill="x")

        tk.Button(cadre_boutons, text="Ajouter", width=10, command=self.ajouter_contact).pack(side="left", padx=5)
        tk.Button(cadre_boutons, text="Supprimer", width=10, command=self.supprimer_contact).pack(side="left", padx=5)
        tk.Button(cadre_boutons, text="Actualiser", width=10, command=self.rafraichir_liste).pack(side="left", padx=5)
        tk.Button(cadre_boutons, text="Exporter CSV", width=12, command=self.exporter_csv).pack(side="left", padx=5)

    def rafraichir_liste(self):
        self.listbox.delete(0, tk.END)
        contacts = self.carnet.lister_contacts()
        for contact in contacts:
            self.listbox.insert(tk.END, str(contact))
        self.label_infos.config(text=f"{len(contacts)} contact(s)")

    def ajouter_contact(self):
        nom = simpledialog.askstring("Ajouter un contact", "Nom :", parent=self.racine)
        if not nom:
            return

        email = simpledialog.askstring("Ajouter un contact", "Email :", parent=self.racine)
        if not email:
            return

        telephone = simpledialog.askstring(
            "Ajouter un contact", "Téléphone (ex: 0612345678) :", parent=self.racine
        )
        if not telephone:
            return

        try:
            self.carnet.ajouter_contact(Contact(nom, email, telephone))
            self.rafraichir_liste()
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))

    def supprimer_contact(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un contact à supprimer.")
            return

        ligne = self.listbox.get(selection[0])
        nom = ligne.split("|")[0].strip()

        confirmation = messagebox.askyesno("Confirmation", f"Supprimer le contact '{nom}' ?")
        if not confirmation:
            return

        if self.carnet.supprimer_contact(nom):
            self.rafraichir_liste()
        else:
            messagebox.showerror("Erreur", f"Aucun contact nommé '{nom}' n'a été trouvé.")

    def exporter_csv(self):
        fichier = self.carnet.exporter_csv()
        messagebox.showinfo("Export réussi", f"Contacts exportés vers '{fichier}'.")


def ouvrir_carnet_adresses():
    racine = tk.Tk()
    CarnetAdressesApp(racine)
    racine.mainloop()


def main():
    racine_connexion = tk.Tk()

    def apres_connexion():
        racine_connexion.destroy()
        ouvrir_carnet_adresses()

    FenetreConnexion(racine_connexion, apres_connexion)
    racine_connexion.mainloop()


if __name__ == "__main__":
    main()
