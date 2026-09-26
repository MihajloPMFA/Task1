# -*- coding: utf-8 -*-
"""Definicija Power BI izveštaja (report.json) - pet strana iz specifikacije.

Raspored je isti na svim stranama:
  A (y 12-80)    naslov i podnaslov
  B (y 92-178)   četiri kartice sa ključnim pokazateljima + slajser
  C (y 190-400)  dva grafikona + slajseri
  D (y 412-704)  tabela ili matrica sa detaljima
"""
import json

SIR, VIS = 1280, 720
# mreza
A_Y, A_H = 12, 44
A2_Y, A2_H = 58, 24
B_Y, B_H = 92, 86
C_Y, C_H = 190, 210
D_Y, D_H = 412, 292
KART_X = [16, 248, 480, 712]
KART_W = 220
C1_X, C1_W = 16, 456
C2_X, C2_W = 484, 444
SL_X, SL_W = 940, 324
D_X, D_W = 16, 1248

_brojac = [0]


def _ime():
    _brojac[0] += 1
    return 'v%04d' % _brojac[0]


def C(tabela, polje):
    """Kolona modela."""
    return ('c', tabela, polje)


def Me(tabela, polje):
    """Mera modela."""
    return ('m', tabela, polje)


def _upit(polja, sort=None):
    """Napravi From/Select/OrderBy i listu queryRef-ova."""
    tabele, alias = [], {}
    for _, t, _p in polja:
        if t not in alias:
            alias[t] = 't%d' % len(alias)
            tabele.append(t)
    frm = [{'Name': alias[t], 'Entity': t, 'Type': 0} for t in tabele]
    sel, refs = [], []
    for kind, t, p in polja:
        izraz = {'Expression': {'SourceRef': {'Source': alias[t]}}, 'Property': p}
        ref = '%s.%s' % (t, p)
        sel.append({('Measure' if kind == 'm' else 'Column'): izraz,
                    'Name': ref, 'NativeReferenceName': p})
        refs.append(ref)
    q = {'Version': 2, 'From': frm, 'Select': sel}
    if sort:
        kind, t, p, smer = sort
        if t not in alias:
            raise ValueError('sortiranje po polju koje nije u upitu: %s.%s' % (t, p))
        q['OrderBy'] = [{'Direction': smer,
                         'Expression': {('Measure' if kind == 'm' else 'Column'):
                                        {'Expression': {'SourceRef': {'Source': alias[t]}},
                                         'Property': p}}}]
    return q, refs


def _lit(v):
    return {'expr': {'Literal': {'Value': v}}}


def _tekst(s):
    return _lit("'" + s.replace("'", "''") + "'")


def visual(vtype, x, y, w, h, uloge, sort=None, naslov=None, objects=None, z=None):
    """uloge: lista (uloga, [polja]) - redosled se čuva."""
    polja, proj = [], {}
    for uloga, lista in uloge:
        proj[uloga] = []
        for f in lista:
            polja.append(f)
    q, refs = _upit(polja, sort)
    i = 0
    for uloga, lista in uloge:
        for _f in lista:
            proj[uloga].append({'queryRef': refs[i]})
            i += 1
    sv = {'visualType': vtype, 'projections': proj, 'prototypeQuery': q,
          'drillFilterOtherVisuals': True}
    if objects:
        sv['objects'] = objects
    vc = {'title': [{'properties': {'show': _lit('true'),
                                    'text': _tekst(naslov or ''),
                                    'fontSize': _lit("10D"),
                                    'titleWrap': _lit('true')}}]}
    if naslov:
        sv['vcObjects'] = vc
    pos = {'x': x, 'y': y, 'z': z if z is not None else 0, 'width': w, 'height': h,
           'tabOrder': _brojac[0] * 100}
    cfg = {'name': _ime(), 'layouts': [{'id': 0, 'position': dict(pos)}],
           'singleVisual': sv}
    return {'x': float(x), 'y': float(y), 'z': float(pos['z']),
            'width': float(w), 'height': float(h),
            'config': json.dumps(cfg, ensure_ascii=False), 'filters': '[]'}


