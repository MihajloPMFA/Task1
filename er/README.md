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
| [`ER_TV_stanica_dijagram.vsdx`](ER_TV_stanica_dijagram.vsdx) | kompaktan ER dijagram (Visio): 69 tabela na 25,4 × 14,2 in, grupisano po celinama |
| `ER_TV_stanica_dijagram.png` / `.pdf` | isti dijagram za gledanje i stampu bez Visio-a |
| `generator/` | `schema.py` (sema), `emit.py` (provera + DDL), `docs.py` (dokumentacija), `erlayout.py` + `route.py` + `erdiagram.py` (dijagram), `check_er.py` (merenje kvaliteta crteza) |

## Brojke

| | |
|---|---|
| PMOV entiteta | 55 (9 slabih) → 55 tabela |
| PMOV specijalizacija | 7 → 20 tabela podtipova |
| PMOV veza 1:N | 31 → strani kljuc |
| PMOV veza N:M | 14 → asocijativna tabela |
| PMOV identifikujucih veza | 6 → kljuc vlasnika u primarnom kljucu slabog entiteta |
| **ukupno tabela** | **69** |

## Dijagram

Skript je poredjan po tematskim celinama, pa ERwin vec pri ucitavanju postavi povezane
tabele jednu do druge. Uz njega ide i gotov, kompaktno rasporedjen dijagram.

Oznake na crtezu (bez legende, da ne zauzima mesto):

* **puna linija** = identifikujuca veza (strani kljuc je deo primarnog kljuca deteta);
* **isprekidana linija** = neidentifikujuca veza;
* **puna tackica** = strana sa "vise" (dete);
* vodoravna crta u kutiji deli primarni kljuc od ostalih kolona; `(FK)` oznacava
  migrirani strani kljuc — ista konvencija kao u ERwin-u (IDEF1X).

Kako je dobijen: raspored celina i tabela biran je minimizacijom ukupne duzine veza
(simulirano kaljenje, 4 pokretanja), veze su rutirane A* algoritmom po mrezi u kojoj su
kutije prepreke, sa kaznom za skretanje i za vec zauzete celije.

| Mera | Vrednost |
|---|---|
| strana | 25,4 × 14,2 in (jedna strana) |
| segmenata koji prolaze kroz kutiju | **0** |
| parova linija koje se poklapaju | **1** (0,10 in ukupno) |
| ukrstanja linija | **20** na 84 veze |
| ukupna duzina veza | 217 in |

## Provere koje su odradjene

* svih 69 `CREATE TABLE` naredbi prihvata pravi SQL parser (SQLite);
* svih 84 stranih kljuceva nezavisno reparsirano iz gotovog `.sql` fajla —
  svaka kolona postoji, svaki FK gadja pun primarni kljuc roditelja, arnost se poklapa;
* nijedno ime tabele ni kolone nije rezervisana SQL rec (provereno prema uniji
  lista ANSI SQL-92/99/2003, SQL Server, Oracle, DB2, ODBC);
* nema izolovanih tabela;
* nema ciklusa obaveznih (NOT NULL) stranih kljuceva — sema se moze napuniti podacima
  (topoloski poredak pokriva svih 69 tabela);
* pokrivenost: svaki od 55 entiteta i svaka od 45 veza iz vaseg PMOV-a ima realizaciju;
* dijagram je nezavisno procitan iz gotovog `.vsdx` fajla: **69/69 imena tabela,
  405/405 kolona i 84/84 veze** su na crtezu — nista nije izostavljeno.

## Jedina dopuna u odnosu na vas PMOV

Vraceno je **sest identifikujucih veza** (`SASTOJI SE OD`, `SADRZI CELINE`,
`REALIZOVAN`, `SADRZI STAVKE PLANA`, `SADRZI STAVKE NARUDZBINE`,
`SADRZI STAVKE FAKTURE`) koje u `PMOV_TV_stanica_2_1_1.vsdx` vise ne postoje.
Bez njih pet slabih entiteta nema vlasnika i ne moze da ima ispravan primarni kljuc,
a `STAVKA FAKTURE` je potpuno odvojena od modela. Detalji u odeljku 6 fajla
`ER_mapiranje_PMOV.md`.
