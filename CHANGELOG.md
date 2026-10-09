# Jurnalul Modificarilor (Changelog)

Toate etapele de dezvoltare ale proiectului conform calendarului universitar.

## [v0.1-analiza] - Saptamanile 1 - 4
- Initializare depozit Git cu structura de directoare obligatorie.
- Redactare README.md: titlu, descriere domeniu, scop si obiective.
- Documentatie Word initiala: pagina de titlu, scop si analiza entitatilor.
- Modelare conceptuala si diagrama ERD Mermaid (`docs/diagrams/er.mmd`).
- Export vizual al schemei (`docs/diagrams/schema.png`) si integrare in Word.

## [v0.2-proiectare] - Saptamanile 5 - 8
- Structura DDL tabele fizice (`db/schema/01_create_tables.sql`).
- Constrangeri de integritate referentiala si verificare (`db/schema/02_constraints.sql`).
- Creare indecsi de performanta (`db/schema/03_indexes.sql`).
- Dictionar de date complet in documentatia Word pentru toate cele 6 tabele.
- Populare cu date de test coerente (`db/seed/01_insert_date.sql`).
- Script de validare a constrangerilor (`teste/teste_constrangeri.sql`).

## [v0.3-implementare] - Saptamanile 9 - 14
- View-uri SQL analitice pentru plati curente si economii (`db/views/`).
- Procedura stocata tranzactionala de transfer economii (`db/procedures/`).
- Set de 20 de interogari SQL analitice, join-uri si functii analitice (`db/queries/`).
- Aplicatie consola pentru operatiuni de tip CRUD (`app/main.py`).
