"""Content library: registries, script compiler, map/battle/scene builders -> chunks."""
import re, shlex, struct, os, sys
import chunks as CHK
from pix import Canvas, pal_bytes
L = CHK.LAYOUT
DIRS = {'down': 0, 'up': 1, 'left': 2, 'right': 3}
CMP = {'==': 0, '!=': 1, '<': 2, '>': 3, '<=': 4, '>=': 5}
RESERVED = {'r': 0, 'kills': 1, 'spares': 2, 'listen': 3, 'zone': 4, 'ng': 5, 'lastbt': 6, 'shells': 7, 'bt_turn': 8, 'bt_hits': 9, 'bt_shield': 10,
            'bt_moved': 11, 'bt_acts': 12, 'bt_f0': 13, 'bt_f1': 14, 'bt_f2': 15, 'bt_f3': 16, 'bt_f4': 17, 'bt_f5': 18, 'bt_f6': 19, 'bt_gift': 20,
            'prev_ending': 21, 'bosskills': 22, 'bossspares': 23}
GFX = {'orb': 0, 'spike': 1, 'bubble': 2, 'note': 3, 'bar': 4, 'star': 5, 'coin': 6, 'drop': 7}
KIND = {'aimed': 0, 'fan': 1, 'rain': 2, 'sweep': 3, 'spiral': 4, 'wall': 5, 'side': 6, 'ring': 7}
ITEMKIND = {'heal': 0, 'key': 1, 'gift': 2, 'tool': 3}

class Env:
    def __init__(self): 
        self.vars = dict(RESERVED); self.nextvar = L['V_USER'] + 1   # V_USER itself = prev_moral
        self.vars['prev_moral'] = L['V_USER']
        self.items = {}; self.itemdefs = []; self.speakers = {'narr': 0, 'kid': 1}; self.spk_spec = {}
        self.songs = {}; self.sfx = {}; self.maps = {}; self.battle_ids = {}; self.scene_ids = {}; self.shops = {}; self.shopdefs = []
        self.cur_ents = {}
    def var(self, n):
        if n.isdigit(): return int(n)
        if n not in self.vars:
            assert self.nextvar < 256, 'out of vars'; self.vars[n] = self.nextvar; self.nextvar += 1
        return self.vars[n]
E = Env()

def wrap(text, width, lines_per_page=3, page=True):
    """word wrap; text may contain control tokens {name} {p} {pp} {e:x} (zero width except name=6)"""
    toks = re.findall(r'\{[^}]*\}|\\n|\\p|\S+|\s+', text)
    words = []; cur = []
    for t in toks:
        if t.isspace(): 
            if cur: words.append(cur); cur = []
        else: cur.append(t)
    if cur: words.append(cur)
    lines = [[]]; w = 0; out = []
    def vis(tok):
        if tok == '{name}': return 6
        if tok.startswith('{') or tok in ('\\n', '\\p'): return 0
        return len(tok)
    for word in words:
        if word == ['\\n'] or word == ['\\p']: pass
        wl = sum(vis(t) for t in word)
        forced = [t for t in word if t in ('\\n', '\\p')]
        if forced:
            # split tokens around forced breaks
            seg = []
            for t in word:
                if t in ('\\n', '\\p'):
                    if seg:
                        sl = sum(vis(x) for x in seg)
                        if w + (1 if w else 0) + sl > width: lines.append([]); w = 0
                        lines[-1].append((' ' if w else '', seg)); w += (1 if w else 0) + sl; seg = []
                    lines.append([]); w = 0
                    if t == '\\p': lines[-1].append(('PAGE', None))
                else: seg.append(t)
            if seg:
                sl = sum(vis(x) for x in seg)
                lines[-1].append((' ' if w else '', seg)); w += (1 if w else 0) + sl
            continue
        if w + (1 if w else 0) + wl > width and w:
            lines.append([]); w = 0
        lines[-1].append((' ' if w else '', word)); w += (1 if w else 0) + wl
    # render
    res = bytearray(); lc = 0
    first = True
    for ln in lines:
        if not ln: 
            continue
        if ln[0][0] == 'PAGE':
            res += b'\x0c'; lc = 0; ln = ln[1:]
            if not ln: continue
            first = True
        if not first:
            if page and lc >= lines_per_page: res += b'\x0c'; lc = 0
            else: res += b'\x0a'
        first = False
        for sp, word in ln:
            res += sp.encode()
            for t in word: res += tok_bytes(t)
        lc += 1
    return bytes(res)
def tok_bytes(t):
    if t == '{name}': return b'\x04'
    if t == '{p}': return b'\x01'
    if t == '{pp}': return b'\x02'
    m = re.match(r'\{e:(\w+)\}', t)
    if m: return b'\x03' + bytes([('neutral happy sad angry surprised'.split().index(m.group(1)))])
    return t.encode('ascii', 'replace')

