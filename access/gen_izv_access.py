# -*- coding: utf-8 -*-
"""Generise VBA modul modIzvestaji (.bas) koji se uvozi u POSTOJECU Access bazu
(Access_v1.accdb) i dodaje osam izvestaja iz Specifikacije izvestaja.

Dodaje samo nove objekte: upite qIzv..., izvestaje rptIzv... i formu
frmIzvestaji.  Postojece tabele, forme i upiti se ne diraju.
"""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
from izv_lib import ZAGLAVLJE
from izv_upiti import U as UPITI

# ---------------------------------------------------------------- srpska slova
MARK = {'Č': '~C', 'č': '~c', 'Ć': '~K', 'ć': '~k',
        'Š': '~S', 'š': '~s', 'Ž': '~Z', 'ž': '~z',
        'Đ': '~D', 'đ': '~d'}

def enc(s):
    s = s.replace('—', '-').replace('–', '-')
    if all(ord(c) <= 126 for c in s):
        return s
    if '~' in s:
        raise ValueError('tekst mesa prava slova i markere: %r' % s)
    for k, v in MARK.items():
        s = s.replace(k, v)
    bad = [c for c in s if ord(c) > 126]
    if bad:
        raise ValueError('neprevedeni znakovi %r u %r' % (bad, s))
    return s

def q(s):
    e = enc(s)
    return '"%s"' % e.replace('"', '""')

# ---------------------------------------------------------------- sekcije
DET, ZAG, POD, PZAG, PPOD = 'acDetail', 'acHeader', 'acFooter', 'acPageHeader', 'acPageFooter'
G1Z, G1P = 'acGroupLevel1Header', 'acGroupLevel1Footer'
G2Z, G2P = 'acGroupLevel2Header', 'acGroupLevel2Footer'

SIVO, CRNO = 9, 9

def _lit(v):
    if isinstance(v, bool):
        return 'True' if v else 'False'
    if isinstance(v, str):
        return q(v)
    return str(v)

def _rep(vals, defs):
    out = list(vals)
    while out and out[-1] == defs[len(out) - 1]:
        out.pop()
    return ''.join(', ' + _lit(v) for v in out)

def lab(sek, x, y, w, h, tekst, vel=9, bold=False, por=1):
    return '    Lab r, %s, %d, %d, %d, %d, %s%s' % (
        sek, x, y, w, h, q(tekst), _rep([vel, bold, por], [9, False, 1]))

def txtf(sek, x, y, w, h, izvor, vel=9, bold=False, por=1, fmt=''):
    """Txt poziv; prati se koji se opcioni argumenti moraju navesti."""
    if fmt:
        return '    Txt r, %s, %d, %d, %d, %d, %s, %s, %s, %s, %s' % (
            sek, x, y, w, h, q(izvor), vel, _lit(bold), por, q(fmt))
    return '    Txt r, %s, %d, %d, %d, %d, %s%s' % (
        sek, x, y, w, h, q(izvor), _rep([vel, bold, por], [9, False, 1]))

def lin(sek, x, y, w):
    return '    Lin r, %s, %d, %d, %d' % (sek, x, y, w)

def sek(s, h, rast=False):
    return '    Sek r, %s, %d%s' % (s, h, ', True' if rast else '')

# ---------------------------------------------------------------- kolone
class Kolone(object):
    def __init__(self, pocetak=0):
        self.poc = pocetak
        self.x = pocetak
        self.k = []

    def add(self, polje, w, natpis, por=1, fmt=''):
        self.k.append(dict(polje=polje, x=self.x, w=w, natpis=natpis, por=por, fmt=fmt))
        self.x += w
        return self

    @property
    def sirina(self):
        return self.x

    def nadji(self, polje):
        for c in self.k:
            if c['polje'] == polje:
                return c
        raise KeyError(polje)

    def zaglavlje(self, y=90, h=250, sekcija=None):
        """Natpisi kolona u zaglavlju strane (ili izvestaja, za podizvestaje)."""
        s = sekcija or PZAG
        out = []
        for c in self.k:
            out.append(lab(s, c['x'], y, c['w'] - 80, h, c['natpis'], 9, True, c['por']))
        return out

    def red(self, y=30, h=240, sekcija=None):
        """Jedan red tela izvestaja."""
        s = sekcija or DET
        out = []
        for c in self.k:
            out.append(txtf(s, c['x'], y, c['w'] - 80, h, c['polje'], 9, False,
                            c['por'], c['fmt']))
        return out

    def suma(self, polje, sekcija, y, agr='Sum', bold=True, fmt=None):
        c = self.nadji(polje)
        return txtf(sekcija, c['x'], y, c['w'] - 80, 260,
                    '=%s([%s])' % (agr, polje), 9, bold, c['por'],
                    fmt if fmt is not None else (c['fmt'] or '#,##0'))

# ---------------------------------------------------------------- parovi natpis+vrednost
def par(x, y, natpis, izvor, lw, vw, sekcija, fmt='', vel=9):
    out = [lab(sekcija, x, y + 30, lw, 220, natpis, vel, False, 1),
           txtf(sekcija, x + lw, y, vw, 260, izvor, vel, True, 1, fmt)]
    return out, x + lw + vw + 160

def parovi(sekcija, y, stavke, x0=0):
    """stavke: lista (natpis, izvor, lw, vw, fmt)"""
    out, x = [], x0
    for st in stavke:
        natpis, izvor, lw, vw = st[0], st[1], st[2], st[3]
        fmt = st[4] if len(st) > 4 else ''
        d, x = par(x, y, natpis, izvor, lw, vw, sekcija, fmt)
        out += d
    return out

# ---------------------------------------------------------------- naslovni blok
def naslov_blok(sirina, naslov, podnaslov, visina, dodatno=None):
    out = [sek(ZAG, visina),
           lab(ZAG, 0, 60, sirina, 400, naslov, 15, True),
           lab(ZAG, 0, 480, sirina, 240, podnaslov, 9, False)]
    y = 760
    for d in (dodatno or []):
        if isinstance(d, tuple):
            out.append(txtf(ZAG, 0, y, sirina, 260, d[0], 9, True, 1, d[1] if len(d) > 1 else ''))
        else:
            out.append(lab(ZAG, 0, y, sirina, 260, d, 9, False))
        y += 280
    out.append(lin(ZAG, 0, visina - 40, sirina))
    return out, y

PODNASLOV = 'Informacioni sistem TV stanice - TV Panorama'

