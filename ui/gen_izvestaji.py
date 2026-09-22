# -*- coding: utf-8 -*-
"""Generise ui/izvestaji.html -- tri izvestaja u istom dizajn sistemu kao forme.
Grafikoni su inline SVG sa unapred izracunatim koordinatama (bez JS biblioteka).

Paleta je proverena skriptom validate_palette.js nad podlogom #ffffff:
  kategorijalno  #2a78d6 (plava), #eb6834 (narandzasta)  -> sve provere PASS
  divergentno    #2a78d6 <-> #e34948, neutralna sredina  -> sve provere PASS
Pravila: jedna osa, tanke marke, 4px zaobljen kraj podatka, 2px razmak u boji
podloge izmedju segmenata, legenda za >=2 serije, tekst nikad u boji serije.
"""
import os, math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'izvestaji.html')

BLUE, ORANGE, RED = '#2a78d6', '#eb6834', '#e34948'
INK, INK2, INK3 = '#0f172a', '#4a5a70', '#8595ab'
GRID, AXIS, SURF = '#e9edf3', '#d3dbe6', '#ffffff'
F = lambda v: ('%.2f' % v).rstrip('0').rstrip('.')

def money(v, dec=0):
    s = ('%.*f' % (dec, v)).replace('.', ',')
    i, _, d = s.partition(',')
    neg = i.startswith('-'); i = i.lstrip('-')
    i = '.'.join([i[max(0, k-3):k] for k in range(len(i), 0, -3)][::-1])
    return ('-' if neg else '') + i + ((',' + d) if d else '')

# ---------------------------------------------------------------- oblici
def bar_up(x, y, w, h, r=4):
    """Stub od osnovice nagore: zaobljen vrh, ravno dno."""
    r = min(r, w / 2, h)
    return ('M%s,%s V%s Q%s,%s %s,%s H%s Q%s,%s %s,%s V%s Z'
            % (F(x), F(y + h), F(y + r), F(x), F(y), F(x + r), F(y),
               F(x + w - r), F(x + w), F(y), F(x + w), F(y + r), F(y + h)))

def bar_flat(x, y, w, h):
    return 'M%s,%s h%s v%s h-%s Z' % (F(x), F(y), F(w), F(h), F(w))

def bar_right(x, y, w, h, r=4):
    """Traka udesno: zaobljen desni kraj, ravan levi."""
    r = min(r, h / 2, w)
    return ('M%s,%s H%s Q%s,%s %s,%s V%s Q%s,%s %s,%s H%s Z'
            % (F(x), F(y), F(x + w - r), F(x + w), F(y), F(x + w), F(y + r),
               F(y + h - r), F(x + w), F(y + h), F(x + w - r), F(y + h), F(x)))

def bar_left(x, y, w, h, r=4):
    """Traka ulevo od osnovice na x: zaobljen levi kraj."""
    r = min(r, h / 2, w)
    return ('M%s,%s H%s Q%s,%s %s,%s V%s Q%s,%s %s,%s H%s Z'
            % (F(x), F(y), F(x - w + r), F(x - w), F(y), F(x - w), F(y + r),
               F(y + h - r), F(x - w), F(y + h), F(x - w + r), F(y + h), F(x)))

def txt(x, y, s, size=11, fill=INK3, anchor='middle', weight=400, tab=True):
    return ('<text x="%s" y="%s" font-size="%s" fill="%s" text-anchor="%s" '
            'font-weight="%d"%s>%s</text>'
            % (F(x), F(y), size, fill, anchor, weight,
               ' style="font-variant-numeric:tabular-nums"' if tab else '', s))

# ---------------------------------------------------------------- 1: linija
REJTING = [5.6,5.9,6.1,6.4,7.3,7.6,5.8,6.0,5.7,6.2,6.6,7.5,7.9,6.1,6.3,
           6.0,6.5,6.8,7.7,8.1,6.2,6.4,6.1,6.6,6.9,7.8,8.0,6.3,6.5,6.4]
PROSEK = sum(REJTING) / len(REJTING)

