# =============================================================================
# interface.py — INTERFACE GRAPHIQUE (customtkinter)
# -----------------------------------------------------------------------------
# Ce fichier construit la fenêtre et relie les boutons aux autres modules :
#   - panneau « Monde W » : saisie des formules, liste, suppression, bouton
#     « Vérifier la cohérence de W » ;
#   - panneau « Défauts D » : saisie par champs (prérequis, justifications,
#     conséquent) ou en texte libre, avec messages d'erreur et avertissements ;
#   - barre d'actions : « Générer les extensions », « Sceptique ? », « Crédule ? » ;
#   - zone de résultats : extensions, littéraux, et onglet « Explication pas à pas » ;
#   - barre d'outils : Nouveau, Ouvrir, Enregistrer (JSON), Importer / Exporter
#     .txt, menu Exemples, mode clair / sombre.
# RÈGLE DU SUJET : l'interface ne fait AUCUN calcul logique. Elle lit la saisie,
# appelle les fonctions des modules (formules, theorie, instances, extensions,
# persistance) et affiche leurs résultats.
# =============================================================================
"""
interface.py — BLOC 5 : l'interface graphique (customtkinter).

RÈGLE DU SUJET : l'interface ne fait AUCUN calcul logique. Elle lit ce que
l'utilisateur écrit, appelle les fonctions des autres modules, et affiche.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from formules import lire_formule, en_texte
from theorie import (nouvelle_theorie, ajouter_formule, supprimer_formule, W_coherent,
                     ajouter_defaut, supprimer_defaut, vider, texte_defaut, type_defaut)
from instances import fermer, variables
from extensions import (calculer_extensions, sceptique, credule, niveau, NIVEAUX,
                        litteraux, texte_extension, expliquer)
from persistance import sauvegarder, charger, importer_texte, exporter_texte
from exemples import EXEMPLES

# ------------------------------------------------------------------ style
VIOLET, VIOLET_H = "#6c63ff", "#5a52e0"
VERT, ROUGE, ORANGE, GRIS = "#22b07d", "#e5484d", "#f0a020", "#8b90a8"
FOND = ("#eef0f7", "#0e1120")
CARTE = ("#ffffff", "#171b2e")
LIGNE = ("#f1f3fa", "#20253d")
TEXTE = ("#1b1f33", "#e8eaf6")
TYPE_COULEUR = {"normal": VERT, "semi-normal": ORANGE, "général": ROUGE}


def lancer():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk(fg_color=FOND)
    app.title("Logique des défauts · Reiter")
    app.geometry("1280x900")
    app.minsize(1100, 700)

    MONO = ctk.CTkFont(family="Consolas", size=14)
    MONO_B = ctk.CTkFont(family="Consolas", size=14, weight="bold")
    TITRE = ctk.CTkFont(size=13, weight="bold")
    NORMAL = ctk.CTkFont(size=13)

    # --- état du programme (la théorie + le dernier calcul)
    T = nouvelle_theorie()
    etat = {"exts": None, "Tg": None, "actif": None, "chemin": None}

    # ================================================== en-tête + barre d'outils
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(2, weight=0)
    app.grid_rowconfigure(4, weight=1)

    entete = ctk.CTkFrame(app, fg_color="transparent")
    entete.grid(row=0, column=0, sticky="ew", padx=22, pady=(16, 4))
    entete.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(entete, text="◆", font=ctk.CTkFont(size=30), text_color=VIOLET).grid(row=0, column=0, rowspan=2, padx=(0, 10))
    ctk.CTkLabel(entete, text="Logique des défauts", font=ctk.CTkFont(size=24, weight="bold"),
                 text_color=TEXTE, anchor="w").grid(row=0, column=1, sticky="w")
    ctk.CTkLabel(entete, text="Théories (W, D) de Reiter · extensions · conséquences sceptiques et crédules",
                 font=NORMAL, text_color=GRIS, anchor="w").grid(row=1, column=1, sticky="w")

    barre = ctk.CTkFrame(entete, fg_color="transparent")
    barre.grid(row=0, column=2, rowspan=2, sticky="e")

    def bouton(parent, texte, cmd, couleur=VIOLET, survol=VIOLET_H, largeur=None, **kw):
        return ctk.CTkButton(parent, text=texte, command=cmd, fg_color=couleur, hover_color=survol,
                             corner_radius=10, height=36, font=TITRE, width=largeur or 100, **kw)

    # ================================================== palette de symboles
    palette = ctk.CTkFrame(app, fg_color="transparent")
    palette.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 6))
    ctk.CTkLabel(palette, text="Symboles :", font=NORMAL, text_color=GRIS).pack(side="left", padx=(2, 8))

    def inserer(symbole):
        e = etat["actif"]
        if e is not None:
            e.insert("insert", symbole)
            e.focus_set()

    for s in ["¬", "∧", "∨", "→", "↔"]:
        ctk.CTkButton(palette, text=s, width=40, height=30, corner_radius=8, font=MONO_B,
                      fg_color=CARTE, hover_color=VIOLET, text_color=TEXTE,
                      command=lambda s=s: inserer(s)).pack(side="left", padx=3)
    ctk.CTkLabel(palette, text="  (ou au clavier :  ~   &   |   ->   <->  )", font=NORMAL,
                 text_color=GRIS).pack(side="left")

    # ================================================== panneaux W et D
    panneaux = ctk.CTkFrame(app, fg_color="transparent")
    panneaux.grid(row=2, column=0, sticky="nsew", padx=22, pady=4)
    panneaux.configure(height=330)          # hauteur fixe : le reste de la fenêtre va aux résultats
    panneaux.grid_propagate(False)
    panneaux.grid_columnconfigure((0, 1), weight=1, uniform="p")
    panneaux.grid_rowconfigure(0, weight=1)

    def carte(col, titre, sous_titre):
        c = ctk.CTkFrame(panneaux, fg_color=CARTE, corner_radius=16)
        c.grid(row=0, column=col, sticky="nsew", padx=(0, 8) if col == 0 else (8, 0))
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(4, weight=1)
        ctk.CTkLabel(c, text=titre, font=ctk.CTkFont(size=15, weight="bold"), text_color=VIOLET,
                     anchor="w").grid(row=0, column=0, sticky="w", padx=18, pady=(14, 0))
        ctk.CTkLabel(c, text=sous_titre, font=NORMAL, text_color=GRIS,
                     anchor="w").grid(row=1, column=0, sticky="w", padx=18)
        return c

    def champ(parent, placeholder, **kw):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder, font=MONO, height=38, corner_radius=10, **kw)
        e.bind("<FocusIn>", lambda ev, e=e: etat.__setitem__("actif", e), add="+")
        return e

    def message(label, texte, genre):
        label.configure(text=texte, text_color={"ok": VERT, "erreur": ROUGE, "avert": ORANGE}[genre])

    # ------------------------------------------------------------ monde W
    cW = carte(0, "MONDE  W", "Faits et règles certains   ·   ex.  Oiseau(tweety),  p → o")
    ligne = ctk.CTkFrame(cW, fg_color="transparent")
    ligne.grid(row=2, column=0, sticky="ew", padx=18, pady=(10, 0))
    ligne.grid_columnconfigure(0, weight=1)
    entree_W = champ(ligne, "Formule…")
    entree_W.grid(row=0, column=0, sticky="ew")
    msg_W = ctk.CTkLabel(cW, text="", font=NORMAL, anchor="w", justify="left", wraplength=520)
    msg_W.grid(row=3, column=0, sticky="w", padx=18, pady=(4, 0))
    liste_W = ctk.CTkScrollableFrame(cW, fg_color="transparent", height=70)
    liste_W.grid(row=4, column=0, sticky="nsew", padx=10, pady=6)
    pied_W = ctk.CTkFrame(cW, fg_color="transparent")
    pied_W.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 14))

    # ------------------------------------------------------------ défauts D
    cD = carte(1, "DÉFAUTS  D", "Règles révisables   ·   prérequis : justifications / conséquent")
    mode = ctk.CTkSegmentedButton(cD, values=["Champs", "Texte libre"], selected_color=VIOLET,
                                  selected_hover_color=VIOLET_H, font=NORMAL)
    mode.set("Champs")
    mode.grid(row=2, column=0, sticky="w", padx=18, pady=(10, 0))

    zone_saisie = ctk.CTkFrame(cD, fg_color="transparent")
    zone_saisie.grid(row=3, column=0, sticky="ew", padx=18, pady=(8, 0))
    zone_saisie.grid_columnconfigure(0, weight=1)
    cadre_champs = ctk.CTkFrame(zone_saisie, fg_color="transparent")
    cadre_champs.grid(row=0, column=0, sticky="ew")
    cadre_champs.grid_columnconfigure((0, 1, 2), weight=1, uniform="c")
    e_pre = champ(cadre_champs, "Prérequis α")
    e_jus = champ(cadre_champs, "Justifications β")
    e_con = champ(cadre_champs, "Conséquent γ")
    e_pre.grid(row=0, column=0, sticky="ew", padx=(0, 4))
    e_jus.grid(row=0, column=1, sticky="ew", padx=4)
    e_con.grid(row=0, column=2, sticky="ew", padx=(4, 0))
    e_libre = champ(zone_saisie, "ex.   Oiseau(x) : Vole(x) / Vole(x)")

    def changer_mode(valeur):
        if valeur == "Champs":
            e_libre.grid_remove()
            cadre_champs.grid(row=0, column=0, sticky="ew")
        else:
            cadre_champs.grid_remove()
            e_libre.grid(row=0, column=0, sticky="ew")

    mode.configure(command=changer_mode)
    msg_D = ctk.CTkLabel(cD, text="", font=NORMAL, anchor="w", justify="left", wraplength=520)
    msg_D.grid(row=3, column=0, sticky="sw", padx=18, pady=(0, 0))
    # le message est placé sous la saisie : on utilise la ligne 3 de zone_saisie
    msg_D.grid_forget()
    msg_D = ctk.CTkLabel(zone_saisie, text="", font=NORMAL, anchor="w", justify="left", wraplength=520)
    msg_D.grid(row=1, column=0, sticky="w", pady=(4, 0))
    liste_D = ctk.CTkScrollableFrame(cD, fg_color="transparent", height=70)
    liste_D.grid(row=4, column=0, sticky="nsew", padx=10, pady=6)
    pied_D = ctk.CTkFrame(cD, fg_color="transparent")
    pied_D.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 14))

    # ================================================== barre d'action
    action = ctk.CTkFrame(app, fg_color=CARTE, corner_radius=16)
    action.grid(row=3, column=0, sticky="ew", padx=22, pady=8)
    action.grid_columnconfigure(1, weight=1)
    b_gen = bouton(action, "⚡  Générer les extensions", lambda: generer(), largeur=220)
    b_gen.configure(height=42)
    b_gen.grid(row=0, column=0, padx=(14, 10), pady=12)
    entree_phi = champ(action, "Formule φ à tester…   ex.  Vole(tweety)")
    entree_phi.grid(row=0, column=1, sticky="ew", padx=6)
    bouton(action, "Sceptique ?", lambda: tester("sceptique"), VERT, "#1a8f65", 130).grid(row=0, column=2, padx=4)
    bouton(action, "Crédule ?", lambda: tester("credule"), ORANGE, "#d08a14", 120).grid(row=0, column=3, padx=(4, 14))
    verdict = ctk.CTkLabel(action, text="", font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
                           justify="left", wraplength=1100)
    verdict.grid(row=1, column=0, columnspan=4, sticky="w", padx=18, pady=(0, 10))

    # ================================================== résultats
    # onglets maison (plus fiables que CTkTabview avec les zones de texte)
    zone_res = ctk.CTkFrame(app, fg_color=CARTE, corner_radius=16)
    zone_res.grid(row=4, column=0, sticky="nsew", padx=22, pady=(0, 6))
    zone_res.grid_columnconfigure(0, weight=1)
    zone_res.grid_rowconfigure(1, weight=1)
    t_res = ctk.CTkFrame(zone_res, fg_color="transparent")
    t_exp = ctk.CTkFrame(zone_res, fg_color="transparent")
    for t in (t_res, t_exp):
        t.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        t.grid_columnconfigure(0, weight=1)
    t_res.grid_rowconfigure(0, weight=1)
    t_exp.grid_rowconfigure(1, weight=1)

    def choisir_onglet(nom):
        (t_res if nom == "Résultats" else t_exp).tkraise()

    onglets = ctk.CTkSegmentedButton(zone_res, values=["Résultats", "Explication pas à pas"],
                                     selected_color=VIOLET, selected_hover_color=VIOLET_H,
                                     font=TITRE, command=choisir_onglet)
    onglets.set("Résultats")
    onglets.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))
    t_res.tkraise()

    def zone_texte(parent, ligne):
        z = ctk.CTkTextbox(parent, font=MONO, wrap="word", fg_color=LIGNE, corner_radius=12, state="disabled", height=90)
        z.grid(row=ligne, column=0, sticky="nsew", padx=4, pady=4)
        for nom, coul in [("titre", VIOLET), ("ok", VERT), ("ko", ROUGE), ("avert", ORANGE), ("gris", GRIS)]:
            z.tag_config(nom, foreground=coul)
        return z

    def ecrire(z, morceaux, effacer=True):
        z.configure(state="normal")
        if effacer:
            z.delete("1.0", "end")
        for texte, tag in morceaux:
            z.insert("end", texte, tag) if tag else z.insert("end", texte)
        z.configure(state="disabled")

    res = zone_texte(t_res, 0)
    exp_choix = ctk.CTkSegmentedButton(t_exp, values=["—"], selected_color=VIOLET,
                                       selected_hover_color=VIOLET_H, font=NORMAL)
    exp_choix.grid(row=0, column=0, sticky="w", padx=6, pady=(4, 0))
    exp = zone_texte(t_exp, 1)

    statut = ctk.CTkLabel(app, text="Prêt.", font=NORMAL, text_color=GRIS, anchor="w")
    statut.grid(row=5, column=0, sticky="ew", padx=26, pady=(0, 8))

    # ================================================== affichage des listes
    def rafraichir_W():
        for w in liste_W.winfo_children():
            w.destroy()
        if not T["W"]:
            ctk.CTkLabel(liste_W, text="Aucune formule. Ajoutez les faits certains du monde.",
                         text_color=GRIS, font=NORMAL).pack(pady=18)
        for i, f in enumerate(T["W"]):
            l = ctk.CTkFrame(liste_W, corner_radius=10, fg_color=LIGNE)
            l.pack(fill="x", pady=3, padx=2)
            ctk.CTkLabel(l, text=f"{i + 1}.", width=30, text_color=GRIS, font=MONO).pack(side="left", padx=(8, 0))
            ctk.CTkLabel(l, text=en_texte(f), font=MONO, anchor="w", text_color=TEXTE).pack(side="left", padx=6, fill="x", expand=True)
            ctk.CTkButton(l, text="✕", width=30, height=26, fg_color="transparent", hover_color=ROUGE,
                          text_color=GRIS, command=lambda i=i: retirer_W(i)).pack(side="right", padx=6, pady=4)

    def rafraichir_D():
        for w in liste_D.winfo_children():
            w.destroy()
        if not T["D"]:
            ctk.CTkLabel(liste_D, text="Aucun défaut. Ajoutez des règles « sauf exception ».",
                         text_color=GRIS, font=NORMAL).pack(pady=18)
        for i, d in enumerate(T["D"]):
            l = ctk.CTkFrame(liste_D, corner_radius=10, fg_color=LIGNE)
            l.pack(fill="x", pady=3, padx=2)
            ctk.CTkLabel(l, text=f"d{i + 1}", width=34, text_color=VIOLET, font=MONO_B).pack(side="left", padx=(8, 0))
            ctk.CTkLabel(l, text=texte_defaut(d), font=MONO, anchor="w", text_color=TEXTE).pack(side="left", padx=6, fill="x", expand=True)
            ctk.CTkLabel(l, text=type_defaut(d), font=ctk.CTkFont(size=11, weight="bold"), text_color="white",
                         fg_color=TYPE_COULEUR[type_defaut(d)], corner_radius=8, width=76,
                         height=22).pack(side="right", padx=(0, 4))
            ctk.CTkButton(l, text="✕", width=30, height=26, fg_color="transparent", hover_color=ROUGE,
                          text_color=GRIS, command=lambda i=i: retirer_D(i)).pack(side="right", padx=4, pady=4)

    def invalider(texte="Théorie modifiée : régénérez les extensions."):
        etat["exts"], etat["Tg"] = None, None
        verdict.configure(text="")
        ecrire(res, [(texte, "gris")])
        ecrire(exp, [("", None)])
        exp_choix.configure(values=["—"])
        exp_choix.set("—")

    def rafraichir_tout():
        rafraichir_W()
        rafraichir_D()

    # ================================================== actions W / D
    def ajout_W():
        try:
            ajouter_formule(T, entree_W.get())
        except ValueError as err:
            return message(msg_W, f"✖ {err}", "erreur")
        entree_W.delete(0, "end")
        invalider()
        rafraichir_W()
        if W_coherent(T):
            message(msg_W, "✔ Formule ajoutée.", "ok")
        else:
            message(msg_W, "⚠ W est maintenant incohérent.", "avert")

    def retirer_W(i):
        supprimer_formule(T, i)
        invalider()
        rafraichir_W()
        message(msg_W, "Formule supprimée.", "ok")

    def verifier_W():
        if not T["W"]:
            return message(msg_W, "W est vide (donc cohérent).", "ok")
        if W_coherent(T):
            message(msg_W, "✔ W est cohérent.", "ok")
        else:
            message(msg_W, "✖ W est incohérent : aucune interprétation ne satisfait toutes ses formules.", "erreur")

    def ajout_D():
        if mode.get() == "Champs":
            texte = f"{e_pre.get()} : {e_jus.get()} / {e_con.get()}"
        else:
            texte = e_libre.get()
        try:
            d, avert = ajouter_defaut(T, texte)
        except ValueError as err:
            return message(msg_D, f"✖ {err}", "erreur")
        for e in (e_pre, e_jus, e_con, e_libre):
            e.delete(0, "end")
        invalider()
        rafraichir_D()
        if avert:
            message(msg_D, "⚠ " + " ".join(avert), "avert")
        else:
            message(msg_D, f"✔ Défaut ajouté ({type_defaut(d)}).", "ok")

    def retirer_D(i):
        supprimer_defaut(T, i)
        invalider()
        rafraichir_D()
        message(msg_D, "Défaut supprimé.", "ok")

    bouton(ligne, "Ajouter", ajout_W, largeur=100).grid(row=0, column=1, padx=(8, 0))
    bouton(pied_W, "Vérifier la cohérence de W", verifier_W, CARTE, VIOLET_H, 220,
           border_width=1, border_color=VIOLET, text_color=VIOLET).pack(side="left")
    bouton(zone_saisie, "Ajouter", ajout_D, largeur=100).grid(row=0, column=1, padx=(8, 0), sticky="n")
    bouton(pied_D, "Tout effacer", lambda: tout_effacer(), CARTE, ROUGE, 140,
           border_width=1, border_color=ROUGE, text_color=ROUGE).pack(side="left")
    for e in (entree_W,):
        e.bind("<Return>", lambda ev: ajout_W())
    for e in (e_pre, e_jus, e_con, e_libre):
        e.bind("<Return>", lambda ev: ajout_D())

    # ================================================== calcul et affichage
    def generer():
        try:
            Tg, infos = fermer(T)
            exts = calculer_extensions(Tg)
        except (ValueError, RuntimeError) as err:
            return messagebox.showerror("Calcul impossible", str(err))
        etat["Tg"], etat["exts"] = Tg, exts
        afficher_extensions(infos)
        statut.configure(text=f"{len(exts)} extension(s) calculée(s).", text_color=VERT)
        verdict.configure(text="")

    def afficher_extensions(infos=()):
        exts = etat["exts"]
        m = []
        for i in infos:
            m.append((f"ℹ {i}\n", "gris"))
        if not exts:
            m += [("Aucune extension.\n", "ko"),
                  ("Cette théorie n'a aucun ensemble de croyances cohérent : un défaut détruit sa propre "
                   "justification (ex. « : a / ¬a »).\n", "gris")]
        else:
            m.append((f"{len(exts)} extension{'s' if len(exts) > 1 else ''}\n\n", "titre"))
            for k, e in enumerate(exts, 1):
                m.append((texte_extension(e, k) + "\n", "ok" if not e["incoherente"] else "ko"))
                lits = litteraux(e)
                if lits:
                    m.append(("      littéraux : " + ", ".join(lits) + "\n", "gris"))
                m.append(("\n", None))
        ecrire(res, m)
        # onglet explication
        noms = [f"E{k}" for k in range(1, len(exts) + 1)] or ["—"]
        exp_choix.configure(values=noms, command=afficher_explication)
        exp_choix.set(noms[0])
        afficher_explication(noms[0])

    def afficher_explication(nom):
        exts, Tg = etat["exts"], etat["Tg"]
        if not exts or nom == "—":
            return ecrire(exp, [("Aucune extension à expliquer.", "gris")])
        k = int(nom[1:]) - 1
        m = [(texte_extension(exts[k], k + 1) + "\n\n", "titre")]
        icones = {"applique": ("✔ ", "ok"), "bloque": ("✖ ", "ko"), "inapplicable": ("○ ", "avert")}
        for ligne_ in expliquer(Tg, exts[k]):
            ic, tag = icones[ligne_["etat"]]
            m.append((f"{ic}d{ligne_['indice']}  {ligne_['texte']}\n", tag))
            m.append((f"      {ligne_['detail']}\n\n", "gris"))
        if not Tg["D"]:
            m.append(("Aucun défaut dans cette théorie.", "gris"))
        ecrire(exp, m)

    def tester(genre):
        try:
            phi = lire_formule(entree_phi.get())
        except ValueError as err:
            return verdict.configure(text=f"✖ φ incorrecte : {err}", text_color=ROUGE)
        if variables(phi):
            return verdict.configure(text="✖ φ doit être close (sans variables x, y, z…) : "
                                          "utilisez des constantes, ex. Vole(tweety).", text_color=ROUGE)
        if etat["exts"] is None:
            generer()
            if etat["exts"] is None:
                return
        exts = etat["exts"]
        phi_t = en_texte(phi)
        n = sum(1 for e in exts if sceptique([e], phi))
        if genre == "sceptique":
            ok = sceptique(exts, phi)
            txt = f"Sceptique : {'OUI ✔' if ok else 'NON ✖'}   ·   φ = {phi_t} est dans {n} extension(s) sur {len(exts)}"
        else:
            ok = credule(exts, phi)
            txt = f"Crédule : {'OUI ✔' if ok else 'NON ✖'}   ·   φ = {phi_t} est dans {n} extension(s) sur {len(exts)}"
        if not exts:
            txt += "   (aucune extension : le sceptique est trivialement vrai)"
        txt += f"\nNiveau de croyance {NIVEAUX[niveau(etat['Tg'], exts, phi)]}"
        verdict.configure(text=txt, text_color=VERT if ok else ROUGE)

    def tout_effacer():
        if (T["W"] or T["D"]) and not messagebox.askyesno("Tout effacer", "Effacer W et D ?"):
            return
        vider(T)
        invalider("Théorie vide.")
        rafraichir_tout()

    # ================================================== fichier / exemples
    def nouveau():
        tout_effacer()
        etat["chemin"] = None

    def enregistrer():
        chemin = filedialog.asksaveasfilename(defaultextension=".json", initialfile="theorie.json",
                                              filetypes=[("Théorie des défauts", "*.json")])
        if not chemin:
            return
        try:
            sauvegarder(chemin, T, etat["exts"], etat["Tg"])
        except (OSError, ValueError) as err:
            return messagebox.showerror("Enregistrement impossible", str(err))
        statut.configure(text=f"Théorie enregistrée : {chemin}", text_color=VERT)

    def ouvrir():
        chemin = filedialog.askopenfilename(filetypes=[("Théorie des défauts", "*.json")])
        if not chemin:
            return
        try:
            T2, exts, Tg = charger(chemin)
        except ValueError as err:
            return messagebox.showerror("Ouverture impossible", str(err))
        vider(T)
        T["W"].extend(T2["W"])
        T["D"].extend(T2["D"])
        rafraichir_tout()
        if exts is not None:
            etat["exts"], etat["Tg"] = exts, Tg
            afficher_extensions()
            statut.configure(text=f"Théorie et {len(exts)} extension(s) rechargées.", text_color=VERT)
        else:
            invalider("Théorie chargée. Cliquez sur « Générer les extensions ».")
            statut.configure(text="Théorie rechargée.", text_color=VERT)
        verdict.configure(text="")

    def importer_txt():
        chemin = filedialog.askopenfilename(filetypes=[("Fichier texte", "*.txt")])
        if not chemin:
            return
        try:
            T2, erreurs, avert = importer_texte(chemin)
        except ValueError as err:
            return messagebox.showerror("Import impossible", str(err))
        vider(T)
        T["W"].extend(T2["W"])
        T["D"].extend(T2["D"])
        rafraichir_tout()
        invalider("Fichier importé. Cliquez sur « Générer les extensions ».")
        statut.configure(text=f"Import : {len(T['W'])} formule(s), {len(T['D'])} défaut(s).", text_color=VERT)
        if erreurs or avert:
            messagebox.showwarning("Import terminé avec remarques", "\n".join(erreurs + avert))

    def exporter_txt():
        chemin = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="theorie.txt",
                                              filetypes=[("Fichier texte", "*.txt")])
        if not chemin:
            return
        try:
            exporter_texte(chemin, T)
        except OSError as err:
            return messagebox.showerror("Export impossible", str(err))
        statut.configure(text=f"Théorie exportée : {chemin}", text_color=VERT)

    def charger_exemple(nom):
        menu_ex.set("Exemples  ▾")
        if nom not in EXEMPLES:
            return
        vider(T)
        for s in EXEMPLES[nom]["W"]:
            ajouter_formule(T, s)
        for s in EXEMPLES[nom]["D"]:
            ajouter_defaut(T, s)
        rafraichir_tout()
        invalider("Exemple chargé. Cliquez sur « Générer les extensions ».")
        statut.configure(text=f"Exemple : {nom}", text_color=VIOLET)
        msg_W.configure(text="")
        msg_D.configure(text="")

    bouton(barre, "Nouveau", nouveau, CARTE, VIOLET, 100, text_color=TEXTE).pack(side="left", padx=3)
    bouton(barre, "Ouvrir", ouvrir, CARTE, VIOLET, 90, text_color=TEXTE).pack(side="left", padx=3)
    bouton(barre, "Enregistrer", enregistrer, CARTE, VIOLET, 110, text_color=TEXTE).pack(side="left", padx=3)
    bouton(barre, "Importer .txt", importer_txt, CARTE, VIOLET, 120, text_color=TEXTE).pack(side="left", padx=3)
    bouton(barre, "Exporter .txt", exporter_txt, CARTE, VIOLET, 120, text_color=TEXTE).pack(side="left", padx=3)
    menu_ex = ctk.CTkOptionMenu(barre, values=list(EXEMPLES), command=charger_exemple, width=190, height=36,
                                corner_radius=10, fg_color=VIOLET, button_color=VIOLET_H,
                                button_hover_color=VIOLET_H, font=TITRE)
    menu_ex.set("Exemples  ▾")
    menu_ex.pack(side="left", padx=(3, 12))
    ctk.CTkSwitch(barre, text="Mode clair", font=NORMAL, progress_color=VIOLET,
                  command=lambda: ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark")
                  ).pack(side="left")

    rafraichir_tout()
    invalider("Bienvenue ! Saisissez W et D (ou chargez un exemple), puis cliquez sur « Générer les extensions ».")
    app.mainloop()
