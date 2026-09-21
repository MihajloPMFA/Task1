# -*- coding: utf-8 -*-
"""Dijagram aktivnosti 2: PRODUKCIJA EMISIJE.
Izvor: PMOV/ER entiteti PROJEKAT PRODUKCIJE, AKTIVNOST PRODUKCIJE, TROSAK
PRODUKCIJE, SIROVI SNIMAK, MEDIJSKI SADRZAJ, GRAFICKI I MUZICKI ELEMENT,
OPREMA, ZAPOSLENI (veze UREDJUJE, ANGAZUJE, ZADUZUJE, SNIMLJEN NA,
MONTIRAN U, UGRADJEN U, IZAZIVA)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from act import Diagram

def build():
    d = Diagram('Produkcija emisije',
                ['Urednik', 'Produkcijska ekipa', 'Tehnička služba'], 1720)
    L0, L1, L2 = 0, 1, 2
    d.node('s',   'start',    L0, 64)
    d.node('a1',  'action',   L0, 140, 'Predlog projekta produkcije')
    d.node('d1',  'decision', L0, 240, 'Projekat je odobren?')
    d.node('a2',  'action',   L0, 380, 'Definisanje aktivnosti i budžeta')
    d.node('f1',  'bar',      L1, 490, x=d.lx(L1) + 20, w=d.lane_w * 2 - 40)
    d.node('a3',  'action',   L1, 550, 'Angažovanje članova ekipe')
    d.node('a4',  'action',   L2, 550, 'Zaduživanje i rezervacija opreme')
    d.node('f2',  'bar',      L1, 654, x=d.lx(L1) + 20, w=d.lane_w * 2 - 40)
    d.node('a5',  'action',   L1, 720, 'Snimanje po planu aktivnosti')
    d.node('a6',  'action',   L1, 810, 'Evidentiranje sirovih snimaka')
    d.node('d2',  'decision', L1, 900, 'Kvalitet snimka je prihvatljiv?')
    d.node('a7',  'action',   L1, 1026, 'Montaža medijskog sadržaja')
    d.node('a8',  'action',   L1, 1116, 'Ugradnja grafičkih i muzičkih elemenata')
    d.node('a9',  'action',   L0, 1220, 'Kontrola i prihvatanje sadržaja')
    d.node('d3',  'decision', L0, 1320, 'Sadržaj je prihvaćen?')
    d.node('a10', 'action',   L1, 1456, 'Evidentiranje troškova produkcije')
    d.node('a11', 'action',   L1, 1546, 'Arhiviranje medijskog sadržaja')
    d.node('e',   'end',      L1, 1640)

    c0, c1, c2 = d.cx(L0), d.cx(L1), d.cx(L2)
    LP0, LP1 = d.lx(L0) + 16, d.lx(L1) + 16

    d.edge([d.B('s'), d.T('a1')])
    d.edge([d.B('a1'), d.T('d1')])
    d.loop(d.L('d1'), LP0, d.L('a1'))
    d.edge([d.B('d1'), d.T('a2')], 'Da', (c0 + 16, d.B('d1')[1] + 20))
    d.jog(d.B('a2'), 458, (c1, 490))
    d.edge([(c1, 500), d.T('a3')])
    d.edge([(c2, 500), d.T('a4')])
    d.edge([d.B('a3'), (c1, 654)])
    d.edge([d.B('a4'), (c2, 654)])
    d.edge([(c1, 664), d.T('a5')])
    d.edge([d.B('a5'), d.T('a6')])
    d.edge([d.B('a6'), d.T('d2')])
    d.loop(d.L('d2'), LP1, d.L('a5'))
    d.edge([d.B('d2'), d.T('a7')], 'Da', (c1 + 16, d.B('d2')[1] + 20))
    d.edge([d.B('a7'), d.T('a8')])
    d.jog(d.B('a8'), 1190, d.T('a9'))
    d.edge([d.B('a9'), d.T('d3')])
    d.loop(d.L('d3'), LP0, d.L('a7'))
    d.jog(d.B('d3'), 1420, d.T('a10'), 'Da', (c0 + 16, d.B('d3')[1] + 20))
    d.edge([d.B('a10'), d.T('a11')])
    d.edge([d.B('a11'), d.T('e')])
    return d

if __name__ == '__main__':
    from act import to_png
    print(to_png(build(), '/tmp/d2.png'))
