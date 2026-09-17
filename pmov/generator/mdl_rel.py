# -*- coding: utf-8 -*-
"""Veze (odnosi) i specijalizacije PMOV-a."""
from geom import *
from mdl_ent import ENT, C, BA, BB, BC, BD, BE, BF

REL, SPEC = [], []
def R(name, e1, c1, e2, c2, x, y, p1=('R',0), p2=('L',0), w1=(), w2=(),
      ident=False, attrs=(), w=DW, h=DH, src='', ad='N'):
    REL.append(dict(name=name, e1=e1, c1=c1, e2=e2, c2=c2, x=x, y=y, p1=p1, p2=p2,
                    w1=list(w1), w2=list(w2), ident=ident, attrs=list(attrs),
                    w=w, h=h, src=src, ad=ad))
def SP(sup, subs, dy=2.95, src='', total=True, disj=True):
    SPEC.append(dict(sup=sup, subs=list(subs), dy=dy, src=src, total=total, disj=disj))

# ---------------- BAND A : organizacija, kadrovi, oprema ------------------------
R('PODREĐENA', 'ORGJED', '(0, N)', 'ORGJED', '(0, 1)', 2.9, 91.2,
  ('B',-0.8), ('B',0.8), w1=[(7.2,91.2)], w2=[(8.8,92.0),(2.9,92.0)], w=2.5,
  src='IDEF0: Hijerarhijska struktura TV stanice')
R('RADI U', 'ZAPOSLENI', '(1, 1)', 'ORGJED', '(0, N)', 14.0, BA, ('L',0), ('R',0), w=2.4,
  src='IDEF0: Pravilnik o organizaciji i sistematizaciji')
R('ZADUŽENA', 'ZAPOSLENI', '(0, N)', 'OPREMA', '(0, N)', 32.0, 100.4,
  ('T',0), ('T',0), w1=[(20.0,100.4)], w2=[(44.0,100.4)], w=2.6,
  attrs=['DATUM ZADUŽENJA','DATUM RAZDUŽENJA','STANJE PRI VRAĆANJU'],
  src='DFD: Zaduzenje i razduzenje, Zaduzena oprema i osobe, Razduzenje opreme')

# ---------------- A -> B : angazovanje resursa na produkciji --------------------
R('ANGAŽUJE', 'ZAPOSLENI', '(0, N)', 'AKTIVNOST', '(0, N)', 32.0, 83.7,
  ('R',0), ('T',0), w1=[(32.0,BA)], w2=[(20.0,83.7)], w=2.6,
  attrs=['ULOGA NA SNIMANJU','DATUM OD','DATUM DO','BROJ ANGAŽOVANIH SATI'],
  src='DFD: Angazovanja ljudi i opreme, Evidencija angazovanja resursa, Raspored angazovanja ljudi')
R('ZADUŽUJE', 'OPREMA', '(0, N)', 'AKTIVNOST', '(0, N)', 37.0, 86.6,
  ('L',0), ('T',-0.8), w1=[(37.0,BA)], w2=[(19.2,86.6)], w=2.6,
  attrs=['DATUM REZERVACIJE','TRAJANJE ZADUŽENJA'],
  src='DFD: Rezervacija opreme za snimanje, Spisak opreme za produkciju')
R('ODOBRAVA', 'UREDNIK', '(0, N)', 'PROJEKAT', '(1, 1)', 2.9, 83.7,
  ('L',0), ('T',0), w1=[(2.9, BA-SUB_DY)], w2=[(8.0,83.7)], w=2.6,
  src='IDEF0: Urednicke odluke i odobrenja; DFD: Odobrenje za proizvodnju sadrzaja')

# ---------------- BAND B : produkcija ------------------------------------------
R('SASTOJI SE OD', 'PROJEKAT', '(1, N)', 'AKTIVNOST', '(1, 1)', 14.0, BB, ident=True, w=3.0,
  src='IDEF0: DEFINISANJE AKTIVNOSTI PROJEKTA')
