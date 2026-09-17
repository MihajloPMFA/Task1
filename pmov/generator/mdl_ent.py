# -*- coding: utf-8 -*-
"""Entiteti PMOV-a IS Televizijske stanice.
Svaki entitet je izveden iz skladista podataka (DFD) i/ili tokova i aktivnosti (IDEF0).
Atribut: (naziv, slot, tip). tip: 'pk' primarni kljuc, 'pd' parcijalni kljuc slabog
entiteta, 'der' izvedeni atribut, '' obican.
"""
from geom import *

ENT, ORDER = {}, []
def E(k, name, x, y, kind, attrs, src=''):
    ENT[k] = dict(k=k, name=name, x=x, y=y, kind=kind, attrs=attrs, src=src)
    ORDER.append(k)

C  = lambda i: 8.0 + COL_DX * i
BA, BB, BC, BD, BE, BF = 96.0, 78.0, 62.0, 45.0, 28.0, 11.0

# ======================= BAND A - ORGANIZACIJA, KADROVI, OPREMA ==================
E('ORGJED', 'ORGANIZACIONA\nJEDINICA', C(0), BA, 'strong', [
    ('ŠIFRA JEDINICE','N0','pk'), ('NAZIV JEDINICE','N3',''),
    ('TIP JEDINICE','NW',''),      ('OPIS DELATNOSTI','NE',''),
    ('DATUM OSNIVANJA','S0',''),   ('BROJ ZAPOSLENIH','S3','der')],
  'DFD: Organizaciona sema i sistematizacija; IDEF0: Hijerarhijska struktura TV stanice')

E('ZAPOSLENI', 'ZAPOSLENI', C(1), BA, 'strong', [
    ('ŠIFRA ZAPOSLENOG','N0','pk'), ('JMBG','N3',''),
    ('IME','NW',''),                ('PREZIME','NE',''),
    ('RADNO MESTO','S0',''),        ('DATUM ZAPOSLENJA','S3',''),
    ('OSNOVNA ZARADA','SW',''),     ('STATUS ZAPOSLENJA','SE','')],
  'DFD: Zaposleni, Dokumentacija o zaposlenima; IDEF0: Podaci o zaposlenom')

E('UREDNIK',  'UREDNIK', 5.5, BA-SUB_DY, 'sub',
  [('NIVO OVLAŠĆENJA','SL',''), ('REDAKCIJA','SR','')], 'IDEF0: Urednik, Glavni urednik')
E('NOVINAR',  'NOVINAR /\nREPORTER', 12.7, BA-SUB_DY, 'sub',
  [('OBLAST IZVEŠTAVANJA','SL',''), ('BROJ NOVINARSKE LEG.','SR','')], 'IDEF0: Novinari, Reporter')
E('SNIMATELJ','SNIMATELJ', 19.9, BA-SUB_DY, 'sub',
  [('SPECIJALNOST','SL',''), ('KATEGORIJA DOZVOLE','SR','')], 'IDEF0: Snimatelji, Audio-rasvetni tehnicar')
E('REFERENT', 'REFERENT', 27.1, BA-SUB_DY, 'sub',
  [('VRSTA REFERATA','SL',''), ('LIMIT ODOBRAVANJA','SR','')],
  'IDEF0: Referent za nabavku, Referent za oglasavanje')

E('OPREMA', 'OPREMA', C(3), BA, 'strong', [
    ('INVENTARSKI BROJ','N0','pk'), ('NAZIV OPREME','N3',''),
    ('MODEL','NW',''),              ('PROIZVOĐAČ','NE',''),
    ('STATUS OPREME','S0',''),      ('DATUM NABAVKE','S3',''),
    ('GARANCIJA DO','SW',''),       ('NABAVNA VREDNOST','SE','')],
  'DFD: Oprema, Registar opreme; IDEF0: Status opreme, Hardver i oprema')
E('OPRSNIM','SNIMATELJSKA\nOPREMA', C(3)-3.0, BA-SUB_DY, 'sub',
  [('TIP NOSAČA ZAPISA','SL',''), ('REZOLUCIJA','SR','')], 'IDEF0: Snimateljska oprema')
E('OPRSTUD','STUDIJSKA I\nEMISIONA OPREMA', C(3)+3.0, BA-SUB_DY, 'sub',
  [('LOKACIJA U STUDIJU','SL',''), ('PROPUSNOST KANALA','SR','')], 'IDEF0: TV studio i kontrolna soba')

