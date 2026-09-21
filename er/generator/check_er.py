# -*- coding: utf-8 -*-
"""Nezavisna provera kvaliteta dijagrama: cita gotov .vsdx i meri
prolaske linija kroz kutije, poklapanja linija i ukrstanja."""
import sys, zipfile, xml.etree.ElementTree as ET
NS = {'v': 'http://schemas.microsoft.com/office/visio/2012/main'}

def load(src):
    z = zipfile.ZipFile(src)
    root = ET.fromstring(z.read('visio/pages/page1.xml'))
    boxes, segs = [], []
    for sh in root.find('v:Shapes', NS).findall('v:Shape', NS):
        c = {x.get('N'): x.get('V') for x in sh.findall('v:Cell', NS)}
        nm = sh.get('NameU', '')
        if c.get('ObjType') == '2':
            bx, by = float(c['BeginX']), float(c['BeginY'])
            pts = []
            for r in sh.findall('v:Section[@N="Geometry"]/v:Row', NS):
                q = {x.get('N'): x.get('V') for x in r.findall('v:Cell', NS)}
                pts.append((bx + float(q['X']), by + float(q['Y'])))
            if len(pts) >= 2 and nm.startswith('Veza'):
                segs.append(pts)
        elif nm.startswith('Tabela'):
            w, h = float(c['Width']), float(c['Height'])
            boxes.append((float(c['PinX']) - w / 2, float(c['PinY']) - h / 2, w, h))
    return boxes, segs

def seg_box(a, b, r, tol=0.02):
    x0, y0, w, h = r
    x0 += tol; y0 += tol; w -= 2 * tol; h -= 2 * tol
    if w <= 0 or h <= 0: return False
    ax, ay = a; bx, by = b
    t0, t1 = 0.0, 1.0
    for p, q in ((-(bx - ax), ax - x0), (bx - ax, x0 + w - ax),
                 (-(by - ay), ay - y0), (by - ay, y0 + h - ay)):
        if p == 0:
            if q < 0: return False
        else:
            t = q / p
            if p < 0:
                if t > t1: return False
                t0 = max(t0, t)
            else:
                if t < t0: return False
                t1 = min(t1, t)
    return t0 < t1

def overlap(s1, s2, tol=0.012):
    """Dva ortogonalna segmenta se poklapaju (idu jedan preko drugog)."""
    (a1, b1), (a2, b2) = s1, s2
    hor1 = abs(a1[1] - b1[1]) < 1e-6; hor2 = abs(a2[1] - b2[1]) < 1e-6
    if hor1 != hor2: return 0.0
    if hor1:
        if abs(a1[1] - a2[1]) > tol: return 0.0
        lo = max(min(a1[0], b1[0]), min(a2[0], b2[0]))
        hi = min(max(a1[0], b1[0]), max(a2[0], b2[0]))
    else:
        if abs(a1[0] - a2[0]) > tol: return 0.0
        lo = max(min(a1[1], b1[1]), min(a2[1], b2[1]))
        hi = min(max(a1[1], b1[1]), max(a2[1], b2[1]))
    return max(0.0, hi - lo)

def crosses(s1, s2):
    (a1, b1), (a2, b2) = s1, s2
    h1 = abs(a1[1] - b1[1]) < 1e-6; h2 = abs(a2[1] - b2[1]) < 1e-6
    if h1 == h2: return False
    (hx0, hx1, hy), (vx, vy0, vy1) = (
        (min(a1[0], b1[0]), max(a1[0], b1[0]), a1[1]), (a2[0], min(a2[1], b2[1]), max(a2[1], b2[1]))
    ) if h1 else (
        (min(a2[0], b2[0]), max(a2[0], b2[0]), a2[1]), (a1[0], min(a1[1], b1[1]), max(a1[1], b1[1]))
    )
    return hx0 + 1e-9 < vx < hx1 - 1e-9 and vy0 + 1e-9 < hy < vy1 - 1e-9

def report(src):
    boxes, polys = load(src)
    segs = [(p[i], p[i + 1]) for p in polys for i in range(len(p) - 1)]
    thru = 0
    for a, b in segs:
        for r in boxes:
            if seg_box(a, b, r):
                thru += 1
                break
    ov = ovlen = 0
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            L = overlap(segs[i], segs[j])
            if L > 0.05:
                ov += 1; ovlen += L
    cr = sum(1 for i in range(len(segs)) for j in range(i + 1, len(segs))
             if crosses(segs[i], segs[j]))
    print('tabela: %d | veza: %d | segmenata: %d' % (len(boxes), len(polys), len(segs)))
    print('segmenata koji prolaze kroz kutiju: %d' % thru)
    print('parova linija koje se poklapaju (>0.05in): %d, ukupna duzina %.2f in' % (ov, ovlen))
    print('ukrstanja linija: %d' % cr)
    return thru, ov, cr

if __name__ == '__main__':
    report(sys.argv[1])
