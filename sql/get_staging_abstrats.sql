SELECT 
    a.id AS id_raw, 
    a.resume_abstrat, 
    a.motifs, 
    a.decision_id AS decision_id_raw,
    COALESCE(d.numero, d.referent) AS numero, 
    d.date_decision, 
    a.id_rubrique,     
    t.sous_type_decision_lib AS type_recours
FROM raw_abstrat a
LEFT JOIN raw_decisions d ON a.decision_id = d.id
LEFT JOIN raw_types t ON d.sous_type_decision_id = t.id;