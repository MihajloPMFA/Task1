# -*- coding: utf-8 -*-
"""Ortogonalno rutiranje veza: A* po mrezi, kutije su prepreke,
kazna za skretanje i za koriscenje vec zauzetih celija (linije se razmicu)."""
import heapq, array

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))

class Router:
    def __init__(self, W, H, cell=0.07, inflate=0.035):
        self.cell = cell
        self.nx = int(W / cell) + 2
        self.ny = int(H / cell) + 2
        self.blocked = bytearray(self.nx * self.ny)
        self.used = array.array('i', [0]) * 1
        self.used = array.array('i', [0] * (self.nx * self.ny))
        self.inflate = inflate

    def idx(self, i, j):
        return j * self.nx + i

    def to_cell(self, x, y):
        return int(round(x / self.cell)), int(round(y / self.cell))

    def to_xy(self, i, j):
        return i * self.cell, j * self.cell

    def block_rect(self, x, y, w, h):
        e = self.inflate
        i0, j0 = int((x - e) / self.cell), int((y - e) / self.cell)
        i1, j1 = int((x + w + e) / self.cell) + 1, int((y + h + e) / self.cell) + 1
        for j in range(max(0, j0), min(self.ny, j1 + 1)):
            base = j * self.nx
            for i in range(max(0, i0), min(self.nx, i1 + 1)):
                self.blocked[base + i] = 1

    def open_cell(self, i, j):
        if 0 <= i < self.nx and 0 <= j < self.ny:
            self.blocked[self.idx(i, j)] = 0

    def route(self, a, b, turn=4, use=9, spread=3):
        """a, b su (i, j) celije; vraca listu celija ili None."""
        nx, ny, bl, us = self.nx, self.ny, self.blocked, self.used
        ai, aj = a; bi, bj = b
        start = (ai, aj)
        INF = float('inf')
        best = {}
        h0 = abs(ai - bi) + abs(aj - bj)
        pq = [(h0, 0, ai, aj, -1, None)]
        while pq:
            fpri, g, i, j, d, par = heapq.heappop(pq)
            key = (i, j, d)
            if key in best:
                continue
            best[key] = (g, par)
            if (i, j) == (bi, bj):
                path = []
                k = key
                while k is not None:
                    path.append((k[0], k[1]))
                    k = best[k][1]
                path.reverse()
                return path
            for nd, (di, dj) in enumerate(DIRS):
                ni, nj = i + di, j + dj
                if not (0 <= ni < nx and 0 <= nj < ny):
                    continue
                ix = nj * nx + ni
                if bl[ix] and (ni, nj) != (bi, bj):
                    continue
                if (ni, nj, nd) in best:
                    continue
                ng = g + 1 + (turn if (d != -1 and nd != d) else 0) + use * us[ix]
                heapq.heappush(pq, (ng + abs(ni - bi) + abs(nj - bj), ng, ni, nj, nd, key))
        return None

    def mark(self, path, w=1):
        nx, ny, us = self.nx, self.ny, self.used
        for (i, j) in path:
            for dj in (-1, 0, 1):
                for di in (-1, 0, 1):
                    ii, jj = i + di, j + dj
                    if 0 <= ii < nx and 0 <= jj < ny:
                        us[jj * nx + ii] += w if (di == 0 or dj == 0) else 0
            us[j * nx + i] += w

def simplify(path):
    """Celije -> temena poligonalne linije."""
    if not path:
        return []
    pts = [path[0]]
    for k in range(1, len(path) - 1):
        px, py = path[k - 1]; cx, cy = path[k]; nx_, ny_ = path[k + 1]
        if (cx - px, cy - py) != (nx_ - cx, ny_ - cy):
            pts.append(path[k])
    pts.append(path[-1])
    return pts
