# -*- coding: utf-8 -*-
"""Dijagram aktivnosti 1: NABAVKA OPREME I MATERIJALA.
Izvor: PMOV/ER entiteti ZAHTEV ZA NABAVKU, PLAN NABAVKE, STAVKA PLANA NABAVKE,
PONUDA DOBAVLJACA, KRITERIJUM VREDNOVANJA, NARUDZBENICA, STAVKA NARUDZBENICE,
PRIJEMNICA, REKLAMACIJA, FAKTURA, NALOG ZA PLACANJE."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from act import Diagram

def build():
    d = Diagram('Nabavka opreme i materijala',
                ['Organizaciona jedinica', 'Referent nabavke', 'Dobavljač',
                 'Finansijska služba'], 1710)
    L0, L1, L2, L3 = 0, 1, 2, 3
    d.node('s',    'start',    L0, 64)
    d.node('a1',   'action',   L0, 140, 'Podnošenje zahteva za nabavku')
    d.node('a2',   'action',   L1, 240, 'Provera zahteva i procenjene vrednosti')
    d.node('d1',   'decision', L1, 330, 'Zahtev je odobren?')
    d.node('arej', 'action',   L0, 343, 'Prijem obaveštenja o odbijanju zahteva')
    d.node('e1',   'end',      L0, 450)
    d.node('a3',   'action',   L1, 446, 'Uvrštavanje stavke u plan nabavke')
    d.node('a4',   'action',   L1, 536, 'Slanje poziva dobavljačima')
    d.node('a5',   'action',   L2, 636, 'Dostavljanje ponude')
    d.node('a6',   'action',   L1, 736, 'Vrednovanje ponuda po kriterijumima')
    d.node('d2',   'decision', L1, 826, 'Ponuda je prihvatljiva?')
    d.node('a7',   'action',   L1, 946, 'Izdavanje narudžbenice')
    d.node('a8',   'action',   L2, 1046, 'Isporuka artikala po narudžbenici')
    d.node('a9',   'action',   L1, 1146, 'Prijem robe i izrada prijemnice')
    d.node('d3',   'decision', L1, 1236, 'Isporuka je ispravna?')
    d.node('arek', 'action',   L1, 1386, 'Podnošenje reklamacije dobavljaču')
    d.node('a12',  'action',   L3, 1366, 'Knjiženje ulazne fakture')
    d.node('a13',  'action',   L3, 1456, 'Izdavanje naloga za plaćanje')
    d.node('a14',  'action',   L3, 1546, 'Evidentiranje realizacije plaćanja')
    d.node('e2',   'end',      L3, 1636)

    c0, c1, c3 = d.cx(L0), d.cx(L1), d.cx(L3)
    LOOP, LOOP2 = d.lx(L1) + 14, d.lx(L2) + 16

    d.edge([d.B('s'), d.T('a1')])
    d.jog(d.B('a1'), 212, d.T('a2'))
    d.edge([d.B('a2'), d.T('d1')])
    d.edge([d.L('d1'), d.R('arej')], 'Ne', (d.L('d1')[0] - 34, d.L('d1')[1] - 14))
    d.edge([d.B('arej'), d.T('e1')])
    d.edge([d.B('d1'), d.T('a3')], 'Da', (c1 + 16, d.B('d1')[1] + 20))
    d.edge([d.B('a3'), d.T('a4')])
    d.jog(d.B('a4'), 608, d.T('a5'))
    d.jog(d.B('a5'), 708, d.T('a6'))
    d.edge([d.B('a6'), d.T('d2')])
    d.loop(d.L('d2'), LOOP, d.L('a4'))
    d.edge([d.B('d2'), d.T('a7')], 'Da', (c1 + 16, d.B('d2')[1] + 20))
    d.jog(d.B('a7'), 1018, d.T('a8'))
    d.jog(d.B('a8'), 1118, d.T('a9'))
    d.edge([d.B('a9'), d.T('d3')])
    d.loop(d.L('d3'), LOOP, d.L('arek'))
    d.edge([d.R('arek'), (LOOP2, d.R('arek')[1]), (LOOP2, d.L('a8')[1]), d.L('a8')])
    d.jog(d.B('d3'), 1336, d.T('a12'), 'Da', (c1 + 16, d.B('d3')[1] + 20))
    d.edge([d.B('a12'), d.T('a13')])
    d.edge([d.B('a13'), d.T('a14')])
    d.edge([d.B('a14'), d.T('e2')])
    return d

if __name__ == '__main__':
    from act import to_png
    print(to_png(build(), '/tmp/d1.png'))
