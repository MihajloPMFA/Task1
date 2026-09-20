# -*- coding: utf-8 -*-
"""Provera konzistentnosti seme + generisanje DDL skripta i dokumentacije."""
import sys, os, io, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import TABLES

BY = {t['name']: t for t in TABLES}
err = []

for t in TABLES:
    names = [c['n'] for c in t['cols']]
    if len(names) != len(set(names)):
        err.append('%s: duplirane kolone' % t['name'])
    if len(t['name']) > 30:
        err.append('%s: ime tabele > 30 znakova' % t['name'])
    for c in t['cols']:
        if len(c['n']) > 30:
            err.append('%s.%s: ime kolone > 30 znakova' % (t['name'], c['n']))
        if not re.match(r'^[A-Z][A-Z0-9_]*$', c['n']):
            err.append('%s.%s: nedozvoljeni znak u imenu' % (t['name'], c['n']))
    if not re.match(r'^[A-Z][A-Z0-9_]*$', t['name']):
        err.append('%s: nedozvoljeni znak u imenu tabele' % t['name'])
    for k in t['pk']:
        if k not in names:
            err.append('%s: PK kolona %s ne postoji' % (t['name'], k))
        else:
            col = [c for c in t['cols'] if c['n'] == k][0]
            if col['null']:
                err.append('%s.%s: PK kolona sme da bude NOT NULL' % (t['name'], k))
    for f in t['fks']:
        p = BY.get(f['parent'])
        if p is None:
            err.append('%s: FK %s -> nepoznata tabela %s' % (t['name'], f['name'], f['parent']))
            continue
        if len(f['child']) != len(f['pcols']):
            err.append('%s: FK %s -> broj kolona se ne poklapa' % (t['name'], f['name']))
        for cc in f['child']:
            if cc not in names:
                err.append('%s: FK %s -> kolona %s ne postoji' % (t['name'], f['name'], cc))
        for pc in f['pcols']:
            if pc not in [c['n'] for c in p['cols']]:
                err.append('%s: FK %s -> kolona %s ne postoji u %s' % (t['name'], f['name'], pc, p['name']))
        if sorted(f['pcols']) != sorted(p['pk']):
            err.append('%s: FK %s -> %s ne pokazuje na pun primarni kljuc %s' % (
                t['name'], f['name'], p['name'], p['pk']))
        # tipovi
        for cc, pc in zip(f['child'], f['pcols']):
            ct = [c['t'] for c in t['cols'] if c['n'] == cc]
            pt = [c['t'] for c in p['cols'] if c['n'] == pc]
            if ct and pt and ct[0] != pt[0]:
                err.append('%s.%s (%s) != %s.%s (%s)' % (t['name'], cc, ct[0], p['name'], pc, pt[0]))

fkn = [f['name'] for t in TABLES for f in t['fks']]
for n in set(fkn):
    if fkn.count(n) > 1:
        err.append('duplirano ime ogranicenja: %s' % n)
    if len(n) > 30:
        err.append('ime ogranicenja > 30 znakova: %s' % n)

if err:
    print('GRESKE (%d):' % len(err))
    for e in err:
        print('  -', e)
    sys.exit(1)
print('Provera seme: OK  (%d tabela, %d kolona, %d stranih kljuceva)'
      % (len(TABLES), sum(len(t['cols']) for t in TABLES), len(fkn)))

# ---------------------------------------------------------------- DDL
HDR = """-- =====================================================================
--  ER model informacionog sistema TV stanice
--  Relaciona sema izvedena iz PMOV dijagrama PMOV_TV_stanica_2_1_1.vsdx
--
--  Namena: reverzni inzenjering u CA ERwin Data Modeler r7.3
--          (File > New > Logical/Physical  ->  Tools > Reverse Engineer
--           -> Reverse Engineer From: Script File -> ovaj .sql fajl)
--
--  %d tabela, %d kolona, %d stranih kljuceva
-- =====================================================================

"""

def ddl():
    out = io.StringIO()
    out.write(HDR % (len(TABLES), sum(len(t['cols']) for t in TABLES), len(fkn)))
    for t in TABLES:
        out.write('-- %s\n' % ('-' * 69))
        out.write('-- %s\n' % t['name'])
        out.write('-- PMOV: %s\n' % t['src'])
        out.write('-- %s\n' % ('-' * 69))
        w = max(len(c['n']) for c in t['cols'])
        wt = max(len(c['t']) for c in t['cols'])
        rows = []
        for c in t['cols']:
            rows.append((('    %-*s  %-*s  %-8s' % (
                w, c['n'], wt, c['t'], '' if c['null'] else 'NOT NULL')).rstrip(), c['d']))
        rows.append(('    CONSTRAINT PK_%s PRIMARY KEY (%s)' % (t['name'][:27], ', '.join(t['pk'])), ''))
        wl = max(len(r[0]) for r in rows) + 1
        lines = []
        for i, (txt, note) in enumerate(rows):
            sep = ',' if i < len(rows) - 1 else ''
            com = ('  /* %s */' % note) if note else ''
            lines.append('%-*s%s' % (wl, txt + sep, com) if com else txt + sep)
        out.write('CREATE TABLE %s\n(\n%s\n);\n\n' % (t['name'], '\n'.join(lines)))
    out.write('\n-- %s\n-- STRANI KLJUCEVI (veze iz PMOV dijagrama)\n-- %s\n\n'
              % ('=' * 69, '=' * 69))
    for t in TABLES:
        for f in t['fks']:
            out.write('ALTER TABLE %s\n    ADD CONSTRAINT %s FOREIGN KEY (%s)\n'
                      '    REFERENCES %s (%s);\n\n'
                      % (t['name'], f['name'], ', '.join(f['child']),
                         f['parent'], ', '.join(f['pcols'])))
    return out.getvalue()

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
open(os.path.join(base, 'ER_TV_stanica.sql'), 'w', encoding='utf-8').write(ddl())
print('-> ER_TV_stanica.sql')

# varijanta bez ijednog komentara -- rezerva ako parser skripta zapne na /* */
plain = re.sub(r'\s*/\*.*?\*/', '', ddl())
plain = '\n'.join(l.rstrip() for l in plain.split('\n') if not l.startswith('--'))
plain = re.sub(r'\n{3,}', '\n\n', plain).lstrip('\n')
open(os.path.join(base, 'ER_TV_stanica_bez_komentara.sql'), 'w', encoding='utf-8').write(plain)
print('-> ER_TV_stanica_bez_komentara.sql')
