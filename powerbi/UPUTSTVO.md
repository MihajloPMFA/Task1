# Power BI izveštaji - TV Panorama

Pet izveštaja iz Specifikacije izveštaja, isti sadržaj i isti brojevi kao u
Access izveštajima `rptIzv2`, `rptIzv3`, `rptIzv4`, `rptIzv6` i `rptIzv7`.

| Strana | Izveštaj iz specifikacije | Access | Poslovna oblast |
|---|---|---|---|
| 1 | 2 - Evidencija emitovanog sadržaja (playout log) | `rptIzv2` | Program i emitovanje |
| 2 | 3 - Gledanost emisija po žanru | `rptIzv3` | Analitika gledanosti |
| 3 | 4 - Realizacija i troškovi projekta produkcije | `rptIzv4` | Produkcija |
| 4 | 6 - Realizacija ugovora o oglašavanju po oglašivaču | `rptIzv6` | Marketing i prodaja |
| 5 | 7 - Realizacija plana nabavke sa vrednovanjem ponuda | `rptIzv7` | Nabavka |

Parametri iz Access izveštaja 2 i 6 (period, oglašivač) u Power BI-ju su
**slajseri**, jer se tako parametri i rade u BI alatima - filtriraju sve
vizuale na strani odjednom.

## Kako do jednog .pbix fajla

`.pbix` se ne može napraviti van Power BI Desktop-a: u njemu model stoji u
delu `DataModel`, a to je binarni Analysis Services (VertiPaq) stream koji
ume da zapiše samo sam Power BI. U `.pbit` fajlu (Power BI šablon) isti model
stoji kao **tekst** (`DataModelSchema`, TMSL JSON), pa se `.pbit` može
napraviti spolja. Zato ide ovako - `.pbit` je jedan fajl i iz njega se u tri
klika dobije jedan `.pbix` sa svih pet izveštaja:

1. Dvoklik na **`TV_Panorama.pbit`** (ili u Power BI Desktop-u
   *File → Open report → Browse*).
2. Power BI pita za tri parametra:
   - **Izvor** - `Access` (čita direktno tvoj `.accdb`) ili `CSV`
   - **PutDoBaze** - puna putanja do `Access_v1.accdb`,
     npr. `C:\TV_Panorama\Access_v1.accdb`
   - **PutDoCsv** - putanja do `csv` foldera iz zip-a
   Popuni i klikni **Load**. Podaci se učitaju sami.
3. **File → Save as → Power BI files (*.pbix)** i sačuvaj kao
   `TV_Panorama.pbix`. Tu su sve pet strana u jednom fajlu.

Ako Power BI prijavi grešku pri čitanju `.accdb` (najčešće 32/64-bit
neusklađenost Office-a i Power BI-ja), u *Transform data → Manage parameters*
prebaci **Izvor** na `CSV` i osveži - u zip-u je izvoz podataka iz tvoje baze,
pa sve radi bez Access drajvera.

> Ako prvi `.pbit` javi da fajl nije ispravan, probaj
> **`TV_Panorama_bez_BOM.pbit`** - isti sadržaj, samo drugo kodiranje
> tekstualnih delova paketa. Jedan od dva prolazi.

## Rezervni put 1 - .pbip projekat

U zip-u je i isti model i izveštaj kao Power BI projekat (folder
`TV_Panorama.SemanticModel` + `TV_Panorama.Report` i fajl `TV_Panorama.pbip`).
Otvori `TV_Panorama.pbip`, postavi parametre u *Manage parameters*, *Refresh*,
pa **File → Save as → .pbix**. Ako Power BI traži da uključiš podršku:
*File → Options and settings → Options → Preview features →*
**Power BI Project (.pbip) save option**, pa restart.

## Rezervni put 2 - ručno sastavljanje

Siguran put, traje oko pola sata:

1. Novi prazan fajl u Power BI Desktop-u.
2. Iz `M_upiti.txt` prenesi tri parametra, pa upite `Tipovi` i `Tabela`,
   pa 13 tabela modela (*Blank Query → Advanced Editor → nalepi → preimenuj*).
