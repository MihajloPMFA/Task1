# Preslikavanje PMOV -> relaciona sema (ER model za ERwin r7.3)

Izvor: `PMOV_TV_stanica_2_1_1.vsdx` (vasa verzija PMOV dijagrama).
Iz njega je masinski procitano: **55 entiteta** (9 slabih), **45 imenovanih veza**,
**7 specijalizacija**, **317 atributa** i **96 oznaka kardinalnosti**.

Rezultat: **69 tabela**, **405 kolona**, **84 stranih kljuceva** (fajl `ER_TV_stanica.sql`).

---

## 1. Pravila preslikavanja koja su primenjena

1. **Jak entitet** -> tabela; njegov kljucni atribut -> primarni kljuc.
2. **Slab entitet** -> tabela ciji je primarni kljuc *kljuc vlasnika + parcijalni kljuc*
   (npr. `AKTIVNOST_PRODUKCIJE(SIFRA_PROJEKTA, RB_AKTIVNOSTI)`). Identifikujuca veza
   ne daje posebnu tabelu - ona je ugradjena u primarni kljuc.
3. **Veza 1:N** -> strani kljuc na strani sa maksimumom 1. Ako je minimum te strane 1,
   kolona je `NOT NULL`; ako je 0, kolona je nullable.
4. **Veza N:M** -> posebna (asocijativna) tabela; primarni kljuc je unija kljuceva
   oba ucesnika; atributi veze postaju kolone te tabele.
5. **Atributi veze 1:N** -> kolone tabele koja nosi strani kljuc
   (npr. `NABAVLJEN PO` -> `NABAVLJENI_SADRZAJ.DATUM_PREUZIMANJA`, `UGOVORENA_NAKNADA`).
6. **Specijalizacija** -> tabela po podtipu; primarni kljuc podtipa je istovremeno
   strani kljuc ka nadtipu. (Ista konvencija kao u vasem primeru `TV_stanica_v7.erwin`,
   gde su `REFERENT_NABAVKE`, `STUDIJSKA_OPREMA` ... zasebne tabele.)
7. **Slozeni atribut** -> razlozen na proste kolone
   (`KLIJENT.ADRESA` -> `ULICA_I_BROJ`, `GRAD`, `POSTANSKI_BROJ`).
8. **Izvedeni atributi** su zadrzani kao kolone, ali su u DDL-u oznaceni komentarom
   `izvedeni atribut` - u fizickoj bazi se racunaju, ne unose.
9. **Imena** su ASCII, velikim slovima, sa podvlakom (S->S, C->C, Z->Z, DJ za D),
   jer ERwin i vecina baza ne rukuju dobro dijakriticima. Duzina imena <= 30 znakova.

---

## 2. Entiteti -> tabele (55)

| PMOV entitet                  | Vrsta             | Tabela                          |
|-------------------------------|-------------------|---------------------------------|
| ORGANIZACIONA JEDINICA        | jak               | `ORGANIZACIONA_JEDINICA`        |
| ZAPOSLENI                     | jak (nadtip)      | `ZAPOSLENI`                     |
| UREDNIK                       | podtip            | `UREDNIK`                       |
| NOVINAR / REPORTER            | podtip            | `NOVINAR_REPORTER`              |
| TEHNICKO OSOBLJE              | podtip            | `TEHNICKO_OSOBLJE`              |
| REFERENT                      | podtip            | `REFERENT`                      |
| SERVISERI                     | podtip            | `SERVISERI`                     |
| OPREMA                        | jak (nadtip)      | `OPREMA`                        |
| SNIMATELJSKA OPREMA           | podtip            | `SNIMATELJSKA_OPREMA`           |
| STUDIJSKA I EMISIONA OPREMA   | podtip (i nadtip) | `STUDIJSKA_I_EMISIONA_OPREMA`   |
| AUDIO OPREMA                  | podtip            | `AUDIO_OPREMA`                  |
| SVETLOSNA OPREMA              | podtip            | `SVETLOSNA_OPREMA`              |
| PROJEKAT PRODUKCIJE           | jak               | `PROJEKAT_PRODUKCIJE`           |
| AKTIVNOST PRODUKCIJE          | slab              | `AKTIVNOST_PRODUKCIJE`          |
| TROSAK PRODUKCIJE             | slab              | `TROSAK_PRODUKCIJE`             |
| SIROVI SNIMAK                 | jak               | `SIROVI_SNIMAK`                 |
| GRAFICKI I MUZICKI ELEMENT    | jak               | `GRAFICKI_I_MUZICKI_ELEMENT`    |
| PROGRAMSKA SEMA               | jak               | `PROGRAMSKA_SEMA`               |
| PROGRAMSKA CELINA             | slab              | `PROGRAMSKA_CELINA`             |
| TERMIN EMITOVANJA             | jak               | `TERMIN_EMITOVANJA`             |
| ZAPIS O EMITOVANJU            | slab              | `ZAPIS_O_EMITOVANJU`            |
| EMISIJA                       | jak               | `EMISIJA`                       |
| MEDIJSKI SADRZAJ              | jak (nadtip)      | `MEDIJSKI_SADRZAJ`              |
| PRODUCIRANI SADRZAJ           | podtip            | `PRODUCIRANI_SADRZAJ`           |
| NABAVLJENI SADRZAJ            | podtip            | `NABAVLJENI_SADRZAJ`            |
| REKLAMNI SADRZAJ              | podtip            | `REKLAMNI_SADRZAJ`              |
| PRAVO KORISCENJA              | jak               | `PRAVO_KORISCENJA`              |
| POVRATNA INFO. GLEDALACA      | jak               | `POVRATNA_INFO_GLEDALACA`       |
| MERENJE GLEDANOSTI            | jak               | `MERENJE_GLEDANOSTI`            |
| CENOVNIK REKL. TERMINA        | jak               | `CENOVNIK_REKL_TERMINA`         |
| REKLAMNI BLOK                 | jak               | `REKLAMNI_BLOK`                 |
| EMITOVANJE REKLAME            | slab              | `EMITOVANJE_REKLAME`            |
| STAVKA UGOVORA                | slab              | `STAVKA_UGOVORA`                |
| UGOVOR                        | jak (nadtip)      | `UGOVOR`                        |
| UGOVOR O OGLASAVANJU          | podtip            | `UGOVOR_O_OGLASAVANJU`          |
| UGOVOR O PRODAJI TV SADRZAJA  | podtip            | `UGOVOR_O_PRODAJI_TV_SADRZAJA`  |
| UGOVOR O NABAVCI              | podtip            | `UGOVOR_O_NABAVCI`              |
| KLIJENT                       | jak (nadtip)      | `KLIJENT`                       |
| OGLASIVAC                     | podtip            | `OGLASIVAC`                     |
| KUPAC SADRZAJA                | podtip            | `KUPAC_SADRZAJA`                |
| ZAHTEV ZA NABAVKU             | jak               | `ZAHTEV_ZA_NABAVKU`             |
| PLAN NABAVKE                  | jak               | `PLAN_NABAVKE`                  |
| STAVKA PLANA NABAVKE          | slab              | `STAVKA_PLANA_NABAVKE`          |
| PONUDA DOBAVLJACA             | jak               | `PONUDA_DOBAVLJACA`             |
| KRITERIJUM VREDNOVANJA        | jak               | `KRITERIJUM_VREDNOVANJA`        |
| DOBAVLJAC                     | jak (nadtip)      | `DOBAVLJAC`                     |
| DOBAVLJAC TV SADRZAJA         | podtip            | `DOBAVLJAC_TV_SADRZAJA`         |
| DOBAVLJAC OPREME I MATERIJALA | podtip            | `DOBAVLJAC_OPREME_I_MATERIJALA` |
| NARUDZBENICA                  | jak               | `NARUDZBENICA`                  |
| STAVKA NARUDZBENICE           | slab              | `STAVKA_NARUDZBENICE`           |
| PRIJEMNICA                    | jak               | `PRIJEMNICA`                    |
| REKLAMACIJA                   | jak               | `REKLAMACIJA`                   |
| FAKTURA                       | jak               | `FAKTURA`                       |
| STAVKA FAKTURE                | slab              | `STAVKA_FAKTURE`                |
| NALOG ZA PLACANJE             | jak               | `NALOG_ZA_PLACANJE`             |

---

## 3. Specijalizacije (7)

| Nadtip                        | Podtipovi u PMOV-u                                                 | Tabele podtipova                                                     |
|-------------------------------|--------------------------------------------------------------------|----------------------------------------------------------------------|
| `ZAPOSLENI`                   | UREDNIK, NOVINAR / REPORTER, TEHNICKO OSOBLJE, REFERENT, SERVISERI | UREDNIK, NOVINAR_REPORTER, TEHNICKO_OSOBLJE, REFERENT, SERVISERI     |
| `OPREMA`                      | SNIMATELJSKA OPREMA, STUDIJSKA I EMISIONA OPREMA                   | SNIMATELJSKA_OPREMA, STUDIJSKA_I_EMISIONA_OPREMA                     |
| `STUDIJSKA_I_EMISIONA_OPREMA` | AUDIO OPREMA, SVETLOSNA OPREMA                                     | AUDIO_OPREMA, SVETLOSNA_OPREMA                                       |
| `MEDIJSKI_SADRZAJ`            | PRODUCIRANI, NABAVLJENI, REKLAMNI SADRZAJ                          | PRODUCIRANI_SADRZAJ, NABAVLJENI_SADRZAJ, REKLAMNI_SADRZAJ            |
| `UGOVOR`                      | O NABAVCI, O OGLASAVANJU, O PRODAJI TV SADRZAJA                    | UGOVOR_O_NABAVCI, UGOVOR_O_OGLASAVANJU, UGOVOR_O_PRODAJI_TV_SADRZAJA |
| `KLIJENT`                     | OGLASIVAC, KUPAC SADRZAJA                                          | OGLASIVAC, KUPAC_SADRZAJA                                            |
| `DOBAVLJAC`                   | DOBAVLJAC TV SADRZAJA, DOBAVLJAC OPREME I MATERIJALA               | DOBAVLJAC_TV_SADRZAJA, DOBAVLJAC_OPREME_I_MATERIJALA                 |

Svaka tabela podtipa ima primarni kljuc koji je istovremeno strani kljuc ka nadtipu,
pa je 1:1 veza sa nadtipom garantovana.

---

## 4. Veze -> strani kljucevi i asocijativne tabele (51)

