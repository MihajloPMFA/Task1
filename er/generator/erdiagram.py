# -*- coding: utf-8 -*-
"""Crta kompaktan ER dijagram (.vsdx) iz iste seme iz koje se generise i DDL.
Ne menja sadrzaj: sve 69 tabela, svih 405 kolona i svih 84 veze su prikazani."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vsdx
from vsdx import Page
from schema import TABLES
from areas import AREAS, AREA_OF
from erlayout import (BY, EDGES, box_parts, size_of, build,
                      ROW_H, HDR_H, PAD, F_HDR, F_COL, AREA_COLOR, AR_PAD, AR_TTL)
from route import Router, simplify

B, POS, W, H, GEO, ROWS = build()
TITLE_H = 0.0   # naslov je vec uracunat u H

def side_of(a, b):
    """Strana kutije a okrenuta ka b: 'L','R','T','B'."""
    ax, ay, aw, ah = B[a]; bx, by, bw, bh = B[b]
    dx = (bx + bw / 2) - (ax + aw / 2)
    dy = (by + bh / 2) - (ay + ah / 2)
    if abs(dx) >= abs(dy):
        return 'R' if dx > 0 else 'L'
    return 'T' if dy > 0 else 'B'

# ---- 1. strana za svaki kraj svake veze -----------------------------
ends = []            # (idx_veze, ime_tabele, strana, kljuc_sortiranja)
for k, (ch, pa, ident, nm) in enumerate(EDGES):
    sc, sp = side_of(ch, pa), side_of(pa, ch)
    ends.append((k, ch, sc, pa))
    ends.append((k, pa, sp, ch))

bucket = {}
for k, t, s, other in ends:
    bucket.setdefault((t, s), []).append((k, other))

CELL = 0.07
def snap(v, taken):
    """Poravnaj tacku prikljucka na mrezu rutera da izlazni potez bude
    strogo vodoravan/uspravan; izbegni da dva prikljucka padnu na istu liniju."""
    g = round(v / CELL)
    while g in taken:
        g += 1
    taken.add(g)
    return g * CELL

PORT = {}            # (idx_veze, ime_tabele) -> (x, y, strana)
for (t, s), lst in sorted(bucket.items()):
    x, y, w, h = B[t]
    taken = set()
    if s in 'LR':
        lst.sort(key=lambda e: B[e[1]][1] + B[e[1]][3] / 2)
        n = len(lst)
        for i, (k, _) in enumerate(lst):
            yy = snap(y + h * (i + 1) / (n + 1), taken)
            yy = min(max(yy, y + 0.06), y + h - 0.06)
            PORT[(k, t)] = (x if s == 'L' else x + w, yy, s)
    else:
        lst.sort(key=lambda e: B[e[1]][0] + B[e[1]][2] / 2)
        n = len(lst)
        for i, (k, _) in enumerate(lst):
            xx = snap(x + w * (i + 1) / (n + 1), taken)
            xx = min(max(xx, x + 0.08), x + w - 0.08)
            PORT[(k, t)] = (xx, y if s == 'B' else y + h, s)

# ---- 2. rutiranje ---------------------------------------------------
def route_all(order):
    R = Router(W, H, cell=CELL, inflate=0.030)
    for n, (x, y, w, h) in B.items():
        R.block_rect(x, y, w, h)
    OUT = 0.105
    def stub(px, py, s):
        return {'L': (px - OUT, py), 'R': (px + OUT, py),
                'B': (px, py - OUT), 'T': (px, py + OUT)}[s]
    paths, fails = [], 0
    for k in order:
        ch, pa, ident, nm = EDGES[k]
        p1 = PORT[(k, ch)]; p2 = PORT[(k, pa)]
        c1 = R.to_cell(*stub(*p1)); c2 = R.to_cell(*stub(*p2))
        R.open_cell(*c1); R.open_cell(*c2)
        path = R.route(c1, c2)
        if path is None:
            fails += 1
            pts = [(p1[0], p1[1]), (p2[0], p2[1])]
        else:
            R.mark(path)
            pts = [(p1[0], p1[1])] + [R.to_xy(*c) for c in simplify(path)] + [(p2[0], p2[1])]
        cl = [pts[0]]
        for q in pts[1:]:
            if abs(q[0] - cl[-1][0]) > 1e-9 or abs(q[1] - cl[-1][1]) > 1e-9:
                cl.append(q)
        paths.append((k, cl, ident))
    paths.sort(key=lambda z: z[0])
    return paths, fails

def quality(paths):
    segs = [(p[i], p[i + 1]) for _, p, _ in paths for i in range(len(p) - 1)]
    def hor(s): return abs(s[0][1] - s[1][1]) < 1e-9
    cr = ov = 0
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            a, b = segs[i], segs[j]
            if hor(a) == hor(b):
                if hor(a) and abs(a[0][1] - b[0][1]) < 0.012:
                    lo = max(min(a[0][0], a[1][0]), min(b[0][0], b[1][0]))
                    hi = min(max(a[0][0], a[1][0]), max(b[0][0], b[1][0]))
                    if hi - lo > 0.05: ov += 1
                elif not hor(a) and abs(a[0][0] - b[0][0]) < 0.012:
                    lo = max(min(a[0][1], a[1][1]), min(b[0][1], b[1][1]))
                    hi = min(max(a[0][1], a[1][1]), max(b[0][1], b[1][1]))
                    if hi - lo > 0.05: ov += 1
            else:
                h_, v_ = (a, b) if hor(a) else (b, a)
                if (min(h_[0][0], h_[1][0]) < v_[0][0] < max(h_[0][0], h_[1][0]) and
                        min(v_[0][1], v_[1][1]) < h_[0][1] < max(v_[0][1], v_[1][1])):
                    cr += 1
    tot = sum(abs(p[i+1][0]-p[i][0]) + abs(p[i+1][1]-p[i][1])
              for _, p, _ in paths for i in range(len(p) - 1))
    return cr, ov, tot

def by_len(k):
    return (abs(B[EDGES[k][0]][0] - B[EDGES[k][1]][0])
            + abs(B[EDGES[k][0]][1] - B[EDGES[k][1]][1]))

import random
cands = [sorted(range(len(EDGES)), key=by_len),
         sorted(range(len(EDGES)), key=by_len, reverse=True)]
for sd in (1, 5, 11, 23):
    o = list(range(len(EDGES))); random.Random(sd).shuffle(o); cands.append(o)
best = None
for o in cands:
    pth, fl = route_all(o)
    cr, ov, tot = quality(pth)
    score = cr * 10 + ov * 25 + tot + fl * 1000
    if best is None or score < best[0]:
        best = (score, pth, fl, cr, ov, tot)
score, paths, fails, cr, ov, tot = best
print('rutirano %d veza, neuspelih %d | ukrstanja %d, poklapanja %d, ukupna duzina %.1f in'
      % (len(paths), fails, cr, ov, tot))

# ---- 3. crtanje -----------------------------------------------------
vsdx.set_page(W, H)
p = Page()
GREY, BLACK = '#6b6b6b', '#000000'

# okviri celina
for area, names in AREAS:
    ax, ay = POS[area]
    aw, ah = GEO[area][1], GEO[area][2]
    head, body = AREA_COLOR[area]
    p.box(ax + aw / 2, ay + ah / 2, aw, ah, 'rect', '', fill=body,
          line_w=0.0104, name='Celina')
    p.label(ax + aw / 2, ay + ah - AR_PAD / 2 - AR_TTL / 2, aw - 2 * AR_PAD, AR_TTL,
            area.upper(), size=9.0, style=1, align=1, color='#3a3a3a')

# veze (ispod kutija)
for k, pts, ident in paths:
    p.polyline(pts, weight=0.0069, pattern=1 if ident else 2, color=GREY)
    # tacka na strani deteta (vise-strana)
    px, py, s = PORT[(k, EDGES[k][0])]
    d = 0.045
    cx = px + (d if s == 'L' else -d if s == 'R' else 0)
    cy = py + (d if s == 'B' else -d if s == 'T' else 0)
    p.box(cx, cy, 0.075, 0.075, 'ellipse', '', fill=BLACK, line_w=0.0035, name='Tacka')

# tabele
for name, (x, y, w, h) in B.items():
    t = BY[name]
    head, body = AREA_COLOR[AREA_OF[name]]
    pk, rest = box_parts(t)
    p.box(x + w / 2, y + h / 2, w, h, 'rect', '', fill='#ffffff',
          line_w=0.0104, name='Tabela')
    p.box(x + w / 2, y + h - HDR_H / 2, w, HDR_H, 'rect', t['name'], fill=head,
          size=F_HDR, style=1, line_w=0.0104, name='Zaglavlje', tscale=(0.98, 0.95))
    ysep = y + h - HDR_H - len(pk) * ROW_H
    p.polyline([(x, ysep), (x + w, ysep)], weight=0.0104, name='Crta')
    p.label(x + w / 2 + 0.03, y + h - HDR_H - len(pk) * ROW_H / 2,
            w - 0.12, len(pk) * ROW_H, '\n'.join(pk), size=F_COL, style=0, align=0,
            spline=ROW_H)
    if rest:
        p.label(x + w / 2 + 0.03, ysep - len(rest) * ROW_H / 2,
                w - 0.12, len(rest) * ROW_H, '\n'.join(rest), size=F_COL, style=0, align=0,
                spline=ROW_H)

# naslov
p.label(W / 2, H - 0.34, W - 1.0, 0.40,
        'ER MODEL INFORMACIONOG SISTEMA TV STANICE   —   %d tabela, %d kolona, %d veza'
        % (len(TABLES), sum(len(t['cols']) for t in TABLES), len(EDGES)),
        size=13.0, style=1, align=1, color='#222222')

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'ER_TV_stanica_dijagram.vsdx')
print(vsdx.write(out, p), 'strana %.2f x %.2f in' % (W, H))
