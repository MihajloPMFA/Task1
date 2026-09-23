# -*- coding: utf-8 -*-
"""Generise VBA modul (.bas) koji se uvozi u prazan Access fajl i jednim
pokretanjem kreira tabele, veze, upite, forme za svaku tabelu, osam izvestaja
i demo podatke.  Sve se izvodi iz er/generator/schema.py, pa skripta ne moze
da se raziðe sa ER semom.

Fajl je namerno CIST ASCII: srpska slova se u Access-u sastavljaju funkcijom
T() preko ChrW, pa uvoz radi bez obzira na kodnu stranu Windows-a.
"""
import os, sys, re
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(BASE), 'er', 'generator'))
from schema import TABLES
from areas import AREAS, AREA_OF
BY = {t['name']: t for t in TABLES}

# ---------------------------------------------------------------- srpska slova
MARK = {'Č': '~C', 'č': '~c', 'Ć': '~K', 'ć': '~k',
        'Š': '~S', 'š': '~s', 'Ž': '~Z', 'ž': '~z',
        'Đ': '~D', 'đ': '~d'}

def enc(s):
    """Srpski tekst -> ASCII sa markerima koje VBA funkcija T() vraca nazad."""
    s = s.replace('\u2014', '-').replace('\u2013', '-')
    s = s.replace('\u201e', '"').replace('\u201c', '"').replace('\u00b7', '-')
    if all(ord(c) <= 126 for c in s):
        return s                       # vec u ASCII obliku (markeri su namerni)
    if '~' in s:
        raise ValueError('tekst mesa prava slova i markere: %r' % s)
    for k, v in MARK.items():
        s = s.replace(k, v)
    bad = [c for c in s if ord(c) > 126]
    if bad:
        raise ValueError('neprevedeni znakovi %r u %r' % (bad, s))
    return s

def q(s):
    """VBA izraz za srpski tekst: literal, a ako ima markera - umotan u T()."""
    e = enc(s)
    lit = '"%s"' % e.replace('"', '""')
    return 'T(%s)' % lit if '~' in e else lit

# ---------------------------------------------------------------- natpisi
IZUZETAK = {
 'SIFRA': 'šifra', 'SEMA': 'šema', 'SEME': 'šeme', 'ZANR': 'žanr',
 'SADRZAJ': 'sadržaj', 'SADRZAJA': 'sadržaja', 'TROSAK': 'trošak',
 'TROSKA': 'troška', 'NARUDZBENICA': 'narudžbenica', 'NARUDZBENICE': 'narudžbenice',
 'NARUDZBINE': 'narudžbine', 'BUDZET': 'budžet', 'DOBAVLJAC': 'dobavljač',
 'DOBAVLJACA': 'dobavljača', 'OGLASIVAC': 'oglašivač', 'OGLASIVACA': 'oglašivača',
 'OGLASAVANJU': 'oglašavanju', 'PROIZVODJAC': 'proizvođač', 'NADREDJENE': 'nadređene',
 'UTVRDJENO': 'utvrđeno', 'PREDVIDJENO': 'predviđeno', 'ISKORISCENO': 'iskorišćeno',
 'ISKORISCENOST': 'iskorišćenost', 'KORISCENJA': 'korišćenja',
 'OVLASCENJA': 'ovlašćenja', 'OVLASCENI': 'ovlašćeni', 'PLACANJA': 'plaćanja',
 'PLACANJE': 'plaćanje', 'ZAVRSETKA': 'završetka', 'POSTANSKI': 'poštanski',
 'MATICNI': 'matični', 'JEDINICNA': 'jedinična', 'GRAFICKI': 'grafički',
 'TEHNICKO': 'tehničko', 'KOLICINA': 'količina', 'OBRAZLOZENJE': 'obrazloženje',
 'ZADUZENJE': 'zaduženje', 'ZADUZENJA': 'zaduženja', 'RAZDUZENJA': 'razduženja',
 'ANGAZOVANJE': 'angažovanje', 'ANGAZOVANIH': 'angažovanih', 'SKLADISTA': 'skladišta',
 'RESAVANJA': 'rešavanja', 'RESENJA': 'rešenja', 'VRACANJU': 'vraćanju',
 'VLASNISTVA': 'vlasništva', 'DONOSENJA': 'donošenja', 'GODISNJI': 'godišnji',
 'BRANSA': 'branša', 'PROSECNO': 'prosečno', 'IZVESTAVANJA': 'izveštavanja',
 'MONTAZA': 'montaža', 'MUZICKI': 'muzički', 'RATING': 'rejting',
 'LEGITIM': 'legitimacije', 'REKL': 'reklamnih', 'INFO': 'informacija',
 'ZAKUPLJENO': 'zakupljeno', 'ZAPIS': 'zapis', 'ZAHTEV': 'zahtev',
 'MEDIJSKI': 'medijski', 'CELINA': 'celina', 'CELINE': 'celine',
}
NEPROMENJENO = {'PIB', 'JMBG', 'PDV', 'TV', 'RB'}
MALA = {'I', 'O', 'U', 'NA', 'ZA', 'PO', 'OD', 'DO', 'PRI'}

