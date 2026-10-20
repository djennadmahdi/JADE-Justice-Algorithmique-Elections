from src.config.settings import DatabaseManager

class FakeDataInjector(DatabaseManager):
    def run(self):
        print("DÉMARRAGE : Injection des fausses données de test...")
        try:
            cur = self.get_cursor()
            
            cur.execute("""
                INSERT INTO raw_decisions (id, numero, date_decision) 
                VALUES (999999, 'TEST-REJET-999999', NULL)
                ON CONFLICT (id) DO NOTHING;
            """)
            
            cur.execute("""
                INSERT INTO raw_abstrat (id, decision_id, resume_abstrat, motifs) 
                VALUES (999999, 999999, 'Nul', '["99"]')
                ON CONFLICT (id) DO NOTHING;
            """)
            
            self.conn.commit()
            print("SUCCÈS : Fausse donnée ID 999999 injectée avec succès dans les tables _raw !")
        except Exception as e:
            print(f"ERREUR LORS DE L'INJECTION : {e}")
            if self.conn: self.conn.rollback()
        finally:
            self.close()

if __name__ == "__main__":
    FakeDataInjector().run()