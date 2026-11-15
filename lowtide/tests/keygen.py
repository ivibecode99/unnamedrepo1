#!/usr/bin/env python3
"""keygen.py out.txt spec...   spec: frame:mask[:hold]  or  mash:start:end:period:mask  (masks hex, K_A=10 B=20 START=40 SELECT=80 UP=1 DOWN=2 LEFT=4 RIGHT=8)"""
import sys
ev = {}
for a in sys.argv[2:]:
    p = a.split(':')
    if p[0] == 'mash':
        s, e, per, m = int(p[1]), int(p[2]), int(p[3]), int(p[4], 16)
        f = s
        while f < e: ev[f] = m; ev[f + 3] = 0; f += per
    else:
        f, m = int(p[0]), int(p[1], 16); hold = int(p[2]) if len(p) > 2 else 4
        ev[f] = m; ev[f + hold] = 0
with open(sys.argv[1], 'w') as fh:
    for f in sorted(ev): fh.write(f'{f} {ev[f]:x}\n')
