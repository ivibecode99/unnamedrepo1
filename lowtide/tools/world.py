"""World builder: collects content definitions, assigns ids, compiles everything into chunks."""
import struct, os
import chunks as CHK
from pix import Canvas, pal_bytes, hexc
import lib
from lib import E, Script, DIRS, L
import art_chars as AC
import art_tiles as AT

class World:
    def __init__(self):
        self.cast_ = {}; self.maps = []; self.battles = []; self.scenes = []; self.tilesets = {}; self.itemlist = []; self.shoplist = []
        self.enc = {}; self.credits_text = ''; self.start = (0, 0, 0); self.zone_of = {}
    # ---- definitions
    def cast(self, name, sp, pal, acc=None, blip=40, face=True, zone=0, shown=None):
        self.cast_[name] = dict(sp=sp, pal=pal, acc=acc, blip=blip, face=face, zone=zone, shown=shown or name.title())
        E.speakers[name] = len(E.speakers); E.spk_spec[name] = self.cast_[name]
    def tileset(self, name, pals, defs, **k): self.tilesets[name] = AT.Tileset(name, pals, defs, **k); return self.tilesets[name]
    def item(self, name, kind, val=0, price=0):
        self.itemlist.append((name, kind, val, price)); E.items[name] = len(self.itemlist)
    def shop(self, name, items): E.shops[name] = len(self.shoplist); self.shoplist.append(items)
    def scene(self, name, text): self.scenes.append((name, text))
    def mapdef(self, name, ts, rows, music, ents=(), script='', enc=0, rate=0, plate_var=None, plates=(), zone=0):
        E.maps[name] = len(self.maps)
        self.maps.append(dict(name=name, ts=ts, rows=rows, music=music, ents=list(ents), script=script, enc=enc, rate=rate, plate_var=plate_var, plates=list(plates), zone=zone))
    def battle(self, name, **k): self.battles.append(dict(name=name, **k))
    def encounters(self, sid, names): self.enc[sid] = names
    def set_start(self, mp, x, y, d='down'): self.start = (mp, x, y, d)
    # ---- build
    def build(self, ch):
        # ids
        for n, _ in self.scenes: E.scene_ids[n] = ch.reserve('scene_' + n)
        for b in self.battles: E.battle_ids[b['name']] = ch.reserve('battle_' + b['name'])
        # item/shop/speaker tables
        self.build_tables(ch)
        # player
        self.build_player(ch)
        # actors
        self.actor_ch = {}
        for n, sp in self.cast_.items(): self.actor_ch[n] = self.make_actor(ch, n, sp)
        for n, (spec) in PROPS.items(): self.actor_ch[n] = self.make_actor(ch, n, spec)
        # tilesets
        self.ts_ch = {}
        for n, ts in self.tilesets.items():
            self.ts_ch[n] = (ch.add(ts.tiles_bytes(), 'tiles_' + n), ch.add(ts.meta_bytes(), 'meta_' + n), ch.add(ts.pal_bytes(), 'pal_' + n))
        # enemy gfx
        self.gfx_ch = {}
        for b in self.battles:
            g = b['gfx']
            if g not in self.gfx_ch:
                pal = b.get('pal', ['#F4EBD0', '#9AA0B0', '#4C4A68', '#0C0B14'])
                data, _ = AC.enemy_chunk(g, pal)
                self.gfx_ch[g] = ch.add(data, 'gfx_' + g)
        for name, ext in getattr(self, 'extra_gfx', {}).items(): pass
        # compile
        for n, text in self.scenes:
            sc = Script(text, E, name='scene ' + n)
            code, _ = sc.link(0, {'gfx': self.gfx_ch})
            assert len(code) <= lib.L['SCENE_MAX'], (n, len(code))
            ch.set(E.scene_ids[n], code)
        for b in self.battles: self.compile_battle(ch, b)
        dirb = bytearray(514)
        for i, m in enumerate(self.maps): struct.pack_into('<H', dirb, i * 2, self.compile_map(ch, m))
        dirb[510:513] = bytes([self.start[1], self.start[2], DIRS[self.start[3]]])
        assert len(self.maps) < 255
        ch.fixed(L['CH_MAPS'], dirb, 'maps')
        # encounters
        eb = bytearray(8 * (max(self.enc) + 2 if self.enc else 2))
        for sid, names in self.enc.items():
            for i, n in enumerate(names[:4]): struct.pack_into('<H', eb, sid * 8 + i * 2, E.battle_ids[n])
        ch.fixed(L['CH_ENC'], eb, 'enc')
        ch.fixed(L['CH_CREDITS'], self.credits_text.encode(), 'credits')
    def build_tables(self, ch):
        b = bytearray([len(self.itemlist)])
        for name, kind, val, price in self.itemlist:
            assert len(name) <= 10, name
            b += name.encode().ljust(10, b'\0') + bytes([lib.ITEMKIND[kind], val]) + struct.pack('<H', price)
        ch.fixed(L['CH_ITEMS'], b, 'items')
        s = bytearray()
        for its in self.shoplist: s += bytes([len(its)] + [E.items[i] for i in its] + [0] * (8 - len(its)) + [0])
        ch.fixed(L['CH_SHOPS'], s or b'\0' * 10, 'shops')
        # speakers: id order
        order = sorted(E.speakers.items(), key=lambda kv: kv[1])
        sp = bytearray(16 * len(order)); self.face_ch = {}
        for name, i in order:
            if name == 'narr': struct.pack_into('<BBH12s', sp, i * 16, 38, 0, 0, b''); continue
            if name == 'kid': struct.pack_into('<BBH12s', sp, i * 16, 52, 0, 0, b''); continue
            c = self.cast_[name]
            fc = 0; ne = 0
            if c['face']:
                faces = [AC.face32(c, e) for e in range(5)]
                data = pal_bytes(AC.face_pal(c)) + b''.join(f.tiles() for f in faces)
                fc = ch.add(data, 'face_' + name); ne = 5
            struct.pack_into('<BBH12s', sp, i * 16, c['blip'], ne, fc, c['shown'][:11].encode())
        ch.fixed(L['CH_SPEAKERS'], sp, 'speakers')
    def make_actor(self, ch, n, spec):
        cv = AC.sprite16(spec)
        return ch.add(pal_bytes(AC.sprite16_pal(spec)) + cv.tiles(), 'actor_' + n)
    def build_player(self, ch):
        frames = []
        for d in ('down', 'up', 'side'):
            for f in (0, 1): frames.append(kid_frame(d, f))
        pal = ['#000000', '#F2D3A0', '#3E7FB0', '#14122A']
        ch.fixed(L['CH_PLAYER'], pal_bytes(pal) + b''.join(fr.tiles() for fr in frames), 'player')
    def compile_battle(self, ch, b):
        name = b['name']
        pats = b.get('patterns', [])
        scr = Script(b['script'], E, name='battle ' + name)
        for need in ('intro', 'turn', 'win', 'spared', 'refuse'):
            assert need in scr.labels or need == 'refuse', (name, need)
        if 'refuse' not in scr.labels:
            scr = Script(b['script'] + '\n:refuse\nflavor "They are not ready to let go."\nend', E, name='battle ' + name)
        listen = b.get('listen', [('Check', 'check')])
        assert len(listen) <= 6
        hdr_size = L['BH_SIZE']
        patblob = bytearray(); offs = []
        tab_size = 2 * len(pats)
        base_pat = hdr_size + tab_size
        for p in pats:
            offs.append(base_pat + len(patblob))
            em = b''.join(p['em']); assert len(p['em']) <= 4
            secs = p['secs']; ln = int(secs * 60 / 4); assert ln < 256
            patblob += bytes([ln, p['box'][0], p['box'][1], p['dmg'], len(p['em'])]) + em
        script_base = base_pat + len(patblob)
        code, labs = scr.link(script_base, {'gfx': self.gfx_ch})
        h = bytearray(hdr_size)
        struct.pack_into('<HBB', h, 0, self.gfx_ch[b['gfx']], E.songs[b['music']], b.get('flags', 0))
        struct.pack_into('<HBBHBB', h, 4, b['hp'], b['atk'], b['exp'], b['gold'], len(pats), len(listen))
        h[12:24] = b.get('shown', name.title()).encode()[:11].ljust(12, b'\0')
        struct.pack_into('<H', h, 24, hdr_size)
        for i, key in enumerate(('intro', 'turn', 'win', 'spared', 'refuse')): struct.pack_into('<H', h, 26 + 2 * i, labs[key])
        for i, (nm, lab) in enumerate(listen):
            assert len(nm) <= 10, nm
            h[38 + i * 12: 38 + i * 12 + 10] = nm.encode().ljust(10, b'\0'); struct.pack_into('<H', h, 38 + i * 12 + 10, labs[lab])
        pt = b''.join(struct.pack('<H', o) for o in offs)
        data = bytes(h) + pt + bytes(patblob) + code
        assert len(data) <= lib.L['SCENE_MAX'], (name, len(data))
        ch.set(E.battle_ids[name], data)
        self.bsize = getattr(self, 'bsize', {}); self.bsize[name] = len(data)
    def compile_map(self, ch, m):
        ts = self.tilesets[m['ts']]; rows = m['rows']; h = len(rows); w = len(rows[0])
        assert w <= 16 and h <= 16 and all(len(r) == w for r in rows), (m['name'], w, h)
        tiles = bytearray()
        for r in rows:
            for c in r:
                assert c in ts.legend, (m['name'], c); tiles.append(ts.legend[c])
        ents = m['ents']; assert len(ents) <= 14, (m['name'], len(ents))
        actors = []; ent_idx = {}
        for i, e in enumerate(ents): ent_idx[e['id']] = i
        for e in ents:
            a = e.get('actor')
            if a and a not in actors: actors.append(a)
        assert len(actors) <= 6, (m['name'], actors)
        extra = ''
        if any(e['k'] == 4 for e in ents): extra += '\n:__save\nsfx save\nnarr: A lantern post hums softly. Your light steadies.\nsave\nend'
        for e in ents:
            if 'exit' in e:
                to, tx, ty, d = e['exit']; extra += f"\n:__exit_{e['id']}\nwarp {to} {tx} {ty} {d}\nend"
        sc = Script(m['script'] + extra, E, ents=ent_idx, name='map ' + m['name'])
        nplate = len(m['plates'])
        base = lib.L['MH_SIZE'] + w * h + len(ents) * lib.L['ENT_SZ'] + 2 * nplate
        code, labs = sc.link(base, {})
        hdr = bytearray(lib.L['MH_SIZE'])
        tch, mch, pch = self.ts_ch[m['ts']]
        hdr[0] = w; hdr[1] = h
        struct.pack_into('<HHH', hdr, 2, tch, mch, pch)
        hdr[8] = 254 if m['music'] is None else E.songs[m['music']]
        hdr[9] = m['enc']; hdr[10] = m['rate']; hdr[11] = 0
        has_water = any(v[0] == 'water' for v in ts.defs.values()) and any(ts.defs[c][0] == 'water' for r in rows for c in r)
        if ts.flags & 2 or has_water: hdr[11] |= 2
        hdr[12] = ts.dmg_bgp; hdr[13] = ts.dmg_obp
        hdr[14] = len(ents); hdr[15] = nplate
        for i, a in enumerate(actors): struct.pack_into('<H', hdr, 16 + 2 * i, self.actor_ch[a])
        struct.pack_into('<H', hdr, 28, labs.get('enter', 0))
        hdr[30] = E.var(m['plate_var']) if m['plate_var'] else 0
        eb = bytearray()
        for e in ents:
            k = e['k']; slot = actors.index(e['actor']) if e.get('actor') else 0
            x, y = e['x'] * 16, e['y'] * 16
            dirv = DIRS[e.get('d', 'down')]
            if k == 6: slot, dirv = e['w'] * 2, e['h'] * 2
            flags = 16 if e.get('ngate') else 0
            gv = E.var(e['gate'] or e['ngate']) if (e.get('gate') or e.get('ngate')) else 0
            lab = e.get('label'); sc_off = labs[lab] if lab else 0
            eb += bytes([k, slot, x, y, dirv, flags, gv, 1]) + struct.pack('<H', sc_off)
        pb = b''.join(bytes(p) for p in m['plates'])
        data = bytes(hdr) + bytes(tiles) + bytes(eb) + pb + code
        assert len(data) <= lib.L['SCENE_MAX'], f"map {m['name']} too big: {len(data)} (script {len(code)})"
        self.msize = getattr(self, 'msize', {}); self.msize[m['name']] = len(data)
        return ch.add(data, 'map_' + m['name'])