# ================================================================ izvestaj 1
def izv1():
    K = Kolone()
    K.add('VREME_POCETKA', 1100, 'Vreme', 2, 'hh:nn')
    K.add('DATUM_TERMINA', 1400, 'Datum', 2, 'dd.mm.yyyy')
    K.add('SIFRA_TERMINA', 1200, 'Šifra termina')
    K.add('NAZIV_EMISIJE', 3300, 'Emisija')
    K.add('ZANR', 1700, 'Žanr')
    K.add('TRAJANJE_TERMINA', 1100, 'Trajanje (min)', 3, '0')
    K.add('TIP_TERMINA', 1400, 'Tip termina')
    K.add('ZONA_GLEDANOSTI', 900, 'Zona', 2)
    K.add('REDNI_BROJ_REPRIZE', 1000, 'Repriza', 3, '0')
    K.add('STATUS_TERMINA', 1500, 'Status')
    W = K.sirina
    L = ['', "' ---------------------------------------------- izvestaj 1",
         'Private Sub Izvestaj1()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv1"', '    r = Poc("qIzv1_Sema")',
         '    Gr r, "SIFRA_SEME", True, True',
         '    Gr r, "CELINA_KLJUC", True, True',
         '    Gr r, "VREME_POCETKA", False, False']
    blok, _ = naslov_blok(W, 'Izveštaj 1 - Programska šema sa terminima emitovanja',
                          PODNASLOV, 820)
    L += blok
    L += [sek(PZAG, 420)] + K.zaglavlje() + [lin(PZAG, 0, 380, W)]
    L += [sek(G1Z, 780)]
    L += parovi(G1Z, 60, [('Programska šema:', 'NAZIV_SEME', 1500, 3000),
                          ('Sezona:', 'SEZONA', 900, 1500),
                          ('Verzija:', 'VERZIJA_SEME', 900, 1100),
                          ('Status:', 'STATUS_SEME', 800, 1600)])
    L += parovi(G1Z, 380, [('Važi od:', 'SEMA_OD', 1000, 1300, 'dd.mm.yyyy'),
                           ('do:', 'SEMA_DO', 500, 1300, 'dd.mm.yyyy'),
                           ('Usvojena:', 'DATUM_USVAJANJA', 1100, 1300, 'dd.mm.yyyy'),
                           ('Urednik:', 'UREDNIK_NAZIV', 900, 2400),
                           ('Redakcija:', 'REDAKCIJA', 1100, 2600)])
    L += [lin(G1Z, 0, 720, W)]
    L += [sek(G2Z, 500)]
    L += parovi(G2Z, 80, [('Programska celina:', 'NAZIV_CELINE', 1700, 3000),
                          ('Tip:', 'TIP_CELINE', 600, 1500),
                          ('Datum:', 'DATUM_CELINE', 800, 1300, 'dd.mm.yyyy'),
                          ('Vreme od:', 'VREME_OD', 1000, 900, 'hh:nn'),
                          ('do:', 'VREME_DO', 500, 900, 'hh:nn')])
    L += [lin(G2Z, 0, 420, W), sek(DET, 300)] + K.red()
    L += [sek(G2P, 400), lin(G2P, 0, 20, W),
          lab(G2P, 0, 80, 2800, 250, 'Ukupno u celini:', 9, True),
          txtf(G2P, 2850, 80, 2200, 250, '=Count([SIFRA_TERMINA]) & " termina"', 9, True),
          K.suma('TRAJANJE_TERMINA', G2P, 80, fmt='0')]
    L += [sek(G1P, 480), lin(G1P, 0, 20, W),
          lab(G1P, 0, 90, 2800, 260, 'UKUPNO PO ŠEMI:', 10, True),
          txtf(G1P, 2850, 90, 2200, 260, '=Count([SIFRA_TERMINA]) & " termina"', 10, True),
          K.suma('TRAJANJE_TERMINA', G1P, 90, fmt='0')]
    L += [sek(POD, 500), lin(POD, 0, 40, W),
          lab(POD, 0, 120, 2800, 280, 'UKUPNO (sve šeme):', 11, True),
          txtf(POD, 2850, 120, 2200, 280, '=Count([SIFRA_TERMINA]) & " termina"', 11, True),
          K.suma('TRAJANJE_TERMINA', POD, 120, fmt='0')]
    L += ['    Podnozje r, %d' % W,
          '    Kraj r, "rptIzv1", %s, %d, True' % (
              q('Izveštaj 1 - Programska šema sa terminima emitovanja'), W),
          'End Sub']
    return L

# ================================================================ izvestaj 2
def izv2():
    K = Kolone()
    K.add('STVARNO_VREME_POCETKA', 1100, 'Stvarno vreme', 2, 'hh:nn')
    K.add('NAZIV_EMISIJE', 2300, 'Emisija')
    K.add('NAZIV_SADRZAJA', 2300, 'Medijski sadržaj')
    K.add('TRAJANJE_TERMINA', 1000, 'Plan (min)', 3, '0')
    K.add('STVARNO_TRAJANJE', 1000, 'Stvarno (min)', 3, '0')
    K.add('ODSTUPANJE', 1000, 'Odstupanje', 3, '0')
    K.add('STATUS_REALIZACIJE', 1300, 'Status realizacije')
    K.add('BROJ_LICENCE', 1200, 'Broj licence')
    K.add('VRSTA_PRAVA', 1500, 'Vrsta prava')
    K.add('OPERATER_EMITOVANJA', 1200, 'Operater')
    K.add('NAPOMENA_O_SMETNJAMA', 1500, 'Napomena o smetnjama')
    W = K.sirina
    L = ['', "' ---------------------------------------------- izvestaj 2",
         'Private Sub Izvestaj2()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv2"', '    r = Poc("qIzv2_Playout")',
         '    Gr r, "DATUM", True, True',
         '    Gr r, "STVARNO_VREME_POCETKA", False, False']
    blok, _ = naslov_blok(W, 'Izveštaj 2 - Evidencija emitovanog sadržaja (playout log)',
                          PODNASLOV, 1120)
    L += blok
    L += parovi(ZAG, 760, [('Period od:', 'PAR_OD', 1000, 1400, 'dd.mm.yyyy'),
                           ('do:', 'PAR_DO', 500, 1400, 'dd.mm.yyyy'),
                           ('Stanje na dan:', '=Date()', 1300, 1400, 'dd.mm.yyyy')])
    L += [sek(PZAG, 420)] + K.zaglavlje() + [lin(PZAG, 0, 380, W)]
    L += [sek(G1Z, 460)]
    L += parovi(G1Z, 60, [('Datum emitovanja:', 'DATUM', 1600, 1600, 'dd.mm.yyyy'),
                          ('dan:', 'DATUM', 500, 1800, 'dddd')])
    L += [lin(G1Z, 0, 390, W), sek(DET, 290)] + K.red()
    L += [sek(G1P, 420), lin(G1P, 0, 20, W),
          lab(G1P, 0, 80, 2200, 250, 'Ukupno za dan:', 9, True),
          txtf(G1P, 2250, 80, 2000, 250, '=Count([NAZIV_EMISIJE]) & " emitovanja"', 9, True),
          K.suma('STVARNO_TRAJANJE', G1P, 80, fmt='0'),
          txtf(G1P, K.nadji('STATUS_REALIZACIJE')['x'], 80, 3400, 250,
               '=Sum([IMA_SMETNJU]) & " sa zabeleženim smetnjama"', 9, True)]
    L += [sek(POD, 500), lin(POD, 0, 40, W),
          lab(POD, 0, 120, 2200, 280, 'UKUPNO ZA PERIOD:', 11, True),
          txtf(POD, 2250, 120, 2000, 280, '=Count([NAZIV_EMISIJE]) & " emitovanja"', 11, True),
          K.suma('STVARNO_TRAJANJE', POD, 120, fmt='0'),
          txtf(POD, K.nadji('STATUS_REALIZACIJE')['x'], 120, 3400, 280,
               '=Sum([IMA_SMETNJU]) & " sa zabeleženim smetnjama"', 10, True)]
    L += ['    Podnozje r, %d' % W,
          '    Kraj r, "rptIzv2", %s, %d, True' % (
              q('Izveštaj 2 - Evidencija emitovanog sadržaja (playout log)'), W),
          'End Sub']
    return L

