# -*- coding: utf-8 -*-
"""Generiše UPUTSTVO.md iz samog report.json, da se opis ne razmine sa fajlom."""
import io, json, os
BASE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(BASE, 'pbip', 'TV_Panorama.Report', 'report.json'),
                   encoding='utf-8'))

VRSTA = {'textbox': 'Tekstualno polje (Text box)', 'card': 'Kartica (Card)',
         'slicer': 'Slajser (Slicer)',
         'columnChart': 'Stubasti grafikon (Stacked column chart)',
         'clusteredColumnChart': 'Grupisani stubasti (Clustered column chart)',
         'lineChart': 'Linijski grafikon (Line chart)',
         'donutChart': 'Prstenasti grafikon (Donut chart)',
         'barChart': 'Trakasti grafikon (Stacked bar chart)',
         'tableEx': 'Tabela (Table)', 'pivotTable': 'Matrica (Matrix)'}
ULOGA = {'Values': 'Values', 'Category': 'X axis / Category', 'Y': 'Y axis',
         'Rows': 'Rows', 'Columns': 'Columns'}

L = []
A = L.append
A('# Power BI izveštaji - TV Panorama')
A('')
A('Pet izveštaja iz Specifikacije izveštaja, isti sadržaj i isti brojevi kao u')
A('Access izveštajima `rptIzv2`, `rptIzv3`, `rptIzv4`, `rptIzv6` i `rptIzv7`.')
A('')
A('| Strana | Izveštaj iz specifikacije | Access | Poslovna oblast |')
A('|---|---|---|---|')
A('| 1 | 2 - Evidencija emitovanog sadržaja (playout log) | `rptIzv2` | Program i emitovanje |')
A('| 2 | 3 - Gledanost emisija po žanru | `rptIzv3` | Analitika gledanosti |')
A('| 3 | 4 - Realizacija i troškovi projekta produkcije | `rptIzv4` | Produkcija |')
A('| 4 | 6 - Realizacija ugovora o oglašavanju po oglašivaču | `rptIzv6` | Marketing i prodaja |')
A('| 5 | 7 - Realizacija plana nabavke sa vrednovanjem ponuda | `rptIzv7` | Nabavka |')
A('')
A('Parametri iz Access izveštaja 2 i 6 (period, oglašivač) u Power BI-ju su')
A('**slajseri**, jer se tako parametri i rade u BI alatima - filtriraju sve')
A('vizuale na strani odjednom.')
A('')
A('## Kako do jednog .pbix fajla')
A('')
A('`.pbix` se ne može napraviti van Power BI Desktop-a: u njemu model stoji u')
A('delu `DataModel`, a to je binarni Analysis Services (VertiPaq) stream koji')
A('ume da zapiše samo sam Power BI. U `.pbit` fajlu (Power BI šablon) isti model')
A('stoji kao **tekst** (`DataModelSchema`, TMSL JSON), pa se `.pbit` može')
A('napraviti spolja. Zato ide ovako - `.pbit` je jedan fajl i iz njega se u tri')
A('klika dobije jedan `.pbix` sa svih pet izveštaja:')
A('')
A('1. Dvoklik na **`TV_Panorama.pbit`** (ili u Power BI Desktop-u')
A('   *File → Open report → Browse*).')
A('2. Power BI pita za tri parametra:')
A('   - **Izvor** - `Access` (čita direktno tvoj `.accdb`) ili `CSV`')
A('   - **PutDoBaze** - puna putanja do `Access_v1.accdb`,')
A('     npr. `C:\\TV_Panorama\\Access_v1.accdb`')
A('   - **PutDoCsv** - putanja do `csv` foldera iz zip-a')
A('   Popuni i klikni **Load**. Podaci se učitaju sami.')
A('3. **File → Save as → Power BI files (*.pbix)** i sačuvaj kao')
A('   `TV_Panorama.pbix`. Tu su sve pet strana u jednom fajlu.')
A('')
A('Ako Power BI prijavi grešku pri čitanju `.accdb` (najčešće 32/64-bit')
A('neusklađenost Office-a i Power BI-ja), u *Transform data → Manage parameters*')
A('prebaci **Izvor** na `CSV` i osveži - u zip-u je izvoz podataka iz tvoje baze,')
A('pa sve radi bez Access drajvera.')
A('')
A('> Ako prvi `.pbit` javi da fajl nije ispravan, probaj')
A('> **`TV_Panorama_bez_BOM.pbit`** - isti sadržaj, samo drugo kodiranje')
A('> tekstualnih delova paketa. Jedan od dva prolazi.')
A('')
A('## Rezervni put 1 - .pbip projekat')
A('')
A('U zip-u je i isti model i izveštaj kao Power BI projekat (folder')
A('`TV_Panorama.SemanticModel` + `TV_Panorama.Report` i fajl `TV_Panorama.pbip`).')
A('Otvori `TV_Panorama.pbip`, postavi parametre u *Manage parameters*, *Refresh*,')
A('pa **File → Save as → .pbix**. Ako Power BI traži da uključiš podršku:')
A('*File → Options and settings → Options → Preview features →*')
A('**Power BI Project (.pbip) save option**, pa restart.')
A('')
A('## Rezervni put 2 - ručno sastavljanje')
A('')
A('Siguran put, traje oko pola sata:')
A('')
A('1. Novi prazan fajl u Power BI Desktop-u.')
A('2. Iz `M_upiti.txt` prenesi tri parametra, pa upite `Tipovi` i `Tabela`,')
A('   pa 13 tabela modela (*Blank Query → Advanced Editor → nalepi → preimenuj*).')
A('3. *Close & Apply*.')
A('4. U *Model view* napravi 13 relacija iz `DAX_mere.txt` (na kraju fajla) i')
A('   označi `Kalendar` kao tabelu datuma (desni klik → *Mark as date table* →')
A('   kolona `Datum`).')
A('5. Iz `DAX_mere.txt` dodaj 37 mera na tabele koje su tamo navedene.')
A('6. Napravi pet strana i na svaku stavi vizuale iz tabela ispod.')
A('7. Sačuvaj kao `.pbix`.')
A('')
A('## Vizuali po stranama')
A('')
A('Pozicije su u pikselima na platnu 1280 x 720 (x, y, širina, visina).')
A('')
for s in R['sections']:
    A('### Strana %d - %s' % (s['ordinal'] + 1, s['displayName']))
    A('')
    A('| Vizual | Pozicija | Polja | Naslov |')
    A('|---|---|---|---|')
    for vc in s['visualContainers']:
        cfg = json.loads(vc['config'])
        sv = cfg['singleVisual']
        p = cfg['layouts'][0]['position']
        poz = '%d, %d, %d x %d' % (p['x'], p['y'], p['width'], p['height'])
        if sv['visualType'] == 'textbox':
            runs = sv['objects']['general'][0]['properties']['paragraphs'][0]['textRuns']
            A('| %s | %s | - | %s |' % (VRSTA['textbox'], poz,
                                        runs[0]['value'].replace('|', '\\|')))
            continue
        naslov = ''
        if 'vcObjects' in sv:
            naslov = sv['vcObjects']['title'][0]['properties']['text']['expr']['Literal']['Value']
            naslov = naslov.strip("'").replace("''", "'")
        delovi = []
        for uloga, lista in sv['projections'].items():
            polja = ', '.join('`%s`' % x['queryRef'] for x in lista)
            delovi.append('**%s:** %s' % (ULOGA.get(uloga, uloga), polja))
        dod = ''
        if sv['visualType'] == 'slicer':
            obj = sv.get('objects', {}).get('data', [])
            if obj:
                rezim = obj[0]['properties']['mode']['expr']['Literal']['Value'].strip("'")
                dod = ' (režim: %s)' % rezim
        if 'OrderBy' in sv['prototypeQuery']:
            o = sv['prototypeQuery']['OrderBy'][0]
            kind = 'Measure' if 'Measure' in o['Expression'] else 'Column'
            dod += ' (sortiranje: %s, %s)' % (
                o['Expression'][kind]['Property'],
                'opadajuće' if o['Direction'] == 2 else 'rastuće')
        A('| %s%s | %s | %s | %s |' % (VRSTA.get(sv['visualType'], sv['visualType']),
                                       dod, poz, '<br>'.join(delovi),
                                       naslov.replace('|', '\\|')))
    A('')