3. *Close & Apply*.
4. U *Model view* napravi 13 relacija iz `DAX_mere.txt` (na kraju fajla) i
   označi `Kalendar` kao tabelu datuma (desni klik → *Mark as date table* →
   kolona `Datum`).
5. Iz `DAX_mere.txt` dodaj 37 mera na tabele koje su tamo navedene.
6. Napravi pet strana i na svaku stavi vizuale iz tabela ispod.
7. Sačuvaj kao `.pbix`.

## Vizuali po stranama

Pozicije su u pikselima na platnu 1280 x 720 (x, y, širina, visina).

### Strana 1 - 2 Playout log

| Vizual | Pozicija | Polja | Naslov |
|---|---|---|---|
| Tekstualno polje (Text box) | 16, 12, 900 x 44 | - | Izveštaj 2 - Evidencija emitovanog sadržaja (playout log) |
| Tekstualno polje (Text box) | 16, 58, 900 x 24 | - | Informacioni sistem TV stanice - TV Panorama  \|  period se bira slajserom Datum |
| Kartica (Card) | 16, 92, 220 x 86 | **Values:** `Playout.Broj emitovanja` | Broj emitovanja |
| Kartica (Card) | 248, 92, 220 x 86 | **Values:** `Playout.Stvarno trajanje (min)` | Stvarno trajanje (min) |
| Kartica (Card) | 480, 92, 220 x 86 | **Values:** `Playout.Odstupanje (min)` | Odstupanje (min) |
| Kartica (Card) | 712, 92, 220 x 86 | **Values:** `Playout.Emitovanja sa smetnjama` | Sa smetnjama |
| Slajser (Slicer) (režim: Between) | 940, 92, 324 x 86 | **Values:** `Kalendar.Datum` | Datum emitovanja (od - do) |
| Stubasti grafikon (Stacked column chart) | 16, 190, 456 x 210 | **X axis / Category:** `Kalendar.Datum`<br>**Y axis:** `Playout.Stvarno trajanje (min)` | Emitovani minuti po danu |
| Prstenasti grafikon (Donut chart) | 484, 190, 444 x 210 | **X axis / Category:** `Playout.Status realizacije`<br>**Y axis:** `Playout.Broj emitovanja` | Emitovanja po statusu realizacije |
| Slajser (Slicer) | 940, 190, 324 x 100 | **Values:** `Playout.Status realizacije` | Status realizacije |
| Slajser (Slicer) | 940, 298, 324 x 102 | **Values:** `Emisije.Žanr` | Žanr emisije |
| Tabela (Table) (sortiranje: Datum, rastuće) | 16, 412, 1248 x 292 | **Values:** `Playout.Datum`, `Playout.Stvarno vreme početka`, `Emisije.Naziv emisije`, `Playout.Medijski sadržaj`, `Playout.Planirano trajanje`, `Playout.Stvarno trajanje`, `Playout.Odstupanje`, `Playout.Status realizacije`, `Playout.Broj licence`, `Playout.Vrsta prava`, `Playout.Operater emitovanja`, `Playout.Napomena o smetnjama` | Hronološki pregled emitovanog sadržaja |

### Strana 2 - 3 Gledanost po žanru

