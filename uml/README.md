# UML dijagrami aktivnosti — informacioni sistem TV stanice

Tri dijagrama aktivnosti za procese koji su nosivi u ovom projektu i koji su već
modelovani u PMOV-u i ER šemi: **nabavka**, **produkcija** i **emitovanje**.
Svaka aktivnost na dijagramima vezuje se za konkretan entitet, atribut ili vezu iz
`PMOV_TV_stanica_2_1_1.vsdx` odnosno iz `er/ER_TV_stanica.sql` — tabele u odeljku
„Traživost" ispod.

| Fajl | Sadržaj |
|------|---------|
| `DA_TV_stanica.drawio` | sva tri dijagrama, svaki na svom listu — otvara se na app.diagrams.net ili u draw.io desktop aplikaciji |
| `DA_1_nabavka.png` | Nabavka opreme i materijala |
| `DA_2_produkcija.png` | Produkcija emisije |
| `DA_3_emitovanje.png` | Planiranje šeme i emitovanje programa |
| `generator/` | `act.py` (okvir: model → .drawio + .png), `d1..d3_*.py` (dijagrami), `build_all.py` |

## Korišćena notacija

| Simbol | Značenje |
|--------|----------|
| pun crn krug | početni čvor (*initial node*) |
| krug u prstenu | završni čvor (*activity final node*) |
| zaobljeni pravougaonik | akcija (*action*) |
| romb | odluka / spajanje toka (*decision / merge*), grane označene `Da` / `Ne` |
| debela crna traka | račvanje i spajanje paralelnih tokova (*fork* / *join*) |
| vertikalne trake sa zaglavljem | particije odgovornosti (*swimlanes*) |

Napomena: na primerima koje ste poslali početni čvor je nacrtan kao **šupalj** krug.
Po UML standardu je pun, pa je ovde tako i nacrtan. Ako profesor traži kao na primerima,
to je jedna izmena u `generator/act.py` (stil `start`) i regeneriše se za minut.

## Traživost — dijagram 1: Nabavka opreme i materijala

Particije: `Organizaciona jedinica` · `Referent nabavke` · `Dobavljač` · `Finansijska služba`

| Aktivnost / odluka | PMOV entitet i veza | ER tabela / kolona |
|---|---|---|
| Podnošenje zahteva za nabavku | ZAHTEV ZA NABAVKU; veza **PODNOSI** (ORG. JEDINICA 0,N – ZAHTEV 1,1) | `ZAHTEV_ZA_NABAVKU.SIFRA_JEDINICE` |
| Provera zahteva i procenjene vrednosti | ZAHTEV.PROCENJENA VREDNOST; REFERENT.NIVO OVLAŠĆENJA | `ZAHTEV_ZA_NABAVKU.PROCENJENA_VREDNOST`, `REFERENT.NIVO_OVLASCENJA` |
| *Zahtev je odobren?* | ZAHTEV.STATUS ZAHTEVA | `ZAHTEV_ZA_NABAVKU.STATUS_ZAHTEVA` |
| Uvrštavanje stavke u plan nabavke | PLAN NABAVKE, STAVKA PLANA NABAVKE; veza **UVRŠTEN U** | `ZAHTEV_ZA_NABAVKU.SIFRA_PLANA`, `STAVKA_PLANA_NABAVKE` |
| Slanje poziva dobavljačima | DOBAVLJAČ (podtip DOBAVLJAČ OPREME I MATERIJALA) | `DOBAVLJAC`, `DOBAVLJAC_OPREME_I_MATERIJALA` |
| Dostavljanje ponude | PONUDA DOBAVLJAČA; veze **DOSTAVIO**, **PONUĐENA** | `PONUDA_DOBAVLJACA.SIFRA_DOBAVLJACA`, `PONUDJENA_STAVKA` |
| Vrednovanje ponuda po kriterijumima | KRITERIJUM VREDNOVANJA; veza **VREDNUJE SE** (BROJ BODOVA) | `OCENA_PONUDE.BROJ_BODOVA` |
| *Ponuda je prihvatljiva?* | PONUDA.STATUS PONUDE, UKUPNO BODOVA | `PONUDA_DOBAVLJACA.STATUS_PONUDE` |
| Izdavanje narudžbenice | NARUDŽBENICA, STAVKA NARUDŽBENICE; veza **NARUČENO OD** | `NARUDZBENICA.SIFRA_DOBAVLJACA` |
| Isporuka artikala po narudžbenici | STAVKA NARUDŽBENICE.STATUS STAVKE | `STAVKA_NARUDZBENICE.STATUS_STAVKE` |
| Prijem robe i izrada prijemnice | PRIJEMNICA; veze **PRAĆENA**, **PRIMLJENO PO** | `PRIJEMNICA.BROJ_NARUDZBENICE`, `PRIJEM_STAVKE` |
| *Isporuka je ispravna?* | PRIJEMNICA.ISPRAVNOST ISPORUKE | `PRIJEMNICA.ISPRAVNOST_ISPORUKE` |
| Podnošenje reklamacije dobavljaču | REKLAMACIJA; veze **REKLAMIRANA**, **ODNOSI SE NA** | `REKLAMACIJA`, `REKLAMIRANA_STAVKA` |
| Knjiženje ulazne fakture | FAKTURA (SMER = ULAZNA); veza **FAKTURISANA** | `PRIJEMNICA.BROJ_FAKTURE`, `FAKTURA.SMER` |
| Izdavanje naloga za plaćanje | NALOG ZA PLAĆANJE; veza **PLAĆENA** | `NALOG_ZA_PLACANJE.BROJ_FAKTURE` |
| Evidentiranje realizacije plaćanja | NALOG.DATUM REALIZACIJE; FAKTURA.STATUS PLAĆANJA | `NALOG_ZA_PLACANJE.DATUM_REALIZACIJE` |

