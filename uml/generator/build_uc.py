# -*- coding: utf-8 -*-
import sys, os, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uc import to_drawio, to_png, _anchor
import u1_nabavka, u2_produkcija, u3_emitovanje

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mods = [('1_nabavka', u1_nabavka), ('2_produkcija', u2_produkcija),
        ('3_emitovanje', u3_emitovanje)]
dgs = []
for tag, m in mods:
    d = m.build(); dgs.append(d)
    print(to_png(d, os.path.join(OUT, 'UC_%s.png' % tag)), d.name)
    free = [i for i, ed in enumerate(d.edges)
            if not _anchor(d, ed['pts'][0]) or not _anchor(d, ed['pts'][-1])]
    print('   aktera+slucajeva %d, prelaza %d | linija kroz oblik: %s | nezakacenih: %s'
          % (len(d.nodes), len(d.edges), d.collisions() or 'nema', free or 'nema'))
p = to_drawio(dgs, os.path.join(OUT, 'UC_TV_stanica.drawio'))
ET.parse(p)
print('->', p, '(XML validan, %d dijagrama)' % len(dgs))
