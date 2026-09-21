# -*- coding: utf-8 -*-
"""Okvir za UML dijagrame slucajeva koriscenja: model -> .drawio + .png,
sa automatskom proverom da nijedna linija ne prolazi kroz elipsu ili aktera."""
import html, math
from PIL import Image, ImageDraw, ImageFont

UC_W, UC_H = 178, 76          # elipsa slucaja koriscenja
AC_W, AC_H = 30, 60           # figura aktera (bez natpisa)
PAD = 30
F_UC, F_AC, F_LBL = 12, 12, 11

def _f(sz, bold=False):
    p = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else '')
    try:
        return ImageFont.truetype(p, sz)
    except Exception:
        return ImageFont.load_default()

class UseCase:
    def __init__(self, name, W, H):
        self.name, self.W, self.H = name, W, H
        self.nodes, self.edges, self.labels = {}, [], []

    # ---- cvorovi (koordinate su centar) ----
    def uc(self, nid, cx, cy, text, w=UC_W, h=UC_H):
        self.nodes[nid] = dict(id=nid, kind='uc', cx=cx, cy=cy, w=w, h=h, text=text)
        return self.nodes[nid]

    def actor(self, nid, cx, cy, text):
        self.nodes[nid] = dict(id=nid, kind='actor', cx=cx, cy=cy,
                               w=AC_W, h=AC_H, text=text)
        return self.nodes[nid]

    # ---- tacke na obodu ----
    def _n(self, nid): return self.nodes[nid]
    def L(self, nid): n = self._n(nid); return (n['cx'] - n['w'] / 2, n['cy'])
    def R(self, nid): n = self._n(nid); return (n['cx'] + n['w'] / 2, n['cy'])
    def T(self, nid): n = self._n(nid); return (n['cx'], n['cy'] - n['h'] / 2)
    def B(self, nid): n = self._n(nid); return (n['cx'], n['cy'] + n['h'] / 2)

    # ---- prelazi ----
    def assoc(self, pts):
        self.edges.append(dict(pts=[(float(a), float(b)) for a, b in pts], kind='assoc'))

    def rel(self, pts, kind, lpos=None):
        """kind: 'include' ili 'extend' -- isprekidana strelica sa natpisom."""
        self.edges.append(dict(pts=[(float(a), float(b)) for a, b in pts], kind=kind))
        p = pts[len(pts) // 2] if len(pts) > 2 else (
            ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2))
        x, y = lpos if lpos else (p[0], p[1] - 12)
        self.labels.append(dict(x=x, y=y, text='«%s»' % kind))

    # ---- provera: nijedan segment ne sme kroz elipsu/akterovu figuru ----
    def collisions(self):
        bad = []
        for ei, ed in enumerate(self.edges):
            ends = (ed['pts'][0], ed['pts'][-1])
            for n in self.nodes.values():
                if any(self._on(n, p) for p in ends):
                    continue
                for a, b in zip(ed['pts'], ed['pts'][1:]):
                    if self._hits(n, a, b):
                        bad.append((ei, n['id'])); break
        return bad

    @staticmethod
    def _on(n, p, tol=2.0):
        return (abs(p[0] - n['cx']) <= n['w'] / 2 + tol
                and abs(p[1] - n['cy']) <= n['h'] / 2 + tol)

    @staticmethod
    def _hits(n, a, b, margin=3.0):
        steps = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        rx, ry = n['w'] / 2 + margin, n['h'] / 2 + margin
        for i in range(steps + 1):
            t = i / steps
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            if n['kind'] == 'uc':
                if ((x - n['cx']) / rx) ** 2 + ((y - n['cy']) / ry) ** 2 < 1.0:
                    return True
            else:
                if abs(x - n['cx']) < rx and abs(y - n['cy']) < ry:
                    return True
        return False

# ---------------------------------------------------------------- draw.io
S_UC = ('ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;'
        'fontSize=12;fontColor=#000000;')
S_AC = ('shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;'
        'outlineConnect=0;fillColor=#ffffff;strokeColor=#000000;fontSize=12;')
S_ASSOC = 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeColor=#000000;'
S_REL = ('edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;endArrow=open;'
         'endSize=12;strokeColor=#000000;')
S_TXT = ('text;html=1;align=center;verticalAlign=middle;fillColor=none;'
         'strokeColor=none;fontSize=11;')

def _anchor(d, pt, tol=2.5):
    for n in d.nodes.values():
        x0, y0 = n['cx'] - n['w'] / 2, n['cy'] - n['h'] / 2
        x1, y1 = x0 + n['w'], y0 + n['h']
        on = ((abs(pt[0] - x0) < tol or abs(pt[0] - x1) < tol) and y0 - tol <= pt[1] <= y1 + tol) \
             or ((abs(pt[1] - y0) < tol or abs(pt[1] - y1) < tol) and x0 - tol <= pt[0] <= x1 + tol)
        if on:
            return n['id'], round((pt[0] - x0) / n['w'], 4), round((pt[1] - y0) / n['h'], 4)
    return None