PROPS = {
 'block': dict(sp='golem', pal=('#C9B79C', '#8A7A66', '#2A2433'), acc=None),
 'chest': dict(sp='clam', pal=('#F2A33C', '#B2542A', '#2A1A12'), acc=None),
 'savepost': dict(sp='bell', pal=('#FFF2C8', '#F2A33C', '#2A1A12'), acc='lamp'),
 'door': dict(sp='golem', pal=('#8A6A4A', '#5A4030', '#1A1210'), acc=None),
}
def kid_frame(d, f):
    c = Canvas(16, 16, 0)
    bob = 1 if f else 0
    c.ellipse(8, 5 + bob, 3, 3, 1)
    c.rect(5, 8 + bob, 6, 5, 2)
    c.rect(4, 9 + bob, 1, 3, 1); c.rect(11, 9 + bob, 1, 3, 1)
    if d == 'down':
        c.rect(5, 2 + bob, 6, 2, 3); c.px(7, 5 + bob, 3); c.px(9, 5 + bob, 3)
        c.rect(5, 13, 2, 2, 3) if not f else c.rect(5, 12, 2, 2, 3); c.rect(9, 13, 2, 2, 3) if f == 0 else c.rect(9, 13, 2, 2, 3)
        c.px(8, 9 + bob, 0); c.px(8, 10 + bob, 0)
    elif d == 'up':
        c.rect(5, 2 + bob, 6, 4, 3); c.rect(5, 13, 2, 2, 3); c.rect(9, 13, 2, 2, 3)
    else:
        c.rect(5, 2 + bob, 6, 2, 3); c.px(7, 5 + bob, 3); c.rect(6, 13 - f, 2, 2, 3); c.rect(8, 12 + f, 2, 3, 3)
        c.px(3, 9 + bob, 0)
    c.px(8, 8 + bob, 0) if d != 'up' else None
    c.outline(3)
    return c
W = World()
