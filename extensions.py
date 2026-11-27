# =============================================================================
# extensions.py — CALCUL DES EXTENSIONS, SCEPTIQUE / CRÉDULE, EXPLICATION
# -----------------------------------------------------------------------------
# C'est le cœur de l'application (algorithme du cours, processus de Reiter) :
#   - calculer_extensions(T) génère TOUTES les extensions d'une théorie close :
#     on part de Th(W), on applique les défauts applicables (prérequis déduit et
#     aucune négation de justification déduite), on essaie tous les ordres, et on
#     vérifie qu'aucune justification d'un défaut appliqué n'est réfutée ;
#   - sceptique(exts, φ) : φ appartient à TOUTES les extensions ;
#     credule(exts, φ) : φ appartient à AU MOINS UNE extension ;
#     niveau() donne le niveau de croyance de φ (hiérarchie du cours, 4 niveaux) ;
#   - litteraux() et texte_extension() préparent l'affichage des extensions ;
#   - expliquer() (fonctionnalité créative) dit, pour chaque défaut, s'il est
#     appliqué, bloqué ou non applicable, et pourquoi.
# =============================================================================
"""
extensions.py — BLOCS 2 et 3 : extensions, conséquences sceptique / crédule, explication.

Une extension est un dictionnaire :
    {"generateurs": [arbres]  (W + conséquents appliqués ; l'extension est Th(generateurs)),
     "appliques":   [indices des défauts appliqués, dans l'ordre],
     "incoherente": bool}

Algorithme (cours, « processus » de Reiter) :
  1. E ← Th(W)
  2. choisir un défaut non appliqué, applicable : prérequis ∈ E et aucun ¬βi ∈ E ; E ← Th(E ∪ {γ})
  3. recommencer jusqu'à ce qu'aucun défaut ne soit applicable
  4. vérification finale : aucune justification des défauts appliqués n'est réfutée
  5. essayer tous les ordres de choix (on mémorise les ensembles de défauts déjà vus)
"""
from formules import (consequence, negation, atomes, en_texte, satisfiable, lire_formule)
from theorie import texte_defaut

LIMITE_ETATS = 100000


def _generateurs(W, D, appliques):
    return list(W) + [D[i]["conseq"] for i in appliques]


def _applicable(d, gen):
    """Prérequis ∈ E  et  pour chaque justification β : ¬β ∉ E."""
    if d["prerequis"] is not None and not consequence(gen, d["prerequis"]):
        return False
    return all(not consequence(gen, negation(j)) for j in d["justifs"])


def _meme_extension(g1, g2):
    return all(consequence(g1, f) for f in g2) and all(consequence(g2, f) for f in g1)


def calculer_extensions(T):
    """Renvoie la liste de TOUTES les extensions de la théorie close T."""
    W, D = T["W"], T["D"]
    vus, exts = set(), []

    def explorer(appliques):
        cle = frozenset(appliques)
        if cle in vus:
            return
        vus.add(cle)
        if len(vus) > LIMITE_ETATS:
            raise RuntimeError("Calcul trop long : trop de défauts pour cette théorie.")
        gen = _generateurs(W, D, appliques)
        # étape 4 (faite au fil de l'eau : E ne fait que grandir) : une justification
        # déjà utilisée ne doit jamais être réfutée
        if any(consequence(gen, negation(j)) for i in appliques for j in D[i]["justifs"]):
            return
        candidats = [i for i in range(len(D)) if i not in cle and _applicable(D[i], gen)]
        if not candidats:                                   # étape 3 : processus clos
            if not any(_meme_extension(gen, e["generateurs"]) for e in exts):
                exts.append({"generateurs": gen, "appliques": list(appliques),
                             "incoherente": not satisfiable(gen)})
            return
        for i in candidats:                                 # étape 5 : tous les ordres
            explorer(appliques + (i,))

    explorer(())
    return exts


# ------------------------------------------------------------ conséquences
def est_consequence(ext, phi):
    return consequence(ext["generateurs"], phi)


def sceptique(exts, phi):
    """φ est dans TOUTES les extensions (vrai trivialement s'il n'y a aucune extension)."""
    return all(est_consequence(e, phi) for e in exts)


def credule(exts, phi):
    """φ est dans AU MOINS UNE extension."""
    return any(est_consequence(e, phi) for e in exts)


NIVEAUX = {1: "1 · certaine : φ est déjà conséquence de W",
           2: "2 · dans toutes les extensions (sceptique et crédule)",
           3: "3 · dans certaines extensions seulement (crédule uniquement)",
           4: "4 · dans aucune extension : personne ne l'accepte"}


def niveau(T, exts, phi):
    """Hiérarchie du cours (4 niveaux)."""
    if consequence(T["W"], phi):
        return 1
    if exts and sceptique(exts, phi):
        return 2
    if credule(exts, phi):
        return 3
    return 4


# ---------------------------------------------------------------- affichage
def litteraux(ext):
    """Littéraux (a ou ¬a) conséquences de l'extension."""
    if ext["incoherente"]:
        return []
    noms = sorted(set().union(*(atomes(f) for f in ext["generateurs"]))) if ext["generateurs"] else []
    res = []
    for a in noms:
        if consequence(ext["generateurs"], ("atom", a)):
            res.append(a)
        elif consequence(ext["generateurs"], ("not", ("atom", a))):
            res.append("¬" + a)
    return res


def texte_extension(ext, k):
    gen = []
    for f in ext["generateurs"]:
        if f not in gen:
            gen.append(f)
    if ext["incoherente"]:
        return f"E{k} = L  (extension incohérente : W est incohérent, tout est conséquence)"
    return f"E{k} = Th({{{', '.join(en_texte(f) for f in gen)}}})"


# -------------------------------------------- fonctionnalité créative : explication
def expliquer(T, ext):
    """Pour CHAQUE défaut : pourquoi il est appliqué, bloqué ou inapplicable dans cette extension."""
    D, gen, res = T["D"], ext["generateurs"], []
    for i, d in enumerate(D):
        base = {"indice": i + 1, "texte": texte_defaut(d)}
        if i in ext["appliques"]:
            rang = ext["appliques"].index(i) + 1
            res.append({**base, "etat": "applique",
                        "detail": f"appliqué à l'étape {rang} : on ajoute {en_texte(d['conseq'])}"})
        elif d["prerequis"] is not None and not consequence(gen, d["prerequis"]):
            res.append({**base, "etat": "inapplicable",
                        "detail": f"non applicable : le prérequis {en_texte(d['prerequis'])} "
                                  f"n'est pas démontrable"})
        else:
            bloc = next((j for j in d["justifs"] if consequence(gen, negation(j))), None)
            detail = (f"bloqué : ¬({en_texte(bloc)}) est dans l'extension, la justification est réfutée"
                      if bloc is not None else "non retenu dans cette extension")
            res.append({**base, "etat": "bloque", "detail": detail})
    return res
