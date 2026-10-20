# Importation de la classe DatabaseManager
# Elle contient les méthodes de connexion, curseur, lecture SQL et fermeture
from src.config.settings import DatabaseManager


# Classe responsable de l’initialisation de la base de données
class DatabaseInitializer(DatabaseManager):

    def run(self):
        # Message de début du traitement
        print("DÉMARRAGE : Initialisation de la base de données")

        try:
            # Création d’un curseur PostgreSQL
            cur = self.get_cursor()

            # Lecture du fichier SQL qui contient la création des tables/index
            sql_query = self.read_sql_file('init_database.sql')

            # Message d’information
            print("Suppression et recréation des tables et index...")

            # Exécution du script SQL
            cur.execute(sql_query)

            # Validation des changements dans PostgreSQL
            self.conn.commit()

            # Message si tout s’est bien passé
            print("SUCCÈS : Base de données initialisée et prête !")

        except Exception as e:
            # Message affiché en cas d’erreur
            print(f"ERREUR FATALE LORS DE L'INITIALISATION : {e}")

            # Annule les changements si une erreur se produit
            if self.conn:
                self.conn.rollback()

        finally:
            # Ferme toujours la connexion à la base de données
            self.close()


# Point d’entrée du script
# Ce bloc s’exécute seulement si le fichier est lancé directement
if __name__ == "__main__":
    DatabaseInitializer().run()