# -*- coding: utf-8 -*-
"""Mali okvir za UML dijagrame aktivnosti: model -> .drawio (diagrams.net) + .png.
Koordinate su u pikselima, y raste nadole (kao u draw.io)."""
import html, os
from PIL import Image, ImageDraw, ImageFont

LANE_W = 300
HDR_H  = 34
ACT_W, ACT_H = 236, 44
DEC_W, DEC_H = 244, 74
CIRC   = 32
BAR_H  = 10
PAD    = 26

FONT_N, FONT_H, FONT_L = 12, 12, 11

def _f(sz, bold=False):
    base = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else '')
    try:
        return ImageFont.truetype(base, sz)
    except Exception:
        return ImageFont.load_default()

class Diagram:
    def __init__(self, name, lanes, height, lane_w=LANE_W):
        self.name = name
        self.lanes = lanes
        self.lane_w = lane_w
        self.W = lane_w * len(lanes)
        self.H = height
        self.nodes = {}
        self.edges = []
        self.labels = []

    # ---- geometrija ----
    def lx(self, i):                      # levi rub trake
        return i * self.lane_w
    def cx(self, i, dx=0):                # sredina trake
        return i * self.lane_w + self.lane_w / 2 + dx

    def node(self, nid, kind, lane, y, text='', dx=0, w=None, h=None, x=None):
        if kind == 'action':   w, h = w or ACT_W, h or ACT_H
        elif kind == 'decision': w, h = w or DEC_W, h or DEC_H
        elif kind in ('start', 'end'): w = h = CIRC
        elif kind == 'bar':    w, h = w or (self.lane_w * 1.5), BAR_H
        if x is None:
            x = self.cx(lane, dx) - w / 2
        self.nodes[nid] = dict(id=nid, kind=kind, x=x, y=y, w=w, h=h, text=text, lane=lane)
        return self.nodes[nid]

    def B(self, nid, fx=0.5): n = self.nodes[nid]; return (n['x'] + n['w'] * fx, n['y'] + n['h'])
    def T(self, nid, fx=0.5): n = self.nodes[nid]; return (n['x'] + n['w'] * fx, n['y'])
    def L(self, nid, fy=0.5): n = self.nodes[nid]; return (n['x'], n['y'] + n['h'] * fy)
    def R(self, nid, fy=0.5): n = self.nodes[nid]; return (n['x'] + n['w'], n['y'] + n['h'] * fy)

    def edge(self, pts, label=None, lpos=None):
        self.edges.append(dict(pts=[(float(a), float(b)) for a, b in pts]))
        if label:
            x, y = lpos if lpos else pts[0]
            self.labels.append(dict(x=x, y=y, text=label))

    def jog(self, p1, y, p2, label=None, lpos=None):
        """Vodoravno-uspravna putanja: dole do y, vodoravno, pa u ciljnu tacku."""
        self.edge([p1, (p1[0], y), (p2[0], y), p2], label, lpos)

    def loop(self, p1, x, p2, label='Ne'):
        """Povratna petlja kroz slobodnu kolonu x."""
        self.edge([p1, (x, p1[1]), (x, p2[1]), p2], label,
                  (x + 26, p1[1] - 16) if label else None)

    def text(self, x, y, s):
        self.labels.append(dict(x=x, y=y, text=s))

# ---------------------------------------------------------------- draw.io
STYLE = {
 'action':   'rounded=1;arcSize=18;whiteSpace=wrap;html=1;fillColor=#ffffff;'
             'strokeColor=#000000;fontSize=12;fontColor=#000000;',
 'decision': 'rhombus;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;'
             'fontSize=12;fontColor=#000000;spacingLeft=52;spacingRight=52;',
 'start':    'ellipse;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#000000;',
 'end':      'ellipse;shape=endState;whiteSpace=wrap;html=1;fillColor=#000000;'
             'strokeColor=#000000;',
 'bar':      'rounded=0;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#000000;',
}
EDGE_STYLE = ('edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=blockThin;'
              'endFill=1;strokeColor=#000000;jumpStyle=none;exitDx=0;exitDy=0;')
LANEHDR = ('rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;'
           'fontSize=12;fontStyle=1;')
