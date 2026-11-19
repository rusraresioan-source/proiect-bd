import customtkinter as ctk
from tkinter import messagebox, ttk
import mysql.connector
from decimal import Decimal
from datetime import date
import calendar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DB_CONFIG = {
    "host": "localhost",
    "user": "app_user",
    "password": "app_pass",
    "database": "personal_finance"
}

BG_DARK = "#14181f"
BG_CARD = "#1e242d"
BG_SIDEBAR = "#181d25"
ACCENT_BLUE = "#2563eb"
ACCENT_HOVER = "#1d4ed8"
TEXT_MUTED = "#94a3b8"
BORDER_SUBTLE = "#2d3748"

class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finanțe Personale & Plăți Recurente — Proiect BD")
        self.geometry("1280x800")
        self.minsize(1120, 700)
        self.configure(fg_color=BG_DARK)

        self.current_user_id = 1
        self._configure_treeview_style()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=BG_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(7, weight=1)

        logo_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_box.grid(row=0, column=0, padx=22, pady=(28, 22), sticky="ew")
        ctk.CTkLabel(
            logo_box, text="FINANȚE PERSONALE",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w")
        ctk.CTkLabel(
            logo_box, text="Gestiune Predictivă & ACID",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "  Dashboard Predictiv", self.show_dashboard),
            ("add_tx", "  + Tranzacție Nouă", self.show_add_transaction),
            ("planned", "  Plăți Planificate & Recurente", self.show_planned_payments),
            ("goals", "  Obiective Economii", self.show_savings_goals),
        ]

        for idx, (key, label, cmd) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self.sidebar, text=label, command=cmd,
                height=42, corner_radius=8, anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                fg_color="transparent", text_color="#cbd5e1",
                hover_color="#263040"
            )
            btn.grid(row=idx, column=0, padx=16, pady=5, sticky="ew")
            self.nav_buttons[key] = btn

        status_card = ctk.CTkFrame(self.sidebar, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER_SUBTLE)
        status_card.grid(row=8, column=0, padx=16, pady=20, sticky="ew")
        ctk.CTkLabel(
            status_card, text="● MySQL 8.0 Conectat",
            text_color="#22c55e", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        ).pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(
            status_card, text="Cont: app_user (InnoDB 3FN)",
            text_color=TEXT_MUTED, font=ctk.CTkFont(family="Segoe UI", size=11)
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # --- ZONA PRINCIPALĂ ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=14, fg_color=BG_DARK)
        self.main_frame.grid(row=0, column=1, padx=22, pady=18, sticky="nsew")

        self.show_dashboard()

    # =========================================================================
    # EFECTE VIZUALE: Toast Notification, Count-Up KPI & Progress Bar Animat
    # =========================================================================
    def show_toast(self, message, kind="success"):
        colors = {
            "success": ("#14532d", "#22c55e"),
            "info": ("#1e3a8a", "#38bdf8"),
            "warning": ("#7c2d12", "#fb923c"),
        }
        bg, border = colors.get(kind, colors["success"])
        toast = ctk.CTkFrame(self, fg_color=bg, corner_radius=10, border_width=1, border_color=border)
        lbl = ctk.CTkLabel(
            toast, text=message,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#f8fafc"
        )
        lbl.pack(padx=18, pady=12)
        toast.place(relx=0.98, rely=0.96, anchor="se")
        toast.lift()
        self.after(3000, lambda: toast.destroy() if toast.winfo_exists() else None)

    def _animate_kpi_value(self, label_widget, target_val, prefix="", suffix=" RON", steps=18, step=1):
        if not label_widget.winfo_exists():
            return
        if step >= steps:
            label_widget.configure(text=f"{prefix}{target_val:.2f}{suffix}")
            return
        # Easing cubic out
        t = step / steps
        eased = 1 - (1 - t) ** 3
        current_val = float(target_val) * eased
        label_widget.configure(text=f"{prefix}{current_val:.2f}{suffix}")
        self.after(20, lambda: self._animate_kpi_value(label_widget, target_val, prefix, suffix, steps, step + 1))

    def _animate_progress(self, bar_widget, target_ratio, steps=20, step=1):
        if not bar_widget.winfo_exists():
            return
        if step >= steps:
            bar_widget.set(target_ratio)
            return
        t = step / steps
        eased = 1 - (1 - t) ** 3
        bar_widget.set(target_ratio * eased)
        self.after(18, lambda: self._animate_progress(bar_widget, target_ratio, steps, step + 1))

    def _configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dark.Treeview",
            background=BG_CARD,
            foreground="#e2e8f0",
            fieldbackground=BG_CARD,
            borderwidth=0,
            rowheight=31,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Dark.Treeview.Heading",
            background="#263040",
            foreground="#f8fafc",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padding=(8, 8)
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", ACCENT_BLUE)],
            foreground=[("selected", "#ffffff")]
        )
        style.map("Dark.Treeview.Heading", background=[("active", "#334155")])

    def _set_active_nav(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color=ACCENT_BLUE, text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#cbd5e1")

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
        self._set_active_nav("dashboard")
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

        cursor.execute("""
            SELECT COALESCE(SUM(sg.current_amount * c.exchange_rate), 0) AS total_economii
            FROM savings_goals sg
            JOIN accounts a ON sg.account_id = a.id
            JOIN currencies c ON a.currency_id = c.id
            WHERE a.user_id = %s
        """, (self.current_user_id,))
        economii_blocate = Decimal(cursor.fetchone()["total_economii"])

        disponibil_real = sold_brut - obligatii - economii_blocate

        # Header
        hdr = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=(4, 10))
        ctk.CTkLabel(
            hdr, text="Situație Financiară Predictivă",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w")
        ctk.CTkLabel(
            hdr, text="Analiză în timp real a lichidității pe orizontul următoarelor 60 de zile (conversie automată în RON)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        # 4 Carduri KPI cu Count-Up
        cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=4, pady=4)
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._create_kpi_card(cards_frame, 0, "SOLD BRUT TOTAL", sold_brut, "", "Total conturi active", "#38bdf8")
        self._create_kpi_card(cards_frame, 1, "OBLIGAȚII (60 ZILE)", obligatii, "- ", "Plăți planificate neachitate", "#fb923c")
        self._create_kpi_card(cards_frame, 2, "ECONOMII REZERVATE", economii_blocate, "- ", "Alocate în obiective", "#a78bfa")
        culoare_disp = "#22c55e" if disponibil_real >= 0 else "#ef4444"
        self._create_kpi_card(cards_frame, 3, "FOND DISPONIBIL REAL", disponibil_real, "", "Buget sigur de cheltuit", culoare_disp)

        # Rând mijloc: Mini-carduri conturi + Grafic Cheltuieli pe Categorii
        mid_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        mid_row.pack(fill="x", padx=4, pady=(8, 4))
        mid_row.grid_columnconfigure(0, weight=3)
        mid_row.grid_columnconfigure(1, weight=2)

        # Coloana stângă: Conturile mele
        acc_box = ctk.CTkFrame(mid_row, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_SUBTLE)
        acc_box.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(
            acc_box, text="Conturile Mele Active",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#f8fafc"
        ).pack(anchor="w", padx=16, pady=(10, 6))

        cursor.execute("""
            SELECT a.name, a.type, a.balance, c.code AS currency_code
            FROM accounts a
            JOIN currencies c ON a.currency_id = c.id
            WHERE a.user_id = %s
            ORDER BY a.id ASC
        """, (self.current_user_id,))
        for acc in cursor.fetchall():
            r_acc = ctk.CTkFrame(acc_box, fg_color="#161b22", corner_radius=8)
            r_acc.pack(fill="x", padx=14, pady=3)
            ctk.CTkLabel(r_acc, text=f"{acc['name']} ({acc['type']})", font=ctk.CTkFont(size=12), text_color="#cbd5e1").pack(side="left", padx=12, pady=6)
            ctk.CTkLabel(r_acc, text=f"{acc['balance']:.2f} {acc['currency_code']}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#38bdf8").pack(side="right", padx=12, pady=6)
        ctk.CTkFrame(acc_box, height=6, fg_color="transparent").pack()

        # Coloana dreaptă: Top Cheltuieli pe Categorii (GROUP BY)
        cat_box = ctk.CTkFrame(mid_row, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_SUBTLE)
        cat_box.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(
            cat_box, text="Distribuție Cheltuieli pe Categorii",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#f8fafc"
        ).pack(anchor="w", padx=16, pady=(10, 6))

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
        """, (self.current_user_id,))
        cat_rows = cursor.fetchall()
        max_cat = max((float(r["total_cat"]) for r in cat_rows), default=1.0)

        if not cat_rows:
            ctk.CTkLabel(cat_box, text="Nicio cheltuială înregistrată încă.", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(pady=24)
        else:
            for crow in cat_rows:
                val_c = float(crow["total_cat"])
                item_f = ctk.CTkFrame(cat_box, fg_color="transparent")
                item_f.pack(fill="x", padx=16, pady=3)
                lbl_f = ctk.CTkFrame(item_f, fg_color="transparent")
                lbl_f.pack(fill="x")
                ctk.CTkLabel(lbl_f, text=crow["cat_name"], font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1").pack(side="left")
                ctk.CTkLabel(lbl_f, text=f"{val_c:.2f} RON", font=ctk.CTkFont(size=11), text_color="#fb923c").pack(side="right")
                pbar = ctk.CTkProgressBar(item_f, height=8, corner_radius=4, progress_color="#fb923c")
                pbar.set(0)
                pbar.pack(fill="x", pady=(2, 2))
                self._animate_progress(pbar, min(val_c / max_cat, 1.0))

        # Tabel Tranzacții + Filtru
        table_card = ctk.CTkFrame(self.main_frame, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_SUBTLE)
        table_card.pack(fill="both", expand=True, padx=10, pady=(8, 6))

        top_bar = ctk.CTkFrame(table_card, fg_color="transparent")
        top_bar.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            top_bar, text="Istoric Tranzacții",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#f8fafc"
        ).pack(side="left")

        filter_type_var = ctk.StringVar(value="TOATE")
        search_var = ctk.StringVar(value="")

        cols = ("ID", "Tip", "Sumă", "Cont Sursă", "Cont Destinație", "Metodă", "Subcategorie", "Descriere", "Data")
        col_widths = {"ID": 40, "Tip": 90, "Sumă": 95, "Cont Sursă": 150, "Cont Destinație": 150, "Metodă": 120, "Subcategorie": 115, "Descriere": 140, "Data": 115}

        tree_wrap = ctk.CTkFrame(table_card, fg_color="transparent")
        tree_wrap.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", style="Dark.Treeview")
        tree.tag_configure("VENIT", foreground="#4ade80")
        tree.tag_configure("CHELTUIALA", foreground="#fb923c")
        tree.tag_configure("TRANSFER", foreground="#38bdf8")

        for col in cols:
            tree.heading(col, text=col)
            anchor = "e" if col == "Sumă" else ("w" if col in ("Cont Sursă", "Cont Destinație", "Metodă", "Subcategorie", "Descriere") else "center")
            tree.column(col, width=col_widths[col], anchor=anchor)

        def load_transactions(*_):
            for item in tree.get_children():
                tree.delete(item)
            c_tbl = self.get_connection()
            if not c_tbl:
                return
            cur_tbl = c_tbl.cursor(dictionary=True)

            t_filter = filter_type_var.get()
            q_text = f"%{search_var.get().strip()}%"

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
            params = [self.current_user_id, self.current_user_id, q_text, q_text]
            if t_filter != "TOATE":
                sql += " AND t.type = %s"
                params.append(t_filter)
            sql += " ORDER BY t.transaction_date DESC, t.id DESC LIMIT 25"

            cur_tbl.execute(sql, tuple(params))
            for r in cur_tbl.fetchall():
                prefix = "+" if r["type"] == "VENIT" else ("-" if r["type"] == "CHELTUIALA" else "")
                tree.insert("", "end", tags=(r["type"],), values=(
                    r["id"], r["type"], f"{prefix}{r['amount']:.2f} RON",
                    r["src_name"], r["dst_name"], r["pm_name"], r["subcat_name"], r["descr"], r["tx_date"]
                ))
            cur_tbl.close()
            c_tbl.close()

        search_entry = ctk.CTkEntry(top_bar, textvariable=search_var, placeholder_text="Caută descriere / categorie...", width=210, height=32)
        search_entry.pack(side="right", padx=(8, 0))
        search_entry.bind("<KeyRelease>", load_transactions)

        ctk.CTkOptionMenu(
            top_bar, values=["TOATE", "CHELTUIALA", "VENIT", "TRANSFER"],
            variable=filter_type_var, command=load_transactions, width=130, height=32
        ).pack(side="right")

        load_transactions()
        tree.pack(fill="both", expand=True)
        cursor.close()
        conn.close()

    def _create_kpi_card(self, parent, col, title, numeric_val, prefix, subtitle, color):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=BG_CARD, border_width=1, border_color=BORDER_SUBTLE)
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        accent_bar = ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=2)
        accent_bar.pack(fill="x", padx=16, pady=(10, 6))

        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=16)

        val_lbl = ctk.CTkLabel(
            card, text=f"{prefix}0.00 RON",
            font=ctk.CTkFont(family="Segoe UI", size=19, weight="bold"),
            text_color=color
        )
        val_lbl.pack(anchor="w", padx=16, pady=(2, 2))
        self._animate_kpi_value(val_lbl, numeric_val, prefix=prefix)

        ctk.CTkLabel(
            card, text=subtitle,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748b"
        ).pack(anchor="w", padx=16, pady=(0, 10))

    # =========================================================================
    # 2. ADĂUGARE TRANZACȚIE
    # =========================================================================
    def show_add_transaction(self):
        self._set_active_nav("add_tx")
        self.clear_main_frame()
        conn = self.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name, balance FROM accounts WHERE user_id = %s", (self.current_user_id,))
        accounts = cursor.fetchall()

        cursor.execute("""
            SELECT s.id, CONCAT(c.name, '  →  ', s.name) AS full_name
            FROM subcategories s
            JOIN categories c ON s.category_id = c.id
            WHERE c.user_id IS NULL OR c.user_id = %s
        """, (self.current_user_id,))
        subcats = cursor.fetchall()

        cursor.execute("SELECT id, name, masked_details FROM payment_methods WHERE user_id = %s", (self.current_user_id,))
        pay_methods = cursor.fetchall()

        cursor.close()
        conn.close()

        if not accounts:
            ctk.CTkLabel(self.main_frame, text="Nu există conturi în baza de date!", font=ctk.CTkFont(size=16)).pack(pady=40)
            return

        hdr = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(6, 16))
        ctk.CTkLabel(hdr, text="Înregistrare Tranzacție Nouă", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Operațiune atomică ACID (actualizează simultan jurnalul și soldurile conturilor)", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=TEXT_MUTED).pack(anchor="w")

        form = ctk.CTkFrame(self.main_frame, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_SUBTLE)
        form.pack(padx=12, pady=6, fill="x")
        form.grid_columnconfigure(1, weight=1)

        def add_row(r_idx, label_text, widget):
            ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#cbd5e1").grid(
                row=r_idx, column=0, padx=22, pady=12, sticky="w"
            )
            widget.grid(row=r_idx, column=1, padx=22, pady=12, sticky="ew")

        tx_type_var = ctk.StringVar(value="CHELTUIALA")
        add_row(0, "Tip operațiune:", ctk.CTkOptionMenu(form, values=["CHELTUIALA", "VENIT", "TRANSFER"], variable=tx_type_var, height=36))

        acc_map = {f"{a['name']}  (Sold: {a['balance']} RON)": a['id'] for a in accounts}
        acc_names = list(acc_map.keys())

        src_var = ctk.StringVar(value=acc_names[0])
        add_row(1, "Cont Sursă (Cheltuială / Transfer):", ctk.CTkOptionMenu(form, values=acc_names, variable=src_var, height=36))

        dst_var = ctk.StringVar(value=acc_names[-1])
        add_row(2, "Cont Destinație (Venit / Transfer):", ctk.CTkOptionMenu(form, values=acc_names, variable=dst_var, height=36))

        pm_map = {"Fără metodă specificată": None}
        for pm in pay_methods:
            label = f"{pm['name']} ({pm['masked_details']})" if pm["masked_details"] else pm["name"]
            pm_map[label] = pm["id"]
        pm_names = list(pm_map.keys())

        pm_var = ctk.StringVar(value=pm_names[1] if len(pm_names) > 1 else pm_names[0])
        add_row(3, "Metodă de Plată:", ctk.CTkOptionMenu(form, values=pm_names, variable=pm_var, height=36))

        sub_map = {s['full_name']: s['id'] for s in subcats} if subcats else {"Fără subcategorie": None}
        sub_names = list(sub_map.keys())
        sub_var = ctk.StringVar(value=sub_names[0])
        add_row(4, "Categorie & Subcategorie:", ctk.CTkOptionMenu(form, values=sub_names, variable=sub_var, height=36))

        amount_entry = ctk.CTkEntry(form, placeholder_text="ex: 150.50", height=36)
        add_row(5, "Sumă (RON):", amount_entry)

        desc_entry = ctk.CTkEntry(form, placeholder_text="Detalii opționale despre tranzacție...", height=36)
        add_row(6, "Descriere:", desc_entry)

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
            pm_id = pm_map[pm_var.get()]
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
                    INSERT INTO transactions (
                        source_account_id, destination_account_id, payment_method_id,
                        subcategory_id, type, amount, description
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (src_id, dst_id, pm_id, sub_id, t_type, val, desc))

                if src_id:
                    cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (val, src_id))
                if dst_id:
                    cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (val, dst_id))

                conn_tx.commit()
                self.show_dashboard()
                self.show_toast(f"✓ Tranzacție ({t_type}: {val:.2f} RON) salvată ACID!", "success")
            except mysql.connector.Error as err:
                conn_tx.rollback()
                messagebox.showerror("Eroare Bază de Date (Rollback)", f"Operațiunea a fost anulată:\n{err}")
            finally:
                cur.close()
                conn_tx.close()

        ctk.CTkButton(
            self.main_frame, text="✓ Salvează Tranzacția în MySQL",
            command=save_tx, height=42, corner_radius=8,
            fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(pady=18, padx=12, anchor="e")

    # =========================================================================
    # 3. PLĂȚI PLANIFICATE + REGULI DE RECURENȚĂ
    # =========================================================================
    def show_planned_payments(self):
        self._set_active_nav("planned")
        self.clear_main_frame()
        conn = self.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(6, 14))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Scadențar Plăți Planificate & Recurente", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Obligațiile viitoare blochează automat suma corespunzătoare în Fondul Disponibil Real", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=TEXT_MUTED).pack(anchor="w")

        ctk.CTkButton(
            header_frame, text="+ Regulă Recurentă Nouă",
            command=self.show_add_recurring_rule,
            fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
            height=40, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="right", pady=6)

        table_card = ctk.CTkFrame(self.main_frame, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_SUBTLE)
        table_card.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("ID", "Titlu Plată", "Sumă", "Scadență", "Status", "Frecvență", "Cont Asociat")
        col_widths = {"ID": 50, "Titlu Plată": 230, "Sumă": 110, "Scadență": 110, "Status": 110, "Frecvență": 110, "Cont Asociat": 190}

        tree_wrap = ctk.CTkFrame(table_card, fg_color="transparent")
        tree_wrap.pack(fill="both", expand=True, padx=16, pady=16)

        tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", style="Dark.Treeview")
        tree.tag_configure("ACHITAT", foreground="#4ade80")
        tree.tag_configure("PLANIFICAT", foreground="#fb923c")

        for col in cols:
            tree.heading(col, text=col)
            anchor = "w" if col in ("Titlu Plată", "Cont Asociat") else ("e" if col == "Sumă" else "center")
            tree.column(col, width=col_widths[col], anchor=anchor)

        cursor.execute("""
            SELECT pp.id, pp.title, pp.amount, pp.due_date, pp.status,
                   COALESCE(rr.frequency, 'MANUAL') AS freq, a.name AS account_name
            FROM planned_payments pp
            JOIN accounts a ON pp.account_id = a.id
            LEFT JOIN recurring_rules rr ON pp.recurring_rule_id = rr.id
            WHERE a.user_id = %s
            ORDER BY pp.due_date ASC
        """, (self.current_user_id,))

        for row in cursor.fetchall():
            tree.insert("", "end", tags=(row["status"],), values=(
                row["id"], row["title"], f"{row['amount']:.2f} RON",
                str(row["due_date"]), row["status"], row["freq"], row["account_name"]
            ))

        tree.pack(fill="both", expand=True)
        cursor.close()
        conn.close()

        def pay_selected():
            selected = tree.selection()
            if not selected:
                self.show_toast("⚠ Selectează mai întâi o plată din tabel!", "warning")
                return

            item_vals = tree.item(selected[0], "values")
            pp_id = int(item_vals[0])
            status = item_vals[4]

            if status != "PLANIFICAT":
                self.show_toast(f"ℹ Plata are deja statusul '{status}'.", "info")
                return

            conn_pay = self.get_connection()
            if not conn_pay:
                return
            cur = conn_pay.cursor(dictionary=True)
            try:
                conn_pay.start_transaction()
                cur.execute("SELECT * FROM planned_payments WHERE id = %s FOR UPDATE", (pp_id,))
                pp_row = cur.fetchone()

                cur.execute("UPDATE planned_payments SET status = 'ACHITAT' WHERE id = %s", (pp_id,))
                cur.execute("""
                    INSERT INTO transactions (source_account_id, subcategory_id, type, amount, description)
                    VALUES (%s, %s, 'CHELTUIALA', %s, %s)
                """, (pp_row["account_id"], pp_row["subcategory_id"], pp_row["amount"], f"Plată scadentă: {pp_row['title']}"))
                cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (pp_row["amount"], pp_row["account_id"]))

                conn_pay.commit()
                self.show_planned_payments()
                self.show_toast(f"✓ '{pp_row['title']}' achitată și decontată ACID!", "success")
            except mysql.connector.Error as err:
                conn_pay.rollback()
                messagebox.showerror("Eroare Tranzacție", f"Operațiunea a eșuat:\n{err}")
            finally:
                cur.close()
                conn_pay.close()

        ctk.CTkButton(
            self.main_frame, text="✓ Marchează ca ACHITAT (Execută Tranzacția ACID)",
            command=pay_selected, fg_color="#16a34a", hover_color="#15803d",
            height=42, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(pady=(12, 10), padx=12, anchor="e")

    def show_add_recurring_rule(self):
        self._set_active_nav("planned")
        self.clear_main_frame()
        conn = self.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name FROM accounts WHERE user_id = %s", (self.current_user_id,))
        accounts = cursor.fetchall()

        cursor.execute("""
            SELECT s.id, CONCAT(c.name, '  →  ', s.name) AS full_name
            FROM subcategories s
            JOIN categories c ON s.category_id = c.id
            WHERE (c.user_id IS NULL OR c.user_id = %s) AND c.is_income = FALSE
        """, (self.current_user_id,))
        subcats = cursor.fetchall()
        cursor.close()
        conn.close()

        hdr = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(6, 16))
        ctk.CTkLabel(hdr, text="Creare Regulă Recurentă", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(hdr, text="Generează automat instanțele viitoare în planned_payments pe următoarele 60 de zile", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=TEXT_MUTED).pack(anchor="w")

        form = ctk.CTkFrame(self.main_frame, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_SUBTLE)
        form.pack(padx=12, pady=6, fill="x")
        form.grid_columnconfigure(1, weight=1)

        def add_row(r_idx, label_text, widget):
            ctk.CTkLabel(form, text=label_text, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#cbd5e1").grid(
                row=r_idx, column=0, padx=22, pady=12, sticky="w"
            )
            widget.grid(row=r_idx, column=1, padx=22, pady=12, sticky="ew")

        title_entry = ctk.CTkEntry(form, placeholder_text="ex: Abonament Internet Digi", height=36)
        add_row(0, "Denumire obligație:", title_entry)

        acc_map = {a["name"]: a["id"] for a in accounts}
        acc_names = list(acc_map.keys())
        acc_var = ctk.StringVar(value=acc_names[0])
        add_row(1, "Cont asociat:", ctk.CTkOptionMenu(form, values=acc_names, variable=acc_var, height=36))

        sub_map = {s["full_name"]: s["id"] for s in subcats}
        sub_names = list(sub_map.keys())
        sub_var = ctk.StringVar(value=sub_names[0])
        add_row(2, "Subcategorie:", ctk.CTkOptionMenu(form, values=sub_names, variable=sub_var, height=36))

        freq_var = ctk.StringVar(value="LUNAR")
        add_row(3, "Frecvență:", ctk.CTkOptionMenu(form, values=["LUNAR", "TRIMESTRIAL", "ANUAL"], variable=freq_var, height=36))

        day_entry = ctk.CTkEntry(form, placeholder_text="ex: 20", height=36)
        add_row(4, "Ziua scadenței din lună (1–28):", day_entry)

        amount_entry = ctk.CTkEntry(form, placeholder_text="ex: 45.00", height=36)
        add_row(5, "Sumă lunară (RON):", amount_entry)

        def save_rule_and_generate():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Eroare", "Introdu denumirea plății recurente.")
                return
            try:
                due_day = int(day_entry.get().strip())
                if not (1 <= due_day <= 28):
                    raise ValueError
                amount = Decimal(amount_entry.get().strip())
                if amount <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Eroare Validare", "Verifică ziua scadenței (1-28) și suma (> 0).")
                return

            acc_id = acc_map[acc_var.get()]
            sub_id = sub_map[sub_var.get()]
            freq = freq_var.get()
            today = date.today()

            conn_rr = self.get_connection()
            if not conn_rr:
                return
            cur = conn_rr.cursor()
            try:
                conn_rr.start_transaction()
                cur.execute("""
                    INSERT INTO recurring_rules (user_id, frequency, due_day, start_date, is_active)
                    VALUES (%s, %s, %s, %s, TRUE)
                """, (self.current_user_id, freq, due_day, today))
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

                conn_rr.commit()
                self.show_planned_payments()
                self.show_toast(f"✓ Regulă salvată! S-au generat {generated_count} plăți în scadențar.", "success")
            except mysql.connector.Error as err:
                conn_rr.rollback()
                messagebox.showerror("Eroare MySQL", str(err))
            finally:
                cur.close()
                conn_rr.close()

        btn_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=18)
        ctk.CTkButton(btn_row, text="← Înapoi la Scadențar", fg_color="#334155", hover_color="#475569", height=40, corner_radius=8, command=self.show_planned_payments).pack(side="left")
        ctk.CTkButton(btn_row, text="✓ Salvează Regula și Generează Plățile", fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER, height=40, corner_radius=8, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), command=save_rule_and_generate).pack(side="right")

    # =========================================================================
    # 4. OBIECTIVE DE ECONOMISIRE (Bare Animate + Creare Obiectiv Nou)
    # =========================================================================
    def show_savings_goals(self):
        self._set_active_nav("goals")
        self.clear_main_frame()
        conn = self.get_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        hdr = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(6, 14))

        title_box = ctk.CTkFrame(hdr, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Obiective de Economisire", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Alocarea fondurilor execută un transfer intern ACID din contul sursă selectat către contul de economii", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=TEXT_MUTED).pack(anchor="w")

        ctk.CTkButton(
            hdr, text="+ Obiectiv Nou",
            command=self._open_new_goal_dialog,
            fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER,
            height=40, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(side="right", pady=6)

        cursor.execute("""
            SELECT sg.id, sg.title AS name, sg.target_amount, sg.current_amount, sg.deadline, a.name AS account_name
            FROM savings_goals sg
            JOIN accounts a ON sg.account_id = a.id
            WHERE a.user_id = %s
            ORDER BY sg.id ASC
        """, (self.current_user_id,))
        goals = cursor.fetchall()
        cursor.close()
        conn.close()

        if not goals:
            ctk.CTkLabel(self.main_frame, text="Nu există obiective definite în tabela savings_goals.", font=ctk.CTkFont(size=14), text_color=TEXT_MUTED).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=6, pady=(0, 12))

        for g in goals:
            card = ctk.CTkFrame(scroll, corner_radius=12, fg_color=BG_CARD, border_width=1, border_color=BORDER_SUBTLE)
            card.pack(fill="x", pady=8, padx=6)

            target = Decimal(g["target_amount"])
            current = Decimal(g["current_amount"])
            ratio = float(current / target) if target > 0 else 0.0
            ratio_clamped = min(max(ratio, 0.0), 1.0)
            pct = ratio * 100
            is_completed = current >= target

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=20, pady=(16, 6))

            ctk.CTkLabel(
                top_row, text=f"{g['name']}",
                font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
                text_color="#f8fafc"
            ).pack(side="left")

            ctk.CTkLabel(
                top_row, text=f"Cont: {g['account_name']}",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color="#38bdf8"
            ).pack(side="left", padx=(14, 0))

            deadline_txt = f"Termen limită: {g['deadline']}" if g["deadline"] else "Fără termen limită"
            ctk.CTkLabel(top_row, text=deadline_txt, font=ctk.CTkFont(family="Segoe UI", size=12), text_color=TEXT_MUTED).pack(side="right")

            bar = ctk.CTkProgressBar(card, height=14, corner_radius=7, progress_color="#22c55e" if is_completed else ACCENT_BLUE)
            bar.set(0)
            bar.pack(fill="x", padx=20, pady=8)
            self._animate_progress(bar, ratio_clamped)

            bot_row = ctk.CTkFrame(card, fg_color="transparent")
            bot_row.pack(fill="x", padx=20, pady=(4, 16))

            status_badge = "   •   ✓ OBIECTIV ÎNDEPLINIT" if is_completed else ""
            ctk.CTkLabel(
                bot_row,
                text=f"Acumulat: {current:.2f} / {target:.2f} RON  ({pct:.1f}%){status_badge}",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold" if is_completed else "normal"),
                text_color="#22c55e" if is_completed else "#cbd5e1"
            ).pack(side="left")

            def make_deposit_fn(goal_id=g["id"], goal_name=g["name"]):
                def deposit():
                    win = ctk.CTkToplevel(self)
                    win.title("Alocare Fonduri către Obiectiv")
                    win.geometry("440x270")
                    win.configure(fg_color=BG_CARD)
                    win.grab_set()

                    c_acc = self.get_connection()
                    if not c_acc:
                        return
                    cur_acc = c_acc.cursor(dictionary=True)
                    cur_acc.execute("SELECT id, name, balance FROM accounts WHERE user_id = %s", (self.current_user_id,))
                    user_accs = cur_acc.fetchall()
                    cur_acc.execute("SELECT account_id FROM savings_goals WHERE id = %s", (goal_id,))
                    dest_acc_id = cur_acc.fetchone()["account_id"]
                    cur_acc.close()
                    c_acc.close()

                    ctk.CTkLabel(win, text=f"Alocare: {goal_name}", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")).pack(pady=(18, 12))

                    acc_options = {f"{a['name']}  (Sold: {a['balance']} RON)": a["id"] for a in user_accs}
                    opt_list = list(acc_options.keys())
                    src_var = ctk.StringVar(value=opt_list[0])

                    ctk.CTkLabel(win, text="Cont sursă (de unde se transferă banii):", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w", padx=26)
                    ctk.CTkOptionMenu(win, values=opt_list, variable=src_var, width=388, height=34).pack(pady=(4, 12), padx=26)

                    ctk.CTkLabel(win, text="Sumă de alocat (RON):", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w", padx=26)
                    amt_entry = ctk.CTkEntry(win, placeholder_text="ex: 250.00", width=388, height=34)
                    amt_entry.pack(pady=(4, 18), padx=26)

                    def confirm_alloc():
                        try:
                            amt = Decimal(amt_entry.get().strip())
                            if amt <= 0:
                                raise ValueError
                        except Exception:
                            messagebox.showerror("Eroare", "Introdu o sumă validă pozitivă.", parent=win)
                            return

                        src_id = acc_options[src_var.get()]
                        c_dep = self.get_connection()
                        if not c_dep:
                            return
                        cur_dep = c_dep.cursor()
                        try:
                            c_dep.start_transaction()
                            cur_dep.execute("UPDATE savings_goals SET current_amount = current_amount + %s WHERE id = %s", (amt, goal_id))
                            if src_id != dest_acc_id:
                                cur_dep.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amt, src_id))
                                cur_dep.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amt, dest_acc_id))
                                cur_dep.execute("""
                                    INSERT INTO transactions (source_account_id, destination_account_id, type, amount, description)
                                    VALUES (%s, %s, 'TRANSFER', %s, %s)
                                """, (src_id, dest_acc_id, amt, f"Economisire: {goal_name}"))
                            c_dep.commit()
                            win.destroy()
                            self.show_savings_goals()
                            self.show_toast(f"✓ S-au alocat {amt:.2f} RON către '{goal_name}'!", "success")
                        except mysql.connector.Error as err:
                            c_dep.rollback()
                            messagebox.showerror("Eroare MySQL (Rollback)", str(err), parent=win)
                        finally:
                            cur_dep.close()
                            c_dep.close()

                    ctk.CTkButton(win, text="✓ Confirmă Alocarea", command=confirm_alloc, fg_color="#16a34a", hover_color="#15803d", height=36, width=180, font=ctk.CTkFont(weight="bold")).pack(pady=4)
                return deposit

            if is_completed:
                ctk.CTkButton(bot_row, text="✓ Finalizat", width=140, height=32, corner_radius=8, state="disabled", fg_color="#166534").pack(side="right")
            else:
                ctk.CTkButton(bot_row, text="+ Alocă Fonduri", width=140, height=32, corner_radius=8, fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER, font=ctk.CTkFont(weight="bold"), command=make_deposit_fn()).pack(side="right")

    def _open_new_goal_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Creare Obiectiv Nou de Economisire")
        win.geometry("450x350")
        win.configure(fg_color=BG_CARD)
        win.grab_set()

        c_acc = self.get_connection()
        if not c_acc:
            return
        cur_acc = c_acc.cursor(dictionary=True)
        cur_acc.execute("SELECT id, name FROM accounts WHERE user_id = %s", (self.current_user_id,))
        user_accs = cur_acc.fetchall()
        cur_acc.close()
        c_acc.close()

        ctk.CTkLabel(win, text="Obiectiv Nou de Economisire", font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold")).pack(pady=(18, 12))

        ctk.CTkLabel(win, text="Denumire obiectiv:", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w", padx=28)
        title_entry = ctk.CTkEntry(win, placeholder_text="ex: Vacanță Vară 2027", width=394, height=34)
        title_entry.pack(pady=(2, 10), padx=28)

        acc_map = {a["name"]: a["id"] for a in user_accs}
        acc_names = list(acc_map.keys())
        acc_var = ctk.StringVar(value=acc_names[-1])
        ctk.CTkLabel(win, text="Cont de economii asociat:", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w", padx=28)
        ctk.CTkOptionMenu(win, values=acc_names, variable=acc_var, width=394, height=34).pack(pady=(2, 10), padx=28)

        ctk.CTkLabel(win, text="Sumă țintă (RON):", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w", padx=28)
        target_entry = ctk.CTkEntry(win, placeholder_text="ex: 3000.00", width=394, height=34)
        target_entry.pack(pady=(2, 10), padx=28)

        ctk.CTkLabel(win, text="Termen limită (YYYY-MM-DD, opțional):", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w", padx=28)
        deadline_entry = ctk.CTkEntry(win, placeholder_text="ex: 2027-08-01", width=394, height=34)
        deadline_entry.pack(pady=(2, 16), padx=28)

        def save_goal():
            t = title_entry.get().strip()
            if not t:
                messagebox.showerror("Eroare", "Introdu denumirea obiectivului.", parent=win)
                return
            try:
                tgt = Decimal(target_entry.get().strip())
                if tgt <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Eroare", "Introdu o sumă țintă validă (> 0).", parent=win)
                return

            dl = deadline_entry.get().strip() or None
            acc_id = acc_map[acc_var.get()]

            c_new = self.get_connection()
            if not c_new:
                return
            cur_new = c_new.cursor()
            try:
                cur_new.execute("""
                    INSERT INTO savings_goals (account_id, title, target_amount, current_amount, deadline)
                    VALUES (%s, %s, %s, 0.00, %s)
                """, (acc_id, t, tgt, dl))
                c_new.commit()
                win.destroy()
                self.show_savings_goals()
                self.show_toast(f"✓ Obiectivul '{t}' a fost creat!", "success")
            except mysql.connector.Error as err:
                messagebox.showerror("Eroare MySQL", str(err), parent=win)
            finally:
                cur_new.close()
                c_new.close()

        ctk.CTkButton(win, text="✓ Salvează Obiectivul", command=save_goal, fg_color=ACCENT_BLUE, hover_color=ACCENT_HOVER, height=36, width=190, font=ctk.CTkFont(weight="bold")).pack()

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
