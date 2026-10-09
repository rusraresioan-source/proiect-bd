-- 1. Utilizatori
INSERT INTO users (id, email, first_name, last_name) VALUES
(1, 'rares.rus@exemplu.ro', 'Rares', 'Rus'),
(2, 'andrei.pop@exemplu.ro', 'Andrei', 'Pop');

-- 2. Conturi
INSERT INTO accounts (id, user_id, name, type, balance, currency) VALUES
(1, 1, 'Cont Curent Salariu', 'PRINCIPAL', 4500.00, 'RON'),
(2, 1, 'Fond de Rezerva', 'ECONOMII', 3200.00, 'RON'),
(3, 2, 'Cont Curent', 'PRINCIPAL', 5100.00, 'RON'),
(4, 2, 'Economii Concediu', 'ECONOMII', 1500.00, 'RON');

-- 3. Categorii
INSERT INTO categories (id, name, is_income) VALUES
(1, 'Salariu', TRUE),
(2, 'Chirie', FALSE),
(3, 'Utilitati', FALSE),
(4, 'Supermarket', FALSE),
(5, 'Abonamente / Internet', FALSE),
(6, 'Economii Lunare', FALSE);

-- 4. Plati Planificate (Luna curenta si Luna urmatoare)
INSERT INTO planned_payments (id, account_id, category_id, title, amount, target_month, due_date, status, is_recurring) VALUES
(1, 1, 2, 'Chirie Octombrie', 1500.00, '2026-10-01', '2026-10-15', 'ACHITAT', TRUE),
(2, 1, 3, 'Factura Energie Electrica', 220.00, '2026-10-01', '2026-10-20', 'PLANIFICAT', TRUE),
(3, 1, 5, 'Abonament Telefonie', 65.00, '2026-10-01', '2026-10-25', 'PLANIFICAT', TRUE),
(4, 1, 2, 'Chirie Noiembrie (Prognoza)', 1500.00, '2026-11-01', '2026-11-15', 'PLANIFICAT', TRUE),
(5, 1, 3, 'Utilitati Noiembrie (Prognoza)', 300.00, '2026-11-01', '2026-11-20', 'PLANIFICAT', TRUE);

-- 5. Tranzactii efectuate
INSERT INTO transactions (id, source_account_id, destination_account_id, category_id, planned_payment_id, type, amount, description) VALUES
(1, NULL, 1, 1, NULL, 'VENIT', 5500.00, 'Incasare salariu luna curenta'),
(2, 1, NULL, 2, 1, 'CHELTUIALA', 1500.00, 'Plata chirie conform planificare'),
(3, 1, 2, 6, NULL, 'TRANSFER_ECONOMII', 500.00, 'Transfer automat 10% spre fondul de rezerva'),
(4, 1, NULL, 4, NULL, 'CHELTUIALA', 280.00, 'Cumparaturi saptamanale alimente');

-- 6. Obiective de economisire
INSERT INTO savings_goals (id, account_id, title, target_amount, current_amount, deadline) VALUES
(1, 2, 'Fond Siguranta 3 Luni', 10000.00, 3200.00, '2027-03-01'),
(2, 4, 'Vacanta Vara', 5000.00, 1500.00, '2027-07-01');
