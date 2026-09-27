# -*- coding: utf-8 -*-
"""Generise klasicni Report/Layout sa 5 stranica izvestaja."""
import json, uuid

W,H = 1280,720
SLOT = {
 'title':(16,10,950,40), 'kpi':(16,58,950,86),
 'v1':(16,152,470,270), 'v2':(494,152,472,270),
 'v3':(16,430,470,274), 'v4':(494,430,472,274),
 's1':(978,58,286,192), 's2':(978,258,286,192), 'v5':(978,458,286,246),
}
ROLE_SORT = {'lineChart':'Category','clusteredBarChart':'Category','clusteredColumnChart':'Category',
             'pieChart':'Category','donutChart':'Category','tableEx':'Values','pivotTable':'Rows',
             'lineClusteredColumnComboChart':'Category','multiRowCard':'Values','slicer':'Values'}

def _nm(): return uuid.uuid4().hex[:20]

def visual(slot, vtype, fields, title=None, sort=None):
    """fields: list of (role, 'c'|'m', table, item, display)"""
    x,y,w,h = SLOT[slot]
    aliases, order = {}, []
    for _,_,t,_,_ in fields:
        if t not in aliases:
            aliases[t] = 't%d' % len(aliases); order.append(t)
    From = [{"Name":aliases[t],"Entity":t,"Type":0} for t in order]
    Select, proj = [], {}
    for role,kind,t,item,disp in fields:
        ref = "%s.%s" % (t,item)
        node = {"Expression":{"SourceRef":{"Source":aliases[t]}},"Property":item}
        Select.append({("Measure" if kind=='m' else "Column"):node,"Name":ref,"NativeReferenceName":disp})
        e = {"queryRef":ref,"displayName":disp}
        if vtype=='slicer': e["active"]=True
        proj.setdefault(role,[]).append(e)
    pq = {"Version":2,"From":From,"Select":Select}
    if sort:
        role,kind,t,item,_ = fields[sort[0]]
        node = {"Expression":{"SourceRef":{"Source":aliases[t]}},"Property":item}
        pq["OrderBy"] = [{"Direction":sort[1],
                          "Expression":{("Measure" if kind=='m' else "Column"):node}}]
    sv = {"visualType":vtype,"projections":proj,"prototypeQuery":pq,"drillFilterOtherVisuals":True}
    if title:
        sv["vcObjects"] = {"title":[{"properties":{
            "show":{"expr":{"Literal":{"Value":"true"}}},
            "text":{"expr":{"Literal":{"Value":"'%s'" % title.replace("'","''")}}}}}]}
    cfg = {"name":_nm(),
           "layouts":[{"id":0,"position":{"x":x,"y":y,"z":list(SLOT).index(slot),
                                          "width":w,"height":h,"tabOrder":list(SLOT).index(slot)*100}}],
           "singleVisual":sv}
    return {"x":x,"y":y,"z":list(SLOT).index(slot),"width":w,"height":h,
            "config":json.dumps(cfg,ensure_ascii=False),"filters":"[]"}

def textbox(slot, text, size="20pt", color="#1F3864"):
    x,y,w,h = SLOT[slot]
    cfg = {"name":_nm(),
      "layouts":[{"id":0,"position":{"x":x,"y":y,"z":0,"width":w,"height":h,"tabOrder":0}}],
      "singleVisual":{"visualType":"textbox","drillFilterOtherVisuals":True,
        "objects":{"general":[{"properties":{"paragraphs":[
            {"textRuns":[{"value":text,"textStyle":{"fontSize":size,"fontWeight":"bold","color":color}}]}]}}]}}}
    return {"x":x,"y":y,"z":0,"width":w,"height":h,
            "config":json.dumps(cfg,ensure_ascii=False),"filters":"[]"}

def M(role, name, disp=None): return (role,'m','_Mere',name,disp or name)
def C(role, t, c, disp):      return (role,'c',t,c,disp)

PAGES = []

# ============ 1. PROGRAM I GLEDANOST ============
PAGES.append(("Program i gledanost", [
 textbox('title', "1 · Program i gledanost"),
 visual('kpi','multiRowCard',[M('Values','Prosečan rejting'),M('Values','Prosečan share'),
        M('Values','Ukupno gledalaca'),M('Values','Broj emitovanja')]),
 visual('v1','lineChart',[C('Category','Kalendar','GodinaMesec','Mesec'),
        M('Y','Prosečan rejting')], "Kretanje prosečnog rejtinga kroz vreme", (0,1)),
 visual('v2','pieChart',[C('Category','EMISIJA','ZANR','Žanr'),
        M('Y','Ukupno gledalaca')], "Gledanost po žanru"),
 visual('v3','clusteredBarChart',[C('Category','EMISIJA','NAZIV_EMISIJE','Emisija'),
        M('Y','Prosečan rejting emisije')], "Emisije po ostvarenom rejtingu", (1,2)),
 visual('v4','pivotTable',[C('Rows','EMISIJA','NAZIV_EMISIJE','Emisija'),
        C('Columns','Kalendar','Kvartal','Kvartal'),
        M('Values','Prosečan rejting emisije')], "Rejting po emisiji i kvartalu"),
 visual('s1','slicer',[C('Values','EMISIJA','ZANR','Žanr')]),
 visual('s2','slicer',[C('Values','Kalendar','Kvartal','Kvartal')]),
 visual('v5','clusteredColumnChart',[C('Category','POVRATNA_INFO_GLEDALACA','VRSTA_PRIJAVE','Vrsta prijave'),
        M('Y','Broj prijava gledalaca')], "Prijave gledalaca"),
]))

