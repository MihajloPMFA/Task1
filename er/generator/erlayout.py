# -*- coding: utf-8 -*-
"""Raspored ER dijagrama: kompaktne kutije po tematskim celinama,
ortogonalno rutiranje veza sa razdvojenim trakama.  Sadrzaj se ne menja -
sve 69 tabela, svih 405 kolona i svih 84 veze su na dijagramu."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import TABLES
from areas import AREAS, AREA_OF

BY = {t['name']: t for t in TABLES}

# ---------------------------------------------------------------- mere (inci)
ROW_H   = 0.098      # visina jednog reda kolone
HDR_H   = 0.190      # traka sa imenom tabele
PAD     = 0.050      # donja margina u kutiji
F_HDR   = 6.6        # pt, ime tabele
F_COL   = 5.6        # pt, kolone
CW      = 0.0455     # priblizna sirina znaka na F_COL
CW_HDR  = 0.0560     # priblizna sirina znaka na F_HDR (bold)
GAP_X   = 0.62       # razmak izmedju kolona kutija (koridor za veze)
GAP_Y   = 0.42       # razmak izmedju kutija u koloni
AR_PAD  = 0.26       # margina unutar okvira celine
AR_TTL  = 0.30       # visina naslova celine
AR_GAP_X, AR_GAP_Y = 1.15, 0.95   # razmak izmedju celina

AREA_COLS = {'Organizacija i kadrovi': 2, 'Oprema': 2, 'Produkcija': 2,
             'Program i emitovanje': 4, 'Marketing i prodaja': 3,
             'Nabavka': 4, 'Finansije': 1}

AREA_COLOR = {
 'Organizacija i kadrovi': ('#cfe0f2', '#eff5fc'),
 'Oprema':                 ('#d3e8d3', '#f0f7f0'),
 'Produkcija':             ('#f5dfc6', '#fdf4ea'),
 'Program i emitovanje':   ('#e0d2ee', '#f5f0fa'),
 'Marketing i prodaja':    ('#f7d6d6', '#fdf1f1'),
 'Nabavka':                ('#cfe8ee', '#eef8fa'),
 'Finansije':              ('#e8e3cd', '#f8f6ec'),
}

# ---------------------------------------------------------------- tekst kutije
def col_text(t, c):
    fk = any(c['n'] in f['child'] for f in t['fks'])
    return c['n'] + (' (FK)' if fk else '')

def box_parts(t):
    pk = [col_text(t, c) for c in t['cols'] if c['n'] in t['pk']]
    rest = [col_text(t, c) for c in t['cols'] if c['n'] not in t['pk']]
    return pk, rest

def box_size(t):
    pk, rest = box_parts(t)
    n = len(pk) + len(rest)
    w_txt = max([len(s) for s in pk + rest] or [0]) * CW + 0.16
    w_hdr = len(t['name']) * CW_HDR + 0.14
    return max(w_txt, w_hdr), HDR_H + n * ROW_H + PAD + 0.02

BW = max(box_size(t)[0] for t in TABLES)          # jedinstvena sirina kutije

def size_of(t):
    return BW, box_size(t)[1]

# ---------------------------------------------------------------- veze
EDGES = []      # (dete, roditelj, identifikujuca?)
for t in TABLES:
    for f in t['fks']:
        ident = all(cc in t['pk'] for cc in f['child'])
        EDGES.append((t['name'], f['parent'], ident, f['name']))

DEG = {}
for a, b, _, _ in EDGES:
    DEG[a] = DEG.get(a, 0) + 1
    DEG[b] = DEG.get(b, 0) + 1

NB = {}
for a, b, _, _ in EDGES:
    NB.setdefault(a, set()).add(b)
    NB.setdefault(b, set()).add(a)

# ---------------------------------------------------------------- raspored
def pack_area(names, ncols):
    """Rasporedi tabele u ncols kolona tako da su kolone priblizno iste visine.
    Vraca listu kolona (liste imena)."""
    cols = [[] for _ in range(ncols)]
    hts = [0.0] * ncols
    for n in names:                                 # redosled iz areas.py
        k = min(range(ncols), key=lambda i: hts[i])
        cols[k].append(n)
        hts[k] += size_of(BY[n])[1] + GAP_Y
    return cols

def area_geometry(area, names, cols=None):
    if cols is None:
        cols = pack_area(names, AREA_COLS[area])
    w = len(cols) * BW + (len(cols) - 1) * GAP_X + 2 * AR_PAD
    h = max(sum(size_of(BY[n])[1] for n in c) + (len(c) - 1) * GAP_Y
            for c in cols) + 2 * AR_PAD + AR_TTL
    return cols, w, h




# ====================================================================
#  RASPORED: (1) redosled celina na strani, (2) raspored tabela u celini
#  Oba se biraju minimizacijom ukupne duzine veza - sadrzaj se ne menja.
# ====================================================================
import random

MARGIN, TITLE_H = 0.45, 0.62

def arrange(rows, colmap):
    """rows: [[imena celina], ...] odozgo nadole; colmap: celina -> [[tabele], ...].
    Vraca (POS, W, H, GEO) gde je POS[celina] donji levi ugao bloka."""
    GEO = {a: area_geometry(a, None, colmap[a]) for r in rows for a in r}
    rw = [sum(GEO[a][1] for a in r) + AR_GAP_X * (len(r) - 1) for r in rows]
    rh = [max(GEO[a][2] for a in r) for r in rows]
    W = max(rw) + 2 * MARGIN
    H = sum(rh) + AR_GAP_Y * (len(rows) - 1) + 2 * MARGIN + TITLE_H
    POS = {}
    ytop = MARGIN + sum(rh) + AR_GAP_Y * (len(rows) - 1)
    for r, hh in zip(rows, rh):
        x = MARGIN
        for a in r:
            POS[a] = (x, ytop - GEO[a][2])
            x += GEO[a][1] + AR_GAP_X
        ytop -= hh + AR_GAP_Y
    return POS, W, H, GEO

def boxes_for(rows, colmap):
    POS, W, H, GEO = arrange(rows, colmap)
    B = {}
    for a in [x for r in rows for x in r]:
        cols, aw, ah = GEO[a]
        ax, ay = POS[a]
        top = ay + ah - AR_PAD - AR_TTL
        for ci, cn in enumerate(cols):
            cx = ax + AR_PAD + ci * (BW + GAP_X)
            y = top
            for n in cn:
                bh = size_of(BY[n])[1]
                y -= bh
                B[n] = (cx, y, BW, bh)
                y -= GAP_Y
    return B, POS, W, H, GEO

def imbalance(colmap):
    """Razlika najvise i najnize kolone unutar celine - manja razlika = manje
    praznog prostora u okviru."""
    tot = 0.0
    for a, cols in colmap.items():
        hs = [sum(size_of(BY[n])[1] for n in c) + GAP_Y * (len(c) - 1) for c in cols if c]
        if hs:
            tot += max(hs) - min(hs)
    return tot

def edge_cost(B):
    s = 0.0
    for ch, pa, _, _ in EDGES:
        x1, y1, w1, h1 = B[ch]; x2, y2, w2, h2 = B[pa]
        s += abs((x1 + w1 / 2) - (x2 + w2 / 2)) + abs((y1 + h1 / 2) - (y2 + h2 / 2))
    return s

def best_area_order(colmap, splits=((4, 3), (3, 4), (5, 2))):
    """Proba sve rasporede celina u dva reda i bira najkraci ukupan razvod."""
    import itertools
    names = [a for a, _ in AREAS]
    best = None
    for k, _ in splits:
        for combo in itertools.combinations(names, k):
            rest = [n for n in names if n not in combo]
            for p1 in itertools.permutations(combo):
                for p2 in itertools.permutations(rest):
                    rows = [list(p1), list(p2)]
                    B, POS, W, H, GEO = boxes_for(rows, colmap)
                    ar = W / H
                    pen = 0.0 if 1.45 <= ar <= 2.05 else 900 * min(abs(ar - 1.45), abs(ar - 2.05))
                    c = edge_cost(B) + pen + 0.9 * W * H
                    if best is None or c < best[0]:
                        best = (c, rows)
    return best[1]

def anneal(rows, colmap, iters=26000, seed=7):
    """Premesta tabele unutar svoje celine da skrati veze. Nista se ne brise."""
    rnd = random.Random(seed)
    cur = {a: [list(c) for c in cs] for a, cs in colmap.items()}
    def cost(cm):
        B, POS, W, H, GEO = boxes_for(rows, cm)
        return edge_cost(B) + 1.1 * W * H + 0.35 * imbalance(cm), (W, H)
    c0, _ = cost(cur)
    best, cbest = {a: [list(c) for c in cs] for a, cs in cur.items()}, c0
    areas = [a for a, _ in AREAS if sum(len(c) for c in cur[a]) > 1]
    T0, T1 = 3.0, 0.05
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        a = rnd.choice(areas)
        cand = {k: [list(c) for c in v] for k, v in cur.items()}
        cs = cand[a]
        if len(cs) > 1 and rnd.random() < 0.5:
            i, j = rnd.sample(range(len(cs)), 2)
            if not cs[i]:
                continue
            t = cs[i].pop(rnd.randrange(len(cs[i])))
            cs[j].insert(rnd.randrange(len(cs[j]) + 1), t)
            if not cs[i]:
                cs[i].append(cs[j].pop())
        else:
            flat = [(ci, k) for ci, c in enumerate(cs) for k in range(len(c))]
            if len(flat) < 2:
                continue
            (c1, k1), (c2, k2) = rnd.sample(flat, 2)
            cs[c1][k1], cs[c2][k2] = cs[c2][k2], cs[c1][k1]
        c1_, _ = cost(cand)
        if c1_ < c0 or rnd.random() < math.exp((c0 - c1_) / max(T, 1e-6)):
            cur, c0 = cand, c1_
            if c0 < cbest:
                cbest, best = c0, {k: [list(c) for c in v] for k, v in cur.items()}
    return best, cbest

def build(verbose=True, seeds=(7, 17, 29, 41)):
    colmap0 = {a: pack_area(ns, AREA_COLS[a]) for a, ns in AREAS}
    rows = best_area_order(colmap0)
    if verbose:
        print('raspored celina:', ' | '.join(' + '.join(r) for r in rows))
    best = None
    for sd in seeds:
        cm, c = anneal(rows, colmap0, iters=18000, seed=sd)
        if best is None or c < best[1]:
            best = (cm, c)
        if verbose:
            print('   seme %2d -> cena %.1f' % (sd, c))
    colmap, c = best
    B, POS, W, H, GEO = boxes_for(rows, colmap)
    if verbose:
        print('ukupna duzina veza (Menhetn): %.1f in | neravnomernost kolona %.2f in'
              ' | strana %.2f x %.2f in' % (edge_cost(B), imbalance(colmap), W, H))
    return B, POS, W, H, GEO, rows

if __name__ == '__main__':
    print('sirina kutije: %.3f in, veza %d' % (BW, len(EDGES)))
    B, POS, W, H, GEO, rows = build()
    it = list(B.items())
    ov = sum(1 for i in range(len(it)) for j in range(i + 1, len(it))
             if it[i][1][0] < it[j][1][0] + it[j][1][2] and it[j][1][0] < it[i][1][0] + it[i][1][2]
             and it[i][1][1] < it[j][1][1] + it[j][1][3] and it[j][1][1] < it[i][1][1] + it[i][1][3])
    print('tabela: %d, preklapanja: %d' % (len(B), ov))
