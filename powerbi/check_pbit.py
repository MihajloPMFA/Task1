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

MIN = ['[Content_Types].xml', 'Version', 'DataModelSchema', 'Report/Layout']
PUN = ['[Content_Types].xml', '_rels/.rels', 'Version', 'DataModelSchema',
       'DiagramLayout', 'Metadata', 'Settings', 'Report/Layout']
SEMA = json.dumps(model_bim(), ensure_ascii=False, sort_keys=True)
IZGLED = json.dumps(layout(), ensure_ascii=False, sort_keys=True)

VARIJANTE = [('%s.pbit' % NAZIV, True, False),
             ('%s_bez_BOM.pbit' % NAZIV, False, False),
             ('%s_v2.pbit' % NAZIV, False, True),
             ('%s_v3.pbit' % NAZIV, True, True)]

for ime, bom, pun in VARIJANTE:
    put = os.path.join(BASE, ime)
    delovi = PUN if pun else MIN
    print('== %s' % ime)
    ok(os.path.exists(put), 'fajl postoji')
    z = zipfile.ZipFile(put)
    ok(z.namelist() == delovi, 'delovi paketa: %s' % z.namelist())
    ok(z.testzip() is None, 'zip nije oštećen')

    ct = z.read('[Content_Types].xml').decode('utf-8')
    navedeni = re.findall(r'PartName="/([^"]+)"', ct)
    ocekivani = [x for x in delovi if x not in ('[Content_Types].xml', '_rels/.rels')]
    ok(sorted(navedeni) == sorted(ocekivani),
       'Content_Types navodi tačno delove bez ekstenzije: %s' % navedeni)
    if pun:
        ok('Extension="rels"' in ct, 'Content_Types ima tip za .rels')
        rels = z.read('_rels/.rels').decode('utf-8')
        ok('<Relationships' in rels and 'openxmlformats' in rels,
           '_rels/.rels je ispravan OPC dokument veza')

    for deo in delovi:
        if deo in ('[Content_Types].xml', '_rels/.rels'):
            continue
        sirovo = z.read(deo)
        ok(len(sirovo) % 2 == 0, '%s ima paran broj bajtova (UTF-16)' % deo)
        t = sirovo.decode('utf-16-le')
        ok(t.startswith('\ufeff') == bom,
           '%s %s BOM, kako je i traženo' % (deo, 'ima' if bom else 'nema'))
        t = t.lstrip('\ufeff')
        if deo == 'Version':
            ok(t == VERZIJA, 'Version = %s' % t)
            continue
        try:
            d = json.loads(t)
            ok(True, '%s je ispravan JSON' % deo)
        except Exception as e:
            ok(False, '%s nije ispravan JSON: %s' % (deo, e))
            continue
        sada = json.dumps(d, ensure_ascii=False, sort_keys=True)
        if deo == 'DataModelSchema':
            ok(sada == SEMA, 'DataModelSchema je isti model kao u .pbip projektu')
        elif deo == 'Report/Layout':
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