# ============ 2. OGLASAVANJE I PRIHOD OD REKLAMA ============
PAGES.append(("Oglašavanje i prihod od reklama", [
 textbox('title', "2 · Oglašavanje i prihod od reklama"),
 visual('kpi','multiRowCard',[M('Values','Prihod od reklama'),M('Values','Broj emitovanja reklama'),
        M('Values','Ukupan budžet oglašivača'),M('Values','Prosečna iskorišćenost bloka')]),
 visual('v1','clusteredColumnChart',[C('Category','OGLASIVAC','BRANSA','Branša'),
        M('Y','Prihod od reklama')], "Prihod od reklama po branši", (1,2)),
 visual('v2','pieChart',[C('Category','EMITOVANJE_REKLAME','STATUS_NAPLATE','Status naplate'),
        M('Y','Prihod od reklama')], "Struktura prihoda po statusu naplate"),
 visual('v3','clusteredBarChart',[C('Category','KLIJENT','NAZIV_KLIJENTA','Oglašivač'),
        M('Y','Prihod od reklama')], "Najveći oglašivači po prihodu", (1,2)),
 visual('v4','tableEx',[C('Values','EMITOVANJE_REKLAME','DATUM_EMITOVANJA','Datum'),
        C('Values','REKLAMNI_SADRZAJ','SIFRA_SADRZAJA','Šifra spota'),
        C('Values','EMITOVANJE_REKLAME','TRAJANJE_SPOTA','Trajanje (s)'),
        M('Values','Prihod od reklama')], "Detalji emitovanja reklama"),
 visual('s1','slicer',[C('Values','OGLASIVAC','BRANSA','Branša')]),
 visual('s2','slicer',[C('Values','Kalendar','Kvartal','Kvartal')]),
 visual('v5','clusteredColumnChart',[C('Category','EMITOVANJE_REKLAME','SAT_EMITOVANJA','Sat'),
        M('Y','Prihod od reklama')], "Prihod po satu emitovanja"),
]))

# ============ 3. FINANSIJE: UGOVORI I FAKTURE ============
PAGES.append(("Finansije: ugovori i fakture", [
 textbox('title', "3 · Finansije: ugovori, fakture i naplata"),
 visual('kpi','multiRowCard',[M('Values','Vrednost ugovora'),M('Values','Iznos fakture'),
        M('Values','Iznos naloga'),M('Values','Broj ugovora')]),
 visual('v1','lineClusteredColumnComboChart',[C('Category','Kalendar','Kvartal','Kvartal'),
        M('Y','Vrednost ugovora'),M('Y2','Iznos fakture')], "Ugovori i fakture po kvartalu", (0,1)),
 visual('v2','pieChart',[C('Category','FAKTURA','STATUS_PLACANJA','Status plaćanja'),
        M('Y','Iznos fakture')], "Fakture po statusu plaćanja"),
 visual('v3','clusteredBarChart',[C('Category','UGOVOR','NAZIV_KLIJENTA','Klijent'),
        M('Y','Vrednost ugovora')], "Najveći klijenti po vrednosti ugovora", (1,2)),
 visual('v4','tableEx',[C('Values','FAKTURA','BROJ_FAKTURE','Broj fakture'),
        C('Values','FAKTURA','NAZIV_KLIJENTA','Klijent'),
        C('Values','FAKTURA','DATUM_IZDAVANJA','Datum izdavanja'),
        M('Values','Osnovica'),M('Values','Iznos PDV'),M('Values','Iznos fakture')], "Pregled faktura"),
 visual('s1','slicer',[C('Values','Kalendar','Kvartal','Kvartal')]),
 visual('s2','slicer',[C('Values','FAKTURA','STATUS_PLACANJA','Status plaćanja')]),
 visual('v5','clusteredColumnChart',[C('Category','NALOG_ZA_PLACANJE','STATUS_NALOGA','Status naloga'),
        M('Y','Iznos naloga')], "Nalozi za plaćanje"),
]))

