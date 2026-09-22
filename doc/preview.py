# -*- coding: utf-8 -*-
"""Cita generisani .docx i pravi HTML pregled + PNG (Chromium), posto
LibreOffice u ovom okruzenju ne ucitava nijedan .docx."""
import zipfile, html, sys, os
import xml.etree.ElementTree as ET
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def runs(el):
    out = []
    for r in el.iter(W + 'r'):
        t = r.find(W + 't')
        if t is not None and t.text:
            bel = r.find(W + 'rPr/' + W + 'b')
            b = bel is not None and bel.get(W + 'val') not in ('false', '0')
            out.append(('<b>%s</b>' if b else '%s') % html.escape(t.text))
    return ''.join(out)

def para(pel):
    st = pel.find(W + 'pPr/' + W + 'pStyle')
    s = st.get(W + 'val') if st is not None else ''
    txt = runs(pel)
    if not txt.strip(): return ''
    if s.startswith('Heading1'): return '<h1>%s</h1>' % txt
    if s.startswith('Heading2'): return '<h2>%s</h2>' % txt
    return '<p>%s</p>' % txt

def shade(tc):
    sh = tc.find(W + 'tcPr/' + W + 'shd')
    return sh.get(W + 'fill') if sh is not None else None

def table(tbl):
    grid = [int(g.get(W + 'w')) for g in tbl.findall(W + 'tblGrid/' + W + 'gridCol')]
    tot = sum(grid) or 1
    rows = []
    for tr in tbl.findall(W + 'tr'):
        cs = []
        for i, tc in enumerate(tr.findall(W + 'tc')):
            body = ''.join(para(p) for p in tc.findall(W + 'p')) or '&nbsp;'
            f = shade(tc)
            style = 'width:%.2f%%;' % (grid[i] / tot * 100) if i < len(grid) else ''
            if f and f != 'auto': style += 'background:#%s;' % f
            cs.append('<td style="%s">%s</td>' % (style, body))
        rows.append('<tr>%s</tr>' % ''.join(cs))
    return '<table>%s</table>' % ''.join(rows)

def build(src, out_html):
    z = zipfile.ZipFile(src)
    root = ET.fromstring(z.read('word/document.xml'))
    body = root.find(W + 'body')
    parts = []
    for el in body:
        if el.tag == W + 'p': parts.append(para(el))
        elif el.tag == W + 'tbl': parts.append(table(el))
    css = """body{background:#eceff3;margin:0;padding:28px;font-family:'Liberation Sans',Arial,sans-serif}
    .page{width:794px;margin:0 auto;background:#fff;padding:54px 64px 48px;
      box-shadow:0 1px 4px rgba(0,0,0,.16);color:#101418}
    h1{font-size:19px;margin:22px 0 10px;color:#1f3864}
    h1:first-child{margin-top:0}
    h2{font-size:15px;margin:20px 0 8px;color:#2f5496}
    p{font-size:11pt;line-height:1.5;margin:0 0 8px;text-align:justify}
    table{border-collapse:collapse;width:100%;margin:6px 0 4px;table-layout:fixed}
    td{border:1px solid #aab4c4;padding:5px 7px;vertical-align:top}
    td p{font-size:10pt;line-height:1.35;margin:0;text-align:left}"""
    open(out_html, 'w', encoding='utf-8').write(
        '<!DOCTYPE html><html lang="sr"><head><meta charset="utf-8"><style>%s</style>'
        '</head><body><div class="page">%s</div></body></html>' % (css, ''.join(parts)))
    return out_html

if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2]))