def chart_line(W=664, H=248):
    L, R, T, B = 40, 52, 16, 30
    x0, x1, y0, y1 = L, W - R, T, H - B
    vmin, vmax = 4.0, 9.0
    sx = lambda i: x0 + (x1 - x0) * i / (len(REJTING) - 1)
    sy = lambda v: y1 - (y1 - y0) * (v - vmin) / (vmax - vmin)
    g = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
         'aria-label="Prosecan rejting po danu">' % (W, H, W, H)]
    for v in (4, 5, 6, 7, 8, 9):
        g.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
                 % (F(x0), F(sy(v)), F(x1), F(sy(v)), GRID))
        g.append(txt(x0 - 10, sy(v) + 4, F(v), 10.5, INK3, 'end'))
    g.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
             % (F(x0), F(y1), F(x1), F(y1), AXIS))
    pts = [(sx(i), sy(v)) for i, v in enumerate(REJTING)]
    d = 'M' + ' L'.join('%s,%s' % (F(a), F(b)) for a, b in pts)
    g.append('<path d="%s L%s,%s L%s,%s Z" fill="%s" opacity="0.10"/>'
             % (d, F(pts[-1][0]), F(y1), F(pts[0][0]), F(y1), BLUE))
    g.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (d, BLUE))
    g.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1" '
             'stroke-dasharray="none" opacity=".55"/>'
             % (F(x0), F(sy(PROSEK)), F(x1), F(sy(PROSEK)), INK3))
    g.append(txt(x0 + 5, sy(PROSEK) - 6, 'prosek %s' % F(round(PROSEK, 1)).replace('.', ','),
                 10, INK3, 'start'))
    for day in (1, 5, 10, 15, 20, 25, 30):
        g.append(txt(sx(day - 1), y1 + 17, '%d.09.' % day, 10.5, INK3))
    # selektivne oznake: maksimum, minimum i poslednja tacka
    imax = REJTING.index(max(REJTING)); imin = REJTING.index(min(REJTING))
    for i, dy, anc in ((imax, -12, 'middle'), (imin, 18, 'middle'), (len(REJTING) - 1, -12, 'end')):
        g.append('<circle cx="%s" cy="%s" r="4.5" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (F(sx(i)), F(sy(REJTING[i])), BLUE, SURF))
        g.append(txt(sx(i) + (4 if anc == 'end' else 0), sy(REJTING[i]) + dy,
                     F(REJTING[i]).replace('.', ','), 11, INK, anc, 700))
    g.append('</svg>')
    return '\n'.join(g)

# ---------------------------------------------------------------- 1: trake
TOP = [('Dnevnik u 19', 9.4), ('Panorama magazin', 7.8), ('Sportski žurnal', 7.1),
       ('Reke Vojvodine', 6.9), ('Kulturni pregled', 6.2), ('Jutarnji program', 5.8),
       ('Dečije carstvo', 5.1), ('Oko', 4.6)]

def chart_bars(W=406, H=248):
    L, R, T = 132, 40, 6
    row = (H - T - 6) / len(TOP)
    bh = min(18, row - 8)
    vmax = 10.0
    g = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
         'aria-label="Prosecan rejting po emisiji">' % (W, H, W, H)]
    for k, (name, v) in enumerate(TOP):
        y = T + row * k + (row - bh) / 2
        w = (W - L - R) * v / vmax
        g.append('<path class="mk" d="%s" fill="%s"/>' % (bar_right(L, y, w, bh), BLUE))
        g.append(txt(L - 9, y + bh / 2 + 4, name, 11, INK2, 'end', 400, False))
        g.append(txt(L + w + 8, y + bh / 2 + 4, F(v).replace('.', ','), 11, INK, 'start', 700))
    g.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
             % (F(L), F(T), F(L), F(H - 6), AXIS))
    g.append('</svg>')
    return '\n'.join(g)

# ---------------------------------------------------------------- 2: stubovi
MES = ['Jan','Feb','Mar','Apr','Maj','Jun','Jul','Avg','Sep','Okt','Nov','Dec']
NAPL = [4.9,5.2,6.1,5.8,6.4,5.1,4.2,4.0,6.8,7.4,7.9,7.4]
DUG  = [0.5,0.4,0.6,0.8,0.7,0.9,0.8,1.0,1.1,1.4,2.0,3.24]

