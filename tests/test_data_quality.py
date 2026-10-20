import pytest  # Framework de tests Python

# Importation de la classe contenant les fonctions à tester
from src.implementation_abstrats.data_quality import DataQualityProcessor


# =========================================================
# Test de la fonction clean_reference()
# =========================================================

# @pytest.mark.parametrize permet de tester plusieurs cas automatiquement
# Chaque tuple contient :
# (valeur d’entrée, résultat attendu)

@pytest.mark.parametrize("input_ref, expected", [

    # Cas standard avec "DÉCISION N°"
    ("DÉCISION N° 2022-123 AN DU 15 DÉCEMBRE 2022", "2022-123AN"),

    # Cas avec "DECISION NO"
    ("DECISION NO 2024-456 SEN", "2024-456SEN"),

    # Cas avec slash dans la référence
    ("2023-789/2 AN", "2023-789/2AN"),

    # Cas avec espaces inutiles
    ("  2021-555  AN  ", "2021-555AN"),

    # Cas vide
    ("", ""),

    # Cas valeur None
    (None, ""),

    # Cas sans identifiant juridique détectable
    ("TEXTE SANS CHIFFRE", "TEXTESANSCHIFFRE")
])

def test_clean_reference(input_ref, expected):

    # Création d’une instance du processeur qualité
    processor = DataQualityProcessor()

    # Vérifie que le résultat obtenu correspond au résultat attendu
    assert processor.clean_reference(input_ref) == expected


# =========================================================
# Test de la fonction fix_encoding()
# =========================================================

# Teste plusieurs cas de problèmes d’encodage UTF-8 / Latin1

@pytest.mark.parametrize("input_text, expected", [

    # Cas de texte mal encodé
    ("ArrÃªt de la Cour", "Arrêt de la Cour"),

    # Cas de texte mal encodé
    ("DÃ©cision du Conseil", "Décision du Conseil"),

    # Cas déjà correct
    ("Texte déjà propre", "Texte déjà propre"),

    # Cas chaîne vide
    ("", ""),

    # Cas valeur None
    (None, None)
])

def test_fix_encoding(input_text, expected):

    # Création d’une instance du processeur qualité
    processor = DataQualityProcessor()

    # Vérifie que le texte corrigé correspond au résultat attendu
    assert processor.fix_encoding(input_text) == expected