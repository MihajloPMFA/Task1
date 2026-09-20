# ER model TV stanice — za ERwin Data Modeler r7.3.12

Relaciona sema izvedena **iskljucivo** iz PMOV dijagrama `PMOV_TV_stanica_2_1_1.vsdx`.
Primer `TV_stanica_v7.erwin` koriscen je samo da se preuzme nacin imenovanja
(velika slova, podvlaka, prefiksi `ID_`/`BROJ_`/`DATUM_`, tipovi `CHAR(18)`,
`INTEGER`, `DATE`) i konvencija da su podtipovi zasebne tabele. Nijedan entitet,
atribut ni veza iz primera nisu preuzeti.

| Fajl | Sadrzaj |
|------|---------|
| [`UPUTSTVO_ERwin.md`](UPUTSTVO_ERwin.md) | **pocnite odavde** — korak po korak kako se skript uveze u ERwin i snimi kao `.erwin` |
| [`ER_TV_stanica.sql`](ER_TV_stanica.sql) | DDL: 69 tabela, 405 kolona, 84 strana kljuca, sa komentarom porekla za svaku kolonu |
| [`ER_TV_stanica_bez_komentara.sql`](ER_TV_stanica_bez_komentara.sql) | isti skript bez komentara (rezervna varijanta) |
| [`ER_mapiranje_PMOV.md`](ER_mapiranje_PMOV.md) | preslikavanje PMOV → sema: 55 entiteta, 7 specijalizacija, 51 veza, struktura svake tabele |
| `generator/` | `schema.py` (definicija seme), `emit.py` (provera + DDL), `docs.py` (dokumentacija) |

## Brojke

| | |
|---|---|
| PMOV entiteta | 55 (9 slabih) → 55 tabela |
| PMOV specijalizacija | 7 → 20 tabela podtipova |
| PMOV veza 1:N | 31 → strani kljuc |
| PMOV veza N:M | 14 → asocijativna tabela |
| PMOV identifikujucih veza | 6 → kljuc vlasnika u primarnom kljucu slabog entiteta |
| **ukupno tabela** | **69** |

## Provere koje su odradjene

* svih 69 `CREATE TABLE` naredbi prihvata pravi SQL parser (SQLite);
* svih 84 stranih kljuceva nezavisno reparsirano iz gotovog `.sql` fajla —
  svaka kolona postoji, svaki FK gadja pun primarni kljuc roditelja, arnost se poklapa;
* nijedno ime tabele ni kolone nije rezervisana SQL rec (provereno prema uniji
  lista ANSI SQL-92/99/2003, SQL Server, Oracle, DB2, ODBC);
* nema izolovanih tabela;
* nema ciklusa obaveznih (NOT NULL) stranih kljuceva — sema se moze napuniti podacima
  (topoloski poredak pokriva svih 69 tabela);
* pokrivenost: svaki od 55 entiteta i svaka od 45 veza iz vaseg PMOV-a ima realizaciju.

## Jedina dopuna u odnosu na vas PMOV

Vraceno je **sest identifikujucih veza** (`SASTOJI SE OD`, `SADRZI CELINE`,
`REALIZOVAN`, `SADRZI STAVKE PLANA`, `SADRZI STAVKE NARUDZBINE`,
`SADRZI STAVKE FAKTURE`) koje u `PMOV_TV_stanica_2_1_1.vsdx` vise ne postoje.
Bez njih pet slabih entiteta nema vlasnika i ne moze da ima ispravan primarni kljuc,
a `STAVKA FAKTURE` je potpuno odvojena od modela. Detalji u odeljku 6 fajla
`ER_mapiranje_PMOV.md`.