def chart_cols(W=664, H=262):
    L, R, T, B = 46, 14, 18, 32
    x0, x1, y0, y1 = L, W - R, T, H - B
    vmax = 11.0
    band = (x1 - x0) / len(MES)
    bw = min(24, band - 12)
    sy = lambda v: y1 - (y1 - y0) * v / vmax
    g = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
         'aria-label="Fakturisano po mesecima">' % (W, H, W, H)]
    for v in (0, 2, 4, 6, 8, 10):
        g.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
                 % (F(x0), F(sy(v)), F(x1), F(sy(v)), GRID if v else AXIS))
        g.append(txt(x0 - 10, sy(v) + 4, '%d' % v, 10.5, INK3, 'end'))
    tot = [NAPL[i] + DUG[i] for i in range(12)]
    imax = tot.index(max(tot))
    for k in range(12):
        cx = x0 + band * k + band / 2 - bw / 2
        hn, hd = (y1 - sy(NAPL[k])), (sy(NAPL[k]) - sy(NAPL[k] + DUG[k]))
        g.append('<path class="mk" d="%s" fill="%s"/>'
                 % (bar_flat(cx, sy(NAPL[k]), bw, hn), BLUE))          # donji: ravan
        g.append('<path class="mk" d="%s" fill="%s"/>'
                 % (bar_up(cx, sy(NAPL[k] + DUG[k]), bw, max(hd - 2, 1)), ORANGE))  # 2px razmak
        g.append(txt(cx + bw / 2, y1 + 17, MES[k], 10.5, INK3))
        if k == imax:
            g.append(txt(cx + bw / 2, sy(tot[k]) - 8, money(tot[k], 1), 11, INK, 'middle', 700))
    g.append('</svg>')
    return '\n'.join(g)

# ---------------------------------------------------------------- 3: divergentno
ODST = [('Snimateljska oprema', 12.4), ('Studijska i emisiona oprema', -8.1),
        ('Potrošni materijal', 3.6), ('Usluge servisa', -21.5),
        ('Licence i prava emitovanja', 6.2), ('Kancelarijski materijal', -4.8)]

def chart_div(W=640, H=228):
    L, R, T, LBL = 196, 40, 6, 58          # LBL = rezervisano za oznaku vrednosti
    row = (H - T - 10) / len(ODST)
    bh = min(18, row - 8)
    zero = L + (W - R - L) * 0.45
    pos = [v for _, v in ODST if v > 0] or [1]
    neg = [-v for _, v in ODST if v < 0] or [1]
    scale = min((zero - L - LBL) / max(neg), (W - R - zero - LBL) / max(pos))
    g = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
         'aria-label="Odstupanje realizacije od plana">' % (W, H, W, H)]
    for k, (name, v) in enumerate(ODST):
        y = T + row * k + (row - bh) / 2
        w = abs(v) * scale
        lab = ('+' if v > 0 else '\u2212') + F(abs(v)).replace('.', ',') + '%'
        if v >= 0:
            g.append('<path class="mk" d="%s" fill="%s"/>' % (bar_right(zero + 1, y, w, bh), RED))
            g.append(txt(zero + w + 9, y + bh / 2 + 4, lab, 11, INK, 'start', 700))
        else:
            g.append('<path class="mk" d="%s" fill="%s"/>' % (bar_left(zero - 1, y, w, bh), BLUE))
            g.append(txt(zero - w - 9, y + bh / 2 + 4, lab, 11, INK, 'end', 700))
        g.append(txt(L - 12, y + bh / 2 + 4, name, 11, INK2, 'end', 400, False))
    g.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
             % (F(zero), F(T), F(zero), F(H - 10), '#9aa7b8'))
    g.append(txt(zero, H - 0.5, 'plan', 10, INK3))
    g.append('</svg>')
    return '\n'.join(g)

