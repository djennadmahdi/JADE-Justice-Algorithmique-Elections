-- Suppression des anciennes versions de la vue unifiée
DROP VIEW IF EXISTS public.v_abstrat_jade CASCADE;
DROP VIEW IF EXISTS public.vue_abstrat_jade CASCADE;

-- ==============================================================================
-- Création de la Vue JADE unifiée (Format v_abstrat_jade)
-- ==============================================================================
CREATE OR REPLACE VIEW public.v_abstrat_jade AS
SELECT 
    abs.id_abstrat,
    abs.numero,
    rub.lib AS theme_juridique,    
    rub.num_rubrique,             
    rub.lib AS rubrique_lib,       
    rub.parent_id,
    rub.niveau AS niveau_rubrique,
    SPLIT_PART(rub.num_rubrique, '.', 1) AS niveau_1,
CONCAT_WS('.', 
    SPLIT_PART(rub.num_rubrique, '.', 1),
    SPLIT_PART(rub.num_rubrique, '.', 2)
) AS niveau_2,
CONCAT_WS('.', 
    SPLIT_PART(rub.num_rubrique, '.', 1),
    SPLIT_PART(rub.num_rubrique, '.', 2),
    SPLIT_PART(rub.num_rubrique, '.', 3)
) AS niveau_3,
CONCAT_WS('.', 
    SPLIT_PART(rub.num_rubrique, '.', 1),
    SPLIT_PART(rub.num_rubrique, '.', 2),
    SPLIT_PART(rub.num_rubrique, '.', 3),
    SPLIT_PART(rub.num_rubrique, '.', 4)
) AS niveau_4,
CONCAT_WS('.', 
    SPLIT_PART(rub.num_rubrique, '.', 1),
    SPLIT_PART(rub.num_rubrique, '.', 2),
    SPLIT_PART(rub.num_rubrique, '.', 3),
    SPLIT_PART(rub.num_rubrique, '.', 4),
    SPLIT_PART(rub.num_rubrique, '.', 5)
) AS niveau_5,
    abs.texte_brut AS abstrat_text,
    dec.nature AS code_nature,
    dec.date_dec,
    vde.min_ecarts AS ecart_voix,
    vde.min_ecarts_pourcent AS ecart_voix_pourcent,
    vde.nb_tours,
    vde.solution_jade AS solution_decision,
    vde.legislature,
    dd.visas,
    dd.considerants,
    dd.decide,
    dd.contenu AS texte_integral,
    LENGTH(abs.texte_brut) AS longueur_abstrat,
    LENGTH(dd.contenu) AS longueur_texte_integral
FROM public.abstrat abs
LEFT JOIN public.rubriques rub ON abs.id_rubrique = rub.id_rubrique
INNER JOIN public.decision dec ON (
    abs.numero = REPLACE(REPLACE(UPPER(dec.numero), ' ', ''), CHR(160), '')
    OR 
    abs.numero = REPLACE(REPLACE(UPPER(dec.numero || dec.nature), ' ', ''), CHR(160), '')
)
LEFT JOIN public.v_decision_election vde 
    ON dec.id_source = vde.id_source
LEFT JOIN public.decision_detail dd 
    ON REPLACE(dec.numero, ' ', '') = REPLACE(dd.numero, ' ', '');

-- =====================================================
-- INDEX D'OPTIMISATION DES JOINTURES
-- =====================================================
-- Cet index supprime les goulots d'étranglement lors des calculs de chaînes (REPLACE/UPPER) dans le INNER JOIN
CREATE INDEX IF NOT EXISTS idx_abstrat_ref_perf ON public.abstrat (numero);