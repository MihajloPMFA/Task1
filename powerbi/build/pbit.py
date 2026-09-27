# -*- coding: utf-8 -*-
"""Generise Power BI template (.pbit) sa ugradjenim podacima iz Access baze."""
import json, zlib, base64, re, uuid, zipfile, os, io

M = json.load(open('model_prep.json'))
RELS = json.load(open('relationships.json'))

TABLES = ['EMISIJA','MERENJE_EMISIJE','MERENJE_GLEDANOSTI','TERMIN_EMITOVANJA','POVRATNA_INFO_GLEDALACA',
 'KLIJENT','OGLASIVAC','REKLAMNI_SADRZAJ','EMITOVANJE_REKLAME','REKLAMNI_BLOK',
 'UGOVOR','STAVKA_UGOVORA','FAKTURA','STAVKA_FAKTURE','NALOG_ZA_PLACANJE',
 'ZAPOSLENI','ORGANIZACIONA_JEDINICA','ANGAZOVANJE_NA_AKTIVNOSTI','AKTIVNOST_PRODUKCIJE',
 'PROJEKAT_PRODUKCIJE','TROSAK_PRODUKCIJE',
 'OPREMA','SERVISIRANJE_OPREME','ZADUZENJE_OPREME','NARUDZBENICA','REKLAMACIJA',
 'PONUDA_DOBAVLJACA','DOBAVLJAC','Kalendar','_Mere']

BIDI = {('MERENJE_EMISIJE','MERENJE_GLEDANOSTI'), ('EMITOVANJE_REKLAME','REKLAMNI_BLOK')}

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
TIME_RE = re.compile(r'^\d{2}:\d{2}:\d{2}$')

def col_kind(t, c):
    """Vrati (tom_dataType, m_type, formatString, summarizeBy)."""
    meta = next(x for x in M[t]['columns'] if x['name']==c)
    k = meta['kind']; i = [x['name'] for x in M[t]['columns']].index(c)
    vals = [r[i] for r in M[t]['rows'] if r[i] is not None]
    if k == 'datetime':
        if vals and all(DATE_RE.match(str(v)) for v in vals):
            return 'dateTime', 'type date', 'Long Date', 'none'
        return 'string', 'type text', None, 'none'
    if k in ('int','long','byte','bigint'):
        return 'int64', 'Int64.Type', '0', 'none' if c.endswith('BR') or 'RB_' in c or 'SIFRA' in c else 'sum'
    if k == 'currency':
        return 'double', 'type number', '#,##0.00', 'sum'
    if k in ('double','single','decimal'):
        return 'double', 'type number', '0.00', 'sum'
    if k == 'bool':
        return 'boolean', 'type logical', None, 'none'
    return 'string', 'type text', None, 'none'

def m_expression(t):
    names = [c['name'] for c in M[t]['columns']]
    rows = M[t]['rows']
    payload = json.dumps(rows, ensure_ascii=False, separators=(',',':')).encode('utf-8')
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    b64 = base64.b64encode(co.compress(payload) + co.flush()).decode('ascii')
    collist = ", ".join('"%s"' % n for n in names)
    trans = ", ".join('{"%s", %s}' % (n, col_kind(t,n)[1]) for n in names)
    return [
        "let",
        '    Izvor = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("%s", BinaryEncoding.Base64), Compression.Deflate)), {%s}),' % (b64, collist),
        '    #"Promenjen tip" = Table.TransformColumnTypes(Izvor,{%s}, "en-US")' % trans,
        "in",
        '    #"Promenjen tip"',
    ]

