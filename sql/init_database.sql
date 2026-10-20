-- Suppression des tables si elles existent
DROP TABLE IF EXISTS public.abstrat CASCADE;
DROP TABLE IF EXISTS public.raw_abstrat CASCADE;
DROP TABLE IF EXISTS public.raw_rubriques CASCADE;
DROP TABLE IF EXISTS public.raw_decisions CASCADE;
DROP TABLE IF EXISTS public.raw_types CASCADE;

ALTER TABLE public.decision DROP CONSTRAINT IF EXISTS uk_decision_numero;
ALTER TABLE public.decision ADD CONSTRAINT uk_decision_numero UNIQUE (numero);

-- 1. TABLES DE STAGING (RAW)
CREATE TABLE public.raw_abstrat (
    id INTEGER PRIMARY KEY,
    statut_abstrat_id INTEGER,
    resume_abstrat_id INTEGER,
    id_rubrique INTEGER,
    decision_id INTEGER,
    solution_implicite TEXT,
    resume_abstrat TEXT,
    renvoi_rubrique_id INTEGER,
    motifs JSONB
);

CREATE TABLE public.raw_rubriques (
    id INTEGER PRIMARY KEY,
    lib TEXT,
    niveau INTEGER,
    num_rubrique VARCHAR(50),
    parent_id INTEGER,
    renvoi_rubrique_id INTEGER,
    ordre INTEGER
);

CREATE TABLE public.raw_decisions (
    id INTEGER PRIMARY KEY,
    date_decision DATE,
    intitule TEXT,
    numero VARCHAR(50),
    referent VARCHAR(50),  -- CORRECTION ICI : Ajout de la colonne
    lien_site_web TEXT,
    lien_legifrance VARCHAR(50),
    ecli VARCHAR(100),
    type_decision_id INTEGER,
    sous_type_decision_id INTEGER,
    departement_id INTEGER,
    demandeurs TEXT,
    defendeurs TEXT,
    premiere_saisine_le DATE,
    affaire_greffe_id VARCHAR(50)
);

CREATE TABLE public.raw_types (
    id INTEGER PRIMARY KEY,
    type_decision_code VARCHAR(50),
    sous_type_decision_lib TEXT
);

-- 2. TABLES DE PRODUCTION ENRICHIES
DROP TABLE IF EXISTS public.rubriques CASCADE;

-- A) On crée D'ABORD la table rubriques
CREATE TABLE public.rubriques (
    id_rubrique INTEGER PRIMARY KEY,
    num_rubrique VARCHAR(50),
    lib TEXT,
    niveau INTEGER,
    parent_id INTEGER
);

-- Dans public.abstrat, ajoutez la référence vers public.decision
CREATE TABLE public.abstrat (
    id_abstrat INTEGER PRIMARY KEY,
    numero VARCHAR(50),
    id_rubrique INTEGER,
    texte_brut TEXT,
    motifs_invoques JSONB,
    FOREIGN KEY (id_rubrique) REFERENCES public.rubriques(id_rubrique),
    -- NOUVELLE CONTRAINTE :
    FOREIGN KEY (numero) REFERENCES public.decision(numero)
);