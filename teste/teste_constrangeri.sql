-- TEST 1: Constrangere sold negativ pe cont (trebuie sa esueze)
-- Asteptat: FAIL (chk_account_balance)
INSERT INTO accounts (user_id, name, type, balance) 
VALUES (1, 'Cont Ilegal Negativ', 'PRINCIPAL', -100.00);

-- TEST 2: Suma negativa la o plata planificata (trebuie sa esueze)
-- Asteptat: FAIL (chk_planned_amount)
INSERT INTO planned_payments (account_id, category_id, title, amount, target_month)
VALUES (1, 2, 'Plata Negativa', -50.00, '2026-10-01');

-- TEST 3: Email duplicat la utilizator (trebuie sa esueze)
-- Asteptat: FAIL (users_email_key / UK)
INSERT INTO users (email, first_name, last_name)
VALUES ('rares.rus@exemplu.ro', 'Test', 'Duplicat');

-- TEST 4: Cheie externa inexistenta (trebuie sa esueze)
-- Asteptat: FAIL (fk_accounts_users)
INSERT INTO accounts (user_id, name, type, balance)
VALUES (9999, 'Cont Fantoma', 'PRINCIPAL', 200.00);

-- TEST 5: Status invalid la plata planificata (trebuie sa esueze)
-- Asteptat: FAIL (chk_planned_status)
INSERT INTO planned_payments (account_id, category_id, title, amount, target_month, status)
VALUES (1, 2, 'Plata Status Invalid', 100.00, '2026-10-01', 'STATUS_INCORECT');
