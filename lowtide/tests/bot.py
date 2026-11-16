#!/usr/bin/env python3
"""LOWTIDE playthrough bot. Drives the real game binary (SDL build, headless, --bridge) using only controller input
and observed state, from the title screen to the credits. Usage: bot.py <ending: peace|true|neutral|fight> [--bin path]"""
import subprocess, sys, os, json, collections, time, tempfile, random
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
UP, DOWN, LEFT, RIGHT, A, B, START, SELECT = 1, 2, 4, 8, 0x10, 0x20, 0x40, 0x80
DIRV = {0: (0, 1, DOWN), 1: (0, -1, UP), 2: (-1, 0, LEFT), 3: (1, 0, RIGHT)}
NAMES = json.load(open(os.path.join(ROOT, 'build', 'gen', 'names.json')))
class Fail(Exception): pass

class Game:
    def __init__(self, binpath, sav, seed=7, log=None, extra=()):
        self.p = subprocess.Popen([binpath, '--headless', '--bridge', '--sav', sav, '--seed', str(seed), *extra], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        self.frame = 0; self.s = {}; self.log = log; self.deaths = 0; self.battles = 0; self.plan_q = []; self.choice_q = []
        self.step(0)
    def step(self, mask=0):
        self.p.stdin.write(f'{mask:x}\n'); self.p.stdin.flush()
        s = {}
        while True:
            ln = self.p.stdout.readline()
            if not ln: raise Fail('game process ended')
            ln = ln.strip()
            if ln == 'END': break
            t = ln.split(' ', 1)
            if t[0] == 'P': s['P'] = list(map(int, t[1].split()))
            elif t[0] == 'V': s['V'] = list(map(int, t[1].split()))
            elif t[0] == 'W': s['W'] = t[1]
            elif t[0] == 'B': s['B'] = t[1]
            elif t[0] == 'G': s['G'] = list(map(int, t[1].split()))
            elif t[0] == 'X': s['X'] = bytes.fromhex(t[1])
            elif t[0] == 'U': s['U'] = int(t[1])
            elif t[0] == 'T': s['T'] = t[1] if len(t) > 1 else ''
        self.frame += 1; self.s = s; self.parse(); return s
    def parse(self):
        s = self.s; P = s['P']; V = s['V']
        self.mode, self.pmode, self.hp, self.maxhp, self.gold, self.lv, self.tflag = P
        self.vm_active, self.vm_wait = V[0], V[1]
        w = s['W'].split(' ')
        self.map = int(w[0]); self.mw = int(w[1]); self.mh = int(w[2]); self.px = int(w[3]); self.py = int(w[4]); self.pdir = int(w[5])
        self.tiles = w[6]; n = int(w[7]); self.ents = []
        for e in w[8:8 + n]:
            k, x, y, vis, slot, d = map(int, e.split(','))
            self.ents.append(dict(k=k, x=x, y=y, vis=vis, slot=slot, d=d))
        toks = s['B'].split(' ')
        nums = []; i = 0
        while i < len(toks) and ',' not in toks[i]: nums.append(int(toks[i])); i += 1
        nums += [0] * (12 - len(nums))
        self.bs, self.bmsel, self.bsub, self.spareable, self.ehp, sx, sy, self.shield_cd, self.invuln, self.atk_x, self.nlisten, self.nitems = nums[:12]
        self.soul = (sx, sy)
        self.box = list(map(int, toks[i].split(','))) if i < len(toks) else [0, 0, 0, 0]
        self.bullets = [tuple(map(int, x.split(','))) for x in toks[i + 1:] if x]
        self.mg = s['G']; self.ui = s['U']
    # ---------- input helpers
    def shot(self, path):
        self.p.stdin.write(f'S {path}\n'); self.p.stdin.flush()
        while self.p.stdout.readline().strip() != 'SHOT': pass
    def tap(self, m, hold=2, gap=2):
        for _ in range(hold): self.step(m)
        for _ in range(gap): self.step(0)
    def hold(self, m, n):
        for _ in range(n): self.step(m)
    def vmname(self): return self.vm_wait
    def ent_blocking(self, x, y):
        for e in self.ents:
            if e['vis'] and e['k'] in (0, 2, 3, 4, 7) and e['x'] // 16 == x and e['y'] // 16 == y: return True
        return False
    def passable(self, x, y):
        return 0 <= x < self.mw and 0 <= y < self.mh and self.tiles[y * self.mw + x] == '0' and not self.ent_blocking(x, y)
    def path(self, goal, adj=False, avoid=()):
        start = ((self.px + 8) // 16, (self.py + 8) // 16)
        goals = {goal}
        if adj: goals = {(goal[0] + dx, goal[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
        q = collections.deque([start]); prev = {start: None}
        while q:
            c = q.popleft()
            if c in goals and (self.passable(*c) or c == start or not adj and c == goal):
                out = []
                while c != start: out.append(c); c = prev[c]
                return out[::-1], None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + dx, c[1] + dy)
                if n in prev or n in avoid: continue
                ok = self.passable(*n) or (n == goal and not adj)
                if ok: prev[n] = c; q.append(n)
        return None, 'no path'
    def walk_tile(self, tx, ty, max_frames=240):
        tx_px, ty_px = tx * 16, ty * 16; n = 0
        while (self.px, self.py) != (tx_px, ty_px) and n < max_frames:
            dx = tx_px - self.px; dy = ty_px - self.py
            horizontal_move = (dx != 0 and abs(dx) >= abs(dy)) or dy == 0
            if horizontal_move:
                row_y = round(self.py / 16) * 16          # align to the current tile row before sliding sideways
                if self.py != row_y: m = DOWN if row_y > self.py else UP
                else: m = RIGHT if dx > 0 else LEFT
            else:
                col_x = round(self.px / 16) * 16
                if self.px != col_x: m = RIGHT if col_x > self.px else LEFT
                else: m = DOWN if dy > 0 else UP
            m0 = self.map; self.step(m); n += 1
            if self.map != m0 or self.vm_active or self.pmode: return False
        return (self.px, self.py) == (tx_px, ty_px)
    def goto(self, tx, ty, adj=False):
        for attempt in range(60):
            path, err = self.path((tx, ty), adj)
            if path is None: raise Fail(f'no path to {(tx, ty)} in map {self.map} from {((self.px+8)//16, (self.py+8)//16)}')
            if not path: return False
            if attempt == 6: print('   goto debug', (tx, ty), 'map', self.map, 'pos', (self.px, self.py), 'path', path[:6], 'vm', self.vm_active, self.pmode, flush=True)
            m0 = self.map; hit = False
            for c in path:
                ok = self.walk_tile(*c)
                if self.map != m0: self.settle(); return True
                if self.vm_active or self.pmode:
                    self.settle()
                    if self.map != m0: return True
                    hit = True; break
                if not ok: hit = True; break
            if not hit: return False
        raise Fail(f'goto failed {tx, ty} in map {self.map}')
    def face(self, d):
        dx, dy, m = DIRV[d]
        for _ in range(3): self.step(m)
    def interact(self, tx, ty):
        """walk adjacent to tile (tx,ty), face it, press A"""
        if self.goto(tx, ty, adj=True): return
        cx, cy = (self.px + 8) // 16, (self.py + 8) // 16
        d = {(1, 0): 3, (-1, 0): 2, (0, 1): 0, (0, -1): 1}[(tx - cx, ty - cy)]
        self.face(d); self.tap(A)
    def push(self, bx, by, d, n):
        dx, dy, m = DIRV[d]
        self.goto(bx - dx, by - dy)
        # hold direction until the block reaches target
        tx, ty = (bx + dx * n) * 16, (by + dy * n) * 16
        for _ in range(16 * n + 40):
            self.step(m)
            blk = [e for e in self.ents if e['k'] == 2 and abs(e['x'] - tx) < 1 and abs(e['y'] - ty) < 1]
            if blk: break
        # step back (away from the block) until aligned on the tile behind it, so realigning can't push it further
        opp = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}[m]
        ax_tile = (bx + dx * n - dx) * 16 if dx else (by + dy * n - dy) * 16
        for _ in range(40):
            cur = self.px if dx else self.py
            if cur == ax_tile: break
            self.step(opp if ((cur - ax_tile) * (dx or dy) > 0) else m)
        self.step(0)
    # ---------- dialogue/menus/minigames/battle
    def settle(self, choices=None, plan=None, limit=6000, stop_when_free=True):
        n = 0
        choices = self.choice_q
        while n < limit:
            n += 1
            if self.mode == 0:      # title: shouldn't happen mid-run except ending
                return 'title'
            if self.pmode == 6: self.tap(START if n % 3 == 0 else 0); continue    # credits
            if (self.vm_active and self.vm_wait == 6) or self.pmode == 5:
                self.battle(self.plan_q.pop(0) if self.plan_q else None); continue
            if self.vm_active:
                w = self.vm_wait
                if w == 10: self.tap(START); continue
                if w == 4:
                    k = choices.pop(0) if choices else 0
                    for _ in range(k): self.tap(DOWN)
                    self.tap(A); continue
                if w == 8: self.tap(A); self.tap(A); self.tap(A); self.tap(B); continue
                if w == 9: self.minigame(); continue
                if w == 7: self.tap(B); continue
                if w == 11: self.step(0); continue
                self.tap(A, 2, 3); continue
            if self.pmode == 1: self.tap(B); continue
            if stop_when_free: 
                # let fades finish
                self.hold(0, 4)
                if not self.vm_active and self.pmode == 0: return 'free'
        self.shot('/tmp/stuck.png')
        raise Fail(f'settle timeout map={self.map} vm={self.vm_active}/{self.vm_wait} pmode={self.pmode} bs={self.bs} ui={self.ui} pos={self.px},{self.py} mode={self.mode}')
    def minigame(self):
        g = self.mg
        if g[1] == 1: self.tap(A, 2, 2); return
        if g[0] == 0:
            want = g[4]
            if want >= 0: self.tap([LEFT, A, RIGHT][want], 2, 1)
            else: self.step(0)
        else:
            t = g[3]
            if t >= 0: self.tap(LEFT if t == 0 else RIGHT, 2, 2)
            else: self.step(0)
    def danger_move(self):
        bx0, by0, bw, bh = self.box; sx, sy = self.soul
        xmax = bx0 + bw * 8 - 8; ymax = by0 + bh * 8 - 8
        cx = bx0 + bw * 4 - 4; cy = by0 + bh * 4 - 4
        best = None
        for mx, my in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            md = 99.0
            px, py = float(sx), float(sy)
            for t in range(1, 15):
                px = min(max(px + mx * 1.5, bx0), xmax); py = min(max(py + my * 1.5, by0), ymax)
                for (x, y, vx, vy) in self.bullets:
                    bx = x + vx / 16.0 * t; by = y + vy / 16.0 * t
                    d = max(abs(px - bx), abs(py - by))
                    if d < md: md = d
            score = min(md, 14.0) * 10 - (abs(px - cx) + abs(py - cy)) * 0.12 - (0.5 if (mx or my) else 0)
            if best is None or score > best[0]: best = (score, mx, my)
        return best[1], best[2]
    def dodge(self):
        mx, my = self.danger_move(); m = 0
        if mx > 0: m |= RIGHT
        if mx < 0: m |= LEFT
        if my > 0: m |= DOWN
        if my < 0: m |= UP
        sx, sy = self.soul
        if self.shield_cd == 0:
            for (x, y, vx, vy) in self.bullets:
                if abs(x - sx) < 14 and abs(y - sy) < 14: m |= B; break
        self.step(m)
    def battle(self, plan):
        self.battles += 1
        plan = list(plan) if plan else [('F',)]
        idx = 0; lastmenu = -1; guard = 0
        while guard < 60000:
            guard += 1
            if guard % 4000 == 0: print('   battle…', guard, 'bs', self.bs, 'hp', self.hp, 'ehp', self.ehp, 'deaths', self.deaths, 'map', self.map, 'idx', idx, 'spare', self.spareable, flush=True)
            if self.pmode != 5 and not (self.vm_active and self.vm_wait == 6): return
            bs = self.bs
            if bs == 5: self.dodge(); continue
            if bs == 7:
                self.deaths += 1; self.hold(0, 60); self.tap(A, 2, 4); self.hold(0, 20); idx = 0; continue    # RELIGHT (battle restarts from scratch)
            if self.ui != 0: self.tap(A, 2, 3); continue
            if self.vm_active and bs == 0:     # battle script text
                self.tap(A, 2, 2); continue
            if bs == 1:
                act = plan[idx] if idx < len(plan) else (('R',) if self.spareable else plan[-1])
                if self.spareable and plan and plan[0][0] != 'A' and plan[0][0] != 'F': act = ('R',)
                if os.environ.get('BOT_DEBUG'): print('   act', act, 'idx', idx, 'bmsel', self.bmsel, 'spare', self.spareable, 'frame', self.frame, flush=True)
                if act[0] == 'F':
                    self.tap(SELECT); continue
                if act[0] == 'A': tgt = 0
                elif act[0] == 'I': tgt = 1
                elif act[0] == 'L': tgt = 2
                else: tgt = 3
                if self.bmsel != tgt:
                    cur = self.bmsel
                    if (cur & 1) != (tgt & 1): self.tap(RIGHT if tgt & 1 else LEFT)
                    elif (cur >> 1) != (tgt >> 1): self.tap(DOWN if tgt >> 1 else UP)
                    continue
                self.tap(A, 2, 3)
                if act[0] == 'L':
                    for _ in range(act[1] % 2): self.tap(RIGHT)
                    for _ in range(act[1] // 2): self.tap(DOWN)
                    self.tap(A, 2, 3)
                if act[0] == 'I':
                    for _ in range(act[1] % 2): self.tap(RIGHT)
                    for _ in range(act[1] // 2): self.tap(DOWN)
                    self.tap(A, 2, 3)
                if act[0] in ('L', 'R', 'I'):
                    idx += 1 if act[0] != 'R' else 0
                if act[0] == 'L' and idx >= len(plan) and not self.spareable: idx = len(plan) - 1   # repeat last
                continue
            if bs == 4:     # attack bar: stop near centre
                if abs(self.atk_x - 80) < 6: self.tap(A, 2, 3)
                else: self.step(0)
                continue
            if bs in (2, 3): self.step(0); continue
            self.step(0)
        raise Fail('battle timeout')

def run(ending, binpath, verbose=True):
    sav = tempfile.mktemp(suffix='.sav'); g = Game(binpath, sav)
    t0 = time.time()
    def say(*a):
        if verbose: print(f'[{g.frame:7d}] ', *a, flush=True)
    # title -> new game
    g.tap(A, 3, 30); g.tap(A, 3, 30)
    g.settle(); say('prologue done, map', g.map)
    R = routes(ending)
    for step in R:
        kind = step[0]
        if kind == 'say': say(step[1]); continue
        if kind == 'walk': g.goto(step[1], step[2]); g.settle()
        elif kind == 'exit':
            m0 = g.map; g.goto(step[1], step[2]); g.settle()
            if g.map == m0 and g.mode != 0: raise Fail(f'exit at {step[1:3]} did not change map from {NAMES["maps"] and m0}')
        elif kind == 'talk':
            g.choice_q[:] = list(step[3]) if len(step) > 3 else []
            g.interact(step[1], step[2]); g.settle()
        elif kind == 'push': g.push(*step[1:]); 
        elif kind == 'fight':
            g.plan_q.append(step[3]); g.goto(step[1], step[2]); g.settle(); g.plan_q.clear()
        elif kind == 'wait': g.settle()
        elif kind == 'save':
            g.interact(step[1], step[2]); g.settle()
        if kind != 'say': say(f'  {step[:3]} -> map {g.map} hp {g.hp}/{g.maxhp} gold {g.gold} lv {g.lv} deaths {g.deaths} mode {g.mode} pmode {g.pmode} tflag {g.tflag} vm {g.vm_active}/{g.vm_wait}')
        if g.mode == 0 and kind != 'say': break
    # wait for credits to end
    for _ in range(40000):
        if g.mode == 0: break
        g.settle() if g.pmode != 6 else g.tap(START)
    ok = g.mode == 0
    if not ok:
        g.shot('/tmp/end_state.png'); say(f'END STATE mode={g.mode} pmode={g.pmode} vm={g.vm_active}/{g.vm_wait} map={g.map} ui={g.ui} bs={g.bs}')
    try: g.p.stdin.write('Q\n'); g.p.stdin.flush()
    except Exception: pass
    data = open(sav, 'rb').read() if os.path.exists(sav) else b''
    end_bits = data[9] if len(data) > 9 else 0
    v = g.s.get('X', b'\0' * 256); vn = NAMES['vars']
    say('vars: ' + ' '.join(f'{k}={v[vn[k]]}' for k in ('shells', 'kills', 'spares', 'bosskills', 'bossspares', 'true_sing', 'skiff_friend', 'z1_shell', 'z2_shell', 'z3_shell', 'z4_shell', 'z5_shell', 'z5_pages') if k in vn))
    say(f'finished title={ok} endings_bits={end_bits:#x} frames={g.frame} deaths={g.deaths} battles={g.battles} secs={time.time()-t0:.1f}')
    return ok, end_bits, g

def routes(ending):
    from routes import build
    return build(ending)

if __name__ == '__main__':
    ending = sys.argv[1]
    binp = sys.argv[sys.argv.index('--bin') + 1] if '--bin' in sys.argv else os.path.join(ROOT, 'build', 'linux-x64', 'lowtide')
    ok, bits, g = run(ending, binp)
    want = {'peace': 1, 'neutral': 2, 'fight': 4, 'true': 8}[ending]
    sys.exit(0 if ok and bits & want else 1)