R('IZAZIVA', 'AKTIVNOST', '(0, N)', 'TROSAK', '(1, 1)', 26.0, BB, ident=True, w=2.4,
  src='IDEF0: EVIDENCIJA TROSKOVA PRODUKCIJE; DFD: Trosak po aktivnosti')
R('SNIMLJEN NA', 'SNIMAK', '(1, 1)', 'AKTIVNOST', '(0, N)', 32.0, 73.0,
  ('B',0), ('B',1.0), w1=[(44.0,73.0)], w2=[(21.0,73.0)], w=2.8,
  src='IDEF0: SNIMANJE I EVIDENCIJA REALIZACIJE; DFD: Evidencija realizacije snimanja')

# ---------------- B -> C : rezultat produkcije ----------------------------------
R('PROIZVODI', 'PROJEKAT', '(0, 1)', 'EMISIJA', '(0, N)', 56.0, 70.2,
  ('B',-1.0), ('T',0), w1=[(7.0,70.2)], w2=[(56.0,70.2)], w=2.6,
  src='DFD: Otvoren projekat produkcije, Producirana emisija')
R('MONTIRAN U', 'SNIMAK', '(0, N)', 'MSADRZAJ', '(0, N)', 61.5, 67.2,
  ('R',0), ('T',-1.0), w1=[(61.5,BB)], w2=[(67.0,67.2)], w=2.8,
  src='DFD: Montaza i obrada materijala, Montazna lista, Montiran video materijal')
R('UGRAĐEN U', 'GRAFEL', '(0, N)', 'MSADRZAJ', '(0, N)', 74.0, 68.9,
  ('R',0), ('T',1.0), w1=[(74.0,BB)], w2=[(69.0,68.9)], w=2.8,
  attrs=['VREME POJAVLJIVANJA','NAČIN KORIŠĆENJA'],
  src='IDEF0: GRAFICKA OBRADA I OZVUCENJE; DFD: Materijal sa grafikom i tonom')

# ---------------- BAND C : emitovanje ------------------------------------------
R('SADRŽI CELINE', 'PSEMA', '(1, N)', 'PCELINA', '(1, 1)', 14.0, BC, ident=True, w=2.6,
  src='DFD: Definisanje programskih celina, Zapis programskih celina')
R('OBUHVATA', 'PCELINA', '(1, N)', 'TERMIN', '(1, 1)', 26.0, BC, w=2.7,
  src='IDEF0: RASPOREDJIVANJE TERMINA EMITOVANJA')
R('REALIZOVAN', 'TERMIN', '(0, 1)', 'ZAPISEM', '(1, 1)', 38.0, BC, ident=True, w=3.0,
  src='DFD: Evidencija emitovanja, Izvestaj o emitovanom programu')
R('PLANIRANA', 'TERMIN', '(1, 1)', 'EMISIJA', '(0, N)', 50.0, 58.4,
  ('B',0.9), ('B',-1.0), w1=[(32.9,58.4)], w2=[(55.0,58.4)], w=2.7,
  src='DFD: Spisak TV programa za emitovanje, Raspored emisija, Detaljan TV program')
R('ČINI', 'EMISIJA', '(1, N)', 'MSADRZAJ', '(0, N)', 62.0, BC, w=2.0,
  attrs=['REDNI BROJ U EMISIJI'],
  src='DFD: Podaci i snimci programskih sadrzaja, Gotov materijal za emitovanje')
R('POKRIVENO', 'MSADRZAJ', '(0, N)', 'PRAVO', '(1, N)', 74.0, BC, w=2.8,
  src='IDEF0: PROVERA PRAVA I PODOBNOSTI SADRZAJA; DFD: Provera prava za termin')