| PMOV veza                  | Kardinalnosti                                       | Tip                | Realizacija u semi                                                            |
|----------------------------|-----------------------------------------------------|--------------------|-------------------------------------------------------------------------------|
| PODREDJENA                 | ORG. JEDINICA (0,N) - ORG. JEDINICA (0,1)           | 1:N rekurzivna     | ORGANIZACIONA_JEDINICA.SIFRA_NADREDJENE_JEDINICE -> ORGANIZACIONA_JEDINICA    |
| RADI U                     | ZAPOSLENI (1,1) - ORG. JEDINICA (0,N)               | 1:N                | ZAPOSLENI.SIFRA_JEDINICE (NOT NULL)                                           |
| ZADUZENA                   | ZAPOSLENI (0,N) - OPREMA (0,N)                      | N:M + atributi     | tabela ZADUZENJE_OPREME                                                       |
| SERVISIRANJE               | SERVISERI (0,N) - OPREMA (0,N)                      | N:M + atributi     | tabela SERVISIRANJE_OPREME                                                    |
| ANGAZUJE                   | ZAPOSLENI (0,N) - AKTIVNOST PRODUKCIJE (0,N)        | N:M + atributi     | tabela ANGAZOVANJE_NA_AKTIVNOSTI                                              |
| ZADUZUJE                   | OPREMA (0,N) - AKTIVNOST PRODUKCIJE (0,N)           | N:M + atributi     | tabela REZERVACIJA_OPREME                                                     |
| UREDJUJE                   | UREDNIK (0,N) - PROJEKAT PRODUKCIJE (1,1)           | 1:N                | PROJEKAT_PRODUKCIJE.SIFRA_UREDNIKA (NOT NULL)                                 |
| ODOBRAVA                   | UREDNIK (0,N) - PROGRAMSKA SEMA (1,1)               | 1:N                | PROGRAMSKA_SEMA.SIFRA_UREDNIKA (NOT NULL)                                     |
| SASTOJI SE OD *            | PROJEKAT (1,N) - AKTIVNOST (1,1)                    | 1:N identifikujuca | AKTIVNOST_PRODUKCIJE.SIFRA_PROJEKTA u primarnom kljucu                        |
| IZAZIVA                    | AKTIVNOST (0,N) - TROSAK (1,1)                      | 1:N identifikujuca | TROSAK_PRODUKCIJE.(SIFRA_PROJEKTA, RB_AKTIVNOSTI) u primarnom kljucu          |
| DOKUMENTOVAN               | TROSAK PRODUKCIJE (0,1) - FAKTURA (0,N)             | 1:N                | TROSAK_PRODUKCIJE.BROJ_FAKTURE (NULL)                                         |
| SNIMLJEN NA                | SIROVI SNIMAK (1,1) - AKTIVNOST (0,N)               | 1:N                | SIROVI_SNIMAK.(SIFRA_PROJEKTA, RB_AKTIVNOSTI) (NOT NULL)                      |
| PROIZVODI                  | PROJEKAT (0,1) - EMISIJA (0,N)                      | 1:N                | PROJEKAT_PRODUKCIJE.SIFRA_EMISIJE (NULL)                                      |
| MONTIRAN U                 | SIROVI SNIMAK (0,N) - MEDIJSKI SADRZAJ (0,N)        | N:M                | tabela MONTAZA_SNIMKA                                                         |
| UGRADJEN U                 | GRAF. I MUZ. ELEMENT (0,N) - MEDIJSKI SADRZAJ (0,N) | N:M + atributi     | tabela UGRADNJA_ELEMENTA                                                      |
| SADRZI CELINE *            | PROGRAMSKA SEMA (1,N) - PROGRAMSKA CELINA (1,1)     | 1:N identifikujuca | PROGRAMSKA_CELINA.SIFRA_SEME u primarnom kljucu                               |
| OBUHVATA                   | PROGRAMSKA CELINA (1,N) - TERMIN (1,1)              | 1:N                | TERMIN_EMITOVANJA.(SIFRA_SEME, RB_CELINE) (NOT NULL)                          |
| REALIZOVAN *               | TERMIN (0,N) - ZAPIS O EMITOVANJU (1,1)             | 1:N identifikujuca | ZAPIS_O_EMITOVANJU.SIFRA_TERMINA u primarnom kljucu                           |
| PLANIRANA                  | TERMIN (1,1) - EMISIJA (0,N)                        | 1:N                | TERMIN_EMITOVANJA.SIFRA_EMISIJE (NOT NULL)                                    |
| EVIDENTIRA                 | ZAPIS O EMITOVANJU (1,1) - MEDIJSKI SADRZAJ (0,N)   | 1:N                | ZAPIS_O_EMITOVANJU.SIFRA_SADRZAJA (NOT NULL)                                  |
| CINI                       | EMISIJA (1,N) - MEDIJSKI SADRZAJ (0,N)              | N:M + atribut      | tabela SADRZAJ_EMISIJE                                                        |
| POKRIVA                    | PRAVO KORISCENJA (1,N) - MEDIJSKI SADRZAJ (0,N)     | N:M + atribut      | tabela POKRIVENOST_PRAVOM                                                     |
| MERENA                     | MERENJE GLEDANOSTI (1,N) - EMISIJA (0,N)            | N:M + atributi     | tabela MERENJE_EMISIJE                                                        |
| ODNOSI SE NA               | POVRATNA INFO. (0,1) - EMISIJA (0,N)                | 1:N                | POVRATNA_INFO_GLEDALACA.SIFRA_EMISIJE (NULL)                                  |
| ZAKUPLJEN U                | REKLAMNI BLOK (1,1) - TERMIN (0,N)                  | 1:N                | REKLAMNI_BLOK.SIFRA_TERMINA (NOT NULL)                                        |
| TARIFIRAN                  | CENOVNIK (1,N) - REKLAMNI BLOK (1,1)                | 1:N                | REKLAMNI_BLOK.SIFRA_CENOVNIKA (NOT NULL)                                      |
| SADRZI SPOT                | REKLAMNI BLOK (1,N) - EMITOVANJE REKLAME (1,1)      | 1:N identifikujuca | EMITOVANJE_REKLAME.SIFRA_BLOKA u primarnom kljucu                             |
| PRIKAZUJE                  | EMITOVANJE REKLAME (1,1) - REKLAMNI SADRZAJ (0,N)   | 1:N                | EMITOVANJE_REKLAME.SIFRA_SADRZAJA (NOT NULL)                                  |
| UGOVOREN                   | EMITOVANJE REKLAME (1,1) - STAVKA UGOVORA (0,N)     | 1:N                | EMITOVANJE_REKLAME.(BROJ_UGOVORA, RB_STAVKE_UGOVORA) (NOT NULL)               |
| PRECIZIRA                  | UGOVOR (1,N) - STAVKA UGOVORA (1,1)                 | 1:N identifikujuca | STAVKA_UGOVORA.BROJ_UGOVORA u primarnom kljucu                                |
| SKLAPA                     | KLIJENT (0,N) - UGOVOR (0,1)                        | 1:N                | UGOVOR.SIFRA_KLIJENTA (NULL)                                                  |
| DOSTAVLJA                  | OGLASIVAC (1,N) - REKLAMNI SADRZAJ (1,1)            | 1:N                | REKLAMNI_SADRZAJ.SIFRA_OGLASIVACA (NOT NULL)                                  |
| USTUPA                     | UGOVOR O PRODAJI (1,N) - PRODUCIRANI SADRZAJ (0,N)  | N:M + atributi     | tabela USTUPANJE_SADRZAJA                                                     |
| UGOVARA                    | DOBAVLJAC (0,N) - UGOVOR O NABAVCI (1,1)            | 1:N                | UGOVOR_O_NABAVCI.SIFRA_DOBAVLJACA (NOT NULL)                                  |
| NABAVLJEN PO               | NABAVLJENI SADRZAJ (1,1) - UGOVOR O NABAVCI (1,N)   | 1:N + atributi     | NABAVLJENI_SADRZAJ.BROJ_UGOVORA + kolone DATUM_PREUZIMANJA, UGOVORENA_NAKNADA |
| PODNOSI                    | ORG. JEDINICA (0,N) - ZAHTEV ZA NABAVKU (1,1)       | 1:N                | ZAHTEV_ZA_NABAVKU.SIFRA_JEDINICE (NOT NULL)                                   |
| UVRSTEN U                  | ZAHTEV (0,1) - PLAN NABAVKE (0,N)                   | 1:N                | ZAHTEV_ZA_NABAVKU.SIFRA_PLANA (NULL)                                          |
| SADRZI STAVKE PLANA *      | PLAN NABAVKE (1,N) - STAVKA PLANA (1,1)             | 1:N identifikujuca | STAVKA_PLANA_NABAVKE.SIFRA_PLANA u primarnom kljucu                           |
| PONUDJENA                  | STAVKA PLANA (0,N) - PONUDA DOBAVLJACA (0,N)        | N:M + atributi     | tabela PONUDJENA_STAVKA                                                       |
| VREDNUJE SE                | PONUDA (1,N) - KRITERIJUM (1,N)                     | N:M + atributi     | tabela OCENA_PONUDE                                                           |
| DOSTAVIO                   | DOBAVLJAC (0,N) - PONUDA DOBAVLJACA (1,1)           | 1:N                | PONUDA_DOBAVLJACA.SIFRA_DOBAVLJACA (NOT NULL)                                 |
| NARUCENO OD                | DOBAVLJAC (0,N) - NARUDZBENICA (1,1)                | 1:N                | NARUDZBENICA.SIFRA_DOBAVLJACA (NOT NULL)                                      |
| SADRZI STAVKE NARUDZBINE * | NARUDZBENICA (1,N) - STAVKA (1,1)                   | 1:N identifikujuca | STAVKA_NARUDZBENICE.BROJ_NARUDZBENICE u primarnom kljucu                      |
| PRACENA                    | NARUDZBENICA (0,N) - PRIJEMNICA (1,1)               | 1:N                | PRIJEMNICA.BROJ_NARUDZBENICE (NOT NULL)                                       |
| PRIMLJENO PO               | PRIJEMNICA (1,N) - STAVKA NARUDZBENICE (0,N)        | N:M + atributi     | tabela PRIJEM_STAVKE                                                          |
| REKLAMIRANA                | PRIJEMNICA (0,N) - REKLAMACIJA (1,1)                | 1:N                | REKLAMACIJA.BROJ_PRIJEMNICE (NOT NULL)                                        |
| ODNOSI SE NA (reklamacija) | REKLAMACIJA (1,N) - STAVKA NARUDZBENICE (0,N)       | N:M                | tabela REKLAMIRANA_STAVKA                                                     |
| FAKTURISANA                | PRIJEMNICA (0,1) - FAKTURA (0,N)                    | 1:N                | PRIJEMNICA.BROJ_FAKTURE (NULL)                                                |
| SADRZI STAVKE FAKTURE *    | FAKTURA (1,N) - STAVKA FAKTURE (1,1)                | 1:N identifikujuca | STAVKA_FAKTURE.BROJ_FAKTURE u primarnom kljucu                                |
| PLACENA                    | FAKTURA (0,N) - NALOG ZA PLACANJE (1,1)             | 1:N                | NALOG_ZA_PLACANJE.BROJ_FAKTURE (NOT NULL)                                     |
| IZDATA PO                  | UGOVOR (0,N) - FAKTURA (0,1)                        | 1:N                | FAKTURA.BROJ_UGOVORA (NULL)                                                   |

`*` = veza koja **nedostaje u vasoj verziji PMOV-a**, a bez koje slab entitet ne moze
da ima ispravan primarni kljuc - vidi odeljak 6.

---

## 5. Asocijativne tabele (N:M veze)

| Tabela                      | PMOV veza    | Primarni kljuc                                      |
|-----------------------------|--------------|-----------------------------------------------------|
| `ZADUZENJE_OPREME`          | ZADUZENA     | SIFRA_ZAPOSLENOG, INVENTARSKI_BROJ, DATUM_ZADUZENJA |
| `SERVISIRANJE_OPREME`       | SERVISIRANJE | SIFRA_ZAPOSLENOG, INVENTARSKI_BROJ, DATUM_SERVISA   |
| `ANGAZOVANJE_NA_AKTIVNOSTI` | ANGAZUJE     | SIFRA_PROJEKTA, RB_AKTIVNOSTI, SIFRA_ZAPOSLENOG     |
| `REZERVACIJA_OPREME`        | ZADUZUJE     | SIFRA_PROJEKTA, RB_AKTIVNOSTI, INVENTARSKI_BROJ     |
| `MONTAZA_SNIMKA`            | MONTIRAN U   | SIFRA_SADRZAJA, SIFRA_SNIMKA                        |
| `UGRADNJA_ELEMENTA`         | UGRADJEN U   | SIFRA_SADRZAJA, SIFRA_ELEMENTA                      |
| `SADRZAJ_EMISIJE`           | CINI         | SIFRA_EMISIJE, SIFRA_SADRZAJA                       |
| `POKRIVENOST_PRAVOM`        | POKRIVA      | BROJ_LICENCE, SIFRA_SADRZAJA                        |
| `MERENJE_EMISIJE`           | MERENA       | SIFRA_MERENJA, SIFRA_EMISIJE                        |
| `USTUPANJE_SADRZAJA`        | USTUPA       | BROJ_UGOVORA, SIFRA_SADRZAJA                        |
| `PONUDJENA_STAVKA`          | PONUDJENA    | SIFRA_PLANA, RB_STAVKE, BROJ_PONUDE                 |
| `OCENA_PONUDE`              | VREDNUJE SE  | BROJ_PONUDE, SIFRA_KRITERIJUMA                      |
| `PRIJEM_STAVKE`             | PRIMLJENO PO | BROJ_PRIJEMNICE, BROJ_NARUDZBENICE, RB_STAVKE       |
| `REKLAMIRANA_STAVKA`        | ODNOSI SE NA | BROJ_REKLAMACIJE, BROJ_NARUDZBENICE, RB_STAVKE      |

---

## 6. Sta je moralo da se doda u odnosu na vas PMOV

U verziji `PMOV_TV_stanica_2_1_1.vsdx` nedostaje **sest identifikujucih veza**
(dvostruki romb) koje su postojale u prethodnoj verziji dijagrama:

| Identifikujuca veza | Vlasnik | Slab entitet |
|---------------------|---------|--------------|
| SASTOJI SE OD | PROJEKAT PRODUKCIJE | AKTIVNOST PRODUKCIJE |
| SADRZI CELINE | PROGRAMSKA SEMA | PROGRAMSKA CELINA |
| REALIZOVAN | TERMIN EMITOVANJA | ZAPIS O EMITOVANJU |
| SADRZI STAVKE PLANA | PLAN NABAVKE | STAVKA PLANA NABAVKE |
| SADRZI STAVKE NARUDZBINE | NARUDZBENICA | STAVKA NARUDZBENICE |
| SADRZI STAVKE FAKTURE | FAKTURA | STAVKA FAKTURE |

Bez njih:

* pet slabih entiteta nema vlasnika, pa njihov parcijalni kljuc (`RB STAVKE`,
  `RB AKTIVNOSTI`, `RB CELINE`) **ne moze da bude primarni kljuc** - `RB_STAVKE = 1`
  postoji u svakoj narudzbenici;
* `STAVKA FAKTURE` u vasem dijagramu **nema nijednu vezu** - potpuno je odvojena od
  ostatka modela;
* `TROSAK PRODUKCIJE` je slab entitet nad `AKTIVNOST PRODUKCIJE`, koja je i sama slaba
  nad `PROJEKAT PRODUKCIJE`, pa lanac kljuceva puca na prvom clanu.

