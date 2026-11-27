# =============================================================================
# main.py — POINT D'ENTRÉE DE L'APPLICATION
# -----------------------------------------------------------------------------
# Ce fichier fait une seule chose : lancer l'application graphique.
#   1. il vérifie que la bibliothèque « customtkinter » est installée
#      (sinon il affiche la commande d'installation : pip install customtkinter) ;
#   2. il appelle la fonction lancer() de interface.py, qui ouvre la fenêtre.
# Utilisation :  python main.py
# Il ne contient aucun calcul logique.
# =============================================================================
"""Point d'entrée : python main.py"""
try:
    import customtkinter  # noqa: F401
except ImportError:
    raise SystemExit("Il manque customtkinter. Installez-le avec :  pip install customtkinter")
from interface import lancer

if __name__ == "__main__":
    lancer()
