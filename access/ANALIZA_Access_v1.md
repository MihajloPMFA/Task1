# Analiza baze Access_v1.accdb

Analiza je urađena čitanjem samog `.accdb` fajla (sistemska tabela
`MSysObjects` i definicije tabela), pa su brojevi ispod izmereni, ne procenjeni.
Snimak strukture je u `sema_accdb.json`.

## Šta baza sadrži

| Objekat | Broj | Napomena |
|---|---|---|
| tabele | 69 | 405 kolona ukupno |
| veze | 84 | sve sa referencijalnim integritetom |
| forme | 70 | po jedna za svaku tabelu + `PlayoutLog` |
| upiti | 16 | vidi ispod |
| izveštaji | 6 | `AKTIVNOST_PRODUKCIJE`, `AKTIVNOST_PRODUKCIJE1`, `EMISIJA`, `Izvestaj3`, `qryGledanostPoZanru`, `qryPlayoutLog` |
| VBA moduli | 0 | baza nema kod |
| redovi podataka | 1880 | u svih 69 tabela |

## Struktura odgovara ER modelu

Uporedio sam sve tabele i kolone sa ER šemom projekta
(`er/generator/schema.py`, odnosno `er/ER_TV_stanica.sql`):

- **69 tabela** — identična imena, bez razlike
- **405 kolona** — identična imena u svim tabelama
- **84 veze** — identična imena (`FK_AKTIVNOST_PROJEKAT`, `FK_ANGAZ_ZAPOSLENI`, ...)

Jedina razlika je **redosled kolona** u fizičkom zapisu: Access interno
premešta polja fiksne dužine (datumi, brojevi) pre tekstualnih. To nije
promena šeme i ne utiče ni na jedan upit.

## Forme

Sve tabele imaju svoju formu. Imena su u obliku `Naziv_tabele`
(`Organizaciona_jedinica`, `Termin_emitovanja`, ...). Dve forme se ne
poklapaju sa imenom tabele:

- `Serveri` — po svemu sudeći forma za tabelu `SERVISERI` (jedina tabela
  bez forme istog imena)
- `PlayoutLog` — forma nad upitom `qryPlayoutLog`, nije vezana za tabelu

## Upiti

Postoji 16 upita:

```
  Izvestaj1
  Izvestaj3
  qryAngazovanje
  qryFaktureINalozi
  qryGledanostEmisija
  qryGledanostPoZanru
  qryKarticaOglasivaca
  qryKarticaOpreme
  qryPlanNabavke
  qryPlayoutLog
  qryPravaKoriscenja
  qryProgramskaSema
  qryTroskoviProjekta
  qryVrednovanjePonuda
  qryZaduzenjeOpreme
  qryZaposleniPoJedinicama
```

Access ne čuva tekst SQL-a u fajlu u čitljivom obliku (upiti su zapisani u
prevedenoj formi), pa **nisam mogao da pročitam njihov sadržaj**. Zato se
novi izveštaji ne oslanjaju na njih — dobili su svoje upite (vidi ispod).

## Šta je nedostajalo za izveštaje

Iz Specifikacije izveštaja traži se osam izveštaja (2 parametarska, 1 sa
grafičkim prikazom). U bazi postoji šest izveštaja, ali nijedan ne odgovara
specifikaciji:

| Izveštaj u bazi | Šta je |
|---|---|
| `AKTIVNOST_PRODUKCIJE`, `AKTIVNOST_PRODUKCIJE1`, `EMISIJA` | čarobnjakom napravljeni spiskovi jedne tabele |
| `Izvestaj3`, `qryGledanostPoZanru`, `qryPlayoutLog` | započeti izveštaji nad istoimenim upitima |

Nijedan nema grupisanje po celini iz specifikacije, zbirove, parametre,
grafikon ni podizveštaje. Dakle: **trebalo je dodati svih osam.**

## Šta dodaje `TV_Stanica_Izvestaji.bas`

Modul `modIzvestaji` dodaje **samo nove objekte**, sa prefiksima koji se ne
poklapaju sa ni jednim postojećim imenom u bazi:

| Prefiks | Broj | Šta je |
|---|---|---|
| `qIzv...` | 16 | upiti - izvor podataka za izveštaje (12 glavnih + 4 pomoćna) |
| `rptIzv1` - `rptIzv8` | 8 | izveštaji iz specifikacije |
| `rptIzv5_Oprema`, `rptIzv7_Ponude` | 2 | podizveštaji |
| `frmIzvestaji` | 1 | forma-meni sa dugmadima za svih osam izveštaja |

### Zašto novi upiti, a ne postojeći `qry...`

Tri razloga:

1. Sadržaj postojećih upita se ne može pročitati iz fajla, pa ne mogu da
   garantujem da vraćaju polja koja izveštaji traže.
2. Izveštaji iz specifikacije traže i izvedene kolone kojih u ranijim
   upitima nije bilo — odstupanje stvarnog od planiranog trajanja, dani do
   isteka prava, status prava, ključeve za grupisanje, ugovoreno vs.
   realizovano po ugovoru, iznos narudžbenice po stavci plana.
3. Tako se **ništa postojeće ne menja** — ni tabele, ni forme, ni tvoji upiti.

Procedure koje brišu (`ObrisiUpit`, `ObrisiIzvestaj`, `ObrisiFormu`) proveravaju
prefiks imena i odbijaju sve što nije `qIzv`/`rptIzv`/`frmIzvestaji`, pa
ponovno pokretanje ne može da obriše ništa tuđe.

## Osam izveštaja - šta je u svakom