Zato su te sest veza **vracene u ER model** i oznacene su zvezdicom u tabeli iz
odeljka 4. To je jedino sto je dodato - nijedan entitet, atribut ni veza nisu izmisljeni.

**Nije vraceno:** entitet `ODLUKA O IZBORU DOBAVLJACA` i veza `BIRA`, koje ste obrisali.
To je sadrzinska odluka (koga bira komisija), a ne strukturna nuznost, pa nisu dirane.
Posledica: u semi ne postoji podatak o tome koja je ponuda izabrana - veza
`PONUDA_DOBAVLJACA -> NARUDZBENICA` ide samo posredno, preko dobavljaca. Ako to zelite,
dovoljno je u `NARUDZBENICA` dodati kolonu `BROJ_PONUDE` kao strani kljuc.

**Jedna izmena kardinalnosti:** `REALIZOVAN` je vracen kao `TERMIN (0,N) - ZAPIS (1,1)`
umesto `(0,1) - (1,1)`. Sa `(0,1)` bi `RB EMITOVANJA` bio suvisan (jedan zapis po terminu),
pa slab entitet ne bi imao smisla. Sa `(0,N)` jedan termin moze imati vise zapisa
(npr. prekid i nastavak emitovanja), sto je i razlog postojanja rednog broja.

---

## 7. Struktura tabela

### `ORGANIZACIONA_JEDINICA`

*PMOV:* jak entitet ORGANIZACIONA JEDINICA + rekurzivna veza PODREDJENA (0,N)-(0,1)

| Kolona                      | Tip          | Obavezno | Kljuc                        | Poreklo iz PMOV-a                          |
|-----------------------------|--------------|----------|------------------------------|--------------------------------------------|
| `SIFRA_JEDINICE`            | CHAR(18)     | NOT NULL | PK                           | PK - SIFRA JEDINICE                        |
| `SIFRA_NADREDJENE_JEDINICE` | CHAR(18)     |          | FK -> ORGANIZACIONA_JEDINICA | FK - veza PODREDJENA (nadredjena jedinica) |
| `NAZIV_JEDINICE`            | VARCHAR(60)  | NOT NULL |                              | NAZIV JEDINICE                             |
| `TIP_JEDINICE`              | VARCHAR(30)  |          |                              | TIP JEDINICE                               |
| `OPIS_DELATNOSTI`           | VARCHAR(255) |          |                              | OPIS DELATNOSTI                            |
| `DATUM_OSNIVANJA`           | DATE         |          |                              | DATUM OSNIVANJA                            |
| `BROJ_ZAPOSLENIH`           | INTEGER      |          |                              | BROJ ZAPOSLENIH - izvedeni atribut         |

### `ZAPOSLENI`

*PMOV:* jak entitet ZAPOSLENI + veza RADI U: ZAPOSLENI (1,1) - ORGANIZACIONA JEDINICA (0,N)

| Kolona              | Tip           | Obavezno | Kljuc                        | Poreklo iz PMOV-a     |
|---------------------|---------------|----------|------------------------------|-----------------------|
| `SIFRA_ZAPOSLENOG`  | CHAR(18)      | NOT NULL | PK                           | PK - SIFRA ZAPOSLENOG |
| `SIFRA_JEDINICE`    | CHAR(18)      | NOT NULL | FK -> ORGANIZACIONA_JEDINICA | FK - veza RADI U      |
| `JMBG`              | CHAR(13)      | NOT NULL |                              | JMBG                  |
| `IME`               | VARCHAR(30)   | NOT NULL |                              | IME                   |
| `PREZIME`           | VARCHAR(30)   | NOT NULL |                              | PREZIME               |
| `RADNO_MESTO`       | VARCHAR(60)   |          |                              | RADNO MESTO           |
| `DATUM_ZAPOSLENJA`  | DATE          |          |                              | DATUM ZAPOSLENJA      |
| `OSNOVNA_ZARADA`    | DECIMAL(12,2) |          |                              | OSNOVNA ZARADA        |
| `STATUS_ZAPOSLENJA` | VARCHAR(20)   |          |                              | STATUS ZAPOSLENJA     |

### `UREDNIK`

*PMOV:* podtip ZAPOSLENI -> UREDNIK (specijalizacija)

| Kolona             | Tip         | Obavezno | Kljuc               | Poreklo iz PMOV-a    |
|--------------------|-------------|----------|---------------------|----------------------|
| `SIFRA_ZAPOSLENOG` | CHAR(18)    | NOT NULL | PK, FK -> ZAPOSLENI | PK = FK ka ZAPOSLENI |
| `NIVO_OVLASCENJA`  | VARCHAR(30) |          |                     | NIVO OVLASCENJA      |
| `REDAKCIJA`        | VARCHAR(60) |          |                     | REDAKCIJA            |

### `NOVINAR_REPORTER`

*PMOV:* podtip ZAPOSLENI -> NOVINAR / REPORTER

| Kolona                    | Tip         | Obavezno | Kljuc               | Poreklo iz PMOV-a            |
|---------------------------|-------------|----------|---------------------|------------------------------|
| `SIFRA_ZAPOSLENOG`        | CHAR(18)    | NOT NULL | PK, FK -> ZAPOSLENI | PK = FK ka ZAPOSLENI         |
| `OBLAST_IZVESTAVANJA`     | VARCHAR(60) |          |                     | OBLAST IZVESTAVANJA          |
| `BROJ_NOVINARSKE_LEGITIM` | VARCHAR(20) |          |                     | BROJ NOVINARSKE LEGITIMACIJE |

### `TEHNICKO_OSOBLJE`

*PMOV:* podtip ZAPOSLENI -> TEHNICKO OSOBLJE

| Kolona             | Tip         | Obavezno | Kljuc               | Poreklo iz PMOV-a    |
|--------------------|-------------|----------|---------------------|----------------------|
| `SIFRA_ZAPOSLENOG` | CHAR(18)    | NOT NULL | PK, FK -> ZAPOSLENI | PK = FK ka ZAPOSLENI |
| `SPECIJALIZACIJA`  | VARCHAR(60) |          |                     | SPECIJALIZACIJA      |
| `TIP_EKIPE`        | VARCHAR(30) |          |                     | TIP EKIPE            |

### `REFERENT`

*PMOV:* podtip ZAPOSLENI -> REFERENT

| Kolona             | Tip         | Obavezno | Kljuc               | Poreklo iz PMOV-a    |
|--------------------|-------------|----------|---------------------|----------------------|
| `SIFRA_ZAPOSLENOG` | CHAR(18)    | NOT NULL | PK, FK -> ZAPOSLENI | PK = FK ka ZAPOSLENI |
| `TIP_REFERENTA`    | VARCHAR(30) |          |                     | TIP REFERENTA        |
| `NIVO_OVLASCENJA`  | VARCHAR(30) |          |                     | NIVO OVLASCENJA      |

### `SERVISERI`

*PMOV:* podtip ZAPOSLENI -> SERVISERI

| Kolona             | Tip         | Obavezno | Kljuc               | Poreklo iz PMOV-a    |
|--------------------|-------------|----------|---------------------|----------------------|
| `SIFRA_ZAPOSLENOG` | CHAR(18)    | NOT NULL | PK, FK -> ZAPOSLENI | PK = FK ka ZAPOSLENI |
| `LICENCA`          | VARCHAR(60) |          |                     | LICENCA              |

### `OPREMA`

*PMOV:* jak entitet OPREMA

| Kolona             | Tip           | Obavezno | Kljuc | Poreklo iz PMOV-a                                |
|--------------------|---------------|----------|-------|--------------------------------------------------|
| `INVENTARSKI_BROJ` | CHAR(18)      | NOT NULL | PK    | PK - INVENTARSKI BROJ                            |
| `NAZIV_OPREME`     | VARCHAR(60)   | NOT NULL |       | NAZIV OPREME                                     |
| `MODEL_OPREME`     | VARCHAR(60)   |          |       | MODEL (MODEL je rezervisana rec -> MODEL_OPREME) |
| `PROIZVODJAC`      | VARCHAR(60)   |          |       | PROIZVODJAC                                      |
| `STATUS_OPREME`    | VARCHAR(20)   |          |       | STATUS OPREME                                    |
| `DATUM_NABAVKE`    | DATE          |          |       | DATUM NABAVKE                                    |
| `GARANCIJA_DO`     | DATE          |          |       | GARANCIJA DO                                     |
| `NABAVNA_VREDNOST` | DECIMAL(12,2) |          |       | NABAVNA VREDNOST                                 |

### `SNIMATELJSKA_OPREMA`

*PMOV:* podtip OPREMA -> SNIMATELJSKA OPREMA

| Kolona                      | Tip         | Obavezno | Kljuc            | Poreklo iz PMOV-a         |
|-----------------------------|-------------|----------|------------------|---------------------------|
| `INVENTARSKI_BROJ`          | CHAR(18)    | NOT NULL | PK, FK -> OPREMA | PK = FK ka OPREMA         |
| `TIP_MEMORIJSKOG_SKLADISTA` | VARCHAR(30) |          |                  | TIP MEMORIJSKOG SKLADISTA |
| `REZOLUCIJA`                | VARCHAR(20) |          |                  | REZOLUCIJA                |
| `TIP_KAMERE`                | VARCHAR(30) |          |                  | TIP KAMERE                |

### `STUDIJSKA_I_EMISIONA_OPREMA`

*PMOV:* podtip OPREMA -> STUDIJSKA I EMISIONA OPREMA

| Kolona               | Tip         | Obavezno | Kljuc            | Poreklo iz PMOV-a  |
|----------------------|-------------|----------|------------------|--------------------|
| `INVENTARSKI_BROJ`   | CHAR(18)    | NOT NULL | PK, FK -> OPREMA | PK = FK ka OPREMA  |
| `LOKACIJA_U_STUDIJU` | VARCHAR(60) |          |                  | LOKACIJA U STUDIJU |

### `AUDIO_OPREMA`

*PMOV:* podtip STUDIJSKA I EMISIONA OPREMA -> AUDIO OPREMA

| Kolona             | Tip         | Obavezno | Kljuc                                 | Poreklo iz PMOV-a                      |
|--------------------|-------------|----------|---------------------------------------|----------------------------------------|
| `INVENTARSKI_BROJ` | CHAR(18)    | NOT NULL | PK, FK -> STUDIJSKA_I_EMISIONA_OPREMA | PK = FK ka STUDIJSKA_I_EMISIONA_OPREMA |
| `TIP`              | VARCHAR(30) |          |                                       | TIP                                    |
| `FREKVENCIJA`      | VARCHAR(20) |          |                                       | FREKVENCIJA                            |

### `SVETLOSNA_OPREMA`

*PMOV:* podtip STUDIJSKA I EMISIONA OPREMA -> SVETLOSNA OPREMA

| Kolona             | Tip         | Obavezno | Kljuc                                 | Poreklo iz PMOV-a                      |
|--------------------|-------------|----------|---------------------------------------|----------------------------------------|
| `INVENTARSKI_BROJ` | CHAR(18)    | NOT NULL | PK, FK -> STUDIJSKA_I_EMISIONA_OPREMA | PK = FK ka STUDIJSKA_I_EMISIONA_OPREMA |
| `SNAGA`            | VARCHAR(20) |          |                                       | SNAGA                                  |
| `TIP_SVETLOSTI`    | VARCHAR(30) |          |                                       | TIP SVETLOSTI                          |

### `ZADUZENJE_OPREME`

*PMOV:* veza ZADUZENA: ZAPOSLENI (0,N) - OPREMA (0,N), sa atributima veze

| Kolona                | Tip          | Obavezno | Kljuc               | Poreklo iz PMOV-a                 |
|-----------------------|--------------|----------|---------------------|-----------------------------------|
| `SIFRA_ZAPOSLENOG`    | CHAR(18)     | NOT NULL | PK, FK -> ZAPOSLENI | PK/FK ka ZAPOSLENI                |
| `INVENTARSKI_BROJ`    | CHAR(18)     | NOT NULL | PK, FK -> OPREMA    | PK/FK ka OPREMA                   |
| `DATUM_ZADUZENJA`     | DATE         | NOT NULL | PK                  | PK - atribut veze DATUM ZADUZENJA |
| `DATUM_RAZDUZENJA`    | DATE         |          |                     | atribut veze DATUM RAZDUZENJA     |
| `STANJE_PRI_VRACANJU` | VARCHAR(255) |          |                     | atribut veze STANJE PRI VRACANJU  |

### `SERVISIRANJE_OPREME`

*PMOV:* veza SERVISIRANJE: SERVISERI (0,N) - OPREMA (0,N), sa atributima veze