R('EMITUJE', 'ZAPISEM', '(1, 1)', 'MSADRZAJ', '(0, N)', 54.0, 71.6,
  ('T',0.9), ('T',0), w1=[(44.9,71.6)], w2=[(68.0,74.6),(54.0,74.6)], w=2.5,
  src='DFD: Zapis o emitovanom sadrzaju, Arhivirani sadrzaj za emitovanje')

# ---------------- C -> D : marketing, gledanost, reklame ------------------------
R('MERENA', 'MERENJE', '(1, N)', 'EMISIJA', '(0, N)', 38.0, 50.4,
  ('T',0), ('B',0), w1=[(20.0,50.4)], w2=[(56.0,50.4)], w=2.5,
  attrs=['OSTVARENI RATING','UDEO U TERMINU'], ad='S',
  src='IDEF0: ANALIZA GLEDANOSTI EMISIJA I REKLAMA; DFD: Izvestaj o gledanosti TV emisija')
R('ODNOSI SE NA', 'POVRINF', '(0, 1)', 'EMISIJA', '(0, N)', 14.0, 52.6,
  ('T',0), ('B',1.0), w1=[(8.0,52.6)], w2=[(57.0,52.0),(14.0,52.0)], w=3.0,
  src='DFD: Pregled zalbi po emisijama, Povratne informacije o emisijama')
R('ZAKUPLJEN U', 'RBLOK', '(1, 1)', 'TERMIN', '(0, N)', 38.0, 57.0,
  ('T',0), ('B',0), w1=[(44.0,57.0)], w2=[(32.0,57.0)], w=2.8,
  src='DFD: Programska sema sa reklamnim blokovima, Podaci o raspolozivim terminima')
R('PRIKAZUJE', 'EMREK', '(1, 1)', 'MSREK', '(0, N)', 68.0, 50.4,
  ('T',0), ('B',0), w1=[(56.0,50.4)], w2=[(75.2,50.4)], w=2.6,
  src='DFD: Preuzimanje i priprema reklamnog materijala, Spreman reklamni materijal')

# ---------------- BAND D : marketing i prodaja ---------------------------------
R('TARIFIRAN', 'CENOVNIK', '(1, N)', 'RBLOK', '(1, 1)', 38.0, BD, w=2.6,
  src='DFD: Planiranje reklamnog prostora i cenovnika, Definisani blokovi i cene')
R('SADRŽI SPOT', 'RBLOK', '(1, N)', 'EMREK', '(1, 1)', 50.0, BD, ident=True, w=2.9,
  src='DFD: Rezervisani reklamni blokovi, Plan emitovanja reklama')
R('UGOVOREN', 'EMREK', '(1, 1)', 'STUGOV', '(0, N)', 62.0, BD, w=2.7,
  src='DFD: Ugovoreni termini, Evidencija emitovanja reklama i naplata')
R('PRECIZIRA', 'UGOVOR', '(1, N)', 'STUGOV', '(1, 1)', 74.0, BD, ('L',0), ('R',0), ident=True, w=2.7,
  src='DFD: Ugovorena cena i uslovi placanja')
R('SKLAPA', 'KLIJENT', '(0, N)', 'UGOVOR', '(0, 1)', 86.0, BD, ('L',0), ('R',0), w=2.4,
  src='DFD: Izrada i zakljucivanje ugovora, Zakljucen ugovor sa klijentom')
R('USTUPA', 'UGPROD', '(1, N)', 'MSPROD', '(0, N)', 60.8, 48.4,
  ('L',0), ('B',0), w1=[(69.6,38.4),(69.6,48.4)], w2=[(60.8,48.4)], w=2.4,
  attrs=['UGOVORENA CENA','OBIM USTUPANJA'],
  src='DFD: Prodaja TV sadrzaja, Ponuda TV emisije, Prodat TV sadrzaj')
R('DOSTAVLJA', 'OGLASIV', '(1, N)', 'MSREK', '(1, 1)', 82.0, 51.8,
  ('R',0), ('B',0), w1=[(93.5,33.2),(93.5,51.8)], w2=[(75.2,51.8)], w=2.8,
  src='DFD: Reklamni materijal oglasivaca, Preuzeta reklama')

