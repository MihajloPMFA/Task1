# Kako od ovih fajlova dobiti `.erwin` model (ERwin Data Modeler r7.3.12)

## Zasto skript, a ne gotov `.erwin` fajl

`.erwin` nije tekstualni format. To je zatvoren binarni kontejner (zaglavlje `GDM`,
dva serijalizovana toka objekata, oko 1.640 razlicitih internih identifikatora
svojstava i GUID-ovi kao identitet svakog objekta) — u vasem primeru
`TV_stanica_v7.erwin` to je 282 KB i ~275.000 tokena. CA nije objavio specifikaciju,
a ovde nema instalacije ERwin-a da se rezultat proveri. Fajl koji bih „pogodio"
najverovatnije se ne bi otvorio, a takav fajl je gori nego nikakav.

Zato je model isporucen kao **DDL skript koji ERwin r7.3 sam ucitava** preko
reverznog inzenjeringa. To je podrzan, dokumentovan put: ERwin iz skripta sam
napravi tabele, kolone, primarne i strane kljuceve i nacrta dijagram, a vi ga
zatim snimite kao `.erwin`. Rezultat je isti model, samo nastao kroz ERwin.

## Fajlovi

| Fajl | Sta je |
|------|--------|
| `ER_TV_stanica.sql` | glavni skript — 69 tabela, 405 kolona, 84 strana kljuca, sa komentarima koji za svaku kolonu kazu iz kog PMOV elementa je nastala |
| `ER_TV_stanica_bez_komentara.sql` | isti skript bez ijednog komentara — rezerva, ako parser zapne na `/* */` |
| `ER_mapiranje_PMOV.md` | preslikavanje PMOV → sema: entitet po entitet, veza po veza, tabela po tabela |
| `ER_TV_stanica_dijagram.vsdx` | gotov kompaktan ER dijagram (Visio), 25,4 × 14,2 in, sve na jednoj strani |
| `ER_TV_stanica_dijagram.png` / `.pdf` | isti dijagram za gledanje i stampu bez Visio-a |

---

## 1. Reverzni inzenjering

1. Otvorite ERwin Data Modeler r7.3.
2. **Tools → Reverse Engineer…**
3. *New Model Type*: **Logical/Physical**.
   *Target Database*: **ODBC/Generic** (ili **SQL Server 2008**, ako vam vise odgovara —
   skript koristi samo `CHAR`, `VARCHAR`, `INTEGER`, `DECIMAL`, `DATE`, `TIME`).
   → **Next**
4. *Reverse Engineer From*: **Script File** → **Browse** → izaberite `ER_TV_stanica.sql`.
   → **Next**
5. *Items / Option Set* — ukljucite: **Tables**, **Columns**, **Primary Keys**,
   **Foreign Keys (Relationships)**, **Indexes**.
   U grupi **Infer** ostavite **Primary Keys: Off** i **Relations: Off** — skript vec
   sadrzi eksplicitne `PRIMARY KEY` i `FOREIGN KEY`, pa bi „infer" napravio duplikate.
6. *Case Conversion of Logical Names*: **Mixed Case**
   *Case Conversion of Physical Names*: **As Is**
   (opciono „Replace underscore with space" za logicka imena, ako zelite
   `Sifra Jedinice` umesto `SIFRA_JEDINICE`)
   → **Next → Finish**

Posle toga u *Model Explorer*-u treba da stoji **69 tabela**. Ako ih je manje,
skript nije procitan do kraja — probajte `ER_TV_stanica_bez_komentara.sql`.

## 2. Razmestaj dijagrama

**Skript je namerno poredjan po tematskim celinama** (`-- CELINA: ...` u komentarisanoj
verziji). ERwin postavlja tabele redom kojim ih cita, pa vec pocetni raspored dolazi
grupisan - povezane tabele su jedna do druge umesto razbacane po celom platnu.

### Kako smanjiti kutije i tekst

Ovo su podesavanja samog ERwin-a; skript na njih ne moze da utice. Nazivi menija su iz
r7.x - ako se kod tebe zovu malo drugacije, sve ovo stoji i na **desni klik na prazan
deo dijagrama**.

| Cilj | Gde |
|------|-----|
| manje kutije | **Format → Table Display** (u logickom modelu *Entity Display*) → `Primary Key` umesto `Column`; kutija se svede na ime + kljuc. `Column` vraca pun spisak. |
| sitniji tekst | oznaci sve (`Ctrl+A`) → **Format → Font**… → 6–7 pt |
| bez tipova podataka | **Format → Table Display → Datatype** iskljuciti |
| gusci raspored | **Format → Layout → Layout Settings…** → smanji *node spacing*, pa **Format → Layout → Auto Layout** |
| manje linija odjednom | **Model → Subject Areas** (tabela ispod) i **Model → Stored Displays** za vise sacuvanih pogleda |
| sve na ekran | **View → Zoom → Fit to Window** |