def tekst(x, y, w, h, delovi):
    """delovi: lista (tekst, velicina_pt, bold, boja)."""
    runs = []
    for t, vel, bold, boja in delovi:
        runs.append({'value': t,
                     'textStyle': {'fontSize': '%dpt' % vel, 'fontFamily': 'Segoe UI',
                                   'fontWeight': 'bold' if bold else 'normal',
                                   'color': boja}})
    sv = {'visualType': 'textbox', 'drillFilterOtherVisuals': True,
          'objects': {'general': [{'properties': {'paragraphs': [{'textRuns': runs}]}}]}}
    pos = {'x': x, 'y': y, 'z': 0, 'width': w, 'height': h, 'tabOrder': 0}
    cfg = {'name': _ime(), 'layouts': [{'id': 0, 'position': dict(pos)}],
           'singleVisual': sv}
    return {'x': float(x), 'y': float(y), 'z': 0.0, 'width': float(w),
            'height': float(h),
            'config': json.dumps(cfg, ensure_ascii=False), 'filters': '[]'}


def kartica(i, polje, naslov):
    return visual('card', KART_X[i], B_Y, KART_W, B_H, [('Values', [polje])],
                  naslov=naslov,
                  objects={'labels': [{'properties': {'fontSize': _lit('19D'),
                                                      'labelPrecision': _lit('0D')}}],
                           'categoryLabels': [{'properties': {'show': _lit('false')}}]})


def slajser(polje, x, y, w, h, naslov, opseg=False, padajuci=False):
    obj = {}
    if opseg:
        obj['data'] = [{'properties': {'mode': _lit("'Between'")}}]
    if padajuci:
        obj['data'] = [{'properties': {'mode': _lit("'Dropdown'")}}]
    return visual('slicer', x, y, w, h, [('Values', [polje])], naslov=naslov,
                  objects=obj or None)


def strana(redni, naziv, vizuali):
    return {'name': 'Strana%d' % redni, 'displayName': naziv, 'ordinal': redni - 1,
            'config': '{}', 'filters': '[]', 'displayOption': 1,
            'width': float(SIR), 'height': float(VIS),
            'visualContainers': vizuali}


# ---------------------------------------------------------------- boje i naslovi
TAMNA, SIVA = '#1B2A41', '#5A6475'
PODNASLOV = 'Informacioni sistem TV stanice - TV Panorama'


def zaglavlje(naslov, dodatak):
    return [tekst(16, A_Y, 900, A_H, [(naslov, 16, True, TAMNA)]),
            tekst(16, A2_Y, 900, A2_H, [(PODNASLOV + '  |  ' + dodatak, 9, False, SIVA)])]


# ================================================================ strana 1 (izv 2)
def strana_playout():
    v = zaglavlje('Izveštaj 2 - Evidencija emitovanog sadržaja (playout log)',
                  'period se bira slajserom Datum')
    v += [kartica(0, Me('Playout', 'Broj emitovanja'), 'Broj emitovanja'),
          kartica(1, Me('Playout', 'Stvarno trajanje (min)'), 'Stvarno trajanje (min)'),
          kartica(2, Me('Playout', 'Odstupanje (min)'), 'Odstupanje (min)'),
          kartica(3, Me('Playout', 'Emitovanja sa smetnjama'), 'Sa smetnjama'),
          slajser(C('Kalendar', 'Datum'), SL_X, B_Y, SL_W, B_H,
                  'Datum emitovanja (od - do)', opseg=True),
          visual('columnChart', C1_X, C_Y, C1_W, C_H,
                 [('Category', [C('Kalendar', 'Datum')]),
                  ('Y', [Me('Playout', 'Stvarno trajanje (min)')])],
                 naslov='Emitovani minuti po danu'),
          visual('donutChart', C2_X, C_Y, C2_W, C_H,
                 [('Category', [C('Playout', 'Status realizacije')]),
                  ('Y', [Me('Playout', 'Broj emitovanja')])],
                 naslov='Emitovanja po statusu realizacije'),
          slajser(C('Playout', 'Status realizacije'), SL_X, C_Y, SL_W, 100,
                  'Status realizacije'),
          slajser(C('Emisije', 'Žanr'), SL_X, C_Y + 108, SL_W, 102, 'Žanr emisije'),
          visual('tableEx', D_X, D_Y, D_W, D_H,
                 [('Values', [C('Playout', 'Datum'),
                              C('Playout', 'Stvarno vreme početka'),
                              C('Emisije', 'Naziv emisije'),
                              C('Playout', 'Medijski sadržaj'),
                              C('Playout', 'Planirano trajanje'),
                              C('Playout', 'Stvarno trajanje'),
                              C('Playout', 'Odstupanje'),
                              C('Playout', 'Status realizacije'),
                              C('Playout', 'Broj licence'),
                              C('Playout', 'Vrsta prava'),
                              C('Playout', 'Operater emitovanja'),
                              C('Playout', 'Napomena o smetnjama')])],
                 sort=('c', 'Playout', 'Datum', 1),
                 naslov='Hronološki pregled emitovanog sadržaja')]
    return strana(1, '2 Playout log', v)


