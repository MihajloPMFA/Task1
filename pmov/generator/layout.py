# -*- coding: utf-8 -*-
"""Racuna konkretnu geometriju svih oblika PMOV dijagrama i proverava kolizije."""
from geom import *
from mdl_ent import ENT, ORDER, COMPOSITE
from mdl_rel import REL, SPEC

PAGE_W, PAGE_H = 112.0, 106.0
XOFF = 7.0            # leva margina za nazive funkcionalnih celina
CARD_W, CARD_H = 0.78, 0.30

def build():
    S = []            # oblici: dict(t, x, y, w, h, text, ...)
    L = []            # linije: dict(pts=[(x,y)..], owner=(a,b))
    def sh(t, x, y, w, h, text='', **kw):
        d = dict(t=t, x=x, y=y, w=w, h=h, text=text, **kw); S.append(d); return d
    def ln(pts, a=None, b=None, dash=False):
        L.append(dict(pts=[(round(px,4), round(py,4)) for px, py in pts],
                      owner=(a, b), dash=dash))

    # ---------- entiteti + atributi ----------
    for k in ORDER:
        e = ENT[k]
        x, y, kind = e['x'], e['y'], e['kind']
        if kind == 'weak':
            sh('rect', x, y, EW, EH, '', key=k+'#o')
            sh('rect', x, y, IW, IH, e['name'], key=k, inner=True)
        else:
            sh('rect', x, y, EW, EH, e['name'], key=k, sub=(kind == 'sub'))
        for nm, pos, typ in e['attrs']:
            dx, dy = slot_xy(pos)
            ax, ay = x + dx, y + dy
            sh('ellipse', ax, ay, AW, AH, nm, key=k+':'+nm, pk=(typ in ('pk', 'pd')),
               der=(typ == 'der'), mv=(typ == 'mv'))
            # linija entitet -> atribut (zavrsava na ivici reda atributa)
            if pos.startswith('N') and pos[-1].isdigit():
                sx = min(max(ax, x - EW/2 + 0.12), x + EW/2 - 0.12)
                ln([(sx, y + EH/2), (ax, ay - AH/2)], k, k+':'+nm)
            elif pos.startswith('S') and pos[-1].isdigit():
                sx = min(max(ax, x - EW/2 + 0.12), x + EW/2 - 0.12)
                ln([(sx, y - EH/2), (ax, ay + AH/2)], k, k+':'+nm)
            else:                                    # krilca NW/NE/SW/SE, SL/SR
                if pos in ('SL', 'SR'):
                    sx = min(max(ax, x - EW/2 + 0.12), x + EW/2 - 0.12)
                    ln([(sx, y - EH/2), (ax, ay + AH/2)], k, k+':'+nm)
                else:
                    side = -1 if 'W' in pos else 1
                    ln([(x + side*EW/2, y + (0.22 if 'N' in pos else -0.22)),
                        (ax - side*AW/2, ay)], k, k+':'+nm)
    for ek, par, kids in COMPOSITE:
        e = ENT[ek]
        pos = next(a[1] for a in e['attrs'] if a[0] == par)
        pdx, pdy = slot_xy(pos)
        px, py = e['x'] + pdx, e['y'] + pdy
        for cn, cdx, cdy in kids:
            cx, cy = px + cdx, py + cdy
            sh('ellipse', cx, cy, AW, AH, cn, key=ek+':'+par+':'+cn, comp=True)
            ln([(px, py - AH/2), (cx, cy + AH/2)], ek+':'+par, ek+':'+par+':'+cn)
    return S, L, sh, ln

def port(k, p):
    """Tacka izlaza sa entiteta: p=(strana, ofset)."""
    e = ENT[k]; x, y = e['x'], e['y']; side, off = p
    if side == 'L': return (x - EW/2, y + off)
    if side == 'R': return (x + EW/2, y + off)
    if side == 'T': return (x + off, y + EH/2)
    return (x + off, y - EH/2)

def diamond_vertex(dx, dy, dw, dh, frm):
    """Najblizi vrh romba u odnosu na tacku frm."""
    cands = [(dx - dw/2, dy), (dx + dw/2, dy), (dx, dy + dh/2), (dx, dy - dh/2)]
    fx, fy = frm
    return min(cands, key=lambda c: (c[0]-fx)**2 + (c[1]-fy)**2)

