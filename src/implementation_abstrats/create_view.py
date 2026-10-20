# Importation de la classe DatabaseManager
# Elle contient déjà les méthodes pour se connecter à PostgreSQL,
# créer un curseur, lire un fichier SQL et fermer la connexion
import sys  #
from src.config.settings import DatabaseManager


# ViewManager hérite de DatabaseManager
# Donc elle peut utiliser directement get_cursor(), read_sql_file(), close(), etc.
class ViewManager(DatabaseManager):

    def run(self):
        # Message de début du script
        print("DÉMARRAGE : Création de toutes les Vues SQL (Format v_...)")

        try:
            # Création d’un curseur PostgreSQL
            cur = self.get_cursor()

            # Lecture et exécution du fichier SQL qui crée la vue principale JADE
            print("Création de la vue JADE unifiée (v_abstrat_jade)...")
            cur.execute(self.read_sql_file('create_view_jade.sql'))

            # Lecture et exécution du fichier SQL qui crée les vues secondaires
            print("Création des vues secondaires (v_jade_elections et v_abstrat_hors_elections)...")
            cur.execute(self.read_sql_file('create_view_abstrat.sql'))

            # Validation des changements dans la base de données
            self.conn.commit()

            # Message si tout s’est bien passé
            print("SUCCÈS : Toutes les vues (v_...) ont été créées et optimisées avec des index !")

        except Exception as e:
            # Message affiché en cas d’erreur SQL
            print(f"ERREUR SQL LORS DE LA CRÉATION DES VUES : {e}")

            # Annule les changements si une erreur s’est produite
            if self.conn:
                self.conn.rollback()

        finally:
            # Ferme toujours la connexion à la base de données
            self.close()


# Point d’entrée du script
# Ce bloc s’exécute seulement si le fichier est lancé directement
if __name__ == "__main__":
    ViewManager().run()