def rec(w):
    if w in NEPROMENJENO:
        return w
    return IZUZETAK.get(w, w.lower())

def natpis(ime):
    d = ime.split('_')
    out = []
    for i, w in enumerate(d):
        r = rec(w)
        if w == 'RB':
            r = 'redni broj' if i == 0 else 'rb'
        if i == 0 and r not in NEPROMENJENO:
            r = r[0].upper() + r[1:]
        out.append(r)
    s = ' '.join(out)
    return s.replace(' ( fk )', '')

# ---------------------------------------------------------------- tipovi
def vba_tip(t):
    m = re.match(r'CHAR\((\d+)\)', t)
    if m: return 'T', m.group(1)
    m = re.match(r'VARCHAR\((\d+)\)', t)
    if m: return 'T', m.group(1)
    if t == 'INTEGER': return 'L', '0'
    if t == 'DECIMAL(12,2)': return 'C', '0'
    if t == 'DECIMAL(5,2)': return 'D', '0'
    if t == 'DATE': return 'Dt', '0'
    if t == 'TIME': return 'Tm', '0'
    raise ValueError(t)

def polja_str(t):
    out = []
    for c in t['cols']:
        tp, sz = vba_tip(c['t'])
        out.append('%s:%s:%s:%s' % (c['n'], tp, sz, '1' if not c['null'] else '0'))
    return '|'.join(out)

# ================================================================ emiter
from vba_lib import ZAGLAVLJE, FORME_IZVESTAJI
from upiti import U as UPITI
from demo_data import D as DEMO

def vba_str(s, uvod='    s = ', nast='    s = s & '):
    """Dugacak string -> niz VBA linija (VBA dozvoljava max 1023 znaka po liniji)."""
    txt = enc(' '.join(s.split()))
    delovi, buf = [], ''
    for w in txt.split(' '):
        if len(buf) + len(w) + 1 > 180:
            delovi.append(buf); buf = w
        else:
            buf = (buf + ' ' + w).strip()
    if buf: delovi.append(buf)
    out = []
    for i, d in enumerate(delovi):
        d = d.replace('"', '""')
        if i == 0:
            out.append('%s"%s "' % (uvod, d))
        else:
            out.append('%s"%s "' % (nast, d))
    return out