# ================================================================ strana 2 (izv 3)
def strana_gledanost():
    v = zaglavlje('Izveštaj 3 - Gledanost emisija po žanru',
                  'grafički prikaz sa pratećom tabelom')
    v += [kartica(0, Me('Gledanost', 'Prosečan rejting'), 'Prosečan rejting'),
          kartica(1, Me('Gledanost', 'Prosečan udeo'), 'Prosečan udeo u terminu'),
          kartica(2, Me('Gledanost', 'Prosečno gledalaca'), 'Prosečno gledalaca'),
          kartica(3, Me('Gledanost', 'Broj merenja'), 'Broj merenja'),
          slajser(C('Kalendar', 'Datum'), SL_X, B_Y, SL_W, B_H,
                  'Period merenja (od - do)', opseg=True),
          visual('clusteredColumnChart', C1_X, C_Y, C1_W, C_H,
                 [('Category', [C('Emisije', 'Žanr')]),
                  ('Y', [Me('Gledanost', 'Prosečan rejting')])],
                 sort=('m', 'Gledanost', 'Prosečan rejting', 2),
                 naslov='Prosečan ostvareni rejting po žanru emisije'),
          visual('lineChart', C2_X, C_Y, C2_W, C_H,
                 [('Category', [C('Gledanost', 'Datum merenja')]),
                  ('Y', [Me('Gledanost', 'Prosečan rejting')])],
                 naslov='Kretanje prosečnog rejtinga po datumu merenja'),
          slajser(C('Gledanost', 'Izvor merenja'), SL_X, C_Y, SL_W, 100,
                  'Izvor merenja'),
          slajser(C('Gledanost', 'Ciljna grupa'), SL_X, C_Y + 108, SL_W, 102,
                  'Ciljna grupa'),
          visual('tableEx', D_X, D_Y, D_W, D_H,
                 [('Values', [C('Emisije', 'Naziv emisije'), C('Emisije', 'Žanr'),
                              Me('Gledanost', 'Broj merenja'),
                              Me('Gledanost', 'Prosečan rejting'),
                              Me('Gledanost', 'Prosečan udeo'),
                              Me('Gledanost', 'Prosečno gledalaca'),
                              Me('Gledanost', 'Prosečno gledanje (min)')])],
                 sort=('m', 'Gledanost', 'Prosečan rejting', 2),
                 naslov='Gledanost po emisiji - opadajuće po ostvarenom rejtingu')]
    return strana(2, '3 Gledanost po žanru', v)