# ============ 4. LJUDSKI RESURSI I PRODUKCIJA ============
PAGES.append(("Ljudski resursi i produkcija", [
 textbox('title', "4 · Ljudski resursi i produkcija"),
 visual('kpi','multiRowCard',[M('Values','Broj zaposlenih'),M('Values','Masa zarada'),
        M('Values','Ukupno angažovanih sati'),M('Values','Trošak produkcije')]),
 visual('v1','clusteredBarChart',[C('Category','ZAPOSLENI','PUNO_IME','Zaposleni'),
        M('Y','Ukupno angažovanih sati')], "Angažovanje po zaposlenom", (1,2)),
 visual('v2','pieChart',[C('Category','ANGAZOVANJE_NA_AKTIVNOSTI','ULOGA_NA_SNIMANJU','Uloga'),
        M('Y','Ukupno angažovanih sati')], "Sati po ulozi na snimanju"),
 visual('v3','clusteredColumnChart',[C('Category','ORGANIZACIONA_JEDINICA','NAZIV_JEDINICE','Organizaciona jedinica'),
        M('Y','Broj zaposlenih')], "Zaposleni po organizacionoj jedinici", (1,2)),
 visual('v4','pivotTable',[C('Rows','PROJEKAT_PRODUKCIJE','NAZIV_PROJEKTA','Projekat'),
        C('Columns','TROSAK_PRODUKCIJE','VRSTA_TROSKA','Vrsta troška'),
        M('Values','Trošak produkcije')], "Troškovi po projektu i vrsti troška"),
 visual('s1','slicer',[C('Values','ORGANIZACIONA_JEDINICA','TIP_JEDINICE','Tip jedinice')]),
 visual('s2','slicer',[C('Values','ANGAZOVANJE_NA_AKTIVNOSTI','ULOGA_NA_SNIMANJU','Uloga')]),
 visual('v5','clusteredColumnChart',[C('Category','PROJEKAT_PRODUKCIJE','STATUS_PROJEKTA','Status projekta'),
        M('Y','Odobren budžet')], "Odobren budžet po statusu projekta"),
]))

# ============ 5. OPREMA, SERVISIRANJE I NABAVKA ============
PAGES.append(("Oprema, servisiranje i nabavka", [
 textbox('title', "5 · Oprema, servisiranje i nabavka"),
 visual('kpi','multiRowCard',[M('Values','Nabavna vrednost opreme'),M('Values','Trošak servisa'),
        M('Values','Broj servisiranja'),M('Values','Broj reklamacija')]),
 visual('v1','clusteredBarChart',[C('Category','OPREMA','NAZIV_OPREME','Oprema'),
        M('Y','Broj servisiranja')], "Broj servisiranja po opremi", (1,2)),
 visual('v2','pieChart',[C('Category','OPREMA','STATUS_OPREME','Status opreme'),
        M('Y','Broj komada opreme')], "Struktura opreme po statusu"),
 visual('v3','lineChart',[C('Category','Kalendar','Mesec','Mesec'),
        M('Y','Trošak servisa')], "Trošak servisa po mesecu"),
 visual('v4','tableEx',[C('Values','OPREMA','NAZIV_OPREME','Oprema'),
        C('Values','SERVISIRANJE_OPREME','OPIS_RADOVA','Opis radova'),
        C('Values','SERVISIRANJE_OPREME','SERVISER','Serviser'),
        M('Values','Trošak servisa')], "Evidencija servisiranja"),
 visual('s1','slicer',[C('Values','OPREMA','PROIZVODJAC','Proizvođač')]),
 visual('s2','slicer',[C('Values','Kalendar','Kvartal','Kvartal')]),
 visual('v5','clusteredColumnChart',[C('Category','DOBAVLJAC','NAZIV_DOBAVLJACA','Dobavljač'),
        M('Y','Vrednost narudžbenica')], "Narudžbenice po dobavljaču", (1,2)),
]))

def build_layout():
    sections=[]
    for i,(nm,vcs) in enumerate(PAGES):
        sections.append({"id":i,"name":"Strana%d"%(i+1),"displayName":nm,"ordinal":i,
                         "visualContainers":vcs,"config":"{}","filters":"[]",
                         "width":W,"height":H,"displayOption":1})
    cfg={"version":"5.43","activeSectionIndex":0,"defaultDrillFilterOtherVisuals":True,
         "settings":{"useStylableVisualContainerHeader":True,"exportDataMode":1,
                     "useNewFilterPaneExperience":True,"allowChangeFilterTypes":True}}
    return {"id":0,"resourcePackages":[],"sections":sections,
            "config":json.dumps(cfg,ensure_ascii=False),"layoutOptimization":0,
            "publicCustomVisuals":[],"filters":"[]"}

if __name__=='__main__':
    L=build_layout()
    json.dump(L, open('Layout.json','w'), ensure_ascii=False, indent=1)
    print(f"Stranica: {len(L['sections'])}")
    for s in L['sections']:
        print(f"  {s['displayName']:<36} {len(s['visualContainers'])} vizuala")
