# =============================================================================
# instances.py — INSTANCIATION DES DÉFAUTS AVEC VARIABLES (défauts « ouverts »)
# -----------------------------------------------------------------------------
# Un défaut comme  Oiseau(x) : Vole(x) / Vole(x)  contient une variable : c'est un
# schéma qui représente tous ses défauts clos, un par constante de la théorie
# (Oiseau(tweety) : Vole(tweety) / Vole(tweety), etc.). Même principe pour les
# formules de W avec variables (quantification universelle implicite).
# Ce module :
#   - reconnaît les variables (lettres u à z, éventuellement suivies de chiffres) ;
#   - remplace les variables par toutes les constantes possibles (substituer) ;
#   - fermer(T) renvoie la théorie close (sans variables) prête pour le calcul des
#     extensions, avec un message d'information et une limite de sécurité sur le
#     nombre d'instances.
# =============================================================================
"""
instances.py — BLOC 2a : instancier les formules/défauts avec variables.

Convention (comme en cours) : dans P(x, tweety), « x » est une VARIABLE
(lettres u, v, w, x, y, z éventuellement suivies de chiffres), « tweety » une CONSTANTE.
Un défaut ouvert  Oiseau(x) : Vole(x) / Vole(x)  est un schéma qui représente
tous ses défauts clos : un par constante du langage. Idem pour les formules de W.
"""
import re
from itertools import product
from formules import en_texte
from theorie import texte_defaut

_VAR = re.compile(r"^[u-z]\d*$")


def est_variable(s):
    return bool(_VAR.match(s))


def decouper_atome(nom):
    """'P(a,b)' -> ('P', ['a','b']) ; 'p' -> ('p', [])"""
    if "(" not in nom:
        return nom, []
    pred, reste = nom.split("(", 1)
    return pred, reste[:-1].split(",")


def _args(f):
    if f[0] == "atom":
        return decouper_atome(f[1])[1]
    return [a for x in f[1:] for a in _args(x)]


def variables(f):
    return {a for a in _args(f) if est_variable(a)}


def constantes(f):
    return {a for a in _args(f) if not est_variable(a)}


def substituer(f, sub):
    """Remplace les variables de f selon le dictionnaire sub."""
    if f[0] == "atom":
        pred, args = decouper_atome(f[1])
        if not args:
            return f
        return ("atom", f"{pred}({','.join(sub.get(a, a) for a in args)})")
    return (f[0],) + tuple(substituer(x, sub) for x in f[1:])


def _parties(d):
    return ([d["prerequis"]] if d["prerequis"] else []) + d["justifs"] + [d["conseq"]]


def _substituer_defaut(d, sub):
    return {"prerequis": substituer(d["prerequis"], sub) if d["prerequis"] else None,
            "justifs": [substituer(j, sub) for j in d["justifs"]],
            "conseq": substituer(d["conseq"], sub)}


def fermer(T, limite=3000):
    """Théorie (avec variables) -> (théorie close, [infos]).
    Si aucune variable n'est utilisée, T est renvoyée telle quelle."""
    toutes = list(T["W"]) + [p for d in T["D"] for p in _parties(d)]
    if not any(variables(f) for f in toutes):
        return T, []
    consts = sorted(set().union(*(constantes(f) for f in toutes)))
    infos = []
    if not consts:
        infos.append("Aucune constante dans la théorie : les formules avec variables "
                     "ne peuvent pas être instanciées.")

    def instances(vs):
        return [dict(zip(vs, c)) for c in product(consts, repeat=len(vs))]

    W2 = []
    for f in T["W"]:
        for sub in instances(sorted(variables(f))):
            g = substituer(f, sub)
            if g not in W2:
                W2.append(g)
    D2, vus = [], set()
    for d in T["D"]:
        vs = sorted(set().union(*(variables(p) for p in _parties(d))))
        for sub in instances(vs):
            g = _substituer_defaut(d, sub)
            if texte_defaut(g) not in vus:
                vus.add(texte_defaut(g))
                D2.append(g)
    if len(W2) + len(D2) > limite:
        raise ValueError(f"Trop d'instances ({len(W2) + len(D2)}) : réduisez le nombre de constantes.")
    infos.append(f"Instanciation sur {len(consts)} constante(s) ({', '.join(consts)}) : "
                 f"{len(W2)} formule(s) et {len(D2)} défaut(s) clos.")
    return {"W": W2, "D": D2}, infos
