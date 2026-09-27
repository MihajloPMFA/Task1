# -*- coding: utf-8 -*-
"""Pravi Power BI šablon (.pbit) - JEDAN fajl sa svih pet izveštaja.

Zašto .pbit a ne .pbix: u .pbix fajlu model je zapisan u delu DataModel, a to
je binarni Analysis Services stream (VertiPaq) koji ume da napiše samo Power BI
Desktop.  U .pbit fajlu isti model stoji kao TEKST (deo DataModelSchema, TMSL
JSON), pa se .pbit može napraviti i van Power BI-ja.  Kad se .pbit otvori i
osveži, File > Save as daje .pbix sa svim izveštajima u jednom fajlu.

Delovi paketa (namerno minimalno, da ne pogrešimo format nečega što Power BI
ionako sam regeneriše):
    [Content_Types].xml   UTF-8
    Version               UTF-16LE
    DataModelSchema       UTF-16LE, TMSL JSON (model, upiti, mere, relacije)
    Report/Layout         UTF-16LE, JSON izveštaja (pet strana, 61 vizual)
"""
import json, os, zipfile
BASE = os.path.dirname(os.path.abspath(__file__))
from gen_pbip import model_bim, NAZIV
from report_def import izvestaj

VERZIJA = '1.28'

# Minimalna varijanta (v1): samo cetiri dela.
CT_MIN = (
    '<?xml version="1.0" encoding="utf-8"?>\r\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="json" ContentType="" />'
    '<Override PartName="/Version" ContentType="" />'
    '<Override PartName="/DataModelSchema" ContentType="" />'
    '<Override PartName="/Report/Layout" ContentType="" />'
    '</Types>'
)
CONTENT_TYPES = CT_MIN            # zadrzano zbog check_pbit.py

# Puna varijanta (v2): dodati su delovi koje Power BI inace pise, plus
# _rels/.rels - OPC paket bez njega citac moze da proglasi neispravnim.
CT_PUN = (
    '<?xml version="1.0" encoding="utf-8"?>\r\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" '
    'ContentType="application/vnd.openxmlformats-package.relationships+xml" />'
    '<Default Extension="json" ContentType="" />'
    '<Override PartName="/Version" ContentType="" />'
    '<Override PartName="/DataModelSchema" ContentType="" />'
    '<Override PartName="/DiagramLayout" ContentType="" />'
    '<Override PartName="/Metadata" ContentType="" />'
    '<Override PartName="/Settings" ContentType="" />'
    '<Override PartName="/Report/Layout" ContentType="" />'
    '</Types>'
)
RELS = (
    '<?xml version="1.0" encoding="utf-8"?>\r\n'
    '<Relationships '
    'xmlns="http://schemas.openxmlformats.org/package/2006/relationships" />'
)
METADATA = '{"Version":3,"AutoCreatedRelationshipsEnabled":false}'
SETTINGS = '{"Version":3}'
DIAGRAM = '{"version":"1.1.0","diagrams":[]}'


def layout():
    d = izvestaj()
    d['id'] = 0
    return d


def u16(tekst, bom):
    return (('﻿' if bom else '') + tekst).encode('utf-16-le')


def napravi(put, bom, pun=False):
    sema = json.dumps(model_bim(), ensure_ascii=False)
    izgled = json.dumps(layout(), ensure_ascii=False)
    with zipfile.ZipFile(put, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', (CT_PUN if pun else CT_MIN).encode('utf-8'))
        if pun:
            z.writestr('_rels/.rels', RELS.encode('utf-8'))
        z.writestr('Version', u16(VERZIJA, bom))
        z.writestr('DataModelSchema', u16(sema, bom))
        if pun:
            z.writestr('DiagramLayout', u16(DIAGRAM, bom))
            z.writestr('Metadata', u16(METADATA, bom))
            z.writestr('Settings', u16(SETTINGS, bom))
        z.writestr('Report/Layout', u16(izgled, bom))
    return os.path.getsize(put)


def main():
    varijante = [('%s.pbit' % NAZIV, True, False),
                 ('%s_bez_BOM.pbit' % NAZIV, False, False),
                 ('%s_v2.pbit' % NAZIV, False, True),
                 ('%s_v3.pbit' % NAZIV, True, True)]
    for ime, bom, pun in varijante:
        put = os.path.join(BASE, ime)
        print('%-30s %s %s  %d KB'
              % (ime, 'BOM   ' if bom else 'bez BOM',
                 'puni delovi' if pun else 'minimalno  ', napravi(put, bom, pun) // 1024))


if __name__ == '__main__':
    main()
