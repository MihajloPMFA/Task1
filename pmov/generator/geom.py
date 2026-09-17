# -*- coding: utf-8 -*-
"""Geometrija PMOV dijagrama (inci; Visio koordinate, y raste ka gore)."""
EW, EH   = 2.30, 1.15
IW, IH   = 2.04, 0.89
AW, AH   = 1.98, 0.56
DW, DH   = 2.70, 1.00
SW, SH   = 0.78, 0.54
CR       = 0.17
ROW_DY   = 2.05
ASLOT    = (-3.35, -1.12, 1.12, 3.35)
WING_DX, WING_DY = 4.50, 1.05
COL_DX   = 12.0
CORR     = 6.0
SUB_DY   = 6.6
SUB_DX   = 7.2
SUB_ADX  = 1.55   # x-ofset atributa podtipa (uzi raspored)

def slot_xy(pos):
    """Vraca (dx, dy) atributskog slota."""
    if pos[0] in 'NS' and len(pos) == 2 and pos[1].isdigit():
        return ASLOT[int(pos[1])], (ROW_DY if pos[0] == 'N' else -ROW_DY)
    m = {'NW': (-WING_DX,  WING_DY), 'NE': ( WING_DX,  WING_DY),
         'SW': (-WING_DX, -WING_DY), 'SE': ( WING_DX, -WING_DY),
         'SL': (-SUB_ADX, -ROW_DY),  'SR': ( SUB_ADX, -ROW_DY)}
    return m[pos]