# ================================================================ izvestaj 3
def izv3():
    K = Kolone()
    K.add('NAZIV_EMISIJE', 2600, 'Emisija')
    K.add('ZANR', 1600, 'Žanr')
    K.add('BROJ_MERENJA', 900, 'Merenja', 3, '0')
    K.add('PROSECAN_REJTING', 1200, 'Prosečan rejting', 3, '0.00')
    K.add('PROSECAN_UDEO', 1200, 'Prosečan udeo (%)', 3, '0.00')
    K.add('PROSECAN_BROJ_GLEDALACA', 1700, 'Prosečno gledalaca', 3, '#,##0')
    K.add('PROSECNO_GLEDANJE', 1500, 'Prosečno gledanje (min)', 3, '0.0')
    W = K.sirina
    L = ['', "' ---------------------------------------------- izvestaj 3",
         'Private Sub Izvestaj3()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv3"', '    r = Poc("qIzv3_Emisije")']
    blok, _ = naslov_blok(W, 'Izveštaj 3 - Gledanost emisija po žanru', PODNASLOV, 8000,
                          dodatno=[('=Zaglavlje3()',)])
    L += blok
    L += [lab(ZAG, 0, 1120, W, 280, 'Prosečan ostvareni rejting po žanru emisije', 10, True),
          '    Grafikon r, %s, 0, 1420, %d, 2900, "qIzv3_RejtingPoZanru"' % (ZAG, W),
          lab(ZAG, 0, 4420, W, 280, 'Kretanje prosečnog rejtinga po datumu merenja', 10, True),
          '    Grafikon r, %s, 0, 4720, %d, 2900, "qIzv3_RejtingPoDatumu"' % (ZAG, W),
          lab(ZAG, 0, 7680, W, 260,
              'Prateći tabelarni prikaz - sortirano opadajuće po ostvarenom rejtingu', 9, True)]
    L += [sek(PZAG, 420)] + K.zaglavlje() + [lin(PZAG, 0, 380, W)]
    L += [sek(DET, 300)] + K.red()
    L += [sek(POD, 520), lin(POD, 0, 40, W),
          lab(POD, 0, 120, 1400, 280, 'UKUPNO:', 11, True),
          txtf(POD, 1450, 120, 2700, 280, '=Count([NAZIV_EMISIJE]) & " emisija"', 11, True),
          K.suma('BROJ_MERENJA', POD, 120, fmt='0'),
          K.suma('PROSECAN_REJTING', POD, 120, agr='Avg', fmt='0.00'),
          K.suma('PROSECAN_UDEO', POD, 120, agr='Avg', fmt='0.00'),
          K.suma('PROSECAN_BROJ_GLEDALACA', POD, 120, agr='Avg', fmt='#,##0')]
    L += ['    Podnozje r, %d' % W,
          '    Kraj r, "rptIzv3", %s, %d, False' % (
              q('Izveštaj 3 - Gledanost emisija po žanru'), W),
          'End Sub']
    return L

# ================================================================ izvestaj 4
def izv4():
    K = Kolone(800)
    K.add('RB_TROSKA', 700, 'RB', 3, '0')
    K.add('VRSTA_TROSKA', 2000, 'Vrsta troška')
    K.add('OPIS_TROSKA', 3400, 'Opis troška')
    K.add('DATUM_NASTANKA', 1400, 'Datum nastanka', 2, 'dd.mm.yyyy')
    K.add('IZNOS', 1800, 'Iznos', 3, '#,##0.00')
    K.add('BROJ_FAKTURE', 1400, 'Broj fakture')
    K.add('STATUS_PLACANJA', 1700, 'Status plaćanja')
    W = K.sirina
    L = ['', "' ---------------------------------------------- izvestaj 4",
         'Private Sub Izvestaj4()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv4"', '    r = Poc("qIzv4_Troskovi")',
         '    Gr r, "SIFRA_PROJEKTA", True, True',
         '    Gr r, "AKT_KLJUC", True, True',
         '    Gr r, "RB_TROSKA", False, False']
    blok, _ = naslov_blok(W, 'Izveštaj 4 - Realizacija i troškovi projekta produkcije',
                          PODNASLOV, 820)
    L += blok
    L += [sek(PZAG, 420)] + K.zaglavlje() + [lin(PZAG, 0, 380, W)]
    L += [sek(G1Z, 760)]
    L += parovi(G1Z, 60, [('Projekat:', 'SIFRA_PROJEKTA', 900, 1400),
                          ('Naziv:', 'NAZIV_PROJEKTA', 700, 3000),
                          ('Vrsta produkcije:', 'VRSTA_PRODUKCIJE', 1500, 1800),
                          ('Status:', 'STATUS_PROJEKTA', 800, 1600)])
    L += parovi(G1Z, 380, [('Urednik:', 'UREDNIK_NAZIV', 900, 2000),
                           ('Emisija:', 'NAZIV_EMISIJE', 800, 2000),
                           ('Period:', 'DATUM_POCETKA', 700, 1300, 'dd.mm.yyyy'),
                           ('-', 'DATUM_ZAVRSETKA', 200, 1300, 'dd.mm.yyyy'),
                           ('Odobren budžet:', 'ODOBREN_BUDZET', 1500, 1800, '#,##0.00')])
    L += [lin(G1Z, 0, 700, W)]
    L += [sek(G2Z, 680)]
    L += parovi(G2Z, 60, [('Aktivnost:', 'RB_AKTIVNOSTI', 900, 500),
                          ('Naziv:', 'NAZIV_AKTIVNOSTI', 700, 3000),
                          ('Vrsta:', 'VRSTA_AKTIVNOSTI', 600, 1800),
                          ('Status:', 'STATUS_AKTIVNOSTI', 700, 1500)], x0=400)
    L += parovi(G2Z, 330, [('Lokacija:', 'LOKACIJA_SNIMANJA', 900, 2400),
                           ('Period:', 'DATUM_OD', 700, 1200, 'dd.mm.yyyy'),
                           ('-', 'DATUM_DO', 200, 1200, 'dd.mm.yyyy')], x0=400)
    L += [lin(G2Z, 400, 640, W - 400), sek(DET, 300)] + K.red()
    L += [sek(G2P, 360), lin(G2P, 400, 20, W - 400),
          lab(G2P, 400, 60, 3000, 250, 'Ukupno za aktivnost:', 9, True),
          K.suma('IZNOS', G2P, 60)]
    L += [sek(G1P, 700), lin(G1P, 0, 20, W),
          lab(G1P, 0, 80, 2600, 260, 'UKUPNO ZA PROJEKAT:', 10, True),
          K.suma('IZNOS', G1P, 80),
          lab(G1P, 0, 360, 2600, 250, 'Odobren budžet:'),
          txtf(G1P, 2650, 360, 1800, 250, '=Max([ODOBREN_BUDZET])', 9, True, 3, '#,##0.00'),
          lab(G1P, 4600, 360, 2000, 250, 'Iskorišćeno budžeta:'),
          txtf(G1P, 6650, 360, 1200, 250,
               '=IIf(Max([ODOBREN_BUDZET])>0,Sum([IZNOS])/Max([ODOBREN_BUDZET]),0)',
               9, True, 1, '0.0%')]
    L += [sek(POD, 520), lin(POD, 0, 40, W),
          lab(POD, 0, 120, 3400, 280, 'UKUPNO (svi projekti):', 11, True),
          K.suma('IZNOS', POD, 120)]
    L += ['    Podnozje r, %d' % W,
          '    Kraj r, "rptIzv4", %s, %d, True' % (
              q('Izveštaj 4 - Realizacija i troškovi projekta produkcije'), W),
          'End Sub']
    return L

