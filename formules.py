# =============================================================================
# formules.py — LECTURE DES FORMULES ET RAISONNEMENT CLASSIQUE
# -----------------------------------------------------------------------------
# Ce module sait faire quatre choses, sans aucune interface graphique :
#   1. LIRE une formule écrite en texte (« p -> ~Vole(x) ») et la transformer en
#      arbre (tuples) : analyse lexicale (lexer) puis analyse par descente
#      récursive. Priorités : ¬ > ∧ > ∨ > → > ↔ ; signale les erreurs de syntaxe
#      avec un message clair (lire_formule, ErreurSyntaxe).
#   2. AFFICHER une formule sous forme de texte lisible (en_texte, negation, atomes).
#   3. TESTER LA SATISFIABILITÉ d'un ensemble de formules (satisfiable) : recherche
#      avec élagage, en logique à trois valeurs (vrai / faux / indéterminé).
#   4. TESTER LA CONSÉQUENCE LOGIQUE (consequence) : W ⊨ f si et seulement si
#      W ∪ {¬f} est insatisfiable ; et l'équivalence de deux formules (equivalentes).
# Ces fonctions servent de base à tous les autres modules.
# =============================================================================
"""
formules.py — BLOC 1a : lire et manipuler des formules logiques.
AUCUNE interface ici : ce module ne fait que du calcul logique.

Une formule est un tuple (arbre) :
    ("atom", "p")  ("not", f)  ("and", f, g)  ("or", f, g)
    ("imp", f, g)  ("iff", f, g)
Symboles acceptés :  ~ ou ¬ | & ou ∧ | | ou ∨ | -> ou → | <-> ou ↔
Atomes : propositions (p, o, Q) ou prédicats clos (Oiseau(tweety), Pere(ali,omar)).
Règle du cours : prédicat = Majuscule, constante/variable = minuscule.
"""
import re


ErreurSyntaxe = ValueError   # erreur de lecture, avec un message clair


# ---------------------------------------------------------------- lexer
_SPEC = [("IFF", r"<->|<=>|↔"), ("IMP", r"->|=>|→"), ("AND", r"&&|&|∧"),
         ("OR", r"\|\||\||∨"), ("NOT", r"~|!|¬"), ("LP", r"\("), ("RP", r"\)"),
         ("COMMA", r","), ("ID", r"[^\W\d]\w*"), ("WS", r"\s+")]
_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in _SPEC))


def _lexer(texte):
    toks, pos = [], 0
    while pos < len(texte):
        m = _RE.match(texte, pos)
        if not m:
            raise ErreurSyntaxe(f"Caractère inattendu « {texte[pos]} » (position {pos + 1}).")
        if m.lastgroup != "WS":
            toks.append((m.lastgroup, m.group(), pos + 1))
        pos = m.end()
    return toks


# --------------------------------------------------------------- parseur
# Chaque fonction lit à partir de la position i et renvoie (arbre, nouvelle_position).
# Priorités : ¬ > ∧ > ∨ > → > ↔

def _type(toks, i):
    return toks[i][0] if i < len(toks) else None


def _iff(toks, i):
    g, i = _imp(toks, i)
    while _type(toks, i) == "IFF":
        d, i = _imp(toks, i + 1)
        g = ("iff", g, d)
    return g, i


def _imp(toks, i):
    g, i = _ou(toks, i)
    if _type(toks, i) == "IMP":            # associatif à droite
        d, i = _imp(toks, i + 1)
        return ("imp", g, d), i
    return g, i


def _ou(toks, i):
    g, i = _et(toks, i)
    while _type(toks, i) == "OR":
        d, i = _et(toks, i + 1)
        g = ("or", g, d)
    return g, i


def _et(toks, i):
    g, i = _non(toks, i)
    while _type(toks, i) == "AND":
        d, i = _non(toks, i + 1)
        g = ("and", g, d)
    return g, i


def _non(toks, i):
    if _type(toks, i) == "NOT":
        g, i = _non(toks, i + 1)
        return ("not", g), i
    return _atome(toks, i)