def ortho(p0, ways, vtx):
    """Ortogonalna putanja: p0 -> medjutacke -> vrh romba."""
    pts = [p0]
    for w in ways:
        lx, ly = pts[-1]
        if abs(w[0]-lx) > 1e-6 and abs(w[1]-ly) > 1e-6:
            pts.append((lx, w[1]) if abs(w[1]-ly) > abs(w[0]-lx) else (w[0], ly))
        pts.append(w)
    lx, ly = pts[-1]
    if abs(vtx[0]-lx) > 1e-6 and abs(vtx[1]-ly) > 1e-6:
        pts.append((vtx[0], ly) if abs(vtx[0]-lx) >= abs(vtx[1]-ly) else (lx, vtx[1]))
    pts.append(vtx)
    out = [pts[0]]
    for p in pts[1:]:
        if abs(p[0]-out[-1][0]) > 1e-6 or abs(p[1]-out[-1][1]) > 1e-6: out.append(p)
    return out

def build_all():
    S, L, sh, ln = build()

    # ---------- veze (rombovi) ----------
    for i, r in enumerate(REL):
        dx, dy, dw, dh = r['x'], r['y'], r['w'], r['h']
        rid = 'R%d' % i
        if r['ident']:
            sh('diamond', dx, dy, dw + 0.42, dh + 0.34, '', key=rid+'#o')
        sh('diamond', dx, dy, dw, dh, r['name'], key=rid)
        for side, (ek, card, p, ways) in enumerate(
                ((r['e1'], r['c1'], r['p1'], r['w1']), (r['e2'], r['c2'], r['p2'], r['w2']))):
            p0 = port(ek, p)
            vtx = diamond_vertex(dx, dy, dw, dh, ways[-1] if ways else p0)
            pts = ortho(p0, ways, vtx)
            ln(pts, ek, rid)
            # kardinalnost uz entitet
            q0, q1 = pts[0], pts[1]
            if abs(q1[0]-q0[0]) > abs(q1[1]-q0[1]):
                cx = q0[0] + (1.05 if q1[0] > q0[0] else -1.05); cy = q0[1] + 0.31
            else:
                cx = q0[0] + 0.52; cy = q0[1] + (0.95 if q1[1] > q0[1] else -0.95)
            sh('card', cx, cy, CARD_W, CARD_H, card, key=rid+'c%d' % side)
        # atributi veze (iznad/ispod romba)
        na = len(r['attrs'])
        if na:
            on_band = min(abs(dy-b) for b in (96., 78., 62., 45., 28., 11.)) < 0.6
            sgn = -1 if r.get('ad') == 'S' else 1
            ry = dy + sgn * (4.3 if on_band else dh/2 + 1.05)
            up = sgn > 0
            xs = [dx + (j - (na-1)/2.0) * 2.12 for j in range(na)]
            for nm, axp in zip(r['attrs'], xs):
                sh('ellipse', axp, ry, AW, AH, nm, key=rid+':'+nm)
                ln([(dx, dy + (dh/2 if up else -dh/2)), (axp, ry - AH/2 if up else ry + AH/2)],
                   rid, rid+':'+nm)

    # ---------- specijalizacije ----------
    for j, s in enumerate(SPEC):
        sup = ENT[s['sup']]; x = sup['x']; ytop = sup['y'] - EH/2
        sy = sup['y'] - s['dy']
        sid = 'S%d' % j
        sh('sdiamond', x, sy, SW, SH, 'S', key=sid)
        sh('circle', x, sy - SH/2 - CR - 0.06, 2*CR, 2*CR,
           'd' if s.get('disj', True) else 'o', key=sid+'o')
        if s.get('total', True):
            ln([(x - 0.05, ytop), (x - 0.05, sy + SH/2)], s['sup'], sid)
            ln([(x + 0.05, ytop), (x + 0.05, sy + SH/2)], s['sup'], sid)
        else:
            ln([(x, ytop), (x, sy + SH/2)], s['sup'], sid)
        cy = sy - SH/2 - 2*CR - 0.12
        for sk in s['subs']:
            sb = ENT[sk]
            ln([(x, cy), (sb['x'], sb['y'] + EH/2)], sid+'o', sk)
    add_title(S, L)
    for d in S:
        d['x'] += XOFF
    for li in L:
        li['pts'] = [(px + XOFF, py) for px, py in li['pts']]
    add_bands(S)
    return S, L


BANDS = ((96.0, 'ORGANIZACIJA,\nKADROVI I OPREMA'), (78.0, 'PRODUKCIJA'),
         (62.0, 'EMITOVANJE'), (45.0, 'MARKETING\nI PRODAJA'),
         (28.0, 'NABAVKA'), (11.0, 'FINANSIJSKA\nDOKUMENTACIJA'))

def add_bands(S):
    for y, nm in BANDS:
        S.append(dict(t='bandlbl', x=3.4, y=y, w=6.0, h=1.9, text=nm, key='BL%d' % int(y)))

# ---------------- provera kolizija ----------------
def bbox(d):
    return (d['x']-d['w']/2, d['y']-d['h']/2, d['x']+d['w']/2, d['y']+d['h']/2)

