# -*- coding: utf-8 -*-
import json
M=json.load(open('model_prep.json'))
def idx(t,c): return [x['name'] for x in M[t]['columns']].index(c)
def vals(t,c):
    i=idx(t,c); return [r[i] for r in M[t]['rows']]

# (from_table, from_col, to_table, to_col)  -- prioritet opada
PLAN=[
 # --- 1 Program i gledanost ---
 ('MERENJE_EMISIJE','SIFRA_EMISIJE','EMISIJA','SIFRA_EMISIJE'),
 ('MERENJE_EMISIJE','SIFRA_MERENJA','MERENJE_GLEDANOSTI','SIFRA_MERENJA'),
 ('MERENJE_GLEDANOSTI','DATUM_MERENJA','Kalendar','Datum'),
 ('TERMIN_EMITOVANJA','SIFRA_EMISIJE','EMISIJA','SIFRA_EMISIJE'),
 ('POVRATNA_INFO_GLEDALACA','SIFRA_EMISIJE','EMISIJA','SIFRA_EMISIJE'),
 ('TERMIN_EMITOVANJA','DATUM','Kalendar','Datum'),
 # --- 2 Oglasavanje ---
 ('OGLASIVAC','SIFRA_KLIJENTA','KLIJENT','SIFRA_KLIJENTA'),
 ('REKLAMNI_SADRZAJ','SIFRA_OGLASIVACA','OGLASIVAC','SIFRA_KLIJENTA'),
 ('EMITOVANJE_REKLAME','SIFRA_SADRZAJA','REKLAMNI_SADRZAJ','SIFRA_SADRZAJA'),
 ('EMITOVANJE_REKLAME','SIFRA_BLOKA','REKLAMNI_BLOK','SIFRA_BLOKA'),
 ('EMITOVANJE_REKLAME','DATUM_EMITOVANJA','Kalendar','Datum'),
 # --- 3 Finansije ---
 ('UGOVOR','DATUM_SKLAPANJA','Kalendar','Datum'),
 ('STAVKA_UGOVORA','BROJ_UGOVORA','UGOVOR','BROJ_UGOVORA'),
 ('FAKTURA','DATUM_IZDAVANJA','Kalendar','Datum'),
 ('STAVKA_FAKTURE','BROJ_FAKTURE','FAKTURA','BROJ_FAKTURE'),
 ('NALOG_ZA_PLACANJE','BROJ_FAKTURE','FAKTURA','BROJ_FAKTURE'),
 # --- 4 HR i produkcija ---
 ('ZAPOSLENI','SIFRA_JEDINICE','ORGANIZACIONA_JEDINICA','SIFRA_JEDINICE'),
 ('ANGAZOVANJE_NA_AKTIVNOSTI','SIFRA_ZAPOSLENOG','ZAPOSLENI','SIFRA_ZAPOSLENOG'),
 ('ANGAZOVANJE_NA_AKTIVNOSTI','KLJUC_AKTIVNOSTI','AKTIVNOST_PRODUKCIJE','KLJUC_AKTIVNOSTI'),
 ('AKTIVNOST_PRODUKCIJE','SIFRA_PROJEKTA','PROJEKAT_PRODUKCIJE','SIFRA_PROJEKTA'),
 ('TROSAK_PRODUKCIJE','SIFRA_PROJEKTA','PROJEKAT_PRODUKCIJE','SIFRA_PROJEKTA'),
 ('TROSAK_PRODUKCIJE','DATUM_NASTANKA','Kalendar','Datum'),
 # --- 5 Oprema i nabavka ---
 ('SERVISIRANJE_OPREME','INVENTARSKI_BROJ','OPREMA','INVENTARSKI_BROJ'),
 ('ZADUZENJE_OPREME','INVENTARSKI_BROJ','OPREMA','INVENTARSKI_BROJ'),
 ('SERVISIRANJE_OPREME','DATUM_SERVISA','Kalendar','Datum'),
 ('NARUDZBENICA','SIFRA_DOBAVLJACA','DOBAVLJAC','SIFRA_DOBAVLJACA'),
 ('PONUDA_DOBAVLJACA','SIFRA_DOBAVLJACA','DOBAVLJAC','SIFRA_DOBAVLJACA'),
 ('NARUDZBENICA','DATUM_IZDAVANJA','Kalendar','Datum'),
 ('REKLAMACIJA','DATUM_REKLAMACIJE','Kalendar','Datum'),
]

parent={}
def find(x):
    parent.setdefault(x,x)
    while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
    return x
def union(a,b):
    ra,rb=find(a),find(b)
    if ra==rb: return False
    parent[ra]=rb; return True

out=[]
for ft,fc,tt,tc in PLAN:
    tv=[v for v in vals(tt,tc) if v is not None]
    uniq = len(tv)==len(set(tv))
    fv=set(v for v in vals(ft,fc) if v is not None)
    matched = len(fv & set(tv))
    if not uniq:
        dup=[k for k,n in __import__('collections').Counter(tv).items() if n>1][:3]
        print(f"  ODBAČENO (nije jedinstveno) {tt}[{tc}] duplikati={dup}")
        continue
    if matched==0:
        print(f"  ODBAČENO (nema poklapanja) {ft}[{fc}] -> {tt}[{tc}]")
        continue
    active = union(ft,tt)
    out.append({'fromTable':ft,'fromColumn':fc,'toTable':tt,'toColumn':tc,'isActive':active})
    flag = "aktivna " if active else "NEAKTIVNA"
    print(f"  {flag}  {ft}[{fc}] -> {tt}[{tc}]   ({matched}/{len(fv)} kljuceva se poklapa)")

json.dump(out, open('relationships.json','w'), ensure_ascii=False, indent=1)
print(f"\nUkupno veza: {len(out)}  (aktivnih {sum(1 for r in out if r['isActive'])})")
