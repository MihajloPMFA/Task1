# -*- coding: utf-8 -*-
"""Provera da Word uputstvo sadrži tačno ono što generator izveštaja emituje."""
import json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
BASE = os.path.dirname(os.path.abspath(__file__))
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
P = json.load(open(os.path.join(BASE, 'uputstvo_podaci.json'), encoding='utf-8'))
DOCX = os.path.join(BASE, 'Uputstvo_izvestaji_Access.docx')

g = []
def ok(c, p):
    print(('  OK   ' if c else '  GRESKA ') + p)
    if not c:
        g.append(p)

z = zipfile.ZipFile(DOCX)
root = ET.fromstring(z.read('word/document.xml'))
body = root.find(W + 'body')

def tekst(el):
    return ''.join(t.text or '' for t in el.iter(W + 't'))

naslovi, tabele, celije = [], [], []
for el in body.iter():
    if el.tag == W + 'p':
        st = el.find(W + 'pPr/' + W + 'pStyle')
        if st is not None and st.get(W + 'val', '').startswith('Heading'):
            naslovi.append((st.get(W + 'val'), tekst(el)))
    elif el.tag == W + 'tbl':
        redovi = [[tekst(tc) for tc in tr.findall(W + 'tc')]
                  for tr in el.findall(W + 'tr')]
        tabele.append(redovi)
        celije += [c for r in redovi for c in r]

print('== struktura dokumenta')
h1 = [t for s, t in naslovi if s.startswith('Heading1')]
ok(len(h1) == 14, 'poglavlja prvog nivoa (Sadržaj + 13): %d' % len(h1))
for i in range(1, 9):
    ok(any(re.match(r'\d+\. Izveštaj %d - ' % i, t) for t in h1),
       'postoji poglavlje za izveštaj %d' % i)
ok(len(tabele) >= 60, 'tabela u dokumentu: %d' % len(tabele))

print('== kontrole')
# tabele kontrola prepoznajemo po zaglavlju
ZAGL = ['#', 'Kontrola', 'Izvor ili tekst', 'Levo', 'Gore', 'Širina', 'Visina', 'Stil']
kt = [t for t in tabele if t and t[0] == ZAGL]
uk_doc = sum(len(t) - 1 for t in kt)
uk_src = sum(len(v) for d in P['izvestaji'] for v in d['kontrole'].values())
uk_src += sum(len(v) for d in P['izvestaji'] if d['pod']
              for v in d['pod']['kontrole'].values())
ok(uk_doc == uk_src, 'kontrola u dokumentu %d, u generatoru %d' % (uk_doc, uk_src))
ok(len(kt) == sum(len(d['kontrole']) for d in P['izvestaji']) +
   sum(len(d['pod']['kontrole']) for d in P['izvestaji'] if d['pod']),
   'tabela kontrola: %d' % len(kt))

# svaka kontrola iz generatora mora postojati u dokumentu sa istim merama
cm = lambda t: '%.2f' % (t / P['twip_cm'])
u_dok = set()
for t in kt:
    for r in t[1:]:
        u_dok.add((r[1], r[2], r[3], r[4], r[5], r[6]))
lose = []
def provera(d):
    for sek, lista in d['kontrole'].items():
        for k in lista:
            kl = (k['vrsta'], k['sadrzaj'], cm(k['x']), cm(k['y']), cm(k['w']),
                  '0' if k['vrsta'] == 'Linija' else cm(k['h']))
            if kl not in u_dok:
                lose.append('%s %s' % (d['ime'], kl))
for d in P['izvestaji']:
    provera(d)
    if d['pod']:
        provera(d['pod'])
ok(not lose, 'svaka kontrola je u dokumentu sa istim merama %s' % lose[:3])

print('== upiti')
sql_u_dok = '\n'.join(tekst(p) for p in body.iter(W + 'p'))
lose = []
for d in P['izvestaji']:
    for ime in [d['upit']] + [gr['upit'] for gr in d['grafikoni']] + \
               ([d['pod']['upit']] if d['pod'] else []):
        if ime not in sql_u_dok:
            lose.append(ime)
for ime, _ in P['pomocni']:
    if ime not in sql_u_dok:
        lose.append(ime)
ok(not lose, 'svi upiti su pomenuti u dokumentu %s' % lose)
# prvi red svakog SQL-a mora biti u dokumentu
lose = []
for d in P['izvestaji']:
    for s in [d['sql']] + [gr['sql'] for gr in d['grafikoni']] + \
             ([d['pod']['sql']] if d['pod'] else []):
        prva = s.split('\n')[0].strip()
        if prva not in sql_u_dok:
            lose.append(prva[:40])
ok(not lose, 'SQL tekst upita je u dokumentu %s' % lose[:3])

print('== formati i grupe')
fm = {k['fmt'] for d in P['izvestaji'] for v in d['kontrole'].values()
      for k in v if k['fmt']}
fm |= {k['fmt'] for d in P['izvestaji'] if d['pod']
       for v in d['pod']['kontrole'].values() for k in v if k['fmt']}
dokumentovani = {c for c in celije}
ok(fm <= dokumentovani, 'svi korišćeni formati su objašnjeni u poglavlju 2.4 %s'
   % sorted(fm - dokumentovani))
grupe = {gr['polje'] for d in P['izvestaji'] for gr in d['grupe']}
ok(grupe <= dokumentovani, 'sva polja grupisanja su u dokumentu %s'
   % sorted(grupe - dokumentovani))
ok(P['izvestaji'][2]['grafikoni'] and len(P['izvestaji'][2]['grafikoni']) == 2,
   'izveštaj 3 ima dva grafikona')
ok(sum(1 for d in P['izvestaji'] if d['pod']) == 2, 'dva izveštaja imaju podizveštaj')

print()
if g:
    print('NEISPRAVNO: %d' % len(g))
    sys.exit(1)
print('SVE PROVERE PROSLE')
