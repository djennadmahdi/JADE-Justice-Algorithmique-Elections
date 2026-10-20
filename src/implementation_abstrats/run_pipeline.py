import subprocess  # Permet d’exécuter d’autres scripts/programmes depuis Python
import os          # Permet de gérer les chemins et variables d’environnement
import sys         # Permet d’interagir avec le système Python
import io          # Permet de gérer l’encodage de la console

# Importation du chemin racine du projet
from src.config.settings import BASE_DIR


# =========================================================
# Configuration UTF-8 pour Windows
# =========================================================

# Sur Windows, certains caractères spéciaux (accents, emojis)
# peuvent mal s’afficher dans le terminal.
# Cette partie force l’encodage UTF-8.

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8'
    )


# =========================================================
# Liste des scripts du pipeline ETL
# =========================================================

# Chaque script sera exécuté automatiquement dans l’ordre

PIPELINE_SCRIPTS = [

    # Initialise la base de données
    "src/implementation_abstrats/import_database.py",

    # Initialise la table des rejets
    "src/implementation_abstrats/init_rejets.py",

    # Importe les abstrat JSON
    "src/implementation_abstrats/import_abstrats.py",

    # Importe les rubriques JSON
    "src/implementation_abstrats/import_rubriques.py",

    "src/implementation_abstrats/import_table_analytique.py",

    # Importe les décisions Excel
    "src/implementation_abstrats/import_decisions.py",

    # Importe les types/sous-types Excel
    "src/implementation_abstrats/import_types.py",

    # Lance les tests liés aux rejets
    "src/implementation_abstrats/test_rejet.py",

    # Crée les vues SQL finales
    "src/implementation_abstrats/create_view.py",

     # Lance le traitement qualité des données
    "src/implementation_abstrats/data_quality.py"  
]


# =========================================================
# Fonction principale du pipeline
# =========================================================

def run_pipeline():

    # Affichage du titre du pipeline
    print("========================================")
    print("DÉMARRAGE DU PIPELINE ETL JADE (POO)")
    print("========================================\n")


    # =====================================================
    # Récupération du Python actuellement utilisé
    # =====================================================

    # sys.executable = chemin du Python courant
    # Cela garantit que tous les scripts utilisent
    # le même environnement Python/venv
    python_exe = sys.executable


    # =====================================================
    # Variables d’environnement du pipeline
    # =====================================================

    # Copie les variables d’environnement actuelles
    pipeline_env = os.environ.copy()

    # Définit PYTHONPATH pour permettre les imports du projet
    pipeline_env["PYTHONPATH"] = BASE_DIR


    # =====================================================
    # Exécution des scripts un par un
    # =====================================================

    for script in PIPELINE_SCRIPTS:

        # Création du chemin complet du script
        script_path = os.path.join(BASE_DIR, script)

        # Affiche le script en cours d’exécution
        print(f"Exécution de : {script}")

        try:

            # Exécute le script Python
            subprocess.run(

                # Commande exécutée :
                # python script.py
                [python_exe, script_path],

                # Variables d’environnement utilisées
                env=pipeline_env,

                # Si erreur → exception automatiquement
                check=True
            )

            # Message si le script réussit
            print("Terminé avec succès.\n")


        except subprocess.CalledProcessError:

            # Message si le script échoue
            print(f"ERREUR FATALE : Le script {script} a échoué.")

            # Arrête complètement le pipeline
            sys.exit(1)


    # =====================================================
    # Fin du pipeline
    # =====================================================

    print("========================================")
    print("PIPELINE ENTIÈREMENT TERMINÉ AVEC SUCCÈS !")
    print("========================================")


# =========================================================
# Point d’entrée du programme
# =========================================================

# Ce bloc s’exécute seulement si le fichier est lancé directement
if __name__ == "__main__":
    run_pipeline()