# ======================= BAND B - PRODUKCIJA =====================================
E('PROJEKAT', 'PROJEKAT\nPRODUKCIJE', C(0), BB, 'strong', [
    ('ŠIFRA PROJEKTA','N0','pk'), ('NAZIV PROJEKTA','N3',''),
    ('DATUM POČETKA','NW',''),    ('DATUM ZAVRŠETKA','NE',''),
    ('ODOBREN BUDŽET','S0',''),   ('STATUS PROJEKTA','S3',''),
    ('VRSTA PRODUKCIJE','SW',''), ('OPIS PROJEKTA','SE','')],
  'DFD: Projekti produkcije, Arhiva planova produkcije; IDEF0: Plan/Budzet produkcije')

E('AKTIVNOST', 'AKTIVNOST\nPRODUKCIJE', C(1), BB, 'weak', [
    ('RB AKTIVNOSTI','N0','pd'),    ('NAZIV AKTIVNOSTI','N3',''),
    ('DATUM OD','NW',''),           ('DATUM DO','NE',''),
    ('VRSTA AKTIVNOSTI','S0',''),   ('LOKACIJA SNIMANJA','S1',''),
    ('STATUS AKTIVNOSTI','S3',''),  ('PLANIRANO TRAJANJE','SE','')],
  'IDEF0: DEFINISANJE AKTIVNOSTI PROJEKTA; DFD: Lista aktivnosti sa resursima')

E('TROSAK', 'TROŠAK\nPRODUKCIJE', C(2), BB, 'weak', [
    ('RB TROŠKA','N0','pd'),   ('VRSTA TROŠKA','N3',''),
    ('IZNOS','NW',''),         ('DATUM NASTANKA','NE',''),
    ('OPIS TROŠKA','S0',''),   ('ODSTUPANJE OD BUDŽETA','S3','der')],
  'DFD: Troskovi produkcije, Evidentiran trosak produkcije')

E('SNIMAK', 'SIROVI\nSNIMAK', C(3), BB, 'strong', [
    ('ŠIFRA SNIMKA','N0','pk'),  ('DATUM SNIMANJA','N3',''),
    ('TRAJANJE','NW',''),        ('FORMAT SNIMKA','NE',''),
    ('LOKACIJA SNIMKA','S0',''), ('OCENA KVALITETA','S3','')],
  'DFD: Sirovi snimci, Snimci za montazu, Preuzeti snimci sa terena')

E('GRAFEL', 'GRAFIČKI I\nMUZIČKI ELEMENT', C(5), BB, 'strong', [
    ('ŠIFRA ELEMENTA','N0','pk'), ('NAZIV ELEMENTA','N3',''),
    ('TIP ELEMENTA','NW',''),     ('AUTOR','NE',''),
    ('FORMAT','S0',''),           ('USLOV KORIŠĆENJA','S3','')],
  'DFD: Graficki sabloni i muzicka biblioteka; IDEF0: Sabloni i muzicke podloge')

# ======================= BAND C - EMITOVANJE =====================================
E('PSEMA', 'PROGRAMSKA\nŠEMA', C(0), BC, 'strong', [
    ('ID ŠEME','N0','pk'),      ('NAZIV ŠEME','N3',''),
    ('SEZONA','NW',''),         ('VERZIJA ŠEME','NE',''),
    ('DATUM OD','S0',''),       ('DATUM DO','S1',''),
    ('STATUS ŠEME','S2',''),    ('DATUM USVAJANJA','S3','')],
  'DFD: Programska sema, Usvojene programske seme, Arhiva programskih sema')

E('PCELINA', 'PROGRAMSKA\nCELINA', C(1), BC, 'weak', [
    ('RB CELINE','N0','pd'),    ('NAZIV CELINE','N3',''),
    ('TIP CELINE','NW',''),     ('DAN U NEDELJI','NE',''),
    ('VREME OD','S0',''),       ('VREME DO','S3','')],
  'DFD: Programske celine, Definisane dnevne programske celine')

E('TERMIN', 'TERMIN\nEMITOVANJA', C(2), BC, 'strong', [
    ('ŠIFRA TERMINA','N0','pk'), ('DATUM','N3',''),
    ('VREME POČETKA','NW',''),   ('TRAJANJE TERMINA','NE',''),
    ('TIP TERMINA','S0',''),     ('ZONA GLEDANOSTI','SW',''),
    ('STATUS TERMINA','S3',''),  ('REDNI BROJ REPRIZE','SE','')],
  'DFD: Raspored termina, TV program po satnici, Raspored repriza')