def ov(a, b, pad=0.04):
    return not (a[2] <= b[0]+pad or b[2] <= a[0]+pad or a[3] <= b[1]+pad or b[3] <= a[1]+pad)

def seg_box(p, q, bx, pad=0.03):
    x0, y0, x1, y1 = bx[0]+pad, bx[1]+pad, bx[2]-pad, bx[3]-pad
    if x1 <= x0 or y1 <= y0: return False
    ax, ay = p; bx_, by = q
    # Liang-Barsky
    dx, dy = bx_-ax, by-ay
    t0, t1 = 0.0, 1.0
    for pv, qv in ((-dx, ax-x0), (dx, x1-ax), (-dy, ay-y0), (dy, y1-ay)):
        if abs(pv) < 1e-12:
            if qv < 0: return False
        else:
            t = qv/pv
            if pv < 0:
                if t > t1: return False
                if t > t0: t0 = t
            else:
                if t < t0: return False
                if t < t1: t1 = t
    return t1 > t0 + 1e-6

LEGKINDS = ('title','subtitle','frame','legend','leglbl','cardbig','bandlbl')
def check(S, L):
    probs = []
    real = [d for d in S if d['t'] != 'card' and d['t'] not in LEGKINDS
            and not d.get('key','').startswith('LG')]
    cards = [d for d in S if d['t'] == 'card']
    for i in range(len(real)):
        for j in range(i+1, len(real)):
            a, b = real[i], real[j]
            ka, kb = a.get('key',''), b.get('key','')
            if ka.rstrip('#o') == kb.rstrip('#o') and ka.split('#')[0] == kb.split('#')[0]:
                continue
            if ka == kb: continue
            if ka.endswith('#o') and kb == ka[:-2]: continue
            if kb.endswith('#o') and ka == kb[:-2]: continue
            if a['t'] == 'circle' or b['t'] == 'circle':
                if ka.rstrip('o') == kb or kb.rstrip('o') == ka: continue
            if ov(bbox(a), bbox(b)):
                probs.append(('SHAPE-SHAPE', ka, kb))
    for d in cards:
        for b in real:
            if b.get('key','').startswith(d.get('key','')[:2]) and b['t'] == 'diamond': continue
            if ov(bbox(d), bbox(b), pad=0.02):
                probs.append(('CARD-SHAPE', d.get('key'), b.get('key'), d['text'], b['text'][:20]))
    for li in L:
        a, b = li['owner']
        for d in real:
            k = d.get('key','')
            if k in (a, b) or k.rstrip('#o') in (a, b) or k == (a or '')+'#o' or k == (b or '')+'#o':
                continue
            if k.endswith('#o') and k[:-2] in (a, b): continue
            for p, q in zip(li['pts'], li['pts'][1:]):
                if seg_box(p, q, bbox(d)):
                    probs.append(('LINE-SHAPE', a, b, k, d['text'][:22])); break
    return probs

