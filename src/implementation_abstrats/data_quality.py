import logging                 
import os                      
import json                    
import re                      
import sys                     
from datetime import datetime, date  

from src.config.settings import DatabaseManager, LOGS_DIR

os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGS_DIR, 'qualite_donnees.log'),  
    level=logging.ERROR,                                     
    format='%(asctime)s | %(levelname)s | %(message)s',       
    encoding='utf-8'                                         
)

class DataQualityProcessor(DatabaseManager):

    def __init__(self):
        super().__init__()
        self.compteur_valides = 0
        self.compteur_rejets = 0

    @staticmethod
    def json_serial(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type non sérialisable")

    @staticmethod
    def clean_reference(ref):
        if not ref:
            return ""

        ref_str = str(ref).upper().replace('\xa0', '').replace(' ', '')
        ref_str = re.sub(r'DÉCISION(?:N°|NO)?', '', ref_str)
        ref_str = re.sub(r'DU[0-9].*', '', ref_str)

        match = re.search(r'[0-9]{2,4}-[0-9/]+', ref_str)
        return match.group(0) if match else ref_str

    @staticmethod
    def fix_encoding(text):
        if not text or not isinstance(text, str):
            return text
        try:
            if 'Ã' in text:
                return text.encode('latin1').decode('utf-8')
        except:
            pass
        return text

    def run(self):
        print("DÉMARRAGE DU PROCESSUS DE QUALITÉ")

        try:
            cur = self.get_cursor(as_dict=True)
            query_staging = self.read_sql_file('get_staging_abstrats.sql')
            cur.execute(query_staging)
            lignes_brutes = cur.fetchall()

            query_upsert = self.read_sql_file('upsert_abstrat.sql')
            query_rejet = self.read_sql_file('insert_rejet.sql')

            # =====================================================
            # NOUVEAU : INSERTION INTELLIGENTE DES RUBRIQUES
            # On insère les rubriques 8 ET les rubriques rattachées à des décisions AN/SEN
            # =====================================================
            cur.execute("""
                INSERT INTO public.rubriques (id_rubrique, num_rubrique, lib, niveau, parent_id)
                SELECT DISTINCT r.id, r.num_rubrique, r.lib, r.niveau, r.parent_id 
                FROM public.raw_rubriques r
                LEFT JOIN public.raw_abstrat a ON r.id = a.id_rubrique
                LEFT JOIN public.raw_decisions d ON a.decision_id = d.id
                WHERE r.num_rubrique LIKE '8%' 
                OR COALESCE(d.numero, d.referent) LIKE '%AN%' 
                  OR COALESCE(d.numero, d.referent) LIKE '%SEN%'
                ON CONFLICT (id_rubrique) DO NOTHING;
            """)
            self.conn.commit()

            # On récupère les ID des rubriques fraîchement insérées en production
            cur.execute("SELECT id_rubrique FROM public.rubriques")
            valid_rubriques = {r['id_rubrique'] for r in cur.fetchall()}

            # =====================================================
            # MODIFICATION ICI : On récupère sous forme de liste pour chercher les correspondances
            # =====================================================
            cur.execute("SELECT numero FROM public.decision WHERE numero IS NOT NULL")
            db_numeros = [r['numero'] for r in cur.fetchall()]

            # Parcours de chaque abstrat
            for row in lignes_brutes:

                ref_brute = row.get('numero')
                
                # Filtre : Exclusion immédiate des hors-sujets (QPC, etc.)
                if not ref_brute or ("AN" not in str(ref_brute).upper() and "SEN" not in str(ref_brute).upper()):
                    continue

                ref_propre = self.clean_reference(ref_brute)[:50]
                texte_propre = self.fix_encoding(row.get('resume_abstrat'))


                # =====================================================
                # MODIFICATION ICI : Recherche tolérante du numéro de décision
                # =====================================================
                vrai_numero_bdd = None
                
                # 1. On cherche d'abord la correspondance exacte
                if ref_propre in db_numeros:
                    vrai_numero_bdd = ref_propre
                else:
                    # 2. On cherche si le numéro de la BDD commence par notre référence propre (ex: "2008-4520 à 2008-4522")
                    for db_num in db_numeros:
                        db_num_str = str(db_num).strip()
                        if db_num_str.startswith(ref_propre):
                            # Sécurité : on s'assure que le caractère suivant n'est pas un chiffre
                            if len(db_num_str) > len(ref_propre) and db_num_str[len(ref_propre)].isdigit():
                                continue
                            vrai_numero_bdd = db_num
                            break


                # Cas 1 : texte de l’abstrat vide ou trop court
                if not texte_propre or len(str(texte_propre).strip()) < 10:
                    cur.execute(
                        query_rejet,
                        (
                            row['id_raw'],
                            row['decision_id_raw'],
                            "Le texte de l'abstrat est vide ou inférieur à 10 caractères.",
                            json.dumps(dict(row), default=self.json_serial)
                        )
                    )
                    self.compteur_rejets += 1

                # Cas 2 : La rubrique n'a pas été insérée (hors électoral ET non rattachée)
                elif row.get('id_rubrique') not in valid_rubriques:
                    cur.execute(
                        query_rejet,
                        (
                            row['id_raw'],
                            row['decision_id_raw'],
                            f"Rubrique exclue ou introuvable (ID: {row.get('id_rubrique')}).",
                            json.dumps(dict(row), default=self.json_serial)
                        )
                    )
                    self.compteur_rejets += 1

                # Cas 3 : La décision n'existe pas dans la base (Abstract orphelin, même avec la tolérance)
                elif vrai_numero_bdd is None:
                    cur.execute(
                        query_rejet,
                        (
                            row['id_raw'],
                            row['decision_id_raw'],
                            f"Référence orpheline : la décision {ref_propre} n'existe pas dans la base.",
                            json.dumps(dict(row), default=self.json_serial)
                        )
                    )
                    self.compteur_rejets += 1

                # Cas 4 : ligne valide -> Insertion (en utilisant vrai_numero_bdd)
                else:
                    cur.execute(
                        query_upsert,
                        (
                            row['id_raw'],                                              
                            vrai_numero_bdd,   # <-- On insère le numéro officiel extrait de la base                                              
                            row['id_rubrique'],                                         
                            texte_propre,                                               
                            json.dumps(row.get('motifs', []), default=self.json_serial) 
                        )
                    )
                    self.compteur_valides += 1

            self.conn.commit()
            print(f"Bilan Qualité : {self.compteur_valides} validés | {self.compteur_rejets} rejetés")

        except Exception as e:
            print(f"ERREUR FATALE : {e}")
            if self.conn:
                self.conn.rollback()
            sys.exit(1)

        finally:
            self.close()

if __name__ == "__main__":
    DataQualityProcessor().run()