E('ZAPISEM', 'ZAPIS O\nEMITOVANJU', C(3), BC, 'weak', [
    ('RB EMITOVANJA','N0','pd'),      ('STATUS REALIZACIJE','N3',''),
    ('STVARNO VREME POČ.','NW',''),   ('STVARNO TRAJANJE','NE',''),
    ('NAPOMENA O SMETNJAMA','S0',''), ('OPERATER EMITOVANJA','S3','')],
  'DFD: Evidencija emitovanja, Zapis o emitovanom sadrzaju, Sta je emitovano i kada')

E('EMISIJA', 'EMISIJA', C(4), BC, 'strong', [
    ('ŠIFRA EMISIJE','N0','pk'),      ('NAZIV EMISIJE','N3',''),
    ('ŽANR','NW','mv'),               ('FORMAT EMISIJE','NE',''),
    ('PREDVIĐENO TRAJANJE','S0',''),  ('CILJNA PUBLIKA','S3',''),
    ('STATUS EMISIJE','SW',''),       ('PROGRAMSKI ELABORAT','SE','')],
  'DFD: Podaci o emisijama, Informacije o emisijama; IDEF0: Emisija, Format emisije')

E('MSADRZAJ', 'MEDIJSKI\nSADRŽAJ', C(5), BC, 'strong', [
    ('ŠIFRA SADRŽAJA','N0','pk'), ('NAZIV SADRŽAJA','N3',''),
    ('TRAJANJE','NW',''),         ('FORMAT ZAPISA','NE',''),
    ('DATUM ARHIVIRANJA','S0',''),('LOKACIJA U ARHIVI','S3','')],
  'DFD: Medijska arhiva, Katalog TV sadrzaja, Metapodaci o sadrzaju')
E('MSPROD','PRODUCIRANI\nSADRŽAJ', C(5)-SUB_DX, BC-SUB_DY, 'sub',
  [('DATUM PRODUKCIJE','SL',''), ('VERZIJA MASTERA','SR','')], 'IDEF0: Produciran TV sadrzaj')
E('MSNAB', 'NABAVLJENI\nSADRŽAJ', C(5), BC-SUB_DY, 'sub',
  [('ZEMLJA POREKLA','SL',''), ('CENA NABAVKE','SR','')], 'DFD: Spisak nabavljenih TV sadrzaja')
E('MSREK', 'REKLAMNI\nSADRŽAJ', C(5)+SUB_DX, BC-SUB_DY, 'sub',
  [('DATUM PRIJEMA','SL',''), ('STATUS PROVERE','SR','')], 'DFD: Reklamni materijali')

E('PRAVO', 'PRAVO\nKORIŠĆENJA', C(6), BC, 'strong', [
    ('BROJ LICENCE','N0','pk'),         ('VRSTA PRAVA','N3',''),
    ('DATUM OD','NW',''),               ('DATUM DO','NE',''),
    ('DOZVOLJENO EMITOVANJA','S0',''),  ('ISKORIŠĆENO EMITOVANJA','S1','der'),
    ('TERITORIJA','S2',''),             ('NOSILAC PRAVA','S3','')],
  'DFD: Prava i licence, Evidencija autorskih prava; IDEF0: Autorska prava i licence')

# ======================= BAND D - MARKETING I PRODAJA ============================
E('POVRINF', 'POVRATNA INFO.\nGLEDALACA', C(0), BD, 'strong', [
    ('BROJ PRIJAVE','N0','pk'),    ('DATUM PRIJEMA','N3',''),
    ('VRSTA PRIJAVE','NW',''),     ('KANAL PRIJEMA','NE',''),
    ('SADRŽAJ PRIJAVE','S0',''),   ('STATUS OBRADE','S1',''),
    ('DATUM ODGOVORA','S2',''),    ('PROFIL GLEDAOCA','S3','')],
  'DFD: Povratne informacije gledalaca, Registar zalbi gledalaca, Zalbe')

E('MERENJE', 'MERENJE\nGLEDANOSTI', C(1), BD, 'strong', [
    ('ŠIFRA MERENJA','N0','pk'), ('DATUM MERENJA','N3',''),
    ('IZVOR MERENJA','NW',''),   ('CILJNA GRUPA','NE',''),
    ('RATING','S0',''),          ('SHARE','S1',''),
    ('BROJ GLEDALACA','S2',''),  ('PROSEČNO GLEDANJE','S3','der')],
  'DFD: Merenja gledanosti, Analize gledanosti, Analiticki pokazatelji')

