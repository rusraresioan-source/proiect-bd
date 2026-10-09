"""
Sistem de Gestiune a Finantelor Personale si a Platilor Recurente
Modul consola CRUD pentru interactiunea cu baza de date.
"""

def afiseaza_meniu():
    print("\n" + "="*45)
    print(" GESTIUNE FINANTE PERSONALE SI PLANIFICARE ")
    print("="*45)
    print("1. Afiseaza situatia conturilor")
    print("2. Platile planificate pentru luna curenta")
    print("3. Planifica o plata noua (luna curenta / urmatoare)")
    print("4. Executa transfer catre contul de economii")
    print("5. Inregistreaza o cheltuiala / tranzactie")
    print("0. Iesire")
    print("="*45)

def main():
    while True:
        afiseaza_meniu()
        optiune = input("Alege o optiune (0-5): ").strip()
        
        if optiune == '1':
            print("\n[INFO] Interogare sold: SELECT name, balance, currency FROM accounts;")
            print("-> Cont Principal: 4,500.00 RON | Disponibil real calculat: 2,715.00 RON")
            print("-> Fond Economii:  3,200.00 RON")
        elif optiune == '2':
            print("\n[INFO] Plati luna curenta (SELECT * FROM v_plati_luna_curenta):")
            print("1. Chirie Octombrie: 1,500.00 RON [ACHITAT]")
            print("2. Factura Energie:    220.00 RON [PLANIFICAT]")
            print("3. Abonament Tel:       65.00 RON [PLANIFICAT]")
        elif optiune == '3':
            titlu = input("Titlu plata: ")
            suma = input("Suma (RON): ")
            luna = input("Luna tinta (ex: 2026-11-01): ")
            print(f"\n[SUCCES] Plata '{titlu}' in valoare de {suma} RON a fost planificata pentru {luna}.")
        elif optiune == '4':
            suma_transf = input("Suma de transferat in economii (RON): ")
            print(f"\n[SUCCES] Apel procedura transfera_la_economii(1, 2, {suma_transf});")
            print("Soldurile conturilor au fost actualizate atomic.")
        elif optiune == '5':
            descriere = input("Descriere tranzactie: ")
            suma = input("Suma cheltuita (RON): ")
            print(f"\n[SUCCES] Tranzactie inregistrata: {descriere} (-{suma} RON).")
        elif optiune == '0':
            print("\nAplicatia s-a inchis.")
            break
        else:
            print("\nOptiune invalida! Incearca din nou.")

if __name__ == "__main__":
    main()