FLAVOR_WARN = []
class Script:
    """compiles script text -> bytes with local label offsets"""
    def __init__(self, text, ctx, ents=None, name='?'):
        self.b = bytearray(); self.labels = {}; self.fix = []; self.ctx = ctx; self.ents = ents or {}; self.name = name
        for ln, raw in enumerate(text.split('\n')): 
            line = raw.strip()
            if not line or line.startswith('#'): continue
            try: self.line(line)
            except Exception as e: raise SystemExit(f'script error in {name} line "{line}": {e!r}')
    def u16ref(self, label): self.fix.append((len(self.b), label)); self.b += b'\0\0'
    def val(self, s): return E.var(s) if not s.lstrip('-').isdigit() else int(s)
    def ent(self, n):
        if n == 'player': return 15
        return self.ents[n]
    def line(self, ln):
        b = self.b
        if ln.startswith(':'): self.labels[ln[1:].strip()] = len(b); return
        m = re.match(r'^([a-z_0-9]+)(?:\.([a-z]+))?:\s+(.*)$', ln)
        if m and m.group(1) in E.speakers:
            spk = E.speakers[m.group(1)]; emo = 0
            if m.group(2): emo = EMO[m.group(2)]
            face = spk > 1 and E.spk_spec.get(m.group(1), {}).get('face', True)
            b += bytes([1, spk, emo]) + wrap(m.group(3), 13 if face else 18) + b'\0'; return
        t = shlex.split(ln); c = t[0]; a = t[1:]
        if c == 'end': b += b'\0'
        elif c == 'set': b += bytes([2, E.var(a[0]), self.val(a[1]) & 255])
        elif c == 'inc': b += bytes([0x3C, E.var(a[0])])
        elif c == 'add': b += bytes([3, E.var(a[0]), self.val(a[1]) & 255])
        elif c == 'copy': b += bytes([0x21, E.var(a[0]), E.var(a[1])])
        elif c == 'addv': b += bytes([0x22, E.var(a[0]), E.var(a[1])])
        elif c == 'rnd': b += bytes([0x23, E.var(a[0]), int(a[1])])
        elif c == 'if':
            # if X [op N] goto L   | if !X goto L
            gi = a.index('goto'); cond = a[:gi]; lab = a[gi + 1]
            if len(cond) == 1: neg = cond[0].startswith('!'); v = cond[0].lstrip('!'); b += bytes([4, E.var(v), 0 if neg else 1, 0])
            else: b += bytes([4, E.var(cond[0]), CMP[cond[1]], self.val(cond[2]) & 255])
            self.u16ref(lab)
        elif c == 'goto': b += bytes([5]); self.u16ref(a[0])
        elif c == 'call': b += bytes([6]); self.u16ref(a[0])
        elif c == 'ret': b += bytes([7])
        elif c == 'choice':
            opts = a[1:]; b += bytes([8, E.var(a[0]), len(opts)])
            for o in opts: b += o.encode() + b'\0'
        elif c == 'warp': b += bytes([9, E.maps[a[0]], int(a[1]), int(a[2]), DIRS[a[3]] if len(a) > 3 else 0])
        elif c == 'warpk': b += bytes([0x3E, E.maps[a[0]], int(a[1]), int(a[2]), DIRS[a[3]] if len(a) > 3 else 0])
        elif c == 'wait': b += bytes([0x0A, int(a[0])])
        elif c == 'fade': b += bytes([0x0B, 1 if a[0] == 'in' else 0])
        elif c == 'shake': b += bytes([0x0C, int(a[0]), int(a[1]) if len(a) > 1 else 2])
        elif c == 'music': b += bytes([0x0D, 255 if a[0] == 'stop' else E.songs[a[0]]])
        elif c == 'sfx': b += bytes([0x0E, E.sfx[a[0]]])
        elif c == 'battle': b += bytes([0x0F]); self.fix.append((len(b), ('battle', a[0]))); b += b'\0\0'
        elif c == 'shop': b += bytes([0x10, E.shops[a[0]]])
        elif c == 'give': b += bytes([0x11, E.items[a[0]]])
        elif c == 'take': b += bytes([0x12, E.items[a[0]]])
        elif c == 'ifhas':
            gi = a.index('goto'); b += bytes([0x13, E.items[a[0]]]); self.u16ref(a[gi + 1])
        elif c == 'save': b += bytes([0x14])
        elif c == 'minigame': b += bytes([0x15, {'rhythm': 0, 'sort': 1}[a[0]]])
        elif c == 'show': b += bytes([0x16, self.ent(a[0]), 1])
        elif c == 'hide': b += bytes([0x16, self.ent(a[0]), 0])
        elif c == 'move': b += bytes([0x17, self.ent(a[0]), DIRS[a[1]], int(a[2])])
        elif c == 'face': b += bytes([0x18, self.ent(a[0]), DIRS[a[1]]])
        elif c == 'pos': b += bytes([0x19, self.ent(a[0]), int(a[1]), int(a[2])])
        elif c == 'gold': b += struct.pack('<h', int(a[0])).join([bytes([0x1A]), b''])
        elif c == 'ending': b += bytes([0x1B, int(a[0])])
        elif c == 'heal': b += bytes([0x1C])
        elif c == 'chunk': b += bytes([0x1D]); self.fix.append((len(b), ('scene', a[0]))); b += b'\0\0'
        elif c == 'name': b += bytes([0x1E])
        elif c == 'flash': b += bytes([0x1F, int(a[0])])
        elif c == 'close': b += bytes([0x20])
        elif c == 'flavor':
            b += bytes([0x24]) + wrap(a[0], 18, 3, page=True) + b'\0'
        elif c == 'attack': b += bytes([0x25, int(a[0])])
        elif c == 'box': b += bytes([0x26, int(a[0]), int(a[1])])
        elif c == 'layers': b += bytes([0x27, int(a[0], 0)])
        elif c == 'spareable': b += bytes([0x28, int(a[0])])
        elif c == 'hurt': b += bytes([0x29, int(a[0])])
        elif c == 'btend': b += bytes([0x2B, int(a[0])])
        elif c == 'cam': b += bytes([0x2D, int(a[0]), int(a[1]), int(a[2]) if len(a) > 2 else 0])
        elif c == 'boost': b += bytes([0x2F, int(a[0])])
        elif c == 'gfx': b += bytes([0x33]); self.fix.append((len(b), ('gfx', a[0]))); b += b'\0\0'
        elif c == 'title': b += bytes([0x37])
        elif c == 'meta': b += bytes([0x38, int(a[0])])
        elif c == 'ifmeta':
            gi = a.index('goto'); b += bytes([0x39, int(a[0])]); self.u16ref(a[gi + 1])
        elif c == 'ifgold':
            gi = a.index('goto'); b += bytes([0x3D, int(a[0])]); self.u16ref(a[gi + 1])
        elif c == 'lock': b += bytes([0x3A, int(a[0])])
        elif c == 'bflag': b += bytes([0x3B, int(a[0])])
        else: raise ValueError('unknown command ' + c)
    def link(self, base, ids):
        out = bytearray(self.b)
        for pos, lab in self.fix:
            if isinstance(lab, tuple):
                kind, n = lab
                v = {'battle': E.battle_ids, 'scene': E.scene_ids, 'gfx': ids.get('gfx', {})}[kind][n]
            else:
                if lab not in self.labels: raise SystemExit(f'undefined label {lab} in {self.name}')
                v = base + self.labels[lab]
            out[pos:pos + 2] = struct.pack('<H', v)
        return bytes(out), {k: base + v for k, v in self.labels.items()}
