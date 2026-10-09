-- View 1: Situatia platilor planificate pentru luna curenta
CREATE OR REPLACE VIEW v_plati_luna_curenta AS
SELECT 
    p.id AS plata_id,
    u.first_name || ' ' || u.last_name AS utilizator,
    a.name AS cont,
    c.name AS categorie,
    p.title AS titlu_plata,
    p.amount AS suma,
    p.due_date AS data_scadenta,
    p.status
FROM planned_payments p
JOIN accounts a ON p.account_id = a.id
JOIN users u ON a.user_id = u.id
JOIN categories c ON p.category_id = c.id
WHERE DATE_TRUNC('month', p.target_month) = DATE_TRUNC('month', CURRENT_DATE);

-- View 2: Progresul acumularii obiectivelor de economii
CREATE OR REPLACE VIEW v_progres_economii AS
SELECT 
    g.id AS obiectiv_id,
    u.first_name || ' ' || u.last_name AS utilizator,
    g.title AS obiectiv,
    g.target_amount AS tinta,
    g.current_amount AS acumulat,
    ROUND((g.current_amount / g.target_amount) * 100, 2) AS procent_progres,
    g.deadline
FROM savings_goals g
JOIN accounts a ON g.account_id = a.id
JOIN users u ON a.user_id = u.id;
