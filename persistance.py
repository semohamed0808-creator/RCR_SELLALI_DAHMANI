# =============================================================================
# persistance.py — SAUVEGARDE ET CHARGEMENT D'UNE THÉORIE
# -----------------------------------------------------------------------------
# Deux formats de fichier :
#   1. JSON (sauvegarder / charger) : enregistre W, D et, si elles ont été
#      calculées, les extensions ; au rechargement on retrouve tout sans recalcul.
#      Un fichier invalide provoque un message d'erreur clair, jamais un plantage.
#   2. Texte .txt, option A du sujet (importer_texte / exporter_texte / lire_texte) :
#      fichier lisible et modifiable à la main avec des sections [W] et [D] (une
#      formule ou un défaut par ligne, commentaires avec #). Une ligne incorrecte
#      est signalée avec son numéro sans bloquer la lecture des autres.
# Les textes sont relus par les mêmes fonctions que la saisie, donc avec les mêmes
# vérifications.
# =============================================================================
"""
persistance.py — BLOC 4 : sauvegarder / recharger une théorie (fichier JSON lisible),
avec ses extensions si elles ont été calculées.
"""
import json
from formules import en_texte, lire_formule
from theorie import theorie_en_dict, theorie_depuis_dict, texte_defaut
from instances import fermer
from extensions import litteraux


def sauvegarder(chemin, T, exts=None, Tg=None):
    """Écrit W, D et (si exts n'est pas None) les extensions dans un fichier JSON."""
    data = theorie_en_dict(T)
    data["version"] = 1
    if exts is not None:
        if Tg is None:
            Tg, _ = fermer(T)
        data["extensions"] = [{
            "generateurs": [en_texte(f) for f in e["generateurs"]],
            "appliques": [texte_defaut(Tg["D"][i]) for i in e["appliques"]],
            "incoherente": e["incoherente"],
            "litteraux": litteraux(e)} for e in exts]
    with open(chemin, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def charger(chemin):
    """Renvoie (T, exts, Tg). exts vaut None si le fichier n'en contient pas."""
    try:
        with open(chemin, encoding="utf-8") as fh:
            data = json.load(fh)
        T = theorie_depuis_dict(data)
        Tg, _ = fermer(T)
        exts = None
        if data.get("extensions") is not None:
            index = {texte_defaut(d): i for i, d in enumerate(Tg["D"])}
            exts = [{"generateurs": [lire_formule(s) for s in e["generateurs"]],
                     "appliques": [index[s] for s in e["appliques"] if s in index],
                     "incoherente": bool(e.get("incoherente", False))}
                    for e in data["extensions"]]
        return T, exts, Tg
    except (OSError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as err:
        raise ValueError(f"Fichier de théorie invalide : {err}")


# ====================================================================
#  Option A du sujet : fichier texte (.txt) lisible et modifiable à la main
# ====================================================================
# Format accepté (lignes vides et commentaires « # ... » ignorés) :
#
#     # Exemple du sujet
#     [W]
#     o
#     p -> o
#     [D]
#     o : v / v
#
# ou, ligne par ligne :   W: p -> o      D: o : v / v
from theorie import nouvelle_theorie, ajouter_formule, ajouter_defaut
from formules import ErreurSyntaxe


def lire_texte(contenu):
    """Texte -> (T, erreurs, avertissements).
    Une ligne incorrecte n'arrête pas la lecture : elle est signalée avec son numéro."""
    T, erreurs, avert = nouvelle_theorie(), [], []
    section = None
    for n, brut in enumerate(contenu.splitlines(), 1):
        ligne = brut.split("#", 1)[0].strip()
        if not ligne:
            continue
        if ligne.upper() in ("[W]", "[D]"):
            section = ligne[1].upper()
            continue
        genre = section
        if ligne[:2].upper() in ("W:", "D:"):
            genre, ligne = ligne[0].upper(), ligne[2:].strip()
        if genre is None:
            erreurs.append(f"Ligne {n} : précisez [W] / [D] ou le préfixe « W: » / « D: ».")
            continue
        try:
            if genre == "W":
                ajouter_formule(T, ligne)
            else:
                _, a = ajouter_defaut(T, ligne)
                avert += [f"Ligne {n} : {m}" for m in a]
        except ErreurSyntaxe as e:
            erreurs.append(f"Ligne {n} : {e}")
    return T, erreurs, avert


def importer_texte(chemin):
    """Lit un fichier .txt de théorie. Renvoie (T, erreurs, avertissements)."""
    try:
        with open(chemin, encoding="utf-8-sig") as fh:      # utf-8-sig : accepte le BOM du Bloc-notes Windows
            return lire_texte(fh.read())
    except (OSError, UnicodeDecodeError) as err:
        raise ValueError(f"Fichier illisible : {err}")


def exporter_texte(chemin, T):
    """Écrit W et D dans un fichier .txt (relisible par importer_texte)."""
    lignes = ["# Théorie des défauts (W, D)", "[W]"] + [en_texte(f) for f in T["W"]]
    lignes += ["", "[D]"] + [texte_defaut(d) for d in T["D"]]
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lignes) + "\n")