| Kolona             | Tip           | Obavezno | Kljuc               | Poreklo iz PMOV-a               |
|--------------------|---------------|----------|---------------------|---------------------------------|
| `SIFRA_ZAPOSLENOG` | CHAR(18)      | NOT NULL | PK, FK -> SERVISERI | PK/FK ka SERVISERI              |
| `INVENTARSKI_BROJ` | CHAR(18)      | NOT NULL | PK, FK -> OPREMA    | PK/FK ka OPREMA                 |
| `DATUM_SERVISA`    | DATE          | NOT NULL | PK                  | PK - atribut veze DATUM SERVISA |
| `OPIS_RADOVA`      | VARCHAR(255)  |          |                     | atribut veze OPIS RADOVA        |
| `TROSAK`           | DECIMAL(12,2) |          |                     | atribut veze TROSAK             |

### `PROJEKAT_PRODUKCIJE`

*PMOV:* jak entitet PROJEKAT PRODUKCIJE + UREDJUJE: UREDNIK (0,N)-(1,1) + PROIZVODI: PROJEKAT (0,1)-EMISIJA (0,N)

| Kolona             | Tip           | Obavezno | Kljuc         | Poreklo iz PMOV-a   |
|--------------------|---------------|----------|---------------|---------------------|
| `SIFRA_PROJEKTA`   | CHAR(18)      | NOT NULL | PK            | PK - SIFRA PROJEKTA |
| `SIFRA_UREDNIKA`   | CHAR(18)      | NOT NULL | FK -> UREDNIK | FK - veza UREDJUJE  |
| `SIFRA_EMISIJE`    | CHAR(18)      |          | FK -> EMISIJA | FK - veza PROIZVODI |
| `NAZIV_PROJEKTA`   | VARCHAR(60)   | NOT NULL |               | NAZIV PROJEKTA      |
| `DATUM_POCETKA`    | DATE          |          |               | DATUM POCETKA       |
| `DATUM_ZAVRSETKA`  | DATE          |          |               | DATUM ZAVRSETKA     |
| `ODOBREN_BUDZET`   | DECIMAL(12,2) |          |               | ODOBREN BUDZET      |
| `STATUS_PROJEKTA`  | VARCHAR(20)   |          |               | STATUS PROJEKTA     |
| `VRSTA_PRODUKCIJE` | VARCHAR(30)   |          |               | VRSTA PRODUKCIJE    |
| `OPIS_PROJEKTA`    | VARCHAR(255)  |          |               | OPIS PROJEKTA       |

### `AKTIVNOST_PRODUKCIJE`

*PMOV:* slab entitet AKTIVNOST PRODUKCIJE; identifikujuca veza SASTOJI SE OD: PROJEKAT (1,N) - AKTIVNOST (1,1)

| Kolona              | Tip         | Obavezno | Kljuc                         | Poreklo iz PMOV-a                   |
|---------------------|-------------|----------|-------------------------------|-------------------------------------|
| `SIFRA_PROJEKTA`    | CHAR(18)    | NOT NULL | PK, FK -> PROJEKAT_PRODUKCIJE | PK/FK - identifikujuci vlasnik      |
| `RB_AKTIVNOSTI`     | INTEGER     | NOT NULL | PK                            | PK - parcijalni kljuc RB AKTIVNOSTI |
| `NAZIV_AKTIVNOSTI`  | VARCHAR(60) | NOT NULL |                               | NAZIV AKTIVNOSTI                    |
| `DATUM_OD`          | DATE        |          |                               | DATUM OD                            |
| `DATUM_DO`          | DATE        |          |                               | DATUM DO                            |
| `VRSTA_AKTIVNOSTI`  | VARCHAR(30) |          |                               | VRSTA AKTIVNOSTI                    |
| `LOKACIJA_SNIMANJA` | VARCHAR(60) |          |                               | LOKACIJA SNIMANJA                   |
| `STATUS_AKTIVNOSTI` | VARCHAR(20) |          |                               | STATUS AKTIVNOSTI                   |

### `TROSAK_PRODUKCIJE`

*PMOV:* slab entitet TROSAK PRODUKCIJE; identifikujuca veza IZAZIVA: AKTIVNOST (0,N) - TROSAK (1,1); DOKUMENTOVAN: TROSAK (0,1) - FAKTURA (0,N)

| Kolona           | Tip           | Obavezno | Kljuc                          | Poreklo iz PMOV-a               |
|------------------|---------------|----------|--------------------------------|---------------------------------|
| `SIFRA_PROJEKTA` | CHAR(18)      | NOT NULL | PK, FK -> AKTIVNOST_PRODUKCIJE | PK/FK - identifikujuci vlasnik  |
| `RB_AKTIVNOSTI`  | INTEGER       | NOT NULL | PK, FK -> AKTIVNOST_PRODUKCIJE | PK/FK - identifikujuci vlasnik  |
| `RB_TROSKA`      | INTEGER       | NOT NULL | PK                             | PK - parcijalni kljuc RB TROSKA |
| `BROJ_FAKTURE`   | CHAR(18)      |          | FK -> FAKTURA                  | FK - veza DOKUMENTOVAN          |
| `VRSTA_TROSKA`   | VARCHAR(30)   |          |                                | VRSTA TROSKA                    |
| `IZNOS`          | DECIMAL(12,2) | NOT NULL |                                | IZNOS                           |
| `DATUM_NASTANKA` | DATE          |          |                                | DATUM NASTANKA                  |
| `OPIS_TROSKA`    | VARCHAR(255)  |          |                                | OPIS TROSKA                     |

### `ANGAZOVANJE_NA_AKTIVNOSTI`

*PMOV:* veza ANGAZUJE: ZAPOSLENI (0,N) - AKTIVNOST PRODUKCIJE (0,N), sa atributima veze

| Kolona                  | Tip         | Obavezno | Kljuc                          | Poreklo iz PMOV-a                  |
|-------------------------|-------------|----------|--------------------------------|------------------------------------|
| `SIFRA_PROJEKTA`        | CHAR(18)    | NOT NULL | PK, FK -> AKTIVNOST_PRODUKCIJE | PK/FK ka AKTIVNOST_PRODUKCIJE      |
| `RB_AKTIVNOSTI`         | INTEGER     | NOT NULL | PK, FK -> AKTIVNOST_PRODUKCIJE | PK/FK ka AKTIVNOST_PRODUKCIJE      |
| `SIFRA_ZAPOSLENOG`      | CHAR(18)    | NOT NULL | PK, FK -> ZAPOSLENI            | PK/FK ka ZAPOSLENI                 |
| `ULOGA_NA_SNIMANJU`     | VARCHAR(60) |          |                                | atribut veze ULOGA NA SNIMANJU     |
| `DATUM_OD`              | DATE        |          |                                | atribut veze DATUM OD              |
| `DATUM_DO`              | DATE        |          |                                | atribut veze DATUM DO              |
| `BROJ_ANGAZOVANIH_SATI` | INTEGER     |          |                                | atribut veze BROJ ANGAZOVANIH SATI |

### `REZERVACIJA_OPREME`

*PMOV:* veza ZADUZUJE: OPREMA (0,N) - AKTIVNOST PRODUKCIJE (0,N), sa atributima veze

| Kolona               | Tip      | Obavezno | Kljuc                          | Poreklo iz PMOV-a                      |
|----------------------|----------|----------|--------------------------------|----------------------------------------|
| `SIFRA_PROJEKTA`     | CHAR(18) | NOT NULL | PK, FK -> AKTIVNOST_PRODUKCIJE | PK/FK ka AKTIVNOST_PRODUKCIJE          |
| `RB_AKTIVNOSTI`      | INTEGER  | NOT NULL | PK, FK -> AKTIVNOST_PRODUKCIJE | PK/FK ka AKTIVNOST_PRODUKCIJE          |
| `INVENTARSKI_BROJ`   | CHAR(18) | NOT NULL | PK, FK -> OPREMA               | PK/FK ka OPREMA                        |
| `DATUM_REZERVACIJE`  | DATE     |          |                                | atribut veze DATUM REZERVACIJE         |
| `TRAJANJE_ZADUZENJA` | INTEGER  |          |                                | atribut veze TRAJANJE ZADUZENJA (dana) |

### `SIROVI_SNIMAK`

*PMOV:* jak entitet SIROVI SNIMAK + veza SNIMLJEN NA: SIROVI SNIMAK (1,1) - AKTIVNOST PRODUKCIJE (0,N)

| Kolona            | Tip         | Obavezno | Kljuc                      | Poreklo iz PMOV-a     |
|-------------------|-------------|----------|----------------------------|-----------------------|
| `SIFRA_SNIMKA`    | CHAR(18)    | NOT NULL | PK                         | PK - SIFRA SNIMKA     |
| `SIFRA_PROJEKTA`  | CHAR(18)    | NOT NULL | FK -> AKTIVNOST_PRODUKCIJE | FK - veza SNIMLJEN NA |
| `RB_AKTIVNOSTI`   | INTEGER     | NOT NULL | FK -> AKTIVNOST_PRODUKCIJE | FK - veza SNIMLJEN NA |
| `DATUM_SNIMANJA`  | DATE        |          |                            | DATUM SNIMANJA        |
| `TRAJANJE`        | INTEGER     |          |                            | TRAJANJE (sekundi)    |
| `FORMAT_SNIMKA`   | VARCHAR(30) |          |                            | FORMAT SNIMKA         |
| `LOKACIJA_SNIMKA` | VARCHAR(60) |          |                            | LOKACIJA SNIMKA       |
| `OCENA_KVALITETA` | VARCHAR(20) |          |                            | OCENA KVALITETA       |

### `GRAFICKI_I_MUZICKI_ELEMENT`

*PMOV:* jak entitet GRAFICKI I MUZICKI ELEMENT

| Kolona             | Tip          | Obavezno | Kljuc | Poreklo iz PMOV-a                                     |
|--------------------|--------------|----------|-------|-------------------------------------------------------|
| `SIFRA_ELEMENTA`   | CHAR(18)     | NOT NULL | PK    | PK - SIFRA ELEMENTA                                   |
| `NAZIV_ELEMENTA`   | VARCHAR(60)  | NOT NULL |       | NAZIV ELEMENTA                                        |
| `TIP_ELEMENTA`     | VARCHAR(30)  |          |       | TIP ELEMENTA                                          |
| `AUTOR`            | VARCHAR(60)  |          |       | AUTOR                                                 |
| `FORMAT_ELEMENTA`  | VARCHAR(30)  |          |       | FORMAT (FORMAT je rezervisana rec -> FORMAT_ELEMENTA) |
| `USLOV_KORISCENJA` | VARCHAR(255) |          |       | USLOV KORISCENJA                                      |

### `PROGRAMSKA_SEMA`

*PMOV:* jak entitet PROGRAMSKA SEMA + veza ODOBRAVA: UREDNIK (0,N) - PROGRAMSKA SEMA (1,1)

| Kolona            | Tip         | Obavezno | Kljuc         | Poreklo iz PMOV-a  |
|-------------------|-------------|----------|---------------|--------------------|
| `SIFRA_SEME`      | CHAR(18)    | NOT NULL | PK            | PK - ID SEME       |
| `SIFRA_UREDNIKA`  | CHAR(18)    | NOT NULL | FK -> UREDNIK | FK - veza ODOBRAVA |
| `NAZIV_SEME`      | VARCHAR(60) | NOT NULL |               | NAZIV SEME         |
| `SEZONA`          | VARCHAR(20) |          |               | SEZONA             |
| `VERZIJA_SEME`    | VARCHAR(20) |          |               | VERZIJA SEME       |
| `DATUM_OD`        | DATE        |          |               | DATUM OD           |
| `DATUM_DO`        | DATE        |          |               | DATUM DO           |
| `STATUS_SEME`     | VARCHAR(20) |          |               | STATUS SEME        |
| `DATUM_USVAJANJA` | DATE        |          |               | DATUM USVAJANJA    |

### `PROGRAMSKA_CELINA`

*PMOV:* slab entitet PROGRAMSKA CELINA; identifikujuca veza SADRZI CELINE: PROGRAMSKA SEMA (1,N) - PROGRAMSKA CELINA (1,1)

| Kolona         | Tip         | Obavezno | Kljuc                     | Poreklo iz PMOV-a               |
|----------------|-------------|----------|---------------------------|---------------------------------|
| `SIFRA_SEME`   | CHAR(18)    | NOT NULL | PK, FK -> PROGRAMSKA_SEMA | PK/FK - identifikujuci vlasnik  |
| `RB_CELINE`    | INTEGER     | NOT NULL | PK                        | PK - parcijalni kljuc RB CELINE |
| `NAZIV_CELINE` | VARCHAR(60) | NOT NULL |                           | NAZIV CELINE                    |
| `TIP_CELINE`   | VARCHAR(30) |          |                           | TIP CELINE                      |
| `DATUM`        | DATE        |          |                           | DATUM                           |
| `VREME_OD`     | TIME        |          |                           | VREME OD                        |
| `VREME_DO`     | TIME        |          |                           | VREME DO                        |

### `EMISIJA`

*PMOV:* jak entitet EMISIJA

