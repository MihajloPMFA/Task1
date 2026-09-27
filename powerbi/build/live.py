# -*- coding: utf-8 -*-
"""Varijanta .pbit koja se povezuje direktno na .accdb preko parametra putanje."""
import json, copy, uuid, datetime
import pbit as B

MES = '{"Januar","Februar","Mart","April","Maj","Jun","Jul","Avgust","Septembar","Oktobar","Novembar","Decembar"}'
DATE_COLS = {
 'MERENJE_GLEDANOSTI':'DATUM_MERENJA','EMITOVANJE_REKLAME':'DATUM_EMITOVANJA',
 'FAKTURA':'DATUM_IZDAVANJA','UGOVOR':'DATUM_SKLAPANJA','TROSAK_PRODUKCIJE':'DATUM_NASTANKA',
 'SERVISIRANJE_OPREME':'DATUM_SERVISA','REKLAMACIJA':'DATUM_REKLAMACIJE',
 'NARUDZBENICA':'DATUM_IZDAVANJA','ANGAZOVANJE_NA_AKTIVNOSTI':'DATUM_OD','TERMIN_EMITOVANJA':'DATUM',
}
# tabela -> [(nova kolona, izvorna tabela, kljuc_ovde, kljuc_tamo, kolona_tamo)]
JOINS = {
 'UGOVOR':   [('NAZIV_KLIJENTA','KLIJENT','SIFRA_KLIJENTA','SIFRA_KLIJENTA','NAZIV_KLIJENTA')],
 'SERVISIRANJE_OPREME':[('SERVISER','ZAPOSLENI','SIFRA_ZAPOSLENOG','SIFRA_ZAPOSLENOG','PUNO_IME')],
 'ZADUZENJE_OPREME':   [('ZADUZENI','ZAPOSLENI','SIFRA_ZAPOSLENOG','SIFRA_ZAPOSLENOG','PUNO_IME')],
}

def access_steps(t):
    """M koraci za ucitavanje tabele t iz Accessa + izvedene kolone."""
    s = [f'    Izvor = Access.Database(File.Contents(PutanjaDoBaze), [CreateNavigationProperties=false]),',
         f'    Tabela = Izvor{{[Name="{t}"]}}[Data]']
    prev = 'Tabela'
    def step(name, expr):
        nonlocal prev, s
        s[-1] += ','
        s.append(f'    {name} = {expr}')
        prev = name
    if t in DATE_COLS:
        d = DATE_COLS[t]
        step('Datum', f'Table.TransformColumnTypes({prev},{{{{"{d}", type date}}}})')
        step('Godina',  f'Table.AddColumn({prev}, "Godina", each if [{d}]=null then null else Date.Year([{d}]), Int64.Type)')
        step('Kvartal', f'Table.AddColumn({prev}, "Kvartal", each if [{d}]=null then null else "K" & Text.From(Date.QuarterOfYear([{d}])), type text)')
        step('Mesec',   f'Table.AddColumn({prev}, "Mesec", each if [{d}]=null then null else {MES}{{Date.Month([{d}])-1}}, type text)')
        step('MesecBr', f'Table.AddColumn({prev}, "MesecBr", each if [{d}]=null then null else Date.Month([{d}]), Int64.Type)')
    if t == 'EMITOVANJE_REKLAME':
        step('Sat', f'Table.AddColumn({prev}, "SAT_EMITOVANJA", each try Time.Hour(DateTime.Time([VREME_EMITOVANJA])) otherwise null, Int64.Type)')
    if t == 'ZAPOSLENI':
        step('PunoIme', f'Table.AddColumn({prev}, "PUNO_IME", each [IME] & " " & [PREZIME], type text)')
    if t == 'FAKTURA':
        step('SpojUgovor', f'Table.NestedJoin({prev}, {{"BROJ_UGOVORA"}}, UGOVOR, {{"BROJ_UGOVORA"}}, "_u", JoinKind.LeftOuter)')
        step('NazivKlijenta', f'Table.ExpandTableColumn({prev}, "_u", {{"NAZIV_KLIJENTA"}}, {{"NAZIV_KLIJENTA"}})')
    for new, src, k1, k2, c in JOINS.get(t, []):
        step('Spoj_'+new, f'Table.NestedJoin({prev}, {{"{k1}"}}, {src}, {{"{k2}"}}, "_j", JoinKind.LeftOuter)')
        step('Kol_'+new,  f'Table.ExpandTableColumn({prev}, "_j", {{"{c}"}}, {{"{new}"}})')
    if 'KLJUC_AKTIVNOSTI' in {c['name'] for c in B.M[t]['columns']}:
        step('Kljuc', f'Table.AddColumn({prev}, "KLJUC_AKTIVNOSTI", each Text.From([SIFRA_PROJEKTA]) & "-" & Text.From([RB_AKTIVNOSTI]), type text)')
    return ['let'] + s + ['in', f'    {prev}']

def kalendar_m():
    dates=[r[0] for r in B.M['Kalendar']['rows']]
    a,b = dates[0], dates[-1]
    ay,am,ad = a.split('-'); by,bm,bd = b.split('-')
    return ['let',
      f'    Pocetak = #date({int(ay)},{int(am)},{int(ad)}),',
      f'    Kraj = #date({int(by)},{int(bm)},{int(bd)}),',
      '    Dani = List.Dates(Pocetak, Duration.Days(Kraj - Pocetak) + 1, #duration(1,0,0,0)),',
      '    Tab = Table.TransformColumnTypes(Table.FromList(Dani, Splitter.SplitByNothing(), {"Datum"}),{{"Datum", type date}}),',
      '    G = Table.AddColumn(Tab, "Godina", each Date.Year([Datum]), Int64.Type),',
      '    K = Table.AddColumn(G, "Kvartal", each "K" & Text.From(Date.QuarterOfYear([Datum])), type text),',
      f'    M1 = Table.AddColumn(K, "Mesec", each {MES}{{Date.Month([Datum])-1}}, type text),',
      '    MB = Table.AddColumn(M1, "MesecBr", each Date.Month([Datum]), Int64.Type),',
      '    GM = Table.AddColumn(MB, "GodinaMesec", each Date.ToText([Datum], "yyyy-MM"), type text)',
      'in', '    GM']

def build():
    s = copy.deepcopy(B.build_model())
    s['model']['expressions'] = [{
      "name":"PutanjaDoBaze","kind":"m",
      "expression":['"C:\\\\Baze\\\\Access_v3.accdb" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'],
      "annotations":[{"name":"PBI_ResultType","value":"Text"}]}]
    for t in s['model']['tables']:
        n=t['name']
        if n=='_Mere': continue
        t['partitions'][0]['source']['expression'] = kalendar_m() if n=='Kalendar' else access_steps(n)
    return s

if __name__=='__main__':
    import pack
    sch=build()
    json.dump(sch, open('DataModelSchema_live.json','w'), ensure_ascii=False, indent=1)
    n=pack.write_pbit('/home/user/Task1/powerbi/TV_stanica_Izvestaji_ACCESS.pbit', sch,
                      "TV stanica - 5 izvestaja (ziva veza ka Access bazi)")
    print(f"Napisano TV_stanica_Izvestaji_ACCESS.pbit  ({n/1024:.0f} KB)")
    print("\nPrimer M koda (SERVISIRANJE_OPREME):")
    for L in access_steps('SERVISIRANJE_OPREME'): print("   ",L)
