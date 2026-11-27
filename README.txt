==========================================================
 LOGIQUE DES DEFAUTS (Reiter) - Mini-projet 1 RCR
 USTHB - 4-ING-IA - Dr N. Mebtouche
==========================================================

1. PREREQUIS
   - Python 3.10 ou plus recent (python.org ; cocher "Add Python to PATH")
   - La bibliotheque customtkinter

2. INSTALLATION (terminal VS Code : Terminal > New Terminal)
   cd chemin\vers\RCR_SELLALI_DAHMANI
   pip install customtkinter
   (ou :  pip install -r requirements.txt)

3. LANCEMENT
   python main.py
   Pour verifier le moteur sans interface :
   python test_projet.py

4. UTILISATION RAPIDE
   - Menu "Exemples" : charge une theorie du cours (Tweety, Nixon...).
   - Monde W : ecrire une formule puis "Ajouter" (ou Entree).
   - Defauts D : prerequis / justifications / consequent, ou "Texte libre"
     sous la forme   prerequis : just1, just2 / consequent
     (prerequis vide autorise :   : a / ~a )
   - "Generer les extensions" calcule toutes les extensions.
   - Ecrire une formule phi puis "Sceptique ?" ou "Credule ?".
   - Onglet "Explication pas a pas" : pourquoi chaque defaut est
     applique, bloque ou non applicable (fonctionnalite creative).
   - Nouveau / Ouvrir / Enregistrer : fichier .json (W, D et extensions).
   - Importer .txt / Exporter .txt : lecture et ecriture de W et D dans un
     fichier texte (option A du sujet), voir exemple_theorie.txt.
     Format :   [W]  une formule par ligne   [D]  un defaut par ligne
     (lignes commencant par # = commentaires ; prefixes « W: » et « D: »
     acceptes). Les lignes incorrectes sont signalees avec leur numero.

5. SYNTAXE DES FORMULES
   non :  ~  ou  ¬          et :  &  ou  ∧          ou :  |  ou  ∨
   implique :  ->  ou  →    equivalent :  <->  ou  ↔
   Propositions : p, o, Q     Predicats : Oiseau(tweety), Pere(ali,omar)
   Predicat = majuscule ; constante = minuscule.
   Variables (defauts ouverts) : u, v, w, x, y, z (+ chiffres), ex. Oiseau(x).
   Un defaut ouvert est instancie automatiquement sur toutes les constantes.

6. ORGANISATION DU CODE (aucune classe : fonctions + dictionnaires)
   formules.py     lecture des formules, affichage, satisfiabilite, consequence
   theorie.py      defauts, theorie (W, D), verifications de saisie, types
   instances.py    instanciation des variables (defauts ouverts)
   extensions.py   algorithme des extensions, sceptique/credule, explication
   persistance.py  sauvegarde / chargement JSON (avec les extensions)
                   + import / export texte (option A)
   exemples.py     theories d'exemple
   exemple_theorie.txt  exemple de fichier texte importable
   interface.py    interface graphique (ne fait AUCUN calcul logique)
   main.py         point d'entree
   test_projet.py   tests automatiques

7. LIMITES
   Logique propositionnelle (les variables sont instanciees sur les constantes
   de la theorie). Le calcul est exponentiel en nombre de defauts : ~12 defauts
   independants < 1 s, 16 defauts ~ 15 s ; limite de securite : 100 000 etats.

8. AUTEUR
   SELLALI Mohamed et DAHMANI (binome) - 4-ING-IA - USTHB