| # | Izveštaj | Izvor | Grupisanje | Zbirovi i posebno |
|---|---|---|---|---|
| 1 | `rptIzv1` Programska šema sa terminima emitovanja | `qIzv1_Sema` | šema → programska celina | minuti i broj termina po celini, po šemi i ukupno; u zaglavlju grupe naziv i sezona šeme, period važenja, verzija, status i urednik |
| 2 | `rptIzv2` Evidencija emitovanog sadržaja (playout log) | `qIzv2_Playout` **parametarski** | datum | po danu: zbir stvarnih minuta, broj emitovanja i broj emitovanja sa zabeleženim smetnjama; kolona odstupanja stvarnog od planiranog trajanja |
| 3 | `rptIzv3` Gledanost emisija po žanru | `qIzv3_Emisije` | — | **dva grafikona** (prosečan rejting po žanru i kretanje rejtinga po datumu merenja) + prateća tabela sortirana opadajuće po rejtingu; u zaglavlju period merenja, izvori i ciljne grupe |
| 4 | `rptIzv4` Realizacija i troškovi projekta produkcije | `qIzv4_Troskovi` | projekat → aktivnost | zbir troškova po aktivnosti, po projektu i ukupno, uz **procenat iskorišćenja odobrenog budžeta** |
| 5 | `rptIzv5` Angažovanje zaposlenih i zaduženje opreme | `qIzv5_Angazovanje` | zaposleni | sati i broj angažovanja po zaposlenom i ukupno; **drugi deo** je podizveštaj `rptIzv5_Oprema` sa danima zaduženja po komadu opreme |
| 6 | `rptIzv6` Realizacija ugovora o oglašavanju po oglašivaču | `qIzv6_Kartica` **parametarski** | ugovor → stavka ugovora | po ugovoru: ugovoreno i realizovano u sekundama i dinarima, razlika, fakturisano i status fakture; u zaglavlju oglašivač sa PIB-om, kontaktom, branšom i godišnjim budžetom |
| 7 | `rptIzv7` Realizacija plana nabavke sa vrednovanjem ponuda | `qIzv7_Stavke` | plan nabavke | po stavci **podizveštaj `rptIzv7_Ponude`** (ponude sa bodovima po svakom kriterijumu i ukupnim bodovima); ukupno planirano, ukupno naručeno i **procenat izvršenja plana** |
| 8 | `rptIzv8` Prava korišćenja i rokovi važenja | `qIzv8_Prava` | status prava → licenca | dani do isteka, dozvoljeno/iskorišćeno/preostalo emitovanja i status prava (važeće, uskoro ističe, isteklo, iskorišćeno); **prava kojima ističe rok izdvojena su na početku** |

Svi izveštaji imaju zaglavlje sa nazivom izveštaja i podnožje sa datumom i
vremenom kreiranja, imenom korisnika koji ih je generisao i brojem strane
(`Strana X od Y`) — kako specifikacija zahteva.

### Parametri

| Izveštaj | Pita | Na postojećim podacima probaj |
|---|---|---|
| `rptIzv2` | `Datum od:` i `Datum do:` | `1.1.2026.` i `31.8.2026.` |
| `rptIzv6` | `Šifra ili naziv oglašivača:` | `KL-001`, ili deo naziva npr. `Market` |

Kod izveštaja 6 parametar prihvata i šifru i deo naziva klijenta
(`LIKE "*" & parametar & "*"`), pa ne moraš da pamtiš šifre.

## Na šta da obratiš pažnju

- **Grafikoni (izveštaj 3).** Dodaju se kao `MSGraph.Chart.8` objekti. Ako
  MSGraph nije registrovan na računaru, skripta to zabeleži i nastavi —
  izveštaj i dalje radi, samo bez slike, a grafikon se onda može dodati
  čarobnjakom nad upitima `qIzv3_RejtingPoZanru` i `qIzv3_RejtingPoDatumu`.
  Podrazumevani tip je stubasti; za drugi grafikon (kretanje po datumu)
  linijski se dobija u dizajnu, desni klik na grafikon → *Chart Type*.
- **Izrazi sa zapetama.** Procenti iskorišćenja budžeta i izvršenja plana
  koriste `IIf(...)` sa zapetama kao razdvajačem argumenata. Ako Access na
  tvom regionalnom podešavanju prikaže `#Error` u tom polju, u prozoru
  svojstava zameni zapete tačkom-zapetom.
- **Podizveštaj u izveštaju 7** vezan je na `SIFRA_PLANA` i `RB_STAVKE`, pa
  ispod svake stavke plana prikazuje samo njene ponude.
- **Izveštaj 1** grupiše po šemi pa po celini zato što baza sadrži 20
  programskih šema. Podaci o šemi (naziv, sezona, period, verzija, status,
  urednik) time su u zaglavlju grupe, a ne u zaglavlju izveštaja.
- **Dupliranje zbirova je izbegnuto.** Gde bi spajanje tabela ponovilo
  redove (stavke ugovora × emitovanja reklame, stavke plana × narudžbenice,
  plan × zahtevi), vrednosti se izvlače podupitima ili pomoćnim upitima
  (`qIzv6_Fakture`, `qIzv7_Zahtev`, `qIzv7_Narudzbe`, `qIzv7_Izabrana`), a u
  podnožju grupe se koristi `Max(...)` umesto `Sum(...)` za vrednosti koje
  su konstantne u okviru grupe.

## Šta nije dirano

- ni jedna od **69 tabela** (ni struktura ni podaci)
- ni jedna od **70 postojećih formi**
- ni jedan od **16 postojećih upita**
- ni jedan od **6 postojećih izveštaja**

Modul ne sadrži ni jedan poziv koji briše tabelu, a brisanje upita, izveštaja
i formi prolazi kroz proveru prefiksa. To je i automatski proveravano —
`python3 access/check_izv.py`.
