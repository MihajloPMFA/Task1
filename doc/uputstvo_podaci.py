# -*- coding: utf-8 -*-
"""Izvlači tačan raspored svih osam izveštaja iz generatora modula modIzvestaji
i tekst zahteva iz Specifikacije izveštaja, pa piše uputstvo_podaci.json.

Time je Word uputstvo izvedeno iz istog izvora kao i VBA modul, pa ne može da
se razmine sa njim.
"""
import json, os, re, sys, zipfile
BASE = os.path.dirname(os.path.abspath(__file__))
KOREN = os.path.dirname(BASE)
sys.path.insert(0, os.path.join(KOREN, 'access'))
import gen_izv_access as G
from izv_upiti import U as UPITI

SPEC = '/root/.claude/uploads/b6283403-6c49-54be-ba3f-14272bcdf06f/8c69bf4a-Specifikacija_izvestaja.docx'
TWIP_CM = 567.0

# ---------------------------------------------------------------- srpska slova
NAZAD = {v: k for k, v in G.MARK.items()}

def dec(s):
    for m, c in NAZAD.items():
        s = s.replace(m, c)
    return s

def cm(t):
    return '%.2f' % (t / TWIP_CM)

# ---------------------------------------------------------------- sekcije
SEK = {
 'acHeader': ('Zaglavlje izveštaja', 'Report Header'),
 'acPageHeader': ('Zaglavlje strane', 'Page Header'),
 'acGroupLevel1Header': ('Zaglavlje grupe 1', 'Group Header 1'),
 'acGroupLevel2Header': ('Zaglavlje grupe 2', 'Group Header 2'),
 'acDetail': ('Detalji', 'Detail'),
 'acGroupLevel2Footer': ('Podnožje grupe 2', 'Group Footer 2'),
 'acGroupLevel1Footer': ('Podnožje grupe 1', 'Group Footer 1'),
 'acFooter': ('Podnožje izveštaja', 'Report Footer'),
 'acPageFooter': ('Podnožje strane', 'Page Footer'),
}
RED = ['acHeader', 'acPageHeader', 'acGroupLevel1Header', 'acGroupLevel2Header',
       'acDetail', 'acGroupLevel2Footer', 'acGroupLevel1Footer', 'acFooter',
       'acPageFooter']
PORAVNANJE = {1: 'levo', 2: 'centar', 3: 'desno'}

# ---------------------------------------------------------------- parsiranje VBA
def niska(s):
    return dec(s.replace('""', '"'))

def parsiraj(linije, sirina_pl=None):
    """Vrati opis jednog izveštaja iz VBA linija koje generator emituje."""
    d = dict(upit=None, ime=None, naslov=None, sirina=None, pejzaz=None,
             grupe=[], visine={}, kontrole={}, grafikoni=[], podizvestaji=[])
    for l in linije:
        t = l.strip()
        m = re.match(r'r = Poc\("([^"]+)"\)$', t)
        if m:
            d['upit'] = m.group(1); continue
        m = re.match(r'Gr r, "([^"]+)", (True|False), (True|False)$', t)
        if m:
            d['grupe'].append(dict(polje=m.group(1), zaglavlje=m.group(2) == 'True',
                                   podnozje=m.group(3) == 'True')); continue
        m = re.match(r'Sek r, (\w+), (\d+)(, True)?$', t)
        if m:
            d['visine'][m.group(1)] = dict(visina=int(m.group(2)),
                                           raste=bool(m.group(3))); continue
        # opcioni argumenti se hvataju pojedinacno - format ume da sadrzi zapetu
        # (npr. "#,##0.00"), pa se ostatak linije ne sme deliti po zapetama
        m = re.match(r'(Lab|Txt) r, (\w+), (\d+), (\d+), (\d+), (\d+), '
                     r'"((?:[^"]|"")*)"'
                     r'(?:, (\d+))?(?:, (True|False))?(?:, (\d+))?'
                     r'(?:, "((?:[^"]|"")*)")?$', t)
        if m:
            vrsta, sek = m.group(1), m.group(2)
            x, y, w, h = (int(m.group(i)) for i in (3, 4, 5, 6))
            vel = int(m.group(8)) if m.group(8) else 9
            bold = m.group(9) == 'True'
            por = int(m.group(10)) if m.group(10) else 1
            fmt = niska(m.group(11)) if m.group(11) else ''
            d['kontrole'].setdefault(sek, []).append(dict(
                vrsta=('Natpis' if vrsta == 'Lab' else 'Polje'),
                sadrzaj=niska(m.group(7)), x=x, y=y, w=w, h=h,
                vel=vel, bold=bold, por=PORAVNANJE[por], fmt=fmt))
            continue
        m = re.match(r'Lin r, (\w+), (\d+), (\d+), (\d+)$', t)
        if m:
            d['kontrole'].setdefault(m.group(1), []).append(dict(
                vrsta='Linija', sadrzaj='-', x=int(m.group(2)), y=int(m.group(3)),
                w=int(m.group(4)), h=0, vel='', bold=False, por='', fmt=''))
            continue
        m = re.match(r'Grafikon r, (\w+), (\d+), (\d+), (\d+), (\d+), "([^"]+)"$', t)
        if m:
            d['grafikoni'].append(dict(sek=m.group(1), x=int(m.group(2)),
                                       y=int(m.group(3)), w=int(m.group(4)),
                                       h=int(m.group(5)), upit=m.group(6)))
            continue
        m = re.match(r'Pod r, (\w+), (\d+), (\d+), (\d+), (\d+), "([^"]+)"'
                     r'(?:, "([^"]*)", "([^"]*)")?$', t)
        if m:
            d['podizvestaji'].append(dict(sek=m.group(1), x=int(m.group(2)),
                                          y=int(m.group(3)), w=int(m.group(4)),
                                          h=int(m.group(5)), izvestaj=m.group(6),
                                          master=m.group(7) or '', dete=m.group(8) or ''))
            continue
        m = re.match(r'Podnozje r, (\d+)$', t)
        if m:
            W = int(m.group(1))
            d['visine']['acPageFooter'] = dict(visina=360, raste=False)
            k = d['kontrole'].setdefault('acPageFooter', [])
            k.append(dict(vrsta='Linija', sadrzaj='-', x=0, y=40, w=W, h=0,
                          vel='', bold=False, por='', fmt=''))
            k.append(dict(vrsta='Polje', sadrzaj='=Now()', x=0, y=100, w=3400, h=240,
                          vel=8, bold=False, por='levo', fmt='dd.mm.yyyy. hh:nn'))
            k.append(dict(vrsta='Polje', sadrzaj='="Izradio: " & CurrentUser()',
                          x=3500, y=100, w=4600, h=240, vel=8, bold=False,
                          por='levo', fmt=''))
            k.append(dict(vrsta='Polje',
                          sadrzaj='="Strana " & [Page] & " od " & [Pages]',
                          x=W - 3100, y=100, w=3000, h=240, vel=8, bold=False,
                          por='desno', fmt=''))
            continue
        m = re.match(r'Kraj r, "([^"]+)", "((?:[^"]|"")*)", (\d+), (True|False)$', t)
        if m:
            d['ime'] = m.group(1)
            d['naslov'] = niska(m.group(2))
            d['sirina'] = int(m.group(3))
            d['pejzaz'] = m.group(4) == 'True'
            continue
    return d