# ---------------- D -> E : nabavka sadrzaja i ugovaranje ------------------------
R('UGOVARA', 'DOBAVLJ', '(0, N)', 'UGNAB', '(1, 1)', 86.0, 32.6,
  ('T',0.8), ('B',0), w1=[(80.8,30.9),(86.0,30.9)], w2=[(82.2,32.6)], w=2.5,
  src='DFD: Ugovori sa dobavljacima, Potpisan ugovor za nabavku')
R('NABAVLJEN PO', 'MSNAB', '(1, 1)', 'UGNAB', '(1, N)', 78.0, 48.4,
  ('B',0), ('L',0), w1=[(68.0,51.4),(78.0,51.4)], w2=[(78.0,38.4)], w=3.0,
  attrs=['DATUM PREUZIMANJA','UGOVORENA NAKNADA'],
  src='IDEF0: IZBOR IZVORA SADRZAJA I UGOVARANJE PRAVA, PREUZIMANJE SADRZAJA I UPIS U KATALOG')

# ---------------- BAND E : nabavka ---------------------------------------------
R('UVRŠTEN U', 'ZAHNAB', '(0, 1)', 'PLANNAB', '(0, N)', 14.0, BE, w=2.7,
  src='IDEF0: Planiranje i iniciranje nabavke; DFD: Plan nabavke')
R('SADRŽI STAVKE PLANA', 'PLANNAB', '(1, N)', 'STPLAN', '(1, 1)', 26.0, BE, ident=True, w=2.6,
  src='DFD: Spisak artikala za nabavku, Spisak opreme za nabavku')
R('PONUĐENA', 'STPLAN', '(0, N)', 'PONUDA', '(0, N)', 38.0, BE, w=2.6,
  attrs=['PONUĐENA CENA','ROK ZA STAVKU'],
  src='IDEF0: PRIKUPLJANJE I VREDNOVANJE PONUDA')
R('VREDNUJE SE', 'PONUDA', '(1, N)', 'KRITER', '(1, N)', 50.0, BE, w=2.9,
  attrs=['BROJ BODOVA','KOMENTAR OCENE'],
  src='DFD: Kriterijumi vrednovanja ponuda, Vrednovane ponude')
R('BIRA', 'PONUDA', '(0, 1)', 'ODLUKA', '(0, 1)', 56.0, 21.5,
  ('B',1.0), ('B',0), w1=[(45.0,21.5)], w2=[(68.0,21.5)], w=2.2,
  src='IDEF0: IZBOR NAJPOVOLJNIJEG DOBAVLJACA; DFD: Odluka o izboru dobavljaca')
R('DOSTAVIO', 'DOBAVLJ', '(0, N)', 'PONUDA', '(1, 1)', 62.0, 34.6,
  ('T',-0.8), ('T',0), w1=[(79.2,34.6)], w2=[(44.0,34.6)], w=2.5,
  src='DFD: Ponude dobavljaca, Ranije ponude dobavljaca')
R('NARUČENO OD', 'DOBAVLJ', '(0, N)', 'NARUDZB', '(1, 1)', 86.0, BE, w=3.0,
  src='DFD: Narudzbenice, Izdata narudzbenica')

# ---------------- BAND F + E->F : prijem, reklamacije, finansije ---------------
R('SADRŽI STAVKE NARUDŽBINE', 'NARUDZB', '(1, N)', 'STNARUD', '(1, 1)', 92.0, 16.4,
  ('B',0), ('T',0), ident=True, w=2.4,
  src='DFD: Podaci sa narudzbenice')
R('PRAĆENA', 'NARUDZB', '(0, N)', 'PRIJEMN', '(1, 1)', 88.0, 16.4,
  ('B',-1.0), ('T',0), w1=[(91.0,19.8),(88.0,19.8)], w2=[(80.0,16.4)], w=2.5,
  src='DFD: Prijemnice, Zapis o prijemu robe, Obavestenje o dostigloj opremi')