| Kolona                 | Tip          | Obavezno | Kljuc | Poreklo iz PMOV-a             |
|------------------------|--------------|----------|-------|-------------------------------|
| `SIFRA_EMISIJE`        | CHAR(18)     | NOT NULL | PK    | PK - SIFRA EMISIJE            |
| `NAZIV_EMISIJE`        | VARCHAR(60)  | NOT NULL |       | NAZIV EMISIJE                 |
| `ZANR`                 | VARCHAR(30)  |          |       | ZANR                          |
| `FORMAT_EMISIJE`       | VARCHAR(30)  |          |       | FORMAT EMISIJE                |
| `PREDVIDJENO_TRAJANJE` | INTEGER      |          |       | PREDVIDJENO TRAJANJE (minuta) |
| `CILJNA_PUBLIKA`       | VARCHAR(60)  |          |       | CILJNA PUBLIKA                |
| `STATUS_EMISIJE`       | VARCHAR(20)  |          |       | STATUS EMISIJE                |
| `PROGRAMSKI_ELABORAT`  | VARCHAR(255) |          |       | PROGRAMSKI ELABORAT           |

### `TERMIN_EMITOVANJA`

*PMOV:* jak entitet TERMIN EMITOVANJA + OBUHVATA: PROGRAMSKA CELINA (1,N)-(1,1) + PLANIRANA: TERMIN (1,1) - EMISIJA (0,N)

| Kolona               | Tip         | Obavezno | Kljuc                   | Poreklo iz PMOV-a         |
|----------------------|-------------|----------|-------------------------|---------------------------|
| `SIFRA_TERMINA`      | CHAR(18)    | NOT NULL | PK                      | PK - SIFRA TERMINA        |
| `SIFRA_SEME`         | CHAR(18)    | NOT NULL | FK -> PROGRAMSKA_CELINA | FK - veza OBUHVATA        |
| `RB_CELINE`          | INTEGER     | NOT NULL | FK -> PROGRAMSKA_CELINA | FK - veza OBUHVATA        |
| `SIFRA_EMISIJE`      | CHAR(18)    | NOT NULL | FK -> EMISIJA           | FK - veza PLANIRANA       |
| `DATUM`              | DATE        | NOT NULL |                         | DATUM                     |
| `VREME_POCETKA`      | TIME        | NOT NULL |                         | VREME POCETKA             |
| `TRAJANJE_TERMINA`   | INTEGER     |          |                         | TRAJANJE TERMINA (minuta) |
| `TIP_TERMINA`        | VARCHAR(30) |          |                         | TIP TERMINA               |
| `ZONA_GLEDANOSTI`    | VARCHAR(20) |          |                         | ZONA GLEDANOSTI           |
| `STATUS_TERMINA`     | VARCHAR(20) |          |                         | STATUS TERMINA            |
| `REDNI_BROJ_REPRIZE` | INTEGER     |          |                         | REDNI BROJ REPRIZE        |

### `MEDIJSKI_SADRZAJ`

*PMOV:* jak entitet MEDIJSKI SADRZAJ (nadtip)

| Kolona              | Tip         | Obavezno | Kljuc | Poreklo iz PMOV-a   |
|---------------------|-------------|----------|-------|---------------------|
| `SIFRA_SADRZAJA`    | CHAR(18)    | NOT NULL | PK    | PK - SIFRA SADRZAJA |
| `NAZIV_SADRZAJA`    | VARCHAR(60) | NOT NULL |       | NAZIV SADRZAJA      |
| `TRAJANJE`          | INTEGER     |          |       | TRAJANJE (sekundi)  |
| `FORMAT_ZAPISA`     | VARCHAR(30) |          |       | FORMAT ZAPISA       |
| `DATUM_ARHIVIRANJA` | DATE        |          |       | DATUM ARHIVIRANJA   |
| `LOKACIJA_U_ARHIVI` | VARCHAR(60) |          |       | LOKACIJA U ARHIVI   |

### `PRODUCIRANI_SADRZAJ`

*PMOV:* podtip MEDIJSKI SADRZAJ -> PRODUCIRANI SADRZAJ

| Kolona             | Tip         | Obavezno | Kljuc                      | Poreklo iz PMOV-a           |
|--------------------|-------------|----------|----------------------------|-----------------------------|
| `SIFRA_SADRZAJA`   | CHAR(18)    | NOT NULL | PK, FK -> MEDIJSKI_SADRZAJ | PK = FK ka MEDIJSKI_SADRZAJ |
| `DATUM_PRODUKCIJE` | DATE        |          |                            | DATUM PRODUKCIJE            |
| `VERZIJA_MASTERA`  | VARCHAR(20) |          |                            | VERZIJA MASTERA             |

### `NABAVLJENI_SADRZAJ`

*PMOV:* podtip MEDIJSKI SADRZAJ -> NABAVLJENI SADRZAJ + veza NABAVLJEN PO: NABAVLJENI SADRZAJ (1,1) - UGOVOR O NABAVCI (1,N), sa atributima veze

| Kolona              | Tip           | Obavezno | Kljuc                      | Poreklo iz PMOV-a                            |
|---------------------|---------------|----------|----------------------------|----------------------------------------------|
| `SIFRA_SADRZAJA`    | CHAR(18)      | NOT NULL | PK, FK -> MEDIJSKI_SADRZAJ | PK = FK ka MEDIJSKI_SADRZAJ                  |
| `BROJ_UGOVORA`      | CHAR(18)      | NOT NULL | FK -> UGOVOR_O_NABAVCI     | FK - veza NABAVLJEN PO                       |
| `ZEMLJA_POREKLA`    | VARCHAR(60)   |          |                            | ZEMLJA POREKLA                               |
| `CENA_NABAVKE`      | DECIMAL(12,2) |          |                            | CENA NABAVKE                                 |
| `DATUM_PREUZIMANJA` | DATE          |          |                            | atribut veze NABAVLJEN PO: DATUM PREUZIMANJA |
| `UGOVORENA_NAKNADA` | DECIMAL(12,2) |          |                            | atribut veze NABAVLJEN PO: UGOVORENA NAKNADA |

### `REKLAMNI_SADRZAJ`

*PMOV:* podtip MEDIJSKI SADRZAJ -> REKLAMNI SADRZAJ + veza DOSTAVLJA: OGLASIVAC (1,N) - REKLAMNI SADRZAJ (1,1)

| Kolona             | Tip         | Obavezno | Kljuc                      | Poreklo iz PMOV-a           |
|--------------------|-------------|----------|----------------------------|-----------------------------|
| `SIFRA_SADRZAJA`   | CHAR(18)    | NOT NULL | PK, FK -> MEDIJSKI_SADRZAJ | PK = FK ka MEDIJSKI_SADRZAJ |
| `SIFRA_OGLASIVACA` | CHAR(18)    | NOT NULL | FK -> OGLASIVAC            | FK - veza DOSTAVLJA         |
| `DATUM_PRIJEMA`    | DATE        |          |                            | DATUM PRIJEMA               |
| `STATUS`           | VARCHAR(20) |          |                            | STATUS                      |

### `ZAPIS_O_EMITOVANJU`

*PMOV:* slab entitet ZAPIS O EMITOVANJU; identifikujuca veza REALIZOVAN: TERMIN (0,N) - ZAPIS (1,1); EVIDENTIRA: ZAPIS (1,1) - MEDIJSKI SADRZAJ (0,N)

| Kolona                  | Tip          | Obavezno | Kljuc                       | Poreklo iz PMOV-a                   |
|-------------------------|--------------|----------|-----------------------------|-------------------------------------|
| `SIFRA_TERMINA`         | CHAR(18)     | NOT NULL | PK, FK -> TERMIN_EMITOVANJA | PK/FK - identifikujuci vlasnik      |
| `RB_EMITOVANJA`         | INTEGER      | NOT NULL | PK                          | PK - parcijalni kljuc RB EMITOVANJA |
| `SIFRA_SADRZAJA`        | CHAR(18)     | NOT NULL | FK -> MEDIJSKI_SADRZAJ      | FK - veza EVIDENTIRA                |
| `STATUS_REALIZACIJE`    | VARCHAR(20)  |          |                             | STATUS REALIZACIJE                  |
| `STVARNO_VREME_POCETKA` | TIME         |          |                             | STVARNO VREME POC.                  |
| `STVARNO_TRAJANJE`      | INTEGER      |          |                             | STVARNO TRAJANJE (sekundi)          |
| `NAPOMENA_O_SMETNJAMA`  | VARCHAR(255) |          |                             | NAPOMENA O SMETNJAMA                |
| `OPERATER_EMITOVANJA`   | VARCHAR(60)  |          |                             | OPERATER EMITOVANJA                 |

### `MONTAZA_SNIMKA`

*PMOV:* veza MONTIRAN U: SIROVI SNIMAK (0,N) - MEDIJSKI SADRZAJ (0,N)

| Kolona           | Tip      | Obavezno | Kljuc                      | Poreklo iz PMOV-a         |
|------------------|----------|----------|----------------------------|---------------------------|
| `SIFRA_SADRZAJA` | CHAR(18) | NOT NULL | PK, FK -> MEDIJSKI_SADRZAJ | PK/FK ka MEDIJSKI_SADRZAJ |
| `SIFRA_SNIMKA`   | CHAR(18) | NOT NULL | PK, FK -> SIROVI_SNIMAK    | PK/FK ka SIROVI_SNIMAK    |

### `UGRADNJA_ELEMENTA`

*PMOV:* veza UGRADJEN U: GRAFICKI I MUZICKI ELEMENT (0,N) - MEDIJSKI SADRZAJ (0,N), sa atributima veze

| Kolona                | Tip         | Obavezno | Kljuc                                | Poreklo iz PMOV-a                   |
|-----------------------|-------------|----------|--------------------------------------|-------------------------------------|
| `SIFRA_SADRZAJA`      | CHAR(18)    | NOT NULL | PK, FK -> MEDIJSKI_SADRZAJ           | PK/FK ka MEDIJSKI_SADRZAJ           |
| `SIFRA_ELEMENTA`      | CHAR(18)    | NOT NULL | PK, FK -> GRAFICKI_I_MUZICKI_ELEMENT | PK/FK ka GRAFICKI_I_MUZICKI_ELEMENT |
| `VREME_POJAVLJIVANJA` | TIME        |          |                                      | atribut veze VREME POJAVLJIVANJA    |
| `NACIN_KORISCENJA`    | VARCHAR(60) |          |                                      | atribut veze NACIN KORISCENJA       |

### `SADRZAJ_EMISIJE`

*PMOV:* veza CINI: EMISIJA (1,N) - MEDIJSKI SADRZAJ (0,N), sa atributom veze

| Kolona                 | Tip      | Obavezno | Kljuc                      | Poreklo iz PMOV-a                 |
|------------------------|----------|----------|----------------------------|-----------------------------------|
| `SIFRA_EMISIJE`        | CHAR(18) | NOT NULL | PK, FK -> EMISIJA          | PK/FK ka EMISIJA                  |
| `SIFRA_SADRZAJA`       | CHAR(18) | NOT NULL | PK, FK -> MEDIJSKI_SADRZAJ | PK/FK ka MEDIJSKI_SADRZAJ         |
| `REDNI_BROJ_U_EMISIJI` | INTEGER  |          |                            | atribut veze REDNI BROJ U EMISIJI |

### `PRAVO_KORISCENJA`

*PMOV:* jak entitet PRAVO KORISCENJA

| Kolona                   | Tip         | Obavezno | Kljuc | Poreklo iz PMOV-a                         |
|--------------------------|-------------|----------|-------|-------------------------------------------|
| `BROJ_LICENCE`           | CHAR(18)    | NOT NULL | PK    | PK - BROJ LICENCE                         |
| `VRSTA_PRAVA`            | VARCHAR(30) |          |       | VRSTA PRAVA                               |
| `DATUM_OD`               | DATE        |          |       | DATUM OD                                  |
| `DATUM_DO`               | DATE        |          |       | DATUM DO                                  |
| `DOZVOLJENO_EMITOVANJA`  | INTEGER     |          |       | DOZVOLJENO EMITOVANJA                     |
| `ISKORISCENO_EMITOVANJA` | INTEGER     |          |       | ISKORISCENO EMITOVANJA - izvedeni atribut |
| `TERITORIJA`             | VARCHAR(60) |          |       | TERITORIJA                                |
| `NOSILAC_PRAVA`          | VARCHAR(60) |          |       | NOSILAC PRAVA                             |

### `POKRIVENOST_PRAVOM`

*PMOV:* veza POKRIVA: PRAVO KORISCENJA (1,N) - MEDIJSKI SADRZAJ (0,N), sa atributom veze

| Kolona                | Tip         | Obavezno | Kljuc                      | Poreklo iz PMOV-a                |
|-----------------------|-------------|----------|----------------------------|----------------------------------|
| `BROJ_LICENCE`        | CHAR(18)    | NOT NULL | PK, FK -> PRAVO_KORISCENJA | PK/FK ka PRAVO_KORISCENJA        |
| `SIFRA_SADRZAJA`      | CHAR(18)    | NOT NULL | PK, FK -> MEDIJSKI_SADRZAJ | PK/FK ka MEDIJSKI_SADRZAJ        |
| `OBLAST_POKRIVENOSTI` | VARCHAR(60) |          |                            | atribut veze OBLAST POKRIVENOSTI |