E('CENOVNIK', 'CENOVNIK\nREKL. TERMINA', C(2), BD, 'strong', [
    ('ŠIFRA CENOVNIKA','N0','pk'), ('VAŽI OD','N3',''),
    ('VAŽI DO','NW',''),           ('ZONA','NE',''),
    ('CENA PO SEKUNDI','S0',''),   ('MINIMALNI PAKET','S3','')],
  'DFD: Cenovnik reklamnih termina, Cene reklamnih termina')

E('RBLOK', 'REKLAMNI\nBLOK', C(3), BD, 'strong', [
    ('ŠIFRA BLOKA','N0','pk'),      ('DATUM','N3',''),
    ('VREME POČETKA','NW',''),      ('TRAJANJE BLOKA','NE',''),
    ('ZAKUPLJENO SEKUNDI','S0',''), ('SLOBODNO SEKUNDI','S1','der'),
    ('ISKORIŠĆENOST','S2','der'),   ('STATUS BLOKA','S3','')],
  'DFD: Reklamni blokovi i cenovnik, Rezervisani reklamni blokovi, Iskoriscenost blokova')

E('EMREK', 'EMITOVANJE\nREKLAME', C(4), BD, 'weak', [
    ('RB U BLOKU','N0','pd'),      ('DATUM EMITOVANJA','N3',''),
    ('VREME EMITOVANJA','NW',''),  ('TRAJANJE SPOTA','NE',''),
    ('NAPLAĆENI IZNOS','S0',''),   ('STATUS NAPLATE','S3','')],
  'DFD: Evidencija emitovanja reklama, Zapis o emitovanoj reklami, Obracun reklama')

E('STUGOV', 'STAVKA\nUGOVORA', C(5), BD, 'weak', [
    ('RB STAVKE','N0','pd'),        ('OPIS STAVKE','N3',''),
    ('KOLIČINA / SEKUNDE','NW',''), ('JEDINIČNA CENA','NE',''),
    ('POPUST','S0',''),             ('VREDNOST STAVKE','S3','der')],
  'DFD: Ugovorena cena i uslovi placanja, Ugovoreni termini')

E('UGOVOR', 'UGOVOR', C(6), BD, 'strong', [
    ('BROJ UGOVORA','N0','pk'),   ('DATUM SKLAPANJA','N3',''),
    ('VAŽI OD','NW',''),          ('VAŽI DO','NE',''),
    ('UKUPNA VREDNOST','S0',''),  ('STATUS UGOVORA','S3','')],
  'DFD: Ugovori sa klijentima, Ugovori oglasivaca, Arhiva potpisanih ugovora, Nacrti ugovora')
E('UGOGL', 'UGOVOR O\nOGLAŠAVANJU', C(6)-2*SUB_DX+2.2, BD-SUB_DY, 'sub',
  [('UGOVORENI TERMINI','SL',''), ('VRSTA REKLAMIRANJA','SR','')], 'DFD: Ugovor o reklamiranju')
E('UGPROD', 'UGOVOR O PRODAJI\nTV SADRŽAJA', C(6)-SUB_DX+2.2, BD-SUB_DY, 'sub',
  [('PRENOS VLASNIŠTVA','SL',''), ('OBIM USTUPLJENIH PRAVA','SR','')],
  'DFD: Ugovor o ustupanju prava za emitovanje TV emisije')
E('UGNAB', 'UGOVOR O\nNABAVCI', C(6)+2.2, BD-SUB_DY, 'sub',
  [('ROK ISPORUKE','SL',''), ('USLOVI PLAĆANJA','SR','')], 'DFD: Ugovori sa dobavljacima')

E('KLIJENT', 'KLIJENT', C(7), BD, 'strong', [
    ('ŠIFRA KLIJENTA','N0','pk'), ('NAZIV KLIJENTA','N3',''),
    ('PIB','NW',''),              ('MATIČNI BROJ','NE',''),
    ('ADRESA','S0','cmp'),        ('KONTAKT OSOBA','S3','mv')],
  'DFD: Klijenti i oglasivaci; eksterni entitet OGLASIVACI')
E('OGLASIV','OGLAŠIVAČ', C(7)-2.6, BD-2*SUB_DY+1.4, 'sub',
  [('BRANŠA','SL',''), ('GODIŠNJI BUDŽET','SR','')], 'DFD: eksterni entitet OGLASIVACI')
