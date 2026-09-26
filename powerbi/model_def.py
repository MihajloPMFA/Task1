# -*- coding: utf-8 -*-
"""Definicija Power BI semantičkog modela za pet izveštaja iz specifikacije.

Model je "fact constellation": šest činjeničnih tabela (po jedna ili dve za
svaki izveštaj) i šest dimenzija (Kalendar, Emisije, Projekti, Ugovori,
Planovi, Dobavljaci).  Svi spojevi koje Access radi u upitu odrađeni su u
Power Query-ju, pa se brojevi poklapaju sa Access izveštajima.

Izvor podataka bira se parametrom Izvor: "Access" (čita .accdb direktno) ili
"CSV" (čita izvezene CSV fajlove iz podfoldera csv).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'er', 'generator'))
from schema import TABLES

# ---------------------------------------------------------------- tipovi za M
M_TIP = {'INTEGER': 'Int64.Type', 'DECIMAL(12,2)': 'Currency.Type',
         'DECIMAL(5,2)': 'type number', 'DATE': 'type date', 'TIME': 'type time'}

def m_tip(t):
    return M_TIP.get(t, 'type text')

OSNOVNE = """ZAPIS_O_EMITOVANJU TERMIN_EMITOVANJA EMISIJA MEDIJSKI_SADRZAJ POKRIVENOST_PRAVOM
PRAVO_KORISCENJA MERENJE_EMISIJE MERENJE_GLEDANOSTI PROJEKAT_PRODUKCIJE AKTIVNOST_PRODUKCIJE
TROSAK_PRODUKCIJE FAKTURA ZAPOSLENI KLIJENT OGLASIVAC UGOVOR UGOVOR_O_OGLASAVANJU
STAVKA_UGOVORA EMITOVANJE_REKLAME REKLAMNI_BLOK CENOVNIK_REKL_TERMINA PLAN_NABAVKE
STAVKA_PLANA_NABAVKE ZAHTEV_ZA_NABAVKU PONUDA_DOBAVLJACA PONUDJENA_STAVKA OCENA_PONUDE
KRITERIJUM_VREDNOVANJA DOBAVLJAC NARUDZBENICA""".split()

BY = {t['name']: t for t in TABLES}

def tipovi_m():
    """M zapis (record) sa listom tipova po tabeli - generiše se iz ER šeme."""
    L = ['let', '    Tipovi = [']
    for i, ime in enumerate(OSNOVNE):
        pol = ', '.join('{"%s", %s}' % (c['n'], m_tip(c['t'])) for c in BY[ime]['cols'])
        L.append('        %s = {%s}%s' % (ime, pol, ',' if i < len(OSNOVNE) - 1 else ''))
    L += ['    ]', 'in', '    Tipovi']
    return L

TABELA_FJA = [
    '// Čita jednu tabelu iz Access baze ili iz CSV izvoza i postavlja tipove.',
    '(ime as text) as table =>',
    'let',
    '    sirovo =',
    '        if Izvor = "CSV" then',
    '            Table.PromoteHeaders(',
    '                Csv.Document(File.Contents(PutDoCsv & "\\" & ime & ".csv"),',
    '                    [Delimiter=";", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
    '                [PromoteAllScalars=true])',
    '        else',
    '            Access.Database(File.Contents(PutDoBaze),',
    '                [CreateNavigationProperties=false]){[Name=ime]}[Data],',
    '    trazeni = Record.FieldOrDefault(Tipovi, ime, {}),',
    '    postojeci = Table.ColumnNames(sirovo),',
    '    primenjivi = List.Select(trazeni, each List.Contains(postojeci, _{0})),',
    '    rez = if List.IsEmpty(primenjivi) then sirovo',
    '          else Table.TransformColumnTypes(sirovo, primenjivi, "en-US")',
    'in',
    '    rez',
]

PARAMETRI = [
    ('Izvor', '"Access" meta [IsParameterQuery=true, List={"Access", "CSV"},'
              ' DefaultValue="Access", Type="Text", IsParameterQueryRequired=true]', 'Text'),
    ('PutDoBaze', '"C:\\TV_Panorama\\Access_v1.accdb" meta [IsParameterQuery=true,'
                  ' Type="Text", IsParameterQueryRequired=true]', 'Text'),
    ('PutDoCsv', '"C:\\TV_Panorama\\csv" meta [IsParameterQuery=true,'
                 ' Type="Text", IsParameterQueryRequired=true]', 'Text'),
]


# ---------------------------------------------------------------- pomoć za M
def zavrsi(prethodni, mapa, ime_koraka='Izlaz'):
    """Odabir kolona + preimenovanje u prikazna imena.  Vraća (linije, zadnji_korak)."""
    izv = ['"%s"' % a for a, b in mapa]
    pre = ['{"%s", "%s"}' % (a, b) for a, b in mapa if a != b]
    L = ['    Odabir = Table.SelectColumns(%s, {%s}),' % (prethodni, ', '.join(izv))]
    if not pre:
        return [L[0].rstrip(',')], 'Odabir'
    L.append('    %s = Table.RenameColumns(Odabir, {%s})' % (ime_koraka, ', '.join(pre)))
    return L, ime_koraka


def upit(koraci, mapa, zadnji):
    L = ['let'] + koraci
    d, ime = zavrsi(zadnji, mapa)
    L += d + ['in', '    ' + ime]
    return L


# ---------------------------------------------------------------- tabele
# kolona: (ime, dataType, summarizeBy, formatString, isHidden)
S, N, D = 'string', 'int64', 'dateTime'
DEC, DBL = 'decimal', 'double'
VAL = '#,##0.00'
CEO = '#,##0'
VRM = 'hh:nn:ss'


def K(ime, tip, sumar='none', fmt=None, sakr=False):
    return dict(ime=ime, tip=tip, sumar=sumar, fmt=fmt, sakr=sakr)


def M(ime, izraz, fmt=None, opis=None):
    return dict(ime=ime, izraz=izraz, fmt=fmt, opis=opis)


KALENDAR = dict(
    ime='Kalendar', datum='Datum', opis='Dimenzija datuma (2025-2028).',
    m=['let',
       '    Od = #date(2025, 1, 1),',
       '    Do = #date(2028, 12, 31),',
       '    Meseci = {"januar", "februar", "mart", "april", "maj", "jun", "jul",',
       '        "avgust", "septembar", "oktobar", "novembar", "decembar"},',
       '    ImenaDana = {"ponedeljak", "utorak", "sreda", "četvrtak", "petak",',
       '        "subota", "nedelja"},',
       '    Lista = List.Dates(Od, Duration.Days(Do - Od) + 1, #duration(1, 0, 0, 0)),',
       '    Osnov = Table.TransformColumnTypes(',
       '        Table.FromList(Lista, Splitter.SplitByNothing(), {"Datum"}),',
       '        {{"Datum", type date}}),',
       '    K1 = Table.AddColumn(Osnov, "Godina", each Date.Year([Datum]), Int64.Type),',
       '    K2 = Table.AddColumn(K1, "Kvartal",',
       '        each "Q" & Text.From(Date.QuarterOfYear([Datum])), type text),',
       '    K3 = Table.AddColumn(K2, "Mesec", each Date.Month([Datum]), Int64.Type),',
       '    K4 = Table.AddColumn(K3, "Naziv meseca",',
       '        each Meseci{Date.Month([Datum]) - 1}, type text),',
       '    K5 = Table.AddColumn(K4, "Godina-mesec",',
       '        each Text.From(Date.Year([Datum])) & "-" &',
       '            Text.PadStart(Text.From(Date.Month([Datum])), 2, "0"), type text),',
       '    K6 = Table.AddColumn(K5, "Dan", each Date.Day([Datum]), Int64.Type),',
       '    K7 = Table.AddColumn(K6, "Naziv dana",',
       '        each ImenaDana{Date.DayOfWeek([Datum], Day.Monday)}, type text)',
       'in',
       '    K7'],
    kolone=[K('Datum', D), K('Godina', N), K('Kvartal', S), K('Mesec', N, sakr=True),
            K('Naziv meseca', S), K('Godina-mesec', S), K('Dan', N, sakr=True),
            K('Naziv dana', S)],
    mere=[])

EMISIJE = dict(
    ime='Emisije', opis='Dimenzija: emisije iz programske šeme.',
    m=upit(['    Osnov = Tabela("EMISIJA"),'],
           [('SIFRA_EMISIJE', 'Šifra emisije'), ('NAZIV_EMISIJE', 'Naziv emisije'),
            ('ZANR', 'Žanr'), ('FORMAT_EMISIJE', 'Format emisije'),
            ('PREDVIDJENO_TRAJANJE', 'Predviđeno trajanje'),
            ('CILJNA_PUBLIKA', 'Ciljna publika'), ('STATUS_EMISIJE', 'Status emisije')],
           'Osnov'),
    kolone=[K('Šifra emisije', S), K('Naziv emisije', S), K('Žanr', S),
            K('Format emisije', S), K('Predviđeno trajanje', N, 'sum', CEO),
            K('Ciljna publika', S), K('Status emisije', S)],
    mere=[])

PROJEKTI = dict(
    ime='Projekti', opis='Dimenzija: projekti produkcije sa odobrenim budžetom.',
    m=upit(['    P = Tabela("PROJEKAT_PRODUKCIJE"),',
            '    Z = Tabela("ZAPOSLENI"),',
            '    E = Tabela("EMISIJA"),',
            '    S1 = Table.NestedJoin(P, {"SIFRA_UREDNIKA"}, Z, {"SIFRA_ZAPOSLENOG"},',
            '        "z", JoinKind.LeftOuter),',
            '    S2 = Table.ExpandTableColumn(S1, "z", {"IME", "PREZIME"},',
            '        {"IME_U", "PREZIME_U"}),',
            '    S3 = Table.AddColumn(S2, "UREDNIK",',
            '        each [PREZIME_U] & " " & [IME_U], type text),',
            '    S4 = Table.NestedJoin(S3, {"SIFRA_EMISIJE"}, E, {"SIFRA_EMISIJE"},',
            '        "e", JoinKind.LeftOuter),',
            '    S5 = Table.ExpandTableColumn(S4, "e", {"NAZIV_EMISIJE"}),'],
           [('SIFRA_PROJEKTA', 'Šifra projekta'), ('NAZIV_PROJEKTA', 'Naziv projekta'),
            ('VRSTA_PRODUKCIJE', 'Vrsta produkcije'), ('STATUS_PROJEKTA', 'Status projekta'),
            ('DATUM_POCETKA', 'Datum početka'), ('DATUM_ZAVRSETKA', 'Datum završetka'),
            ('ODOBREN_BUDZET', 'Odobren budžet'), ('UREDNIK', 'Urednik'),
            ('NAZIV_EMISIJE', 'Emisija'), ('OPIS_PROJEKTA', 'Opis projekta')],
           'S5'),
    kolone=[K('Šifra projekta', S), K('Naziv projekta', S), K('Vrsta produkcije', S),
            K('Status projekta', S), K('Datum početka', D), K('Datum završetka', D),
            K('Odobren budžet', DEC, 'sum', VAL), K('Urednik', S), K('Emisija', S),
            K('Opis projekta', S)],
    mere=[M('Odobren budžet (ukupno)', 'SUM(Projekti[Odobren budžet])', VAL),
          M('% iskorišćenja budžeta',
            "DIVIDE([Ukupno troškova], [Odobren budžet (ukupno)])", '0.0%')])

UGOVORI = dict(
    ime='Ugovori', opis='Dimenzija: ugovori o oglašavanju sa podacima o oglašivaču.',
    m=upit(['    U = Tabela("UGOVOR"),',
            '    UO = Tabela("UGOVOR_O_OGLASAVANJU"),',
            '    Kl = Tabela("KLIJENT"),',
            '    OG = Tabela("OGLASIVAC"),',
            '    F = Tabela("FAKTURA"),',
            '    S1 = Table.NestedJoin(U, {"BROJ_UGOVORA"}, UO, {"BROJ_UGOVORA"},',
            '        "uo", JoinKind.Inner),',
            '    S2 = Table.ExpandTableColumn(S1, "uo", {"UGOVORENI_TERMINI"}),',
            '    S3 = Table.NestedJoin(S2, {"SIFRA_KLIJENTA"}, Kl, {"SIFRA_KLIJENTA"},',
            '        "k", JoinKind.Inner),',
            '    S4 = Table.ExpandTableColumn(S3, "k",',
            '        {"NAZIV_KLIJENTA", "PIB", "KONTAKT_OSOBA", "GRAD"}),',
            '    S5 = Table.NestedJoin(S4, {"SIFRA_KLIJENTA"}, OG, {"SIFRA_KLIJENTA"},',
            '        "og", JoinKind.Inner),',
            '    S6 = Table.ExpandTableColumn(S5, "og", {"BRANSA", "GODISNJI_BUDZET"}),',
            '    Fak = Table.Group(Table.SelectRows(F, each [BROJ_UGOVORA] <> null),',
            '        {"BROJ_UGOVORA"},',
            '        {{"FAKTURISANO", each List.Sum([IZNOS_ZA_PLACANJE]), Currency.Type},',
            '         {"STATUS_FAKTURE", each List.Min([STATUS_PLACANJA]), type text}}),',
            '    S7 = Table.NestedJoin(S6, {"BROJ_UGOVORA"}, Fak, {"BROJ_UGOVORA"},',
            '        "f", JoinKind.LeftOuter),',
            '    S8 = Table.ExpandTableColumn(S7, "f",',
            '        {"FAKTURISANO", "STATUS_FAKTURE"}),'],
           [('BROJ_UGOVORA', 'Broj ugovora'), ('SIFRA_KLIJENTA', 'Šifra oglašivača'),
            ('NAZIV_KLIJENTA', 'Oglašivač'), ('PIB', 'PIB'),
            ('KONTAKT_OSOBA', 'Kontakt osoba'), ('GRAD', 'Grad'), ('BRANSA', 'Branša'),
            ('GODISNJI_BUDZET', 'Godišnji budžet'),
            ('DATUM_SKLAPANJA', 'Datum sklapanja'), ('VAZI_OD', 'Važi od'),
            ('VAZI_DO', 'Važi do'), ('STATUS_UGOVORA', 'Status ugovora'),
            ('UKUPNA_VREDNOST', 'Vrednost ugovora'),
            ('UGOVORENI_TERMINI', 'Ugovoreni termini'),
            ('FAKTURISANO', 'Fakturisano (iznos)'), ('STATUS_FAKTURE', 'Status fakture')],
           'S8'),
    kolone=[K('Broj ugovora', S), K('Šifra oglašivača', S), K('Oglašivač', S), K('PIB', S),
            K('Kontakt osoba', S), K('Grad', S), K('Branša', S),
            K('Godišnji budžet', DEC, 'sum', VAL), K('Datum sklapanja', D),
            K('Važi od', D), K('Važi do', D), K('Status ugovora', S),
            K('Vrednost ugovora', DEC, 'sum', VAL), K('Ugovoreni termini', S),
            K('Fakturisano (iznos)', DEC, 'sum', VAL), K('Status fakture', S)],
    mere=[M('Fakturisano', 'SUM(Ugovori[Fakturisano (iznos)])', VAL),
          M('Broj ugovora (broj)', 'DISTINCTCOUNT(Ugovori[Broj ugovora])', CEO),
          M('Razlika sekundi', '[Ugovoreno sekundi] - [Realizovano sekundi]', CEO),
          M('% realizacije sekundi',
            'DIVIDE([Realizovano sekundi], [Ugovoreno sekundi])', '0.0%'),
          M('% naplate', 'DIVIDE([Naplaćeno], [Ugovorena vrednost])', '0.0%')])

PLANOVI = dict(
    ime='Planovi', opis='Dimenzija: planovi nabavke sa povezanim zahtevom.',
    m=upit(['    P = Tabela("PLAN_NABAVKE"),',
            '    Z = Tabela("ZAHTEV_ZA_NABAVKU"),',
            '    Z1 = Table.SelectRows(Z, each [SIFRA_PLANA] <> null),',
            '    Zg = Table.Group(Z1, {"SIFRA_PLANA"}, {{"prvi",',
            '        each Table.FirstN(Table.Sort(_,',
            '            {{"BROJ_ZAHTEVA", Order.Ascending}}), 1), type table}}),',
            '    Ze = Table.ExpandTableColumn(Zg, "prvi",',
            '        {"BROJ_ZAHTEVA", "DATUM_ZAHTEVA", "STATUS_ZAHTEVA", "PRIORITET"}),',
            '    S1 = Table.NestedJoin(P, {"SIFRA_PLANA"}, Ze, {"SIFRA_PLANA"},',
            '        "z", JoinKind.LeftOuter),',
            '    S2 = Table.ExpandTableColumn(S1, "z",',
            '        {"BROJ_ZAHTEVA", "DATUM_ZAHTEVA", "STATUS_ZAHTEVA", "PRIORITET"}),'],
           [('SIFRA_PLANA', 'Šifra plana'), ('GODINA_PLANA', 'Godina plana'),
            ('DATUM_DONOSENJA', 'Datum donošenja'), ('STATUS_PLANA', 'Status plana'),
            ('DONOSILAC_PLANA', 'Donosilac plana'),
            ('UKUPNA_VREDNOST', 'Vrednost plana'), ('BROJ_ZAHTEVA', 'Broj zahteva'),
            ('DATUM_ZAHTEVA', 'Datum zahteva'), ('STATUS_ZAHTEVA', 'Status zahteva'),
            ('PRIORITET', 'Prioritet')],
           'S2'),
    kolone=[K('Šifra plana', S), K('Godina plana', N, 'none', '0'),
            K('Datum donošenja', D), K('Status plana', S), K('Donosilac plana', S),
            K('Vrednost plana', DEC, 'sum', VAL), K('Broj zahteva', S),
            K('Datum zahteva', D), K('Status zahteva', S), K('Prioritet', S)],
    mere=[])

DOBAVLJACI = dict(
    ime='Dobavljaci', opis='Dimenzija: dobavljači koji su dostavili ponude.',
    m=upit(['    Osnov = Tabela("DOBAVLJAC"),'],
           [('SIFRA_DOBAVLJACA', 'Šifra dobavljača'),
            ('NAZIV_DOBAVLJACA', 'Naziv dobavljača'), ('PIB', 'PIB'),
            ('ADRESA', 'Adresa'), ('OCENA_DOBAVLJACA', 'Ocena dobavljača')],
           'Osnov'),
    kolone=[K('Šifra dobavljača', S), K('Naziv dobavljača', S), K('PIB', S),
            K('Adresa', S), K('Ocena dobavljača', DBL, 'average', '0.00')],
    mere=[])


PLAYOUT = dict(
    ime='Playout', opis='Izveštaj 2: evidencija stvarno emitovanog sadržaja.',
    m=upit(['    ZE = Tabela("ZAPIS_O_EMITOVANJU"),',
            '    TE = Tabela("TERMIN_EMITOVANJA"),',
            '    MS = Tabela("MEDIJSKI_SADRZAJ"),',
            '    PP = Tabela("POKRIVENOST_PRAVOM"),',
            '    PK = Tabela("PRAVO_KORISCENJA"),',
            '    S1 = Table.NestedJoin(ZE, {"SIFRA_TERMINA"}, TE, {"SIFRA_TERMINA"},',
            '        "te", JoinKind.Inner),',
            '    S2 = Table.ExpandTableColumn(S1, "te", {"DATUM", "VREME_POCETKA",',
            '        "TRAJANJE_TERMINA", "SIFRA_EMISIJE", "TIP_TERMINA",',
            '        "ZONA_GLEDANOSTI", "STATUS_TERMINA"}),',
            '    S3 = Table.NestedJoin(S2, {"SIFRA_SADRZAJA"}, MS, {"SIFRA_SADRZAJA"},',
            '        "ms", JoinKind.Inner),',
            '    S4 = Table.ExpandTableColumn(S3, "ms",',
            '        {"NAZIV_SADRZAJA", "FORMAT_ZAPISA"}),',
            '    // jedno pravo po sadrzaju, da spajanje ne umnozi redove',
            '    Pr1 = Table.NestedJoin(PP, {"BROJ_LICENCE"}, PK, {"BROJ_LICENCE"},',
            '        "pk", JoinKind.Inner),',
            '    Pr2 = Table.ExpandTableColumn(Pr1, "pk", {"VRSTA_PRAVA"}),',
            '    Pr3 = Table.Group(Pr2, {"SIFRA_SADRZAJA"},',
            '        {{"BROJ_LICENCE", each List.Min([BROJ_LICENCE]), type text},',
            '         {"VRSTA_PRAVA", each List.Min([VRSTA_PRAVA]), type text}}),',
            '    S5 = Table.NestedJoin(S4, {"SIFRA_SADRZAJA"}, Pr3, {"SIFRA_SADRZAJA"},',
            '        "pr", JoinKind.LeftOuter),',
            '    S6 = Table.ExpandTableColumn(S5, "pr",',
            '        {"BROJ_LICENCE", "VRSTA_PRAVA"}),',
            '    S7 = Table.AddColumn(S6, "ODSTUPANJE",',
            '        each [STVARNO_TRAJANJE] - [TRAJANJE_TERMINA], Int64.Type),',
            '    S8 = Table.AddColumn(S7, "IMA_SMETNJU",',
            '        each if [NAPOMENA_O_SMETNJAMA] = null',
            '            or [NAPOMENA_O_SMETNJAMA] = "" then 0 else 1, Int64.Type),'],
           [('DATUM', 'Datum'), ('STVARNO_VREME_POCETKA', 'Stvarno vreme početka'),
            ('SIFRA_EMISIJE', 'Šifra emisije'), ('NAZIV_SADRZAJA', 'Medijski sadržaj'),
            ('FORMAT_ZAPISA', 'Format zapisa'),
            ('TRAJANJE_TERMINA', 'Planirano trajanje'),
            ('STVARNO_TRAJANJE', 'Stvarno trajanje'), ('ODSTUPANJE', 'Odstupanje'),
            ('STATUS_REALIZACIJE', 'Status realizacije'),
            ('BROJ_LICENCE', 'Broj licence'), ('VRSTA_PRAVA', 'Vrsta prava'),
            ('OPERATER_EMITOVANJA', 'Operater emitovanja'),
            ('NAPOMENA_O_SMETNJAMA', 'Napomena o smetnjama'),
            ('IMA_SMETNJU', 'Ima smetnju'), ('SIFRA_TERMINA', 'Šifra termina'),
            ('RB_EMITOVANJA', 'Rb emitovanja'), ('TIP_TERMINA', 'Tip termina'),
            ('ZONA_GLEDANOSTI', 'Zona gledanosti')],
           'S8'),
    kolone=[K('Datum', D), K('Stvarno vreme početka', D, 'none', VRM),
            K('Šifra emisije', S, sakr=True), K('Medijski sadržaj', S),
            K('Format zapisa', S), K('Planirano trajanje', N, 'sum', CEO),
            K('Stvarno trajanje', N, 'sum', CEO), K('Odstupanje', N, 'sum', CEO),
            K('Status realizacije', S), K('Broj licence', S), K('Vrsta prava', S),
            K('Operater emitovanja', S), K('Napomena o smetnjama', S),
            K('Ima smetnju', N, 'sum', CEO, True), K('Šifra termina', S),
            K('Rb emitovanja', N), K('Tip termina', S), K('Zona gledanosti', S)],
    mere=[M('Broj emitovanja', 'COUNTROWS(Playout)', CEO),
          M('Stvarno trajanje (min)', 'SUM(Playout[Stvarno trajanje])', CEO),
          M('Planirano trajanje (min)', 'SUM(Playout[Planirano trajanje])', CEO),
          M('Odstupanje (min)', 'SUM(Playout[Odstupanje])', CEO),
          M('Emitovanja sa smetnjama', 'SUM(Playout[Ima smetnju])', CEO),
          M('% realizovanih',
            'DIVIDE(\n    CALCULATE(COUNTROWS(Playout),'
            ' Playout[Status realizacije] = "Realizovano"),\n    COUNTROWS(Playout)\n)',
            '0.0%')])

GLEDANOST = dict(
    ime='Gledanost', opis='Izveštaj 3: merenja gledanosti po emisiji i žanru.',
    m=upit(['    ME = Tabela("MERENJE_EMISIJE"),',
            '    MG = Tabela("MERENJE_GLEDANOSTI"),',
            '    S1 = Table.NestedJoin(ME, {"SIFRA_MERENJA"}, MG, {"SIFRA_MERENJA"},',
            '        "mg", JoinKind.Inner),',
            '    S2 = Table.ExpandTableColumn(S1, "mg", {"DATUM_MERENJA",',
            '        "IZVOR_MERENJA", "CILJNA_GRUPA", "BROJ_GLEDALACA",',
            '        "PROSECNO_GLEDANJE"}),'],
           [('SIFRA_MERENJA', 'Šifra merenja'), ('SIFRA_EMISIJE', 'Šifra emisije'),
            ('DATUM_MERENJA', 'Datum merenja'), ('IZVOR_MERENJA', 'Izvor merenja'),
            ('CILJNA_GRUPA', 'Ciljna grupa'), ('OSTVARENI_RATING', 'Ostvareni rejting'),
            ('UDEO_U_TERMINU', 'Udeo u terminu'), ('BROJ_GLEDALACA', 'Broj gledalaca'),
            ('PROSECNO_GLEDANJE', 'Prosečno gledanje')],
           'S2'),
    kolone=[K('Šifra merenja', S), K('Šifra emisije', S, sakr=True),
            K('Datum merenja', D), K('Izvor merenja', S), K('Ciljna grupa', S),
            K('Ostvareni rejting', DBL, 'average', '0.00'),
            K('Udeo u terminu', DBL, 'average', '0.00'),
            K('Broj gledalaca', N, 'sum', CEO),
            K('Prosečno gledanje', N, 'average', '0.0')],
    mere=[M('Broj merenja', 'COUNTROWS(Gledanost)', CEO),
          M('Prosečan rejting', 'AVERAGE(Gledanost[Ostvareni rejting])', '0.00'),
          M('Prosečan udeo', 'AVERAGE(Gledanost[Udeo u terminu])', '0.00'),
          M('Prosečno gledalaca', 'AVERAGE(Gledanost[Broj gledalaca])', CEO),
          M('Prosečno gledanje (min)', 'AVERAGE(Gledanost[Prosečno gledanje])', '0.0')])

TROSKOVI = dict(
    ime='Troskovi', opis='Izveštaj 4: troškovi po aktivnostima projekata produkcije.',
    m=upit(['    TP = Tabela("TROSAK_PRODUKCIJE"),',
            '    AP = Tabela("AKTIVNOST_PRODUKCIJE"),',
            '    F = Tabela("FAKTURA"),',
            '    S1 = Table.NestedJoin(TP, {"SIFRA_PROJEKTA", "RB_AKTIVNOSTI"}, AP,',
            '        {"SIFRA_PROJEKTA", "RB_AKTIVNOSTI"}, "ap", JoinKind.Inner),',
            '    S2 = Table.ExpandTableColumn(S1, "ap", {"NAZIV_AKTIVNOSTI",',
            '        "VRSTA_AKTIVNOSTI", "LOKACIJA_SNIMANJA", "STATUS_AKTIVNOSTI",',
            '        "DATUM_OD", "DATUM_DO"}),',
            '    S3 = Table.NestedJoin(S2, {"BROJ_FAKTURE"}, F, {"BROJ_FAKTURE"},',
            '        "f", JoinKind.LeftOuter),',
            '    S4 = Table.ExpandTableColumn(S3, "f", {"STATUS_PLACANJA"}),',
            '    S5 = Table.AddColumn(S4, "KLJUC_AKTIVNOSTI",',
            '        each [SIFRA_PROJEKTA] & "-" &',
            '            Text.PadStart(Text.From([RB_AKTIVNOSTI]), 3, "0"), type text),'],
           [('SIFRA_PROJEKTA', 'Šifra projekta'), ('RB_AKTIVNOSTI', 'Rb aktivnosti'),
            ('NAZIV_AKTIVNOSTI', 'Aktivnost'), ('VRSTA_AKTIVNOSTI', 'Vrsta aktivnosti'),
            ('LOKACIJA_SNIMANJA', 'Lokacija snimanja'),
            ('STATUS_AKTIVNOSTI', 'Status aktivnosti'), ('DATUM_OD', 'Aktivnost od'),
            ('DATUM_DO', 'Aktivnost do'), ('RB_TROSKA', 'Rb troška'),
            ('VRSTA_TROSKA', 'Vrsta troška'), ('OPIS_TROSKA', 'Opis troška'),
            ('DATUM_NASTANKA', 'Datum nastanka'), ('IZNOS', 'Iznos'),
            ('BROJ_FAKTURE', 'Broj fakture'), ('STATUS_PLACANJA', 'Status plaćanja'),
            ('KLJUC_AKTIVNOSTI', 'Ključ aktivnosti')],
           'S5'),
    kolone=[K('Šifra projekta', S, sakr=True), K('Rb aktivnosti', N),
            K('Aktivnost', S), K('Vrsta aktivnosti', S), K('Lokacija snimanja', S),
            K('Status aktivnosti', S), K('Aktivnost od', D), K('Aktivnost do', D),
            K('Rb troška', N), K('Vrsta troška', S), K('Opis troška', S),
            K('Datum nastanka', D), K('Iznos', DEC, 'sum', VAL),
            K('Broj fakture', S), K('Status plaćanja', S),
            K('Ključ aktivnosti', S, sakr=True)],
    mere=[M('Ukupno troškova', 'SUM(Troskovi[Iznos])', VAL),
          M('Broj troškova', 'COUNTROWS(Troskovi)', CEO),
          M('Broj aktivnosti', 'DISTINCTCOUNT(Troskovi[Ključ aktivnosti])', CEO),
          M('Prosečan trošak', 'AVERAGE(Troskovi[Iznos])', VAL)])

STAVKE_UGOVORA = dict(
    ime='StavkeUgovora', opis='Izveštaj 6: ugovorene stavke (sekunde i vrednost).',
    m=upit(['    SU = Tabela("STAVKA_UGOVORA"),',
            '    UO = Tabela("UGOVOR_O_OGLASAVANJU"),',
            '    S1 = Table.NestedJoin(SU, {"BROJ_UGOVORA"}, UO, {"BROJ_UGOVORA"},',
            '        "uo", JoinKind.Inner),'],
           [('BROJ_UGOVORA', 'Broj ugovora'), ('RB_STAVKE', 'Rb stavke'),
            ('OPIS_STAVKE', 'Opis stavke'), ('KOLICINA_SEKUNDE', 'Ugovoreno sekundi'),
            ('JEDINICNA_CENA', 'Jedinična cena'), ('POPUST', 'Popust (%)'),
            ('VREDNOST_STAVKE', 'Vrednost stavke')],
           'S1'),
    kolone=[K('Broj ugovora', S, sakr=True), K('Rb stavke', N), K('Opis stavke', S),
            K('Ugovoreno sekundi', N, 'sum', CEO),
            K('Jedinična cena', DEC, 'sum', VAL), K('Popust (%)', DBL, 'average', '0.0'),
            K('Vrednost stavke', DEC, 'sum', VAL)],
    mere=[M('Ugovoreno sekundi', 'SUM(StavkeUgovora[Ugovoreno sekundi])', CEO),
          M('Ugovorena vrednost', 'SUM(StavkeUgovora[Vrednost stavke])', VAL),
          M('Broj stavki ugovora', 'COUNTROWS(StavkeUgovora)', CEO)])

EMITOVANJA_REKLAMA = dict(
    ime='EmitovanjaReklama', opis='Izveštaj 6: stvarno emitovani reklamni spotovi.',
    m=upit(['    ER = Tabela("EMITOVANJE_REKLAME"),',
            '    RB = Tabela("REKLAMNI_BLOK"),',
            '    CN = Tabela("CENOVNIK_REKL_TERMINA"),',
            '    S1 = Table.NestedJoin(ER, {"SIFRA_BLOKA"}, RB, {"SIFRA_BLOKA"},',
            '        "rb", JoinKind.LeftOuter),',
            '    S2 = Table.ExpandTableColumn(S1, "rb",',
            '        {"SIFRA_TERMINA", "SIFRA_CENOVNIKA"}),',
            '    S3 = Table.NestedJoin(S2, {"SIFRA_CENOVNIKA"}, CN, {"SIFRA_CENOVNIKA"},',
            '        "cn", JoinKind.LeftOuter),',
            '    S4 = Table.ExpandTableColumn(S3, "cn", {"ZONA", "CENA_PO_SEKUNDI"}),'],
           [('BROJ_UGOVORA', 'Broj ugovora'),
            ('RB_STAVKE_UGOVORA', 'Rb stavke ugovora'),
            ('DATUM_EMITOVANJA', 'Datum emitovanja'),
            ('VREME_EMITOVANJA', 'Vreme emitovanja'), ('SIFRA_BLOKA', 'Reklamni blok'),
            ('RB_U_BLOKU', 'Rb u bloku'), ('SIFRA_TERMINA', 'Termin'),
            ('ZONA', 'Zona'), ('CENA_PO_SEKUNDI', 'Cena po sekundi'),
            ('TRAJANJE_SPOTA', 'Trajanje spota'),
            ('NAPLACENI_IZNOS', 'Naplaćeni iznos'),
            ('STATUS_NAPLATE', 'Status naplate')],
           'S4'),
    kolone=[K('Broj ugovora', S, sakr=True), K('Rb stavke ugovora', N),
            K('Datum emitovanja', D), K('Vreme emitovanja', D, 'none', VRM),
            K('Reklamni blok', S), K('Rb u bloku', N), K('Termin', S), K('Zona', S),
            K('Cena po sekundi', DEC, 'sum', VAL),
            K('Trajanje spota', N, 'sum', CEO),
            K('Naplaćeni iznos', DEC, 'sum', VAL), K('Status naplate', S)],
    mere=[M('Realizovano sekundi', 'SUM(EmitovanjaReklama[Trajanje spota])', CEO),
          M('Naplaćeno', 'SUM(EmitovanjaReklama[Naplaćeni iznos])', VAL),
          M('Broj spotova', 'COUNTROWS(EmitovanjaReklama)', CEO)])

STAVKE_PLANA = dict(
    ime='StavkePlana', opis='Izveštaj 7: stavke plana nabavke i njihova realizacija.',
    m=upit(['    SP = Tabela("STAVKA_PLANA_NABAVKE"),',
            '    PS = Tabela("PONUDJENA_STAVKA"),',
            '    PD = Tabela("PONUDA_DOBAVLJACA"),',
            '    Db = Tabela("DOBAVLJAC"),',
            '    Nr = Tabela("NARUDZBENICA"),',
            '    // izabrana ponuda po stavci plana',
            '    I1 = Table.NestedJoin(PS, {"BROJ_PONUDE"}, PD, {"BROJ_PONUDE"},',
            '        "pd", JoinKind.Inner),',
            '    I2 = Table.ExpandTableColumn(I1, "pd",',
            '        {"SIFRA_DOBAVLJACA", "STATUS_PONUDE"}),',
            '    I3 = Table.SelectRows(I2, each [STATUS_PONUDE] = "Izabrana"),',
            '    I4 = Table.Group(I3, {"SIFRA_PLANA", "RB_STAVKE"},',
            '        {{"BROJ_PONUDE", each List.Min([BROJ_PONUDE]), type text},',
            '         {"SIFRA_DOBAVLJACA", each List.Min([SIFRA_DOBAVLJACA]), type text},',
            '         {"PONUDJENA_CENA", each List.Min([PONUDJENA_CENA]),',
            '          Currency.Type}}),',
            '    // narudzbenice po dobavljacu',
            '    N1 = Table.Group(Nr, {"SIFRA_DOBAVLJACA"},',
            '        {{"BROJ_NARUDZBENICE", each List.Min([BROJ_NARUDZBENICE]),',
            '          type text},',
            '         {"IZNOS_NARUDZBENICA", each List.Sum([UKUPAN_IZNOS]),',
            '          Currency.Type}}),',
            '    S1 = Table.NestedJoin(SP, {"SIFRA_PLANA", "RB_STAVKE"}, I4,',
            '        {"SIFRA_PLANA", "RB_STAVKE"}, "iz", JoinKind.LeftOuter),',
            '    S2 = Table.ExpandTableColumn(S1, "iz",',
            '        {"BROJ_PONUDE", "SIFRA_DOBAVLJACA", "PONUDJENA_CENA"}),',
            '    S3 = Table.NestedJoin(S2, {"SIFRA_DOBAVLJACA"}, Db,',
            '        {"SIFRA_DOBAVLJACA"}, "d", JoinKind.LeftOuter),',
            '    S4 = Table.ExpandTableColumn(S3, "d", {"NAZIV_DOBAVLJACA"}),',
            '    S5 = Table.NestedJoin(S4, {"SIFRA_DOBAVLJACA"}, N1,',
            '        {"SIFRA_DOBAVLJACA"}, "n", JoinKind.LeftOuter),',
            '    S6 = Table.ExpandTableColumn(S5, "n",',
            '        {"BROJ_NARUDZBENICE", "IZNOS_NARUDZBENICA"}),',
            '    S7 = Table.AddColumn(S6, "ODSTUPANJE",',
            '        each (if [IZNOS_NARUDZBENICA] = null then 0',
            '            else [IZNOS_NARUDZBENICA])',
            '            - (if [PROCENJENA_CENA] = null then 0',
            '            else [PROCENJENA_CENA]), Currency.Type),'],
           [('SIFRA_PLANA', 'Šifra plana'), ('RB_STAVKE', 'Rb stavke'),
            ('OPIS_ARTIKLA', 'Opis artikla'), ('KOLICINA', 'Količina'),
            ('JEDINICA_MERE', 'Jedinica mere'),
            ('PROCENJENA_CENA', 'Procenjena cena'),
            ('PLANIRANI_KVARTAL', 'Planirani kvartal'),
            ('BROJ_PONUDE', 'Izabrana ponuda'),
            ('PONUDJENA_CENA', 'Ponuđena cena'),
            ('NAZIV_DOBAVLJACA', 'Izabrani dobavljač'),
            ('BROJ_NARUDZBENICE', 'Broj narudžbenice'),
            ('IZNOS_NARUDZBENICA', 'Iznos narudžbenice'),
            ('ODSTUPANJE', 'Odstupanje')],
           'S7'),
    kolone=[K('Šifra plana', S, sakr=True), K('Rb stavke', N), K('Opis artikla', S),
            K('Količina', N, 'sum', CEO), K('Jedinica mere', S),
            K('Procenjena cena', DEC, 'sum', VAL), K('Planirani kvartal', S),
            K('Izabrana ponuda', S), K('Ponuđena cena', DEC, 'sum', VAL),
            K('Izabrani dobavljač', S), K('Broj narudžbenice', S),
            K('Iznos narudžbenice', DEC, 'sum', VAL),
            K('Odstupanje', DEC, 'sum', VAL)],
    mere=[M('Ukupno planirano', 'SUM(StavkePlana[Procenjena cena])', VAL),
          M('Ukupno naručeno', 'SUM(StavkePlana[Iznos narudžbenice])', VAL),
          M('Odstupanje nabavke', '[Ukupno naručeno] - [Ukupno planirano]', VAL),
          M('% izvršenja plana',
            'DIVIDE([Ukupno naručeno], [Ukupno planirano])', '0.0%'),
          M('Broj stavki plana', 'COUNTROWS(StavkePlana)', CEO)])

VREDNOVANJE = dict(
    ime='VrednovanjePonuda',
    opis='Izveštaj 7: bodovanje ponuda po kriterijumima vrednovanja.',
    m=upit(['    PS = Tabela("PONUDJENA_STAVKA"),',
            '    PD = Tabela("PONUDA_DOBAVLJACA"),',
            '    Db = Tabela("DOBAVLJAC"),',
            '    OP = Tabela("OCENA_PONUDE"),',
            '    KV = Tabela("KRITERIJUM_VREDNOVANJA"),',
            '    S1 = Table.NestedJoin(PS, {"BROJ_PONUDE"}, PD, {"BROJ_PONUDE"},',
            '        "pd", JoinKind.Inner),',
            '    S2 = Table.ExpandTableColumn(S1, "pd", {"SIFRA_DOBAVLJACA",',
            '        "DATUM_PRIJEMA", "UKUPNA_CENA", "ROK_ISPORUKE",',
            '        "USLOVI_PLACANJA", "UKUPNO_BODOVA", "STATUS_PONUDE"}),',
            '    S3 = Table.NestedJoin(S2, {"SIFRA_DOBAVLJACA"}, Db,',
            '        {"SIFRA_DOBAVLJACA"}, "d", JoinKind.Inner),',
            '    S4 = Table.ExpandTableColumn(S3, "d", {"NAZIV_DOBAVLJACA"}),',
            '    S5 = Table.NestedJoin(S4, {"BROJ_PONUDE"}, OP, {"BROJ_PONUDE"},',
            '        "op", JoinKind.LeftOuter),',
            '    S6 = Table.ExpandTableColumn(S5, "op",',
            '        {"SIFRA_KRITERIJUMA", "BROJ_BODOVA", "KOMENTAR_OCENE"}),',
            '    S7 = Table.NestedJoin(S6, {"SIFRA_KRITERIJUMA"}, KV,',
            '        {"SIFRA_KRITERIJUMA"}, "kv", JoinKind.LeftOuter),',
            '    S8 = Table.ExpandTableColumn(S7, "kv",',
            '        {"NAZIV_KRITERIJUMA", "NACIN_BODOVANJA"}),'],
           [('SIFRA_PLANA', 'Šifra plana'), ('RB_STAVKE', 'Rb stavke'),
            ('BROJ_PONUDE', 'Broj ponude'),
            ('SIFRA_DOBAVLJACA', 'Šifra dobavljača'),
            ('NAZIV_DOBAVLJACA', 'Dobavljač'), ('DATUM_PRIJEMA', 'Datum prijema'),
            ('UKUPNA_CENA', 'Ukupna cena ponude'),
            ('PONUDJENA_CENA', 'Ponuđena cena za stavku'),
            ('ROK_ISPORUKE', 'Rok isporuke'), ('USLOVI_PLACANJA', 'Uslovi plaćanja'),
            ('UKUPNO_BODOVA', 'Ukupno bodova'), ('STATUS_PONUDE', 'Status ponude'),
            ('NAZIV_KRITERIJUMA', 'Kriterijum'),
            ('NACIN_BODOVANJA', 'Način bodovanja'), ('BROJ_BODOVA', 'Bodovi'),
            ('KOMENTAR_OCENE', 'Komentar ocene')],
           'S8'),
    kolone=[K('Šifra plana', S, sakr=True), K('Rb stavke', N),
            K('Broj ponude', S), K('Šifra dobavljača', S, sakr=True),
            K('Dobavljač', S), K('Datum prijema', D),
            K('Ukupna cena ponude', DEC, 'sum', VAL),
            K('Ponuđena cena za stavku', DEC, 'sum', VAL), K('Rok isporuke', D),
            K('Uslovi plaćanja', S), K('Ukupno bodova', DBL, 'sum', '0.00'),
            K('Status ponude', S), K('Kriterijum', S), K('Način bodovanja', S),
            K('Bodovi', DBL, 'sum', '0.00'), K('Komentar ocene', S)],
    mere=[M('Bodovi (zbir)', 'SUM(VrednovanjePonuda[Bodovi])', '0.00'),
          M('Ukupno bodova ponude', 'MAX(VrednovanjePonuda[Ukupno bodova])', '0.00'),
          M('Broj ponuda', 'DISTINCTCOUNT(VrednovanjePonuda[Broj ponude])', CEO),
          M('Broj kriterijuma', 'DISTINCTCOUNT(VrednovanjePonuda[Kriterijum])', CEO)])

MODEL_TABELE = [KALENDAR, EMISIJE, PROJEKTI, UGOVORI, PLANOVI, DOBAVLJACI,
                PLAYOUT, GLEDANOST, TROSKOVI, STAVKE_UGOVORA, EMITOVANJA_REKLAMA,
                STAVKE_PLANA, VREDNOVANJE]

# ---------------------------------------------------------------- relacije
# (dim, kolona_dim, fact, kolona_fact)
RELACIJE = [
    ('Kalendar', 'Datum', 'Playout', 'Datum'),
    ('Kalendar', 'Datum', 'Gledanost', 'Datum merenja'),
    ('Kalendar', 'Datum', 'Troskovi', 'Datum nastanka'),
    ('Kalendar', 'Datum', 'EmitovanjaReklama', 'Datum emitovanja'),
    ('Kalendar', 'Datum', 'Planovi', 'Datum donošenja'),
    ('Emisije', 'Šifra emisije', 'Playout', 'Šifra emisije'),
    ('Emisije', 'Šifra emisije', 'Gledanost', 'Šifra emisije'),
    ('Projekti', 'Šifra projekta', 'Troskovi', 'Šifra projekta'),
    ('Ugovori', 'Broj ugovora', 'StavkeUgovora', 'Broj ugovora'),
    ('Ugovori', 'Broj ugovora', 'EmitovanjaReklama', 'Broj ugovora'),
    ('Planovi', 'Šifra plana', 'StavkePlana', 'Šifra plana'),
    ('Planovi', 'Šifra plana', 'VrednovanjePonuda', 'Šifra plana'),
    ('Dobavljaci', 'Šifra dobavljača', 'VrednovanjePonuda', 'Šifra dobavljača'),
]
