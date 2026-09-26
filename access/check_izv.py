# -*- coding: utf-8 -*-
"""Provera modula TV_Stanica_Izvestaji.bas pre isporuke.

Provera se vrsi i prema semi baze Access_v1.accdb: imena novih objekata ne
smeju da se poklope sa postojecim, a sva polja u izvestajima moraju da
postoje u izlazu odgovarajuceg upita.
"""
import io, os, re, sys, json
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(BASE), 'er', 'generator'))
from izv_upiti import U as UPITI
from gen_izv_access import STAVKE

txt = io.open(os.path.join(BASE, 'TV_Stanica_Izvestaji.bas'), encoding='latin-1').read()
lines = txt.replace('\r\n', '\n').split('\n')
g = []

def ok(c, p):
    print(('  OK   ' if c else '  GRESKA ') + p)
    if not c:
        g.append(p)

print('== .bas fajl')
bad = [c for l in lines for c in l if ord(c) > 126]
ok(not bad, 'cist ASCII (%d spornih znakova)' % len(bad))
ok(max(len(l) for l in lines) <= 1023,
   'nijedna linija duza od 1023 znaka (max %d)' % max(len(l) for l in lines))
for a, b, ime in (('Sub', 'End Sub', 'Sub'), ('Function', 'End Function', 'Function')):
    n1 = len(re.findall(r'(?m)^\s*(?:Public |Private )?%s \w+' % a, txt))
    n2 = len(re.findall(r'(?m)^\s*%s\s*$' % b, txt))
    ok(n1 == n2, '%s/End %s: %d/%d' % (ime, ime, n1, n2))
ok(len(re.findall(r'(?m)^\s*Select Case ', txt)) == len(re.findall(r'(?m)^\s*End Select\s*$', txt)),
   'Select Case/End Select uravnotezeni')
ok(len(re.findall(r'(?m)^\s*Do While ', txt)) == len(re.findall(r'(?m)^\s*Loop\s*$', txt)),
   'Do While/Loop uravnotezeni')

# ---------------------------------------------------------------- bezbednost
print('== bezbednost (ne sme se dirati nista postojece)')
for poz, pref, kon in (('ObrisiUpit', 'qIzv', 'P_UPIT'),
                       ('ObrisiIzvestaj', 'rptIzv', 'P_IZV'),
                       ('ObrisiFormu', 'frmIzvestaji', 'P_FORMA')):
    arg = re.findall(r'%s "([^"]+)"' % poz, txt)
    los = [a for a in arg if not a.startswith(pref)]
    ok(not los, '%s se poziva samo sa prefiksom %s (%d poziva) %s' % (poz, pref, len(arg), los))
    telo = txt[txt.index('Private Sub %s(' % poz):]
    telo = telo[:telo.index('End Sub')]
    ok('Left(ime, Len(%s)) <> %s' % (kon, kon) in telo,
       '%s odbija ime bez prefiksa %s' % (poz, pref))
ok('Private Const P_UPIT As String = "qIzv"' in txt and
   'Private Const P_IZV As String = "rptIzv"' in txt and
   'Private Const P_FORMA As String = "frmIzvestaji"' in txt,
   'prefiksi su definisani kao konstante')
ok('DoCmd.DeleteObject acTable' not in txt and 'TableDefs.Delete' not in txt,
   'nijedna tabela se ne brise')
napravljeni = re.findall(r'Upit "([^"]+)"', txt)
ok(all(n.startswith('qIzv') for n in napravljeni),
   'svi upiti nose prefiks qIzv (%d)' % len(napravljeni))
izvestaji = re.findall(r'Kraj r, "([^"]+)"', txt)
ok(all(n.startswith('rptIzv') for n in izvestaji),
   'svi izvestaji nose prefiks rptIzv (%d)' % len(izvestaji))
forme = re.findall(r'DoCmd.Rename "([^"]+)", acForm', txt)
ok(forme == ['frmIzvestaji'], 'jedina nova forma je frmIzvestaji (%s)' % forme)
ok('acSaveYes' in txt and 'DoCmd.Close acForm' in txt, 'forma se zatvara sa cuvanjem')

# ---------------------------------------------------------------- sadrzaj
print('== sadrzaj')
ok(len(napravljeni) == len(UPITI), 'upita: %d (definisano %d)' % (len(napravljeni), len(UPITI)))
ok(sorted(napravljeni) == sorted(n for n, _ in UPITI), 'imena upita se poklapaju')
glavni = [n for n in izvestaji if re.match(r'rptIzv\d$', n)]
ok(len(glavni) == 8, 'osam glavnih izvestaja: %s' % sorted(glavni))
ok(len(izvestaji) == 10, 'ukupno izvestaja (8 + 2 podizvestaja): %d' % len(izvestaji))
par = [n for n, s in UPITI if 'PARAMETERS' in s]
ok(len(par) == 2, 'dva parametarska upita: %s' % par)
ok(txt.count('    Grafikon r,') == 2, 'dva graficka prikaza u izvestaju 3')
ok(txt.count('    Pod r,') == 2, 'dva podizvestaja ugradjena')
ok(len(STAVKE) == 8, 'meni ima osam dugmadi')