# ================================================================ sablon
def side(active):
    items = [('Kontrolna tabla', '<rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/>'),
             ('Produkcija', '<rect x="2" y="6" width="14" height="12" rx="2"/><path d="M16 10l6-3v10l-6-3"/>'),
             ('Program i emitovanje', '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M8 4v5"/>'),
             ('Marketing i prodaja', '<path d="M3 11l18-7-7 18-2-8-9-3z"/>'),
             ('Nabavka', '<path d="M3 7h18v13H3z"/><path d="M8 7V4h8v3M3 12h18"/>'),
             ('Oprema', '<rect x="3" y="7" width="13" height="10" rx="2"/><circle cx="9.5" cy="12" r="2.6"/><path d="M16 11l5-3v8l-5-3"/>')]
    ana = [('Izveštaji', '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'),
           ('Šifarnici', '<circle cx="12" cy="12" r="3.2"/><path d="M19 12a7 7 0 0 0-.2-1.6l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2.8-1.6L13.4 2h-3.8l-.3 2.9A7 7 0 0 0 6.5 6.5l-2.3-1-2 3.4 2 1.5A7 7 0 0 0 4 12"/>')]
    def links(lst):
        return '\n'.join('<a%s href="#"><svg viewBox="0 0 24 24">%s</svg>%s</a>'
                         % (' class="on"' if n == active else '', ic, n) for n, ic in lst)
    return ('<aside class="side"><div class="brand"><div class="dot">TV</div>'
            '<b>TV Panorama<span>INFORMACIONI SISTEM</span></b></div>'
            '<div class="navlbl">POSLOVANJE</div><nav class="nav">%s</nav>'
            '<div class="navlbl">ANALITIKA</div><nav class="nav">%s</nav></aside>'
            % (links(items), links(ana)))

def top(crumb, ini, ime, uloga):
    return ('<div class="top"><div class="crumb">%s</div><div class="sp"></div>'
            '<div class="search"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/>'
            '<path d="M20 20l-4-4"/></svg>Pretraga…</div>'
            '<div class="who"><div class="av">%s</div><div>%s<small>%s</small></div></div></div>'
            % (crumb, ini, ime, uloga))

def kpi(label, val, note='', tone=''):
    n = ('<div class="dl %s">%s</div>' % (tone, note)) if note else ''
    return '<div class="kpi"><label>%s</label><div class="v">%s</div>%s</div>' % (label, val, n)

def sel(t):
    return ('<div class="inp" style="width:auto">%s<span class="sp"></span>'
            '<svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg></div>' % t)

CSS = """
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);
  padding:15px 18px 16px}
.kpi label{display:block;font-size:11.5px;font-weight:700;color:var(--ink2);margin-bottom:7px}
.kpi .v{font-size:27px;font-weight:700;letter-spacing:-.6px;line-height:1.05}
.kpi .dl{font-size:11.5px;color:var(--ink3);margin-top:6px}
.kpi .dl b{font-weight:700}
.kpi .dl.up b{color:#0b7a44}.kpi .dl.dn b{color:#b52a2a}.kpi .dl.wn b{color:#9a5b00}
.filters{display:flex;align-items:center;gap:10px;background:#fff;border:1px solid var(--line);
  border-radius:var(--r);box-shadow:var(--sh);padding:11px 14px}
.filters .lb{font-size:11.5px;font-weight:700;color:var(--ink2)}
.two{display:grid;grid-template-columns:700px 1fr;gap:16px;align-items:start}
.lg{display:flex;gap:16px;align-items:center;font-size:11.5px;color:var(--ink2)}
.lg span{display:flex;align-items:center;gap:6px}
.lg i{width:10px;height:10px;border-radius:3px;display:block}
.mk{transition:opacity .12s}.mk:hover{opacity:.78}
.chart{padding:14px 18px 10px}
.axlbl{font-size:11px;color:var(--ink3);padding:0 18px 12px}
.mtr{padding:13px 0;border-bottom:1px solid var(--line-soft)}
.mtr:last-child{border-bottom:0}
.mh{display:flex;justify-content:space-between;font-size:12.5px;color:var(--ink2);margin-bottom:8px}
.mh b{color:var(--ink);font-variant-numeric:tabular-nums}
.track{height:9px;border-radius:99px;background:#cde2fb;overflow:hidden}
.track i{display:block;height:100%;background:#2a78d6;border-radius:99px}
.track.w{background:#fdeecd}.track.w i{background:#fab219}
.mnote{font-size:11px;color:#9a5b00;margin-top:6px;display:flex;gap:5px;align-items:center}
.paper{background:#fff;border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);
  padding:26px 30px 22px}
.ph{display:flex;align-items:flex-start;gap:16px;border-bottom:2px solid var(--ink);
  padding-bottom:13px;margin-bottom:16px}
.ph .dot{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#2f6bff,#16b9d9);
  color:#fff;font-weight:700;font-size:15px;display:flex;align-items:center;justify-content:center}
.ph h3{font-size:17px;letter-spacing:-.2px}
.ph p{font-size:12px;color:var(--ink3);margin-top:3px}
.ph .meta{margin-left:auto;text-align:right;font-size:11.5px;color:var(--ink2);line-height:1.7}
.ph .meta b{color:var(--ink)}
.psum{display:grid;grid-template-columns:repeat(5,1fr);gap:0;border:1px solid var(--line);
  border-radius:8px;overflow:hidden;margin-bottom:18px}
.psum div{padding:11px 14px;border-right:1px solid var(--line-soft)}
.psum div:last-child{border-right:0}
.psum label{display:block;font-size:10px;letter-spacing:.7px;color:#7a89a0;font-weight:700;margin-bottom:5px}
.psum b{font-size:14px;font-variant-numeric:tabular-nums}
.sig{display:flex;gap:40px;margin-top:22px;padding-top:6px}
.sig div{flex:1;border-top:1px solid #c9d2df;padding-top:7px;font-size:11.5px;color:var(--ink3);text-align:center}
.ptab th{background:#fff}
"""