def _atome(toks, i):
    if i >= len(toks):
        raise ErreurSyntaxe("Formule incomplète : il manque une opérande.")
    k, v, pos = toks[i]
    if k == "ID":
        i += 1
        if _type(toks, i) != "LP":
            return ("atom", v), i
        if not v[0].isupper():
            raise ErreurSyntaxe(f"Le prédicat « {v} » doit commencer par une majuscule "
                                f"(ex. {v.capitalize()}(x)).")
        i += 1
        args = []
        while True:
            if _type(toks, i) != "ID":
                raise ErreurSyntaxe(f"Argument attendu dans {v}(...).")
            a = toks[i][1]
            i += 1
            if a[0].isupper():
                raise ErreurSyntaxe(f"L'argument « {a} » de {v} doit commencer par une minuscule.")
            args.append(a)
            if _type(toks, i) == "COMMA":
                i += 1
                continue
            break
        if _type(toks, i) != "RP":
            raise ErreurSyntaxe(f"Parenthèse fermante manquante après {v}(...).")
        return ("atom", f"{v}({','.join(args)})"), i + 1
    if k == "LP":
        g, i = _iff(toks, i + 1)
        if _type(toks, i) != "RP":
            raise ErreurSyntaxe("Parenthèse fermante « ) » manquante.")
        return g, i + 1
    raise ErreurSyntaxe(f"Symbole inattendu « {v} » (position {pos}).")


def lire_formule(texte):
    """Texte -> arbre. Lève ErreurSyntaxe si la formule est incorrecte."""
    if texte is None or not texte.strip():
        raise ErreurSyntaxe("La formule est vide.")
    toks = _lexer(texte)
    f, i = _iff(toks, 0)
    if i < len(toks):
        raise ErreurSyntaxe(f"Symbole inattendu « {toks[i][1]} » (position {toks[i][2]}).")
    return f


# -------------------------------------------------------------- affichage
_PREC = {"iff": 1, "imp": 2, "or": 3, "and": 4}
_SYM = {"iff": " ↔ ", "imp": " → ", "or": " ∨ ", "and": " ∧ "}


def en_texte(f, parent=0):
    """Arbre -> texte lisible (parenthèses minimales)."""
    t = f[0]
    if t == "atom":
        return f[1]
    if t == "not":
        return "¬" + en_texte(f[1], 5)
    p = _PREC[t]
    if t == "imp":
        g, d = en_texte(f[1], p + 1), en_texte(f[2], p)
    elif t == "iff":
        g, d = en_texte(f[1], p + 1), en_texte(f[2], p + 1)
    else:
        g, d = en_texte(f[1], p), en_texte(f[2], p + 1)
    s = g + _SYM[t] + d
    return f"({s})" if p < parent else s


def negation(f):
    """¬f en évitant la double négation (¬¬a devient a)."""
    return f[1] if f[0] == "not" else ("not", f)


def atomes(f):
    """Ensemble des atomes d'une formule."""
    return {f[1]} if f[0] == "atom" else set().union(*(atomes(x) for x in f[1:]))


# ------------------------------------------------- raisonnement (SAT / ⊨)
def _eval3(f, v):
    """Évaluation à 3 valeurs : True / False / None (pas encore décidé)."""
    t = f[0]
    if t == "atom":
        return v.get(f[1])
    a = _eval3(f[1], v)
    if t == "not":
        return None if a is None else (not a)
    b = _eval3(f[2], v)
    if t == "and":
        if a is False or b is False: return False
        return True if (a is True and b is True) else None
    if t == "or":
        if a is True or b is True: return True
        return False if (a is False and b is False) else None
    if t == "imp":
        if a is False or b is True: return True
        return False if (a is True and b is False) else None
    if a is None or b is None:        # iff
        return None
    return a == b


def satisfiable(formules):
    """Existe-t-il une interprétation qui rend TOUTES les formules vraies ?
    (recherche avec élagage : on arrête dès qu'une formule est déjà fausse)"""
    formules = list(formules)
    noms = sorted(set().union(*(atomes(f) for f in formules))) if formules else []
    v = {}

    def rec(i):
        if any(_eval3(f, v) is False for f in formules):
            return False
        if i == len(noms):
            return True
        for b in (True, False):
            v[noms[i]] = b
            if rec(i + 1):
                return True
        del v[noms[i]]
        return False

    return rec(0)


def consequence(formules, f):
    """formules ⊨ f ?  (f est conséquence si formules ∪ {¬f} est insatisfiable)"""
    return not satisfiable(list(formules) + [negation(f)])


def equivalentes(f, g):
    return consequence([f], g) and consequence([g], f)