E('KUPACS', 'KUPAC\nSADRŽAJA', C(7)+4.6, BD-2*SUB_DY+1.4, 'sub',
  [('TIP MEDIJA','SL',''), ('TERITORIJA EMITOVANJA','SR','')], 'DFD: Prodaja TV sadrzaja')

# ======================= BAND E - NABAVKA =======================================
E('ZAHNAB', 'ZAHTEV ZA\nNABAVKU', C(0), BE, 'strong', [
    ('BROJ ZAHTEVA','N0','pk'),  ('DATUM ZAHTEVA','N3',''),
    ('VRSTA NABAVKE','NW',''),   ('PREDMET ZAHTEVA','NE',''),
    ('OBRAZLOŽENJE','S0',''),    ('STATUS ZAHTEVA','S1',''),
    ('PRIORITET','S2',''),       ('PROCENJENA VREDNOST','S3','')],
  'DFD: Zahtev za nabavku sa specifikacijom, Zahtev za nabavku/servis opreme')

E('PLANNAB', 'PLAN\nNABAVKE', C(1), BE, 'strong', [
    ('ŠIFRA PLANA','N0','pk'),    ('GODINA PLANA','N3',''),
    ('DATUM DONOŠENJA','NW',''),  ('STATUS PLANA','NE',''),
    ('UKUPNA VREDNOST','S0','der'), ('DONOSILAC PLANA','S3','')],
  'DFD: Plan nabavke, Usvojen plan nabavke; IDEF0: Godisnji plan nabavke')

E('STPLAN', 'STAVKA PLANA\nNABAVKE', C(2), BE, 'weak', [
    ('RB STAVKE','N0','pd'),       ('OPIS ARTIKLA','N3',''),
    ('KOLIČINA','NW',''),          ('JEDINICA MERE','NE',''),
    ('PROCENJENA CENA','S0',''),   ('PLANIRANI KVARTAL','S3','')],
  'DFD: Spisak artikala za nabavku, Spisak opreme za nabavku')

E('PONUDA', 'PONUDA\nDOBAVLJAČA', C(3), BE, 'strong', [
    ('BROJ PONUDE','N0','pk'),     ('DATUM PRIJEMA','N3',''),
    ('VAŽI DO','NW',''),           ('UKUPNA CENA','NE',''),
    ('ROK ISPORUKE','S0',''),      ('USLOVI PLAĆANJA','S1',''),
    ('STATUS PONUDE','S3',''),  ('UKUPNO BODOVA','SE','der')],
  'DFD: Ponude dobavljaca, Vrednovane ponude; IDEF0: Uporedni pregled ponuda')

E('KRITER', 'KRITERIJUM\nVREDNOVANJA', C(4), BE, 'strong', [
    ('ŠIFRA KRITERIJUMA','N0','pk'), ('NAZIV KRITERIJUMA','N3',''),
    ('PONDER','NW',''),              ('NAČIN BODOVANJA','NE',''),
    ('OPIS KRITERIJUMA','S0',''),    ('VAŽI OD','S3','')],
  'DFD: Kriterijumi vrednovanja ponuda, Kriterijumi za vrednovanje')

E('ODLUKA', 'ODLUKA O IZBORU\nDOBAVLJAČA', C(5), BE, 'strong', [
    ('BROJ ODLUKE','N0','pk'),        ('DATUM ODLUKE','N3',''),
    ('DONOSILAC ODLUKE','NW',''),     ('UGOVORENA VREDNOST','NE',''),
    ('OBRAZLOŽENJE IZBORA','S0',''),  ('STATUS ODLUKE','S3','')],
  'DFD: Odluke o izboru dobavljaca, Obrazlozenje izbora dobavljaca')

E('DOBAVLJ', 'DOBAVLJAČ', C(6), BE, 'strong', [
    ('ŠIFRA DOBAVLJAČA','N0','pk'), ('NAZIV DOBAVLJAČA','N3',''),
    ('PIB','NW',''),                ('MATIČNI BROJ','NE',''),
    ('ADRESA','S0',''),             ('OCENA DOBAVLJAČA','S3','der')],
  'DFD: Dobavljaci, Registar dobavljaca; eksterni entitet DOBAVLJACI')
E('DOBSAD','DOBAVLJAČ\nTV SADRŽAJA', C(6)-3.6, BE-SUB_DY, 'sub',
  [('VRSTA SADRŽAJA','SL',''), ('KATALOG PONUDE','SR','')], 'DFD: Nabavka TV sadrzaja')