def screen(sid, active, crumb, ini, ime, uloga, h1, chip, actions, body):
    return ('<section class="screen" id="%s">%s<div class="main">%s<div class="body">'
            '<div class="h1"><h1>%s</h1>%s<div class="sp"></div>%s</div>%s</div></div></section>'
            % (sid, side(active), top(crumb, ini, ime, uloga), h1, chip, actions, body))

# ================================================================ izvestaj 1
R1 = """
<div class="filters">
  <span class="lb">Programska šema</span>{s1}
  <span class="lb">Period</span>{s2}
  <span class="lb">Žanr</span>{s3}
  <div class="sp" style="flex:1"></div>
  <button class="btn sm">Osveži</button>
  <button class="btn sm">Izvoz u PDF</button>
</div>

<div class="kpis">
  {k1}{k2}{k3}{k4}
</div>

<div class="two">
  <div class="card">
    <h2>Prosečan rejting po danu<div class="sp"></div><em>septembar 2026 · sve emisije</em></h2>
    <div class="chart">{c1}</div>
    <div class="axlbl">Izvor: merenja gledanosti povezana sa emisijama · označene su najviša, najniža i poslednja vrednost</div>
  </div>
  <div class="card">
    <h2>Najgledanije emisije<div class="sp"></div><em>prosek u periodu</em></h2>
    <div class="chart">{c2}</div>
  </div>
</div>

<div class="card">
  <h2>Termini sa odstupanjem od šeme<div class="sp"></div><em>5 od 1.212 termina</em></h2>
  <table>
    <tr><th style="width:110px">Datum</th><th style="width:80px">Vreme</th><th>Emisija</th>
      <th style="width:110px" class="num">Planirano</th><th style="width:110px" class="num">Stvarno</th>
      <th style="width:110px" class="num">Odstupanje</th><th style="width:300px">Napomena o smetnjama</th></tr>
    <tr><td>03.09.2026.</td><td>19:00</td><td><b>Dnevnik u 19</b></td><td class="num">42:00</td>
      <td class="num">44:10</td><td class="num">+2:10</td><td>Produžen zbog vanredne vesti</td></tr>
    <tr><td>08.09.2026.</td><td>22:15</td><td><b>Sportski žurnal</b></td><td class="num">25:00</td>
      <td class="num">21:35</td><td class="num">−3:25</td><td>Skraćen zbog prenosa utakmice</td></tr>
    <tr><td>14.09.2026.</td><td>20:00</td><td><b>Panorama magazin</b></td><td class="num">60:00</td>
      <td class="num">—</td><td class="num">—</td><td><span class="chip r">Otkazan</span> Kvar emisione opreme</td></tr>
    <tr><td>19.09.2026.</td><td>09:00</td><td><b>Jutarnji program</b></td><td class="num">180:00</td>
      <td class="num">176:20</td><td class="num">−3:40</td><td>Prekid signala u trajanju 3 min</td></tr>
    <tr><td>27.09.2026.</td><td>16:00</td><td><b>Kulturni pregled</b></td><td class="num">45:00</td>
      <td class="num">47:05</td><td class="num">+2:05</td><td>Produžen intervju sa gostom</td></tr>
  </table>
</div>
"""

