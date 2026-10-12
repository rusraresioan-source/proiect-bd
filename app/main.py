import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem de Gestiune a Finanțelor Personale")
        self.geometry("720x550")
        self.configure(padx=15, pady=10)

        # Stare dinamica solduri
        self.sold_principal = 4500.00
        self.sold_economii = 3200.00

        # Header: Data si Ora exacta
        self.lbl_ceas = ttk.Label(self, text="", font=("Segoe UI", 10, "bold"), foreground="#2c3e50")
        self.lbl_ceas.pack(anchor='ne', pady=(0, 10))
        self.actualizeaza_ceas()

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        # Tab 1: Situatie Conturi & Plati Curente
        tab_curent = ttk.Frame(notebook)
        notebook.add(tab_curent, text="Luna Curentă & Sold")
        
        self.lbl_sold = ttk.Label(
            tab_curent, 
            text="", 
            font=("Segoe UI", 10, "bold"),
            justify="center",
            foreground="#1a5276"
        )
        self.lbl_sold.pack(pady=10)

        ttk.Label(tab_curent, text="Plăți planificate luna curentă:", font=("Segoe UI", 9, "italic")).pack(anchor='w', pady=(5, 2))
        self.tree_plati = ttk.Treeview(tab_curent, columns=("Titlu", "Suma", "Status", "Scadenta"), show='headings', height=6)
        self.tree_plati.heading("Titlu", text="Titlu Plată")
        self.tree_plati.heading("Suma", text="Suma (RON)")
        self.tree_plati.heading("Status", text="Status")
        self.tree_plati.heading("Scadenta", text="Scadență")
        
        self.tree_plati.column("Titlu", width=220)
        self.tree_plati.column("Suma", width=100, anchor='center')
        self.tree_plati.column("Status", width=110, anchor='center')
        self.tree_plati.column("Scadenta", width=110, anchor='center')

        # Plati initiale
        self.tree_plati.insert("", "end", values=("Chirie Octombrie", "1500.00", "ACHITAT", "2026-10-15"))
        self.tree_plati.insert("", "end", values=("Factura Energie Electrică", "220.00", "PLANIFICAT", "2026-10-20"))
        self.tree_plati.insert("", "end", values=("Abonament Telefonie", "65.00", "PLANIFICAT", "2026-10-25"))
        self.tree_plati.pack(fill='x', pady=5)

        # Tab 2: Istoric Tranzactii
        tab_istoric = ttk.Frame(notebook)
        notebook.add(tab_istoric, text="Istoric Tranzacții")

        ttk.Label(tab_istoric, text="Jurnal de tranzacții executate (Extrase de cont):", font=("Segoe UI", 9, "italic")).pack(anchor='w', pady=(10, 5))
        self.tree_istoric = ttk.Treeview(tab_istoric, columns=("Data", "Tip", "Suma", "Descriere"), show='headings', height=10)
        self.tree_istoric.heading("Data", text="Data & Ora")
        self.tree_istoric.heading("Tip", text="Tip")
        self.tree_istoric.heading("Suma", text="Sumă (RON)")
        self.tree_istoric.heading("Descriere", text="Descriere")

        self.tree_istoric.column("Data", width=150, anchor='center')
        self.tree_istoric.column("Tip", width=140, anchor='center')
        self.tree_istoric.column("Suma", width=110, anchor='center')
        self.tree_istoric.column("Descriere", width=240)

        # Date initiale istoric
        self.tree_istoric.insert("", "end", values=("2026-10-01 09:00", "VENIT", "+5500.00", "Încasare salariu luna curentă"))
        self.tree_istoric.insert("", "end", values=("2026-10-02 11:30", "CHELTUIALĂ", "-1500.00", "Plată chirie conform planificare"))
        self.tree_istoric.insert("", "end", values=("2026-10-03 14:15", "TRANSFER_ECONOMII", "-500.00", "Transfer automat 10% spre fond rezervă"))
        self.tree_istoric.insert("", "end", values=("2026-10-05 18:45", "CHELTUIALĂ", "-280.00", "Cumpărături supermarket"))
        self.tree_istoric.pack(fill='both', expand=True, pady=5)

        # Tab 3: Planificare Plata Noua
        tab_plan = ttk.Frame(notebook)
        notebook.add(tab_plan, text="Planificare Plată")

        ttk.Label(tab_plan, text="Titlu Plată:").pack(anchor='w', pady=(10, 2))
        self.entry_titlu = ttk.Entry(tab_plan, width=40)
        self.entry_titlu.pack(anchor='w')

        ttk.Label(tab_plan, text="Suma (RON):").pack(anchor='w', pady=(10, 2))
        self.entry_suma = ttk.Entry(tab_plan, width=20)
        self.entry_suma.pack(anchor='w')

        ttk.Label(tab_plan, text="Luna Scadentă (ex: 2026-11-01):").pack(anchor='w', pady=(10, 2))
        self.entry_luna = ttk.Entry(tab_plan, width=20)
        self.entry_luna.pack(anchor='w')

        btn_adauga = ttk.Button(tab_plan, text="Salvează Plata Planificată", command=self.adauga_plata)
        btn_adauga.pack(anchor='w', pady=15)

        # Tab 4: Operatiuni & Transfer Economii
        tab_operatiuni = ttk.Frame(notebook)
        notebook.add(tab_operatiuni, text="Înregistrare Cheltuială / Transfer")

        ttk.Label(tab_operatiuni, text="1. Transfer în Contul de Economii", font=("Segoe UI", 10, "bold")).pack(anchor='w', pady=(10, 2))
        ttk.Label(tab_operatiuni, text="Suma transfer (RON):").pack(anchor='w')
        self.entry_transf = ttk.Entry(tab_operatiuni, width=20)
        self.entry_transf.pack(anchor='w', pady=3)
        btn_transfer = ttk.Button(tab_operatiuni, text="Execută Transfer Atomic", command=self.executa_transfer)
        btn_transfer.pack(anchor='w', pady=(2, 15))

        ttk.Label(tab_operatiuni, text="2. Adaugă o Cheltuială Nouă", font=("Segoe UI", 10, "bold")).pack(anchor='w', pady=(5, 2))
        ttk.Label(tab_operatiuni, text="Descriere cheltuială:").pack(anchor='w')
        self.entry_desc_ch = ttk.Entry(tab_operatiuni, width=40)
        self.entry_desc_ch.pack(anchor='w', pady=3)
        ttk.Label(tab_operatiuni, text="Suma cheltuită (RON):").pack(anchor='w')
        self.entry_suma_ch = ttk.Entry(tab_operatiuni, width=20)
        self.entry_suma_ch.pack(anchor='w', pady=3)
        btn_cheltuiala = ttk.Button(tab_operatiuni, text="Înregistrează Cheltuială", command=self.adauga_cheltuiala)
        btn_cheltuiala.pack(anchor='w', pady=5)

        # Afisare initiala a balantei
        self.actualizeaza_balanta()

    def actualizeaza_ceas(self):
        acum = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.lbl_ceas.config(text=f"Data & Ora curentă: {acum}")
        self.after(1000, self.actualizeaza_ceas)

    def calculeaza_plati_blocate(self):
        total = 0.0
        for item in self.tree_plati.get_children():
            valori = self.tree_plati.item(item, "values")
            if len(valori) >= 3 and valori[2] == "PLANIFICAT":
                try:
                    total += float(valori[1])
                except ValueError:
                    pass
        return total

    def actualizeaza_balanta(self):
        plati_blocate = self.calculeaza_plati_blocate()
        disponibil_real = self.sold_principal - plati_blocate
        text = (
            f"Cont Principal: {self.sold_principal:,.2f} RON  |  Fond Economii: {self.sold_economii:,.2f} RON\n"
            f"Plăți blocate: {plati_blocate:,.2f} RON  ➔  Disponibil real: {disponibil_real:,.2f} RON"
        )
        self.lbl_sold.config(text=text)

    def adauga_plata(self):
        t = self.entry_titlu.get().strip()
        s = self.entry_suma.get().strip()
        l = self.entry_luna.get().strip()
        if not t or not s:
            messagebox.showwarning("Atenție", "Te rugăm să completezi cel puțin titlul și suma!")
            return
        try:
            val_s = float(s)
            if val_s <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Eroare", "Suma trebuie să fie un număr pozitiv!")
            return

        self.tree_plati.insert("", "end", values=(t, f"{val_s:.2f}", "PLANIFICAT", l if l else "-"))
        self.actualizeaza_balanta()
        messagebox.showinfo("Succes", f"Plata '{t}' ({val_s:.2f} RON) a fost planificată!\nDisponibilul real a fost recalculat.")
        self.entry_titlu.delete(0, 'end')
        self.entry_suma.delete(0, 'end')
        self.entry_luna.delete(0, 'end')

    def executa_transfer(self):
        s = self.entry_transf.get().strip()
        if not s:
            messagebox.showwarning("Atenție", "Introdu suma pentru transfer!")
            return
        try:
            val_s = float(s)
            if val_s <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Eroare", "Suma de transfer trebuie să fie un număr pozitiv!")
            return

        # Constrangere: fonduri suficiente
        if val_s > self.sold_principal:
            messagebox.showerror("Fonduri Insuficiente", f"Soldul contului principal ({self.sold_principal:.2f} RON) este insuficient pentru a transfera {val_s:.2f} RON!")
            return

        # Actualizare solduri (atomic)
        self.sold_principal -= val_s
        self.sold_economii += val_s
        self.actualizeaza_balanta()

        acum = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.tree_istoric.insert("", 0, values=(acum, "TRANSFER_ECONOMII", f"-{val_s:.2f}", "Transfer spre fondul de economii"))
        messagebox.showinfo("Succes", f"Transfer de {val_s:.2f} RON realizat cu succes!\nSoldurile au fost actualizate.")
        self.entry_transf.delete(0, 'end')

    def adauga_cheltuiala(self):
        desc = self.entry_desc_ch.get().strip()
        s = self.entry_suma_ch.get().strip()
        if not desc or not s:
            messagebox.showwarning("Atenție", "Completează descrierea și suma!")
            return
        try:
            val_s = float(s)
            if val_s <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Eroare", "Suma cheltuită trebuie să fie un număr pozitiv!")
            return

        if val_s > self.sold_principal:
            messagebox.showerror("Fonduri Insuficiente", f"Soldul contului principal ({self.sold_principal:.2f} RON) nu acoperă cheltuiala de {val_s:.2f} RON!")
            return

        self.sold_principal -= val_s
        self.actualizeaza_balanta()

        acum = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.tree_istoric.insert("", 0, values=(acum, "CHELTUIALĂ", f"-{val_s:.2f}", desc))
        messagebox.showinfo("Succes", f"Cheltuiala '{desc}' de {val_s:.2f} RON a fost salvată!\nSoldul principal a scăzut corespunzător.")
        self.entry_desc_ch.delete(0, 'end')
        self.entry_suma_ch.delete(0, 'end')

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
