# Sistem de Gestiune a Finanțelor Personale, Planificare Bugetară și Acumulare a Economiilor

## 1. Domeniu și Utilitate Practică
Proiectul se încadrează în domeniul **Finanțelor Personale (Personal Finance Management)** și abordează problema lipsei de predictibilitate financiară în rândul persoanelor fizice. Aplicația oferă o evidență riguroasă a veniturilor și cheltuielilor, planificarea obligațiilor financiare curente și viitoare, precum și mecanisme automatizate de economisire.

## 2. Scopul Proiectului
Dezvoltarea unei baze de date relaționale robuste și a unei aplicații asociate care să permită utilizatorului:
- Evidența conturilor curente și a fondurilor de economii;
- Monitorizarea și achitarea plăților scadente în luna curentă;
- Planificarea și blocarea bugetară a plăților recurente pentru luna următoare;
- Distribuirea automată/manuală a unui procent sau a unei sume fixe din venitul principal către un cont dedicat de economii.

## 3. Obiective Funcționale
1. **Gestiunea Conturilor:** Administrarea contului curent principal și a conturilor de economii/obiective financiare.
2. **Urmărirea Plăților Curente:** Înregistrarea tranzacțiilor și actualizarea atomică a soldurilor la achitarea plăților.
3. **Planificare și Prognoză:** Previzionarea cheltuielilor lunii următoare pe baza recurențelor și afișarea fondului disponibil real.
4. **Reguli de Economisire:** Executarea de transferuri interne garantate tranzacțional între conturi.
5. **Raportare și Analiză:** Interogări analitice privind distribuția cheltuielilor pe categorii și evoluția economiilor.

## 4. Structura Depozitului
```text
proiect-bd/
├── README.md               # Prezentare generală a proiectului
├── CHANGELOG.md            # Jurnalul modificărilor pe etape/săptămâni
├── .gitignore              # Reguli de ignorare pentru fișiere temporare
├── docs/                   # Documentația oficială a proiectului (.docx)
│   └── diagrams/           # Diagrame conceptuale și logice (ERD)
├── db/                     # Scripturi SQL organizate pe responsabilități
│   ├── schema/             # DDL: tabele, constrângeri, indecși
│   ├── seed/               # Date inițiale de test
│   ├── views/              # View-uri pentru rapoarte și statistici
│   ├── procedures/         # Proceduri stocate și triggere
│   ├── queries/            # Min. 20 de interogări SQL
│   └── diagrams/           # Exportul schemei relaționale
├── app/                    # Codul sursă al aplicației de gestiune
└── teste/                  # Teste de integritate și validare a constrângerilor