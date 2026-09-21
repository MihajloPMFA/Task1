# -*- coding: utf-8 -*-
"""Use case 3: EMITOVANJE PROGRAMA I PRODAJA REKLAMNOG PROSTORA.
Akteri i slucajevi izvedeni iz PMOV/ER: PROGRAMSKA SEMA, PROGRAMSKA CELINA,
TERMIN EMITOVANJA, PRAVO KORISCENJA, REKLAMNI BLOK, REKLAMNI SADRZAJ,
EMITOVANJE REKLAME, ZAPIS O EMITOVANJU, FAKTURA, MERENJE GLEDANOSTI,
POVRATNA INFO. GLEDALACA, OGLASIVAC, UREDNIK, TEHNICKO OSOBLJE, REFERENT."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uc import UseCase

def build():
    d = UseCase('Emitovanje programa i prodaja reklamnog prostora', 1420, 1180)
    d.actor('a1', 70, 250,  'Urednik programa')
    d.actor('a2', 70, 770,  'Tehničko osoblje')
    d.actor('a3', 70, 960,  'Referent marketinga')
    d.actor('a4', 1320, 430, 'Oglašivač')
    d.actor('a5', 1320, 1110, 'Gledalac')

    d.uc('u1', 340, 120,  'Izrada programske šeme')
    d.uc('u2', 340, 250,  'Odobravanje programske šeme')
    d.uc('u3', 340, 380,  'Planiranje termina emitovanja')
    d.uc('u4', 340, 510,  'Zakup reklamnog bloka')
    d.uc('u5', 340, 640,  'Provera reklamnog sadržaja')
    d.uc('u6', 340, 770,  'Emitovanje programa')
    d.uc('u7', 340, 900,  'Naplata emitovanih spotova')
    d.uc('u8', 340, 1030, 'Obrada povratnih informacija gledalaca')

    d.uc('i1', 700, 120,  'Provera prava korišćenja')
    d.uc('i2', 700, 380,  'Raspoređivanje programskih celina')
    d.uc('i3', 700, 510,  'Provera dostupnosti termina')
    d.uc('i4', 700, 770,  'Kreiranje zapisa o emitovanju')
    d.uc('i5', 700, 900,  'Izdavanje fakture oglašivaču')
    d.uc('i6', 700, 1030, 'Preuzimanje rezultata merenja gledanosti')

    d.uc('e1', 1030, 660, 'Upis napomene o smetnjama')

    d.assoc([d.R('a1'), (140, 250), (140, 120), d.L('u1')])
    d.assoc([d.R('a1'), d.L('u2')])
    d.assoc([d.R('a1'), (170, 250), (170, 380), d.L('u3')])
    d.assoc([d.R('a2'), d.L('u6')])
    d.assoc([d.R('a3'), (150, 960), (150, 510), d.L('u4')])
    d.assoc([d.R('a3'), (185, 960), (185, 640), d.L('u5')])
    d.assoc([d.R('a3'), (210, 960), (210, 900), d.L('u7')])
    d.assoc([d.R('a3'), (235, 960), (235, 1030), d.L('u8')])
    d.assoc([d.L('a4'), (1230, 430), (1230, 450), (340, 450), d.T('u4')])
    d.assoc([d.L('a4'), (1270, 430), (1270, 600), (480, 600), (480, 640), d.R('u5')])
    d.assoc([d.L('a5'), (340, 1110), d.B('u8')])

    for b, i in (('u1', 'i1'), ('u3', 'i2'), ('u4', 'i3'), ('u6', 'i4'),
                 ('u7', 'i5'), ('u8', 'i6')):
        p1, p2 = d.R(b), d.L(i)
        d.rel([p1, p2], 'include', ((p1[0] + p2[0]) / 2, p1[1] - 18))
    d.rel([d.B('e1'), (1030, 845), (340, 845), d.B('u6')], 'extend', (690, 827))
    return d

if __name__ == '__main__':
    from uc import to_png
    d = build()
    print(to_png(d, '/tmp/u3.png'), 'kolizije:', d.collisions() or 'nema')