# ================================================================ strana 3 (izv 4)
def strana_troskovi():
    v = zaglavlje('Izveštaj 4 - Realizacija i troškovi projekta produkcije',
                  'zbirovi po projektu i aktivnosti, sa iskorišćenjem budžeta')
    v += [kartica(0, Me('Troskovi', 'Ukupno troškova'), 'Ukupno troškova'),
          kartica(1, Me('Projekti', 'Odobren budžet (ukupno)'), 'Odobren budžet'),
          kartica(2, Me('Projekti', '% iskorišćenja budžeta'), '% iskorišćenja budžeta'),
          kartica(3, Me('Troskovi', 'Broj aktivnosti'), 'Broj aktivnosti'),
          slajser(C('Projekti', 'Naziv projekta'), SL_X, B_Y, SL_W, B_H,
                  'Projekat produkcije', padajuci=True),
          visual('columnChart', C1_X, C_Y, C1_W, C_H,
                 [('Category', [C('Troskovi', 'Vrsta troška')]),
                  ('Y', [Me('Troskovi', 'Ukupno troškova')])],
                 sort=('m', 'Troskovi', 'Ukupno troškova', 2),
                 naslov='Troškovi po vrsti troška'),
          visual('barChart', C2_X, C_Y, C2_W, C_H,
                 [('Category', [C('Projekti', 'Naziv projekta')]),
                  ('Y', [Me('Projekti', '% iskorišćenja budžeta')])],
                 sort=('m', 'Projekti', '% iskorišćenja budžeta', 2),
                 naslov='Iskorišćenost odobrenog budžeta po projektu'),
          slajser(C('Projekti', 'Vrsta produkcije'), SL_X, C_Y, SL_W, 100,
                  'Vrsta produkcije'),
          slajser(C('Kalendar', 'Datum'), SL_X, C_Y + 108, SL_W, 102,
                  'Datum nastanka troška (od - do)', opseg=True),
          visual('pivotTable', D_X, D_Y, D_W, D_H,
                 [('Rows', [C('Projekti', 'Naziv projekta'), C('Troskovi', 'Aktivnost'),
                            C('Troskovi', 'Vrsta troška')]),
                  ('Values', [Me('Troskovi', 'Ukupno troškova'),
                              Me('Troskovi', 'Broj troškova'),
                              Me('Projekti', 'Odobren budžet (ukupno)'),
                              Me('Projekti', '% iskorišćenja budžeta')])],
                 naslov='Projekat - aktivnost - trošak, sa zbirovima')]
    return strana(3, '4 Troškovi produkcije', v)


# ================================================================ strana 4 (izv 6)
def strana_oglasivac():
    v = zaglavlje('Izveštaj 6 - Realizacija ugovora o oglašavanju po oglašivaču',
                  'oglašivač se bira slajserom - zamena za parametar iz Access izveštaja')
    v += [kartica(0, Me('StavkeUgovora', 'Ugovoreno sekundi'), 'Ugovoreno sekundi'),
          kartica(1, Me('EmitovanjaReklama', 'Realizovano sekundi'), 'Realizovano sekundi'),
          kartica(2, Me('EmitovanjaReklama', 'Naplaćeno'), 'Naplaćeno'),
          kartica(3, Me('Ugovori', '% naplate'), '% naplate'),
          slajser(C('Ugovori', 'Oglašivač'), SL_X, B_Y, SL_W, B_H, 'Oglašivač',
                  padajuci=True),
          visual('pivotTable', C1_X, C_Y, C1_W, C_H,
                 [('Rows', [C('Ugovori', 'Broj ugovora'),
                            C('StavkeUgovora', 'Opis stavke')]),
                  ('Values', [Me('StavkeUgovora', 'Ugovoreno sekundi'),
                              Me('StavkeUgovora', 'Ugovorena vrednost')])],
                 naslov='Ugovorene stavke po ugovoru'),
          visual('columnChart', C2_X, C_Y, C2_W, C_H,
                 [('Category', [C('Kalendar', 'Naziv meseca')]),
                  ('Y', [Me('EmitovanjaReklama', 'Naplaćeno')])],
                 naslov='Naplaćeni iznos po mesecu emitovanja'),
          slajser(C('Ugovori', 'Status ugovora'), SL_X, C_Y, SL_W, 100,
                  'Status ugovora'),
          slajser(C('Kalendar', 'Datum'), SL_X, C_Y + 108, SL_W, 102,
                  'Datum emitovanja (od - do)', opseg=True),
          visual('tableEx', D_X, D_Y, D_W, D_H,
                 [('Values', [C('Ugovori', 'Broj ugovora'),
                              C('EmitovanjaReklama', 'Datum emitovanja'),
                              C('EmitovanjaReklama', 'Vreme emitovanja'),
                              C('EmitovanjaReklama', 'Reklamni blok'),
                              C('EmitovanjaReklama', 'Termin'),
                              C('EmitovanjaReklama', 'Zona'),
                              C('EmitovanjaReklama', 'Trajanje spota'),
                              C('EmitovanjaReklama', 'Naplaćeni iznos'),
                              C('EmitovanjaReklama', 'Status naplate')])],
                 sort=('c', 'EmitovanjaReklama', 'Datum emitovanja', 1),
                 naslov='Stvarno emitovani reklamni spotovi')]
    return strana(4, '6 Kartica oglašivača', v)