# ================================================================ izvestaj 2
R2 = """
<div class="filters">
  <span class="lb">Godina</span>{s1}
  <span class="lb">Zona gledanosti</span>{s2}
  <span class="lb">Oglašivač</span>{s3}
  <div class="sp" style="flex:1"></div>
  <button class="btn sm">Osveži</button>
  <button class="btn sm">Izvoz u XLSX</button>
</div>

<div class="kpis">
  {k1}{k2}{k3}{k4}
</div>

<div class="two">
  <div class="card">
    <h2>Fakturisano po mesecima<div class="sp"></div>
      <div class="lg"><span><i style="background:#2a78d6"></i>Naplaćeno</span>
        <span><i style="background:#eb6834"></i>Za naplatu</span></div></h2>
    <div class="chart">{c1}</div>
    <div class="axlbl">Milioni RSD · označen je mesec sa najvećim fakturisanim iznosom</div>
  </div>
  <div class="card">
    <h2>Popunjenost reklamnih blokova<div class="sp"></div><em>prosek za godinu</em></h2>
    <div class="pad" style="padding-top:6px;padding-bottom:10px">
      <div class="mtr"><div class="mh"><span>Zona A — udarni termin</span><b>92%</b></div>
        <div class="track"><i style="width:92%"></i></div></div>
      <div class="mtr"><div class="mh"><span>Zona B — dnevni termin</span><b>74%</b></div>
        <div class="track"><i style="width:74%"></i></div></div>
      <div class="mtr"><div class="mh"><span>Zona C — noćni termin</span><b>58%</b></div>
        <div class="track w"><i style="width:58%"></i></div>
        <div class="mnote">⚠ Ispod ciljne popunjenosti od 70%</div></div>
    </div>
  </div>
</div>

<div class="card">
  <h2>Oglašivači po ostvarenom prihodu<div class="sp"></div><em>19 aktivnih ugovora</em></h2>
  <table>
    <tr><th>Oglašivač</th><th style="width:150px">Ugovor</th>
      <th style="width:140px" class="num">Zakupljeno (s)</th>
      <th style="width:160px" class="num">Fakturisano</th>
      <th style="width:160px" class="num">Naplaćeno</th>
      <th style="width:150px">Status naplate</th></tr>
    <tr><td><b>Delta Market d.o.o.</b></td><td>UG-2026-0087</td><td class="num">12.480</td>
      <td class="num">18.720.000</td><td class="num">16.200.000</td><td><span class="chip y">Delimično</span></td></tr>
    <tr><td><b>Telekom Srbija a.d.</b></td><td>UG-2026-0031</td><td class="num">9.900</td>
      <td class="num">14.850.000</td><td class="num">14.850.000</td><td><span class="chip g">Naplaćeno</span></td></tr>
    <tr><td><b>NIS Petrol</b></td><td>UG-2026-0044</td><td class="num">7.320</td>
      <td class="num">10.980.000</td><td class="num">10.980.000</td><td><span class="chip g">Naplaćeno</span></td></tr>
    <tr><td><b>Gorenje d.o.o.</b></td><td>UG-2026-0062</td><td class="num">5.640</td>
      <td class="num">8.460.000</td><td class="num">6.100.000</td><td><span class="chip y">Delimično</span></td></tr>
    <tr><td><b>Voda Vrnjci a.d.</b></td><td>UG-2026-0095</td><td class="num">4.200</td>
      <td class="num">6.300.000</td><td class="num">4.900.000</td><td><span class="chip y">Delimično</span></td></tr>
    <tr><td>Ostali (14 oglašivača)</td><td>—</td><td class="num">16.860</td>
      <td class="num">25.330.000</td><td class="num">18.150.000</td><td>—</td></tr>
    <tr style="background:#fafbfd"><td><b>UKUPNO</b></td><td></td><td class="num"><b>56.400</b></td>
      <td class="num"><b>84.640.000</b></td><td class="num"><b>71.180.000</b></td>
      <td><span class="chip b">84,1%</span></td></tr>
  </table>
</div>
"""