# ---------------- naslov i legenda ----------------
LEG_X, LEG_Y = 60.0, 103.2          # gornji levi ugao bloka legende
def add_title(S, L):
    def sh(t, x, y, w, h, text='', **kw):
        d = dict(t=t, x=x, y=y, w=w, h=h, text=text, **kw); S.append(d); return d
    def ln(pts):
        L.append(dict(pts=[(round(a,4), round(b,4)) for a, b in pts], owner=('LEG','LEG')))
    sh('title', LEG_X + 21.0, LEG_Y - 1.1, 42.0, 2.2,
       'PMOV – PROŠIRENI MODEL OBJEKTI–VEZE\nINFORMACIONI SISTEM TELEVIZIJSKE STANICE', key='TTL')
    sh('subtitle', LEG_X + 21.0, LEG_Y - 3.1, 42.0, 1.4,
       'Izvedeno iz DFD (DFD_16_09_2026__v12) i IDEF0 (IDEF0_16_09_2026__v11) modela\n'
       'Obuhvat: emitovanje, produkcija, marketing i prodaja, nabavka, administracija',
       key='STL')
    # okvir legende
    bx, by, bw, bh = LEG_X + 21.0, LEG_Y - 11.4, 42.0, 8.6
    sh('frame', bx, by, bw, bh, '', key='LEGF')
    sh('legend', bx, by + bh/2 - 0.55, bw, 0.7, 'LEGENDA  (sintaksa PMOV notacije)', key='LEGT')
    col = [LEG_X + 1.4, LEG_X + 15.2, LEG_X + 29.0]
    row = [by + bh/2 - 2.0, by + bh/2 - 3.3, by + bh/2 - 4.6,
           by + bh/2 - 5.9, by + bh/2 - 7.2]
    def item(c, r, kind, label):
        x, y = col[c], row[r]
        if kind == 'ent':   sh('rect', x, y, 1.5, 0.66, '', key='LG%s%d%d' % (kind, c, r))
        elif kind == 'weak':
            sh('rect', x, y, 1.5, 0.66, '', key='LGw1%d%d' % (c, r))
            sh('rect', x, y, 1.26, 0.42, '', key='LGw2%d%d' % (c, r), inner=True)
        elif kind == 'sub': sh('rect', x, y, 1.5, 0.66, '', key='LGs%d%d' % (c, r), sub=True)
        elif kind == 'rel': sh('diamond', x, y, 1.6, 0.66, '', key='LGr%d%d' % (c, r))
        elif kind == 'irel':
            sh('diamond', x, y, 1.9, 0.88, '', key='LGi1%d%d' % (c, r))
            sh('diamond', x, y, 1.6, 0.66, '', key='LGi2%d%d' % (c, r))
        elif kind == 'attr': sh('ellipse', x, y, 1.5, 0.52, '', key='LGa%d%d' % (c, r))
        elif kind == 'key':  sh('ellipse', x, y, 1.5, 0.52, 'KLJUČ', key='LGk%d%d' % (c, r), pk=True)
        elif kind == 'der':  sh('ellipse', x, y, 1.5, 0.52, '', key='LGd%d%d' % (c, r), der=True)
        elif kind == 'spec':
            sh('sdiamond', x - 0.4, y, 0.62, 0.44, 'S', key='LGp%d%d' % (c, r))
            sh('circle', x + 0.35, y, 0.26, 0.26, 'd', key='LGpc%d%d' % (c, r))
            ln([(x - 0.09, y), (x + 0.22, y)])
        elif kind == 'spec2':
            sh('sdiamond', x - 0.4, y, 0.62, 0.44, 'S', key='LGq%d%d' % (c, r))
            sh('circle', x + 0.35, y, 0.26, 0.26, 'o', key='LGqc%d%d' % (c, r))
            ln([(x - 0.09, y), (x + 0.22, y)])
            ln([(x - 0.86, y + 0.05), (x - 0.71, y + 0.05)])
            ln([(x - 0.86, y - 0.05), (x - 0.71, y - 0.05)])
        elif kind == 'mv':
            sh('ellipse', x, y, 1.5, 0.52, '', key='LGm%d%d' % (c, r), mv=True)
        elif kind == 'comp':
            sh('ellipse', x - 0.45, y + 0.13, 1.1, 0.4, '', key='LGz%d%d' % (c, r))
            sh('ellipse', x + 0.62, y + 0.26, 0.7, 0.26, '', key='LGz1%d%d' % (c, r))
            sh('ellipse', x + 0.62, y - 0.10, 0.7, 0.26, '', key='LGz2%d%d' % (c, r))
            ln([(x + 0.10, y + 0.16), (x + 0.27, y + 0.26)])
            ln([(x + 0.10, y + 0.08), (x + 0.27, y - 0.10)])
        elif kind == 'card': sh('cardbig', x, y, 1.5, 0.52, '(min, max)', key='LGc%d%d' % (c, r))
        elif kind == 'ent2':
            sh('rect', x, y, 1.5, 0.66, '', key='LGe2%d%d' % (c, r))
            sh('ellipse', x + 0.05, y, 0.9, 0.34, '', key='LGe2a%d%d' % (c, r), pk=True)
        elif kind == 'rel2':
            sh('diamond', x - 0.25, y, 1.25, 0.6, '', key='LGr2%d%d' % (c, r))
            sh('ellipse', x + 0.72, y, 0.8, 0.34, '', key='LGr2a%d%d' % (c, r))
            ln([(x + 0.38, y), (x + 0.32, y)])
        sh('leglbl', x + 1.05 + 5.3, y, 10.6, 0.5, label, key='LGL%s%d%d' % (kind, c, r))
    item(0, 0, 'ent',  'entitet')
    item(0, 1, 'weak', 'slab entitet')
    item(0, 2, 'sub',  'podtip (specijalizacija)')
    item(1, 0, 'rel',  'veza (odnos)')
    item(1, 1, 'irel', 'identifikujuća veza')
    item(1, 2, 'spec', 'parcijalna specijalizacija, disjunktna „d\u201c')
    item(2, 0, 'attr', 'atribut')
    item(2, 1, 'key',  'primarni / parcijalni ključ')
    item(2, 2, 'der',  'izvedeni (izračunati) atribut')
    item(2, 3, 'mv',   'višeznačni atribut')
    item(2, 4, 'comp', 'kompozitni (složeni) atribut')
    item(0, 3, 'ent2', 'jaki entitet nosi primarni ključ')
    item(0, 4, 'card', 'kardinalnost veze (min, max)')
    item(1, 3, 'rel2', 'veza sa sopstvenim atributima')
    item(1, 4, 'spec2','totalna (dvostruka linija) / preklapajuća „o\u201c')
