# -*- coding: utf-8 -*-
"""Dijagram aktivnosti 3: PLANIRANJE SEME I EMITOVANJE PROGRAMA.
Izvor: PMOV/ER entiteti PROGRAMSKA SEMA, PROGRAMSKA CELINA, TERMIN EMITOVANJA,
MEDIJSKI SADRZAJ, PRAVO KORISCENJA, REKLAMNI BLOK, EMITOVANJE REKLAME,
ZAPIS O EMITOVANJU, MERENJE GLEDANOSTI (veze SADRZI CELINE, OBUHVATA,
PLANIRANA, POKRIVA, ODOBRAVA, ZAKUPLJEN U, REALIZOVAN, EVIDENTIRA, MERENA)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from act import Diagram

def build():
    d = Diagram('Planiranje šeme i emitovanje programa',
                ['Urednik programa', 'Marketing i prodaja', 'Tehnička služba'], 1600)
    L0, L1, L2 = 0, 1, 2
    d.node('s',   'start',    L0, 64)
    d.node('a1',  'action',   L0, 140, 'Izrada programske šeme')
    d.node('a2',  'action',   L0, 230, 'Raspoređivanje celina i termina emitovanja')
    d.node('d1',  'decision', L0, 340, 'Postoji važeće pravo korišćenja?')
    d.node('a3',  'action',   L0, 470, 'Odobravanje programske šeme')
    d.node('f1',  'bar',      L1, 570, x=d.lx(L1) + 20, w=d.lane_w * 2 - 40)
    d.node('a4',  'action',   L1, 630, 'Zakup reklamnog bloka u terminu')
    d.node('a5',  'action',   L2, 630, 'Priprema tehničkih resursa za emitovanje')
    d.node('f2',  'bar',      L1, 734, x=d.lx(L1) + 20, w=d.lane_w * 2 - 40)
    d.node('a6',  'action',   L2, 800, 'Emitovanje po programskoj šemi')
    d.node('d2',  'decision', L2, 890, 'Emitovanje bez smetnji?')
    d.node('a7',  'action',   L2, 1016, 'Upis napomene o smetnjama')
    d.node('a8',  'action',   L2, 1116, 'Kreiranje zapisa o emitovanju')
    d.node('a9',  'action',   L1, 1220, 'Naplata emitovanih reklamnih spotova')
    d.node('a10', 'action',   L0, 1320, 'Preuzimanje rezultata merenja gledanosti')
    d.node('a11', 'action',   L0, 1420, 'Izrada izveštaja o realizaciji šeme')
    d.node('e',   'end',      L0, 1520)

    c0, c1, c2 = d.cx(L0), d.cx(L1), d.cx(L2)
    LP0, LP2 = d.lx(L0) + 16, d.lx(L2) + 16

    d.edge([d.B('s'), d.T('a1')])
    d.edge([d.B('a1'), d.T('a2')])
    d.edge([d.B('a2'), d.T('d1')])
    d.loop(d.L('d1'), LP0, d.L('a2'))
    d.edge([d.B('d1'), d.T('a3')], 'Da', (c0 + 16, d.B('d1')[1] + 20))
    d.jog(d.B('a3'), 542, (c1, 570))
    d.edge([(c1, 580), d.T('a4')])
    d.edge([(c2, 580), d.T('a5')])
    d.edge([d.B('a4'), (c1, 734)])
    d.edge([d.B('a5'), (c2, 734)])
    d.edge([(c2, 744), d.T('a6')])
    d.edge([d.B('a6'), d.T('d2')])
    d.edge([d.B('d2'), d.T('a7')], 'Ne', (c2 + 16, d.B('d2')[1] + 20))
    d.edge([d.L('d2'), (LP2, d.L('d2')[1]), (LP2, d.L('a8')[1]), d.L('a8')],
           'Da', (LP2 + 26, d.L('d2')[1] - 16))
    d.edge([d.B('a7'), d.T('a8')])
    d.jog(d.B('a8'), 1190, d.T('a9'))
    d.jog(d.B('a9'), 1292, d.T('a10'))
    d.edge([d.B('a10'), d.T('a11')])
    d.edge([d.B('a11'), d.T('e')])
    return d

if __name__ == '__main__':
    from act import to_png
    print(to_png(build(), '/tmp/d3.png'))