### `POVRATNA_INFO_GLEDALACA`

*PMOV:* jak entitet POVRATNA INFO. GLEDALACA + veza ODNOSI SE NA: POVRATNA INFO (0,1) - EMISIJA (0,N)

| Kolona            | Tip          | Obavezno | Kljuc         | Poreklo iz PMOV-a      |
|-------------------|--------------|----------|---------------|------------------------|
| `BROJ_PRIJAVE`    | CHAR(18)     | NOT NULL | PK            | PK - BROJ PRIJAVE      |
| `SIFRA_EMISIJE`   | CHAR(18)     |          | FK -> EMISIJA | FK - veza ODNOSI SE NA |
| `DATUM_PRIJEMA`   | DATE         |          |               | DATUM PRIJEMA          |
| `VRSTA_PRIJAVE`   | VARCHAR(30)  |          |               | VRSTA PRIJAVE          |
| `KANAL_PRIJEMA`   | VARCHAR(30)  |          |               | KANAL PRIJEMA          |
| `SADRZAJ_PRIJAVE` | VARCHAR(255) |          |               | SADRZAJ PRIJAVE        |
| `STATUS_OBRADE`   | VARCHAR(20)  |          |               | STATUS OBRADE          |
| `DATUM_ODGOVORA`  | DATE         |          |               | DATUM ODGOVORA         |
| `PROFIL_GLEDAOCA` | VARCHAR(60)  |          |               | PROFIL GLEDAOCA        |

### `MERENJE_GLEDANOSTI`

*PMOV:* jak entitet MERENJE GLEDANOSTI

| Kolona              | Tip          | Obavezno | Kljuc | Poreklo iz PMOV-a                              |
|---------------------|--------------|----------|-------|------------------------------------------------|
| `SIFRA_MERENJA`     | CHAR(18)     | NOT NULL | PK    | PK - SIFRA MERENJA                             |
| `DATUM_MERENJA`     | DATE         |          |       | DATUM MERENJA                                  |
| `IZVOR_MERENJA`     | VARCHAR(60)  |          |       | IZVOR MERENJA                                  |
| `CILJNA_GRUPA`      | VARCHAR(60)  |          |       | CILJNA GRUPA                                   |
| `RATING`            | DECIMAL(5,2) |          |       | RATING                                         |
| `SHARE_UDEO`        | DECIMAL(5,2) |          |       | SHARE (SHARE je rezervisana rec -> SHARE_UDEO) |
| `BROJ_GLEDALACA`    | INTEGER      |          |       | BROJ GLEDALACA                                 |
| `PROSECNO_GLEDANJE` | INTEGER      |          |       | PROSECNO GLEDANJE (minuta)                     |

### `MERENJE_EMISIJE`

*PMOV:* veza MERENA: MERENJE GLEDANOSTI (1,N) - EMISIJA (0,N), sa atributima veze

| Kolona             | Tip          | Obavezno | Kljuc                        | Poreklo iz PMOV-a             |
|--------------------|--------------|----------|------------------------------|-------------------------------|
| `SIFRA_MERENJA`    | CHAR(18)     | NOT NULL | PK, FK -> MERENJE_GLEDANOSTI | PK/FK ka MERENJE_GLEDANOSTI   |
| `SIFRA_EMISIJE`    | CHAR(18)     | NOT NULL | PK, FK -> EMISIJA            | PK/FK ka EMISIJA              |
| `OSTVARENI_RATING` | DECIMAL(5,2) |          |                              | atribut veze OSTVARENI RATING |
| `UDEO_U_TERMINU`   | DECIMAL(5,2) |          |                              | atribut veze UDEO U TERMINU   |

### `CENOVNIK_REKL_TERMINA`

*PMOV:* jak entitet CENOVNIK REKL. TERMINA

| Kolona                 | Tip           | Obavezno | Kljuc | Poreklo iz PMOV-a    |
|------------------------|---------------|----------|-------|----------------------|
| `SIFRA_CENOVNIKA`      | CHAR(18)      | NOT NULL | PK    | PK - SIFRA CENOVNIKA |
| `VAZI_OD`              | DATE          |          |       | VAZI OD              |
| `VAZI_DO`              | DATE          |          |       | VAZI DO              |
| `ZONA`                 | VARCHAR(30)   |          |       | ZONA                 |
| `CENA_PO_SEKUNDI`      | DECIMAL(12,2) |          |       | CENA PO SEKUNDI      |
| `TIP_CENOVNOG_PAKETA`  | VARCHAR(30)   |          |       | TIP CENOVNOG PAKETA  |
| `OPIS_CENOVNOG_PAKETA` | VARCHAR(255)  |          |       | OPIS CENOVNOG PAKETA |

### `REKLAMNI_BLOK`

*PMOV:* jak entitet REKLAMNI BLOK + ZAKUPLJEN U: BLOK (1,1) - TERMIN (0,N) + TARIFIRAN: CENOVNIK (1,N) - BLOK (1,1)

| Kolona               | Tip          | Obavezno | Kljuc                       | Poreklo iz PMOV-a                     |
|----------------------|--------------|----------|-----------------------------|---------------------------------------|
| `SIFRA_BLOKA`        | CHAR(18)     | NOT NULL | PK                          | PK - SIFRA BLOKA                      |
| `SIFRA_TERMINA`      | CHAR(18)     | NOT NULL | FK -> TERMIN_EMITOVANJA     | FK - veza ZAKUPLJEN U                 |
| `SIFRA_CENOVNIKA`    | CHAR(18)     | NOT NULL | FK -> CENOVNIK_REKL_TERMINA | FK - veza TARIFIRAN                   |
| `DATUM`              | DATE         |          |                             | DATUM                                 |
| `VREME_POCETKA`      | TIME         |          |                             | VREME POCETKA                         |
| `TRAJANJE_BLOKA`     | INTEGER      |          |                             | TRAJANJE BLOKA (sekundi)              |
| `ZAKUPLJENO_SEKUNDI` | INTEGER      |          |                             | ZAKUPLJENO SEKUNDI - izvedeni atribut |
| `SLOBODNO_SEKUNDI`   | INTEGER      |          |                             | SLOBODNO SEKUNDI - izvedeni atribut   |
| `ISKORISCENOST`      | DECIMAL(5,2) |          |                             | ISKORISCENOST - izvedeni atribut      |
| `STATUS_BLOKA`       | VARCHAR(20)  |          |                             | STATUS BLOKA                          |

### `EMITOVANJE_REKLAME`

*PMOV:* slab entitet EMITOVANJE REKLAME; identifikujuca veza SADRZI SPOT: REKLAMNI BLOK (1,N) - (1,1); PRIKAZUJE: (1,1) - REKLAMNI SADRZAJ (0,N); UGOVOREN: (1,1) - STAVKA UGOVORA (0,N)

| Kolona              | Tip           | Obavezno | Kljuc                   | Poreklo iz PMOV-a                |
|---------------------|---------------|----------|-------------------------|----------------------------------|
| `SIFRA_BLOKA`       | CHAR(18)      | NOT NULL | PK, FK -> REKLAMNI_BLOK | PK/FK - identifikujuci vlasnik   |
| `RB_U_BLOKU`        | INTEGER       | NOT NULL | PK                      | PK - parcijalni kljuc RB U BLOKU |
| `SIFRA_SADRZAJA`    | CHAR(18)      | NOT NULL | FK -> REKLAMNI_SADRZAJ  | FK - veza PRIKAZUJE              |
| `BROJ_UGOVORA`      | CHAR(18)      | NOT NULL | FK -> STAVKA_UGOVORA    | FK - veza UGOVOREN               |
| `RB_STAVKE_UGOVORA` | INTEGER       | NOT NULL | FK -> STAVKA_UGOVORA    | FK - veza UGOVOREN               |
| `DATUM_EMITOVANJA`  | DATE          |          |                         | DATUM EMITOVANJA                 |
| `VREME_EMITOVANJA`  | TIME          |          |                         | VREME EMITOVANJA                 |
| `TRAJANJE_SPOTA`    | INTEGER       |          |                         | TRAJANJE SPOTA (sekundi)         |
| `NAPLACENI_IZNOS`   | DECIMAL(12,2) |          |                         | NAPLACENI IZNOS                  |
| `STATUS_NAPLATE`    | VARCHAR(20)   |          |                         | STATUS NAPLATE                   |

### `KLIJENT`

*PMOV:* jak entitet KLIJENT (nadtip); ADRESA je slozeni atribut

| Kolona           | Tip         | Obavezno | Kljuc | Poreklo iz PMOV-a                         |
|------------------|-------------|----------|-------|-------------------------------------------|
| `SIFRA_KLIJENTA` | CHAR(18)    | NOT NULL | PK    | PK - SIFRA KLIJENTA                       |
| `NAZIV_KLIJENTA` | VARCHAR(60) | NOT NULL |       | NAZIV KLIJENTA                            |
| `PIB`            | CHAR(9)     |          |       | PIB                                       |
| `MATICNI_BROJ`   | CHAR(8)     |          |       | MATICNI BROJ                              |
| `ULICA_I_BROJ`   | VARCHAR(60) |          |       | ADRESA / ULICA I BROJ (slozeni atribut)   |
| `GRAD`           | VARCHAR(30) |          |       | ADRESA / GRAD (slozeni atribut)           |
| `POSTANSKI_BROJ` | CHAR(5)     |          |       | ADRESA / POSTANSKI BROJ (slozeni atribut) |
| `KONTAKT_OSOBA`  | VARCHAR(60) |          |       | KONTAKT OSOBA                             |

### `OGLASIVAC`

*PMOV:* podtip KLIJENT -> OGLASIVAC

| Kolona            | Tip           | Obavezno | Kljuc             | Poreklo iz PMOV-a  |
|-------------------|---------------|----------|-------------------|--------------------|
| `SIFRA_KLIJENTA`  | CHAR(18)      | NOT NULL | PK, FK -> KLIJENT | PK = FK ka KLIJENT |
| `BRANSA`          | VARCHAR(60)   |          |                   | BRANSA             |
| `GODISNJI_BUDZET` | DECIMAL(12,2) |          |                   | GODISNJI BUDZET    |

### `KUPAC_SADRZAJA`

*PMOV:* podtip KLIJENT -> KUPAC SADRZAJA

| Kolona                  | Tip         | Obavezno | Kljuc             | Poreklo iz PMOV-a     |
|-------------------------|-------------|----------|-------------------|-----------------------|
| `SIFRA_KLIJENTA`        | CHAR(18)    | NOT NULL | PK, FK -> KLIJENT | PK = FK ka KLIJENT    |
| `TIP_MEDIJA`            | VARCHAR(30) |          |                   | TIP MEDIJA            |
| `TERITORIJA_EMITOVANJA` | VARCHAR(60) |          |                   | TERITORIJA EMITOVANJA |

### `UGOVOR`

*PMOV:* jak entitet UGOVOR (nadtip) + veza SKLAPA: KLIJENT (0,N) - UGOVOR (0,1)

| Kolona            | Tip           | Obavezno | Kljuc         | Poreklo iz PMOV-a                  |
|-------------------|---------------|----------|---------------|------------------------------------|
| `BROJ_UGOVORA`    | CHAR(18)      | NOT NULL | PK            | PK - BROJ UGOVORA                  |
| `SIFRA_KLIJENTA`  | CHAR(18)      |          | FK -> KLIJENT | FK - veza SKLAPA                   |
| `DATUM_SKLAPANJA` | DATE          |          |               | DATUM SKLAPANJA                    |
| `VAZI_OD`         | DATE          |          |               | VAZI OD                            |
| `VAZI_DO`         | DATE          |          |               | VAZI DO                            |
| `UKUPNA_VREDNOST` | DECIMAL(12,2) |          |               | UKUPNA VREDNOST - izvedeni atribut |
| `STATUS_UGOVORA`  | VARCHAR(20)   |          |               | STATUS UGOVORA                     |

### `STAVKA_UGOVORA`

*PMOV:* slab entitet STAVKA UGOVORA; identifikujuca veza PRECIZIRA: UGOVOR (1,N) - STAVKA (1,1)

| Kolona             | Tip           | Obavezno | Kljuc            | Poreklo iz PMOV-a                  |
|--------------------|---------------|----------|------------------|------------------------------------|
| `BROJ_UGOVORA`     | CHAR(18)      | NOT NULL | PK, FK -> UGOVOR | PK/FK - identifikujuci vlasnik     |
| `RB_STAVKE`        | INTEGER       | NOT NULL | PK               | PK - parcijalni kljuc RB STAVKE    |
| `OPIS_STAVKE`      | VARCHAR(255)  |          |                  | OPIS STAVKE                        |
| `KOLICINA_SEKUNDE` | INTEGER       |          |                  | KOLICINA / SEKUNDE                 |
| `JEDINICNA_CENA`   | DECIMAL(12,2) |          |                  | JEDINICNA CENA                     |
| `POPUST`           | DECIMAL(5,2)  |          |                  | POPUST                             |
| `VREDNOST_STAVKE`  | DECIMAL(12,2) |          |                  | VREDNOST STAVKE - izvedeni atribut |

