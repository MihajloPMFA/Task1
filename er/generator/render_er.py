# -*- coding: utf-8 -*-
"""Nezavisno cita generisani .vsdx i crta PNG pregled -- provera da je u fajlu
zaista ono sto mislimo da jeste."""
import sys, zipfile, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
NS = {'v': 'http://schemas.microsoft.com/office/visio/2012/main'}

def fonts(sz):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
              '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()

def fontb(sz):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
              '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return fonts(sz)

def render(src, dst, dpi=110):
    z = zipfile.ZipFile(src)
    pg = ET.fromstring(z.read('visio/pages/pages.xml'))
    cw = {c.get('N'): c.get('V') for c in pg.iter('{%s}Cell' % NS['v'])}
    W, H = float(cw['PageWidth']), float(cw['PageHeight'])
    img = Image.new('RGB', (int(W * dpi), int(H * dpi)), 'white')
    d = ImageDraw.Draw(img)
    X = lambda x: x * dpi
    Y = lambda y: (H - y) * dpi
    root = ET.fromstring(z.read('visio/pages/page1.xml'))
    shapes = root.find('v:Shapes', NS).findall('v:Shape', NS)
    def cells(sh):
        return {c.get('N'): c.get('V') for c in sh.findall('v:Cell', NS)}
    def txt(sh):
        t = sh.find('v:Text', NS)
        return ''.join(t.itertext()) if t is not None else ''
    def chsec(sh):
        s = sh.find('v:Section[@N="Character"]/v:Row', NS)
        if s is None: return 9.0, 0, '#000000'
        c = {x.get('N'): x.get('V') for x in s.findall('v:Cell', NS)}
        return float(c.get('Size', 0.125)) * 72, int(c.get('Style', 0)), c.get('Color', '#000000')
    npoly = nbox = 0
    for sh in shapes:
        c = cells(sh)
        if c.get('ObjType') == '2':
            bx, by = float(c['BeginX']), float(c['BeginY'])
            pts = []
            for r in sh.findall('v:Section[@N="Geometry"]/v:Row', NS):
                q = {x.get('N'): x.get('V') for x in r.findall('v:Cell', NS)}
                pts.append((bx + float(q['X']), by + float(q['Y'])))
            dash = c.get('LinePattern') == '2'
            col = c.get('LineColor', '#000000')
            for a, b in zip(pts, pts[1:]):
                if dash:
                    n = max(1, int((abs(b[0]-a[0]) + abs(b[1]-a[1])) / 0.055))
                    for i in range(n):
                        if i % 2: continue
                        t0, t1 = i / n, min(1.0, (i + 0.75) / n)
                        d.line([X(a[0] + (b[0]-a[0])*t0), Y(a[1] + (b[1]-a[1])*t0),
                                X(a[0] + (b[0]-a[0])*t1), Y(a[1] + (b[1]-a[1])*t1)],
                               fill=col, width=1)
                else:
                    d.line([X(a[0]), Y(a[1]), X(b[0]), Y(b[1])], fill=col, width=1)
            npoly += 1
            continue
        w, h = float(c.get('Width', 0)), float(c.get('Height', 0))
        px, py = float(c.get('PinX', 0)), float(c.get('PinY', 0))
        x0, y0 = px - w / 2, py - h / 2
        fill = c.get('FillForegnd', '#ffffff')
        arc = sh.find('v:Section[@N="Geometry"]/v:Row[@T="EllipticalArcTo"]', NS) is not None
        if c.get('FillPattern') == '1':
            if arc:
                d.ellipse([X(x0), Y(y0 + h), X(x0 + w), Y(y0)], fill=fill,
                          outline='#000000')
            else:
                d.rectangle([X(x0), Y(y0 + h), X(x0 + w), Y(y0)], fill=fill,
                            outline='#000000')
            nbox += 1
        s, st, col = chsec(sh)
        t = txt(sh).strip('\n')
        if not t: continue
        fnt = (fontb if st & 1 else fonts)(max(5, int(s * dpi / 72)))
        align = sh.find('v:Section[@N="Paragraph"]/v:Row/v:Cell[@N="HorzAlign"]', NS)
        left = align is not None and align.get('V') == '0'
        lines = t.split('\n')
        lh = h * dpi / max(1, len(lines))
        for i, ln in enumerate(lines):
            ty = Y(y0 + h) + i * lh + lh / 2
            if left:
                d.text((X(x0) + 3, ty), ln, font=fnt, fill=col, anchor='lm')
            else:
                d.text((X(px), ty), ln, font=fnt, fill=col, anchor='mm')
    img.save(dst)
    return dst, W, H, nbox, npoly, len(shapes)

if __name__ == '__main__':
    print(render(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 110))
