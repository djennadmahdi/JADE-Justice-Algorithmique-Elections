import pandas as pd  # Permet de lire et manipuler les fichiers Excel

# Importation de DatabaseManager et du chemin du fichier Excel des types
from src.config.settings import DatabaseManager, FILE_TYPES


# Classe responsable de l’importation des types de décisions
class TypesImporter(DatabaseManager):

    def run(self):
        # Message de début du traitement
        print("DÉMARRAGE : Importation des types de décisions (Excel)")

        try:
            # Création d’un curseur PostgreSQL
            cur = self.get_cursor()

            # Lecture de la requête SQL d’insertion des types
            query_insert = self.read_sql_file('insert_raw_types.sql')

            # Chargement du fichier Excel contenant les types/sous-types
            df = pd.read_excel(FILE_TYPES)

            # Compteur des lignes importées
            compteur = 0

            # Parcours de chaque ligne du fichier Excel
            for _, row in df.iterrows():

                # =====================================================
                # Récupération de l’identifiant du sous-type
                # =====================================================

                # Si la cellule est vide (NaN), on met None
                # Sinon on convertit la valeur en entier
                id_val = (
                    None
                    if pd.isna(row.get("SousTypeDecisionSet Id"))
                    else int(row.get("SousTypeDecisionSet Id"))
                )


                # =====================================================
                # Récupération du code du type de décision
                # =====================================================

                # Si la cellule est vide, on met None
                # Sinon on convertit la valeur en chaîne de caractères
                code_val = (
                    None
                    if pd.isna(row.get("TypeDecisionSet Code"))
                    else str(row.get("TypeDecisionSet Code"))
                )


                # =====================================================
                # Récupération du libellé du sous-type
                # =====================================================

                # Si la cellule est vide, on met None
                # Sinon on convertit la valeur en chaîne de caractères
                lib_val = (
                    None
                    if pd.isna(row.get("SousTypeDecisionSet Lib"))
                    else str(row.get("SousTypeDecisionSet Lib"))
                )


                # =====================================================
                # Insertion dans la table raw_types
                # =====================================================

                cur.execute(
                    query_insert,
                    (
                        id_val,    # Identifiant du sous-type
                        code_val,  # Code du type de décision
                        lib_val    # Libellé du sous-type
                    )
                )

                # Incrémente le compteur
                compteur += 1


            # Validation des insertions dans PostgreSQL
            self.conn.commit()

            # Message final si tout s’est bien passé
            print(f"SUCCÈS : {compteur} types importés dans 'raw_types'.")

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
    TypesImporter().run()