LANEBOX = ('rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#000000;')
TXT = ('text;html=1;align=center;verticalAlign=middle;fillColor=none;strokeColor=none;'
       'fontSize=11;')

def _anchor(d, pt, tol=1.2):
    """Nadji cvor na cijoj ivici lezi tacka -> (id, relX, relY)."""
    x, y = pt
    for n in d.nodes.values():
        x0, y0, x1, y1 = n['x'], n['y'], n['x'] + n['w'], n['y'] + n['h']
        on_v = (abs(x - x0) < tol or abs(x - x1) < tol) and y0 - tol <= y <= y1 + tol
        on_h = (abs(y - y0) < tol or abs(y - y1) < tol) and x0 - tol <= x <= x1 + tol
        if on_v or on_h:
            return n['id'], round((x - x0) / n['w'], 4), round((y - y0) / n['h'], 4)
    return None

def to_drawio(dgs, path):
    e = lambda s: html.escape(s, quote=True)
    out = ['<mxfile host="app.diagrams.net" type="device">']
    for di, d in enumerate(dgs):
        out.append('  <diagram id="d%d" name="%s">' % (di + 1, e(d.name)))
        out.append('    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" '
                   'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
                   'pageWidth="%d" pageHeight="%d" math="0" shadow="0">'
                   % (d.W + 2 * PAD, d.H + 2 * PAD))
        out.append('      <root><mxCell id="0"/><mxCell id="1" parent="0"/>')
        c = [0]
        def cell(body):
            c[0] += 1
            out.append('        ' + body)
        # trake
        if d.lanes:
            cell('<mxCell id="%s_pool" value="" style="%s" vertex="1" parent="1">'
                 '<mxGeometry x="0" y="0" width="%d" height="%d" as="geometry"/></mxCell>'
                 % (d.name[:3] + str(di), LANEBOX, d.W, d.H))
            for i, ln in enumerate(d.lanes):
                cell('<mxCell id="%s_h%d" value="%s" style="%s" vertex="1" parent="1">'
                     '<mxGeometry x="%d" y="0" width="%d" height="%d" as="geometry"/></mxCell>'
                     % (d.name[:3] + str(di), i, e(ln), LANEHDR, d.lx(i), d.lane_w, HDR_H))
                if i:
                    cell('<mxCell id="%s_v%d" style="endArrow=none;html=1;strokeColor=#000000;" '
                         'edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                         '<mxPoint x="%d" y="%d" as="sourcePoint"/>'
                         '<mxPoint x="%d" y="%d" as="targetPoint"/></mxGeometry></mxCell>'
                         % (d.name[:3] + str(di), i, d.lx(i), HDR_H, d.lx(i), d.H))
        for n in d.nodes.values():
            cell('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
                 '<mxGeometry x="%g" y="%g" width="%g" height="%g" as="geometry"/></mxCell>'
                 % (e(n['id']), e(n['text']), STYLE[n['kind']], n['x'], n['y'], n['w'], n['h']))
        for k, ed in enumerate(d.edges):
            pts = ed['pts']
            mid = ''.join('<mxPoint x="%g" y="%g"/>' % p for p in pts[1:-1])
            a, b = _anchor(d, pts[0]), _anchor(d, pts[-1])
            st = EDGE_STYLE
            ref = ''
            if a:
                st += 'exitX=%g;exitY=%g;' % (a[1], a[2]); ref += ' source="%s"' % e(a[0])
            if b:
                st += 'entryX=%g;entryY=%g;entryDx=0;entryDy=0;' % (b[1], b[2])
                ref += ' target="%s"' % e(b[0])
            cell('<mxCell id="e%d_%d" style="%s" edge="1" parent="1"%s>'
                 '<mxGeometry relative="1" as="geometry">'
                 '<mxPoint x="%g" y="%g" as="sourcePoint"/>'
                 '<mxPoint x="%g" y="%g" as="targetPoint"/>'
                 '%s</mxGeometry></mxCell>'
                 % (di, k, st, ref, pts[0][0], pts[0][1], pts[-1][0], pts[-1][1],
                    ('<Array as="points">%s</Array>' % mid) if mid else ''))
        for k, lb in enumerate(d.labels):
            cell('<mxCell id="t%d_%d" value="%s" style="%s" vertex="1" parent="1">'
                 '<mxGeometry x="%g" y="%g" width="40" height="18" as="geometry"/></mxCell>'
                 % (di, k, e(lb['text']), TXT, lb['x'] - 20, lb['y'] - 9))
        out.append('      </root>')
        out.append('    </mxGraphModel>')
        out.append('  </diagram>')
    out.append('</mxfile>')
    open(path, 'w', encoding='utf-8').write('\n'.join(out))
    return path

