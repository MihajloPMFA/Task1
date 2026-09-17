# PMOV – trasabilnost prema DFD i IDEF0 modelu

Dijagram: `PMOV_TV_stanica.vsdx` (Microsoft Visio 2013+).
Izvori: `DFD_16_09_2026__v12.bp1`, `IDEF0_16_09_2026__v11.bp1` (BPwin).

U DFD modelu je prepoznato: 88 procesa, 78 skladišta podataka, 8 eksternih
entiteta i 647 tokova podataka; u IDEF0 modelu 90 aktivnosti i 554 strelice
(ulazi, izlazi, upravljanja i mehanizmi). PMOV je izveden tako što su
skladišta podataka i eksterni entiteti preslikani u tipove objekata, a tokovi
podataka i mehanizmi u atribute i veze.

## 1. Tipovi objekata (entiteti)

| # | Tip objekta | Vrsta | Br. atributa | Izvor u DFD / IDEF0 |
|---|---|---|---|---|
| 1 | **ORGANIZACIONA JEDINICA** | jaki entitet | 6 | DFD: Organizaciona sema i sistematizacija; IDEF0: Hijerarhijska struktura TV stanice |
| 2 | **ZAPOSLENI** | jaki entitet | 8 | DFD: Zaposleni, Dokumentacija o zaposlenima; IDEF0: Podaci o zaposlenom |
| 3 | **UREDNIK** | podtip | 2 | IDEF0: Urednik, Glavni urednik |
| 4 | **NOVINAR / REPORTER** | podtip | 2 | IDEF0: Novinari, Reporter |
| 5 | **SNIMATELJ** | podtip | 2 | IDEF0: Snimatelji, Audio-rasvetni tehnicar |
| 6 | **REFERENT** | podtip | 2 | IDEF0: Referent za nabavku, Referent za oglasavanje |
| 7 | **OPREMA** | jaki entitet | 8 | DFD: Oprema, Registar opreme; IDEF0: Status opreme, Hardver i oprema |
| 8 | **SNIMATELJSKA OPREMA** | podtip | 2 | IDEF0: Snimateljska oprema |
| 9 | **STUDIJSKA I EMISIONA OPREMA** | podtip | 2 | IDEF0: TV studio i kontrolna soba |
| 10 | **PROJEKAT PRODUKCIJE** | jaki entitet | 8 | DFD: Projekti produkcije, Arhiva planova produkcije; IDEF0: Plan/Budzet produkcije |
| 11 | **AKTIVNOST PRODUKCIJE** | slab entitet | 8 | IDEF0: DEFINISANJE AKTIVNOSTI PROJEKTA; DFD: Lista aktivnosti sa resursima |
| 12 | **TROŠAK PRODUKCIJE** | slab entitet | 6 | DFD: Troskovi produkcije, Evidentiran trosak produkcije |
| 13 | **SIROVI SNIMAK** | jaki entitet | 6 | DFD: Sirovi snimci, Snimci za montazu, Preuzeti snimci sa terena |
| 14 | **GRAFIČKI I MUZIČKI ELEMENT** | jaki entitet | 6 | DFD: Graficki sabloni i muzicka biblioteka; IDEF0: Sabloni i muzicke podloge |
| 15 | **PROGRAMSKA ŠEMA** | jaki entitet | 8 | DFD: Programska sema, Usvojene programske seme, Arhiva programskih sema |
| 16 | **PROGRAMSKA CELINA** | slab entitet | 6 | DFD: Programske celine, Definisane dnevne programske celine |
| 17 | **TERMIN EMITOVANJA** | jaki entitet | 8 | DFD: Raspored termina, TV program po satnici, Raspored repriza |
| 18 | **ZAPIS O EMITOVANJU** | slab entitet | 6 | DFD: Evidencija emitovanja, Zapis o emitovanom sadrzaju, Sta je emitovano i kada |
| 19 | **EMISIJA** | jaki entitet | 8 | DFD: Podaci o emisijama, Informacije o emisijama; IDEF0: Emisija, Format emisije |
| 20 | **MEDIJSKI SADRŽAJ** | jaki entitet | 6 | DFD: Medijska arhiva, Katalog TV sadrzaja, Metapodaci o sadrzaju |
| 21 | **PRODUCIRANI SADRŽAJ** | podtip | 2 | IDEF0: Produciran TV sadrzaj |
| 22 | **NABAVLJENI SADRŽAJ** | podtip | 2 | DFD: Spisak nabavljenih TV sadrzaja |
| 23 | **REKLAMNI SADRŽAJ** | podtip | 2 | DFD: Reklamni materijali |
| 24 | **PRAVO KORIŠĆENJA** | jaki entitet | 8 | DFD: Prava i licence, Evidencija autorskih prava; IDEF0: Autorska prava i licence |
| 25 | **POVRATNA INFO. GLEDALACA** | jaki entitet | 8 | DFD: Povratne informacije gledalaca, Registar zalbi gledalaca, Zalbe |
| 26 | **MERENJE GLEDANOSTI** | jaki entitet | 8 | DFD: Merenja gledanosti, Analize gledanosti, Analiticki pokazatelji |
| 27 | **CENOVNIK REKL. TERMINA** | jaki entitet | 6 | DFD: Cenovnik reklamnih termina, Cene reklamnih termina |
| 28 | **REKLAMNI BLOK** | jaki entitet | 8 | DFD: Reklamni blokovi i cenovnik, Rezervisani reklamni blokovi, Iskoriscenost blokova |
| 29 | **EMITOVANJE REKLAME** | slab entitet | 6 | DFD: Evidencija emitovanja reklama, Zapis o emitovanoj reklami, Obracun reklama |
| 30 | **STAVKA UGOVORA** | slab entitet | 6 | DFD: Ugovorena cena i uslovi placanja, Ugovoreni termini |
| 31 | **UGOVOR** | jaki entitet | 6 | DFD: Ugovori sa klijentima, Ugovori oglasivaca, Arhiva potpisanih ugovora, Nacrti ugovora |
| 32 | **UGOVOR O OGLAŠAVANJU** | podtip | 2 | DFD: Ugovor o reklamiranju |
| 33 | **UGOVOR O PRODAJI TV SADRŽAJA** | podtip | 2 | DFD: Ugovor o ustupanju prava za emitovanje TV emisije |
| 34 | **UGOVOR O NABAVCI** | podtip | 2 | DFD: Ugovori sa dobavljacima |
| 35 | **KLIJENT** | jaki entitet | 6 | DFD: Klijenti i oglasivaci; eksterni entitet OGLASIVACI |
| 36 | **OGLAŠIVAČ** | podtip | 2 | DFD: eksterni entitet OGLASIVACI |
| 37 | **KUPAC SADRŽAJA** | podtip | 2 | DFD: Prodaja TV sadrzaja |
| 38 | **ZAHTEV ZA NABAVKU** | jaki entitet | 8 | DFD: Zahtev za nabavku sa specifikacijom, Zahtev za nabavku/servis opreme |
| 39 | **PLAN NABAVKE** | jaki entitet | 6 | DFD: Plan nabavke, Usvojen plan nabavke; IDEF0: Godisnji plan nabavke |
| 40 | **STAVKA PLANA NABAVKE** | slab entitet | 6 | DFD: Spisak artikala za nabavku, Spisak opreme za nabavku |
| 41 | **PONUDA DOBAVLJAČA** | jaki entitet | 8 | DFD: Ponude dobavljaca, Vrednovane ponude; IDEF0: Uporedni pregled ponuda |
| 42 | **KRITERIJUM VREDNOVANJA** | jaki entitet | 6 | DFD: Kriterijumi vrednovanja ponuda, Kriterijumi za vrednovanje |
| 43 | **ODLUKA O IZBORU DOBAVLJAČA** | jaki entitet | 6 | DFD: Odluke o izboru dobavljaca, Obrazlozenje izbora dobavljaca |
| 44 | **DOBAVLJAČ** | jaki entitet | 6 | DFD: Dobavljaci, Registar dobavljaca; eksterni entitet DOBAVLJACI |
| 45 | **DOBAVLJAČ TV SADRŽAJA** | podtip | 2 | DFD: Nabavka TV sadrzaja |
| 46 | **DOBAVLJAČ OPREME I MATERIJALA** | podtip | 2 | DFD: Spisak opreme za nabavku |
| 47 | **NARUDŽBENICA** | jaki entitet | 6 | DFD: Narudzbenice, Izdata narudzbenica, Podaci sa narudzbenice |
| 48 | **NALOG ZA PLAĆANJE** | jaki entitet | 8 | DFD: Evidencija naloga za placanje, Evidencija realizovanih placanja |
| 49 | **STAVKA FAKTURE** | slab entitet | 6 | DFD: Fakture, Evidentirana faktura |
| 50 | **FAKTURA** | jaki entitet | 8 | DFD: Fakture, Fakture i placanja, Kontrolisana faktura za placanje, Profaktura |
| 51 | **REKLAMACIJA** | jaki entitet | 8 | DFD: Evidencija reklamacija, Evidentirana reklamacija, Odgovor na reklamaciju |
| 52 | **PRIJEMNICA** | jaki entitet | 6 | DFD: Prijemnice, Zapis o prijemu robe, Otpremnica |
| 53 | **STAVKA NARUDŽBENICE** | slab entitet | 6 | DFD: Podaci sa narudzbenice, Spisak artikala za nabavku |

