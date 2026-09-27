# -*- coding: utf-8 -*-
"""Priprema podataka iz Access modela: izvedene kolone, denormalizacija, Kalendar."""
import json, datetime, collections

M = json.load(open('/tmp/model.json'))

def cols(t):  return [c['name'] for c in M[t]['columns']]
def kind(t,c):
    for x in M[t]['columns']:
        if x['name']==c: return x['kind']
    raise KeyError((t,c))
def cap(t,c):
    for x in M[t]['columns']:
        if x['name']==c: return x['caption'] or c.replace('_',' ').capitalize()
    return c
def idx(t,c): return cols(t).index(c)
def col_values(t,c):
    i=idx(t,c); return [r[i] for r in M[t]['rows']]
def lookup(t, keycol, valcol):
    i,j = idx(t,keycol), idx(t,valcol)
    return {r[i]: r[j] for r in M[t]['rows']}

def add_col(t, name, kindname, caption, values):
    M[t]['columns'].append({'name':name,'jet':0,'kind':kindname,'caption':caption})
    for r,v in zip(M[t]['rows'], values): r.append(v)

MES = ["Januar","Februar","Mart","April","Maj","Jun","Jul","Avgust","Septembar","Oktobar","Novembar","Decembar"]

# ---------- izvedene kolone iz datuma ----------
DATE_COLS = {
    'MERENJE_GLEDANOSTI':'DATUM_MERENJA',
    'EMITOVANJE_REKLAME':'DATUM_EMITOVANJA',
    'FAKTURA':'DATUM_IZDAVANJA',
    'UGOVOR':'DATUM_SKLAPANJA',
    'TROSAK_PRODUKCIJE':'DATUM_NASTANKA',
    'SERVISIRANJE_OPREME':'DATUM_SERVISA',
    'REKLAMACIJA':'DATUM_REKLAMACIJE',
    'NARUDZBENICA':'DATUM_IZDAVANJA',
    'ANGAZOVANJE_NA_AKTIVNOSTI':'DATUM_OD',
    'TERMIN_EMITOVANJA':'DATUM',
}
all_dates=[]
for t,c in DATE_COLS.items():
    vals=col_values(t,c)
    ys,qs,ms,mb=[],[],[],[]
    for v in vals:
        if v:
            d=datetime.date.fromisoformat(v); all_dates.append(d)
            ys.append(d.year); qs.append("K%d"%((d.month-1)//3+1)); ms.append(MES[d.month-1]); mb.append(d.month)
        else:
            ys.append(None); qs.append(None); ms.append(None); mb.append(None)
    add_col(t,'Godina','int','Godina',ys)
    add_col(t,'Kvartal','text','Kvartal',qs)
    add_col(t,'Mesec','text','Mesec',ms)
    add_col(t,'MesecBr','int','Mesec (br)',mb)

# ---------- sat emitovanja reklame ----------
v=col_values('EMITOVANJE_REKLAME','VREME_EMITOVANJA')
add_col('EMITOVANJE_REKLAME','SAT_EMITOVANJA','int','Sat emitovanja',
        [int(x.split(':')[0]) if x else None for x in v])

# ---------- puno ime zaposlenog ----------
im=col_values('ZAPOSLENI','IME'); pr=col_values('ZAPOSLENI','PREZIME')
add_col('ZAPOSLENI','PUNO_IME','text','Zaposleni',[f"{a} {b}" for a,b in zip(im,pr)])
zap_ime = dict(zip(col_values('ZAPOSLENI','SIFRA_ZAPOSLENOG'), col_values('ZAPOSLENI','PUNO_IME')))

# ---------- denormalizacije ----------
kl_naziv = lookup('KLIJENT','SIFRA_KLIJENTA','NAZIV_KLIJENTA')
ug_klijent = dict(zip(col_values('UGOVOR','BROJ_UGOVORA'), col_values('UGOVOR','SIFRA_KLIJENTA')))
add_col('UGOVOR','NAZIV_KLIJENTA','text','Klijent',
        [kl_naziv.get(k) for k in col_values('UGOVOR','SIFRA_KLIJENTA')])
add_col('FAKTURA','NAZIV_KLIJENTA','text','Klijent',
        [kl_naziv.get(ug_klijent.get(b)) for b in col_values('FAKTURA','BROJ_UGOVORA')])
add_col('SERVISIRANJE_OPREME','SERVISER','text','Serviser',
        [zap_ime.get(s) for s in col_values('SERVISIRANJE_OPREME','SIFRA_ZAPOSLENOG')])
add_col('ZADUZENJE_OPREME','ZADUZENI','text','Zaduženi zaposleni',
        [zap_ime.get(s) for s in col_values('ZADUZENJE_OPREME','SIFRA_ZAPOSLENOG')])

# surogat kljuc aktivnosti (kompozitni PK -> jedna kolona)
for t in ('AKTIVNOST_PRODUKCIJE','ANGAZOVANJE_NA_AKTIVNOSTI','REZERVACIJA_OPREME','SIROVI_SNIMAK','TROSAK_PRODUKCIJE'):
    if t in M and 'RB_AKTIVNOSTI' in cols(t) and 'SIFRA_PROJEKTA' in cols(t):
        p=col_values(t,'SIFRA_PROJEKTA'); r=col_values(t,'RB_AKTIVNOSTI')
        add_col(t,'KLJUC_AKTIVNOSTI','text','Ključ aktivnosti',
                [f"{a}-{b}" if a is not None and b is not None else None for a,b in zip(p,r)])

# ---------- Kalendar ----------
dmin, dmax = min(all_dates), max(all_dates)
start = datetime.date(dmin.year,1,1); end = datetime.date(dmax.year,12,31)
rows=[]; d=start
while d<=end:
    rows.append([d.isoformat(), d.year, "K%d"%((d.month-1)//3+1), MES[d.month-1], d.month, d.strftime("%Y-%m")])
    d+=datetime.timedelta(days=1)
M['Kalendar']={'columns':[
    {'name':'Datum','jet':8,'kind':'datetime','caption':'Datum'},
    {'name':'Godina','jet':4,'kind':'int','caption':'Godina'},
    {'name':'Kvartal','jet':10,'kind':'text','caption':'Kvartal'},
    {'name':'Mesec','jet':10,'kind':'text','caption':'Mesec'},
    {'name':'MesecBr','jet':4,'kind':'int','caption':'Mesec (br)'},
    {'name':'GodinaMesec','jet':10,'kind':'text','caption':'Godina-mesec'},
],'rows':rows}

# ---------- _Mere ----------
M['_Mere']={'columns':[{'name':'Mera','jet':4,'kind':'int','caption':'Mera'}],'rows':[[1]]}

json.dump(M, open('/home/user/Task1/powerbi/build/model_prep.json','w'), ensure_ascii=False)
print(f"Kalendar: {start} .. {end} ({len(rows)} dana)")
print("Pripremljeno tabela:", len(M))
