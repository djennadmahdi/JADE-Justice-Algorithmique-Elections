import pandas as pd  # Permet de lire et manipuler les fichiers Excel
import sys           # Permet d’arrêter le programme en cas d’erreur

# Importation de DatabaseManager et du chemin du fichier Excel des décisions
from src.config.settings import DatabaseManager, FILE_DECISIONS


# Classe responsable de l’importation des décisions
class DecisionsImporter(DatabaseManager):

    def run(self):
        # Message de début du traitement
        print("DÉMARRAGE : Importation des décisions (Excel)")

        try:
            # Création d’un curseur PostgreSQL
            cur = self.get_cursor()

            # Lecture de la requête SQL d’insertion des décisions brutes
            query_insert = self.read_sql_file('insert_raw_decisions.sql')

            # Chargement du fichier Excel
            print(f"Chargement du fichier : {FILE_DECISIONS}...")
            df = pd.read_excel(FILE_DECISIONS).dropna(subset=['Id'])

            # Compteur des décisions importées
            compteur = 0

            # Parcours de chaque ligne du fichier Excel
            for _, row in df.iterrows():

                # Récupération de la référence officielle
                # On teste plusieurs noms possibles de colonnes
                ref_val = (
                    row.get("ReferenceOfficielle")
                    or row.get("Referent")
                    or row.get("ReferenceOfficelle")
                )

                # Limite la référence officielle à 50 caractères
                ref_off = str(ref_val)[:50] if pd.notna(ref_val) else None

                # Récupération et limitation du champ Referent
                referent_val = (
                    str(row.get("Referent"))[:50]
                    if pd.notna(row.get("Referent"))
                    else None
                )

                # Récupération et limitation du lien Legifrance
                lien_leg = (
                    str(row.get("LienLegifrance"))[:50]
                    if pd.notna(row.get("LienLegifrance"))
                    else None
                )

                # Récupération du champ ECLI
                # On teste Ecli puis ECLI selon le nom présent dans le fichier
                ecli_val = (
                    str(row.get("Ecli"))[:100]
                    if pd.notna(row.get("Ecli"))
                    else str(row.get("ECLI"))[:100]
                    if pd.notna(row.get("ECLI"))
                    else None
                )

                # Récupération de l’identifiant de l’affaire au greffe
                greffe_id = (
                    str(row.get("AffaireGreffeId"))[:50]
                    if pd.notna(row.get("AffaireGreffeId"))
                    else None
                )

                # Récupération de la date
                # On utilise la colonne "Date" si elle existe,
                # sinon on utilise "DateDecision"
                date_val = (
                    row.get("Date")
                    if "Date" in df.columns
                    else row.get("DateDecision")
                )

                # Si la date n’est pas vide, on la garde
                date_propre = date_val if pd.notna(date_val) else None

                # Exécution de l’insertion dans la table raw_decisions
                cur.execute(
                    query_insert,
                    (
                        int(row.get("Id")),  # Identifiant de la décision

                        date_propre,         # Date de décision propre

                        # Intitulé de la décision
                        str(row.get("Intitule"))
                        if pd.notna(row.get("Intitule"))
                        else None,

                        ref_off,             # Référence officielle
                        referent_val,        # Référent

                        # Lien vers le site web
                        str(row.get("LienSiteWeb"))
                        if pd.notna(row.get("LienSiteWeb"))
                        else None,

                        lien_leg,            # Lien Legifrance
                        ecli_val,            # Code ECLI

                        # Type de décision
                        int(row.get("TypeDecisionId"))
                        if pd.notna(row.get("TypeDecisionId"))
                        else None,

                        # Sous-type de décision
                        int(row.get("SousTypeDecisionId"))
                        if pd.notna(row.get("SousTypeDecisionId"))
                        else None,

                        # Département
                        int(row.get("DepartementId"))
                        if pd.notna(row.get("DepartementId"))
                        else None,

                        # Demandeurs
                        str(row.get("Demandeurs"))
                        if pd.notna(row.get("Demandeurs"))
                        else None,

                        # Défendeurs
                        str(row.get("Defendeurs"))
                        if pd.notna(row.get("Defendeurs"))
                        else None,

                        # Date de première saisine
                        row.get("PremiereSaisineLe")
                        if pd.notna(row.get("PremiereSaisineLe"))
                        else None,

                        greffe_id             # Identifiant affaire greffe
                    )
                )

                # Incrémente le compteur
                compteur += 1

            # Validation des insertions
            self.conn.commit()

            # Message final de succès
            print(f"SUCCÈS : {compteur} décisions importées dans 'raw_decisions'.")

        except Exception as e:
            # Affiche l’erreur
            print(f"ERREUR LORS DE L'IMPORTATION : {e}")

            # Annule les insertions si erreur
            if self.conn:
                self.conn.rollback()

            # Arrête le programme avec un code erreur
            sys.exit(1)

        finally:
            # Ferme toujours la connexion
            self.close()


# Point d’entrée du script
# Ce bloc s’exécute seulement si le fichier est lancé directement
if __name__ == "__main__":
    DecisionsImporter().run()