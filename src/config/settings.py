import os                         # Permset de gérer les chemins et fichiers
import psycopg2                  # Permet de se connecter à PostgreSQL
import psycopg2.extras           # Fournit des fonctionnalités supplémentaires pour les curseurs PostgreSQL
from dotenv import load_dotenv   # Permet de charger automatiquement les variables du fichier .env


# =========================================================
# 1. Définition du répertoire racine du projet (BASE_DIR)
# =========================================================

# __file__ = fichier actuel
# os.path.dirname(__file__) = dossier du fichier actuel
# "..", ".." = remonte de deux dossiers
# abspath = transforme en chemin absolu

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)


# =========================================================
# 2. Auto-détection du fichier d’environnement
# =========================================================

# Liste des noms possibles du fichier contenant
# les variables d’environnement

noms_possibles = [
    ".env",
    "env",
    "env_template",
    ".env.template",
    ".env.local"
]

# Boucle qui teste chaque nom de fichier
for nom in noms_possibles:

    # Création du chemin complet du fichier
    chemin_test = os.path.join(BASE_DIR, nom)

    # Vérifie si le fichier existe
    if os.path.exists(chemin_test):

        # Charge automatiquement les variables du fichier trouvé
        load_dotenv(dotenv_path=chemin_test)

        # Arrête la boucle dès qu’un fichier valide est trouvé
        break


# =========================================================
# 3. Définition des dossiers du projet
# =========================================================

# os.getenv permet de récupérer une variable d’environnement
# Si elle n’existe pas, on utilise une valeur par défaut

# Dossier contenant les fichiers bruts
DATA_RAW_DIR = os.getenv(
    "DATA_RAW_DIR",
    os.path.join(BASE_DIR, "data", "raw")
)

# Dossier des logs
LOGS_DIR = os.getenv(
    "LOGS_DIR",
    os.path.join(BASE_DIR, "logs")
)

# Dossier des fichiers SQL
SQL_DIR = os.getenv(
    "SQL_DIR",
    os.path.join(BASE_DIR, "sql")
)


# =========================================================
# 4. Emplacements des fichiers de données
# =========================================================

# Fichier JSON des abstrats
FILE_ABSTRACTS = os.path.join(
    DATA_RAW_DIR,
    "abstrats.json"
)

# Fichier Excel des décisions
FILE_DECISIONS = os.path.join(
    DATA_RAW_DIR,
    "extraction.xlsx"
)

# Fichier JSON des rubriques
FILE_RUBRIQUES = os.path.join(
    DATA_RAW_DIR,
    "rubriques.json"
)

# Fichier Excel des types/sous-types
FILE_TYPES = os.path.join(
    DATA_RAW_DIR,
    "type sous type.xlsx"
)


# =========================================================
# 5. Configuration PostgreSQL
# =========================================================

# Les informations sont récupérées depuis le fichier .env

DB_CONFIG = {

    # Nom de la base de données
    "dbname": str(os.getenv("DB_NAME", "")).strip(),

    # Utilisateur PostgreSQL
    "user": str(os.getenv("DB_USER", "")).strip(),

    # Mot de passe PostgreSQL
    "password": str(os.getenv("DB_PASSWORD", "")).strip(),

    # Adresse du serveur PostgreSQL
    # localhost par défaut
    "host": str(os.getenv("DB_HOST", "localhost")).strip(),

    # Port PostgreSQL
    # 5432 par défaut
    "port": str(os.getenv("DB_PORT", "5432")).strip()
}


# =========================================================
# 6. Classe de gestion de la base de données
# =========================================================

class DatabaseManager:

    # Constructeur de la classe
    def __init__(self):

        # Variable qui contiendra la connexion PostgreSQL
        self.conn = None


    # =====================================================
    # Connexion à PostgreSQL
    # =====================================================

    def connect(self):

        # Si aucune connexion n’existe
        if self.conn is None:

            # Création de la connexion PostgreSQL
            self.conn = psycopg2.connect(**DB_CONFIG)

        # Retourne la connexion
        return self.conn


    # =====================================================
    # Création d’un curseur PostgreSQL
    # =====================================================

    def get_cursor(self, as_dict=False):

        # Récupère la connexion
        conn = self.connect()

        # Si as_dict=True
        # les résultats seront retournés sous forme de dictionnaire
        if as_dict:
            return conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )

        # Sinon retourne un curseur classique
        return conn.cursor()


    # =====================================================
    # Lecture d’un fichier SQL
    # =====================================================

    def read_sql_file(self, filename):

        # Création du chemin complet du fichier SQL
        filepath = os.path.join(SQL_DIR, filename)

        # Ouvre le fichier en lecture UTF-8
        with open(filepath, 'r', encoding='utf-8') as f:

            # Retourne tout le contenu du fichier SQL
            return f.read()


    # =====================================================
    # Fermeture de la connexion PostgreSQL
    # =====================================================

    def close(self):

        # Vérifie si une connexion existe
        if self.conn:

            # Ferme la connexion
            self.conn.close()

            # Réinitialise la variable
            self.conn = None