import customtkinter as ctk
from tkinter import messagebox, ttk
import mysql.connector
from decimal import Decimal

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DB_CONFIG = {
    "host": "localhost",
    "user": "app_user",
    "password": "app_pass",
    "database": "personal_finance"
}

class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance & Recurring Payments Manager - Proiect BD")
        self.geometry("1060x680")

        self.current_user_id = 1

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            self.sidebar, text="FINANȚE\nPERSONALE",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(25, 20))

        ctk.CTkButton(self.sidebar, text="Dashboard Predictiv", command=self.show_dashboard).grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar, text="+ Tranzacție Nouă", command=self.show_add_transaction).grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Plăți Planificate (2 Luni)", command=self.show_planned_payments).grid(row=3, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Obiective Economii", command=self.show_savings_goals).grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        ctk.CTkLabel(
            self.sidebar, text="MySQL: Conectat (app_user)",
            text_color="#4caf50", font=ctk.CTkFont(size=12)
        ).grid(row=7, column=0, padx=20, pady=20)

        # --- ZONA PRINCIPALĂ ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.show_dashboard()

    def get_connection(self):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error as err:
            messagebox.showerror("Eroare Conexiune MySQL", f"Nu s-a putut conecta la baza de date:\n{err}")
            return None

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # =========================================================================
    # 1. DASHBOARD PREDICTIV
    # =========================================================================
    def show_dashboard(self):
        self.clear_main_frame()
        conn = self.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT COALESCE(SUM(a.balance * c.exchange_rate), 0) AS total_brut
            FROM accounts a
            JOIN currencies c ON a.currency_id = c.id
            WHERE a.user_id = %s
        """, (self.current_user_id,))
        sold_brut = Decimal(cursor.fetchone()["total_brut"])

        cursor.execute("""
            SELECT COALESCE(SUM(pp.amount * c.exchange_rate), 0) AS total_planificat
            FROM planned_payments pp
            JOIN accounts a ON pp.account_id = a.id
            JOIN currencies c ON a.currency_id = c.id
            WHERE a.user_id = %s
              AND pp.status = 'PLANIFICAT'
              AND pp.due_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 60 DAY)
        """, (self.current_user_id,))
        obligatii = Decimal(cursor.fetchone()["total_planificat"])

        disponibil_real = sold_brut - obligatii

        ctk.CTkLabel(
            self.main_frame, text="Situație Financiară Predictivă (Orizont 2 Luni)",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(20, 15), padx=20, anchor="w")

        cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._create_kpi_card(cards_frame, 0, "SOLD BRUT TOTAL", f"{sold_brut:.2f} RON", "#2196f3")
        self._create_kpi_card(cards_frame, 1, "OBLIGAȚII PLANIFICATE (60 ZILE)", f"- {obligatii:.2f} RON", "#ff9800")
        culoare_disp = "#4caf50" if disponibil_real >= 0 else "#f44336"
        self._create_kpi_card(cards_frame, 2, "FOND DISPONIBIL REAL", f"{disponibil_real:.2f} RON", culoare_disp)

        ctk.CTkLabel(
            self.main_frame, text="Ultimele Tranzacții Înregistrate",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(25, 10), padx=20, anchor="w")

        cols = ("ID", "Tip", "Sumă", "Cont Sursă", "Cont Destinație", "Subcategorie", "Descriere", "Data")
        tree = ttk.Treeview(self.main_frame, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=95, anchor="center")

        cursor.execute("""
            SELECT t.id, t.type, t.amount,
                   COALESCE(a_src.name, '-') AS src_name,
                   COALESCE(a_dst.name, '-') AS dst_name,
                   COALESCE(s.name, 'General') AS subcat_name,
                   COALESCE(t.description, '-') AS descr,
                   DATE_FORMAT(t.transaction_date, '%Y-%m-%d %H:%i') AS tx_date
            FROM transactions t
            LEFT JOIN accounts a_src ON t.source_account_id = a_src.id
            LEFT JOIN accounts a_dst ON t.destination_account_id = a_dst.id
            LEFT JOIN subcategories s ON t.subcategory_id = s.id
            WHERE a_src.user_id = %s OR a_dst.user_id = %s
            ORDER BY t.transaction_date DESC, t.id DESC
            LIMIT 15
        """, (self.current_user_id, self.current_user_id))

        for row in cursor.fetchall():
            tree.insert("", "end", values=(
                row["id"], row["type"], f"{row['amount']:.2f}",
                row["src_name"], row["dst_name"], row["subcat_name"], row["descr"], row["tx_date"]
            ))

        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        cursor.close()
        conn.close()

    def _create_kpi_card(self, parent, col, title, value, color):
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.grid(row=0, column=col, padx=8, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(pady=(15, 5))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color=color).pack(pady=(0, 15))

    # =========================================================================
    # 2. ADĂUGARE TRANZACȚIE
    # =========================================================================
    def show_add_transaction(self):
        self.clear_main_frame()
        conn = self.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name, balance FROM accounts WHERE user_id = %s", (self.current_user_id,))
        accounts = cursor.fetchall()

        cursor.execute("""
            SELECT s.id, CONCAT(c.name, ' -> ', s.name) AS full_name
            FROM subcategories s
            JOIN categories c ON s.category_id = c.id
            WHERE c.user_id IS NULL OR c.user_id = %s
        """, (self.current_user_id,))
        subcats = cursor.fetchall()
        cursor.close()
        conn.close()

        if not accounts:
            ctk.CTkLabel(self.main_frame, text="Nu există conturi în baza de date!", font=ctk.CTkFont(size=16)).pack(pady=40)
            return

        ctk.CTkLabel(self.main_frame, text="Înregistrare Tranzacție Nouă", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20, padx=20, anchor="w")

        form = ctk.CTkFrame(self.main_frame)
        form.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(form, text="Tip operațiune:").grid(row=0, column=0, padx=15, pady=12, sticky="w")
        tx_type_var = ctk.StringVar(value="CHELTUIALA")
        ctk.CTkOptionMenu(form, values=["CHELTUIALA", "VENIT", "TRANSFER"], variable=tx_type_var).grid(row=0, column=1, padx=15, pady=12, sticky="ew")

        acc_map = {f"{a['name']} (Sold: {a['balance']})": a['id'] for a in accounts}
        acc_names = list(acc_map.keys())

        ctk.CTkLabel(form, text="Cont Sursă (Cheltuială / Transfer):").grid(row=1, column=0, padx=15, pady=12, sticky="w")
        src_var = ctk.StringVar(value=acc_names[0])
        ctk.CTkOptionMenu(form, values=acc_names, variable=src_var).grid(row=1, column=1, padx=15, pady=12, sticky="ew")

        ctk.CTkLabel(form, text="Cont Destinație (Venit / Transfer):").grid(row=2, column=0, padx=15, pady=12, sticky="w")
        dst_var = ctk.StringVar(value=acc_names[-1])
        ctk.CTkOptionMenu(form, values=acc_names, variable=dst_var).grid(row=2, column=1, padx=15, pady=12, sticky="ew")

        sub_map = {s['full_name']: s['id'] for s in subcats} if subcats else {"Fără subcategorie": None}
        sub_names = list(sub_map.keys())
        ctk.CTkLabel(form, text="Subcategorie:").grid(row=3, column=0, padx=15, pady=12, sticky="w")
        sub_var = ctk.StringVar(value=sub_names[0])
        ctk.CTkOptionMenu(form, values=sub_names, variable=sub_var).grid(row=3, column=1, padx=15, pady=12, sticky="ew")

        ctk.CTkLabel(form, text="Sumă:").grid(row=4, column=0, padx=15, pady=12, sticky="w")
        amount_entry = ctk.CTkEntry(form, placeholder_text="ex: 150.50")
        amount_entry.grid(row=4, column=1, padx=15, pady=12, sticky="ew")

        ctk.CTkLabel(form, text="Descriere:").grid(row=5, column=0, padx=15, pady=12, sticky="w")
        desc_entry = ctk.CTkEntry(form, placeholder_text="Detalii opționale...")
        desc_entry.grid(row=5, column=1, padx=15, pady=12, sticky="ew")

        def save_tx():
            try:
                val = Decimal(amount_entry.get().strip())
                if val <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Eroare Validare", "Introdu o sumă validă mai mare ca 0.")
                return

            t_type = tx_type_var.get()
            src_id = acc_map[src_var.get()] if t_type in ("CHELTUIALA", "TRANSFER") else None
            dst_id = acc_map[dst_var.get()] if t_type in ("VENIT", "TRANSFER") else None
            sub_id = sub_map[sub_var.get()]
            desc = desc_entry.get().strip() or None

            if t_type == "TRANSFER" and src_id == dst_id:
                messagebox.showerror("Eroare Logică", "La transfer, contul sursă trebuie să fie diferit de contul destinație!")
                return

            conn_tx = self.get_connection()
            if not conn_tx:
                return
            cur = conn_tx.cursor()
            try:
                conn_tx.start_transaction()
                cur.execute("""
                    INSERT INTO transactions (source_account_id, destination_account_id, subcategory_id, type, amount, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (src_id, dst_id, sub_id, t_type, val, desc))

                if src_id:
                    cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (val, src_id))
                if dst_id:
                    cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (val, dst_id))

                conn_tx.commit()
                messagebox.showinfo("Succes", "Tranzacția a fost salvată și soldurile au fost actualizate ACID!")
                self.show_dashboard()
            except mysql.connector.Error as err:
                conn_tx.rollback()
                messagebox.showerror("Eroare Bază de Date (Rollback)", f"Operațiunea a fost anulată:\n{err}")
            finally:
                cur.close()
                conn_tx.close()

        ctk.CTkButton(self.main_frame, text="Salvează Tranzacția în MySQL", command=save_tx, height=40).pack(pady=20, padx=20, anchor="e")

    # =========================================================================
    # 3. PLĂȚI PLANIFICATE + BUTON ACHITARE ACID
    # =========================================================================
    def show_planned_payments(self):
        self.clear_main_frame()
        conn = self.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(header_frame, text="Scadențar Plăți Planificate & Recurente", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")

        cols = ("ID", "Titlu Plată", "Sumă", "Scadență", "Status", "Cont Asociat")
        tree = ttk.Treeview(self.main_frame, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=115, anchor="center")

        cursor.execute("""
            SELECT pp.id, pp.title, pp.amount, pp.due_date, pp.status, a.name AS account_name
            FROM planned_payments pp
            JOIN accounts a ON pp.account_id = a.id
            WHERE a.user_id = %s
            ORDER BY pp.due_date ASC
        """, (self.current_user_id,))

        for row in cursor.fetchall():
            tree.insert("", "end", values=(
                row["id"], row["title"], f"{row['amount']:.2f}",
                str(row["due_date"]), row["status"], row["account_name"]
            ))

        tree.pack(fill="both", expand=True, padx=20, pady=10)
        cursor.close()
        conn.close()

        def pay_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selecție lipsă", "Selectează o plată din tabel mai întâi!")
                return

            item_vals = tree.item(selected[0], "values")
            pp_id = int(item_vals[0])
            status = item_vals[4]

            if status != "PLANIFICAT":
                messagebox.showinfo("Info", f"Această plată are deja statusul '{status}'.")
                return

            conn_pay = self.get_connection()
            if not conn_pay:
                return
            cur = conn_pay.cursor(dictionary=True)
            try:
                conn_pay.start_transaction()
                cur.execute("SELECT * FROM planned_payments WHERE id = %s FOR UPDATE", (pp_id,))
                pp_row = cur.fetchone()

                # 1. Actualizare status în planned_payments
                cur.execute("UPDATE planned_payments SET status = 'ACHITAT' WHERE id = %s", (pp_id,))

                # 2. Inserare cheltuială în transactions
                cur.execute("""
                    INSERT INTO transactions (source_account_id, subcategory_id, type, amount, description)
                    VALUES (%s, %s, 'CHELTUIALA', %s, %s)
                """, (pp_row["account_id"], pp_row["subcategory_id"], pp_row["amount"], f"Plată scadentă: {pp_row['title']}"))

                # 3. Scădere sold din contul asociat
                cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (pp_row["amount"], pp_row["account_id"]))

                conn_pay.commit()
                messagebox.showinfo("Plată Efectuată", f"'{pp_row['title']}' a fost marcată ca ACHITAT, tranzacția a fost înregistrată și soldul actualizat!")
                self.show_planned_payments()
            except mysql.connector.Error as err:
                conn_pay.rollback()
                messagebox.showerror("Eroare Tranzacție", f"Operațiunea a eșuat:\n{err}")
            finally:
                cur.close()
                conn_pay.close()

        ctk.CTkButton(
            self.main_frame, text="✓ Marchează ca ACHITAT (Execută Tranzacția)",
            command=pay_selected, fg_color="#2e7d32", hover_color="#1b5e20", height=40
        ).pack(pady=(5, 20), padx=20, anchor="e")

    # =========================================================================
    # 4. OBIECTIVE DE ECONOMISIRE (savings_goals - CF6)
    # =========================================================================
    def show_savings_goals(self):
        self.clear_main_frame()
        conn = self.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        ctk.CTkLabel(self.main_frame, text="Obiective de Economisire (Savings Goals)", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 15), padx=20, anchor="w")

        cursor.execute("""
            SELECT sg.id, sg.name, sg.target_amount, sg.current_amount, sg.target_date, a.name AS account_name
            FROM savings_goals sg
            JOIN accounts a ON sg.account_id = a.id
            WHERE a.user_id = %s
        """, (self.current_user_id,))
        goals = cursor.fetchall()
        cursor.close()
        conn.close()

        if not goals:
            ctk.CTkLabel(
                self.main_frame,
                text="Nu există obiective definite în tabela savings_goals.\nAdaugă date de test în baza de date pentru a vizualiza progresul.",
                font=ctk.CTkFont(size=14), text_color="gray"
            ).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for g in goals:
            card = ctk.CTkFrame(scroll, corner_radius=8)
            card.pack(fill="x", pady=8)

            target = Decimal(g["target_amount"])
            current = Decimal(g["current_amount"])
            ratio = float(current / target) if target > 0 else 0.0
            ratio_clamped = min(max(ratio, 0.0), 1.0)
            pct = ratio * 100

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(12, 4))

            ctk.CTkLabel(top_row, text=f"{g['name']}  ({g['account_name']})", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            deadline_txt = f"Termen: {g['target_date']}" if g["target_date"] else "Fără termen limită"
            ctk.CTkLabel(top_row, text=deadline_txt, font=ctk.CTkFont(size=12), text_color="gray").pack(side="right")

            bar = ctk.CTkProgressBar(card, height=14)
            bar.set(ratio_clamped)
            bar.pack(fill="x", padx=15, pady=6)

            bot_row = ctk.CTkFrame(card, fg_color="transparent")
            bot_row.pack(fill="x", padx=15, pady=(2, 12))

            ctk.CTkLabel(bot_row, text=f"Acumulat: {current:.2f} / {target:.2f} RON ({pct:.1f}%)", font=ctk.CTkFont(size=13)).pack(side="left")

            def make_deposit_fn(goal_id=g["id"], goal_name=g["name"]):
                def deposit():
                    dialog = ctk.CTkInputDialog(text=f"Sumă de alocat către '{goal_name}' (RON):", title="Alimentare Obiectiv")
                    val_str = dialog.get_input()
                    if not val_str:
                        return
                    try:
                        amt = Decimal(val_str.strip())
                        if amt <= 0:
                            raise ValueError
                    except Exception:
                        messagebox.showerror("Eroare", "Introdu o sumă validă pozitivă.")
                        return

                    c_dep = self.get_connection()
                    if not c_dep:
                        return
                    cur_dep = c_dep.cursor()
                    try:
                        cur_dep.execute("UPDATE savings_goals SET current_amount = current_amount + %s WHERE id = %s", (amt, goal_id))
                        c_dep.commit()
                        self.show_savings_goals()
                    except mysql.connector.Error as err:
                        messagebox.showerror("Eroare MySQL", str(err))
                    finally:
                        cur_dep.close()
                        c_dep.close()
                return deposit

            ctk.CTkButton(bot_row, text="+ Alocă Fonduri", width=130, height=28, command=make_deposit_fn()).pack(side="right")

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
