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

CONTENT_TYPES = (
    '<?xml version="1.0" encoding="utf-8"?>\r\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="json" ContentType="" />'
    '<Override PartName="/Version" ContentType="" />'
    '<Override PartName="/DataModelSchema" ContentType="" />'
    '<Override PartName="/Report/Layout" ContentType="" />'
    '</Types>'
)


def layout():
    d = izvestaj()
    d['id'] = 0
    return d


def u16(tekst, bom):
    return (('﻿' if bom else '') + tekst).encode('utf-16-le')


def napravi(put, bom):
    sema = json.dumps(model_bim(), ensure_ascii=False)
    izgled = json.dumps(layout(), ensure_ascii=False)
    with zipfile.ZipFile(put, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', CONTENT_TYPES.encode('utf-8'))
        z.writestr('Version', u16(VERZIJA, bom))
        z.writestr('DataModelSchema', u16(sema, bom))
        z.writestr('Report/Layout', u16(izgled, bom))
    return os.path.getsize(put)


def main():
    a = os.path.join(BASE, '%s.pbit' % NAZIV)
    b = os.path.join(BASE, '%s_bez_BOM.pbit' % NAZIV)
    print('%s   %d KB' % (os.path.basename(a), napravi(a, True) // 1024))
    print('%s   %d KB' % (os.path.basename(b), napravi(b, False) // 1024))


if __name__ == '__main__':
    main()
