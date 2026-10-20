import json
import sys
from src.config.settings import DatabaseManager, FILE_RUBRIQUES

class RubriquesImporter(DatabaseManager):

    def run(self):
        print("DÉMARRAGE : Importation des rubriques en Staging (JSON)")

        try:
            cur = self.get_cursor()

            query_insert = """
                INSERT INTO raw_rubriques (
                    id, lib, niveau, num_rubrique, parent_id, renvoi_rubrique_id, ordre
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """

            with open(FILE_RUBRIQUES, "r", encoding="utf-8") as f:
                data = json.load(f)

            compteur = 0

            for key, value in data.items():
                num_rubrique = str(value.get("NumRubrique", ""))

                # On insère TOUT dans la table raw_ (Staging)
                cur.execute(
                    query_insert,
                    (
                        value.get("Id"),
                        value.get("Lib"),
                        value.get("Niveau"),
                        num_rubrique,
                        value.get("ParentId"),
                        value.get("RenvoiRubriqueId"),
                        value.get("Ordre")
                    )
                )
                compteur += 1

            self.conn.commit()
            print(f"SUCCÈS : {compteur} rubriques importées dans 'raw_rubriques'.")

        except Exception as e:
            print(f"ERREUR LORS DE L'IMPORTATION : {e}")
            if self.conn:
                self.conn.rollback()
            sys.exit(1)

        finally:
            self.close()

if __name__ == "__main__":
    RubriquesImporter().run()