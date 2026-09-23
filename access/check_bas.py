# -*- coding: utf-8 -*-
"""Provera generisanog .bas modula pre isporuke."""
import os, sys, re, io
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(BASE), 'er', 'generator'))
from schema import TABLES
from demo_data import D as DEMO
from upiti import U as UPITI
from gen_access import IZV
BY = {t['name']: t for t in TABLES}

txt = io.open(os.path.join(BASE, 'TV_Stanica_Access.bas'), encoding='latin-1').read()
lines = txt.replace('\r\n', '\n').split('\n')
g = []
def ok(c, p):
    print(('  OK   ' if c else '  GRESKA ') + p)
    if not c: g.append(p)

print('== .bas fajl')
bad = [(i+1, c) for i, l in enumerate(lines) for c in l if ord(c) > 126]
ok(not bad, 'cist ASCII (%d spornih znakova)' % len(bad))
dug = [i+1 for i, l in enumerate(lines) if len(l) > 1023]
ok(not dug, 'nijedna linija duza od 1023 znaka (max %d)' % max(len(l) for l in lines))

# balans procedura
subs = len(re.findall(r'(?m)^\s*(?:Public |Private )?Sub \w+', txt))
esubs = len(re.findall(r'(?m)^\s*End Sub\s*$', txt))
fun = len(re.findall(r'(?m)^\s*(?:Public |Private )?Function \w+', txt))
efun = len(re.findall(r'(?m)^\s*End Function\s*$', txt))
ok(subs == esubs, 'Sub/End Sub: %d/%d' % (subs, esubs))
ok(fun == efun, 'Function/End Function: %d/%d' % (fun, efun))
ok(txt.count('If ') >= txt.count('End If'), 'If/End If nije neuravnotezen')
sel = len(re.findall(r'(?m)^\s*Select Case ', txt))
esel = len(re.findall(r'(?m)^\s*End Select\s*$', txt))
ok(sel == esel, 'Select Case/End Select: %d/%d' % (sel, esel))
fo = len(re.findall(r'(?m)^\s*For (?:i|Each) ', txt))
nx = len(re.findall(r'(?m)^\s*Next', txt))
ok(fo == nx, 'For/Next: %d/%d' % (fo, nx))

# nastavak linije
loscont = [i+1 for i, l in enumerate(lines) if l.rstrip().endswith(' _') and
           not re.search(r'[,&(=\s]\s*_$', l.rstrip())]
ok(not loscont, 'ispravan nastavak linije ( _ )')

# definicije i pozivi
defs = set(re.findall(r'(?m)^\s*(?:Public |Private )?(?:Sub|Function) (\w+)', txt))
m = re.search(r'Public Sub KreirajSve\(\)(.*?)\nEnd Sub', txt, re.S)
pozvani = set(re.findall(r'(?m)^    ([A-Z]\w+)\s*$', m.group(1)))
ok(pozvani <= defs, 'sve procedure iz KreirajSve postoje (%s)' % sorted(pozvani - defs))

print('== sadrzaj')
tabele = re.findall(r'(?m)^    NapraviTabelu "(\w+)"', txt)
ok(len(tabele) == len(TABLES), 'tabela: %d (sema %d)' % (len(tabele), len(TABLES)))
ok(sorted(tabele) == sorted(BY), 'imena tabela se poklapaju sa semom')
forme = re.findall(r'(?m)^    NapraviFormu "(\w+)"', txt)
ok(sorted(forme) == sorted(BY), 'forma po tabeli: %d' % len(forme))
pk = re.findall(r'(?m)^    PK "(\w+)"', txt)
ok(sorted(pk) == sorted(BY), 'primarni kljuc za svaku tabelu: %d' % len(pk))
fk = re.findall(r'(?m)^    FK "', txt)
ukFk = sum(len(t['fks']) for t in TABLES)
ok(len(fk) == ukFk, 'veza: %d (sema %d)' % (len(fk), ukFk))
up = re.findall(r'(?m)^    NapraviUpit "(\w+)", s', txt)
ok(len(up) == len(UPITI), 'upita: %d' % len(up))
par = [n for n, s in UPITI if 'PARAMETERS' in s]
ok(len(par) >= 2, 'parametarskih upita: %d %s' % (len(par), par))
izv = re.findall(r'(?m)^    r = NapraviIzvestaj\("(\w+)"', txt)
ok(len(izv) == len(IZV), 'izvestaja (ukljucujuci podizvestaje): %d' % len(izv))
gl = [d for d in IZV if d['naslov'].startswith('Izve')]
ok(len(gl) == 8, 'numerisanih izvestaja iz specifikacije: %d' % len(gl))
ok(txt.count('DodajGrafikon "') == 1, 'jedan izvestaj sa grafickim prikazom')
ok(txt.count('DodajPodizvestaj "') == 2, 'dva podizvestaja')

