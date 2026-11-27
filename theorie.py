# =============================================================================
# theorie.py — LA THÉORIE DES DÉFAUTS T = (W, D) ET LA SAISIE CONTRÔLÉE
# -----------------------------------------------------------------------------
# Ce module gère les données de l'utilisateur, sans interface graphique :
#   - un DÉFAUT « prérequis : justifications / conséquent » est un dictionnaire ;
#     une THÉORIE est un dictionnaire {"W": [formules], "D": [défauts]} ;
#   - lire_defaut() lit le texte d'un défaut et applique les vérifications du sujet :
#     présence d'un seul « : » et d'un seul « / », chaque partie est une formule
#     correcte, et AVERTISSEMENT si une justification est incohérente (x & ~x)
#     car le défaut ne sera jamais applicable ;
#   - ajouter / supprimer une formule dans W (refuse les doublons), ajouter /
#     supprimer un défaut dans D, vérifier la cohérence de W (W_coherent) ;
#   - type_defaut() classe un défaut : normal, semi-normal ou général ;
#   - theorie_en_dict() / theorie_depuis_dict() convertissent la théorie en texte
#     (utilisé pour la sauvegarde).
# =============================================================================
"""
theorie.py — BLOC 1b : la théorie des défauts T = (W, D), SANS classes.

  • un défaut  = dictionnaire {"prerequis": arbre|None, "justifs": [arbres], "conseq": arbre}
  • une théorie = dictionnaire {"W": [arbres], "D": [défauts]}
Tout le reste ce sont des fonctions. AUCUNE interface ici.
"""
from formules import (ErreurSyntaxe, lire_formule, en_texte, satisfiable,
                      equivalentes, consequence)


# ------------------------------------------------------------ défauts
def texte_defaut(d):
    """Défaut -> 'prérequis : j1, j2 / conséquent'."""
    pre = en_texte(d["prerequis"]) if d["prerequis"] else ""
    just = ", ".join(en_texte(j) for j in d["justifs"])
    return f"{pre} : {just} / {en_texte(d['conseq'])}".strip()


def type_defaut(d):
    """normal : β ≡ γ | semi-normal : une justification β qui implique γ | général."""
    if len(d["justifs"]) == 1 and satisfiable(d["justifs"]):
        b = d["justifs"][0]
        if equivalentes(b, d["conseq"]):
            return "normal"
        if consequence([b], d["conseq"]):
            return "semi-normal"
    return "général"


def _split_virgules(s):
    """Coupe sur les virgules hors parenthèses (garde Pere(ali,omar) intact)."""
    parts, prof, cur = [], 0, ""
    for c in s:
        prof += (c == "(") - (c == ")")
        if c == "," and prof == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    return parts + [cur]


def lire_defaut(texte):
    """'prérequis : j1, j2 / conséquent' -> (défaut, [avertissements]).
    Lève ErreurSyntaxe si le texte est incorrect."""
    if texte.count(":") != 1:
        raise ErreurSyntaxe("Un défaut doit contenir exactement un « : » (prérequis : justifications / conséquent).")
    if texte.count("/") != 1:
        raise ErreurSyntaxe("Un défaut doit contenir exactement un « / » avant le conséquent.")
    if texte.index(":") > texte.index("/"):
        raise ErreurSyntaxe("Ordre incorrect : le « : » doit venir avant le « / ».")
    pre_t, reste = texte.split(":")
    just_t, cons_t = reste.split("/")

    try:
        pre = lire_formule(pre_t) if pre_t.strip() else None
    except ErreurSyntaxe as e:
        raise ErreurSyntaxe(f"Prérequis incorrect : {e}")
    if not just_t.strip():
        raise ErreurSyntaxe("Il faut au moins une justification.")
    justifs = []
    for k, j in enumerate(_split_virgules(just_t), 1):
        try:
            justifs.append(lire_formule(j))
        except ErreurSyntaxe as e:
            raise ErreurSyntaxe(f"Justification n°{k} incorrecte : {e}")
    try:
        cons = lire_formule(cons_t)
    except ErreurSyntaxe as e:
        raise ErreurSyntaxe(f"Conséquent incorrect : {e}")

    avert = []
    for j in justifs:
        if not satisfiable([j]):
            avert.append(f"La justification « {en_texte(j)} » est incohérente : "
                         f"ce défaut ne sera jamais applicable.")
    if len(justifs) > 1 and all(satisfiable([j]) for j in justifs) and not satisfiable(justifs):
        avert.append("Les justifications sont incohérentes entre elles : "
                     "ce défaut ne sera jamais applicable.")
    return {"prerequis": pre, "justifs": justifs, "conseq": cons}, avert


# ------------------------------------------------------ la théorie (W, D)
def nouvelle_theorie():
    return {"W": [], "D": []}


def ajouter_formule(T, texte):
    f = lire_formule(texte)
    if f in T["W"]:
        raise ErreurSyntaxe(f"La formule « {en_texte(f)} » est déjà dans W.")
    T["W"].append(f)
    return f


def supprimer_formule(T, i):
    del T["W"][i]


def W_coherent(T):
    return satisfiable(T["W"])


def ajouter_defaut(T, texte):
    d, avert = lire_defaut(texte)
    if any(texte_defaut(d) == texte_defaut(x) for x in T["D"]):
        raise ErreurSyntaxe(f"Le défaut « {texte_defaut(d)} » existe déjà.")
    T["D"].append(d)
    return d, avert


def supprimer_defaut(T, i):
    del T["D"][i]


def vider(T):
    T["W"].clear()
    T["D"].clear()


# --- sauvegarde (bloc 4) : on stocke du TEXTE, simple et lisible
def theorie_en_dict(T):
    return {"W": [en_texte(f) for f in T["W"]], "D": [texte_defaut(d) for d in T["D"]]}


def theorie_depuis_dict(data):
    T = nouvelle_theorie()
    for s in data.get("W", []):
        ajouter_formule(T, s)
    for s in data.get("D", []):
        ajouter_defaut(T, s)
    return T
