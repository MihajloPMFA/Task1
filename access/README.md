# Access baza - TV Panorama

U ovoj fascikli su dva VBA modula. Koji ti treba zavisi od toga da li već imaš bazu:

| Fajl | Kada se koristi | Šta radi |
|---|---|---|
| **`TV_Stanica_Izvestaji.bas`** | imaš bazu sa tabelama, podacima i formama (npr. `Access_v1.accdb`) | dodaje **osam izveštaja iz Specifikacije izveštaja** i upite koji im trebaju; ne menja ništa postojeće |
| `TV_Stanica_Access.bas` | praviš bazu od nule, u prazan `.accdb` | kreira celu bazu: 69 tabela, 84 veze, upite, formu za svaku tabelu, izveštaje i demo podatke |

Analiza postojeće baze i spisak svega što je dodato: **`ANALIZA_Access_v1.md`**.

---

# 1. Izveštaji za postojeću bazu - `TV_Stanica_Izvestaji.bas`

Modul `modIzvestaji` se uvozi u **postojeću** bazu i dodaje samo nove objekte:

| Prefiks | Broj | Šta je |
|---|---|---|
| `qIzv...` | 16 | upiti kao izvor podataka za izveštaje (12 glavnih + 4 pomoćna) |
| `rptIzv1` - `rptIzv8` | 8 | izveštaji iz specifikacije (2 parametarska, 1 sa grafičkim prikazom) |
| `rptIzv5_Oprema`, `rptIzv7_Ponude` | 2 | podizveštaji |
| `frmIzvestaji` | 1 | forma-meni sa dugmadima za svih osam izveštaja |

**Postojeće tabele, forme, upiti i izveštaji se ne menjaju.** Procedure koje brišu
proveravaju prefiks imena i odbijaju sve što nije `qIzv`/`rptIzv`/`frmIzvestaji`,
pa se modul može pokretati više puta bez rizika.

## Uvoz

1. Otvori svoju bazu (`Access_v1.accdb`).
2. `Alt+F11` → **File → Import File...** → izaberi `TV_Stanica_Izvestaji.bas`.
3. **Tools → References...** → uključi *Microsoft Office x.0 Access database
   engine Object Library* (DAO), ako već nije uključena.
4. Klikni bilo gde u proceduru **`KreirajIzvestaje`** i pritisni **F5**.

Na kraju procedura **sama proveri sve što je napravila**: otvori svaki upit i
svaki izveštaj i u poruci prikaže koliko ih je u redu, koliko radi ali nema
podataka i koliko ih je vratilo grešku. Detaljan spisak (red po red, sa brojem
redova po upitu) je u *Immediate* prozoru — `Ctrl+G`, ili procedura `Dnevnik`.

Provera se može pokrenuti i posebno, kad god: klikni u proceduru **`Provera`**
i pritisni F5.

Izveštaji se posle pokreću dvoklikom u oknu objekata ili preko forme
`frmIzvestaji`.

## Izveštaji

| # | Izveštaj | Tip | Izvor |
|---|---|---|---|
| 1 | Programska šema sa terminima emitovanja | tabelarni, grupisan po šemi i celini | `qIzv1_Sema` |
| 2 | Evidencija emitovanog sadržaja (playout log) | **parametarski** (datum od - do) | `qIzv2_Playout` |
| 3 | Gledanost emisija po žanru | **grafički** (2 grafikona) + prateća tabela | `qIzv3_Emisije` |
| 4 | Realizacija i troškovi projekta produkcije | grupisan po projektu i aktivnosti, sa zbirovima i % budžeta | `qIzv4_Troskovi` |
| 5 | Angažovanje zaposlenih i zaduženje opreme | dva dela, drugi je podizveštaj | `qIzv5_Angazovanje` |
| 6 | Realizacija ugovora o oglašavanju po oglašivaču | **parametarski** (šifra ili naziv) | `qIzv6_Kartica` |
| 7 | Realizacija plana nabavke sa vrednovanjem ponuda | sa vezanim podizveštajem ponuda | `qIzv7_Stavke` |
| 8 | Prava korišćenja medijskog sadržaja i rokovi važenja | tabelarni, prava na isteku prva | `qIzv8_Prava` |

Na podacima koji su već u bazi: za izveštaj 2 unesi `1.1.2026.` i `31.8.2026.`,
za izveštaj 6 `KL-001` (ili deo naziva, npr. `Market`).

## Generisanje i provera

```
python3 access/gen_izv_access.py                      # pravi TV_Stanica_Izvestaji.bas
python3 access/check_izv.py                           # sadrzaj, raspored, bezbednost
python3 access/check_vba.py TV_Stanica_Izvestaji.bas  # VBA identifikatori
```

Izvori: `gen_izv_access.py` (raspored izveštaja), `izv_lib.py` (pomoćne VBA
procedure), `izv_upiti.py` (SQL upita), `sema_accdb.json` (snimak strukture
analizirane baze).

