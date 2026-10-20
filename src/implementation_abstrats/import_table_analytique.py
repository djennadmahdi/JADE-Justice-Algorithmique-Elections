# Importation de la classe DatabaseManager
# Elle permet de gérer la connexion à la base de données PostgreSQL
from src.config.settings import DatabaseManager


# Création d'une classe pour importer les rubriques analytiques
# Elle hérite de DatabaseManager pour utiliser la connexion à la base
class TableAnalytiqueImporter(DatabaseManager):

    # Méthode principale qui lance l'importation
    def run(self):
        print("DÉMARRAGE : Création de la table analytique depuis raw_rubriques")

        try:
            # Récupération du curseur PostgreSQL
            # Le curseur permet d'exécuter des requêtes SQL
            cur = self.get_cursor()

            # Requête SQL qui insère les rubriques analytiques
            # depuis la table raw_rubriques vers la table rubriques
            query = """
                INSERT INTO public.rubriques (
                    id_rubrique,
                    num_rubrique,
                    lib,
                    niveau,
                    parent_id
                )
                SELECT
                    id,
                    num_rubrique,
                    lib,
                    niveau,
                    parent_id
                FROM public.raw_rubriques

                -- On garde uniquement les rubriques dont le numéro commence par 8
                -- Cela correspond aux rubriques analytiques utilisées dans le projet
                WHERE num_rubrique LIKE '8%'

                -- Si une rubrique existe déjà avec le même id_rubrique,
                -- on ne fait rien pour éviter les doublons
                ON CONFLICT (id_rubrique) DO NOTHING;
            """

            # Exécution de la requête SQL
            cur.execute(query)

            # Validation des changements dans la base de données
            self.conn.commit()

            print("SUCCÈS : table analytique alimentée depuis raw_rubriques.")

        except Exception as e:
            # Affichage de l'erreur si l'importation échoue
            print(f"ERREUR : alimentation de la table analytique impossible : {e}")

            # Annulation des changements en cas d'erreur
            if self.conn:
                self.conn.rollback()

        finally:
            # Fermeture de la connexion à la base de données
            self.close()


# Ce bloc permet d'exécuter le script directement
# Exemple : python import_table_analytique.py
if __name__ == "__main__":
    TableAnalytiqueImporter().run()