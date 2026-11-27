import os
import base64
import hashlib
import sqlite3
import calendar
from datetime import date
from decimal import Decimal
import mysql.connector

VAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_vault.db")
_VAULT_SECRET = b"ProiectBD_UTCN_CUNBM_2026_SecureVault!"


def _protect_secret(plain_text):
    if not plain_text:
        return ""
    raw = plain_text.encode("utf-8")
    key_stream = hashlib.sha256(_VAULT_SECRET).digest()
    xored = bytes(b ^ key_stream[i % len(key_stream)] for i, b in enumerate(raw))
    return base64.urlsafe_b64encode(xored).decode("ascii")


def _unprotect_secret(token_text):
    if not token_text:
        return ""
    xored = base64.urlsafe_b64decode(token_text.encode("ascii"))
    key_stream = hashlib.sha256(_VAULT_SECRET).digest()
    raw = bytes(b ^ key_stream[i % len(key_stream)] for i, b in enumerate(xored))
    return raw.decode("utf-8")


def _init_local_vault():
    conn = sqlite3.connect(VAULT_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS server_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                host TEXT NOT NULL,
                port INTEGER NOT NULL CHECK (port BETWEEN 1 AND 65535),
                database_name TEXT NOT NULL,
                db_user TEXT NOT NULL,
                encrypted_password TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur = conn.execute("SELECT COUNT(*) FROM server_config WHERE id = 1")
        if cur.fetchone()[0] == 0:
            conn.execute("""
                INSERT INTO server_config (id, host, port, database_name, db_user, encrypted_password)
                VALUES (1, ?, ?, ?, ?, ?)
            """, ("localhost", 3306, "personal_finance", "app_user", _protect_secret("app_pass")))
        conn.commit()
    finally:
        conn.close()


def load_vault_config():
    _init_local_vault()
    conn = sqlite3.connect(VAULT_PATH)
    try:
        row = conn.execute("""
            SELECT host, port, database_name, db_user, encrypted_password
            FROM server_config WHERE id = 1
        """).fetchone()
        return {
            "host": row[0],
            "port": int(row[1]),
            "database": row[2],
            "user": row[3],
            "password": _unprotect_secret(row[4]),
        }
    finally:
        conn.close()


DB_CONFIG = load_vault_config()


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def test_and_update_config(new_cfg):
    # 1. Validăm conexiunea live la serverul MySQL înainte de a salva în SQLite
    conn_mysql = mysql.connector.connect(**new_cfg)
    conn_mysql.close()

    # 2. Salvăm atomic în baza de date locală SQLite cu parola criptată
    _init_local_vault()
    conn_sq = sqlite3.connect(VAULT_PATH)
    try:
        conn_sq.execute("""
            UPDATE server_config
            SET host = ?, port = ?, database_name = ?, db_user = ?,
                encrypted_password = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (
            new_cfg["host"], int(new_cfg["port"]), new_cfg["database"],
            new_cfg["user"], _protect_secret(new_cfg["password"])
        ))
        conn_sq.commit()
    finally:
        conn_sq.close()

    DB_CONFIG.update(new_cfg)


def hash_password(raw_password):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", raw_password.encode("utf-8"), salt, 100_000)
    return f"pbkdf2${salt.hex()}${dk.hex()}"


def verify_password(raw_password, stored_hash):
    if stored_hash.startswith("pbkdf2$"):
        _, salt_hex, dk_hex = stored_hash.split("$", 2)
        dk = hashlib.pbkdf2_hmac("sha256", raw_password.encode("utf-8"), bytes.fromhex(salt_hex), 100_000)
        return dk.hex() == dk_hex
    legacy_sha256 = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
    return stored_hash in (legacy_sha256, raw_password)


def authenticate_user(email, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id, full_name, email, password_hash FROM users WHERE email = %s", (email.strip(),))
        user = cur.fetchone()
        if not user:
            return None
        if verify_password(password, user["password_hash"]):
            return {"id": user["id"], "full_name": user["full_name"], "email": user["email"]}
        return None
    finally:
        cur.close()
        conn.close()


def register_user_acid(full_name, email, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        conn.start_transaction()
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)",
            (full_name.strip(), email.strip(), hash_password(password))
        )
        new_user_id = cur.lastrowid

        cur.execute("SELECT id FROM currencies WHERE code = 'RON' LIMIT 1")
        row_curr = cur.fetchone()
        curr_id = row_curr[0] if row_curr else 1

        cur.execute("""
            INSERT INTO accounts (user_id, currency_id, name, type, balance)
            VALUES (%s, %s, 'Cont Principal', 'CURENT', 0.00)
        """, (new_user_id, curr_id))

        conn.commit()
        return {"id": new_user_id, "full_name": full_name.strip(), "email": email.strip()}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def get_dashboard_summary(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(a.balance * c.exchange_rate), 0) AS total_brut
            FROM accounts a
            JOIN currencies c ON a.currency_id = c.id
            WHERE a.user_id = %s
        """, (user_id,))
        sold_brut = Decimal(cursor.fetchone()["total_brut"])

        cursor.execute("""
            SELECT COALESCE(SUM(pp.amount * c.exchange_rate), 0) AS total_planificat
            FROM planned_payments pp
            JOIN accounts a ON pp.account_id = a.id
            JOIN currencies c ON a.currency_id = c.id
            WHERE a.user_id = %s
              AND pp.status = 'PLANIFICAT'
              AND pp.due_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 60 DAY)
        """, (user_id,))
        obligatii = Decimal(cursor.fetchone()["total_planificat"])

        cursor.execute("""
            SELECT COALESCE(SUM(sg.current_amount * c.exchange_rate), 0) AS total_economii
            FROM savings_goals sg
            JOIN accounts a ON sg.account_id = a.id
            JOIN currencies c ON a.currency_id = c.id
            WHERE a.user_id = %s
        """, (user_id,))
        economii_blocate = Decimal(cursor.fetchone()["total_economii"])

        cursor.execute("""
            SELECT a.id, a.name, a.type, a.balance, c.code AS currency_code
            FROM accounts a
            JOIN currencies c ON a.currency_id = c.id
            WHERE a.user_id = %s
            ORDER BY a.id ASC
        """, (user_id,))
        accounts = cursor.fetchall()

        cursor.execute("""
            SELECT COALESCE(c.name, 'Necategorisit') AS cat_name, SUM(t.amount) AS total_cat
            FROM transactions t
            JOIN accounts a ON t.source_account_id = a.id
            LEFT JOIN subcategories s ON t.subcategory_id = s.id
            LEFT JOIN categories c ON s.category_id = c.id
            WHERE a.user_id = %s AND t.type = 'CHELTUIALA'
            GROUP BY c.name
            ORDER BY total_cat DESC
            LIMIT 3
        """, (user_id,))
        top_categories = cursor.fetchall()

        return {
            "sold_brut": sold_brut,
            "obligatii": obligatii,
            "economii_blocate": economii_blocate,
            "disponibil_real": sold_brut - obligatii - economii_blocate,
            "accounts": accounts,
            "top_categories": top_categories,
        }
    finally:
        cursor.close()
        conn.close()


def get_transactions(user_id, tx_type="TOATE", search_query=""):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        q_text = f"%{search_query.strip()}%"
        sql = """
            SELECT t.id, t.type, t.amount,
                   COALESCE(a_src.name, '—') AS src_name,
                   COALESCE(a_dst.name, '—') AS dst_name,
                   COALESCE(pm.name, '—') AS pm_name,
                   COALESCE(s.name, 'General') AS subcat_name,
                   COALESCE(t.description, '—') AS descr,
                   DATE_FORMAT(t.transaction_date, '%d.%m.%Y %H:%i') AS tx_date
            FROM transactions t
            LEFT JOIN accounts a_src ON t.source_account_id = a_src.id
            LEFT JOIN accounts a_dst ON t.destination_account_id = a_dst.id
            LEFT JOIN payment_methods pm ON t.payment_method_id = pm.id
            LEFT JOIN subcategories s ON t.subcategory_id = s.id
            WHERE (a_src.user_id = %s OR a_dst.user_id = %s)
              AND (COALESCE(t.description, '') LIKE %s OR COALESCE(s.name, '') LIKE %s)
        """
        params = [user_id, user_id, q_text, q_text]
        if tx_type != "TOATE":
            sql += " AND t.type = %s"
            params.append(tx_type)
        sql += " ORDER BY t.transaction_date DESC, t.id DESC LIMIT 25"
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_form_metadata(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, balance FROM accounts WHERE user_id = %s", (user_id,))
        accounts = cursor.fetchall()

        cursor.execute("""
            SELECT s.id, CONCAT(c.name, '  →  ', s.name) AS full_name, c.is_income
            FROM subcategories s
            JOIN categories c ON s.category_id = c.id
            WHERE c.user_id IS NULL OR c.user_id = %s
        """, (user_id,))
        subcats = cursor.fetchall()

        cursor.execute("SELECT id, name, masked_details FROM payment_methods WHERE user_id = %s", (user_id,))
        pay_methods = cursor.fetchall()

        return {"accounts": accounts, "subcats": subcats, "pay_methods": pay_methods}
    finally:
        cursor.close()
        conn.close()


def create_transaction_acid(src_id, dst_id, pm_id, sub_id, tx_type, amount, desc):
    conn = get_connection()
    cur = conn.cursor()
    try:
        conn.start_transaction()
        cur.execute("""
            INSERT INTO transactions (
                source_account_id, destination_account_id, payment_method_id,
                subcategory_id, type, amount, description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (src_id, dst_id, pm_id, sub_id, tx_type, amount, desc))

        if src_id:
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, src_id))
        if dst_id:
            cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, dst_id))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def get_planned_payments(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT pp.id, pp.title, pp.amount, pp.due_date, pp.status,
                   COALESCE(rr.frequency, 'MANUAL') AS freq, a.name AS account_name
            FROM planned_payments pp
            JOIN accounts a ON pp.account_id = a.id
            LEFT JOIN recurring_rules rr ON pp.recurring_rule_id = rr.id
            WHERE a.user_id = %s
            ORDER BY pp.due_date ASC
        """, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def pay_planned_payment_acid(pp_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        cur.execute("SELECT * FROM planned_payments WHERE id = %s FOR UPDATE", (pp_id,))
        pp_row = cur.fetchone()

        cur.execute("UPDATE planned_payments SET status = 'ACHITAT' WHERE id = %s", (pp_id,))
        cur.execute("""
            INSERT INTO transactions (source_account_id, subcategory_id, type, amount, description)
            VALUES (%s, %s, 'CHELTUIALA', %s, %s)
        """, (pp_row["account_id"], pp_row["subcategory_id"], pp_row["amount"], f"Plată scadentă: {pp_row['title']}"))
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (pp_row["amount"], pp_row["account_id"]))

        conn.commit()
        return pp_row["title"]
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def create_recurring_rule_acid(user_id, acc_id, sub_id, title, freq, due_day, amount):
    today = date.today()
    conn = get_connection()
    cur = conn.cursor()
    try:
        conn.start_transaction()
        cur.execute("""
            INSERT INTO recurring_rules (user_id, frequency, due_day, start_date, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (user_id, freq, due_day, today))
        rule_id = cur.lastrowid

        months_to_generate = [0, 1] if freq == "LUNAR" else [0]
        generated_count = 0
        for offset in months_to_generate:
            y = today.year + (today.month + offset - 1) // 12
            m = (today.month + offset - 1) % 12 + 1
            last_day = calendar.monthrange(y, m)[1]
            d = min(due_day, last_day)
            due_dt = date(y, m, d)
            target_m = date(y, m, 1)

            if due_dt >= today:
                cur.execute("""
                    INSERT INTO planned_payments (
                        account_id, subcategory_id, recurring_rule_id,
                        title, amount, target_month, due_date, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'PLANIFICAT')
                """, (acc_id, sub_id, rule_id, f"{title} ({m:02d}/{y})", amount, target_m, due_dt))
                generated_count += 1

        conn.commit()
        return generated_count
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def get_savings_goals(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT sg.id, sg.account_id, sg.title AS name, sg.target_amount,
                   sg.current_amount, sg.deadline, a.name AS account_name
            FROM savings_goals sg
            JOIN accounts a ON sg.account_id = a.id
            WHERE a.user_id = %s
            ORDER BY sg.id ASC
        """, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def allocate_to_goal_acid(goal_id, goal_name, src_acc_id, dest_acc_id, amount):
    conn = get_connection()
    cur = conn.cursor()
    try:
        conn.start_transaction()
        cur.execute("UPDATE savings_goals SET current_amount = current_amount + %s WHERE id = %s", (amount, goal_id))
        if src_acc_id != dest_acc_id:
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, src_acc_id))
            cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, dest_acc_id))
            cur.execute("""
                INSERT INTO transactions (source_account_id, destination_account_id, type, amount, description)
                VALUES (%s, %s, 'TRANSFER', %s, %s)
            """, (src_acc_id, dest_acc_id, amount, f"Economisire: {goal_name}"))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def create_savings_goal(account_id, title, target_amount, deadline):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO savings_goals (account_id, title, target_amount, current_amount, deadline)
            VALUES (%s, %s, %s, 0.00, %s)
        """, (account_id, title, target_amount, deadline))
        conn.commit()
    finally:
        cur.close()
        conn.close()