EMO = {'neutral': 0, 'happy': 1, 'sad': 2, 'angry': 3, 'surprised': 4}
# fix gold encoding
_old_line = Script.line
def _line(self, ln):
    t = ln.split()
    if t and t[0] == 'gold': self.b += bytes([0x1A]) + struct.pack('<h', int(t[1])); return
    return _old_line(self, ln)
Script.line = _line

# --------------------------------------------------------------- entity helper constructors (tile units)
def NPC(i, actor, x, y, label, d='down', gate=None, ngate=None): return dict(k=0, id=i, actor=actor, x=x, y=y, d=d, label=label, gate=gate, ngate=ngate)
def SPOT(i, x, y, label, gate=None, ngate=None): return dict(k=1, id=i, x=x, y=y, label=label, gate=gate, ngate=ngate, d='down')
def BLOCK(i, x, y): return dict(k=2, id=i, actor='block', x=x, y=y, d='down', label=None)
def CHEST(i, x, y, label, gate=None, ngate=None): return dict(k=3, id=i, actor='chest', x=x, y=y, d='down', label=label, gate=gate, ngate=ngate)
def SAVE(i, x, y): return dict(k=4, id=i, actor='savepost', x=x, y=y, d='down', label='__save')
def ENEMY(i, actor, x, y, label, gate=None, ngate=None): return dict(k=5, id=i, actor=actor, x=x, y=y, d='down', label=label, gate=gate, ngate=ngate)
def ZONE(i, x, y, w, h, label, gate=None, ngate=None): return dict(k=6, id=i, x=x, y=y, w=w, h=h, label=label, gate=gate, ngate=ngate, d='down')
def DOOR(i, x, y, gate=None, ngate=None): return dict(k=7, id=i, actor='door', x=x, y=y, d='down', label=None, gate=gate, ngate=ngate)
def EXIT(i, x, y, w, h, to, tx, ty, d='down', gate=None, ngate=None):
    return dict(k=6, id=i, x=x, y=y, w=w, h=h, label='__exit_' + i, gate=gate, ngate=ngate, d='down', exit=(to, tx, ty, d))
def E_(kind, at=(128, 0), sp=24, ang=64, spread=0, n=1, every=20, start=0, dur=0, param=0, gfx='orb', beh=0):
    return bytes([KIND[kind], at[0], at[1], sp, ang & 255, spread, n, every, start, dur, param, GFX[gfx] | (beh << 4)])
def PAT(secs, box, em, dmg=0): return dict(secs=secs, box=box, em=em, dmg=dmg)