### `UGOVOR_O_OGLASAVANJU`

*PMOV:* podtip UGOVOR -> UGOVOR O OGLASAVANJU

| Kolona              | Tip          | Obavezno | Kljuc            | Poreklo iz PMOV-a |
|---------------------|--------------|----------|------------------|-------------------|
| `BROJ_UGOVORA`      | CHAR(18)     | NOT NULL | PK, FK -> UGOVOR | PK = FK ka UGOVOR |
| `UGOVORENI_TERMINI` | VARCHAR(255) |          |                  | UGOVORENI TERMINI |

### `UGOVOR_O_PRODAJI_TV_SADRZAJA`

*PMOV:* podtip UGOVOR -> UGOVOR O PRODAJI TV SADRZAJA

| Kolona                   | Tip          | Obavezno | Kljuc            | Poreklo iz PMOV-a      |
|--------------------------|--------------|----------|------------------|------------------------|
| `BROJ_UGOVORA`           | CHAR(18)     | NOT NULL | PK, FK -> UGOVOR | PK = FK ka UGOVOR      |
| `PRENOS_VLASNISTVA`      | VARCHAR(20)  |          |                  | PRENOS VLASNISTVA      |
| `OBIM_USTUPLJENIH_PRAVA` | VARCHAR(255) |          |                  | OBIM USTUPLJENIH PRAVA |

### `UGOVOR_O_NABAVCI`

*PMOV:* podtip UGOVOR -> UGOVOR O NABAVCI + veza UGOVARA: DOBAVLJAC (0,N) - UGOVOR O NABAVCI (1,1)

| Kolona               | Tip          | Obavezno | Kljuc            | Poreklo iz PMOV-a  |
|----------------------|--------------|----------|------------------|--------------------|
| `BROJ_UGOVORA`       | CHAR(18)     | NOT NULL | PK, FK -> UGOVOR | PK = FK ka UGOVOR  |
| `SIFRA_DOBAVLJACA`   | CHAR(18)     | NOT NULL | FK -> DOBAVLJAC  | FK - veza UGOVARA  |
| `VRSTA_REKLAMIRANJA` | VARCHAR(30)  |          |                  | VRSTA REKLAMIRANJA |
| `ROK_ISPORUKE`       | DATE         |          |                  | ROK ISPORUKE       |
| `USLOVI_PLACANJA`    | VARCHAR(255) |          |                  | USLOVI PLACANJA    |

### `USTUPANJE_SADRZAJA`

*PMOV:* veza USTUPA: UGOVOR O PRODAJI TV SADRZAJA (1,N) - PRODUCIRANI SADRZAJ (0,N), sa atributima veze

| Kolona           | Tip           | Obavezno | Kljuc                                  | Poreklo iz PMOV-a                     |
|------------------|---------------|----------|----------------------------------------|---------------------------------------|
| `BROJ_UGOVORA`   | CHAR(18)      | NOT NULL | PK, FK -> UGOVOR_O_PRODAJI_TV_SADRZAJA | PK/FK ka UGOVOR_O_PRODAJI_TV_SADRZAJA |
| `SIFRA_SADRZAJA` | CHAR(18)      | NOT NULL | PK, FK -> PRODUCIRANI_SADRZAJ          | PK/FK ka PRODUCIRANI_SADRZAJ          |
| `UGOVORENA_CENA` | DECIMAL(12,2) |          |                                        | atribut veze UGOVORENA CENA           |
| `OBIM_USTUPANJA` | VARCHAR(255)  |          |                                        | atribut veze OBIM USTUPANJA           |

### `PLAN_NABAVKE`

*PMOV:* jak entitet PLAN NABAVKE

| Kolona            | Tip           | Obavezno | Kljuc | Poreklo iz PMOV-a                  |
|-------------------|---------------|----------|-------|------------------------------------|
| `SIFRA_PLANA`     | CHAR(18)      | NOT NULL | PK    | PK - SIFRA PLANA                   |
| `GODINA_PLANA`    | INTEGER       |          |       | GODINA PLANA                       |
| `DATUM_DONOSENJA` | DATE          |          |       | DATUM DONOSENJA                    |
| `STATUS_PLANA`    | VARCHAR(20)   |          |       | STATUS PLANA                       |
| `UKUPNA_VREDNOST` | DECIMAL(12,2) |          |       | UKUPNA VREDNOST - izvedeni atribut |
| `DONOSILAC_PLANA` | VARCHAR(60)   |          |       | DONOSILAC PLANA                    |

### `ZAHTEV_ZA_NABAVKU`

*PMOV:* jak entitet ZAHTEV ZA NABAVKU + PODNOSI: ORG. JEDINICA (0,N) - ZAHTEV (1,1) + UVRSTEN U: ZAHTEV (0,1) - PLAN (0,N)

| Kolona                | Tip           | Obavezno | Kljuc                        | Poreklo iz PMOV-a   |
|-----------------------|---------------|----------|------------------------------|---------------------|
| `BROJ_ZAHTEVA`        | CHAR(18)      | NOT NULL | PK                           | PK - BROJ ZAHTEVA   |
| `SIFRA_JEDINICE`      | CHAR(18)      | NOT NULL | FK -> ORGANIZACIONA_JEDINICA | FK - veza PODNOSI   |
| `SIFRA_PLANA`         | CHAR(18)      |          | FK -> PLAN_NABAVKE           | FK - veza UVRSTEN U |
| `DATUM_ZAHTEVA`       | DATE          |          |                              | DATUM ZAHTEVA       |
| `VRSTA_NABAVKE`       | VARCHAR(30)   |          |                              | VRSTA NABAVKE       |
| `PREDMET_ZAHTEVA`     | VARCHAR(255)  |          |                              | PREDMET ZAHTEVA     |
| `OBRAZLOZENJE`        | VARCHAR(255)  |          |                              | OBRAZLOZENJE        |
| `STATUS_ZAHTEVA`      | VARCHAR(20)   |          |                              | STATUS ZAHTEVA      |
| `PRIORITET`           | VARCHAR(20)   |          |                              | PRIORITET           |
| `PROCENJENA_VREDNOST` | DECIMAL(12,2) |          |                              | PROCENJENA VREDNOST |

### `STAVKA_PLANA_NABAVKE`

*PMOV:* slab entitet STAVKA PLANA NABAVKE; identifikujuca veza SADRZI STAVKE PLANA: PLAN (1,N) - STAVKA (1,1)

| Kolona              | Tip           | Obavezno | Kljuc                  | Poreklo iz PMOV-a               |
|---------------------|---------------|----------|------------------------|---------------------------------|
| `SIFRA_PLANA`       | CHAR(18)      | NOT NULL | PK, FK -> PLAN_NABAVKE | PK/FK - identifikujuci vlasnik  |
| `RB_STAVKE`         | INTEGER       | NOT NULL | PK                     | PK - parcijalni kljuc RB STAVKE |
| `OPIS_ARTIKLA`      | VARCHAR(255)  |          |                        | OPIS ARTIKLA                    |
| `KOLICINA`          | INTEGER       |          |                        | KOLICINA                        |
| `JEDINICA_MERE`     | VARCHAR(20)   |          |                        | JEDINICA MERE                   |
| `PROCENJENA_CENA`   | DECIMAL(12,2) |          |                        | PROCENJENA CENA                 |
| `PLANIRANI_KVARTAL` | VARCHAR(20)   |          |                        | PLANIRANI KVARTAL               |

### `DOBAVLJAC`

*PMOV:* jak entitet DOBAVLJAC (nadtip)

| Kolona             | Tip          | Obavezno | Kljuc | Poreklo iz PMOV-a                   |
|--------------------|--------------|----------|-------|-------------------------------------|
| `SIFRA_DOBAVLJACA` | CHAR(18)     | NOT NULL | PK    | PK - SIFRA DOBAVLJACA               |
| `NAZIV_DOBAVLJACA` | VARCHAR(60)  | NOT NULL |       | NAZIV DOBAVLJACA                    |
| `PIB`              | CHAR(9)      |          |       | PIB                                 |
| `MATICNI_BROJ`     | CHAR(8)      |          |       | MATICNI BROJ                        |
| `ADRESA`           | VARCHAR(60)  |          |       | ADRESA                              |
| `OCENA_DOBAVLJACA` | DECIMAL(5,2) |          |       | OCENA DOBAVLJACA - izvedeni atribut |

### `DOBAVLJAC_TV_SADRZAJA`

*PMOV:* podtip DOBAVLJAC -> DOBAVLJAC TV SADRZAJA

| Kolona             | Tip          | Obavezno | Kljuc               | Poreklo iz PMOV-a    |
|--------------------|--------------|----------|---------------------|----------------------|
| `SIFRA_DOBAVLJACA` | CHAR(18)     | NOT NULL | PK, FK -> DOBAVLJAC | PK = FK ka DOBAVLJAC |
| `VRSTA_SADRZAJA`   | VARCHAR(30)  |          |                     | VRSTA SADRZAJA       |
| `KATALOG_PONUDE`   | VARCHAR(255) |          |                     | KATALOG PONUDE       |

### `DOBAVLJAC_OPREME_I_MATERIJALA`

*PMOV:* podtip DOBAVLJAC -> DOBAVLJAC OPREME I MATERIJALA

| Kolona             | Tip          | Obavezno | Kljuc               | Poreklo iz PMOV-a    |
|--------------------|--------------|----------|---------------------|----------------------|
| `SIFRA_DOBAVLJACA` | CHAR(18)     | NOT NULL | PK, FK -> DOBAVLJAC | PK = FK ka DOBAVLJAC |
| `ASORTIMAN`        | VARCHAR(255) |          |                     | ASORTIMAN            |
| `OVLASCENI_SERVIS` | VARCHAR(20)  |          |                     | OVLASCENI SERVIS     |

### `PONUDA_DOBAVLJACA`

*PMOV:* jak entitet PONUDA DOBAVLJACA + veza DOSTAVIO: DOBAVLJAC (0,N) - PONUDA (1,1)

| Kolona             | Tip           | Obavezno | Kljuc           | Poreklo iz PMOV-a                |
|--------------------|---------------|----------|-----------------|----------------------------------|
| `BROJ_PONUDE`      | CHAR(18)      | NOT NULL | PK              | PK - BROJ PONUDE                 |
| `SIFRA_DOBAVLJACA` | CHAR(18)      | NOT NULL | FK -> DOBAVLJAC | FK - veza DOSTAVIO               |
| `DATUM_PRIJEMA`    | DATE          |          |                 | DATUM PRIJEMA                    |
| `VAZI_DO`          | DATE          |          |                 | VAZI DO                          |
| `UKUPNA_CENA`      | DECIMAL(12,2) |          |                 | UKUPNA CENA                      |
| `ROK_ISPORUKE`     | DATE          |          |                 | ROK ISPORUKE                     |
| `USLOVI_PLACANJA`  | VARCHAR(255)  |          |                 | USLOVI PLACANJA                  |
| `STATUS_PONUDE`    | VARCHAR(20)   |          |                 | STATUS PONUDE                    |
| `UKUPNO_BODOVA`    | DECIMAL(5,2)  |          |                 | UKUPNO BODOVA - izvedeni atribut |

### `PONUDJENA_STAVKA`

*PMOV:* veza PONUDJENA: STAVKA PLANA NABAVKE (0,N) - PONUDA DOBAVLJACA (0,N), sa atributima veze

| Kolona           | Tip           | Obavezno | Kljuc                          | Poreklo iz PMOV-a             |
|------------------|---------------|----------|--------------------------------|-------------------------------|
| `SIFRA_PLANA`    | CHAR(18)      | NOT NULL | PK, FK -> STAVKA_PLANA_NABAVKE | PK/FK ka STAVKA_PLANA_NABAVKE |
| `RB_STAVKE`      | INTEGER       | NOT NULL | PK, FK -> STAVKA_PLANA_NABAVKE | PK/FK ka STAVKA_PLANA_NABAVKE |
| `BROJ_PONUDE`    | CHAR(18)      | NOT NULL | PK, FK -> PONUDA_DOBAVLJACA    | PK/FK ka PONUDA_DOBAVLJACA    |
| `PONUDJENA_CENA` | DECIMAL(12,2) |          |                                | atribut veze PONUDJENA CENA   |
| `ROK_ZA_STAVKU`  | DATE          |          |                                | atribut veze ROK ZA STAVKU    |

### `KRITERIJUM_VREDNOVANJA`

*PMOV:* jak entitet KRITERIJUM VREDNOVANJA

