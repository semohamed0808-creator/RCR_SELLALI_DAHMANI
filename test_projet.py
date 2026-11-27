# =============================================================================
# test_projet.py — TESTS AUTOMATIQUES DU MOTEUR (sans interface graphique)
# -----------------------------------------------------------------------------
# Lancer :  python test_projet.py
# Vérifie avec des « assert » les résultats attendus sur les exemples du sujet et
# du cours : exemple du sujet, Tweety (oiseau, pingouin, semi-normal), deux
# extensions, Nixon, théorie sans extension, défauts généraux, explication,
# sauvegarde / rechargement JSON, import / export texte, défauts avec variables.
# Affiche « Tous les tests du projet passent » si tout est correct.
# =============================================================================
"""Tests complets : python test_projet.py"""
import os, tempfile
from formules import lire_formule as L
from theorie import *
from instances import fermer
from extensions import *
from persistance import sauvegarder, charger
from exemples import EXEMPLES


def theorie(nom):
    T = nouvelle_theorie()
    for s in EXEMPLES[nom]["W"]: ajouter_formule(T, s)
    for s in EXEMPLES[nom]["D"]: ajouter_defaut(T, s)
    return T


def calc(nom):
    T = theorie(nom)
    Tg, _ = fermer(T)
    return T, Tg, calculer_extensions(Tg)


# sujet : une extension, littéraux o, v, ¬p
T, Tg, E = calc("Exemple du sujet")
assert len(E) == 1 and set(litteraux(E[0])) == {"o", "v", "¬p"}, litteraux(E[0])
print(texte_extension(E[0], 1), "|", ", ".join(litteraux(E[0])))

# Tweety
T, Tg, E = calc("Tweety est un oiseau")
assert len(E) == 1 and sceptique(E, L("Vole(tweety)"))
T, Tg, E = calc("Tweety est un pingouin")
assert len(E) == 1 and sceptique(E, L("~Vole(tweety)")) and not credule(E, L("Vole(tweety)"))
T, Tg, E = calc("Tweety (défaut semi-normal)")
assert len(E) == 1 and not credule(E, L("Vole(tweety)"))

# Exemple 3 du cours : deux extensions Th({a,c}) et Th({a,¬b})
T, Tg, E = calc("Deux extensions (cours)")
assert len(E) == 2
assert credule(E, L("c")) and not sceptique(E, L("c")) and sceptique(E, L("c | ~b"))
assert niveau(T, E, L("a")) == 1 and niveau(T, E, L("c | ~b")) == 2
assert niveau(T, E, L("c")) == 3 and niveau(T, E, L("b")) == 4

# Nixon
T, Tg, E = calc("Diamant de Nixon")
assert len(E) == 2 and credule(E, L("Pacifiste(nixon)")) and credule(E, L("~Pacifiste(nixon)"))
assert not sceptique(E, L("Pacifiste(nixon)")) and not sceptique(E, L("~Pacifiste(nixon)"))

# aucune extension ; défauts généraux (extension unique Th({¬a}))
T, Tg, E = calc("Aucune extension")
assert E == []
T, Tg, E = calc("Défauts généraux (cours)")
assert len(E) == 1 and "¬a" in litteraux(E[0]) and "b" not in litteraux(E[0])

# explication
T, Tg, E = calc("Tweety est un pingouin")
assert expliquer(Tg, E[0])[0]["etat"] == "bloque"

# sauvegarde / chargement avec extensions
T, Tg, E = calc("Diamant de Nixon")
f = os.path.join(tempfile.mkdtemp(), "t.json")
sauvegarder(f, T, E, Tg)
T2, E2, Tg2 = charger(f)
assert theorie_en_dict(T2) == theorie_en_dict(T) and len(E2) == 2
assert [texte_extension(e, 1) for e in E2] == [texte_extension(e, 1) for e in E]
print("\nTous les tests du projet passent ✔")

# ---- option A : import / export fichier texte
from persistance import lire_texte, importer_texte, exporter_texte
T3, err, av = importer_texte("exemple_theorie.txt")
assert not err and len(T3["W"]) == 3 and len(T3["D"]) == 2
Tg3, _ = fermer(T3)
assert [texte_extension(e, 1) for e in calculer_extensions(Tg3)][0].startswith("E1 = Th({o, p → o, p → ¬v, v})")
T4, err, av = lire_texte("[W]\np &\nq\nW: r\n[D]\na b / c\nD: a : b / c\n: x, ~x / y\nzzz")
assert len(T4["W"]) == 2 and len(T4["D"]) == 2 and len(err) == 3 and len(av) == 1, (err, av)
f = os.path.join(tempfile.mkdtemp(), "t.txt")
exporter_texte(f, T3)
T5, err, _ = importer_texte(f)
assert not err and theorie_en_dict(T5) == theorie_en_dict(T3)
print("Import/export texte ✔")

# ---- variables : deux individus, instanciation sur toutes les constantes
T6 = nouvelle_theorie()
for s in ["Oiseau(tweety)", "Oiseau(titi)", "Pingouin(titi)", "Pingouin(x) -> ~Vole(x)"]:
    ajouter_formule(T6, s)
ajouter_defaut(T6, "Oiseau(x) : Vole(x) / Vole(x)")
Tg6, _ = fermer(T6)
E6 = calculer_extensions(Tg6)
assert len(E6) == 1 and sceptique(E6, L("Vole(tweety)")) and sceptique(E6, L("~Vole(titi)"))
print("Défauts ouverts (2 individus) ✔")
