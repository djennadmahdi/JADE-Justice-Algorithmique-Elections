import sys
from src.config.settings import DatabaseManager

class RejetsInitializer(DatabaseManager):

    def run(self):
        print("DÉMARRAGE : Initialisation de la table des rejets")

        try:
            cur = self.get_cursor()

            # 1. Suppression en cascade pour repartir à zéro à chaque run
            cur.execute("DROP TABLE IF EXISTS public.abstrat_rejets CASCADE;")

            # 2. Recréation de la table vierge
            cur.execute("""
                CREATE TABLE public.abstrat_rejets (
                    id_rejet SERIAL PRIMARY KEY,
                    id_abstrat_raw INTEGER,
                    decision_id_raw INTEGER,
                    motif_rejet VARCHAR(255),
                    donnees_brutes JSONB,
                    date_rejet TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            self.conn.commit()
            print("SUCCÈS : Table 'abstrat_rejets' prête (vidée et recréée).")

        except Exception as e:
            print(f"ERREUR FATALE : {e}")
            if self.conn:
                self.conn.rollback()
            sys.exit(1)

        finally:
            self.close()

if __name__ == "__main__":
    RejetsInitializer().run()