def blokovi(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

# ---- 1. recnik natpisa
def gen_recnik():
    L = ['', "' ---------------------------------------------------------------- recnik",
         'Private Sub PuniRecnik()', '    Set gRec = CreateObject("Scripting.Dictionary")']
    for k in sorted(IZUZETAK):
        L.append('    R "%s", %s' % (k, q(IZUZETAK[k])))
    L.append('End Sub')
    return L

# ---- 2. tabele
def gen_tabele():
    L, imena = [], []
    for i, grupa in enumerate(blokovi([t['name'] for t in TABLES], 24), 1):
        imena.append('Tabele%d' % i)
        L += ['', 'Private Sub Tabele%d()' % i]
        for n in grupa:
            L.append('    NapraviTabelu "%s", "%s"' % (n, polja_str(BY[n])))
        L.append('End Sub')
    return L, imena

# ---- 3. kljucevi i veze
def gen_kljucevi():
    L, imena = [], []
    pk = [(t['name'], ','.join(t['pk'])) for t in TABLES]
    fk = [(f['name'], t['name'], ','.join(f['child']), f['parent'], ','.join(f['pcols']))
          for t in TABLES for f in t['fks']]
    for i, grupa in enumerate(blokovi(pk, 40), 1):
        imena.append('Kljucevi%d' % i)
        L += ['', 'Private Sub Kljucevi%d()' % i]
        for n, p in grupa:
            L.append('    PK "%s", "%s"' % (n, p))
        L.append('End Sub')
    for i, grupa in enumerate(blokovi(fk, 30), 1):
        imena.append('Veze%d' % i)
        L += ['', 'Private Sub Veze%d()' % i]
        for a in grupa:
            L.append('    FK "%s", "%s", "%s", "%s", "%s"' % a)
        L.append('End Sub')
    return L, imena

# ---- 4. upiti
def gen_upiti():
    L, imena = [], []
    for i, grupa in enumerate(blokovi(UPITI, 5), 1):
        imena.append('Upiti%d' % i)
        L += ['', 'Private Sub Upiti%d()' % i, '    Dim s As String']
        for ime, sql in grupa:
            L.append('    ' + "'" + ' ' + ime)
            L += vba_str(sql)
            L.append('    NapraviUpit "%s", s' % ime)
        L.append('End Sub')
    return L, imena

# ---- 5. forme
def gen_forme():
    L, imena = [], []
    for i, grupa in enumerate(blokovi([t['name'] for t in TABLES], 24), 1):
        imena.append('Forme%d' % i)
        L += ['', 'Private Sub Forme%d()' % i]
        for n in grupa:
            L.append('    NapraviFormu "%s"' % n)
        L.append('End Sub')
    return L, imena

# ---- 6. izvestaji
IZV = [
 dict(ime='rptProgramskaSema', upit='qryProgramskaSema',
      naslov='Izveštaj 1 - Programska šema sa terminima emitovanja',
      grupa='NAZIV_CELINE', sume='TRAJANJE_TERMINA', pejzaz=True,
      kolone=[('VREME_POCETKA',1100),('NAZIV_EMISIJE',2600),('ZANR',1400),
              ('TRAJANJE_TERMINA',1100),('TIP_TERMINA',1300),('ZONA_GLEDANOSTI',1100),
              ('REDNI_BROJ_REPRIZE',1100),('STATUS_TERMINA',1400)]),
 dict(ime='rptPlayoutLog', upit='qryPlayoutLog',
      naslov='Izveštaj 2 - Evidencija emitovanog sadržaja (playout log)',
      grupa='DATUM', sume='STVARNO_TRAJANJE', pejzaz=True,
      kolone=[('DATUM',1100),('STVARNO_VREME_POCETKA',1100),('NAZIV_EMISIJE',2200),
              ('NAZIV_SADRZAJA',2400),('TRAJANJE_TERMINA',1000),('STVARNO_TRAJANJE',1000),
              ('ODSTUPANJE',1000),('STATUS_REALIZACIJE',1300),('BROJ_LICENCE',1400),
              ('NAPOMENA_O_SMETNJAMA',2400)]),
 dict(ime='rptGledanost', upit='qryGledanostEmisija',
      naslov='Izveštaj 3 - Gledanost emisija po žanru', grupa='', sume='', pejzaz=True,
      kolone=[('NAZIV_EMISIJE',2800),('ZANR',1600),('BROJ_MERENJA',1200),
              ('PROSECAN_REJTING',1500),('PROSECAN_UDEO',1500),
              ('PROSECAN_BROJ_GLEDALACA',2000),('PROSECNO_GLEDANJE',1800)]),
 dict(ime='rptTroskoviProjekta', upit='qryTroskoviProjekta',
      naslov='Izveštaj 4 - Realizacija i troškovi projekta produkcije',
      grupa='NAZIV_PROJEKTA', sume='IZNOS', pejzaz=True,
      kolone=[('RB_AKTIVNOSTI',700),('NAZIV_AKTIVNOSTI',2600),('VRSTA_AKTIVNOSTI',1600),
              ('RB_TROSKA',700),('VRSTA_TROSKA',1600),('OPIS_TROSKA',2400),
              ('DATUM_NASTANKA',1200),('IZNOS',1500),('BROJ_FAKTURE',1400)]),
 dict(ime='rptZaduzenjeOpreme', upit='qryZaduzenjeOpreme',
      naslov='Zaduženje opreme po aktivnostima produkcije', grupa='',
      sume='TRAJANJE_ZADUZENJA', pejzaz=False,
      kolone=[('INVENTARSKI_BROJ',1500),('NAZIV_OPREME',2400),('NAZIV_AKTIVNOSTI',3000),
              ('DATUM_REZERVACIJE',1500),('TRAJANJE_ZADUZENJA',1600)]),
 dict(ime='rptAngazovanjeIOprema', upit='qryAngazovanje',
      naslov='Izveštaj 5 - Angažovanje zaposlenih i zaduženje opreme',
      grupa='ZAPOSLENI_NAZIV', sume='BROJ_ANGAZOVANIH_SATI', pejzaz=True,
      kolone=[('NAZIV_PROJEKTA',3000),('NAZIV_AKTIVNOSTI',3000),('ULOGA_NA_SNIMANJU',2400),
              ('DATUM_OD',1300),('DATUM_DO',1300),('BROJ_ANGAZOVANIH_SATI',1600)]),
 dict(ime='rptKarticaOglasivaca', upit='qryKarticaOglasivaca',
      naslov='Izveštaj 6 - Realizacija ugovora o oglašavanju po oglašivaču',
      grupa='BROJ_UGOVORA', sume='NAPLACENI_IZNOS', pejzaz=True,
      kolone=[('RB_STAVKE',800),('OPIS_STAVKE',2800),('KOLICINA_SEKUNDE',1300),
              ('JEDINICNA_CENA',1400),('VREDNOST_STAVKE',1600),('DATUM_EMITOVANJA',1400),
              ('VREME_EMITOVANJA',1200),('TRAJANJE_SPOTA',1200),('NAPLACENI_IZNOS',1600),
              ('STATUS_NAPLATE',1600)]),
 dict(ime='rptVrednovanjePonuda', upit='qryVrednovanjePonuda',
      naslov='Vrednovanje ponuda dobavljača', grupa='BROJ_PONUDE', sume='', pejzaz=False,
      kolone=[('NAZIV_DOBAVLJACA',2600),('NAZIV_KRITERIJUMA',2800),('BROJ_BODOVA',1200),
              ('UKUPNO_BODOVA',1400),('STATUS_PONUDE',1600)]),
 dict(ime='rptPlanNabavke', upit='qryPlanNabavke',
      naslov='Izveštaj 7 - Realizacija plana nabavke sa vrednovanjem ponuda',
      grupa='', sume='PROCENJENA_CENA|UKUPAN_IZNOS', pejzaz=True,
      kolone=[('RB_STAVKE',800),('OPIS_ARTIKLA',3000),('KOLICINA',1000),
              ('PLANIRANI_KVARTAL',1400),('PROCENJENA_CENA',1600),('BROJ_ZAHTEVA',1600),
              ('STATUS_ZAHTEVA',1400),('BROJ_NARUDZBENICE',1500),('UKUPAN_IZNOS',1600)]),
 dict(ime='rptPravaKoriscenja', upit='qryPravaKoriscenja',
      naslov='Izveštaj 8 - Prava korišćenja medijskog sadržaja i rokovi važenja',
      grupa='', sume='', pejzaz=True,
      kolone=[('BROJ_LICENCE',1600),('VRSTA_PRAVA',2400),('DATUM_DO',1200),
              ('DANA_DO_ISTEKA',1300),('DOZVOLJENO_EMITOVANJA',1400),
              ('ISKORISCENO_EMITOVANJA',1400),('PREOSTALO_EMITOVANJA',1400),
              ('NAZIV_SADRZAJA',2400),('STATUS_PRAVA',1500)]),
]

def gen_izvestaji():
    L = ['', "' ---------------------------------------------------------------- izvestaji",
         'Private Sub Izvestaji()', '    Dim r As String']
    for d in IZV:
        kol = '|'.join('%s:%d' % (k, w) for k, w in d['kolone'])
        L.append('    r = NapraviIzvestaj("%s", "%s", %s, _' % (d['ime'], d['upit'], q(d['naslov'])))
        L.append('        "%s", "%s", "%s", %s)'
                 % (kol, d['grupa'], d['sume'], 'True' if d['pejzaz'] else 'False'))
    L += ['',
          '    DodajGrafikon "rptGledanost", "qryGledanostPoZanru", ' +
          q('Prosečan ostvareni rejting po žanru emisije'),
          '    DodajPodizvestaj "rptAngazovanjeIOprema", "rptZaduzenjeOpreme", ' +
          q('Zaduženje opreme u istom periodu') + ', 3000',
          '    DodajPodizvestaj "rptPlanNabavke", "rptVrednovanjePonuda", ' +
          q('Vrednovanje prikupljenih ponuda') + ', 3400',
          'End Sub']
    return L

# ---- 7. demo podaci
def gen_demo():
    L, imena = [], []
    stavke = []
    for tab, kol, redovi in DEMO:
        for r in redovi:
            stavke.append((tab, kol, r))
    for i, grupa in enumerate(blokovi(stavke, 45), 1):
        imena.append('DemoPodaci%d' % i)
        L += ['', 'Private Sub DemoPodaci%d()' % i]
        for tab, kol, r in grupa:
            sql = 'INSERT INTO [%s] (%s) VALUES (%s);' % (
                tab, ','.join('[%s]' % c for c in kol.split(',')), ','.join(r))
            L.append('    Ubaci %s' % q(sql))
        L.append('End Sub')
    return L, imena

# ---- 8. glavni meni
def gen_meni():
    stavke = [(d['ime'], d['naslov']) for d in IZV if d['naslov'].startswith('Izve')]
    L = ['', "' ---------------------------------------------------------------- glavni meni",
         'Public Function OtvoriIzvestaj(ByVal ime As String)',
         '    On Error Resume Next',
         '    DoCmd.OpenReport ime, acViewPreview',
         'End Function', '',
         'Public Function OtvoriFormu(ByVal ime As String)',
         '    On Error Resume Next',
         '    DoCmd.OpenForm ime',
         'End Function', '',
         'Private Sub GlavniMeni()',
         '    Dim frm As Form, ctl As Control, lbl As Control, priv As String, y As Long',
         '    On Error GoTo Greska',
         '    Obrisi "F", "frm_GLAVNI_MENI"',
         '    Set frm = CreateForm()',
         '    priv = frm.Name',
         '    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, 260, 9000, 460)',
         '    lbl.Caption = ' + q('TV Panorama - informacioni sistem TV stanice'),
         '    lbl.FontSize = 18',
         '    lbl.FontBold = True',
         '    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, 760, 9000, 300)',
         '    lbl.Caption = ' + q('Izveštaji'),
         '    lbl.FontSize = 11',
         '    lbl.FontBold = True',
         '    y = 1120']
    for ime, naslov in stavke:
        L += ['    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, y, 8600, 400)',
              '    ctl.Caption = %s' % q(naslov),
              '    ctl.OnClick = "=OtvoriIzvestaj(""%s"")"' % ime,
              '    y = y + 460']
    L += ['    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, y + 200, 9000, 300)',
          '    lbl.Caption = ' + q('Forme za unos nalaze se u oknu objekata, sa prefiksom frm_'),
          '    lbl.FontSize = 9',
          '    lbl.ForeColor = RGB(90, 100, 120)',
          '    frm.Section(acDetail).Height = y + 800',
          '    frm.Width = 9300',
          '    frm.Caption = ' + q('TV Panorama'),
          '    frm.NavigationButtons = False',
          '    frm.RecordSelectors = False',
          '    DoCmd.Close acForm, priv, acSaveYes',
          '    DoCmd.Rename "frm_GLAVNI_MENI", acForm, priv',
          '    gForm = gForm + 1',
          '    Exit Sub',
          'Greska:',
          '    Beleska "  glavni meni nije napravljen: " & Err.Description',
          '    Err.Clear',
          'End Sub']
    return L

# ---- 9. glavna procedura
def gen_glavni(faze):
    L = ['', "' ================================================================",
         "'  GLAVNA PROCEDURA - pokrenuti je (kursor u njoj, pa F5)",
         "' ================================================================",
         'Public Sub KreirajSve()',
         '    Dim t0 As Single',
         '    On Error GoTo Greska',
         '    t0 = Timer',
         '    gTab = 0: gUpit = 0: gForm = 0: gIzv = 0',
         '    gVeza = 0: gRed = 0: gGreske = 0',
         '    gPoruke = ""',
         '    DoCmd.SetWarnings False',
         '    Beleska ' + q('--- TV Panorama: kreiranje baze ---')]
    naslovi = {'obrisi': 'brisanje postojecih objekata', 'recnik': 'recnik natpisa',
               'tabele': 'tabele', 'kljucevi': 'primarni kljucevi', 'veze': 'veze',
               'upiti': 'upiti', 'demo': 'demo podaci', 'forme': 'forme',
               'izvestaji': 'izvestaji', 'meni': 'glavni meni'}
    for kljuc, imena in faze:
        L.append('    Beleska "> %s"' % naslovi[kljuc])
        for ime in imena:
            L.append('    %s' % ime)
        if kljuc == 'tabele':
            L.append('    CurrentDb.TableDefs.Refresh')
    L += ['    Application.RefreshDatabaseWindow',
          '    DoCmd.SetWarnings True',
          '    Beleska ' + q('--- gotovo ---'),
          '    MsgBox ' + q('Baza je kreirana.') + ' & vbCrLf & vbCrLf & _',
          '           ' + q('tabela: ') + ' & gTab & vbCrLf & _',
          '           ' + q('veza: ') + ' & gVeza & vbCrLf & _',
          '           ' + q('upita: ') + ' & gUpit & vbCrLf & _',
          '           ' + q('formi: ') + ' & gForm & vbCrLf & _',
          '           ' + q('izveštaja: ') + ' & gIzv & vbCrLf & _',
          '           ' + q('demo redova: ') + ' & gRed & vbCrLf & _',
          '           ' + q('upozorenja: ') + ' & gGreske & vbCrLf & vbCrLf & _',
          '           ' + q('Trajanje: ') + ' & Format(Timer - t0, "0.0") & " s", _',
          '           vbInformation, APP_NAZIV',
          '    Exit Sub',
          'Greska:',
          '    DoCmd.SetWarnings True',
          '    MsgBox ' + q('Prekid u koraku kreiranja:') + ' & vbCrLf & _',
          '           Err.Number & " - " & Err.Description, vbCritical, APP_NAZIV',
          'End Sub', '',
          "' Ispis dnevnika poslednjeg pokretanja u Immediate prozor (Ctrl+G).",
          'Public Sub Dnevnik()',
          '    Debug.Print gPoruke',
          'End Sub']
    return L

# ================================================================ sklapanje
MODUL = 'modKreirajBazu'

def build():
    faze = []
    L = []
    L += gen_recnik()
    faze.append(('obrisi', ['ObrisiSve']))
    faze.append(('recnik', ['PuniRecnik']))

    d, imena = gen_tabele();   L += d; faze.append(('tabele', imena))
    d, imena = gen_kljucevi()
    L += d
    faze.append(('kljucevi', [i for i in imena if i.startswith('Kljucevi')]))
    faze.append(('veze', [i for i in imena if i.startswith('Veze')]))
    d, imena = gen_upiti();    L += d; faze.append(('upiti', imena))
    d, imena = gen_demo();     L += d; faze.append(('demo', imena))
    d, imena = gen_forme();    L += d; faze.append(('forme', imena))
    L += gen_izvestaji();      faze.append(('izvestaji', ['Izvestaji']))
    L += gen_meni();           faze.append(('meni', ['GlavniMeni']))
    L += gen_glavni(faze)

    telo = ('Attribute VB_Name = "%s"\n' % MODUL) + ZAGLAVLJE + FORME_IZVESTAJI \
           + '\n'.join(L) + '\n'
    return telo

def main():
    txt = build()
    put = os.path.join(BASE, 'TV_Stanica_Access.bas')
    with open(put, 'w', newline='\r\n') as f:
        f.write(txt)
    print('%s  %d linija  %d KB' % (put, txt.count('\n'), len(txt) // 1024))

if __name__ == '__main__':
    main()