Najveci efekat ima kombinacija: *Subject Areas* + `Primary Key` prikaz + font 6 pt.
Na 69 tabela je jedan dijagram sa svim kolonama uvek velik - zato je uz skript
prilozen i gotov dijagram (`ER_TV_stanica_dijagram.vsdx` / `.png` / `.pdf`) koji
sve to drzi na 25,4 × 14,2 inca.

Odmah po ucitavanju sve tabele su nagomilane. **Format → Layout → Auto Layout**
(ili dugme *Layout* na traci) ih razvuce. Za citljivost od 69 tabela vredi napraviti
*Subject Area*-e (**Model → Subject Areas → New**), po istim celinama po kojima je
radjen i PMOV:

| Subject Area | Tabele |
|--------------|--------|
| Organizacija i kadrovi | `ORGANIZACIONA_JEDINICA`, `ZAPOSLENI`, `UREDNIK`, `NOVINAR_REPORTER`, `TEHNICKO_OSOBLJE`, `REFERENT`, `SERVISERI` |
| Oprema | `OPREMA`, `SNIMATELJSKA_OPREMA`, `STUDIJSKA_I_EMISIONA_OPREMA`, `AUDIO_OPREMA`, `SVETLOSNA_OPREMA`, `ZADUZENJE_OPREME`, `SERVISIRANJE_OPREME` |
| Produkcija | `PROJEKAT_PRODUKCIJE`, `AKTIVNOST_PRODUKCIJE`, `TROSAK_PRODUKCIJE`, `ANGAZOVANJE_NA_AKTIVNOSTI`, `REZERVACIJA_OPREME`, `SIROVI_SNIMAK`, `GRAFICKI_I_MUZICKI_ELEMENT` |
| Program i emitovanje | `PROGRAMSKA_SEMA`, `PROGRAMSKA_CELINA`, `TERMIN_EMITOVANJA`, `EMISIJA`, `MEDIJSKI_SADRZAJ`, `PRODUCIRANI_SADRZAJ`, `NABAVLJENI_SADRZAJ`, `REKLAMNI_SADRZAJ`, `ZAPIS_O_EMITOVANJU`, `MONTAZA_SNIMKA`, `UGRADNJA_ELEMENTA`, `SADRZAJ_EMISIJE`, `PRAVO_KORISCENJA`, `POKRIVENOST_PRAVOM`, `POVRATNA_INFO_GLEDALACA`, `MERENJE_GLEDANOSTI`, `MERENJE_EMISIJE` |
| Marketing i prodaja | `CENOVNIK_REKL_TERMINA`, `REKLAMNI_BLOK`, `EMITOVANJE_REKLAME`, `KLIJENT`, `OGLASIVAC`, `KUPAC_SADRZAJA`, `UGOVOR`, `STAVKA_UGOVORA`, `UGOVOR_O_OGLASAVANJU`, `UGOVOR_O_PRODAJI_TV_SADRZAJA`, `UGOVOR_O_NABAVCI`, `USTUPANJE_SADRZAJA` |
| Nabavka | `PLAN_NABAVKE`, `ZAHTEV_ZA_NABAVKU`, `STAVKA_PLANA_NABAVKE`, `DOBAVLJAC`, `DOBAVLJAC_TV_SADRZAJA`, `DOBAVLJAC_OPREME_I_MATERIJALA`, `PONUDA_DOBAVLJACA`, `PONUDJENA_STAVKA`, `KRITERIJUM_VREDNOVANJA`, `OCENA_PONUDE`, `NARUDZBENICA`, `STAVKA_NARUDZBENICE`, `PRIJEMNICA`, `PRIJEM_STAVKE`, `REKLAMACIJA`, `REKLAMIRANA_STAVKA` |
| Finansije | `FAKTURA`, `STAVKA_FAKTURE`, `NALOG_ZA_PLACANJE` |

## 3. Specijalizacije (podtipovi)

Reverzni inzenjering iz DDL-a **ne moze** da prepozna specijalizaciju — u SQL-u ona
i ne postoji. Svih 7 hijerarhija dodje kao obicne identifikujuce veze 1:1
(primarni kljuc podtipa = strani kljuc ka nadtipu), sto je semanticki ispravno i
potpuno upotrebljivo. U vasem primeru `TV_stanica_v7.erwin` podtipovi su takodje
zasebne tabele (`REFERENT_NABAVKE`, `STUDIJSKA_OPREMA`, …).

Ako zelite da se u dijagramu vidi i ERwin-ov simbol podtipa (polukrug):