## Traživost — dijagram 2: Produkcija emisije

Particije: `Urednik` · `Produkcijska ekipa` · `Tehnička služba`

| Aktivnost / odluka | PMOV entitet i veza | ER tabela / kolona |
|---|---|---|
| Predlog projekta produkcije | PROJEKAT PRODUKCIJE | `PROJEKAT_PRODUKCIJE` |
| *Projekat je odobren?* | veza **UREĐUJE** (UREDNIK 0,N – PROJEKAT 1,1); ODOBREN BUDŽET | `PROJEKAT_PRODUKCIJE.SIFRA_UREDNIKA`, `.ODOBREN_BUDZET` |
| Definisanje aktivnosti i budžeta | AKTIVNOST PRODUKCIJE (slab entitet); veza **SASTOJI SE OD** | `AKTIVNOST_PRODUKCIJE(SIFRA_PROJEKTA, RB_AKTIVNOSTI)` |
| Angažovanje članova ekipe *(paralelno)* | veza **ANGAŽUJE** (ULOGA NA SNIMANJU, BROJ ANGAŽOVANIH SATI) | `ANGAZOVANJE_NA_AKTIVNOSTI` |
| Zaduživanje i rezervacija opreme *(paralelno)* | OPREMA; veza **ZADUŽUJE** (DATUM REZERVACIJE, TRAJANJE ZADUŽENJA) | `REZERVACIJA_OPREME` |
| Snimanje po planu aktivnosti | AKTIVNOST.LOKACIJA SNIMANJA, STATUS AKTIVNOSTI | `AKTIVNOST_PRODUKCIJE.LOKACIJA_SNIMANJA` |
| Evidentiranje sirovih snimaka | SIROVI SNIMAK; veza **SNIMLJEN NA** | `SIROVI_SNIMAK.(SIFRA_PROJEKTA, RB_AKTIVNOSTI)` |
| *Kvalitet snimka je prihvatljiv?* | SIROVI SNIMAK.OCENA KVALITETA | `SIROVI_SNIMAK.OCENA_KVALITETA` |
| Montaža medijskog sadržaja | MEDIJSKI SADRŽAJ / PRODUCIRANI SADRŽAJ; veza **MONTIRAN U** | `MONTAZA_SNIMKA`, `PRODUCIRANI_SADRZAJ` |
| Ugradnja grafičkih i muzičkih elemenata | GRAFIČKI I MUZIČKI ELEMENT; veza **UGRAĐEN U** | `UGRADNJA_ELEMENTA.VREME_POJAVLJIVANJA` |
| Kontrola i prihvatanje sadržaja | UREDNIK; PRODUCIRANI SADRŽAJ.VERZIJA MASTERA | `PRODUCIRANI_SADRZAJ.VERZIJA_MASTERA` |
| *Sadržaj je prihvaćen?* | isto — vraćanje na montažu ako nije | — |
| Evidentiranje troškova produkcije | TROŠAK PRODUKCIJE; veze **IZAZIVA**, **DOKUMENTOVAN** | `TROSAK_PRODUKCIJE`, `.BROJ_FAKTURE` |
| Arhiviranje medijskog sadržaja | MEDIJSKI SADRŽAJ.DATUM ARHIVIRANJA, LOKACIJA U ARHIVI | `MEDIJSKI_SADRZAJ.DATUM_ARHIVIRANJA` |