# ================================================================ izvestaj 3
R3 = """
<div class="filters">
  <span class="lb">Plan nabavke</span>{s1}
  <span class="lb">Status stavke</span>{s2}
  <span class="lb">Organizaciona jedinica</span>{s3}
  <div class="sp" style="flex:1"></div>
  <button class="btn sm">Štampa</button>
  <button class="btn sm">Izvoz u PDF</button>
</div>

<div class="paper">
  <div class="ph">
    <div class="dot">TV</div>
    <div><h3>Izveštaj o realizaciji plana nabavke</h3>
      <p>TV Panorama d.o.o. · Novi Sad · Služba nabavke</p></div>
    <div class="meta">Broj izveštaja: <b>IZV-NAB-2026-09</b><br>
      Period: <b>01.01.2026 – 30.09.2026.</b><br>
      Izradio: <b>Nikola Antić</b> · 30.09.2026.</div>
  </div>

  <div class="psum">
    <div><label>PLAN NABAVKE</label><b>PN-2026</b></div>
    <div><label>UKUPNO PLANIRANO</label><b>14.450.000 RSD</b></div>
    <div><label>UGOVORENO</label><b>12.003.000 RSD</b></div>
    <div><label>REALIZOVANO</label><b>11.603.000 RSD</b></div>
    <div><label>IZVRŠENJE PLANA</label><b>83,1%</b></div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 340px;gap:26px;align-items:start;margin-bottom:20px">
    <div>
      <div style="font-size:12.5px;font-weight:700;color:var(--ink2);margin-bottom:2px">
        Odstupanje realizovane od planirane vrednosti</div>
      <div style="font-size:11px;color:var(--ink3);margin-bottom:8px">po kategoriji nabavke, u procentima</div>
      {c1}
      <div class="lg" style="margin-top:8px;padding-left:196px">
        <span><i style="background:#2a78d6"></i>ispod plana</span>
        <span><i style="background:#e34948"></i>iznad plana</span></div>
    </div>
    <div style="border-left:1px solid var(--line-soft);padding-left:22px">
      <div style="font-size:12.5px;font-weight:700;color:var(--ink2);margin-bottom:10px">Napomene uz izveštaj</div>
      <div style="font-size:12px;color:var(--ink2);line-height:1.62">
        Prekoračenje kod snimateljske opreme (+12,4%) posledica je kursne razlike
        i dodatnog stativa uvrštenog u narudžbenicu NR-2026-0211.<br><br>
        Usluge servisa realizovane su znatno ispod plana (−21,5%) jer je oprema
        u garantnom roku servisirana bez naknade.<br><br>
        Dve reklamacije (RK-2026-0018 i RK-2026-0023) su rešene zamenom robe;
        obe se odnose na istog dobavljača.
      </div>
    </div>
  </div>

  <table class="ptab">
    <tr><th style="width:44px" class="num">RB</th><th>Predmet nabavke</th>
      <th style="width:92px">Kvartal</th><th style="width:140px" class="num">Planirano</th>
      <th style="width:140px" class="num">Realizovano</th><th style="width:110px" class="num">Odstupanje</th>
      <th style="width:168px">Status</th></tr>
    <tr><td class="num">1</td><td><b>Studijske kamere i stativi</b></td><td>Q2</td>
      <td class="num">4.200.000</td><td class="num">3.950.000</td><td class="num">−5,9%</td>
      <td><span class="chip g">Realizovano</span></td></tr>
    <tr><td class="num">2</td><td><b>Rasveta studija 2</b></td><td>Q2</td>
      <td class="num">1.850.000</td><td class="num">2.080.000</td><td class="num">+12,4%</td>
      <td><span class="chip g">Realizovano</span></td></tr>
    <tr><td class="num">3</td><td><b>Audio miks pult</b></td><td>Q3</td>
      <td class="num">2.400.000</td><td class="num">—</td><td class="num">—</td>
      <td><span class="chip y">Prikupljanje ponuda</span></td></tr>
    <tr><td class="num">4</td><td><b>Servis emisione opreme</b></td><td>Q1–Q4</td>
      <td class="num">1.200.000</td><td class="num">942.000</td><td class="num">−21,5%</td>
      <td><span class="chip b">U toku</span></td></tr>
    <tr><td class="num">5</td><td><b>Prava emitovanja — strani format</b></td><td>Q3</td>
      <td class="num">3.600.000</td><td class="num">3.823.000</td><td class="num">+6,2%</td>
      <td><span class="chip g">Realizovano</span></td></tr>
    <tr><td class="num">6</td><td><b>Potrošni materijal</b></td><td>Q1–Q4</td>
      <td class="num">780.000</td><td class="num">808.000</td><td class="num">+3,6%</td>
      <td><span class="chip b">U toku</span></td></tr>
    <tr><td class="num">7</td><td><b>Kancelarijski materijal</b></td><td>Q1–Q4</td>
      <td class="num">420.000</td><td class="num">400.000</td><td class="num">−4,8%</td>
      <td><span class="chip b">U toku</span></td></tr>
    <tr style="background:#fafbfd"><td></td><td><b>UKUPNO</b></td><td></td>
      <td class="num"><b>14.450.000</b></td><td class="num"><b>11.603.000</b></td>
      <td class="num"><b>−19,7%</b></td><td><span class="chip b">83,1%</span></td></tr>
  </table>

  <div class="sig"><div>Izradio — referent nabavke</div><div>Kontrolisao — rukovodilac službe</div>
    <div>Odobrio — direktor</div></div>
</div>
"""