# ================================================================ strana 5 (izv 7)
def strana_nabavka():
    v = zaglavlje('Izveštaj 7 - Realizacija plana nabavke sa vrednovanjem ponuda',
                  'izvršenje plana po stavkama i bodovi po kriterijumima')
    v += [kartica(0, Me('StavkePlana', 'Ukupno planirano'), 'Ukupno planirano'),
          kartica(1, Me('StavkePlana', 'Ukupno naručeno'), 'Ukupno naručeno'),
          kartica(2, Me('StavkePlana', '% izvršenja plana'), '% izvršenja plana'),
          kartica(3, Me('StavkePlana', 'Broj stavki plana'), 'Broj stavki plana'),
          slajser(C('Planovi', 'Šifra plana'), SL_X, B_Y, SL_W, B_H, 'Plan nabavke',
                  padajuci=True),
          visual('columnChart', C1_X, C_Y, C1_W, C_H,
                 [('Category', [C('StavkePlana', 'Planirani kvartal')]),
                  ('Y', [Me('StavkePlana', 'Ukupno planirano'),
                         Me('StavkePlana', 'Ukupno naručeno')])],
                 naslov='Planirano i naručeno po kvartalu'),
          visual('barChart', C2_X, C_Y, C2_W, C_H,
                 [('Category', [C('VrednovanjePonuda', 'Dobavljač')]),
                  ('Y', [Me('VrednovanjePonuda', 'Ukupno bodova ponude')])],
                 sort=('m', 'VrednovanjePonuda', 'Ukupno bodova ponude', 2),
                 naslov='Ukupan broj bodova po dobavljaču'),
          slajser(C('Planovi', 'Status plana'), SL_X, C_Y, SL_W, 100, 'Status plana'),
          slajser(C('StavkePlana', 'Planirani kvartal'), SL_X, C_Y + 108, SL_W, 102,
                  'Planirani kvartal'),
          visual('pivotTable', D_X, D_Y, 616, D_H,
                 [('Rows', [C('Planovi', 'Šifra plana'),
                            C('StavkePlana', 'Opis artikla')]),
                  ('Values', [Me('StavkePlana', 'Ukupno planirano'),
                              Me('StavkePlana', 'Ukupno naručeno'),
                              Me('StavkePlana', 'Odstupanje nabavke'),
                              Me('StavkePlana', '% izvršenja plana')])],
                 naslov='Stavke plana i njihova realizacija'),
          visual('pivotTable', 648, D_Y, 616, D_H,
                 [('Rows', [C('VrednovanjePonuda', 'Dobavljač'),
                            C('VrednovanjePonuda', 'Broj ponude')]),
                  ('Columns', [C('VrednovanjePonuda', 'Kriterijum')]),
                  ('Values', [Me('VrednovanjePonuda', 'Bodovi (zbir)')])],
                 naslov='Bodovi po kriterijumu vrednovanja')]
    return strana(5, '7 Plan nabavke i ponude', v)


STRANE = [strana_playout, strana_gledanost, strana_troskovi,
          strana_oglasivac, strana_nabavka]


def izvestaj():
    _brojac[0] = 0                      # imena vizuala moraju biti determinisana
    sekcije = [f() for f in STRANE]
    cfg = {'version': '5.55', 'activeSectionIndex': 0,
           'defaultDrillFilterOtherVisuals': True,
           'settings': {'useStylableVisualContainerHeader': True,
                        'exportDataMode': 1,
                        'useNewFilterPaneExperience': True,
                        'allowChangeFilterTypes': True,
                        'allowInlineExploration': False,
                        'disableFilterPaneSearch': False,
                        'useCrossReportDrillthrough': False,
                        'allowDataPointLassoSelect': False}}
    return {'config': json.dumps(cfg, ensure_ascii=False),
            'layoutOptimization': 0, 'publicCustomVisuals': [],
            'filters': '[]', 'sections': sekcije}