## Traživost — dijagram 3: Planiranje šeme i emitovanje programa

Particije: `Urednik programa` · `Marketing i prodaja` · `Tehnička služba`

| Aktivnost / odluka | PMOV entitet i veza | ER tabela / kolona |
|---|---|---|
| Izrada programske šeme | PROGRAMSKA ŠEMA | `PROGRAMSKA_SEMA` |
| Raspoređivanje celina i termina emitovanja | PROGRAMSKA CELINA (**SADRŽI CELINE**), TERMIN EMITOVANJA (**OBUHVATA**, **PLANIRANA**) | `PROGRAMSKA_CELINA`, `TERMIN_EMITOVANJA` |
| *Postoji važeće pravo korišćenja?* | PRAVO KORIŠĆENJA (DATUM OD/DO, DOZVOLJENO / ISKORIŠĆENO EMITOVANJA); veza **POKRIVA** | `PRAVO_KORISCENJA`, `POKRIVENOST_PRAVOM` |
| Odobravanje programske šeme | veza **ODOBRAVA** (UREDNIK 0,N – ŠEMA 1,1); DATUM USVAJANJA | `PROGRAMSKA_SEMA.SIFRA_UREDNIKA`, `.DATUM_USVAJANJA` |
| Zakup reklamnog bloka u terminu *(paralelno)* | REKLAMNI BLOK (**ZAKUPLJEN U**, **TARIFIRAN**), EMITOVANJE REKLAME (**SADRŽI SPOT**, **UGOVOREN**) | `REKLAMNI_BLOK`, `EMITOVANJE_REKLAME` |
| Priprema tehničkih resursa za emitovanje *(paralelno)* | STUDIJSKA I EMISIONA OPREMA; TEHNIČKO OSOBLJE | `STUDIJSKA_I_EMISIONA_OPREMA`, `TEHNICKO_OSOBLJE` |
| Emitovanje po programskoj šemi | TERMIN EMITOVANJA.STATUS TERMINA | `TERMIN_EMITOVANJA.STATUS_TERMINA` |
| *Emitovanje bez smetnji?* | ZAPIS O EMITOVANJU.STATUS REALIZACIJE | `ZAPIS_O_EMITOVANJU.STATUS_REALIZACIJE` |
| Upis napomene o smetnjama | ZAPIS O EMITOVANJU.NAPOMENA O SMETNJAMA | `ZAPIS_O_EMITOVANJU.NAPOMENA_O_SMETNJAMA` |
| Kreiranje zapisa o emitovanju | ZAPIS O EMITOVANJU (slab entitet); veze **REALIZOVAN**, **EVIDENTIRA** | `ZAPIS_O_EMITOVANJU(SIFRA_TERMINA, RB_EMITOVANJA)` |
| Naplata emitovanih reklamnih spotova | EMITOVANJE REKLAME.NAPLAĆENI IZNOS, STATUS NAPLATE; FAKTURA (**IZDATA PO**) | `EMITOVANJE_REKLAME.NAPLACENI_IZNOS`, `FAKTURA.BROJ_UGOVORA` |
| Preuzimanje rezultata merenja gledanosti | MERENJE GLEDANOSTI; veza **MERENA** (OSTVARENI RATING, UDEO U TERMINU) | `MERENJE_EMISIJE` |
| Izrada izveštaja o realizaciji šeme | izvedeno iz ZAPIS O EMITOVANJU i MERENJE GLEDANOSTI | — |

## Provere

* sva tri dijagrama su generisana iz istog modela iz kog se crta i `.png` i `.drawio`,
  pa su slike i fajl za uređivanje uvek identični;
* svaki prelaz je u `.drawio` fajlu **zakačen za oba čvora** (provereno automatski:
  nema slobodnih krajeva), pa se pomeranjem kutije veza pomera s njom;
* XML `.drawio` fajla je proveren parserom.
