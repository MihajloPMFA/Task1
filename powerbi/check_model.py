# -*- coding: utf-8 -*-
"""Provera logike modela: CSV izvoz se ucita u SQLite i izracunaju se iste
vrednosti koje Power BI mere treba da daju.  Proverava spojeve i grupisanja,
tj. da li se brojevi poklapaju sa Access izvestajima."""
import csv, os, sqlite3, sys
BASE = os.path.dirname(os.path.abspath(__file__))
CSVD = os.path.join(BASE, 'csv')
from model_def import OSNOVNE

db = sqlite3.connect(':memory:')
db.row_factory = sqlite3.Row
for tab in OSNOVNE:
    with open(os.path.join(CSVD, tab + '.csv'), encoding='utf-8') as f:
        r = csv.reader(f, delimiter=';')
        kol = next(r)
        redovi = list(r)
    db.execute('CREATE TABLE %s (%s)' % (tab, ','.join('"%s"' % c for c in kol)))
    db.executemany('INSERT INTO %s VALUES (%s)' % (tab, ','.join('?' * len(kol))),
                   [[None if v == '' else v for v in x] for x in redovi])
db.commit()

def q(sql):
    return db.execute(sql).fetchall()

def red(sql):
    return q(sql)[0]

print('== broj redova po tabeli modela')
UPITI = {
 'Playout': """SELECT COUNT(*) n FROM ZAPIS_O_EMITOVANJU ZE
   JOIN TERMIN_EMITOVANJA TE ON ZE.SIFRA_TERMINA=TE.SIFRA_TERMINA
   JOIN MEDIJSKI_SADRZAJ MS ON ZE.SIFRA_SADRZAJA=MS.SIFRA_SADRZAJA""",
 'Gledanost': """SELECT COUNT(*) n FROM MERENJE_EMISIJE ME
   JOIN MERENJE_GLEDANOSTI MG ON ME.SIFRA_MERENJA=MG.SIFRA_MERENJA""",
 'Troskovi': """SELECT COUNT(*) n FROM TROSAK_PRODUKCIJE TP
   JOIN AKTIVNOST_PRODUKCIJE AP ON TP.SIFRA_PROJEKTA=AP.SIFRA_PROJEKTA
    AND TP.RB_AKTIVNOSTI=AP.RB_AKTIVNOSTI""",
 'StavkeUgovora': """SELECT COUNT(*) n FROM STAVKA_UGOVORA SU
   JOIN UGOVOR_O_OGLASAVANJU UO ON SU.BROJ_UGOVORA=UO.BROJ_UGOVORA""",
 'EmitovanjaReklama': "SELECT COUNT(*) n FROM EMITOVANJE_REKLAME",
 'StavkePlana': "SELECT COUNT(*) n FROM STAVKA_PLANA_NABAVKE",
 'VrednovanjePonuda': """SELECT COUNT(*) n FROM PONUDJENA_STAVKA PS
   JOIN PONUDA_DOBAVLJACA PD ON PS.BROJ_PONUDE=PD.BROJ_PONUDE
   JOIN DOBAVLJAC D ON PD.SIFRA_DOBAVLJACA=D.SIFRA_DOBAVLJACA
   LEFT JOIN OCENA_PONUDE OP ON PD.BROJ_PONUDE=OP.BROJ_PONUDE""",
 'Ugovori': """SELECT COUNT(*) n FROM UGOVOR U
   JOIN UGOVOR_O_OGLASAVANJU UO ON U.BROJ_UGOVORA=UO.BROJ_UGOVORA
   JOIN KLIJENT K ON U.SIFRA_KLIJENTA=K.SIFRA_KLIJENTA
   JOIN OGLASIVAC OG ON U.SIFRA_KLIJENTA=OG.SIFRA_KLIJENTA""",
 'Projekti': "SELECT COUNT(*) n FROM PROJEKAT_PRODUKCIJE",
 'Planovi': "SELECT COUNT(*) n FROM PLAN_NABAVKE",
 'Emisije': "SELECT COUNT(*) n FROM EMISIJA",
 'Dobavljaci': "SELECT COUNT(*) n FROM DOBAVLJAC",
}
for k in ('Emisije','Projekti','Ugovori','Planovi','Dobavljaci','Playout','Gledanost',
          'Troskovi','StavkeUgovora','EmitovanjaReklama','StavkePlana','VrednovanjePonuda'):
    print('  %-20s %4d' % (k, red(UPITI[k])['n']))

print()
print('== izvestaj 2 (Playout)')
r = red("""SELECT COUNT(*) broj, SUM(ZE.STVARNO_TRAJANJE) stv, SUM(TE.TRAJANJE_TERMINA) plan,
 SUM(ZE.STVARNO_TRAJANJE-TE.TRAJANJE_TERMINA) ods,
 SUM(CASE WHEN ZE.NAPOMENA_O_SMETNJAMA IS NULL OR ZE.NAPOMENA_O_SMETNJAMA='' THEN 0 ELSE 1 END) sm,
 SUM(CASE WHEN ZE.STATUS_REALIZACIJE='Realizovano' THEN 1 ELSE 0 END) realiz
 FROM ZAPIS_O_EMITOVANJU ZE JOIN TERMIN_EMITOVANJA TE ON ZE.SIFRA_TERMINA=TE.SIFRA_TERMINA
 JOIN MEDIJSKI_SADRZAJ MS ON ZE.SIFRA_SADRZAJA=MS.SIFRA_SADRZAJA""")