# ---------------------------------------------------------------- specifikacija
def spec():
    x = zipfile.ZipFile(SPEC).read('word/document.xml').decode('utf-8')
    def cist(frag):
        # <w:t> ili <w:t xml:space="...">, ali NE <w:tcPr> i slicni tagovi
        t = ''.join(re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', frag, re.S))
        return t.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip()
    red = []
    for m in re.finditer(r'<w:tbl\b.*?</w:tbl>|<w:p\b.*?</w:p>', x, re.S):
        frag = m.group(0)
        if frag.startswith('<w:tbl'):
            for tc in re.findall(r'<w:tc\b.*?</w:tc>', frag, re.S):
                t = cist(tc)
                if t:
                    red.append(t)
        else:
            t = cist(frag)
            if t:
                red.append(t)
    KLJ = ['ID izveštaja', 'Naziv', 'Tip izveštaja', 'Svrha', 'Izvor podataka',
           'Parametri', 'Učestalost i raspodela', 'Zaglavlje i podnožje',
           'Telo izveštaja', 'Pristup izveštaju']
    out, tek, i = {}, None, 0
    while i < len(red):
        m = re.match(r'Izveštaj (\d) ', red[i])
        if m:
            tek = int(m.group(1)); out[tek] = {}
        elif tek and red[i] in KLJ and i + 1 < len(red):
            out[tek][red[i]] = red[i + 1]; i += 1
        i += 1
    return out

# ---------------------------------------------------------------- sklapanje
IZVESTAJI = [
    (1, G.izv1, None), (2, G.izv2, None), (3, G.izv3, None), (4, G.izv4, None),
    (5, G.izv5, G.izv5oprema), (6, G.izv6, None), (7, G.izv7, G.izv7ponude),
    (8, G.izv8, None),
]

def main():
    S = spec()
    SQL = dict(UPITI)
    izv = []
    for broj, fja, podf in IZVESTAJI:
        d = parsiraj(fja())
        d['broj'] = broj
        d['spec'] = S.get(broj, {})
        d['sql'] = dec(SQL[d['upit']]).strip()
        d['pod'] = None
        if podf:
            p = parsiraj(podf())
            p['sql'] = dec(SQL[p['upit']]).strip()
            d['pod'] = p
        for g in d['grafikoni']:
            g['sql'] = dec(SQL[g['upit']]).strip()
        izv.append(d)
    pom = [(n, dec(s).strip()) for n, s in UPITI
           if n in ('qIzv6_Fakture', 'qIzv7_Zahtev', 'qIzv7_Narudzbe', 'qIzv7_Izabrana')]
    podatak = dict(izvestaji=izv, pomocni=pom, sekcije=SEK, red=RED,
                   twip_cm=TWIP_CM)
    with open(os.path.join(BASE, 'uputstvo_podaci.json'), 'w', encoding='utf-8') as f:
        json.dump(podatak, f, ensure_ascii=False, indent=1)
    uk = sum(len(v) for d in izv for v in d['kontrole'].values())
    uk += sum(len(v) for d in izv if d['pod'] for v in d['pod']['kontrole'].values())
    print('izveštaja: %d' % len(izv))
    print('kontrola ukupno: %d' % uk)
    for d in izv:
        print('  %s  upit %-22s grupa %d  sekcija %d  kontrola %d%s'
              % (d['ime'], d['upit'], len(d['grupe']), len(d['visine']),
                 sum(len(v) for v in d['kontrole'].values()),
                 '  + podizveštaj %s' % d['pod']['ime'] if d['pod'] else ''))
        assert d['spec'], 'nema teksta specifikacije za izveštaj %d' % d['broj']

if __name__ == '__main__':
    main()
