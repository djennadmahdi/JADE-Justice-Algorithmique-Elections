import json  # Permet de lire et convertir un fichier JSON en données Python

# Importation de la classe DatabaseManager et du chemin du fichier abstrat JSON
from src.config.settings import DatabaseManager, FILE_ABSTRACTS


# Classe responsable de l’importation des abstrat
class AbstractsImporter(DatabaseManager):

    def run(self):
        # Message de début du traitement
        print("DÉMARRAGE : Importation des abstrat (JSON)")

        try:
            # Création d’un curseur PostgreSQL
            cur = self.get_cursor()

            # Lecture de la requête SQL d’insertion des abstrat bruts
            query_insert = self.read_sql_file('insert_raw_abstrat.sql')

            # Ouverture du fichier JSON des abstrat
            with open(FILE_ABSTRACTS, encoding="utf-8") as f:

                # Conversion du contenu JSON en dictionnaire Python
                data = json.load(f)

            # Compteur des abstrat importés
            compteur = 0

            # Parcours de chaque abstrat dans le fichier JSON
            for key, value in data.items():

                # Exécution de la requête INSERT avec les valeurs de l’abstrat
                cur.execute(
                    query_insert,
                    (
                        value.get("Id"),                # Identifiant de l’abstrat
                        value.get("StatutAbstratId"),   # Statut de l’abstrat
                        value.get("ResumeAbstratId"),   # Identifiant du résumé
                        value.get("RubriqueId"),        # Identifiant de la rubrique
                        value.get("DecisionId"),        # Identifiant de la décision
                        value.get("SolutionImplicite"), # Solution implicite
                        value.get("ResumeAbstrat"),     # Texte du résumé/abstrat
                        value.get("RenvoiRubriqueId"),  # Renvoi vers une autre rubrique

                        # Conversion du champ motifs en texte JSON
                        json.dumps(value.get("motifs", []))
                    )
                )

                # Incrémente le compteur après chaque insertion
                compteur += 1

            # Validation des insertions dans PostgreSQL
            self.conn.commit()

            # Message final si tout s’est bien passé
            print(f"SUCCÈS : {compteur} abstrat importés dans 'raw_abstrat'.")

        except Exception as e:
            # Message affiché en cas d’erreur
            print(f"ERREUR LORS DE L'IMPORTATION : {e}")

            # Annule les insertions si une erreur se produit
            if self.conn:
                self.conn.rollback()

        finally:
            # Ferme toujours la connexion à la base de données
            self.close()


# Point d’entrée du script
# Ce bloc s’exécute seulement si le fichier est lancé directement
if __name__ == "__main__":
    AbstractsImporter().run()