## 2. Tipovi veza

| # | Veza | Objekti i kardinalnosti | Atributi veze | Izvor u DFD / IDEF0 |
|---|---|---|---|---|
| 1 | **PODREĐENA** | ORGANIZACIONA JEDINICA (0, N) — ORGANIZACIONA JEDINICA (0, 1) | – | IDEF0: Hijerarhijska struktura TV stanice |
| 2 | **RADI U** | ZAPOSLENI (1, 1) — ORGANIZACIONA JEDINICA (1, N) | – | IDEF0: Pravilnik o organizaciji i sistematizaciji |
| 3 | **ZADUŽENA** | ZAPOSLENI (0, N) — OPREMA (0, N) | DATUM ZADUŽENJA, DATUM RAZDUŽENJA, STANJE PRI VRAĆANJU | DFD: Zaduzenje i razduzenje, Zaduzena oprema i osobe, Razduzenje opreme |
| 4 | **ANGAŽUJE** | ZAPOSLENI (0, N) — AKTIVNOST PRODUKCIJE (0, N) | ULOGA NA SNIMANJU, DATUM OD, DATUM DO, BROJ ANGAŽOVANIH SATI | DFD: Angazovanja ljudi i opreme, Evidencija angazovanja resursa, Raspored angazovanja ljudi |
| 5 | **ZADUŽUJE** | OPREMA (0, N) — AKTIVNOST PRODUKCIJE (0, N) | DATUM REZERVACIJE, TRAJANJE ZADUŽENJA | DFD: Rezervacija opreme za snimanje, Spisak opreme za produkciju |
| 6 | **ODOBRAVA** | UREDNIK (0, N) — PROJEKAT PRODUKCIJE (1, 1) | – | IDEF0: Urednicke odluke i odobrenja; DFD: Odobrenje za proizvodnju sadrzaja |
| 7 | **SASTOJI SE OD** *(identifikujuća)* | PROJEKAT PRODUKCIJE (1, N) — AKTIVNOST PRODUKCIJE (1, 1) | – | IDEF0: DEFINISANJE AKTIVNOSTI PROJEKTA |
| 8 | **IZAZIVA** *(identifikujuća)* | AKTIVNOST PRODUKCIJE (1, N) — TROŠAK PRODUKCIJE (1, 1) | – | IDEF0: EVIDENCIJA TROSKOVA PRODUKCIJE; DFD: Trosak po aktivnosti |
| 9 | **SNIMLJEN NA** | SIROVI SNIMAK (1, 1) — AKTIVNOST PRODUKCIJE (0, N) | – | IDEF0: SNIMANJE I EVIDENCIJA REALIZACIJE; DFD: Evidencija realizacije snimanja |
| 10 | **PROIZVODI** | PROJEKAT PRODUKCIJE (1, 1) — EMISIJA (0, 1) | – | DFD: Otvoren projekat produkcije, Producirana emisija |
| 11 | **MONTIRAN U** | SIROVI SNIMAK (0, N) — MEDIJSKI SADRŽAJ (1, 1) | – | DFD: Montaza i obrada materijala, Montazna lista, Montiran video materijal |
| 12 | **UGRAĐEN U** | GRAFIČKI I MUZIČKI ELEMENT (0, N) — MEDIJSKI SADRŽAJ (0, N) | VREME POJAVLJIVANJA, NAČIN KORIŠĆENJA | IDEF0: GRAFICKA OBRADA I OZVUCENJE; DFD: Materijal sa grafikom i tonom |
| 13 | **SADRŽI** *(identifikujuća)* | PROGRAMSKA ŠEMA (1, N) — PROGRAMSKA CELINA (1, 1) | – | DFD: Definisanje programskih celina, Zapis programskih celina |
| 14 | **OBUHVATA** *(identifikujuća)* | PROGRAMSKA CELINA (1, N) — TERMIN EMITOVANJA (1, 1) | – | IDEF0: RASPOREDJIVANJE TERMINA EMITOVANJA |
| 15 | **REALIZOVAN** *(identifikujuća)* | TERMIN EMITOVANJA (1, N) — ZAPIS O EMITOVANJU (1, 1) | – | DFD: Evidencija emitovanja, Izvestaj o emitovanom programu |
| 16 | **PLANIRANA** | ZAPIS O EMITOVANJU (1, 1) — EMISIJA (0, N) | – | DFD: Spisak TV programa za emitovanje, Raspored emisija |
| 17 | **ČINI** | EMISIJA (1, N) — MEDIJSKI SADRŽAJ (0, N) | REDNI BROJ U EMISIJI | DFD: Podaci i snimci programskih sadrzaja, Gotov materijal za emitovanje |
| 18 | **POKRIVENO** | MEDIJSKI SADRŽAJ (1, N) — PRAVO KORIŠĆENJA (1, 1) | – | IDEF0: PROVERA PRAVA I PODOBNOSTI SADRZAJA; DFD: Provera prava za termin |
| 19 | **EMITUJE** | ZAPIS O EMITOVANJU (1, 1) — MEDIJSKI SADRŽAJ (0, N) | – | DFD: Zapis o emitovanom sadrzaju, Arhivirani sadrzaj za emitovanje |
| 20 | **MERENA** | MERENJE GLEDANOSTI (1, N) — EMISIJA (1, N) | OSTVARENI RATING, UDEO U TERMINU | IDEF0: ANALIZA GLEDANOSTI EMISIJA I REKLAMA; DFD: Izvestaj o gledanosti TV emisija |
| 21 | **ODNOSI SE NA** | POVRATNA INFO. GLEDALACA (0, N) — EMISIJA (0, 1) | – | DFD: Pregled zalbi po emisijama, Povratne informacije o emisijama |
| 22 | **ZAKUPLJEN U** | REKLAMNI BLOK (1, 1) — TERMIN EMITOVANJA (1, N) | – | DFD: Programska sema sa reklamnim blokovima, Podaci o raspolozivim terminima |
| 23 | **PRIKAZUJE** | EMITOVANJE REKLAME (1, N) — REKLAMNI SADRŽAJ (1, 1) | – | DFD: Preuzimanje i priprema reklamnog materijala, Spreman reklamni materijal |
| 24 | **PODNOSI** | POVRATNA INFO. GLEDALACA (1, N) — MERENJE GLEDANOSTI (0, N) | UDEO U UZORKU | IDEF0: PRIKUPLJANJE MERENJA I ANKETA; DFD: Objedinjene povratne informacije gledalaca |
| 25 | **TARIFIRAN** | CENOVNIK REKL. TERMINA (1, N) — REKLAMNI BLOK (1, 1) | – | DFD: Planiranje reklamnog prostora i cenovnika, Definisani blokovi i cene |
| 26 | **SADRŽI SPOT** *(identifikujuća)* | REKLAMNI BLOK (1, N) — EMITOVANJE REKLAME (1, 1) | – | DFD: Rezervisani reklamni blokovi, Plan emitovanja reklama |
| 27 | **UGOVOREN** | EMITOVANJE REKLAME (1, 1) — STAVKA UGOVORA (0, N) | – | DFD: Ugovoreni termini, Evidencija emitovanja reklama i naplata |
| 28 | **PRECIZIRA** *(identifikujuća)* | UGOVOR (1, N) — STAVKA UGOVORA (1, 1) | – | DFD: Ugovorena cena i uslovi placanja |
| 29 | **SKLAPA** | KLIJENT (1, N) — UGOVOR (1, 1) | – | DFD: Izrada i zakljucivanje ugovora, Zakljucen ugovor sa klijentom |
| 30 | **USTUPA** | UGOVOR O PRODAJI TV SADRŽAJA (1, N) — PRODUCIRANI SADRŽAJ (0, N) | UGOVORENA CENA, OBIM USTUPANJA | DFD: Prodaja TV sadrzaja, Ponuda TV emisije, Prodat TV sadrzaj |
| 31 | **DOSTAVLJA** | OGLAŠIVAČ (1, N) — REKLAMNI SADRŽAJ (1, 1) | – | DFD: Reklamni materijal oglasivaca, Preuzeta reklama |
| 32 | **UGOVARA** | DOBAVLJAČ (1, N) — UGOVOR O NABAVCI (1, 1) | – | DFD: Ugovori sa dobavljacima, Potpisan ugovor za nabavku |
| 33 | **NABAVLJEN PO** | NABAVLJENI SADRŽAJ (1, 1) — UGOVOR O NABAVCI (1, N) | DATUM PREUZIMANJA, UGOVORENA NAKNADA | IDEF0: IZBOR IZVORA SADRZAJA I UGOVARANJE PRAVA, PREUZIMANJE SADRZAJA I UPIS U KATALOG |
| 34 | **UVRŠTEN U** | ZAHTEV ZA NABAVKU (1, 1) — PLAN NABAVKE (0, N) | – | IDEF0: Planiranje i iniciranje nabavke; DFD: Plan nabavke |
| 35 | **SADRŽI** *(identifikujuća)* | PLAN NABAVKE (1, N) — STAVKA PLANA NABAVKE (1, 1) | – | DFD: Spisak artikala za nabavku, Spisak opreme za nabavku |
| 36 | **PONUĐENA** | STAVKA PLANA NABAVKE (0, N) — PONUDA DOBAVLJAČA (1, N) | PONUĐENA CENA, ROK ZA STAVKU | IDEF0: PRIKUPLJANJE I VREDNOVANJE PONUDA |
| 37 | **VREDNUJE SE** | PONUDA DOBAVLJAČA (1, N) — KRITERIJUM VREDNOVANJA (1, N) | BROJ BODOVA, KOMENTAR OCENE | DFD: Kriterijumi vrednovanja ponuda, Vrednovane ponude |
| 38 | **BIRA** | PONUDA DOBAVLJAČA (1, 1) — ODLUKA O IZBORU DOBAVLJAČA (0, 1) | – | IDEF0: IZBOR NAJPOVOLJNIJEG DOBAVLJACA; DFD: Odluka o izboru dobavljaca |
| 39 | **DOSTAVIO** | DOBAVLJAČ (1, N) — PONUDA DOBAVLJAČA (1, 1) | – | DFD: Ponude dobavljaca, Ranije ponude dobavljaca |
| 40 | **NARUČENO OD** | DOBAVLJAČ (1, N) — NARUDŽBENICA (1, 1) | – | DFD: Narudzbenice, Izdata narudzbenica |
| 41 | **SADRŽI** *(identifikujuća)* | NARUDŽBENICA (1, N) — STAVKA NARUDŽBENICE (1, 1) | – | DFD: Podaci sa narudzbenice |
| 42 | **PRAĆENA** | NARUDŽBENICA (1, N) — PRIJEMNICA (1, 1) | – | DFD: Prijemnice, Zapis o prijemu robe, Obavestenje o dostigloj opremi |
| 43 | **OBUHVATA** | PRIJEMNICA (1, N) — STAVKA NARUDŽBENICE (1, N) | PRIMLJENA KOLIČINA, UTVRĐENO ODSTUPANJE | DFD: Zapis o prijemu robe, Otpremnica |
| 44 | **REKLAMIRANA** | PRIJEMNICA (0, N) — REKLAMACIJA (1, 1) | – | DFD: Evidencija reklamacija, Reklamacija, Odgovor na reklamaciju |
| 45 | **FAKTURISANA** | PRIJEMNICA (1, 1) — FAKTURA (0, N) | – | DFD: Obrada faktura i placanja, Kontrolisana faktura za placanje |
| 46 | **SADRŽI** *(identifikujuća)* | FAKTURA (1, N) — STAVKA FAKTURE (1, 1) | – | DFD: Fakture, Evidentirana faktura |
| 47 | **PLAĆENA** | FAKTURA (1, N) — NALOG ZA PLAĆANJE (1, 1) | – | DFD: Evidencija naloga za placanje, Evidencija realizovanih placanja, Potvrde o uplati |
| 48 | **NAPLAĆUJE** | UGOVOR (1, N) — FAKTURA (0, N) | – | DFD: Faktura za reklamiranje, Izvestaji i fakture oglasivacima, Podaci za fakturisanje oglasivaca |