| Vizual | Pozicija | Polja | Naslov |
|---|---|---|---|
| Tekstualno polje (Text box) | 16, 12, 900 x 44 | - | Izveštaj 3 - Gledanost emisija po žanru |
| Tekstualno polje (Text box) | 16, 58, 900 x 24 | - | Informacioni sistem TV stanice - TV Panorama  \|  grafički prikaz sa pratećom tabelom |
| Kartica (Card) | 16, 92, 220 x 86 | **Values:** `Gledanost.Prosečan rejting` | Prosečan rejting |
| Kartica (Card) | 248, 92, 220 x 86 | **Values:** `Gledanost.Prosečan udeo` | Prosečan udeo u terminu |
| Kartica (Card) | 480, 92, 220 x 86 | **Values:** `Gledanost.Prosečno gledalaca` | Prosečno gledalaca |
| Kartica (Card) | 712, 92, 220 x 86 | **Values:** `Gledanost.Broj merenja` | Broj merenja |
| Slajser (Slicer) (režim: Between) | 940, 92, 324 x 86 | **Values:** `Kalendar.Datum` | Period merenja (od - do) |
| Grupisani stubasti (Clustered column chart) (sortiranje: Prosečan rejting, opadajuće) | 16, 190, 456 x 210 | **X axis / Category:** `Emisije.Žanr`<br>**Y axis:** `Gledanost.Prosečan rejting` | Prosečan ostvareni rejting po žanru emisije |
| Linijski grafikon (Line chart) | 484, 190, 444 x 210 | **X axis / Category:** `Gledanost.Datum merenja`<br>**Y axis:** `Gledanost.Prosečan rejting` | Kretanje prosečnog rejtinga po datumu merenja |
| Slajser (Slicer) | 940, 190, 324 x 100 | **Values:** `Gledanost.Izvor merenja` | Izvor merenja |
| Slajser (Slicer) | 940, 298, 324 x 102 | **Values:** `Gledanost.Ciljna grupa` | Ciljna grupa |
| Tabela (Table) (sortiranje: Prosečan rejting, opadajuće) | 16, 412, 1248 x 292 | **Values:** `Emisije.Naziv emisije`, `Emisije.Žanr`, `Gledanost.Broj merenja`, `Gledanost.Prosečan rejting`, `Gledanost.Prosečan udeo`, `Gledanost.Prosečno gledalaca`, `Gledanost.Prosečno gledanje (min)` | Gledanost po emisiji - opadajuće po ostvarenom rejtingu |

### Strana 3 - 4 Troškovi produkcije

| Vizual | Pozicija | Polja | Naslov |
|---|---|---|---|
| Tekstualno polje (Text box) | 16, 12, 900 x 44 | - | Izveštaj 4 - Realizacija i troškovi projekta produkcije |
| Tekstualno polje (Text box) | 16, 58, 900 x 24 | - | Informacioni sistem TV stanice - TV Panorama  \|  zbirovi po projektu i aktivnosti, sa iskorišćenjem budžeta |
| Kartica (Card) | 16, 92, 220 x 86 | **Values:** `Troskovi.Ukupno troškova` | Ukupno troškova |
| Kartica (Card) | 248, 92, 220 x 86 | **Values:** `Projekti.Odobren budžet (ukupno)` | Odobren budžet |
| Kartica (Card) | 480, 92, 220 x 86 | **Values:** `Projekti.% iskorišćenja budžeta` | % iskorišćenja budžeta |
| Kartica (Card) | 712, 92, 220 x 86 | **Values:** `Troskovi.Broj aktivnosti` | Broj aktivnosti |
| Slajser (Slicer) (režim: Dropdown) | 940, 92, 324 x 86 | **Values:** `Projekti.Naziv projekta` | Projekat produkcije |
| Stubasti grafikon (Stacked column chart) (sortiranje: Ukupno troškova, opadajuće) | 16, 190, 456 x 210 | **X axis / Category:** `Troskovi.Vrsta troška`<br>**Y axis:** `Troskovi.Ukupno troškova` | Troškovi po vrsti troška |
| Trakasti grafikon (Stacked bar chart) (sortiranje: % iskorišćenja budžeta, opadajuće) | 484, 190, 444 x 210 | **X axis / Category:** `Projekti.Naziv projekta`<br>**Y axis:** `Projekti.% iskorišćenja budžeta` | Iskorišćenost odobrenog budžeta po projektu |
| Slajser (Slicer) | 940, 190, 324 x 100 | **Values:** `Projekti.Vrsta produkcije` | Vrsta produkcije |
| Slajser (Slicer) (režim: Between) | 940, 298, 324 x 102 | **Values:** `Kalendar.Datum` | Datum nastanka troška (od - do) |
| Matrica (Matrix) | 16, 412, 1248 x 292 | **Rows:** `Projekti.Naziv projekta`, `Troskovi.Aktivnost`, `Troskovi.Vrsta troška`<br>**Values:** `Troskovi.Ukupno troškova`, `Troskovi.Broj troškova`, `Projekti.Odobren budžet (ukupno)`, `Projekti.% iskorišćenja budžeta` | Projekat - aktivnost - trošak, sa zbirovima |

