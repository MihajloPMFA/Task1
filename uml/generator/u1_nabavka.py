# -*- coding: utf-8 -*-
"""Use case 1: NABAVKA I SNABDEVANJE.
Akteri i slucajevi izvedeni iz PMOV/ER: ZAHTEV ZA NABAVKU, PLAN NABAVKE,
PONUDA DOBAVLJACA, KRITERIJUM VREDNOVANJA, NARUDZBENICA, PRIJEMNICA,
REKLAMACIJA, FAKTURA, NALOG ZA PLACANJE, DOBAVLJAC, REFERENT."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uc import UseCase

def build():
    d = UseCase('Nabavka i snabdevanje', 1420, 1100)
    d.actor('a1', 70, 120, 'Organizaciona jedinica')
    d.actor('a2', 70, 560, 'Referent nabavke')
    d.actor('a3', 70, 980, 'Finansijska služba')
    d.actor('a4', 1320, 620, 'Dobavljač')

    d.uc('u1', 340, 120,  'Podnošenje zahteva za nabavku')
    d.uc('u2', 340, 250,  'Izrada plana nabavke')
    d.uc('u3', 340, 380,  'Prikupljanje ponuda dobavljača')
    d.uc('u4', 340, 510,  'Vrednovanje ponuda')
    d.uc('u5', 340, 640,  'Izdavanje narudžbenice')
    d.uc('u6', 340, 770,  'Prijem isporuke')
    d.uc('u7', 340, 900,  'Knjiženje ulazne fakture')
    d.uc('u8', 340, 1030, 'Izdavanje naloga za plaćanje')

    d.uc('i1', 700, 120,  'Provera procenjene vrednosti')
    d.uc('i3', 700, 510,  'Bodovanje po kriterijumima')
    d.uc('i4', 700, 770,  'Izrada prijemnice')
    d.uc('i5', 700, 1030, 'Evidentiranje plaćanja')
    d.uc('e1', 1030, 650, 'Podnošenje reklamacije')

    AR = d.R('a1')[0]                      # desna ivica aktera
    d.assoc([d.R('a1'), d.L('u1')])
    for uid, x in (('u2', 150), ('u3', 170), ('u4', 190), ('u5', 210), ('u6', 230)):
        d.assoc([d.R('a2'), (x, 560), (x, d.L(uid)[1]), d.L(uid)])
    d.assoc([d.R('a3'), (170, 980), (170, 900), d.L('u7')])
    d.assoc([d.R('a3'), (190, 980), (190, 1030), d.L('u8')])

    d.assoc([d.L('a4'), (1230, 620), (1230, 380), d.R('u3')])
    d.assoc([d.L('a4'), (1290, 620), (1290, 830), (340, 830), d.B('u6')])

    for b, i in (('u1', 'i1'), ('u4', 'i3'), ('u6', 'i4'), ('u8', 'i5')):
        p1, p2 = d.R(b), d.L(i)
        d.rel([p1, p2], 'include', ((p1[0] + p2[0]) / 2, p1[1] - 18))
    d.rel([d.L('e1'), (520, 650), (520, 700), (340, 700), d.T('u6')], 'extend', (730, 632))
    return d

if __name__ == '__main__':
    from uc import to_png
    d = build()
    print(to_png(d, '/tmp/u1.png'), 'kolizije:', d.collisions() or 'nema')
