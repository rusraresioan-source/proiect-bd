-- 1. Soldul curent pentru fiecare utilizator
SELECT u.id, u.first_name, u.last_name, a.name AS cont, a.balance, a.currency
FROM users u
JOIN accounts a ON u.id = a.user_id;

-- 2. Totalul platilor planificate neachitate pe luna curenta
SELECT a.name AS cont, SUM(p.amount) AS total_de_plata
FROM planned_payments p
JOIN accounts a ON p.account_id = a.id
WHERE p.status = 'PLANIFICAT'
GROUP BY a.name;

-- 3. Toate platile scadente in urmatoarele 7 zile
SELECT title, amount, due_date, status
FROM planned_payments
WHERE status = 'PLANIFICAT' AND due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days';

-- 4. Situatia cheltuielilor grupate pe categorii
SELECT c.name AS categorie, COUNT(t.id) AS numar_tranzactii, SUM(t.amount) AS total_cheltuit
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.type = 'CHELTUIALA'
GROUP BY c.name
ORDER BY total_cheltuit DESC;

-- 5. Venitul total incasat per utilizator
SELECT u.first_name, u.last_name, SUM(t.amount) AS total_venituri
FROM transactions t
JOIN accounts a ON t.destination_account_id = a.id
JOIN users u ON a.user_id = u.id
WHERE t.type = 'VENIT'
GROUP BY u.id, u.first_name, u.last_name;

-- 6. Calcul fond disponibil real (Sold curent minus plati neachitate)
SELECT 
    a.name AS cont,
    a.balance AS sold_cont,
    COALESCE(SUM(p.amount), 0) AS plati_blocate,
    a.balance - COALESCE(SUM(p.amount), 0) AS disponibil_real
FROM accounts a
LEFT JOIN planned_payments p ON a.id = p.account_id AND p.status = 'PLANIFICAT'
WHERE a.type = 'PRINCIPAL'
GROUP BY a.id, a.name, a.balance;

-- 7. Platile recurente programate pentru luna urmatoare
SELECT title, amount, target_month, status
FROM planned_payments
WHERE is_recurring = TRUE AND target_month > CURRENT_DATE;

-- 8. Progresul procentual al fiecarui obiectiv de economii
SELECT 
    title, 
    target_amount, 
    current_amount,
    ROUND((current_amount / target_amount) * 100, 2) AS procentaj_atins
FROM savings_goals
WHERE deadline >= CURRENT_DATE;

-- 9. Utilizatorii care au obiective de economisire sub 50%
SELECT u.first_name, u.last_name, g.title, g.current_amount, g.target_amount
FROM savings_goals g
JOIN accounts a ON g.account_id = a.id
JOIN users u ON a.user_id = u.id
WHERE (g.current_amount / g.target_amount) < 0.50;

-- 10. Tranzactiile cele mai mari (top 5 cheltuieli)
SELECT t.id, t.transaction_date, c.name AS categorie, t.amount, t.description
FROM transactions t
LEFT JOIN categories c ON t.category_id = c.id
WHERE t.type = 'CHELTUIALA'
ORDER BY t.amount DESC
LIMIT 5;

-- 11. Suma totala transferata in contul de economii
SELECT a.name AS cont_economii, SUM(t.amount) AS total_economisit
FROM transactions t
JOIN accounts a ON t.destination_account_id = a.id
WHERE t.type = 'TRANSFER_ECONOMII'
GROUP BY a.name;

-- 12. Categorii care nu au nicio tranzactie inregistrata
SELECT c.name
FROM categories c
LEFT JOIN transactions t ON c.id = t.category_id
WHERE t.id IS NULL;

-- 13. Numarul de plati planificate dupa status
SELECT status, COUNT(*) AS numar_plati, SUM(amount) AS valoare_totala
FROM planned_payments
GROUP BY status;

-- 14. Istoricul tranzactiilor pentru un anumit cont (extrase cont)
SELECT t.transaction_date, t.type, t.amount, t.description
FROM transactions t
WHERE t.source_account_id = 1 OR t.destination_account_id = 1
ORDER BY t.transaction_date DESC;

-- 15. Conturile cu sold peste media tuturor conturilor
SELECT name, type, balance
FROM accounts
WHERE balance > (SELECT AVG(balance) FROM accounts);

-- 16. Plati planificate care depasesc soldul actual al contului
SELECT a.name, a.balance, p.title, p.amount
FROM planned_payments p
JOIN accounts a ON p.account_id = a.id
WHERE p.status = 'PLANIFICAT' AND p.amount > a.balance;

-- 17. Ponderea fiecarei cheltuieli in totalul cheltuielilor efectuate
SELECT 
    description,
    amount,
    ROUND((amount / (SELECT SUM(amount) FROM transactions WHERE type = 'CHELTUIALA')) * 100, 2) AS pondere_procent
FROM transactions
WHERE type = 'CHELTUIALA';

-- 18. Platile achitate grupate pe luna calendaristica
SELECT 
    TO_CHAR(target_month, 'YYYY-MM') AS luna,
    COUNT(*) AS total_plati_achitate,
    SUM(amount) AS suma_totala
FROM planned_payments
WHERE status = 'ACHITAT'
GROUP BY TO_CHAR(target_month, 'YYYY-MM');

-- 19. Utilizatorii si numarul total de conturi detinute
SELECT u.id, u.first_name, u.last_name, COUNT(a.id) AS numar_conturi
FROM users u
LEFT JOIN accounts a ON u.id = a.user_id
GROUP BY u.id, u.first_name, u.last_name;

-- 20. Tranzactii cu rang analitic descrescator dupa suma per categorie
SELECT 
    c.name AS categorie,
    t.amount,
    t.description,
    DENSE_RANK() OVER (PARTITION BY t.category_id ORDER BY t.amount DESC) AS rang_suma
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.type = 'CHELTUIALA';
