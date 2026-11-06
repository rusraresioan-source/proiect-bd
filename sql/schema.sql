-- ============================================================================
-- DISCIPLINA: Proiectarea Bazelor de Date
-- PROIECT: Sistem de Gestiune a Finanțelor Personale și a Plăților Recurente
-- COORDONATOR: Bogdan Văduva
-- STUDENT: Rus Rareș-Ioan (Anul III)
-- MOTOR STOCARE: MySQL 8.0 InnoDB (Suport complet ACID & Multi-Tenant)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS personal_finance
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE personal_finance;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS savings_goals;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS planned_payments;
DROP TABLE IF EXISTS recurring_rules;
DROP TABLE IF EXISTS payment_methods;
DROP TABLE IF EXISTS subcategories;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS currencies;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. USERS
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. CURRENCIES
CREATE TABLE currencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(3) NOT NULL,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(5) NOT NULL,
    exchange_rate DECIMAL(10,4) NOT NULL DEFAULT 1.0000,
    CONSTRAINT uq_currencies_code UNIQUE (code),
    CONSTRAINT chk_currencies_rate CHECK (exchange_rate > 0.0000)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. ACCOUNTS
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    currency_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type ENUM('PRINCIPAL', 'ECONOMII', 'CASH') NOT NULL DEFAULT 'PRINCIPAL',
    balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_accounts_user 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_accounts_currency 
        FOREIGN KEY (currency_id) REFERENCES currencies(id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_accounts_balance CHECK (balance >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. CATEGORIES
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    name VARCHAR(60) NOT NULL,
    is_income BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_categories_user 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_categories_user_name UNIQUE (user_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. SUBCATEGORIES
CREATE TABLE subcategories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(60) NOT NULL,
    CONSTRAINT fk_subcategories_category 
        FOREIGN KEY (category_id) REFERENCES categories(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_subcategories_category_name UNIQUE (category_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. PAYMENT_METHODS
CREATE TABLE payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(60) NOT NULL,
    type ENUM('CARD_DEBIT', 'CARD_CREDIT', 'CASH', 'TRANSFER') NOT NULL DEFAULT 'CARD_DEBIT',
    masked_details VARCHAR(20) NULL,
    CONSTRAINT fk_payment_methods_user 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. RECURRING_RULES
CREATE TABLE recurring_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    frequency ENUM('LUNAR', 'TRIMESTRIAL', 'ANUAL') NOT NULL DEFAULT 'LUNAR',
    due_day TINYINT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    CONSTRAINT fk_recurring_rules_user 
        FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_recurring_due_day CHECK (due_day BETWEEN 1 AND 31),
    CONSTRAINT chk_recurring_dates CHECK (end_date IS NULL OR end_date >= start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. PLANNED_PAYMENTS
CREATE TABLE planned_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    subcategory_id INT NOT NULL,
    recurring_rule_id INT NULL,
    title VARCHAR(150) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    target_month DATE NOT NULL,
    due_date DATE NOT NULL,
    status ENUM('PLANIFICAT', 'ACHITAT', 'ANULAT') NOT NULL DEFAULT 'PLANIFICAT',
    CONSTRAINT fk_planned_payments_account 
        FOREIGN KEY (account_id) REFERENCES accounts(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_planned_payments_subcategory 
        FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_planned_payments_rule 
        FOREIGN KEY (recurring_rule_id) REFERENCES recurring_rules(id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_planned_payments_amount CHECK (amount > 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. TRANSACTIONS
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_account_id INT NULL,
    destination_account_id INT NULL,
    subcategory_id INT NULL,
    payment_method_id INT NULL,
    type ENUM('CHELTUIALA', 'VENIT', 'TRANSFER') NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT NULL,
    CONSTRAINT fk_transactions_source_account 
        FOREIGN KEY (source_account_id) REFERENCES accounts(id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_transactions_dest_account 
        FOREIGN KEY (destination_account_id) REFERENCES accounts(id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_transactions_subcategory 
        FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_transactions_payment_method 
        FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_transactions_amount CHECK (amount > 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. SAVINGS_GOALS
CREATE TABLE savings_goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    target_amount DECIMAL(12,2) NOT NULL,
    current_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    deadline DATE NULL,
    CONSTRAINT fk_savings_goals_account 
        FOREIGN KEY (account_id) REFERENCES accounts(id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_savings_target CHECK (target_amount > 0.00),
    CONSTRAINT chk_savings_current CHECK (current_amount >= 0.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- INDECSI
CREATE INDEX idx_accounts_user ON accounts(user_id);
CREATE INDEX idx_transactions_source ON transactions(source_account_id);
CREATE INDEX idx_transactions_dest ON transactions(destination_account_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_planned_payments_due ON planned_payments(account_id, status, target_month);