A('## Kako se brojevi poklapaju sa Access-om')
A('')
A('Spojevi koje Access radi u upitu odrađeni su u Power Query-ju, ali tamo gde')
A('bi spajanje umnožilo redove i pokvarilo zbirove, model je razdvojen u dve')
A('tabele povezane preko dimenzije:')
A('')
A('- **Izveštaj 6:** `StavkeUgovora` (ugovoreno) i `EmitovanjaReklama`')
A('  (realizovano) su odvojene tabele, obe vezane na `Ugovori`. Zato')
A('  „Ugovoreno sekundi" i „Realizovano sekundi" mogu da stoje jedno uz drugo')
A('  bez dupliranja - u Access-u je to rešeno podupitima i `Max(...)`.')
A('- **Izveštaj 7:** `StavkePlana` (izvršenje) i `VrednovanjePonuda` (bodovi)')
A('  su odvojene, obe vezane na `Planovi`.')
A('- **Izveštaj 2:** jedno pravo korišćenja po medijskom sadržaju (najmanji broj')
A('  licence), da spajanje sa `POKRIVENOST_PRAVOM` ne umnoži redove playout loga.')
A('- **Izveštaj 4:** odobren budžet stoji u dimenziji `Projekti`, pa se ne')
A('  sabira po svakom troškovnom redu.')
A('')
A('Provereno na podacima iz tvoje baze (`python3 powerbi/check_model.py`):')
A('40 emitovanja, 2490 stvarnih minuta prema 2530 planiranih, 20 sa smetnjama,')
A('87,5% realizovanih; prosečan rejting po žanru od 4,05 (Dečji) do 7,95')
A('(Obrazovni); izvršenje plana nabavke 41,2%.')
A('')
A('## Generisanje')
A('')
A('```')
A('python3 powerbi/export_csv.py     # izvoz podataka iz .accdb u csv/')
A('python3 powerbi/check_model.py    # provera logike modela nad tim podacima')
A('python3 powerbi/gen_docs.py       # M_upiti.txt i DAX_mere.txt')
A('python3 powerbi/gen_pbip.py       # pbip/ projekat + zip')
A('python3 powerbi/check_pbip.py     # provera model.bim i report.json')
A('python3 powerbi/gen_uputstvo.py   # ovo uputstvo')
A('```')
io.open(os.path.join(BASE, 'UPUTSTVO.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('UPUTSTVO.md %d linija' % len(L))