### Strana 4 - 6 Kartica oglašivača

| Vizual | Pozicija | Polja | Naslov |
|---|---|---|---|
| Tekstualno polje (Text box) | 16, 12, 900 x 44 | - | Izveštaj 6 - Realizacija ugovora o oglašavanju po oglašivaču |
| Tekstualno polje (Text box) | 16, 58, 900 x 24 | - | Informacioni sistem TV stanice - TV Panorama  \|  oglašivač se bira slajserom - zamena za parametar iz Access izveštaja |
| Kartica (Card) | 16, 92, 220 x 86 | **Values:** `StavkeUgovora.Ugovoreno sekundi` | Ugovoreno sekundi |
| Kartica (Card) | 248, 92, 220 x 86 | **Values:** `EmitovanjaReklama.Realizovano sekundi` | Realizovano sekundi |
| Kartica (Card) | 480, 92, 220 x 86 | **Values:** `EmitovanjaReklama.Naplaćeno` | Naplaćeno |
| Kartica (Card) | 712, 92, 220 x 86 | **Values:** `Ugovori.% naplate` | % naplate |
| Slajser (Slicer) (režim: Dropdown) | 940, 92, 324 x 86 | **Values:** `Ugovori.Oglašivač` | Oglašivač |
| Matrica (Matrix) | 16, 190, 456 x 210 | **Rows:** `Ugovori.Broj ugovora`, `StavkeUgovora.Opis stavke`<br>**Values:** `StavkeUgovora.Ugovoreno sekundi`, `StavkeUgovora.Ugovorena vrednost` | Ugovorene stavke po ugovoru |
| Stubasti grafikon (Stacked column chart) | 484, 190, 444 x 210 | **X axis / Category:** `Kalendar.Naziv meseca`<br>**Y axis:** `EmitovanjaReklama.Naplaćeno` | Naplaćeni iznos po mesecu emitovanja |
| Slajser (Slicer) | 940, 190, 324 x 100 | **Values:** `Ugovori.Status ugovora` | Status ugovora |
| Slajser (Slicer) (režim: Between) | 940, 298, 324 x 102 | **Values:** `Kalendar.Datum` | Datum emitovanja (od - do) |
| Tabela (Table) (sortiranje: Datum emitovanja, rastuće) | 16, 412, 1248 x 292 | **Values:** `Ugovori.Broj ugovora`, `EmitovanjaReklama.Datum emitovanja`, `EmitovanjaReklama.Vreme emitovanja`, `EmitovanjaReklama.Reklamni blok`, `EmitovanjaReklama.Termin`, `EmitovanjaReklama.Zona`, `EmitovanjaReklama.Trajanje spota`, `EmitovanjaReklama.Naplaćeni iznos`, `EmitovanjaReklama.Status naplate` | Stvarno emitovani reklamni spotovi |

### Strana 5 - 7 Plan nabavke i ponude