# ---------------------------------------------------------------- PNG
def wrap(dr, s, fnt, maxw):
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
    O = PAD * S
    X = lambda v: O + v * S
    Y = lambda v: O + v * S
    fn, fh, fl = _f(FONT_N * S), _f(FONT_H * S, True), _f(FONT_L * S)
    if d.lanes:
        dr.rectangle([X(0), Y(0), X(d.W), Y(d.H)], outline='black', width=S)
        for i, ln in enumerate(d.lanes):
            dr.rectangle([X(d.lx(i)), Y(0), X(d.lx(i) + d.lane_w), Y(HDR_H)],
                         outline='black', width=S)
            dr.text((X(d.cx(i)), Y(HDR_H / 2)), ln, font=fh, fill='black', anchor='mm')
            if i:
                dr.line([X(d.lx(i)), Y(HDR_H), X(d.lx(i)), Y(d.H)], fill='black', width=S)
    for ed in d.edges:
        pts = [(X(a), Y(b)) for a, b in ed['pts']]
        for a, b in zip(pts, pts[1:]):
            dr.line([a[0], a[1], b[0], b[1]], fill='black', width=S)
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        a = 7 * S
        if abs(x2 - x1) < 1e-6:
            s_ = 1 if y2 > y1 else -1
            dr.polygon([(x2, y2), (x2 - a * 0.55, y2 - s_ * a), (x2 + a * 0.55, y2 - s_ * a)],
                       fill='black')
        else:
            s_ = 1 if x2 > x1 else -1
            dr.polygon([(x2, y2), (x2 - s_ * a, y2 - a * 0.55), (x2 - s_ * a, y2 + a * 0.55)],
                       fill='black')
    for n in d.nodes.values():
        x0, y0, x1, y1 = X(n['x']), Y(n['y']), X(n['x'] + n['w']), Y(n['y'] + n['h'])
        k = n['kind']
        if k == 'action':
            dr.rounded_rectangle([x0, y0, x1, y1], radius=9 * S, fill='white',
                                 outline='black', width=S)
        elif k == 'decision':
            dr.polygon([((x0 + x1) / 2, y0), (x1, (y0 + y1) / 2),
                        ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2)],
                       fill='white', outline='black')
            dr.line([((x0+x1)/2, y0), (x1, (y0+y1)/2), ((x0+x1)/2, y1), (x0, (y0+y1)/2),
                     ((x0+x1)/2, y0)], fill='black', width=S)
        elif k == 'start':
            dr.ellipse([x0, y0, x1, y1], fill='black', outline='black')
        elif k == 'end':
            dr.ellipse([x0, y0, x1, y1], fill='white', outline='black', width=2 * S)
            m = 6 * S
            dr.ellipse([x0 + m, y0 + m, x1 - m, y1 - m], fill='black')
        elif k == 'bar':
            dr.rectangle([x0, y0, x1, y1], fill='black')
        if n['text']:
            # u rombu je upotrebljiva sirina manja od pune -- tekst se suzava
            maxw = (n['w'] * 0.55 if k == 'decision' else n['w'] - 16) * S
            lines = wrap(dr, n['text'], fn, maxw)
            lh = fn.size * 1.22
            ty = (y0 + y1) / 2 - lh * (len(lines) - 1) / 2
            for i, ln in enumerate(lines):
                dr.text(((x0 + x1) / 2, ty + i * lh), ln, font=fn, fill='black', anchor='mm')
    for lb in d.labels:
        dr.text((X(lb['x']), Y(lb['y'])), lb['text'], font=fl, fill='black', anchor='mm')
    img.save(path)
    return path, img.size