print('  emitovanja %d | stvarno %s min | planirano %s min | odstupanje %s | sa smetnjama %d | %% realizovanih %.1f%%'
      % (r['broj'], r['stv'], r['plan'], r['ods'], r['sm'], 100.0*r['realiz']/r['broj']))

print()
print('== izvestaj 3 (Gledanost) - prosecan rejting po zanru')
for x in q("""SELECT E.ZANR z, COUNT(*) n, ROUND(AVG(ME.OSTVARENI_RATING),2) r
 FROM EMISIJA E JOIN MERENJE_EMISIJE ME ON E.SIFRA_EMISIJE=ME.SIFRA_EMISIJE
 GROUP BY E.ZANR ORDER BY r DESC"""):
    print('  %-22s merenja %2d  rejting %s' % (x['z'], x['n'], x['r']))

print()
print('== izvestaj 4 (Troskovi) - prva tri projekta')
for x in q("""SELECT PP.SIFRA_PROJEKTA p, PP.ODOBREN_BUDZET b,
 ROUND(SUM(TP.IZNOS),2) t, COUNT(DISTINCT TP.RB_AKTIVNOSTI) a
 FROM PROJEKAT_PRODUKCIJE PP
 JOIN AKTIVNOST_PRODUKCIJE AP ON PP.SIFRA_PROJEKTA=AP.SIFRA_PROJEKTA
 JOIN TROSAK_PRODUKCIJE TP ON TP.SIFRA_PROJEKTA=AP.SIFRA_PROJEKTA
  AND TP.RB_AKTIVNOSTI=AP.RB_AKTIVNOSTI
 GROUP BY PP.SIFRA_PROJEKTA ORDER BY PP.SIFRA_PROJEKTA LIMIT 3"""):
    print('  %s  budzet %10s  troskovi %10s  iskoriscenost %.1f%%  aktivnosti %d'
          % (x['p'], x['b'], x['t'], 100.0*float(x['t'])/float(x['b']), x['a']))

print()
print('== izvestaj 6 (Kartica oglasivaca) - KL-001')
r = red("""SELECT (SELECT SUM(SU.KOLICINA_SEKUNDE) FROM STAVKA_UGOVORA SU
   JOIN UGOVOR U2 ON SU.BROJ_UGOVORA=U2.BROJ_UGOVORA
   JOIN UGOVOR_O_OGLASAVANJU UO2 ON SU.BROJ_UGOVORA=UO2.BROJ_UGOVORA
   WHERE U2.SIFRA_KLIJENTA='KL-001') ug,
 (SELECT ROUND(SUM(SU.VREDNOST_STAVKE),2) FROM STAVKA_UGOVORA SU
   JOIN UGOVOR U2 ON SU.BROJ_UGOVORA=U2.BROJ_UGOVORA
   JOIN UGOVOR_O_OGLASAVANJU UO2 ON SU.BROJ_UGOVORA=UO2.BROJ_UGOVORA
   WHERE U2.SIFRA_KLIJENTA='KL-001') uv,
 (SELECT SUM(ER.TRAJANJE_SPOTA) FROM EMITOVANJE_REKLAME ER
   JOIN UGOVOR U3 ON ER.BROJ_UGOVORA=U3.BROJ_UGOVORA
   WHERE U3.SIFRA_KLIJENTA='KL-001') rs,
 (SELECT ROUND(SUM(ER.NAPLACENI_IZNOS),2) FROM EMITOVANJE_REKLAME ER
   JOIN UGOVOR U4 ON ER.BROJ_UGOVORA=U4.BROJ_UGOVORA
   WHERE U4.SIFRA_KLIJENTA='KL-001') np""")
print('  ugovoreno %s s | ugovorena vrednost %s | realizovano %s s | naplaceno %s'
      % (r['ug'], r['uv'], r['rs'], r['np']))

print()
print('== izvestaj 7 (Plan nabavke) - ukupno')
r = red("""SELECT ROUND(SUM(SP.PROCENJENA_CENA),2) plan,
 ROUND(SUM(COALESCE(N.IZNOS,0)),2) nar, COUNT(*) st FROM STAVKA_PLANA_NABAVKE SP
 LEFT JOIN (SELECT PS.SIFRA_PLANA, PS.RB_STAVKE, MIN(PD.SIFRA_DOBAVLJACA) SD
   FROM PONUDJENA_STAVKA PS JOIN PONUDA_DOBAVLJACA PD ON PS.BROJ_PONUDE=PD.BROJ_PONUDE
   WHERE PD.STATUS_PONUDE='Izabrana' GROUP BY PS.SIFRA_PLANA, PS.RB_STAVKE) IZ
  ON SP.SIFRA_PLANA=IZ.SIFRA_PLANA AND SP.RB_STAVKE=IZ.RB_STAVKE
 LEFT JOIN (SELECT SIFRA_DOBAVLJACA, SUM(UKUPAN_IZNOS) IZNOS FROM NARUDZBENICA
   GROUP BY SIFRA_DOBAVLJACA) N ON IZ.SD=N.SIFRA_DOBAVLJACA""")
print('  stavki %d | planirano %s | naruceno %s | izvrsenje %.1f%%'
      % (r['st'], r['plan'], r['nar'], 100.0*float(r['nar'])/float(r['plan'])))
r = red("SELECT COUNT(DISTINCT BROJ_PONUDE) p, COUNT(*) o FROM OCENA_PONUDE")
print('  ponuda sa ocenama %d, ocena %d' % (r['p'], r['o']))