## 3. Specijalizacije (proširenje MOV-a u PMOV)

| # | Nadtip | Podtipovi | Izvor u DFD / IDEF0 |
|---|---|---|---|
| 1 | **ZAPOSLENI** | UREDNIK, NOVINAR / REPORTER, SNIMATELJ, REFERENT | IDEF0 mehanizmi: Urednik, Novinari/Reporter, Snimatelji, Referent za nabavku/oglasavanje |
| 2 | **OPREMA** | SNIMATELJSKA OPREMA, STUDIJSKA I EMISIONA OPREMA | IDEF0: Snimateljska oprema, TV studio i kontrolna soba, Hardver i oprema |
| 3 | **MEDIJSKI SADRŽAJ** | PRODUCIRANI SADRŽAJ, NABAVLJENI SADRŽAJ, REKLAMNI SADRŽAJ | DFD: Produciran TV sadrzaj / Spisak nabavljenih TV sadrzaja / Reklamni materijali |
| 4 | **UGOVOR** | UGOVOR O OGLAŠAVANJU, UGOVOR O PRODAJI TV SADRŽAJA, UGOVOR O NABAVCI | DFD: Ugovori oglasivaca / Ugovor o prenosu vlasnistva tv emisije / Ugovori sa dobavljacima |
| 5 | **KLIJENT** | OGLAŠIVAČ, KUPAC SADRŽAJA | DFD: Klijenti i oglasivaci; eksterni entitet OGLASIVACI; Prodaja TV sadrzaja |
| 6 | **DOBAVLJAČ** | DOBAVLJAČ TV SADRŽAJA, DOBAVLJAČ OPREME I MATERIJALA | DFD: Dobavljaci, Registar dobavljaca; Nabavka TV sadrzaja / Spisak opreme za nabavku |