# ================================================================ izvestaj 5
def izv5oprema():
    K = Kolone(600)
    K.add('NAZIV_PROJEKTA', 3000, 'Projekat')
    K.add('RB_AKTIVNOSTI', 700, 'RB', 3, '0')
    K.add('NAZIV_AKTIVNOSTI', 3000, 'Aktivnost')
    K.add('DATUM_REZERVACIJE', 1600, 'Datum rezervacije', 2, 'dd.mm.yyyy')
    K.add('TRAJANJE_ZADUZENJA', 1800, 'Trajanje (dana)', 3, '0')
    W = K.sirina
    L = ['', "' ------------------------------- podizvestaj: zaduzenje opreme (izvestaj 5)",
         'Private Sub Izvestaj5Oprema()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv5_Oprema"', '    r = Poc("qIzv5_Oprema")',
         '    Gr r, "INVENTARSKI_BROJ", True, True',
         '    Gr r, "DATUM_REZERVACIJE", False, False',
         sek(ZAG, 340)] + K.zaglavlje(y=40, h=240, sekcija=ZAG) + [lin(ZAG, 0, 300, W)]
    L += [sek(G1Z, 460)]
    L += parovi(G1Z, 40, [('Oprema:', 'INVENTARSKI_BROJ', 900, 1400),
                          ('Naziv:', 'NAZIV_OPREME', 700, 2400),
                          ('Model:', 'MODEL_OPREME', 700, 2000),
                          ('Status:', 'STATUS_OPREME', 700, 1400)])
    L += [lin(G1Z, 0, 400, W), sek(DET, 290)] + K.red()
    L += [sek(G1P, 340), lin(G1P, 600, 20, W - 600),
          lab(G1P, 600, 50, 3000, 250, 'Ukupno dana zaduženja:', 9, True),
          K.suma('TRAJANJE_ZADUZENJA', G1P, 50, fmt='0')]
    L += [sek(POD, 420), lin(POD, 0, 40, W),
          lab(POD, 0, 100, 3400, 260, 'UKUPNO dana zaduženja:', 10, True),
          K.suma('TRAJANJE_ZADUZENJA', POD, 100, fmt='0')]
    L += ['    Kraj r, "rptIzv5_Oprema", %s, %d, True' % (
              q('Zaduženje opreme na aktivnostima produkcije'), W),
          'End Sub']
    return L

def izv5():
    K = Kolone(600)
    K.add('NAZIV_PROJEKTA', 3000, 'Projekat')
    K.add('RB_AKTIVNOSTI', 700, 'RB', 3, '0')
    K.add('NAZIV_AKTIVNOSTI', 3000, 'Aktivnost')
    K.add('ULOGA_NA_SNIMANJU', 2400, 'Uloga na snimanju')
    K.add('DATUM_OD', 1400, 'Datum od', 2, 'dd.mm.yyyy')
    K.add('DATUM_DO', 1400, 'Datum do', 2, 'dd.mm.yyyy')
    K.add('BROJ_ANGAZOVANIH_SATI', 1500, 'Sati', 3, '0')
    W = K.sirina
    L = ['', "' ---------------------------------------------- izvestaj 5",
         'Private Sub Izvestaj5()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv5"', '    r = Poc("qIzv5_Angazovanje")',
         '    Gr r, "ZAPOSLENI_KLJUC", True, True',
         '    Gr r, "DATUM_OD", False, False']
    blok, _ = naslov_blok(
        W, 'Izveštaj 5 - Angažovanje zaposlenih i zaduženje opreme na produkciji',
        PODNASLOV, 1080, dodatno=['Prvi deo - angažovanje zaposlenih na aktivnostima produkcije'])
    L += blok
    L += [sek(PZAG, 420)] + K.zaglavlje() + [lin(PZAG, 0, 380, W)]
    L += [sek(G1Z, 500)]
    L += parovi(G1Z, 60, [('Zaposleni:', 'ZAPOSLENI_KLJUC', 1100, 3200),
                          ('Radno mesto:', 'RADNO_MESTO', 1300, 2400),
                          ('Organizaciona jedinica:', 'NAZIV_JEDINICE', 2000, 2600)])
    L += [lin(G1Z, 0, 440, W), sek(DET, 290)] + K.red()
    L += [sek(G1P, 380), lin(G1P, 600, 20, W - 600),
          lab(G1P, 600, 60, 3000, 250, 'Ukupno za zaposlenog:', 9, True),
          txtf(G1P, 3650, 60, 2400, 250,
               '=Count([NAZIV_AKTIVNOSTI]) & " angažovanja"', 9, True),
          K.suma('BROJ_ANGAZOVANIH_SATI', G1P, 60, fmt='0')]
    L += [sek(POD, 4600, rast=True), lin(POD, 0, 40, W),
          lab(POD, 0, 110, 3400, 280, 'UKUPNO SATI (svi zaposleni):', 11, True),
          K.suma('BROJ_ANGAZOVANIH_SATI', POD, 110, fmt='0'),
          lab(POD, 0, 520, W, 320,
              'Drugi deo - zaduženje opreme na aktivnostima produkcije', 12, True),
          '    Pod r, %s, 0, 880, %d, 3500, "rptIzv5_Oprema"' % (POD, W - 200)]
    L += ['    Podnozje r, %d' % W,
          '    Kraj r, "rptIzv5", %s, %d, True' % (
              q('Izveštaj 5 - Angažovanje zaposlenih i zaduženje opreme'), W),
          'End Sub']
    return L