# ---------------------------------------------------------------- polja upita
def izlaz(sql):
    """Imena kolona koje upit vraca."""
    s = re.sub(r'^\s*PARAMETERS.*?;', '', sql, flags=re.S)
    i = re.search(r'\bSELECT\b', s, re.I).end()
    dub, j = 0, i
    while j < len(s):                      # FROM na nivou nula, ne unutar podupita
        if s[j] == '(':
            dub += 1
        elif s[j] == ')':
            dub -= 1
        elif dub == 0 and s[j:j + 4].upper() == 'FROM' and not s[j - 1].isalnum():
            break
        j += 1
    telo = s[i:j]
    delovi, d, dub = [], '', 0
    for ch in telo:
        if ch == '(':
            dub += 1
        elif ch == ')':
            dub -= 1
        if ch == ',' and dub == 0:
            delovi.append(d); d = ''
        else:
            d += ch
    delovi.append(d)
    out = []
    for dd in delovi:
        dd = dd.strip()
        m = re.search(r'\bAS\s+([A-Za-z_][\w]*)\s*$', dd, re.I)
        if m:
            out.append(m.group(1))
        else:
            out.append(dd.split('.')[-1].strip('[] '))
    return set(out)

SQL = dict(UPITI)
IZLAZ = {n: izlaz(s) for n, s in UPITI}

# koji izvestaj koristi koji upit + koja polja
bloks = re.split(r'(?m)^Private Sub (Izvestaj\w*)\(\)', txt)
mapa = {}
for i in range(1, len(bloks), 2):
    mapa[bloks[i]] = bloks[i + 1]
lose = []
for sub, telo in mapa.items():
    m = re.search(r'r = Poc\("([^"]+)"\)', telo)
    if not m:
        continue
    upit = m.group(1)
    kol = IZLAZ[upit]
    for izv in re.findall(r'Txt r, \w+, [\d\-]+, [\d\-]+, \d+, \d+, "([^"]+)"', telo):
        if izv.startswith('='):
            for p in re.findall(r'\[([A-Z][A-Z0-9_]+)\]', izv):
                if p not in kol:
                    lose.append('%s(%s): [%s]' % (sub, upit, p))
        elif izv not in kol:
            lose.append('%s(%s): %s' % (sub, upit, izv))
    for p in re.findall(r'Gr r, "([^"]+)"', telo):
        if p not in kol:
            lose.append('%s(%s): grupa %s' % (sub, upit, p))
ok(not lose, 'sva polja izvestaja postoje u upitu %s' % sorted(set(lose))[:8])

# ---------------------------------------------------------------- sirine i preklapanja
print('== raspored')
for sub, telo in mapa.items():
    m = re.search(r'Kraj r, "([^"]+)", "[^"]*", (\d+), (True|False)', telo)
    if not m:
        continue
    ime, w, pejzaz = m.group(1), int(m.group(2)), m.group(3) == 'True'
    lim = 16100 if pejzaz else 11200
    ok(w <= lim, '%s sirina %d twips (granica %d, %s)'
       % (ime, w, lim, 'pejzaz' if pejzaz else 'portret'))
    # desna ivica svake kontrole
    maxx = 0
    for kind, sek, x, y, cw, ch in re.findall(
            r'(Lab|Txt|Lin|Grafikon|Pod) r, (\w+), (\d+), (\d+), (\d+), (\d+)', telo):
        maxx = max(maxx, int(x) + int(cw))
    ok(maxx <= w, '%s: najdesnija kontrola na %d (sirina %d)' % (ime, maxx, w))

# preklapanja unutar sekcije (isti y opseg)
prekl = []
for sub, telo in mapa.items():
    po_sek = {}
    for kind, sek, x, y, cw, ch in re.findall(
            r'(Lab|Txt|Grafikon|Pod) r, (\w+), (\d+), (\d+), (\d+), (\d+)', telo):
        po_sek.setdefault(sek, []).append((int(x), int(y), int(cw), int(ch), kind))
    for sek, lst in po_sek.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                x1, y1, w1, h1, k1 = lst[i]
                x2, y2, w2, h2, k2 = lst[j]
                if x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1:
                    prekl.append('%s/%s: (%d,%d,%d,%d) %s x (%d,%d,%d,%d) %s'
                                 % (sub, sek, x1, y1, w1, h1, k1, x2, y2, w2, h2, k2))
ok(not prekl, 'nema preklapanja kontrola (%d)' % len(prekl))
if prekl:
    for p in prekl[:12]:
        print('        ' + p)

# ---------------------------------------------------------------- sema baze
sema = os.path.join(BASE, 'sema_accdb.json')
if os.path.exists(sema):
    acc = json.load(open(sema))
    postojeci = set(acc.get('_objekti', []))
    if postojeci:
        novi = set(napravljeni) | set(izvestaji) | {'frmIzvestaji', 'modIzvestaji'}
        sudar = sorted(novi & postojeci)
        ok(not sudar, 'nijedno novo ime ne postoji u bazi %s' % sudar)
    # polja u upitima moraju postojati u tabelama
    tab = {k: set(v['kolone']) for k, v in acc.items() if not k.startswith('_')}
    lose = []
    for n, sql in UPITI:
        al = dict(re.findall(r'\b([A-Z][A-Z0-9_]{2,})\s+AS\s+([A-Z]{1,3})\b', sql))
        al = {v: k for k, v in al.items()}
        for a, c in re.findall(r'\b([A-Z]{1,3})\.([A-Z][A-Z0-9_]+)\b', sql):
            if a in al and al[a] in tab and c not in tab[al[a]]:
                lose.append('%s: %s.%s' % (n, al[a], c))
    ok(not lose, 'kolone u upitima postoje u tabelama baze %s' % sorted(set(lose))[:6])
else:
    print('  (sema_accdb.json nije pronadjena - preskacem proveru prema bazi)')

print()
if g:
    print('NEISPRAVNO: %d' % len(g))
    sys.exit(1)
print('SVE PROVERE PROSLE')