---

# 2. Cela baza od nule - `TV_Stanica_Access.bas`

`TV_Stanica_Access.bas` je VBA modul koji se uveze u prazan Access fajl i
jednim pokretanjem napravi celu bazu: tabele, veze, upite, forme i izveštaje.
Sve je izvedeno iz ER dijagrama ovog projekta (`er/ER_TV_stanica.sql`,
odnosno `er/generator/schema.py`), pa skripta ne može da se raziđe sa modelom.

## Uvoz u Access

1. Napravi prazan Access fajl (**Blank database**, `.accdb`).
2. `Alt+F11` → **File → Import File...** → izaberi `TV_Stanica_Access.bas`.
   (U oknu objekata pojavi se modul `modKreirajBazu`.)
3. **Tools → References...** → uključi *Microsoft Office x.0 Access database
   engine Object Library* (DAO), ako već nije uključena.
4. Klikni bilo gde u proceduru `KreirajSve` i pritisni **F5**.

Na kraju se javlja poruka sa brojem napravljenih objekata. Detaljan dnevnik
(uključujući eventualna upozorenja) ispisuje se u *Immediate* prozor
(`Ctrl+G`), a može se ponovo prikazati procedurom `Dnevnik`.

> `KreirajSve` prvo **briše** sve postojeće tabele, upite, forme i izveštaje u
> otvorenoj bazi, pa je pokrećeš u praznom fajlu ili u onom koji sme da se
> prepiše. Može se pokretati više puta zaredom.

## Šta se kreira

| Objekat | Broj |
|---|---|
| tabele | 69 (405 kolona) |
| veze (referencijalni integritet) | 84 |
| upiti | 13, od toga 2 parametarska |
| forme za unos | 69 - po jedna za svaku tabelu |
| glavni meni | `frm_GLAVNI_MENI` sa dugmadima za izveštaje |
| izveštaji | 10 (8 iz specifikacije + 2 podizveštaja) |
| demo redovi | 230 u 53 tabele |

Forme se zovu `frm_<IME_TABELE>`, upiti `qry...`, izveštaji `rpt...`.
Natpisi polja (Caption) i formati se upisuju u samu tabelu, pa ih forme i
izveštaji preuzimaju automatski.

## Izveštaji iz specifikacije

| # | Izveštaj | Upit | Napomena |
|---|---|---|---|
| 1 | Programska šema sa terminima emitovanja | `qryProgramskaSema` | grupisanje po `NAZIV_CELINE` |
| 2 | Evidencija emitovanog sadržaja (playout log) | `qryPlayoutLog` | **parametarski**, grupisanje po `DATUM` |
| 3 | Gledanost emisija po žanru | `qryGledanostEmisija` | **grafički prikaz** (MSGraph nad `qryGledanostPoZanru`) |
| 4 | Realizacija i troškovi projekta produkcije | `qryTroskoviProjekta` | grupisanje po `NAZIV_PROJEKTA` |
| 5 | Angažovanje zaposlenih i zaduženje opreme | `qryAngazovanje` | podizveštaj `rptZaduzenjeOpreme`, grupisanje po `ZAPOSLENI_NAZIV` |
| 6 | Realizacija ugovora o oglašavanju po oglašivaču | `qryKarticaOglasivaca` | **parametarski**, grupisanje po `BROJ_UGOVORA` |
| 7 | Realizacija plana nabavke sa vrednovanjem ponuda | `qryPlanNabavke` | podizveštaj `rptVrednovanjePonuda` |
| 8 | Prava korišćenja medijskog sadržaja i rokovi važenja | `qryPravaKoriscenja` | - |

Parametarski izveštaji pitaju za vrednosti pri otvaranju. Na demo podacima:
`rptPlayoutLog` za period - unesi `14.9.2026.` i `15.9.2026.`;
`rptKarticaOglasivaca` za šifru oglašivača - unesi `KL-001`
(oglašivači u demo podacima su `KL-001`, `KL-002`, `KL-003`).

## Srpska slova

`.bas` je namerno čist ASCII, da bi se uvozio bez obzira na kodnu stranu
Windows-a. Slova č, ć, š, ž, đ zapisana su markerima (`~c`, `~k`, `~s`,
`~z`, `~d`), a funkcija `T()` ih pri izvršavanju sastavlja preko `ChrW`.
U bazi su natpisi ispravni.

## Generisanje

```
python3 access/gen_access.py     # pravi TV_Stanica_Access.bas
python3 access/check_bas.py      # provera sadrzaja (tabele, veze, izvestaji)
python3 access/check_vba.py      # provera VBA identifikatora (Option Explicit)
```

Izvori: `gen_access.py` (emiteri), `vba_lib.py` (pomoćne VBA procedure),
`upiti.py` (SQL upita), `demo_data.py` (demo podaci).
