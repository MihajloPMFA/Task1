# -*- coding: utf-8 -*-
"""PNG pregled PMOV dijagrama (za vizuelnu kontrolu)."""
import sys
from PIL import Image, ImageDraw, ImageFont
import layout
from layout import PAGE_W, PAGE_H

DPI = float(sys.argv[2]) if len(sys.argv) > 2 else 26.0
FP = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FPB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
ORANGE, WHITE, BLACK = '#f59d56', '#ffffff', '#000000'

def main():
    S, L = layout.build_all()
    Wp, Hp = int(PAGE_W*DPI), int(PAGE_H*DPI)
    im = Image.new('RGB', (Wp, Hp), 'white'); dr = ImageDraw.Draw(im)
    X = lambda x: x*DPI
    Y = lambda y: (PAGE_H - y)*DPI
    def fnt(pt, bold=False):
        return ImageFont.truetype(FPB if bold else FP, max(5, int(pt*DPI/72.0)))
    def txt(cx, cy, s, pt, bold=False, ul=False, w=None):
        f = fnt(pt, bold)
        lines = []
        for part in s.split('\n'):
            if w is None: lines.append(part); continue
            cur = ''
            for wd in part.split(' '):
                t = (cur+' '+wd).strip()
                if dr.textlength(t, font=f) <= w*DPI or not cur: cur = t
                else: lines.append(cur); cur = wd
            lines.append(cur)
        lh = f.size*1.12
        y0 = Y(cy) - (len(lines)-1)*lh/2
        for i, ln in enumerate(lines):
            tw = dr.textlength(ln, font=f)
            dr.text((X(cx)-tw/2, y0+i*lh), ln, font=f, fill=BLACK, anchor='lm')
            if ul:
                dr.line([X(cx)-tw/2, y0+i*lh+f.size*0.55, X(cx)+tw/2, y0+i*lh+f.size*0.55],
                        fill=BLACK, width=1)
    for li in L:
        pts = [(X(p[0]), Y(p[1])) for p in li['pts']]
        dr.line(pts, fill=BLACK, width=1)
    for d in S:
        x, y, w, h, t = d['x'], d['y'], d['w'], d['h'], d['t']
        bb = [X(x-w/2), Y(y+h/2), X(x+w/2), Y(y-h/2)]
        if t == 'rect':
            fill = WHITE if d.get('inner') or d.get('sub') else ORANGE
            if d.get('sub'): fill = '#ffe2c4'
            dr.rectangle(bb, outline=BLACK, fill=fill, width=1)
            if d['text']: txt(x, y, d['text'], 9.5, w=w*0.92)
        elif t == 'ellipse':
            if d.get('der'):
                dr.ellipse(bb, outline='#777777', fill=WHITE, width=1)
            else:
                dr.ellipse(bb, outline=BLACK, fill=WHITE, width=1)
            if d.get('mv'):
                k = 0.055*DPI
                dr.ellipse([bb[0]+k, bb[1]+k, bb[2]-k, bb[3]-k], outline=BLACK, width=1)
            txt(x, y, d['text'], 6.6, ul=d.get('pk', False), w=w*0.90)
        elif t in ('diamond', 'sdiamond'):
            pl = [(X(x), Y(y+h/2)), (X(x+w/2), Y(y)), (X(x), Y(y-h/2)), (X(x-w/2), Y(y))]
            dr.polygon(pl, outline=BLACK, fill=WHITE)
            if d['text']: txt(x, y, d['text'], 8.0 if t == 'diamond' else 9.0, w=w*0.80)
        elif t == 'circle':
            dr.ellipse(bb, outline=BLACK, fill=WHITE, width=1)
            if d['text']: txt(x, y, d['text'], 6.5)
        elif t == 'card':
            txt(x, y, d['text'], 6.8)
        elif t == 'title':
            txt(x, y, d['text'], 30, bold=True, w=w)
        elif t == 'subtitle':
            txt(x, y, d['text'], 13, w=w)
        elif t == 'frame':
            dr.rectangle(bb, outline=BLACK, fill='#fdf6ef', width=1)
        elif t == 'legend':
            txt(x, y, d['text'], 12.5, bold=True, w=w)
        elif t == 'leglbl':
            f = fnt(9.8)
            dr.text((X(x-w/2), Y(y)), d['text'], font=f, fill=BLACK, anchor='lm')
        elif t == 'cardbig':
            txt(x, y, d['text'], 9.8)
        elif t == 'bandlbl':
            dr.rectangle(bb, outline='#c8772e', fill='#fdf3e8', width=1)
            txt(x, y, d['text'], 15, bold=True, w=w*0.9)
    im.save(sys.argv[1]); print('saved', sys.argv[1], im.size)

main()
