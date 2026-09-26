# -*- coding: utf-8 -*-
"""Provera Power BI projekta pre isporuke: model.bim i report.json."""
import json, os, re, sys
BASE = os.path.dirname(os.path.abspath(__file__))
PB = os.path.join(BASE, 'pbip')
NAZIV = 'TV_Panorama'
from model_def import OSNOVNE

g = []
def ok(c, p):
    print(('  OK   ' if c else '  GRESKA ') + p)
    if not c:
        g.append(p)

def ucitaj(put):
    with open(put, encoding='utf-8') as f:
        return json.load(f)

print('== fajlovi projekta')
for rel in (NAZIV + '.pbip', NAZIV + '.SemanticModel/definition.pbism',
            NAZIV + '.SemanticModel/model.bim', NAZIV + '.Report/definition.pbir',
            NAZIV + '.Report/report.json'):
    p = os.path.join(PB, rel)
    ok(os.path.exists(p), 'postoji %s' % rel)
    if os.path.exists(p):
        try:
            ucitaj(p)
            ok(True, 'ispravan JSON: %s' % rel)
        except Exception as e:
            ok(False, 'neispravan JSON %s: %s' % (rel, e))

M = ucitaj(os.path.join(PB, NAZIV + '.SemanticModel/model.bim'))
R = ucitaj(os.path.join(PB, NAZIV + '.Report/report.json'))
mm = M['model']

print('== semanticki model')
KOL, MER, M_TXT = {}, {}, {}
for t in mm['tables']:
    KOL[t['name']] = {c['name']: c for c in t['columns']}
    MER[t['name']] = {x['name'] for x in t.get('measures', [])}
    M_TXT[t['name']] = '\n'.join(t['partitions'][0]['source']['expression'])
ok(len(mm['tables']) == 13, 'tabela: %d' % len(mm['tables']))
ok(all(t.get('partitions') for t in mm['tables']), 'svaka tabela ima particiju')
ok(all(c.get('sourceColumn') == c['name'] for t in mm['tables'] for c in t['columns']),
   'svaka kolona ima sourceColumn')
kal = [t for t in mm['tables'] if t['name'] == 'Kalendar'][0]
ok(kal.get('dataCategory') == 'Time' and kal['columns'][0].get('isKey'),
   'Kalendar je označen kao tabela datuma')

# relacije
lose = []
for r in mm['relationships']:
    if r['fromColumn'] not in KOL.get(r['fromTable'], {}):
        lose.append('%s[%s]' % (r['fromTable'], r['fromColumn']))
    if r['toColumn'] not in KOL.get(r['toTable'], {}):
        lose.append('%s[%s]' % (r['toTable'], r['toColumn']))
ok(not lose, 'relacije gađaju postojeće kolone %s' % lose)
ok(len({r['name'] for r in mm['relationships']}) == len(mm['relationships']),
   'imena relacija su jedinstvena')
# smer: uvek fact -> dim (many to one); dim strana mora biti jedinstvena kolona
dims = {'Kalendar', 'Emisije', 'Projekti', 'Ugovori', 'Planovi', 'Dobavljaci'}
ok(all(r['toTable'] in dims for r in mm['relationships']),
   'sve relacije vode ka dimenziji (many-to-one)')

# DAX mere
svi_mera = {m for s in MER.values() for m in s}
lose = []
for t in mm['tables']:
    for x in t.get('measures', []):
        dax = '\n'.join(x['expression'])
        for tab, kol in re.findall(r"(\w+)\[([^\]]+)\]", dax):
            if tab not in KOL:
                lose.append('%s: nepoznata tabela %s' % (x['name'], tab))
            elif kol not in KOL[tab] and kol not in MER[tab]:
                lose.append('%s: %s[%s] ne postoji' % (x['name'], tab, kol))
        for ref in re.findall(r"(?<![\w\]])\[([^\]]+)\]", dax):
            if ref not in svi_mera:
                lose.append('%s: mera [%s] ne postoji' % (x['name'], ref))