MEASURES = [
 # --- 1 Program i gledanost ---
 ("Prosečan rejting",            "AVERAGE(MERENJE_GLEDANOSTI[RATING])", "0.00"),
 ("Maks rejting",                "MAX(MERENJE_GLEDANOSTI[RATING])", "0.00"),
 ("Prosečan share",              "AVERAGE(MERENJE_GLEDANOSTI[SHARE_UDEO])", "0.00"),
 ("Ukupno gledalaca",            "SUM(MERENJE_GLEDANOSTI[BROJ_GLEDALACA])", "#,##0"),
 ("Prosečan rejting emisije",    "AVERAGE(MERENJE_EMISIJE[OSTVARENI_RATING])", "0.00"),
 ("Broj emitovanja",             "COUNTROWS(TERMIN_EMITOVANJA)", "#,##0"),
 ("Broj prijava gledalaca",      "COUNTROWS(POVRATNA_INFO_GLEDALACA)", "#,##0"),
 # --- 2 Oglasavanje ---
 ("Prihod od reklama",           "SUM(EMITOVANJE_REKLAME[NAPLACENI_IZNOS])", "#,##0"),
 ("Broj emitovanja reklama",     "COUNTROWS(EMITOVANJE_REKLAME)", "#,##0"),
 ("Ukupan budžet oglašivača",    "SUM(OGLASIVAC[GODISNJI_BUDZET])", "#,##0"),
 ("Prosečna iskorišćenost bloka","AVERAGE(REKLAMNI_BLOK[ISKORISCENOST])", "0.00"),
 ("Zakupljeno sekundi",          "SUM(REKLAMNI_BLOK[ZAKUPLJENO_SEKUNDI])", "#,##0"),
 # --- 3 Finansije ---
 ("Vrednost ugovora",            "SUM(UGOVOR[UKUPNA_VREDNOST])", "#,##0"),
 ("Broj ugovora",                "COUNTROWS(UGOVOR)", "#,##0"),
 ("Iznos fakture",               "SUM(FAKTURA[IZNOS_ZA_PLACANJE])", "#,##0"),
 ("Osnovica",                    "SUM(FAKTURA[OSNOVICA])", "#,##0"),
 ("Iznos PDV",                   "SUM(FAKTURA[IZNOS_PDV])", "#,##0"),
 ("Iznos naloga",                "SUM(NALOG_ZA_PLACANJE[IZNOS_NALOGA])", "#,##0"),
 ("Vrednost stavki ugovora",     "SUM(STAVKA_UGOVORA[VREDNOST_STAVKE])", "#,##0"),
 # --- 4 HR i produkcija ---
 ("Broj zaposlenih",             "COUNTROWS(ZAPOSLENI)", "#,##0"),
 ("Masa zarada",                 "SUM(ZAPOSLENI[OSNOVNA_ZARADA])", "#,##0"),
 ("Prosečna zarada",             "AVERAGE(ZAPOSLENI[OSNOVNA_ZARADA])", "#,##0"),
 ("Ukupno angažovanih sati",     "SUM(ANGAZOVANJE_NA_AKTIVNOSTI[BROJ_ANGAZOVANIH_SATI])", "#,##0"),
 ("Trošak produkcije",           "SUM(TROSAK_PRODUKCIJE[IZNOS])", "#,##0"),
 ("Odobren budžet",              "SUM(PROJEKAT_PRODUKCIJE[ODOBREN_BUDZET])", "#,##0"),
 # --- 5 Oprema ---
 ("Nabavna vrednost opreme",     "SUM(OPREMA[NABAVNA_VREDNOST])", "#,##0"),
 ("Broj komada opreme",          "COUNTROWS(OPREMA)", "#,##0"),
 ("Trošak servisa",              "SUM(SERVISIRANJE_OPREME[TROSAK])", "#,##0"),
 ("Broj servisiranja",           "COUNTROWS(SERVISIRANJE_OPREME)", "#,##0"),
 ("Broj reklamacija",            "COUNTROWS(REKLAMACIJA)", "#,##0"),
 ("Reklamirani iznos",           "SUM(REKLAMACIJA[REKLAMIRANI_IZNOS])", "#,##0"),
 ("Vrednost narudžbenica",       "SUM(NARUDZBENICA[UKUPAN_IZNOS])", "#,##0"),
]

def build_model():
    tables=[]
    for t in TABLES:
        names=[c['name'] for c in M[t]['columns']]
        tcols=[]
        for c in M[t]['columns']:
            dt, mt, fmt, summ = col_kind(t, c['name'])
            o={"name":c['name'],"dataType":dt,"sourceColumn":c['name'],
               "lineageTag":str(uuid.uuid4()),"summarizeBy":summ,
               "annotations":[{"name":"SummarizationSetBy","value":"Automatic"}]}
            if fmt and dt in ('int64','double'): o["formatString"]=fmt
            if dt=='dateTime': o["formatString"]="yyyy\\-mm\\-dd"
            if c['name']=='Mesec' and 'MesecBr' in names: o["sortByColumn"]="MesecBr"
            if c['name']=='KLJUC_AKTIVNOSTI': o["isHidden"]=True
            tables.append if False else tcols.append(o)
        tab={"name":t,"lineageTag":str(uuid.uuid4()),"columns":tcols,
             "partitions":[{"name":t,"mode":"import",
                            "source":{"type":"m","expression":m_expression(t)}}],
             "annotations":[{"name":"PBI_ResultType","value":"Table"}]}
        if t=='_Mere':
            tab["isHidden"]=False
            tab["columns"][0]["isHidden"]=True
            tab["measures"]=[{"name":n,"expression":e,"formatString":f,
                              "lineageTag":str(uuid.uuid4())} for n,e,f in MEASURES]
        if t=='Kalendar':
            tab["dataCategory"]="Time"
            for c in tab["columns"]:
                if c["name"]=="Datum": c["isKey"]=True
        tables.append(tab)

    rels=[]
    for r in RELS:
        o={"name":str(uuid.uuid4()),"fromTable":r['fromTable'],"fromColumn":r['fromColumn'],
           "toTable":r['toTable'],"toColumn":r['toColumn']}
        if not r['isActive']: o["isActive"]=False
        if (r['fromTable'],r['toTable']) in BIDI: o["crossFilteringBehavior"]="bothDirections"
        rels.append(o)

    return {"name":"TV_stanica_izvestaji","compatibilityLevel":1550,
        "model":{"culture":"en-US",
            "dataAccessOptions":{"legacyRedirects":True,"returnErrorValuesAsNull":True},
            "defaultPowerBIDataSourceVersion":"powerBI_V3","sourceQueryCulture":"en-US",
            "tables":tables,"relationships":rels,
            "annotations":[{"name":"PBI_QueryOrder","value":json.dumps(TABLES)},
                           {"name":"__PBI_TimeIntelligenceEnabled","value":"0"}]}}

if __name__=='__main__':
    m=build_model()
    json.dump(m, open('DataModelSchema.json','w'), ensure_ascii=False, indent=1)
    sz=len(json.dumps(m,ensure_ascii=False))
    print(f"Model: {len(m['model']['tables'])} tabela, {len(m['model']['relationships'])} veza, "
          f"{len(MEASURES)} mera, schema {sz/1024:.0f} KB")