print('== polja')
lose = []
for t in TABLES:
    for c in t['cols']:
        if len(c['n']) > 64: lose.append(c['n'])
ok(not lose, 'nijedno ime polja duze od 64 znaka')

# demo: obavezna polja i postojanje kolona
nedostaje, nepostoje, brRedova = [], [], 0
for tab, kol, redovi in DEMO:
    t = BY[tab]
    imena = [c.strip() for c in kol.split(',')]
    sve = {c['n'] for c in t['cols']}
    for c in imena:
        if c not in sve: nepostoje.append('%s.%s' % (tab, c))
    for c in t['cols']:
        if not c['null'] and c['n'] not in imena:
            nedostaje.append('%s.%s' % (tab, c['n']))
    for r in redovi:
        brRedova += 1
        if len(r) != len(imena):
            nepostoje.append('%s: %d vrednosti za %d kolona' % (tab, len(r), len(imena)))
ok(not nepostoje, 'demo kolone postoje u semi %s' % nepostoje[:5])
ok(not nedostaje, 'demo redovi popunjavaju sva obavezna polja %s' % nedostaje[:8])
print('       demo redova: %d, blokova: %d' % (brRedova, len(DEMO)))

# izvestaji: kolone moraju postojati u SELECT listi upita
SQL = dict(UPITI)
prom = []
for d in IZV:
    s = SQL[d['upit']]
    izlaz = set(re.findall(r'\b(?:AS\s+)?([A-Z][A-Z0-9_]{2,})\b', s))
    for k, w in d['kolone']:
        if k not in izlaz: prom.append('%s.%s' % (d['ime'], k))
    for k in [x for x in (d['grupa'], ) if x] + [x for x in d['sume'].split('|') if x]:
        if k not in izlaz: prom.append('%s.%s (grupa/suma)' % (d['ime'], k))
ok(not prom, 'kolone izvestaja postoje u upitu %s' % prom[:6])

# sirina izvestaja <= A4
for d in IZV:
    uk = sum(w for _, w in d['kolone'])
    lim = 15100 if d['pejzaz'] else 10500
    ok(uk <= lim, '%s sirina %d twips (granica %d)' % (d['ime'], uk, lim))

# upiti: svaka kvalifikovana kolona mora postojati u semi
lose = []
for n, sql in UPITI:
    al = dict(re.findall(r'\b([A-Z][A-Z0-9_]{2,})\s+AS\s+([A-Z]{1,3})\b', sql))
    al = {v: k for k, v in al.items()}
    for a, c in re.findall(r'\b([A-Z]{1,3})\.([A-Z][A-Z0-9_]+)\b', sql):
        if a not in al:
            lose.append('%s: nepoznat alias %s' % (n, a))
        elif a in al and c not in {x['n'] for x in BY[al[a]]['cols']}:
            lose.append('%s: %s.%s ne postoji' % (n, al[a], c))
ok(not lose, 'kolone u upitima postoje u semi %s' % sorted(set(lose))[:5])

print()
if g:
    print('NEISPRAVNO: %d' % len(g)); sys.exit(1)
print('SVE PROVERE PROSLE')
