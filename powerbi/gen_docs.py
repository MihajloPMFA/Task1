# -*- coding: utf-8 -*-
"""Generiše M_upiti.txt i DAX_mere.txt - rezervni put, za nalepiti u Power BI."""
import io, os
BASE = os.path.dirname(os.path.abspath(__file__))
from model_def import MODEL_TABELE, RELACIJE, PARAMETRI, TABELA_FJA, tipovi_m

CRTA = '=' * 78

def m_txt():
    L = ['POWER QUERY (M) UPITI - TV Panorama',
         '',
         'Redosled je važan: prvo tri parametra, pa Tipovi i Tabela, pa tabele modela.',
         'U Power BI Desktop-u: Home > Transform data > New Source > Blank Query,',
         'pa View > Advanced Editor i nalepi kod.  Upit preimenuj u naziv iz naslova.',
         '', CRTA, 'PARAMETRI (Home > Manage Parameters > New Parameter)', CRTA, '']
    for ime, izraz, tip in PARAMETRI:
        L += ['--- %s  (tip %s)' % (ime, tip), izraz, '']
    L += [CRTA, 'POMOĆNI UPITI', CRTA, '']
    L += ['--- Tipovi   (obična prazna upitnica, nije parametar)'] + tipovi_m() + ['']
    L += ['--- Tabela   (funkcija koja čita jednu tabelu)'] + TABELA_FJA + ['']
    L += [CRTA, 'TABELE MODELA', CRTA, '']
    for t in MODEL_TABELE:
        L += ['--- %s' % t['ime'], '// %s' % t['opis']] + t['m'] + ['']
    return '\n'.join(L) + '\n'

def dax_txt():
    L = ['DAX MERE - TV Panorama',
         '',
         'Mera se dodaje na tabelu koja je navedena u naslovu:',
         'desni klik na tabelu u oknu Data > New measure, pa nalepi izraz.',
         'U koloni "format" je format koji treba postaviti (Measure tools > Format).',
         '']
    for t in MODEL_TABELE:
        if not t['mere']:
            continue
        L += [CRTA, 'Tabela: %s' % t['ime'], CRTA, '']
        for m in t['mere']:
            L += ['-- %s     [format: %s]' % (m['ime'], m['fmt'] or 'opšti'),
                  '%s = %s' % (m['ime'], m['izraz']), '']
    L += [CRTA, 'RELACIJE (Model view - prevuci sa dimenzije na činjenicu)', CRTA, '',
          'Sve su tipa jedan-prema-više (1:*), smer filtriranja: jedan.', '']
    for dim, kd, fakt, kf in RELACIJE:
        L.append('  %-12s[%-18s]  1  ->  *  %-20s[%s]' % (dim, kd, fakt, kf))
    return '\n'.join(L) + '\n'

io.open(os.path.join(BASE, 'M_upiti.txt'), 'w', encoding='utf-8').write(m_txt())
io.open(os.path.join(BASE, 'DAX_mere.txt'), 'w', encoding='utf-8').write(dax_txt())
print('M_upiti.txt   %d linija' % m_txt().count('\n'))
print('DAX_mere.txt  %d linija' % dax_txt().count('\n'))