| Kolona              | Tip          | Obavezno | Kljuc | Poreklo iz PMOV-a      |
|---------------------|--------------|----------|-------|------------------------|
| `SIFRA_KRITERIJUMA` | CHAR(18)     | NOT NULL | PK    | PK - SIFRA KRITERIJUMA |
| `NAZIV_KRITERIJUMA` | VARCHAR(60)  | NOT NULL |       | NAZIV KRITERIJUMA      |
| `NACIN_BODOVANJA`   | VARCHAR(60)  |          |       | NACIN BODOVANJA        |
| `OPIS_KRITERIJUMA`  | VARCHAR(255) |          |       | OPIS KRITERIJUMA       |

### `OCENA_PONUDE`

*PMOV:* veza VREDNUJE SE: PONUDA DOBAVLJACA (1,N) - KRITERIJUM VREDNOVANJA (1,N), sa atributima veze

| Kolona              | Tip          | Obavezno | Kljuc                            | Poreklo iz PMOV-a               |
|---------------------|--------------|----------|----------------------------------|---------------------------------|
| `BROJ_PONUDE`       | CHAR(18)     | NOT NULL | PK, FK -> PONUDA_DOBAVLJACA      | PK/FK ka PONUDA_DOBAVLJACA      |
| `SIFRA_KRITERIJUMA` | CHAR(18)     | NOT NULL | PK, FK -> KRITERIJUM_VREDNOVANJA | PK/FK ka KRITERIJUM_VREDNOVANJA |
| `BROJ_BODOVA`       | DECIMAL(5,2) |          |                                  | atribut veze BROJ BODOVA        |
| `KOMENTAR_OCENE`    | VARCHAR(255) |          |                                  | atribut veze KOMENTAR OCENE     |

### `NARUDZBENICA`

*PMOV:* jak entitet NARUDZBENICA + veza NARUCENO OD: DOBAVLJAC (0,N) - NARUDZBENICA (1,1)

| Kolona              | Tip           | Obavezno | Kljuc           | Poreklo iz PMOV-a               |
|---------------------|---------------|----------|-----------------|---------------------------------|
| `BROJ_NARUDZBENICE` | CHAR(18)      | NOT NULL | PK              | PK - BROJ NARUDZBENICE          |
| `SIFRA_DOBAVLJACA`  | CHAR(18)      | NOT NULL | FK -> DOBAVLJAC | FK - veza NARUCENO OD           |
| `DATUM_IZDAVANJA`   | DATE          |          |                 | DATUM IZDAVANJA                 |
| `ROK_ISPORUKE`      | DATE          |          |                 | ROK ISPORUKE                    |
| `MESTO_ISPORUKE`    | VARCHAR(60)   |          |                 | MESTO ISPORUKE                  |
| `UKUPAN_IZNOS`      | DECIMAL(12,2) |          |                 | UKUPAN IZNOS - izvedeni atribut |
| `STATUS_NARUDZBINE` | VARCHAR(20)   |          |                 | STATUS NARUDZBINE               |

### `STAVKA_NARUDZBENICE`

*PMOV:* slab entitet STAVKA NARUDZBENICE; identifikujuca veza SADRZI STAVKE NARUDZBINE: NARUDZBENICA (1,N) - STAVKA (1,1)

| Kolona              | Tip           | Obavezno | Kljuc                  | Poreklo iz PMOV-a                  |
|---------------------|---------------|----------|------------------------|------------------------------------|
| `BROJ_NARUDZBENICE` | CHAR(18)      | NOT NULL | PK, FK -> NARUDZBENICA | PK/FK - identifikujuci vlasnik     |
| `RB_STAVKE`         | INTEGER       | NOT NULL | PK                     | PK - parcijalni kljuc RB STAVKE    |
| `NAZIV_ARTIKLA`     | VARCHAR(60)   |          |                        | NAZIV ARTIKLA                      |
| `KOLICINA`          | INTEGER       |          |                        | KOLICINA                           |
| `JEDINICNA_CENA`    | DECIMAL(12,2) |          |                        | JEDINICNA CENA                     |
| `STATUS_STAVKE`     | VARCHAR(20)   |          |                        | STATUS STAVKE                      |
| `VREDNOST_STAVKE`   | DECIMAL(12,2) |          |                        | VREDNOST STAVKE - izvedeni atribut |

### `PRIJEMNICA`

*PMOV:* jak entitet PRIJEMNICA + PRACENA: NARUDZBENICA (0,N) - PRIJEMNICA (1,1) + FAKTURISANA: PRIJEMNICA (0,1) - FAKTURA (0,N)

| Kolona                | Tip          | Obavezno | Kljuc              | Poreklo iz PMOV-a     |
|-----------------------|--------------|----------|--------------------|-----------------------|
| `BROJ_PRIJEMNICE`     | CHAR(18)     | NOT NULL | PK                 | PK - BROJ PRIJEMNICE  |
| `BROJ_NARUDZBENICE`   | CHAR(18)     | NOT NULL | FK -> NARUDZBENICA | FK - veza PRACENA     |
| `BROJ_FAKTURE`        | CHAR(18)     |          | FK -> FAKTURA      | FK - veza FAKTURISANA |
| `DATUM_PRIJEMA`       | DATE         |          |                    | DATUM PRIJEMA         |
| `BROJ_OTPREMNICE`     | VARCHAR(30)  |          |                    | BROJ OTPREMNICE       |
| `PRIMIO_MAGACIONER`   | VARCHAR(60)  |          |                    | PRIMIO (MAGACIONER)   |
| `ISPRAVNOST_ISPORUKE` | VARCHAR(20)  |          |                    | ISPRAVNOST ISPORUKE   |
| `NAPOMENA`            | VARCHAR(255) |          |                    | NAPOMENA              |

### `PRIJEM_STAVKE`

*PMOV:* veza PRIMLJENO PO: PRIJEMNICA (1,N) - STAVKA NARUDZBENICE (0,N), sa atributima veze

| Kolona                 | Tip          | Obavezno | Kljuc                         | Poreklo iz PMOV-a                 |
|------------------------|--------------|----------|-------------------------------|-----------------------------------|
| `BROJ_PRIJEMNICE`      | CHAR(18)     | NOT NULL | PK, FK -> PRIJEMNICA          | PK/FK ka PRIJEMNICA               |
| `BROJ_NARUDZBENICE`    | CHAR(18)     | NOT NULL | PK, FK -> STAVKA_NARUDZBENICE | PK/FK ka STAVKA_NARUDZBENICE      |
| `RB_STAVKE`            | INTEGER      | NOT NULL | PK, FK -> STAVKA_NARUDZBENICE | PK/FK ka STAVKA_NARUDZBENICE      |
| `PRIMLJENA_KOLICINA`   | INTEGER      |          |                               | atribut veze PRIMLJENA KOLICINA   |
| `UTVRDJENO_ODSTUPANJE` | VARCHAR(255) |          |                               | atribut veze UTVRDJENO ODSTUPANJE |

### `REKLAMACIJA`

*PMOV:* jak entitet REKLAMACIJA + veza REKLAMIRANA: PRIJEMNICA (0,N) - REKLAMACIJA (1,1)

| Kolona               | Tip           | Obavezno | Kljuc            | Poreklo iz PMOV-a     |
|----------------------|---------------|----------|------------------|-----------------------|
| `BROJ_REKLAMACIJE`   | CHAR(18)      | NOT NULL | PK               | PK - BROJ REKLAMACIJE |
| `BROJ_PRIJEMNICE`    | CHAR(18)      | NOT NULL | FK -> PRIJEMNICA | FK - veza REKLAMIRANA |
| `DATUM_REKLAMACIJE`  | DATE          |          |                  | DATUM REKLAMACIJE     |
| `RAZLOG_REKLAMACIJE` | VARCHAR(60)   |          |                  | RAZLOG REKLAMACIJE    |
| `OPIS_NEDOSTATKA`    | VARCHAR(255)  |          |                  | OPIS NEDOSTATKA       |
| `STATUS_REKLAMACIJE` | VARCHAR(20)   |          |                  | STATUS REKLAMACIJE    |
| `DATUM_RESENJA`      | DATE          |          |                  | DATUM RESENJA         |
| `REKLAMIRANI_IZNOS`  | DECIMAL(12,2) |          |                  | REKLAMIRANI IZNOS     |
| `NACIN_RESAVANJA`    | VARCHAR(60)   |          |                  | NACIN RESAVANJA       |

### `REKLAMIRANA_STAVKA`

*PMOV:* veza ODNOSI SE NA: REKLAMACIJA (1,N) - STAVKA NARUDZBENICE (0,N)

| Kolona              | Tip      | Obavezno | Kljuc                         | Poreklo iz PMOV-a            |
|---------------------|----------|----------|-------------------------------|------------------------------|
| `BROJ_REKLAMACIJE`  | CHAR(18) | NOT NULL | PK, FK -> REKLAMACIJA         | PK/FK ka REKLAMACIJA         |
| `BROJ_NARUDZBENICE` | CHAR(18) | NOT NULL | PK, FK -> STAVKA_NARUDZBENICE | PK/FK ka STAVKA_NARUDZBENICE |
| `RB_STAVKE`         | INTEGER  | NOT NULL | PK, FK -> STAVKA_NARUDZBENICE | PK/FK ka STAVKA_NARUDZBENICE |

### `FAKTURA`

*PMOV:* jak entitet FAKTURA + veza IZDATA PO: UGOVOR (0,N) - FAKTURA (0,1)

| Kolona              | Tip           | Obavezno | Kljuc        | Poreklo iz PMOV-a                    |
|---------------------|---------------|----------|--------------|--------------------------------------|
| `BROJ_FAKTURE`      | CHAR(18)      | NOT NULL | PK           | PK - BROJ FAKTURE                    |
| `BROJ_UGOVORA`      | CHAR(18)      |          | FK -> UGOVOR | FK - veza IZDATA PO                  |
| `DATUM_IZDAVANJA`   | DATE          |          |              | DATUM IZDAVANJA                      |
| `ROK_PLACANJA`      | DATE          |          |              | ROK PLACANJA                         |
| `SMER`              | VARCHAR(20)   |          |              | SMER (ULAZNA/IZLAZNA)                |
| `OSNOVICA`          | DECIMAL(12,2) |          |              | OSNOVICA - izvedeni atribut          |
| `IZNOS_PDV`         | DECIMAL(12,2) |          |              | IZNOS PDV - izvedeni atribut         |
| `STATUS_PLACANJA`   | VARCHAR(20)   |          |              | STATUS PLACANJA                      |
| `IZNOS_ZA_PLACANJE` | DECIMAL(12,2) |          |              | IZNOS ZA PLACANJE - izvedeni atribut |

### `STAVKA_FAKTURE`

*PMOV:* slab entitet STAVKA FAKTURE; identifikujuca veza SADRZI STAVKE FAKTURE: FAKTURA (1,N) - STAVKA (1,1)

| Kolona            | Tip           | Obavezno | Kljuc             | Poreklo iz PMOV-a                  |
|-------------------|---------------|----------|-------------------|------------------------------------|
| `BROJ_FAKTURE`    | CHAR(18)      | NOT NULL | PK, FK -> FAKTURA | PK/FK - identifikujuci vlasnik     |
| `RB_STAVKE`       | INTEGER       | NOT NULL | PK                | PK - parcijalni kljuc RB STAVKE    |
| `OPIS_STAVKE`     | VARCHAR(255)  |          |                   | OPIS STAVKE                        |
| `KOLICINA`        | INTEGER       |          |                   | KOLICINA                           |
| `JEDINICNA_CENA`  | DECIMAL(12,2) |          |                   | JEDINICNA CENA                     |
| `STOPA_PDV`       | DECIMAL(5,2)  |          |                   | STOPA PDV                          |
| `VREDNOST_STAVKE` | DECIMAL(12,2) |          |                   | VREDNOST STAVKE - izvedeni atribut |

### `NALOG_ZA_PLACANJE`

*PMOV:* jak entitet NALOG ZA PLACANJE + veza PLACENA: FAKTURA (0,N) - NALOG (1,1)

| Kolona              | Tip           | Obavezno | Kljuc         | Poreklo iz PMOV-a |
|---------------------|---------------|----------|---------------|-------------------|
| `BROJ_NALOGA`       | CHAR(18)      | NOT NULL | PK            | PK - BROJ NALOGA  |
| `BROJ_FAKTURE`      | CHAR(18)      | NOT NULL | FK -> FAKTURA | FK - veza PLACENA |
| `DATUM_NALOGA`      | DATE          |          |               | DATUM NALOGA      |
| `IZNOS_NALOGA`      | DECIMAL(12,2) |          |               | IZNOS NALOGA      |
| `SVRHA_PLACANJA`    | VARCHAR(255)  |          |               | SVRHA PLACANJA    |
| `DATUM_REALIZACIJE` | DATE          |          |               | DATUM REALIZACIJE |
| `STATUS_NALOGA`     | VARCHAR(20)   |          |               | STATUS NALOGA     |
| `RACUN_PRIMAOCA`    | VARCHAR(30)   |          |               | RACUN PRIMAOCA    |
| `ODOBRIO`           | VARCHAR(60)   |          |               | ODOBRIO           |

