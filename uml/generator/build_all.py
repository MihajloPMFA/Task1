# -*- coding: utf-8 -*-
import sys, os, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from act import to_drawio, to_png, _anchor
import d1_nabavka, d2_produkcija, d3_emitovanje

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mods = [('1_nabavka', d1_nabavka), ('2_produkcija', d2_produkcija),
        ('3_emitovanje', d3_emitovanje)]
dgs = []
for tag, m in mods:
    d = m.build()
    dgs.append(d)
    png = os.path.join(OUT, 'DA_%s.png' % tag)
    print(to_png(d, png), d.name)
    # provera: svaka veza je zakacena na cvorove sa oba kraja
    free = [i for i, ed in enumerate(d.edges)
            if not _anchor(d, ed['pts'][0]) or not _anchor(d, ed['pts'][-1])]
    print('   cvorova %d, prelaza %d, nezakacenih krajeva: %s'
          % (len(d.nodes), len(d.edges), free or 'nema'))
p = to_drawio(dgs, os.path.join(OUT, 'DA_TV_stanica.drawio'))
ET.parse(p)
print('->', p, '(XML validan, %d dijagrama)' % len(dgs))