def build():
    b1 = R1.format(
        s1=sel('Jesen 2026'), s2=sel('01.09.2026 – 30.09.2026.'), s3=sel('Svi žanrovi'),
        k1=kpi('Realizovanih termina', '1.184', '<b>97,7%</b> od 1.212 planiranih', 'up'),
        k2=kpi('Prosečan rejting', F(round(PROSEK, 1)).replace('.', ','),
               '<b>+0,4</b> u odnosu na avgust', 'up'),
        k3=kpi('Prosečan share', '21,8%', '<b>−1,2 pp</b> u odnosu na avgust', 'dn'),
        k4=kpi('Emitovanja sa smetnjama', '9', '<b>0,8%</b> svih emitovanja', 'wn'),
        c1=chart_line(), c2=chart_bars())
    b2 = R2.format(
        s1=sel('2026.'), s2=sel('Sve zone'), s3=sel('Svi oglašivači'),
        k1=kpi('Fakturisano', '84,64 M', 'RSD · 19 ugovora o oglašavanju'),
        k2=kpi('Naplaćeno', '71,18 M', '<b>84,1%</b> fakturisanog iznosa', 'up'),
        k3=kpi('Popunjenost blokova', '78,4%', '<b>+5,1 pp</b> u odnosu na 2025.', 'up'),
        k4=kpi('Emitovanih spotova', '4.318', '56.400 sekundi ukupno'),
        c1=chart_cols())
    b3 = R3.format(s1=sel('PN-2026'), s2=sel('Sve stavke'), s3=sel('Sve jedinice'),
                   c1=chart_div())

    scr = [
      screen('r1', 'Izveštaji', 'Izveštaji<i>›</i>Program i emitovanje<i>›</i>'
             '<b>Realizacija šeme i gledanost</b>', 'MJ', 'Milica Jovanović', 'Urednik programa',
             'Realizacija programske šeme i gledanost',
             '<span class="chip b"><span class="d"></span>septembar 2026.</span>',
             '<button class="btn">Sačuvaj pogled</button>'
             '<button class="btn p">Pošalji izveštaj</button>', b1),
      screen('r2', 'Izveštaji', 'Izveštaji<i>›</i>Marketing i prodaja<i>›</i>'
             '<b>Prihodi od oglašavanja</b>', 'SP', 'Stefan Perić', 'Referent marketinga',
             'Prihodi od oglašavanja',
             '<span class="chip b"><span class="d"></span>2026. godina</span>',
             '<button class="btn">Sačuvaj pogled</button>'
             '<button class="btn p">Pošalji izveštaj</button>', b2),
      screen('r3', 'Izveštaji', 'Izveštaji<i>›</i>Nabavka<i>›</i>'
             '<b>Realizacija plana nabavke</b>', 'NA', 'Nikola Antić', 'Referent nabavke',
             'Realizacija plana nabavke',
             '<span class="chip g"><span class="d"></span>Konačan</span>',
             '<button class="btn">Vrati na doradu</button>'
             '<button class="btn p">Overi i arhiviraj</button>', b3),
    ]
    html = ('<!DOCTYPE html>\n<html lang="sr">\n<head>\n<meta charset="utf-8">\n'
            '<title>TV Panorama — izveštaji</title>\n'
            '<link rel="stylesheet" href="ui.css">\n<style>%s</style>\n</head>\n<body>\n%s\n'
            '</body>\n</html>\n' % (CSS, '\n\n'.join(scr)))
    open(OUT, 'w', encoding='utf-8').write(html)
    return OUT

if __name__ == '__main__':
    p = build()
    print('->', p, '(%d KB)' % (os.path.getsize(p) // 1024))
    print('prosecan rejting iz podataka: %.2f' % PROSEK)