| Vizual | Pozicija | Polja | Naslov |
|---|---|---|---|
| Tekstualno polje (Text box) | 16, 12, 900 x 44 | - | Izveštaj 7 - Realizacija plana nabavke sa vrednovanjem ponuda |
| Tekstualno polje (Text box) | 16, 58, 900 x 24 | - | Informacioni sistem TV stanice - TV Panorama  \|  izvršenje plana po stavkama i bodovi po kriterijumima |
| Kartica (Card) | 16, 92, 220 x 86 | **Values:** `StavkePlana.Ukupno planirano` | Ukupno planirano |
| Kartica (Card) | 248, 92, 220 x 86 | **Values:** `StavkePlana.Ukupno naručeno` | Ukupno naručeno |
| Kartica (Card) | 480, 92, 220 x 86 | **Values:** `StavkePlana.% izvršenja plana` | % izvršenja plana |
| Kartica (Card) | 712, 92, 220 x 86 | **Values:** `StavkePlana.Broj stavki plana` | Broj stavki plana |
| Slajser (Slicer) (režim: Dropdown) | 940, 92, 324 x 86 | **Values:** `Planovi.Šifra plana` | Plan nabavke |
| Stubasti grafikon (Stacked column chart) | 16, 190, 456 x 210 | **X axis / Category:** `StavkePlana.Planirani kvartal`<br>**Y axis:** `StavkePlana.Ukupno planirano`, `StavkePlana.Ukupno naručeno` | Planirano i naručeno po kvartalu |
| Trakasti grafikon (Stacked bar chart) (sortiranje: Ukupno bodova ponude, opadajuće) | 484, 190, 444 x 210 | **X axis / Category:** `VrednovanjePonuda.Dobavljač`<br>**Y axis:** `VrednovanjePonuda.Ukupno bodova ponude` | Ukupan broj bodova po dobavljaču |
| Slajser (Slicer) | 940, 190, 324 x 100 | **Values:** `Planovi.Status plana` | Status plana |
| Slajser (Slicer) | 940, 298, 324 x 102 | **Values:** `StavkePlana.Planirani kvartal` | Planirani kvartal |
| Matrica (Matrix) | 16, 412, 616 x 292 | **Rows:** `Planovi.Šifra plana`, `StavkePlana.Opis artikla`<br>**Values:** `StavkePlana.Ukupno planirano`, `StavkePlana.Ukupno naručeno`, `StavkePlana.Odstupanje nabavke`, `StavkePlana.% izvršenja plana` | Stavke plana i njihova realizacija |
| Matrica (Matrix) | 648, 412, 616 x 292 | **Rows:** `VrednovanjePonuda.Dobavljač`, `VrednovanjePonuda.Broj ponude`<br>**Columns:** `VrednovanjePonuda.Kriterijum`<br>**Values:** `VrednovanjePonuda.Bodovi (zbir)` | Bodovi po kriterijumu vrednovanja |

## Kako se brojevi poklapaju sa Access-om

Spojevi koje Access radi u upitu odrađeni su u Power Query-ju, ali tamo gde
bi spajanje umnožilo redove i pokvarilo zbirove, model je razdvojen u dve
tabele povezane preko dimenzije:

- **Izveštaj 6:** `StavkeUgovora` (ugovoreno) i `EmitovanjaReklama`
  (realizovano) su odvojene tabele, obe vezane na `Ugovori`. Zato
  „Ugovoreno sekundi" i „Realizovano sekundi" mogu da stoje jedno uz drugo
  bez dupliranja - u Access-u je to rešeno podupitima i `Max(...)`.
- **Izveštaj 7:** `StavkePlana` (izvršenje) i `VrednovanjePonuda` (bodovi)
  su odvojene, obe vezane na `Planovi`.
- **Izveštaj 2:** jedno pravo korišćenja po medijskom sadržaju (najmanji broj
  licence), da spajanje sa `POKRIVENOST_PRAVOM` ne umnoži redove playout loga.
- **Izveštaj 4:** odobren budžet stoji u dimenziji `Projekti`, pa se ne
  sabira po svakom troškovnom redu.

Provereno na podacima iz tvoje baze (`python3 powerbi/check_model.py`):
40 emitovanja, 2490 stvarnih minuta prema 2530 planiranih, 20 sa smetnjama,
87,5% realizovanih; prosečan rejting po žanru od 4,05 (Dečji) do 7,95
(Obrazovni); izvršenje plana nabavke 41,2%.

## Generisanje

```
python3 powerbi/export_csv.py     # izvoz podataka iz .accdb u csv/
python3 powerbi/check_model.py    # provera logike modela nad tim podacima
python3 powerbi/gen_docs.py       # M_upiti.txt i DAX_mere.txt
python3 powerbi/gen_pbip.py       # pbip/ projekat + zip
python3 powerbi/check_pbip.py     # provera model.bim i report.json
python3 powerbi/gen_uputstvo.py   # ovo uputstvo
```
