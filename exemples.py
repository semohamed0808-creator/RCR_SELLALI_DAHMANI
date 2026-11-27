# =============================================================================
# exemples.py — THÉORIES D'EXEMPLE (menu « Exemples » de l'interface)
# -----------------------------------------------------------------------------
# Ce fichier ne contient que des données : un dictionnaire EXEMPLES qui associe un
# nom à une théorie (liste W de formules, liste D de défauts écrits en texte).
# Théories tirées du sujet et du cours : exemple du sujet, Tweety (oiseau,
# pingouin, défaut semi-normal), deux extensions, diamant de Nixon, théorie sans
# extension, défauts généraux. Elles servent à la démonstration et aux tests.
# =============================================================================
"""exemples.py — théories prêtes à charger (menu « Exemples »). Tirées du cours."""

EXEMPLES = {
    "Exemple du sujet": {
        "W": ["o", "p -> o", "p -> ~v"],
        "D": ["o : v / v", "a : c / b"]},
    "Tweety est un oiseau": {
        "W": ["Oiseau(tweety)"],
        "D": ["Oiseau(x) : Vole(x) / Vole(x)"]},
    "Tweety est un pingouin": {
        "W": ["Oiseau(tweety)", "Pingouin(tweety)", "Pingouin(x) -> ~Vole(x)"],
        "D": ["Oiseau(x) : Vole(x) / Vole(x)"]},
    "Tweety (défaut semi-normal)": {
        "W": ["Oiseau(tweety)", "Pingouin(tweety)"],
        "D": ["Oiseau(x) : Vole(x) & ~Pingouin(x) / Vole(x)"]},
    "Deux extensions (cours)": {
        "W": ["a"],
        "D": ["a : b / c", "a : ~c / ~b"]},
    "Diamant de Nixon": {
        "W": ["Quaker(nixon)", "Republicain(nixon)"],
        "D": ["Quaker(x) : Pacifiste(x) / Pacifiste(x)",
              "Republicain(x) : ~Pacifiste(x) / ~Pacifiste(x)"]},
    "Aucune extension": {
        "W": [],
        "D": [": a / ~a"]},
    "Défauts généraux (cours)": {
        "W": [],
        "D": [": a / b", ": c / ~a"]},
}
