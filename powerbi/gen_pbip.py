# -*- coding: utf-8 -*-
"""Sklapa Power BI projekat (.pbip) - semantički model (model.bim, TMSL) i
izveštaj (report.json).  Sve je običan tekst, pa se otvara u Power BI Desktop-u.
"""
import json, os, shutil, zipfile
BASE = os.path.dirname(os.path.abspath(__file__))
from model_def import (MODEL_TABELE, RELACIJE, PARAMETRI, TABELA_FJA, tipovi_m,
                       OSNOVNE)
from report_def import izvestaj

NAZIV = 'TV_Panorama'
IZLAZ = os.path.join(BASE, 'pbip')
SM = NAZIV + '.SemanticModel'
RP = NAZIV + '.Report'

TIPOVI_PBI = {'string': 'string', 'int64': 'int64', 'decimal': 'decimal',
              'double': 'double', 'dateTime': 'dateTime'}


def kolona(c):
    d = {'name': c['ime'], 'dataType': TIPOVI_PBI[c['tip']],
         'sourceColumn': c['ime'], 'summarizeBy': c['sumar']}
    if c['fmt']:
        d['formatString'] = c['fmt']
    if c['sakr']:
        d['isHidden'] = True
    return d


def mera(m):
    d = {'name': m['ime'], 'expression': m['izraz'].split('\n'),
         'displayFolder': 'Mere'}
    if m['fmt']:
        d['formatString'] = m['fmt']
    if m['opis']:
        d['description'] = m['opis']
    return d


def tabela(t):
    d = {'name': t['ime'],
         'columns': [kolona(c) for c in t['kolone']],
         'partitions': [{'name': t['ime'], 'mode': 'import',
                         'source': {'type': 'm', 'expression': t['m']}}]}
    if t.get('opis'):
        d['description'] = t['opis']
    if t['mere']:
        d['measures'] = [mera(m) for m in t['mere']]
    if t['ime'] == 'Kalendar':
        d['dataCategory'] = 'Time'
        d['columns'][0]['isKey'] = True
    return d


def model_bim():
    izrazi = []
    for ime, m, tip in PARAMETRI:
        izrazi.append({'name': ime, 'kind': 'm', 'expression': m,
                       'annotations': [{'name': 'PBI_ResultType', 'value': tip}]})
    izrazi.append({'name': 'Tipovi', 'kind': 'm', 'expression': tipovi_m(),
                   'annotations': [{'name': 'PBI_ResultType', 'value': 'Record'}]})
    izrazi.append({'name': 'Tabela', 'kind': 'm', 'expression': TABELA_FJA,
                   'annotations': [{'name': 'PBI_ResultType', 'value': 'Function'}]})
    rel = []
    for i, (dim, kd, fakt, kf) in enumerate(RELACIJE, 1):
        rel.append({'name': 'rel%02d_%s_%s' % (i, dim, fakt),
                    'fromTable': fakt, 'fromColumn': kf,
                    'toTable': dim, 'toColumn': kd})
    poredak = [p[0] for p in PARAMETRI] + ['Tipovi', 'Tabela'] + \
              [t['ime'] for t in MODEL_TABELE]
    return {'name': SM, 'compatibilityLevel': 1550,
            'model': {'culture': 'en-US',
                      'dataAccessOptions': {'legacyRedirects': True,
                                            'returnErrorValuesAsNull': True},
                      'defaultPowerBIDataSourceVersion': 'powerBI_V3',
                      'sourceQueryCulture': 'en-US',
                      'tables': [tabela(t) for t in MODEL_TABELE],
                      'relationships': rel,
                      'expressions': izrazi,
                      'annotations': [
                          {'name': 'PBI_QueryOrder',
                           'value': json.dumps(poredak, ensure_ascii=False)},
                          {'name': 'PBI_ProTooling', 'value': '["DevMode"]'}]}}


def upisi(put, podatak):
    os.makedirs(os.path.dirname(put), exist_ok=True)
    with open(put, 'w', encoding='utf-8', newline='\n') as f:
        if isinstance(podatak, str):
            f.write(podatak)
        else:
            json.dump(podatak, f, ensure_ascii=False, indent=2)
            f.write('\n')


def main():
    if os.path.isdir(IZLAZ):
        shutil.rmtree(IZLAZ)
    upisi(os.path.join(IZLAZ, NAZIV + '.pbip'), {
        'version': '1.0',
        'artifacts': [{'report': {'path': RP}}],
        'settings': {'enableAutoRecovery': True}})
    upisi(os.path.join(IZLAZ, SM, 'definition.pbism'),
          {'version': '1.0', 'settings': {}})
    upisi(os.path.join(IZLAZ, SM, 'model.bim'), model_bim())
    upisi(os.path.join(IZLAZ, RP, 'definition.pbir'),
          {'version': '1.0',
           'datasetReference': {'byPath': {'path': '../' + SM}}})
    upisi(os.path.join(IZLAZ, RP, 'report.json'), izvestaj())

    # CSV kopija kao rezervni izvor podataka
    src = os.path.join(BASE, 'csv')
    dst = os.path.join(IZLAZ, 'csv')
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        shutil.copy(os.path.join(src, f), os.path.join(dst, f))

    zip_put = os.path.join(BASE, 'TV_Panorama_PowerBI.zip')
    with zipfile.ZipFile(zip_put, 'w', zipfile.ZIP_DEFLATED) as z:
        for koren, _d, fajlovi in os.walk(IZLAZ):
            for f in sorted(fajlovi):
                p = os.path.join(koren, f)
                z.write(p, os.path.relpath(p, IZLAZ))
        for d in ('UPUTSTVO.md', 'M_upiti.txt', 'DAX_mere.txt',
                  NAZIV + '.pbit', NAZIV + '_bez_BOM.pbit'):
            p = os.path.join(BASE, d)
            if os.path.exists(p):
                z.write(p, d)
    print('projekat: %s' % IZLAZ)
    print('zip:      %s  (%d KB)' % (zip_put, os.path.getsize(zip_put) // 1024))
    print('tabela %d, kolona %d, mera %d, relacija %d, strana %d, vizuala %d'
          % (len(MODEL_TABELE),
             sum(len(t['kolone']) for t in MODEL_TABELE),
             sum(len(t['mere']) for t in MODEL_TABELE),
             len(RELACIJE), len(izvestaj()['sections']),
             sum(len(s['visualContainers']) for s in izvestaj()['sections'])))


if __name__ == '__main__':
    main()