R('PRIMLJENO PO', 'PRIJEMN', '(1, N)', 'STNARUD', '(0, N)', 86.0, BF, w=2.7,
  attrs=['PRIMLJENA KOLIČINA','UTVRĐENO ODSTUPANJE'],
  src='DFD: Zapis o prijemu robe, Otpremnica')
R('REKLAMIRANA', 'PRIJEMN', '(0, N)', 'REKLAMAC', '(1, 1)', 74.0, BF, ('L',0), ('R',0), w=3.0,
  src='DFD: Evidencija reklamacija, Reklamacija, Odgovor na reklamaciju')
R('FAKTURISANA', 'PRIJEMN', '(0, 1)', 'FAKTURA', '(0, N)', 56.0, 5.6,
  ('B',0), ('B',1.0), w1=[(80.0,5.6)], w2=[(45.0,5.6)], w=2.9,
  src='DFD: Obrada faktura i placanja, Kontrolisana faktura za placanje')
R('SADRŽI STAVKE FAKTURE', 'FAKTURA', '(1, N)', 'STFAKT', '(1, 1)', 50.0, BF, ident=True, w=2.6,
  src='DFD: Fakture, Evidentirana faktura')
R('PLAĆENA', 'FAKTURA', '(0, N)', 'NALOG', '(1, 1)', 38.0, BF, ('L',0), ('R',0), w=2.5,
  src='DFD: Evidencija naloga za placanje, Evidencija realizovanih placanja, Potvrde o uplati')
R('NAPLAĆUJE', 'UGOVOR', '(0, N)', 'FAKTURA', '(0, 1)', 26.0, 18.6,
  ('B',-1.0), ('T',0), w1=[(79.0,41.9),(1.3,41.9),(1.3,18.6)], w2=[(44.0,18.6)], w=2.8,
  src='DFD: Faktura za reklamiranje, Izvestaji i fakture oglasivacima, Podaci za fakturisanje oglasivaca')

R('TIČE SE', 'REKLAMAC', '(1, N)', 'STNARUD', '(0, N)', 86.0, 7.6,
  ('B',0.6), ('B',0), w1=[(68.6,7.6)], w2=[(92.0,7.6)], w=2.5,
  src='DFD: Evidencija reklamacija, Reklamacija, Podaci sa narudzbenice')

# ---------------- specijalizacije (PMOV) ---------------------------------------
SP('ZAPOSLENI', ['UREDNIK','NOVINAR','SNIMATELJ','REFERENT'], total=False, disj=True,
   src='IDEF0 mehanizmi: Urednik, Novinari/Reporter, Snimatelji, Referent za nabavku/oglasavanje')
SP('OPREMA', ['OPRSNIM','OPRSTUD'], total=False, disj=True,
   src='IDEF0: Snimateljska oprema, TV studio i kontrolna soba, Hardver i oprema')
SP('MSADRZAJ', ['MSPROD','MSNAB','MSREK'], total=True, disj=True,
   src='DFD: Produciran TV sadrzaj / Spisak nabavljenih TV sadrzaja / Reklamni materijali')
SP('UGOVOR', ['UGOGL','UGPROD','UGNAB'], total=True, disj=True,
   src='DFD: Ugovori oglasivaca / Ugovor o prenosu vlasnistva tv emisije / Ugovori sa dobavljacima')
SP('KLIJENT', ['OGLASIV','KUPACS'], dy=9.0, total=True, disj=False,
   src='DFD: Klijenti i oglasivaci; eksterni entitet OGLASIVACI; Prodaja TV sadrzaja')
SP('DOBAVLJ', ['DOBSAD','DOBOPR'], total=True, disj=False,
   src='DFD: Dobavljaci, Registar dobavljaca; Nabavka TV sadrzaja / Spisak opreme za nabavku')