# ================================================================ izvestaj 6
def izv6():
    K = Kolone(800)
    K.add('DATUM_EMITOVANJA', 1400, 'Datum emitovanja', 2, 'dd.mm.yyyy')
    K.add('VREME_EMITOVANJA', 1100, 'Vreme', 2, 'hh:nn')
    K.add('SIFRA_BLOKA', 1400, 'Reklamni blok')
    K.add('SIFRA_TERMINA', 1400, 'Termin')
    K.add('ZONA', 900, 'Zona', 2)
    K.add('TRAJANJE_SPOTA', 1200, 'Trajanje (s)', 3, '0')
    K.add('NAPLACENI_IZNOS', 1900, 'Naplaćeni iznos', 3, '#,##0.00')
    K.add('STATUS_NAPLATE', 1800, 'Status naplate')
    W = 14000
    L = ['', "' ---------------------------------------------- izvestaj 6",
         'Private Sub Izvestaj6()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv6"', '    r = Poc("qIzv6_Kartica")',
         '    Gr r, "BROJ_UGOVORA", True, True',
         '    Gr r, "STAVKA_KLJUC", True, True',
         '    Gr r, "DATUM_EMITOVANJA", False, False']
    blok, _ = naslov_blok(
        W, 'Izveštaj 6 - Realizacija ugovora o oglašavanju i naplata po oglašivaču',
        PODNASLOV, 1440)
    L += blok
    L += parovi(ZAG, 760, [('Oglašivač:', 'NAZIV_KLIJENTA', 1200, 3000),
                           ('Šifra:', 'SIFRA_KLIJENTA', 700, 1300),
                           ('PIB:', 'PIB', 500, 1200),
                           ('Kontakt osoba:', 'KONTAKT_OSOBA', 1500, 2200)])
    L += parovi(ZAG, 1040, [('Branša:', 'BRANSA', 800, 2200),
                            ('Grad:', 'GRAD', 600, 1800),
                            ('Godišnji budžet:', 'GODISNJI_BUDZET', 1500, 2000, '#,##0.00')])
    L += [sek(PZAG, 420)] + K.zaglavlje() + [lin(PZAG, 0, 380, W)]
    L += [sek(G1Z, 700)]
    L += parovi(G1Z, 60, [('Ugovor:', 'BROJ_UGOVORA', 800, 1400),
                          ('Sklopljen:', 'DATUM_SKLAPANJA', 1000, 1300, 'dd.mm.yyyy'),
                          ('Važi od:', 'VAZI_OD', 900, 1300, 'dd.mm.yyyy'),
                          ('do:', 'VAZI_DO', 500, 1300, 'dd.mm.yyyy'),
                          ('Status:', 'STATUS_UGOVORA', 700, 1500)])
    L += parovi(G1Z, 340, [('Vrednost ugovora:', 'UKUPNA_VREDNOST', 1700, 1900, '#,##0.00'),
                           ('Ugovoreni termini:', 'UGOVORENI_TERMINI', 1700, 3000)])
    L += [lin(G1Z, 0, 660, W)]
    L += [sek(G2Z, 680)]
    L += parovi(G2Z, 60, [('Stavka:', 'RB_STAVKE', 700, 400),
                          ('Opis:', 'OPIS_STAVKE', 600, 3200),
                          ('Ugovoreno (s):', 'KOLICINA_SEKUNDE', 1300, 900, '0'),
                          ('Jed. cena:', 'JEDINICNA_CENA', 1000, 1500, '#,##0.00'),
                          ('Popust (%):', 'POPUST', 1100, 700, '0.0')], x0=400)
    L += parovi(G2Z, 330, [('Vrednost stavke:', 'VREDNOST_STAVKE', 1600, 1800, '#,##0.00')],
                x0=400)
    L += [lin(G2Z, 400, 640, W - 400), sek(DET, 290)] + K.red()
    L += [sek(G2P, 360), lin(G2P, 800, 20, W - 800),
          lab(G2P, 800, 50, 2600, 250, 'Realizovano po stavci:', 9, True),
          K.suma('TRAJANJE_SPOTA', G2P, 50, fmt='0'),
          K.suma('NAPLACENI_IZNOS', G2P, 50)]
    L += [sek(G1P, 960), lin(G1P, 0, 20, W),
          lab(G1P, 0, 70, 3000, 260, 'REALIZACIJA UGOVORA', 10, True),
          lab(G1P, 0, 350, 1900, 250, 'Ugovoreno:'),
          txtf(G1P, 1950, 350, 1200, 250, '=Max([UGOVORENO_SEKUNDI])', 9, True, 3, '0'),
          lab(G1P, 3200, 350, 300, 250, 's'),
          txtf(G1P, 3550, 350, 1900, 250, '=Max([UGOVORENA_VREDNOST])', 9, True, 3, '#,##0.00'),
          lab(G1P, 0, 620, 1900, 250, 'Realizovano:'),
          txtf(G1P, 1950, 620, 1200, 250, '=Sum([TRAJANJE_SPOTA])', 9, True, 3, '0'),
          lab(G1P, 3200, 620, 300, 250, 's'),
          txtf(G1P, 3550, 620, 1900, 250, '=Sum([NAPLACENI_IZNOS])', 9, True, 3, '#,##0.00'),
          lab(G1P, 5700, 350, 1700, 250, 'Razlika (sekundi):'),
          txtf(G1P, 7450, 350, 1200, 250,
               '=Nz(Max([UGOVORENO_SEKUNDI]),0)-Nz(Sum([TRAJANJE_SPOTA]),0)', 9, True, 3, '0'),
          lab(G1P, 5700, 620, 1700, 250, 'Fakturisano:'),
          txtf(G1P, 7450, 620, 1900, 250, '=Max([FAKTURISANO])', 9, True, 3, '#,##0.00'),
          lab(G1P, 9600, 620, 1700, 250, 'Status fakture:'),
          txtf(G1P, 11350, 620, 2200, 250, '=Max([STATUS_FAKTURE])', 9, True, 1)]
    L += [sek(POD, 520), lin(POD, 0, 40, W),
          lab(POD, 0, 120, 3400, 280, 'UKUPNO PO OGLAŠIVAČU:', 11, True),
          K.suma('TRAJANJE_SPOTA', POD, 120, fmt='0'),
          K.suma('NAPLACENI_IZNOS', POD, 120)]
    L += ['    Podnozje r, %d' % W,
          '    Kraj r, "rptIzv6", %s, %d, True' % (
              q('Izveštaj 6 - Realizacija ugovora o oglašavanju po oglašivaču'), W),
          'End Sub']
    return L