ok(not lose, 'DAX mere se oslanjaju na postojeće kolone i mere %s' % sorted(set(lose))[:6])

# M kod: izlazne kolone moraju biti tacno deklarisane kolone
def izlazne(txt, ime):
    if ime == 'Kalendar':
        return {'Datum'} | set(re.findall(r'Table\.AddColumn\([^,]+, "([^"]+)"', txt))
    sel = re.search(r'Table\.SelectColumns\([^,]+, \{(.*?)\}\)', txt, re.S)
    imena = re.findall(r'"([^"]+)"', sel.group(1))
    pre = dict(re.findall(r'\{"([^"]+)", "([^"]+)"\}',
                          re.search(r'Table\.RenameColumns\([^,]+, \{(.*?)\}\)',
                                    txt, re.S).group(1))) \
        if 'Table.RenameColumns' in txt else {}
    return {pre.get(x, x) for x in imena}

lose = []
for t in mm['tables']:
    izl = izlazne(M_TXT[t['name']], t['name'])
    dekl = set(KOL[t['name']])
    if izl != dekl:
        lose.append('%s: samo u M %s, samo u modelu %s'
                    % (t['name'], sorted(izl - dekl), sorted(dekl - izl)))
ok(not lose, 'M kod vraća tačno deklarisane kolone')
for x in lose:
    print('        ' + x)

# M kod: svaka kolona koja se bira mora negde da postoji
import sys as _s
_s.path.insert(0, os.path.join(os.path.dirname(BASE), 'er', 'generator'))
from schema import TABLES as _T
SEMA = {t['name']: [c['n'] for c in t['cols']] for t in _T}
lose = []
for t in mm['tables']:
    txt = M_TXT[t['name']]
    dostupne = set()
    for tab in re.findall(r'Tabela\("([A-Z_]+)"\)', txt):
        dostupne |= set(SEMA.get(tab, []))
    for m2 in re.finditer(r'Table\.ExpandTableColumn\([^,]+, "[^"]+", \{(.*?)\}'
                          r'(?:, \{(.*?)\})?\)', txt, re.S):
        nova = m2.group(2) or m2.group(1)
        dostupne |= set(re.findall(r'"([^"]+)"', nova))
    dostupne |= set(re.findall(r'Table\.AddColumn\([^,]+, "([^"]+)"', txt))
    for m2 in re.finditer(r'Table\.Group\(.*?\{(.*?)\},\s*\{(.*?)\}\)', txt, re.S):
        dostupne |= set(re.findall(r'"([^"]+)"', m2.group(1)))
        dostupne |= set(re.findall(r'\{\{?"([^"]+)", each', m2.group(2)))
    sel = re.search(r'Table\.SelectColumns\([^,]+, \{(.*?)\}\)', txt, re.S)
    if not sel:
        continue
    for k in re.findall(r'"([^"]+)"', sel.group(1)):
        if k not in dostupne:
            lose.append('%s: %s' % (t['name'], k))
ok(not lose, 'svaka kolona u Table.SelectColumns postoji u lancu %s' % sorted(set(lose))[:8])

# M kod: sve osnovne tabele koje se citaju moraju biti u Tipovi
tra = set()
for txt in M_TXT.values():
    tra |= set(re.findall(r'Tabela\("([A-Z_]+)"\)', txt))
ok(tra <= set(OSNOVNE), 'sve čitane tabele su u listi tipova %s' % sorted(tra - set(OSNOVNE)))
ok(tra <= set(os.path.splitext(f)[0] for f in os.listdir(os.path.join(PB, 'csv'))),
   'za svaku čitanu tabelu postoji CSV')
izr = {e['name'] for e in mm['expressions']}
ok(izr == {'Izvor', 'PutDoBaze', 'PutDoCsv', 'Tipovi', 'Tabela'},
   'parametri i pomoćni izrazi: %s' % sorted(izr))
tabela_m = [e for e in mm['expressions'] if e['name'] == 'Tabela'][0]
t_txt = '\n'.join(tabela_m['expression'])
for potreban in ('Izvor', 'PutDoCsv', 'PutDoBaze', 'Tipovi'):
    ok(potreban in t_txt, 'funkcija Tabela koristi %s' % potreban)

