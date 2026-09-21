# -*- coding: utf-8 -*-
"""Use case 2: PRODUKCIJA I ARHIVIRANJE SADRZAJA.
Akteri i slucajevi izvedeni iz PMOV/ER: PROJEKAT PRODUKCIJE, AKTIVNOST
PRODUKCIJE, TROSAK PRODUKCIJE, SIROVI SNIMAK, MEDIJSKI SADRZAJ, GRAFICKI I
MUZICKI ELEMENT, OPREMA, UREDNIK, NOVINAR / REPORTER, TEHNICKO OSOBLJE,
SERVISERI."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uc import UseCase

def build():
    d = UseCase('Produkcija i arhiviranje sadržaja', 1420, 1140)
    d.actor('a1', 70, 180,  'Urednik')
    d.actor('a2', 70, 640,  'Novinar / reporter')
    d.actor('a3', 70, 950,  'Tehničko osoblje')
    d.actor('a4', 1320, 1030, 'Serviser')

    d.uc('u1', 340, 120,  'Predlaganje projekta produkcije')
    d.uc('u2', 340, 250,  'Odobravanje projekta produkcije')
    d.uc('u3', 340, 380,  'Planiranje aktivnosti produkcije')
    d.uc('u4', 340, 510,  'Zaduživanje opreme za snimanje')
    d.uc('u5', 340, 640,  'Snimanje materijala')
    d.uc('u6', 340, 770,  'Montaža medijskog sadržaja')
    d.uc('u7', 340, 900,  'Evidentiranje troškova produkcije')
    d.uc('u8', 340, 1030, 'Arhiviranje medijskog sadržaja')

    d.uc('i1', 700, 250,  'Provera odobrenog budžeta')
    d.uc('i2', 700, 380,  'Angažovanje članova ekipe')
    d.uc('i3', 700, 510,  'Provera raspoloživosti opreme')
    d.uc('i4', 700, 640,  'Evidentiranje sirovog snimka')
    d.uc('i5', 700, 770,  'Ugradnja grafičkih i muzičkih elemenata')

    d.uc('e1', 1030, 900,  'Ponovno snimanje')
    d.uc('u9', 1030, 1030, 'Servisiranje opreme')

    d.assoc([d.R('a1'), (140, 180), (140, 120), d.L('u1')])
    d.assoc([d.R('a1'), (170, 180), (170, 250), d.L('u2')])
    d.assoc([d.R('a1'), (190, 180), (190, 380), d.L('u3')])
    d.assoc([d.R('a2'), d.L('u5')])
    d.assoc([d.R('a3'), (150, 950), (150, 510), d.L('u4')])
    d.assoc([d.R('a3'), (175, 950), (175, 770), d.L('u6')])
    d.assoc([d.R('a3'), (200, 950), (200, 900), d.L('u7')])
    d.assoc([d.R('a3'), (225, 950), (225, 1030), d.L('u8')])
    d.assoc([d.L('a4'), d.R('u9')])

    for b, i in (('u2', 'i1'), ('u3', 'i2'), ('u4', 'i3'), ('u5', 'i4'), ('u6', 'i5')):
        p1, p2 = d.R(b), d.L(i)
        d.rel([p1, p2], 'include', ((p1[0] + p2[0]) / 2, p1[1] - 18))
    d.rel([d.T('e1'), (1030, 700), (340, 700), d.B('u5')], 'extend', (700, 682))
    return d

if __name__ == '__main__':
    from uc import to_png
    d = build()
    print(to_png(d, '/tmp/u2.png'), 'kolizije:', d.collisions() or 'nema')
