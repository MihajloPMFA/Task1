# -*- coding: utf-8 -*-
"""Izvoz tabela iz Access_v1.accdb u CSV (rezervni izvor podataka za Power BI).

Valute su u Jet-u zapisane kao celi brojevi skalirani sa 10000, pa se dele.
Datumi izlaze kao yyyy-MM-dd, vreme kao HH:mm:ss, decimale sa tackom.
"""
import os, sys, csv, datetime
SP = '/tmp/claude-0/-home-user-Task1/b6283403-6c49-54be-ba3f-14272bcdf06f/scratchpad/lib'
sys.path.insert(0, SP)
sys.path.insert(0, '/home/user/Task1/er/generator')
from access_parser import AccessParser
from schema import TABLES

DB = '/root/.claude/uploads/b6283403-6c49-54be-ba3f-14272bcdf06f/ad8c7ee6-Access_v1.accdb'
IZLAZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'csv')

TIP = {}
for t in TABLES:
    for c in t['cols']:
        TIP[(t['name'], c['n'])] = c['t']

POTREBNE = """ZAPIS_O_EMITOVANJU TERMIN_EMITOVANJA EMISIJA MEDIJSKI_SADRZAJ POKRIVENOST_PRAVOM
PRAVO_KORISCENJA MERENJE_EMISIJE MERENJE_GLEDANOSTI PROJEKAT_PRODUKCIJE AKTIVNOST_PRODUKCIJE
TROSAK_PRODUKCIJE FAKTURA ZAPOSLENI KLIJENT OGLASIVAC UGOVOR UGOVOR_O_OGLASAVANJU
STAVKA_UGOVORA EMITOVANJE_REKLAME REKLAMNI_BLOK CENOVNIK_REKL_TERMINA PLAN_NABAVKE
STAVKA_PLANA_NABAVKE ZAHTEV_ZA_NABAVKU PONUDA_DOBAVLJACA PONUDJENA_STAVKA OCENA_PONUDE
KRITERIJUM_VREDNOVANJA DOBAVLJAC NARUDZBENICA""".split()

def vrednost(tab, kol, v):
    if v is None or v == 'None':
        return ''
    t = TIP.get((tab, kol), '')
    if t == 'DATE':
        if isinstance(v, (datetime.datetime, datetime.date)):
            return v.strftime('%Y-%m-%d')
        return str(v)[:10]
    if t == 'TIME':
        if isinstance(v, datetime.datetime):
            return v.strftime('%H:%M:%S')
        return str(v)[-8:]
    if t == 'DECIMAL(12,2)':                 # valuta: Jet cuva x10000
        try:
            return '%.2f' % (float(v) / 10000.0)
        except (TypeError, ValueError):
            return ''
    if t == 'DECIMAL(5,2)':
        try:
            return '%.2f' % float(v)
        except (TypeError, ValueError):
            return ''
    if t == 'INTEGER':
        try:
            return str(int(v))
        except (TypeError, ValueError):
            return ''
    return str(v)

def main():
    db = AccessParser(DB)
    uk = 0
    for tab in POTREBNE:
        t = db.parse_table(tab)
        kol = list(t.keys())
        n = len(t[kol[0]])
        redovi = []
        for i in range(n):
            redovi.append(tuple(vrednost(tab, c, t[c][i]) for c in kol))
        redovi = list(dict.fromkeys(redovi))          # parser ume da ponovi red
        put = os.path.join(IZLAZ, tab + '.csv')
        with open(put, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
            w.writerow(kol)
            w.writerows(redovi)
        uk += len(redovi)
        print('%-30s %3d redova  %2d kolona' % (tab, len(redovi), len(kol)))
    print('ukupno redova:', uk)

if __name__ == '__main__':
    main()