# ================================================================ izvestaj 7
def izv7ponude():
    K = Kolone(500)
    K.add('NAZIV_KRITERIJUMA', 3400, 'Kriterijum vrednovanja')
    K.add('NACIN_BODOVANJA', 1800, 'Način bodovanja')
    K.add('BROJ_BODOVA', 1100, 'Bodovi', 3, '0.00')
    K.add('KOMENTAR_OCENE', 3400, 'Komentar ocene')
    W = 13800
    L = ['', "' ------------------------------- podizvestaj: ponude (izvestaj 7)",
         'Private Sub Izvestaj7Ponude()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv7_Ponude"', '    r = Poc("qIzv7_Ponude")',
         '    Gr r, "PONUDA_KLJUC", True, True',
         '    Gr r, "NAZIV_KRITERIJUMA", False, False',
         sek(ZAG, 330)] + K.zaglavlje(y=40, h=240, sekcija=ZAG) + [lin(ZAG, 0, 300, W)]
    L += [sek(G1Z, 660)]
    L += parovi(G1Z, 40, [('Ponuda:', 'BROJ_PONUDE', 800, 1300),
                          ('Dobavljač:', 'NAZIV_DOBAVLJACA', 1000, 2000),
                          ('Ukupna cena:', 'UKUPNA_CENA', 1300, 1600, '#,##0.00'),
                          ('Cena za stavku:', 'PONUDJENA_CENA', 1400, 1500, '#,##0.00'),
                          ('Status:', 'STATUS_PONUDE', 700, 1500)])
    L += parovi(G1Z, 320, [('Rok isporuke:', 'ROK_ISPORUKE', 1300, 1300, 'dd.mm.yyyy'),
                           ('Uslovi plaćanja:', 'USLOVI_PLACANJA', 1500, 2600),
                           ('Ukupno bodova:', 'UKUPNO_BODOVA', 1400, 900, '0.00')])
    L += [lin(G1Z, 0, 620, W), sek(DET, 280)] + K.red(y=20)
    L += [sek(G1P, 160), lin(G1P, 500, 40, W - 500)]
    L += ['    Kraj r, "rptIzv7_Ponude", %s, %d, True' % (
              q('Vrednovanje prikupljenih ponuda'), W),
          'End Sub']
    return L

def izv7():
    K = Kolone()
    K.add('RB_STAVKE', 600, 'RB', 3, '0')
    K.add('OPIS_ARTIKLA', 2400, 'Opis artikla')
    K.add('KOLICINA', 700, 'Kol.', 3, '0')
    K.add('JEDINICA_MERE', 800, 'JM')
    K.add('PROCENJENA_CENA', 1500, 'Procenjena cena', 3, '#,##0.00')
    K.add('PLANIRANI_KVARTAL', 900, 'Kvartal', 2)
    K.add('BROJ_ZAHTEVA', 1200, 'Zahtev')
    K.add('STATUS_ZAHTEVA', 1200, 'Status zahteva')
    K.add('IZABRANA_PONUDA', 1200, 'Izabrana ponuda')
    K.add('BROJ_NARUDZBENICE', 1300, 'Narudžbenica')
    K.add('IZNOS_NARUDZBENICA', 1500, 'Iznos narudžbenice', 3, '#,##0.00')
    K.add('ODSTUPANJE', 1400, 'Odstupanje', 3, '#,##0.00')
    W = K.sirina
    IZV = ('=IIf(Sum([PROCENJENA_CENA])>0,'
           'Sum([IZNOS_NARUDZBENICA])/Sum([PROCENJENA_CENA]),0)')
    L = ['', "' ---------------------------------------------- izvestaj 7",
         'Private Sub Izvestaj7()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv7"', '    r = Poc("qIzv7_Stavke")',
         '    Gr r, "SIFRA_PLANA", True, True',
         '    Gr r, "RB_STAVKE", False, False']
    blok, _ = naslov_blok(W, 'Izveštaj 7 - Realizacija plana nabavke sa vrednovanjem ponuda',
                          PODNASLOV, 820)
    L += blok
    L += [sek(PZAG, 420)] + K.zaglavlje() + [lin(PZAG, 0, 380, W)]
    L += [sek(G1Z, 760)]
    L += parovi(G1Z, 60, [('Plan nabavke:', 'SIFRA_PLANA', 1300, 1400),
                          ('Godina:', 'GODINA_PLANA', 800, 800, '0'),
                          ('Donet:', 'DATUM_DONOSENJA', 700, 1300, 'dd.mm.yyyy'),
                          ('Status:', 'STATUS_PLANA', 700, 1500),
                          ('Ukupna vrednost:', 'UKUPNA_VREDNOST', 1600, 1900, '#,##0.00')])
    L += parovi(G1Z, 380, [('Donosilac:', 'DONOSILAC_PLANA', 1000, 2400),
                           ('Zahtev za nabavku:', 'BROJ_ZAHTEVA', 1700, 1400),
                           ('Status zahteva:', 'STATUS_ZAHTEVA', 1400, 1400),
                           ('Prioritet:', 'PRIORITET', 900, 1200)])
    L += [lin(G1Z, 0, 720, W)]
    L += [sek(DET, 3300, rast=True)] + K.red()
    L += [lab(DET, 400, 340, 5000, 250, 'Prikupljene ponude i vrednovanje:', 9, True),
          '    Pod r, %s, 400, 620, %d, 2500, "rptIzv7_Ponude", "SIFRA_PLANA;RB_STAVKE",'
          ' "SIFRA_PLANA;RB_STAVKE"' % (DET, W - 800)]
    L += [sek(G1P, 700), lin(G1P, 0, 20, W),
          lab(G1P, 0, 70, 2800, 260, 'UKUPNO ZA PLAN:', 10, True),
          K.suma('PROCENJENA_CENA', G1P, 70),
          K.suma('IZNOS_NARUDZBENICA', G1P, 70),
          lab(G1P, 0, 360, 2800, 250, 'Izvršenje plana:'),
          txtf(G1P, 2850, 360, 1400, 250, IZV, 9, True, 1, '0.0%')]
    L += [sek(POD, 700), lin(POD, 0, 40, W),
          lab(POD, 0, 110, 3400, 280, 'UKUPNO (svi planovi):', 11, True),
          K.suma('PROCENJENA_CENA', POD, 110),
          K.suma('IZNOS_NARUDZBENICA', POD, 110),
          lab(POD, 0, 400, 3400, 250, 'Izvršenje plana - ukupno:'),
          txtf(POD, 3450, 400, 1400, 250, IZV, 10, True, 1, '0.0%')]
    L += ['    Podnozje r, %d' % W,
          '    Kraj r, "rptIzv7", %s, %d, True' % (
              q('Izveštaj 7 - Realizacija plana nabavke sa vrednovanjem ponuda'), W),
          'End Sub']
    return L

