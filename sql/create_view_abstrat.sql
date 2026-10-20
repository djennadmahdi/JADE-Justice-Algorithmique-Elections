-- Suppression des anciennes versions
DROP VIEW IF EXISTS public.v_jade_elections CASCADE;
DROP VIEW IF EXISTS public.v_abstrat_hors_elections CASCADE;
DROP VIEW IF EXISTS public.vue_jade_elections CASCADE;
DROP VIEW IF EXISTS public.vue_abstrat_hors_elections CASCADE;

-- =====================================================
-- 1. VUE JADE : UNIQUEMENT LES ÉLECTIONS (AN & SEN)
-- =====================================================
CREATE OR REPLACE VIEW public.v_jade_elections AS
SELECT 
    abs.id_abstrat,
    abs.numero,
    dec.date_dec AS date_decision,
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
    abs.texte_brut
FROM public.abstrat abs
LEFT JOIN public.rubriques rub ON abs.id_rubrique = rub.id_rubrique
INNER JOIN public.decision dec ON (
    abs.numero = REPLACE(REPLACE(UPPER(dec.numero), ' ', ''), CHR(160), '')
    OR 
    abs.numero = REPLACE(REPLACE(UPPER(dec.numero || dec.nature), ' ', ''), CHR(160), '')
)
WHERE dec.nature IN ('AN', 'SEN');

-- =====================================================
-- 2. VUE GÉNÉRALE : TOUT SAUF LES ÉLECTIONS
-- =====================================================
CREATE OR REPLACE VIEW public.v_abstrat_hors_elections AS
SELECT 
    abs.id_abstrat,
    abs.numero,
    dec.date_dec AS date_decision,
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
    abs.texte_brut
FROM public.abstrat abs
LEFT JOIN public.rubriques rub ON abs.id_rubrique = rub.id_rubrique
INNER JOIN public.decision dec ON (
    abs.numero = REPLACE(REPLACE(UPPER(dec.numero), ' ', ''), CHR(160), '')
    OR 
    abs.numero = REPLACE(REPLACE(UPPER(dec.numero || dec.nature), ' ', ''), CHR(160), '')
)
WHERE dec.nature NOT IN ('AN', 'SEN') OR dec.nature IS NULL;

-- =====================================================
-- INDEX D'OPTIMISATION
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_abstrat_ref_search ON public.abstrat (numero);