1. Obrisite vezu koju je RE napravio izmedju nadtipa i podtipa.
2. Na paleti izaberite alat **Subtype Relationship**.
3. Kliknite na nadtip, pa na podtip — ERwin ce nacrtati simbol podtipa.
4. Ostale podtipove istog nadtipa prikacite na isti simbol.
5. U *Subtype Relationship Editor*-u podesite **Complete / Incomplete** i
   **Inclusive / Exclusive**.

Sedam hijerarhija:

| Nadtip | Podtipovi |
|--------|-----------|
| `ZAPOSLENI` | `UREDNIK`, `NOVINAR_REPORTER`, `TEHNICKO_OSOBLJE`, `REFERENT`, `SERVISERI` |
| `OPREMA` | `SNIMATELJSKA_OPREMA`, `STUDIJSKA_I_EMISIONA_OPREMA` |
| `STUDIJSKA_I_EMISIONA_OPREMA` | `AUDIO_OPREMA`, `SVETLOSNA_OPREMA` |
| `MEDIJSKI_SADRZAJ` | `PRODUCIRANI_SADRZAJ`, `NABAVLJENI_SADRZAJ`, `REKLAMNI_SADRZAJ` |
| `UGOVOR` | `UGOVOR_O_NABAVCI`, `UGOVOR_O_OGLASAVANJU`, `UGOVOR_O_PRODAJI_TV_SADRZAJA` |
| `KLIJENT` | `OGLASIVAC`, `KUPAC_SADRZAJA` |
| `DOBAVLJAC` | `DOBAVLJAC_TV_SADRZAJA`, `DOBAVLJAC_OPREME_I_MATERIJALA` |

## 4. Imena veza

ERwin posle RE imenuje veze `R/1`, `R/2`, … (isto kao u vasem primeru). Ako zelite
da nose nazive iz PMOV-a, dvoklik na vezu → *Relationship Editor* → polje
**Verb Phrase**. Tabela „PMOV veza → realizacija" u `ER_mapiranje_PMOV.md` daje
za svaku vezu tacno koji je strani kljuc nosi, pa je preimenovanje mehanicko.

## 5. Snimanje

**File → Save As…** → tip **ERwin File (*.erwin)** → ime npr. `TV_stanica_ER.erwin`.

---

## Napomene o tipovima

* `DATE` i `TIME` su odvojeni gde PMOV razlikuje datum od vremena
  (`TERMIN_EMITOVANJA.DATUM` / `VREME_POCETKA`). Ako vas ciljni dijalekt ne poznaje
  `TIME`, u RE cete ga dobiti kao podrazumevani tip — promenite ga rucno ili
  izaberite ODBC/Generic kao target.
* `TRAJANJE` je svuda `INTEGER` (sekunde odnosno minuti, pise u komentaru kolone),
  a ne `TIME`, jer u PMOV-u to je duzina a ne trenutak.
* **Rezervisane reci.** ERwin-ov parser skripta odbija kolonu koja se zove kao SQL
  kljucna rec — cela `CREATE TABLE` naredba tada padne, a za njom i svi strani
  kljucevi koji pokazuju na tu tabelu (`RES-1: Syntax error` pa `REP-39: ... Failed.
  Unable to find Table ...`). Zato su tri kolone preimenovane:

  | PMOV atribut | Tabela | Kolona u semi |
  |---|---|---|
  | FORMAT | `GRAFICKI_I_MUZICKI_ELEMENT` | `FORMAT_ELEMENTA` |
  | MODEL | `OPREMA` | `MODEL_OPREME` |
  | SHARE | `MERENJE_GLEDANOSTI` | `SHARE_UDEO` |

  Skript se sada proverava prema uniji rezervisanih reci ANSI SQL-92/99/2003,
  SQL Server-a, Oracle-a, DB2 i ODBC-a (`er/generator/reserved.py`) — nijedno ime
  tabele ni kolone se ne poklapa ni sa jednom.

* Izvedeni atributi (`BROJ_ZAPOSLENIH`, `ZAKUPLJENO_SEKUNDI`, `ISKORISCENOST`,
  `UKUPNA_VREDNOST`, `OSNOVICA`, `IZNOS_PDV`, `IZNOS_ZA_PLACANJE`,
  `VREDNOST_STAVKE`, `UKUPAN_IZNOS`, `UKUPNO_BODOVA`, `OCENA_DOBAVLJACA`,
  `ISKORISCENO_EMITOVANJA`, `SLOBODNO_SEKUNDI`) su zadrzani kao kolone i oznaceni
  komentarom. U fizickoj bazi bi bili racunati (view ili `COMPUTED` kolona) —
  za ER dijagram je uobicajeno da se prikazu.