## 4. Atributi po tipu objekta

- **ORGANIZACIONA JEDINICA**: ŠIFRA JEDINICE *(primarni ključ)*, NAZIV JEDINICE, TIP JEDINICE, OPIS DELATNOSTI, DATUM OSNIVANJA, BROJ ZAPOSLENIH *(izvedeni)*
- **ZAPOSLENI**: ŠIFRA ZAPOSLENOG *(primarni ključ)*, JMBG, IME, PREZIME, RADNO MESTO, DATUM ZAPOSLENJA, OSNOVNA ZARADA, STATUS ZAPOSLENJA
- **UREDNIK**: NIVO OVLAŠĆENJA, REDAKCIJA
- **NOVINAR / REPORTER**: OBLAST IZVEŠTAVANJA, BROJ NOVINARSKE LEG.
- **SNIMATELJ**: SPECIJALNOST, KATEGORIJA DOZVOLE
- **REFERENT**: VRSTA REFERATA, LIMIT ODOBRAVANJA
- **OPREMA**: INVENTARSKI BROJ *(primarni ključ)*, NAZIV OPREME, MODEL, PROIZVOĐAČ, STATUS OPREME, DATUM NABAVKE, GARANCIJA DO, NABAVNA VREDNOST
- **SNIMATELJSKA OPREMA**: TIP NOSAČA ZAPISA, REZOLUCIJA
- **STUDIJSKA I EMISIONA OPREMA**: LOKACIJA U STUDIJU, PROPUSNOST KANALA
- **PROJEKAT PRODUKCIJE**: ŠIFRA PROJEKTA *(primarni ključ)*, NAZIV PROJEKTA, DATUM POČETKA, DATUM ZAVRŠETKA, ODOBREN BUDŽET, STATUS PROJEKTA, VRSTA PRODUKCIJE, OPIS PROJEKTA
- **AKTIVNOST PRODUKCIJE**: RB AKTIVNOSTI *(parcijalni ključ)*, NAZIV AKTIVNOSTI, DATUM OD, DATUM DO, VRSTA AKTIVNOSTI, LOKACIJA SNIMANJA, STATUS AKTIVNOSTI, PLANIRANO TRAJANJE
- **TROŠAK PRODUKCIJE**: RB TROŠKA *(parcijalni ključ)*, VRSTA TROŠKA, IZNOS, DATUM NASTANKA, OPIS TROŠKA, ODSTUPANJE OD BUDŽETA *(izvedeni)*
- **SIROVI SNIMAK**: ŠIFRA SNIMKA *(primarni ključ)*, DATUM SNIMANJA, TRAJANJE, FORMAT SNIMKA, LOKACIJA SNIMKA, OCENA KVALITETA
- **GRAFIČKI I MUZIČKI ELEMENT**: ŠIFRA ELEMENTA *(primarni ključ)*, NAZIV ELEMENTA, TIP ELEMENTA, AUTOR, FORMAT, USLOV KORIŠĆENJA
- **PROGRAMSKA ŠEMA**: ID ŠEME *(primarni ključ)*, NAZIV ŠEME, SEZONA, VERZIJA ŠEME, DATUM OD, DATUM DO, STATUS ŠEME, DATUM USVAJANJA
- **PROGRAMSKA CELINA**: RB CELINE *(parcijalni ključ)*, NAZIV CELINE, TIP CELINE, DAN U NEDELJI, VREME OD, VREME DO
- **TERMIN EMITOVANJA**: ŠIFRA TERMINA *(primarni ključ)*, DATUM, VREME POČETKA, TRAJANJE TERMINA, TIP TERMINA, ZONA GLEDANOSTI, STATUS TERMINA, REDNI BROJ REPRIZE
- **ZAPIS O EMITOVANJU**: RB EMITOVANJA *(parcijalni ključ)*, STATUS REALIZACIJE, STVARNO VREME POČ., STVARNO TRAJANJE, NAPOMENA O SMETNJAMA, OPERATER EMITOVANJA
- **EMISIJA**: ŠIFRA EMISIJE *(primarni ključ)*, NAZIV EMISIJE, ŽANR, FORMAT EMISIJE, PREDVIĐENO TRAJANJE, CILJNA PUBLIKA, STATUS EMISIJE, PROGRAMSKI ELABORAT
- **MEDIJSKI SADRŽAJ**: ŠIFRA SADRŽAJA *(primarni ključ)*, NAZIV SADRŽAJA, TRAJANJE, FORMAT ZAPISA, DATUM ARHIVIRANJA, LOKACIJA U ARHIVI
- **PRODUCIRANI SADRŽAJ**: DATUM PRODUKCIJE, VERZIJA MASTERA
- **NABAVLJENI SADRŽAJ**: IZVOR NABAVKE, CENA NABAVKE
- **REKLAMNI SADRŽAJ**: DATUM PRIJEMA, STATUS PROVERE
- **PRAVO KORIŠĆENJA**: BROJ LICENCE *(primarni ključ)*, VRSTA PRAVA, DATUM OD, DATUM DO, DOZVOLJENO EMITOVANJA, ISKORIŠĆENO EMITOVANJA *(izvedeni)*, TERITORIJA, NOSILAC PRAVA
- **POVRATNA INFO. GLEDALACA**: BROJ PRIJAVE *(primarni ključ)*, DATUM PRIJEMA, VRSTA PRIJAVE, KANAL PRIJEMA, SADRŽAJ PRIJAVE, STATUS OBRADE, DATUM ODGOVORA, PROFIL GLEDAOCA
- **MERENJE GLEDANOSTI**: ŠIFRA MERENJA *(primarni ključ)*, DATUM MERENJA, IZVOR MERENJA, CILJNA GRUPA, RATING, SHARE, BROJ GLEDALACA, PROSEČNO GLEDANJE *(izvedeni)*
- **CENOVNIK REKL. TERMINA**: ŠIFRA CENOVNIKA *(primarni ključ)*, VAŽI OD, VAŽI DO, ZONA, CENA PO SEKUNDI, MINIMALNI PAKET
- **REKLAMNI BLOK**: ŠIFRA BLOKA *(primarni ključ)*, DATUM, VREME POČETKA, TRAJANJE BLOKA, ZAKUPLJENO SEKUNDI, SLOBODNO SEKUNDI *(izvedeni)*, ISKORIŠĆENOST *(izvedeni)*, STATUS BLOKA
- **EMITOVANJE REKLAME**: RB U BLOKU *(parcijalni ključ)*, DATUM EMITOVANJA, VREME EMITOVANJA, TRAJANJE SPOTA, NAPLAĆENI IZNOS, STATUS NAPLATE
- **STAVKA UGOVORA**: RB STAVKE *(parcijalni ključ)*, OPIS STAVKE, KOLIČINA / SEKUNDE, JEDINIČNA CENA, POPUST, VREDNOST STAVKE *(izvedeni)*
- **UGOVOR**: BROJ UGOVORA *(primarni ključ)*, DATUM SKLAPANJA, VAŽI OD, VAŽI DO, UKUPNA VREDNOST, STATUS UGOVORA
- **UGOVOR O OGLAŠAVANJU**: UGOVORENI TERMINI, VRSTA REKLAMIRANJA
- **UGOVOR O PRODAJI TV SADRŽAJA**: PRENOS VLASNIŠTVA, OBIM USTUPLJENIH PRAVA
- **UGOVOR O NABAVCI**: ROK ISPORUKE, USLOVI PLAĆANJA
- **KLIJENT**: ŠIFRA KLIJENTA *(primarni ključ)*, NAZIV KLIJENTA, PIB, MATIČNI BROJ, ADRESA, KONTAKT OSOBA
- **OGLAŠIVAČ**: BRANŠA, GODIŠNJI BUDŽET
- **KUPAC SADRŽAJA**: TIP MEDIJA, TERITORIJA EMITOVANJA
- **ZAHTEV ZA NABAVKU**: BROJ ZAHTEVA *(primarni ključ)*, DATUM ZAHTEVA, VRSTA NABAVKE, PREDMET ZAHTEVA, OBRAZLOŽENJE, STATUS ZAHTEVA, PRIORITET, PROCENJENA VREDNOST
- **PLAN NABAVKE**: ŠIFRA PLANA *(primarni ključ)*, GODINA PLANA, DATUM DONOŠENJA, STATUS PLANA, UKUPNA VREDNOST *(izvedeni)*, DONOSILAC PLANA
- **STAVKA PLANA NABAVKE**: RB STAVKE *(parcijalni ključ)*, OPIS ARTIKLA, KOLIČINA, JEDINICA MERE, PROCENJENA CENA, PLANIRANI KVARTAL
- **PONUDA DOBAVLJAČA**: BROJ PONUDE *(primarni ključ)*, DATUM PRIJEMA, VAŽI DO, UKUPNA CENA, ROK ISPORUKE, USLOVI PLAĆANJA, STATUS PONUDE, UKUPNO BODOVA *(izvedeni)*
- **KRITERIJUM VREDNOVANJA**: ŠIFRA KRITERIJUMA *(primarni ključ)*, NAZIV KRITERIJUMA, PONDER, NAČIN BODOVANJA, OPIS KRITERIJUMA, VAŽI OD
- **ODLUKA O IZBORU DOBAVLJAČA**: BROJ ODLUKE *(primarni ključ)*, DATUM ODLUKE, DONOSILAC ODLUKE, UGOVORENA VREDNOST, OBRAZLOŽENJE IZBORA, STATUS ODLUKE
- **DOBAVLJAČ**: ŠIFRA DOBAVLJAČA *(primarni ključ)*, NAZIV DOBAVLJAČA, PIB, MATIČNI BROJ, ADRESA, OCENA DOBAVLJAČA *(izvedeni)*
- **DOBAVLJAČ TV SADRŽAJA**: VRSTA SADRŽAJA, KATALOG PONUDE
- **DOBAVLJAČ OPREME I MATERIJALA**: ASORTIMAN, OVLAŠĆENI SERVIS
- **NARUDŽBENICA**: BROJ NARUDŽBENICE *(primarni ključ)*, DATUM IZDAVANJA, ROK ISPORUKE, MESTO ISPORUKE, UKUPAN IZNOS *(izvedeni)*, STATUS NARUDŽBINE
- **NALOG ZA PLAĆANJE**: BROJ NALOGA *(primarni ključ)*, DATUM NALOGA, IZNOS NALOGA, SVRHA PLAĆANJA, DATUM REALIZACIJE, STATUS NALOGA, RAČUN PRIMAOCA, ODOBRIO
- **STAVKA FAKTURE**: RB STAVKE *(parcijalni ključ)*, OPIS STAVKE, KOLIČINA, JEDINIČNA CENA, STOPA PDV, VREDNOST STAVKE *(izvedeni)*
- **FAKTURA**: BROJ FAKTURE *(primarni ključ)*, DATUM IZDAVANJA, ROK PLAĆANJA, SMER (ULAZNA/IZLAZNA), OSNOVICA, IZNOS PDV, STATUS PLAĆANJA, IZNOS ZA PLAĆANJE *(izvedeni)*
- **REKLAMACIJA**: BROJ REKLAMACIJE *(primarni ključ)*, DATUM REKLAMACIJE, RAZLOG REKLAMACIJE, OPIS NEDOSTATKA, STATUS REKLAMACIJE, DATUM REŠENJA, NAČIN REŠAVANJA, REKLAMIRANI IZNOS
- **PRIJEMNICA**: BROJ PRIJEMNICE *(primarni ključ)*, DATUM PRIJEMA, BROJ OTPREMNICE, PRIMIO (MAGACIONER), ISPRAVNOST ISPORUKE, NAPOMENA
- **STAVKA NARUDŽBENICE**: RB STAVKE *(parcijalni ključ)*, NAZIV ARTIKLA, KOLIČINA, JEDINIČNA CENA, STATUS STAVKE, VREDNOST STAVKE *(izvedeni)*