# ================================================================ izvestaj 8
def izv8():
    K = Kolone(800)
    K.add('SIFRA_SADRZAJA', 1400, 'Šifra sadržaja')
    K.add('NAZIV_SADRZAJA', 3600, 'Medijski sadržaj')
    K.add('FORMAT_ZAPISA', 1500, 'Format zapisa')
    K.add('OBLAST_POKRIVENOSTI', 2600, 'Oblast pokrivenosti')
    K.add('ZEMLJA_POREKLA', 1600, 'Zemlja porekla')
    K.add('UGOVOR_NABAVKE', 1500, 'Ugovor o nabavci')
    K.add('BROJ_EMITOVANJA', 1600, 'Emitovanja', 3, '0')
    W = K.sirina
    L = ['', "' ---------------------------------------------- izvestaj 8",
         'Private Sub Izvestaj8()', '    Dim r As String',
         '    ObrisiIzvestaj "rptIzv8"', '    r = Poc("qIzv8_Prava")',
         '    Gr r, "PRIORITET_STATUSA", True, True',
         '    Gr r, "LICENCA_KLJUC", True, True',
         '    Gr r, "NAZIV_SADRZAJA", False, False']
    blok, _ = naslov_blok(W, 'Izveštaj 8 - Prava korišćenja medijskog sadržaja i rokovi važenja',
                          PODNASLOV, 1080)
    L += blok
    L += parovi(ZAG, 760, [('Stanje prava na dan:', '=Date()', 1900, 1400, 'dd.mm.yyyy')])
    L += [sek(PZAG, 420)] + K.zaglavlje() + [lin(PZAG, 0, 380, W)]
    L += [sek(G1Z, 520),
          txtf(G1Z, 0, 80, 11000, 320, 'GRUPA_STATUSA', 12, True),
          lin(G1Z, 0, 460, W)]
    L += [sek(G2Z, 920)]
    L += parovi(G2Z, 60, [('Licenca:', 'BROJ_LICENCE', 800, 1400),
                          ('Vrsta prava:', 'VRSTA_PRAVA', 1200, 2200),
                          ('Nosilac prava:', 'NOSILAC_PRAVA', 1400, 2400),
                          ('Teritorija:', 'TERITORIJA', 1000, 2000)], x0=400)
    L += parovi(G2Z, 340, [('Važi od:', 'DATUM_OD', 900, 1300, 'dd.mm.yyyy'),
                           ('do:', 'DATUM_DO', 400, 1300, 'dd.mm.yyyy'),
                           ('Dana do isteka:', 'DANA_DO_ISTEKA', 1400, 900, '0'),
                           ('Status prava:', 'STATUS_PRAVA', 1200, 1900)], x0=400)
    L += parovi(G2Z, 620, [('Dozvoljeno emitovanja:', 'DOZVOLJENO_EMITOVANJA', 2200, 700, '0'),
                           ('Iskorišćeno:', 'ISKORISCENO_EMITOVANJA', 1200, 700, '0'),
                           ('Preostalo:', 'PREOSTALO_EMITOVANJA', 1100, 700, '0')], x0=400)
    L += [lin(G2Z, 400, 880, W - 400), sek(DET, 290)] + K.red()
    L += [sek(G2P, 340), lin(G2P, 800, 20, W - 800),
          lab(G2P, 800, 50, 3000, 250, 'Broj pokrivenih sadržaja:', 9, True),
          txtf(G2P, 3850, 50, 900, 250, '=Count([SIFRA_SADRZAJA])', 9, True, 1, '0'),
          K.suma('BROJ_EMITOVANJA', G2P, 50, fmt='0')]
    L += [sek(G1P, 420), lin(G1P, 0, 20, W),
          lab(G1P, 0, 80, 3400, 260, 'Ukupno u grupi:', 10, True),
          txtf(G1P, 3450, 80, 3000, 260,
               '=Count([BROJ_LICENCE]) & " redova (pravo x sadržaj)"', 10, True),
          K.suma('BROJ_EMITOVANJA', G1P, 80, fmt='0')]
    L += [sek(POD, 520), lin(POD, 0, 40, W),
          lab(POD, 0, 120, 3400, 280, 'UKUPNO:', 11, True),
          txtf(POD, 3450, 120, 3000, 280,
               '=Count([BROJ_LICENCE]) & " redova (pravo x sadržaj)"', 11, True),
          K.suma('BROJ_EMITOVANJA', POD, 120, fmt='0')]
    L += ['    Podnozje r, %d' % W,
          '    Kraj r, "rptIzv8", %s, %d, True' % (
              q('Izveštaj 8 - Prava korišćenja medijskog sadržaja i rokovi važenja'), W),
          'End Sub']
    return L

# ================================================================ upiti
def vba_str(s, uvod='    s = ', nast='    s = s & '):
    """Dugacak SQL -> niz VBA linija."""
    txt = enc(' '.join(s.split()))
    delovi, buf = [], ''
    for w in txt.split(' '):
        if len(buf) + len(w) + 1 > 170:
            delovi.append(buf); buf = w
        else:
            buf = (buf + ' ' + w).strip()
    if buf:
        delovi.append(buf)
    out = []
    for i, d in enumerate(delovi):
        d = d.replace('"', '""')
        out.append('%s"%s "' % (uvod if i == 0 else nast, d))
    return out

def gen_upiti():
    grupe = [UPITI[i:i + 4] for i in range(0, len(UPITI), 4)]
    L, imena = [], []
    for i, grupa in enumerate(grupe, 1):
        imena.append('Upiti%d' % i)
        L += ['', "' ---------------------------------------------- upiti (%d)" % i,
              'Private Sub Upiti%d()' % i, '    Dim s As String']
        for ime, sql in grupa:
            L.append("    ' " + ime)
            L += vba_str(sql)
            L.append('    Upit "%s", s' % ime)
        L.append('End Sub')
    return L, imena

