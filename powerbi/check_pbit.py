# -*- coding: utf-8 -*-
"""Provera .pbit paketa: delovi, kodiranje, JSON i poklapanje sa generatorom."""
import json, os, re, sys, zipfile
BASE = os.path.dirname(os.path.abspath(__file__))
from gen_pbip import model_bim, NAZIV
from gen_pbit import layout, CONTENT_TYPES, VERZIJA

g = []
def ok(c, p):
    print(('  OK   ' if c else '  GRESKA ') + p)
    if not c:
        g.append(p)

DELOVI = ['[Content_Types].xml', 'Version', 'DataModelSchema', 'Report/Layout']
SEMA = json.dumps(model_bim(), ensure_ascii=False, sort_keys=True)
IZGLED = json.dumps(layout(), ensure_ascii=False, sort_keys=True)

for ime, bom in (('%s.pbit' % NAZIV, True), ('%s_bez_BOM.pbit' % NAZIV, False)):
    put = os.path.join(BASE, ime)
    print('== %s' % ime)
    ok(os.path.exists(put), 'fajl postoji')
    z = zipfile.ZipFile(put)
    imena = z.namelist()
    ok(imena == DELOVI, 'delovi paketa i njihov redosled: %s' % imena)
    ok(z.testzip() is None, 'zip nije oštećen')

    ct = z.read('[Content_Types].xml').decode('utf-8')
    ok(ct == CONTENT_TYPES, '[Content_Types].xml se poklapa sa generatorom')
    navedeni = re.findall(r'PartName="/([^"]+)"', ct)
    ok(sorted(navedeni) == sorted(x for x in DELOVI if x != '[Content_Types].xml'),
       'Content_Types navodi tačno prisutne delove: %s' % navedeni)

    for deo in ('Version', 'DataModelSchema', 'Report/Layout'):
        sirovo = z.read(deo)
        ok(len(sirovo) % 2 == 0, '%s ima paran broj bajtova (UTF-16)' % deo)
        t = sirovo.decode('utf-16-le')
        ok(t.startswith('﻿') == bom,
           '%s %s BOM, kako je i traženo' % (deo, 'ima' if bom else 'nema'))
        t = t.lstrip('﻿')
        if deo == 'Version':
            ok(t == VERZIJA, 'Version = %s' % t)
        else:
            try:
                d = json.loads(t)
                ok(True, '%s je ispravan JSON' % deo)
            except Exception as e:
                ok(False, '%s nije ispravan JSON: %s' % (deo, e))
                continue
            sada = json.dumps(d, ensure_ascii=False, sort_keys=True)
            if deo == 'DataModelSchema':
                ok(sada == SEMA, 'DataModelSchema je isti model kao u .pbip projektu')
            else:
                ok(sada == IZGLED, 'Report/Layout je isti izveštaj kao u .pbip projektu')
                ok(len(d['sections']) == 5, 'pet strana u jednom fajlu')
                ok(sum(len(s['visualContainers']) for s in d['sections']) == 61,
                   '61 vizual')

# sadrzaj modela u .pbit mora biti isti kao u .pbip (jedan izvor istine)
pbip = os.path.join(BASE, 'pbip', NAZIV + '.SemanticModel', 'model.bim')
if os.path.exists(pbip):
    with open(pbip, encoding='utf-8') as f:
        d = json.load(f)
    ok(json.dumps(d, ensure_ascii=False, sort_keys=True) == SEMA,
       'model.bim u .pbip projektu je identičan onom u .pbit')

print()
if g:
    print('NEISPRAVNO: %d' % len(g))
    sys.exit(1)
print('SVE PROVERE PROSLE')