def to_drawio(dgs, path):
    e = lambda s: html.escape(s, quote=True)
    out = ['<mxfile host="app.diagrams.net" type="device">']
    for di, d in enumerate(dgs):
        out.append('  <diagram id="u%d" name="%s">' % (di + 1, e(d.name)))
        out.append('    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" '
                   'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
                   'pageWidth="%d" pageHeight="%d" math="0" shadow="0">'
                   % (d.W + 2 * PAD, d.H + 2 * PAD))
        out.append('      <root><mxCell id="0"/><mxCell id="1" parent="0"/>')
        for n in d.nodes.values():
            st = S_UC if n['kind'] == 'uc' else S_AC
            out.append('        <mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
                       '<mxGeometry x="%g" y="%g" width="%g" height="%g" as="geometry"/>'
                       '</mxCell>'
                       % (e(n['id']), e(n['text']), st,
                          n['cx'] - n['w'] / 2, n['cy'] - n['h'] / 2, n['w'], n['h']))
        for k, ed in enumerate(d.edges):
            pts = ed['pts']
            st = S_ASSOC if ed['kind'] == 'assoc' else S_REL
            a, b = _anchor(d, pts[0]), _anchor(d, pts[-1])
            ref = ''
            if a:
                st += 'exitX=%g;exitY=%g;exitDx=0;exitDy=0;' % (a[1], a[2])
                ref += ' source="%s"' % e(a[0])
            if b:
                st += 'entryX=%g;entryY=%g;entryDx=0;entryDy=0;' % (b[1], b[2])
                ref += ' target="%s"' % e(b[0])
            mid = ''.join('<mxPoint x="%g" y="%g"/>' % p for p in pts[1:-1])
            out.append('        <mxCell id="r%d_%d" style="%s" edge="1" parent="1"%s>'
                       '<mxGeometry relative="1" as="geometry">'
                       '<mxPoint x="%g" y="%g" as="sourcePoint"/>'
                       '<mxPoint x="%g" y="%g" as="targetPoint"/>%s</mxGeometry></mxCell>'
                       % (di, k, st, ref, pts[0][0], pts[0][1], pts[-1][0], pts[-1][1],
                          ('<Array as="points">%s</Array>' % mid) if mid else ''))
        for k, lb in enumerate(d.labels):
            out.append('        <mxCell id="l%d_%d" value="%s" style="%s" vertex="1" '
                       'parent="1"><mxGeometry x="%g" y="%g" width="70" height="18" '
                       'as="geometry"/></mxCell>'
                       % (di, k, e(lb['text']), S_TXT, lb['x'] - 35, lb['y'] - 9))
        out.append('      </root>')
        out.append('    </mxGraphModel>')
        out.append('  </diagram>')
    out.append('</mxfile>')
    open(path, 'w', encoding='utf-8').write('\n'.join(out))
    return path

# ---------------------------------------------------------------- PNG
def _wrap(dr, s, fnt, maxw):
    words, lines, cur = s.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if dr.textlength(t, font=fnt) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def to_png(d, path, scale=2):
    S = scale
    img = Image.new('RGB', (int((d.W + 2 * PAD) * S), int((d.H + 2 * PAD) * S)), 'white')
    dr = ImageDraw.Draw(img)
    X = lambda v: (PAD + v) * S
    Y = lambda v: (PAD + v) * S
    fu, fa, fl = _f(F_UC * S), _f(F_AC * S), _f(F_LBL * S)

    for ed in d.edges:
        pts = [(X(a), Y(b)) for a, b in ed['pts']]
        dash = ed['kind'] != 'assoc'
        for a, b in zip(pts, pts[1:]):
            if not dash:
                dr.line([a[0], a[1], b[0], b[1]], fill='black', width=S)
            else:
                ln = math.hypot(b[0] - a[0], b[1] - a[1])
                n = max(1, int(ln / (7 * S)))
                for i in range(n):
                    if i % 2: continue
                    t0, t1 = i / n, min(1.0, (i + 0.8) / n)
                    dr.line([a[0] + (b[0]-a[0])*t0, a[1] + (b[1]-a[1])*t0,
                             a[0] + (b[0]-a[0])*t1, a[1] + (b[1]-a[1])*t1],
                            fill='black', width=S)
        if dash:                                   # otvorena strelica na kraju
            (x1, y1), (x2, y2) = pts[-2], pts[-1]
            ang = math.atan2(y2 - y1, x2 - x1)
            a_ = 10 * S
            for s_ in (+1, -1):
                dr.line([x2, y2, x2 - a_ * math.cos(ang - s_ * 0.45),
                         y2 - a_ * math.sin(ang - s_ * 0.45)], fill='black', width=S)

    for n in d.nodes.values():
        cx, cy = X(n['cx']), Y(n['cy'])
        w, h = n['w'] * S, n['h'] * S
        if n['kind'] == 'uc':
            dr.ellipse([cx - w/2, cy - h/2, cx + w/2, cy + h/2],
                       fill='white', outline='black', width=S)
            lines = _wrap(dr, n['text'], fu, w * 0.74)
            lh = fu.size * 1.22
            ty = cy - lh * (len(lines) - 1) / 2
            for i, t in enumerate(lines):
                dr.text((cx, ty + i * lh), t, font=fu, fill='black', anchor='mm')
        else:
            r = 9 * S
            top = cy - h / 2
            dr.ellipse([cx - r, top, cx + r, top + 2 * r], fill='white',
                       outline='black', width=S)
            body0, body1 = top + 2 * r, top + h * 0.62
            dr.line([cx, body0, cx, body1], fill='black', width=S)
            dr.line([cx - 15 * S, body0 + 9 * S, cx + 15 * S, body0 + 9 * S],
                    fill='black', width=S)
            dr.line([cx, body1, cx - 12 * S, top + h], fill='black', width=S)
            dr.line([cx, body1, cx + 12 * S, top + h], fill='black', width=S)
            dr.text((cx, top + h + 11 * S), n['text'], font=fa, fill='black', anchor='ma')

    for lb in d.labels:
        dr.text((X(lb['x']), Y(lb['y'])), lb['text'], font=fl, fill='black', anchor='mm')
    img.save(path)
    return path, img.size