# ================================================================ meni
STAVKE = [
 ('rptIzv1', 'Izveštaj 1 - Programska šema sa terminima emitovanja'),
 ('rptIzv2', 'Izveštaj 2 - Evidencija emitovanog sadržaja (playout log) - parametarski'),
 ('rptIzv3', 'Izveštaj 3 - Gledanost emisija po žanru - sa grafičkim prikazom'),
 ('rptIzv4', 'Izveštaj 4 - Realizacija i troškovi projekta produkcije'),
 ('rptIzv5', 'Izveštaj 5 - Angažovanje zaposlenih i zaduženje opreme na produkciji'),
 ('rptIzv6', 'Izveštaj 6 - Realizacija ugovora o oglašavanju po oglašivaču - parametarski'),
 ('rptIzv7', 'Izveštaj 7 - Realizacija plana nabavke sa vrednovanjem ponuda'),
 ('rptIzv8', 'Izveštaj 8 - Prava korišćenja medijskog sadržaja i rokovi važenja'),
]

def gen_meni():
    L = ['', "' ---------------------------------------------- meni izvestaja",
         'Private Sub MeniForma()',
         '    Dim frm As Form, ctl As Control, lbl As Control, priv As String',
         '    On Error GoTo Greska',
         '    ObrisiFormu "frmIzvestaji"',
         '    Set frm = CreateForm()',
         '    priv = frm.Name',
         '    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, 260, 9400, 440)',
         '    lbl.Caption = %s' % q('Izveštaji informacionog sistema TV stanice'),
         '    lbl.FontSize = 17',
         '    lbl.FontBold = True',
         '    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, 740, 9400, 280)',
         '    lbl.Caption = %s' % q('Osam izveštaja iz Specifikacije izveštaja'),
         '    lbl.FontSize = 10',
         '    lbl.ForeColor = RGB(90, 100, 120)']
    y = 1180
    for ime, naslov in STAVKE:
        L += ['    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, %d, 9400, 420)' % y,
              '    ctl.Caption = %s' % q(naslov),
              '    ctl.OnClick = "=OtvoriIzvestaj(""%s"")"' % ime,
              '    ctl.FontSize = 9']
        y += 470
    L += ['    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, %d, 9400, 560)' % (y + 160),
          '    lbl.Caption = %s' % q('Parametarski izveštaji (2 i 6) pri pokretanju traže '
                                     'vrednosti: izveštaj 2 period od-do, izveštaj 6 šifru '
                                     'ili naziv oglašivača.'),
          '    lbl.FontSize = 9',
          '    lbl.ForeColor = RGB(90, 100, 120)',
          '    frm.Section(acDetail).Height = %d' % (y + 900),
          '    frm.Width = 9800',
          '    frm.Caption = %s' % q('Izveštaji - TV Panorama'),
          '    frm.NavigationButtons = False',
          '    frm.RecordSelectors = False',
          '    frm.DividingLines = False',
          '    DoCmd.Close acForm, priv, acSaveYes',
          '    DoCmd.Rename "frmIzvestaji", acForm, priv',
          '    gForm = gForm + 1',
          '    Beleska "  forma frmIzvestaji napravljena"',
          '    Exit Sub',
          'Greska:',
          '    gGreske = gGreske + 1',
          '    Beleska "  forma frmIzvestaji nije napravljena: " & Err.Description',
          '    Err.Clear',
          '    On Error Resume Next',
          '    DoCmd.Close acForm, priv, acSaveNo',
          '    Err.Clear',
          'End Sub']
    return L

# ================================================================ glavna procedura
def gen_glavni(imena_upita):
    L = ['', "' ================================================================",
         "'  GLAVNA PROCEDURA - klikni u nju i pritisni F5",
         "' ================================================================",
         'Public Sub KreirajIzvestaje()',
         '    Dim t0 As Single',
         '    On Error GoTo Greska',
         '    t0 = Timer',
         '    gUpit = 0: gIzv = 0: gForm = 0: gGreske = 0',
         '    gPoruke = ""',
         '    DoCmd.SetWarnings False',
         '    Beleska ' + q('--- TV Panorama: dodavanje izveštaja ---'),
         '    Beleska "> upiti (qIzv...)"']
    L += ['    %s' % n for n in imena_upita]
    L += ['    Beleska "> podizvestaji"',
          '    Izvestaj5Oprema',
          '    Izvestaj7Ponude',
          '    Beleska "> izvestaji 1-8"']
    L += ['    Izvestaj%d' % i for i in range(1, 9)]
    L += ['    Beleska "> meni"',
          '    MeniForma',
          '    Application.RefreshDatabaseWindow',
          '    DoCmd.SetWarnings True',
          '    Beleska ' + q('--- gotovo ---'),
          '    MsgBox ' + q('Izveštaji su dodati u bazu.') + ' & vbCrLf & vbCrLf & _',
          '           ' + q('upita (qIzv...): ') + ' & gUpit & vbCrLf & _',
          '           ' + q('izveštaja (rptIzv...): ') + ' & gIzv & vbCrLf & _',
          '           ' + q('formi (frmIzvestaji): ') + ' & gForm & vbCrLf & _',
          '           ' + q('upozorenja: ') + ' & gGreske & vbCrLf & vbCrLf & _',
          '           ' + q('Trajanje: ') + ' & Format(Timer - t0, "0.0") & " s" & vbCrLf & _',
          '           ' + q('Tabele, forme i postojeći upiti nisu menjani.') + ', _',
          '           vbInformation, APP_NAZIV',
          '    Exit Sub',
          'Greska:',
          '    DoCmd.SetWarnings True',
          '    MsgBox ' + q('Prekid pri kreiranju izveštaja:') + ' & vbCrLf & _',
          '           Err.Number & " - " & Err.Description, vbCritical, APP_NAZIV',
          'End Sub', '',
          "' Dnevnik poslednjeg pokretanja (Ctrl+G).",
          'Public Sub Dnevnik()',
          '    Debug.Print gPoruke',
          'End Sub']
    return L

# ================================================================ sklapanje
def build():
    L = []
    d, imena = gen_upiti()
    L += d
    L += izv1() + izv2() + izv3() + izv4()
    L += izv5oprema() + izv5()
    L += izv6()
    L += izv7ponude() + izv7()
    L += izv8()
    L += gen_meni()
    L += gen_glavni(imena)
    return ZAGLAVLJE + '\n'.join(L) + '\n'

def main():
    txt = build()
    put = os.path.join(BASE, 'TV_Stanica_Izvestaji.bas')
    with open(put, 'w', newline='\r\n') as f:
        f.write(txt)
    print('%s  %d linija  %d KB' % (put, txt.count('\n'), len(txt) // 1024))

if __name__ == '__main__':
    main()
