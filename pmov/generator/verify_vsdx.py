# -*- coding: utf-8 -*-
"""Nezavisna provera: cita generisani .vsdx i iscrtava ga u PNG."""
import sys, zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
NS = {'v': 'http://schemas.microsoft.com/office/visio/2012/main'}
FP = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FPB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

z = zipfile.ZipFile(sys.argv[1])
pg = ET.fromstring(z.read('visio/pages/pages.xml')).find('v:Page/v:PageSheet', NS)
cell = lambda e, n: (e.find("v:Cell[@N='%s']" % n, NS).get('V')
                     if e.find("v:Cell[@N='%s']" % n, NS) is not None else None)
PW, PH = float(cell(pg, 'PageWidth')), float(cell(pg, 'PageHeight'))
root = ET.fromstring(z.read('visio/pages/page1.xml'))
DPI = float(sys.argv[3]) if len(sys.argv) > 3 else 22.0
im = Image.new('RGB', (int(PW*DPI), int(PH*DPI)), 'white'); dr = ImageDraw.Draw(im)
X = lambda x: x*DPI
Y = lambda y: (PH-y)*DPI
fcache = {}
def fnt(pt, b):
    k = (round(pt, 2), b)
    if k not in fcache: fcache[k] = ImageFont.truetype(FPB if b else FP, max(5, int(pt*DPI)))
    return fcache[k]

nshape = dict(rect=0, dia=0, ell=0, line=0, text=0)
for sh in root.find('v:Shapes', NS).findall('v:Shape', NS):
    px, py = float(cell(sh, 'PinX')), float(cell(sh, 'PinY'))
    w, h = float(cell(sh, 'Width')), float(cell(sh, 'Height'))
    lpx = float(cell(sh, 'LocPinX') or 0); lpy = float(cell(sh, 'LocPinY') or 0)
    ox, oy = px - lpx, py - lpy
    g = sh.find("v:Section[@N='Geometry']", NS)
    ch = sh.find("v:Section[@N='Character']/v:Row", NS)
    size = float(cell(ch, 'Size')) if ch is not None and cell(ch, 'Size') else 0.1
    style = int(cell(ch, 'Style') or 0) if ch is not None else 0
    fill = cell(sh, 'FillForegnd'); fpat = cell(sh, 'FillPattern')
    lpat = cell(sh, 'LinePattern')
    te = sh.find('v:Text', NS)
    txt = ''.join(te.itertext()) if te is not None else ''
    rows = g.findall('v:Row', NS) if g is not None else []
    types = [r.get('T') for r in rows]
    pts = []
    for r in rows:
        rx, ry = cell(r, 'X'), cell(r, 'Y')
        if rx is None and ry is None: continue
        pts.append((ox + float(rx or 0), oy + float(ry or 0)))
    if 'EllipticalArcTo' in types:
        bb = [X(ox), Y(oy+h), X(ox+w), Y(oy)]
        outline = '#888888' if lpat == '2' else 'black'
        dr.ellipse(bb, outline=outline, fill=(fill if fpat != '0' else None)); nshape['ell'] += 1
    elif len(pts) == 5 and abs(pts[0][0]-(ox+w/2)) < 1e-6:
        dr.polygon([(X(a), Y(b)) for a, b in pts], outline='black',
                   fill=(fill if fpat != '0' else None)); nshape['dia'] += 1
    elif len(pts) >= 5 and fpat != '0' and abs(pts[0][0]-ox) < 1e-6 and abs(pts[0][1]-oy) < 1e-6:
        dr.rectangle([X(ox), Y(oy+h), X(ox+w), Y(oy)], outline='black', fill=fill)
        nshape['rect'] += 1
    elif pts:
        if fpat == '0' and not txt:
            dr.line([(X(a), Y(b)) for a, b in pts], fill='black', width=1); nshape['line'] += 1
        else:
            nshape['text'] += 1
    if txt.strip():
        f = fnt(size, style & 1)
        al = int(cell(sh.find("v:Section[@N='Paragraph']/v:Row", NS), 'HorzAlign') or 1) \
             if sh.find("v:Section[@N='Paragraph']/v:Row", NS) is not None else 1
        tw_ = float(cell(sh, 'TxtWidth') or w)
        lines = []
        for part in txt.strip('\n').split('\n'):
            cur = ''
            for wd in part.split(' '):
                t = (cur+' '+wd).strip()
                if dr.textlength(t, font=f) <= tw_*DPI or not cur: cur = t
                else: lines.append(cur); cur = wd
            lines.append(cur)
        lh = f.size*1.1
        y0 = Y(py) - (len(lines)-1)*lh/2
        for i, l in enumerate(lines):
            lw = dr.textlength(l, font=f)
            sx = X(px)-lw/2 if al == 1 else X(ox)
            dr.text((sx, y0+i*lh), l, font=f, fill='black', anchor='lm')
            if style & 4:
                dr.line([sx, y0+i*lh+f.size*0.55, sx+lw, y0+i*lh+f.size*0.55], fill='black')
im.save(sys.argv[2])
print('page %.1f x %.1f in ; shapes: %s ; saved %s' % (PW, PH, nshape, sys.argv[2]))