print('== izvestaj')
ok(len(R['sections']) == 5, 'strana: %d' % len(R['sections']))
json.loads(R['config'])
ok(True, 'config izveštaja je ispravan JSON')
uk_viz, lose, prekl = 0, [], []
for s in R['sections']:
    json.loads(s['filters'])
    imena = set()
    okviri = []
    for vc in s['visualContainers']:
        uk_viz += 1
        cfg = json.loads(vc['config'])
        imena.add(cfg['name'])
        sv = cfg['singleVisual']
        p = cfg['layouts'][0]['position']
        for k in ('x', 'y', 'width', 'height'):
            if vc[k] != float(p[k]):
                lose.append('%s/%s: %s se ne poklapa sa layouts' % (s['name'], cfg['name'], k))
        if p['x'] < 0 or p['y'] < 0 or p['x'] + p['width'] > 1280 or p['y'] + p['height'] > 720:
            lose.append('%s/%s: izlazi iz platna' % (s['name'], cfg['name']))
        okviri.append((p['x'], p['y'], p['width'], p['height'], cfg['name']))
        if sv['visualType'] == 'textbox':
            continue
        q = sv['prototypeQuery']
        alias = {f['Name']: f['Entity'] for f in q['From']}
        for f in q['From']:
            if f['Entity'] not in KOL:
                lose.append('%s: nepoznata tabela %s' % (cfg['name'], f['Entity']))
        nazivi = set()
        for sel in q['Select']:
            kind = 'Measure' if 'Measure' in sel else 'Column'
            izr2 = sel[kind]
            ent = alias.get(izr2['Expression']['SourceRef']['Source'])
            prop = izr2['Property']
            nazivi.add(sel['Name'])
            if sel['Name'] != '%s.%s' % (ent, prop):
                lose.append('%s: Name %s ne odgovara %s.%s' % (cfg['name'], sel['Name'], ent, prop))
            if kind == 'Measure' and prop not in MER.get(ent, set()):
                lose.append('%s: mera %s[%s] ne postoji' % (cfg['name'], ent, prop))
            if kind == 'Column' and prop not in KOL.get(ent, {}):
                lose.append('%s: kolona %s[%s] ne postoji' % (cfg['name'], ent, prop))
        for uloga, lista in sv['projections'].items():
            for pr in lista:
                if pr['queryRef'] not in nazivi:
                    lose.append('%s: queryRef %s nije u upitu' % (cfg['name'], pr['queryRef']))
        if 'OrderBy' in q:
            for o in q['OrderBy']:
                kind = 'Measure' if 'Measure' in o['Expression'] else 'Column'
                e2 = o['Expression'][kind]
                if e2['Expression']['SourceRef']['Source'] not in alias:
                    lose.append('%s: OrderBy koristi nepoznat alias' % cfg['name'])
    if len(imena) != len(s['visualContainers']):
        lose.append('%s: imena vizuala nisu jedinstvena' % s['name'])
    for i in range(len(okviri)):
        for j in range(i + 1, len(okviri)):
            x1, y1, w1, h1, n1 = okviri[i]
            x2, y2, w2, h2, n2 = okviri[j]
            if x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1:
                prekl.append('%s: %s x %s' % (s['name'], n1, n2))
ok(not lose, 'vizuali se oslanjaju na postojeća polja i staju na platno')
for x in sorted(set(lose))[:10]:
    print('        ' + x)
ok(not prekl, 'nema preklapanja vizuala (%d)' % len(prekl))
for x in prekl[:8]:
    print('        ' + x)
ok(uk_viz == 61, 'vizuala ukupno: %d' % uk_viz)
imena_strana = [s['displayName'] for s in R['sections']]
ok(len(set(imena_strana)) == 5, 'imena strana: %s' % imena_strana)

print()
if g:
    print('NEISPRAVNO: %d' % len(g))
    sys.exit(1)
print('SVE PROVERE PROSLE')