E('DOBOPR','DOBAVLJAČ OPREME\nI MATERIJALA', C(6)+3.6, BE-SUB_DY, 'sub',
  [('ASORTIMAN','SL',''), ('OVLAŠĆENI SERVIS','SR','')], 'DFD: Spisak opreme za nabavku')

E('NARUDZB', 'NARUDŽBENICA', C(7), BE, 'strong', [
    ('BROJ NARUDŽBENICE','N0','pk'), ('DATUM IZDAVANJA','N3',''),
    ('ROK ISPORUKE','NW',''),        ('MESTO ISPORUKE','NE',''),
    ('UKUPAN IZNOS','S0','der'),     ('STATUS NARUDŽBINE','S3','')],
  'DFD: Narudzbenice, Izdata narudzbenica, Podaci sa narudzbenice')

# ======================= BAND F - FINANSIJSKA DOKUMENTACIJA =====================
E('NALOG', 'NALOG ZA\nPLAĆANJE', C(2), BF, 'strong', [
    ('BROJ NALOGA','N0','pk'),      ('DATUM NALOGA','N3',''),
    ('IZNOS NALOGA','NW',''),       ('SVRHA PLAĆANJA','NE',''),
    ('DATUM REALIZACIJE','S0',''),  ('STATUS NALOGA','S1',''),
    ('RAČUN PRIMAOCA','S2',''),     ('ODOBRIO','S3','')],
  'DFD: Evidencija naloga za placanje, Evidencija realizovanih placanja')

E('STFAKT', 'STAVKA\nFAKTURE', C(4), BF, 'weak', [
    ('RB STAVKE','N0','pd'),      ('OPIS STAVKE','N3',''),
    ('KOLIČINA','NW',''),         ('JEDINIČNA CENA','NE',''),
    ('STOPA PDV','S0',''),        ('VREDNOST STAVKE','S3','der')],
  'DFD: Fakture, Evidentirana faktura')

E('FAKTURA', 'FAKTURA', C(3), BF, 'strong', [
    ('BROJ FAKTURE','N0','pk'),    ('DATUM IZDAVANJA','N3',''),
    ('ROK PLAĆANJA','NW',''),      ('SMER (ULAZNA/IZLAZNA)','NE',''),
    ('OSNOVICA','S0',''),          ('IZNOS PDV','S1',''),
    ('STATUS PLAĆANJA','S3',''), ('IZNOS ZA PLAĆANJE','SE','der')],
  'DFD: Fakture, Fakture i placanja, Kontrolisana faktura za placanje, Profaktura')

E('REKLAMAC', 'REKLAMACIJA', C(5), BF, 'strong', [
    ('BROJ REKLAMACIJE','N0','pk'),  ('DATUM REKLAMACIJE','N3',''),
    ('RAZLOG REKLAMACIJE','NW',''),  ('OPIS NEDOSTATKA','NE',''),
    ('STATUS REKLAMACIJE','S0',''),  ('DATUM REŠENJA','S1',''),
    ('REKLAMIRANI IZNOS','S3',''),   ('NAČIN REŠAVANJA','SE','')],
  'DFD: Evidencija reklamacija, Evidentirana reklamacija, Odgovor na reklamaciju')

E('PRIJEMN', 'PRIJEMNICA', C(6), BF, 'strong', [
    ('BROJ PRIJEMNICE','N0','pk'),   ('DATUM PRIJEMA','N3',''),
    ('BROJ OTPREMNICE','NW',''),     ('PRIMIO (MAGACIONER)','NE',''),
    ('ISPRAVNOST ISPORUKE','S0',''), ('NAPOMENA','S3','')],
  'DFD: Prijemnice, Zapis o prijemu robe, Otpremnica')

E('STNARUD', 'STAVKA\nNARUDŽBENICE', C(7), BF, 'weak', [
    ('RB STAVKE','N0','pd'),          ('NAZIV ARTIKLA','N3',''),
    ('KOLIČINA','NW',''),             ('JEDINIČNA CENA','NE',''),
    ('STATUS STAVKE','S0',''),       ('VREDNOST STAVKE','S3','der')],
  'DFD: Podaci sa narudzbenice, Spisak artikala za nabavku')


# ---- kompozitni atributi: (entitet, roditeljski atribut, [(naziv, dx, dy), ...]) ----
COMPOSITE = [
    ('KLIJENT', 'ADRESA', [('ULICA I BROJ', -2.10, -1.50),
                           ('GRAD',          0.00, -1.50),
                           ('POŠTANSKI BROJ', 2.10, -1.50)]),
]
