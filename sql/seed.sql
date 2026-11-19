USE personal_finance;

INSERT INTO users (email, password_hash, first_name, last_name) VALUES
('rares.rus@student.cunbm.ro', 'sha256_hash_demo_123', 'Rareș', 'Rus');

INSERT INTO currencies (code, name, symbol, exchange_rate) VALUES
('RON', 'Leu Românesc', 'lei', 1.0000),
('EUR', 'Euro', '€', 4.9750);

INSERT INTO accounts (user_id, currency_id, name, type, balance) VALUES
(1, 1, 'Cont Curent Banca Transilvania', 'PRINCIPAL', 4500.00),
(1, 1, 'Fond Urgență & Economii', 'ECONOMII', 3200.00),
(1, 1, 'Portofel Numerar', 'CASH', 350.00);

INSERT INTO categories (user_id, name, is_income) VALUES
(NULL, 'Locuință & Utilități', FALSE),
(NULL, 'Alimentație', FALSE),
(NULL, 'Venituri Salariale / Burse', TRUE),
(1, 'Proiecte & Hardware IT', FALSE);

INSERT INTO subcategories (category_id, name) VALUES
(1, 'Chirie Apartament'),
(1, 'Energie Electrică & Gaz'),
(2, 'Supermarket'),
(3, 'Bursă Universitară'),
(4, 'Componente PC');

INSERT INTO recurring_rules (user_id, frequency, due_day, start_date) VALUES
(1, 'LUNAR', 15, '2026-11-01'),
(1, 'LUNAR', 25, '2026-11-01');

INSERT INTO planned_payments (account_id, subcategory_id, recurring_rule_id, title, amount, target_month, due_date, status) VALUES
(1, 1, 1, 'Chirie Apartament Noiembrie', 1400.00, '2026-11-01', '2026-11-15', 'PLANIFICAT'),
(1, 2, 2, 'Factură Electrica & Gaz', 320.00, '2026-11-01', '2026-11-25', 'PLANIFICAT'),
(1, 1, 1, 'Chirie Apartament Decembrie', 1400.00, '2026-12-01', '2026-12-15', 'PLANIFICAT');

INSERT INTO transactions (source_account_id, destination_account_id, subcategory_id, type, amount, description) VALUES
(NULL, 1, 4, 'VENIT', 1200.00, 'Încasare bursă de studiu'),
(1, NULL, 3, 'CHELTUIALA', 245.50, 'Cumpărături săptămânale'),
(1, 2, NULL, 'TRANSFER', 500.00, 'Economii lunare');

INSERT INTO savings_goals (account_id, title, target_amount, current_amount, deadline) VALUES
(2, 'Fond de Urgență (6 luni)', 10000.00, 3200.00, '2027-06-01'),
(2, 'Upgrade Stație Lucru & Laptop', 4500.00, 1350.00, '2027-03-15');

INSERT INTO payment_methods (user_id, name, type, masked_details) VALUES
(1, 'Card Debit Banca Transilvania', 'CARD_DEBIT', '*4512'),
(1, 'Numerar Portofel', 'CASH', NULL),
(1, 'Internet Banking BT24', 'TRANSFER', 'RO98BTRL...');
