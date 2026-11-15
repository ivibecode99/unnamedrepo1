"""LOWTIDE music: composition DSL -> note-event streams (2 pulse, 1 wave, 1 noise) + numpy preview renderer."""
import struct, math
MODES = {'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10], 'dorian': [0, 2, 3, 5, 7, 9, 10], 'lydian': [0, 2, 4, 6, 7, 9, 11],
         'phrygian': [0, 1, 3, 5, 7, 8, 10], 'mixo': [0, 2, 4, 5, 7, 9, 10], 'hminor': [0, 2, 3, 5, 7, 8, 11], 'pent': [0, 2, 4, 7, 9, 12, 14]}
def deg_midi(root, mode, d, oct_=0):
    sc = MODES[mode]; d0 = d - 1
    return root + sc[d0 % 7] + 12 * (d0 // 7) + 12 * oct_
def note_idx(m): return max(1, min(84, m - 35))

DRUMS = {
 'four': {0: 0, 4: 0, 8: 0, 12: 0, 4.5: None, 2: 2, 6: 2, 10: 2, 14: 2},
}
def drum_bar(style, bar):
    ev = {}
    K, S, H, O, C, T = 0, 1, 2, 3, 4, 5
    if style == 'four': [ev.__setitem__(r, K) for r in (0, 4, 8, 12)]; [ev.__setitem__(r, S) for r in (4, 12)]; [ev.__setitem__(r, H) for r in (2, 6, 10, 14)]
    elif style == 'half': [ev.__setitem__(r, K) for r in (0, 8)]; ev[8] = S if False else K; ev[4] = H; ev[12] = S; ev[10] = H
    elif style == 'shuf': [ev.__setitem__(r, K) for r in (0, 6, 10)]; [ev.__setitem__(r, S) for r in (4, 12)]; [ev.__setitem__(r, H) for r in (2, 8, 14)]
    elif style == 'boss': [ev.__setitem__(r, K) for r in (0, 3, 6, 8, 11, 14)]; [ev.__setitem__(r, S) for r in (4, 12)]; [ev.__setitem__(r, H) for r in (2, 10, 15)]; (ev.__setitem__(0, C) if bar % 4 == 0 else None)
    elif style == 'march': [ev.__setitem__(r, K) for r in (0, 8)]; [ev.__setitem__(r, S) for r in (4, 12, 14)]; ev[10] = H
    elif style == 'calm': ev[0] = K; ev[8] = H; ev[12] = H
    elif style == 'hat': [ev.__setitem__(r, H) for r in range(0, 16, 2)]
    elif style == 'tom': [ev.__setitem__(r, K) for r in (0, 6)]; [ev.__setitem__(r, T) for r in (8, 10, 12, 14)]; ev[4] = S
    elif style == 'click': [ev.__setitem__(r, 6) for r in (0, 4, 8, 12)]
    elif style == 'waltz': ev[0] = K; ev[5] = H; ev[10] = H
    return ev

def parse_phrase(txt, root, mode, base_oct, shift=0, chroma=None):
    """'1:4 3+:2 r:2 | ...' -> list of bars, each list of (midi|0, len) summing to 16"""
    bars = []
    for b in txt.split('|'):
        ev = []; tot = 0
        for tok in b.split():
            d, l = tok.split(':'); l = int(l)
            if d == 'r' or d == '.': ev.append((0, l)); tot += l; continue
            o = 0
            while d.endswith('+'): o += 1; d = d[:-1]
            while d.endswith('-'): o -= 1; d = d[:-1]
            m = deg_midi(root, mode, int(d), base_oct + o) + shift
            if chroma and (int(d) in chroma): m += chroma[int(d)]
            ev.append((m, l)); tot += l
        if tot < 16: ev.append((0, 16 - tot))
        bars.append(ev)
    return bars

class Song:
    def __init__(self, name, key=62, mode='major', speed=7, prog=(1, 5, 6, 4), A='', B='', form='AABA', harm='arp', bass='root', drums='four',
                 lead_env=0xA2, lead_duty=2, vib=0, harm_env=0x62, harm_duty=1, harm_oct=-1, bass_oct=-2, wave=0, lead_oct=1, shift_b=0,
                 bass_vol=0x20, loop=True, chroma=None, density=1.0, hold_drums=True, intro=None):
        self.__dict__.update(locals()); del self.__dict__['self']
    def build_bars(self):
        key = self.key
        a = parse_phrase(self.A, key, self.mode, self.lead_oct, chroma=self.chroma) if self.A else []
        b = parse_phrase(self.B, key, self.mode, self.lead_oct, self.shift_b, chroma=self.chroma) if self.B else a
        lead = []
        for f in self.form: lead += (a if f == 'A' else b)
        n = len(lead)
        prog = list(self.prog)
        chords = [prog[i % len(prog)] for i in range(n)]
        # harmony
        harm = []; bass = []; drums = []
        for i in range(n):
            ch = chords[i]
            r = deg_midi(key, self.mode, ch, 0); t3 = deg_midi(key, self.mode, ch + 2, 0); t5 = deg_midi(key, self.mode, ch + 4, 0)
            ho = 12 * (1 + self.harm_oct)
            tones = [r + ho, t3 + ho, t5 + ho, t3 + ho]
            h = []
            if self.harm == 'arp': h = [(tones[(k // 1) % 4], 2) for k in range(8)]
            elif self.harm == 'arp16': h = [(tones[k % 4] + (12 if k % 8 > 3 else 0), 1) for k in range(16)]
            elif self.harm == 'block': h = [(t3 + ho, 4), (t5 + ho, 4), (t3 + ho, 4), (r + ho + 12, 4)]
            elif self.harm == 'off': h = sum([[(0, 2), (t3 + ho, 2)] for _ in range(4)], [])
            elif self.harm == 'drone': h = [(t5 + ho, 16)]
            elif self.harm == 'slow': h = [(t3 + ho, 8), (t5 + ho, 8)]
            elif self.harm == 'trem': h = [(tones[k % 2 * 2], 1) for k in range(16)]
            elif self.harm == 'none': h = [(0, 16)]
            harm.append(h)
            bo = 12 * 3 + self.bass_oct * 0
            rb = deg_midi(key, self.mode, ch, 0) ; 
            while rb > 52: rb -= 12
            while rb < 38: rb += 12
            fb = rb + MODES[self.mode][(ch + 3) % 7] - MODES[self.mode][(ch - 1) % 7] if False else rb + 7
            if self.bass == 'root': bs = [(rb, 4)] * 4
            elif self.bass == 'eighth': bs = [(rb, 2)] * 8
            elif self.bass == 'walk': bs = [(rb, 4), (fb, 4), (rb + 12, 4), (fb, 4)]
            elif self.bass == 'sync': bs = [(rb, 3), (rb, 3), (rb + 12, 2), (rb, 4), (fb, 4)]
            elif self.bass == 'long': bs = [(rb, 16)]
            elif self.bass == 'oct': bs = [(rb + (12 if k % 2 else 0), 2) for k in range(8)]
            elif self.bass == 'half': bs = [(rb, 8), (fb, 8)]
            elif self.bass == 'none': bs = [(0, 16)]
            bass.append(bs)
            dv = drum_bar(self.drums, i)
            d = []; last = -1
            for r_ in range(16):
                if r_ in dv: d.append([dv[r_], 1])
                else:
                    if d and self.hold_drums and d[-1][0] != 0x7F: d.append([0x7F, 1])
                    elif d and d[-1][0] == 0x7F: d[-1][1] += 1
                    else: d.append([0, 1])
            drums.append([tuple(x) for x in d])
        return [lead, harm, bass, drums]

def encode_bar(ev, is_noise=False, wave=False):
    out = bytearray()
    for m, l in ev:
        while l > 0:
            seg = min(l, 255)
            if is_noise: out += bytes([m if m in (0, 0x7F) else 8 + m, seg])
            else: out += bytes([0 if m == 0 else note_idx(m), seg])
            l -= seg
    return bytes(out)

def compile_song(s):
    bars = s.build_bars()
    chans = [(0xE0, s.lead_env), (0xE0, s.harm_env), (0xE0, s.bass_vol), (0xE0, 0xF1)]
    head = 4 + 8 + 4  # 4 bytes hdr + 4 chan offsets (u16) = 12 ... we use 12
    body = bytearray(); offs = []
    base = 12
    for ci in range(4):
        pre = bytearray()
        if ci == 0: pre += bytes([0xE0, s.lead_env, 0xE1, s.lead_duty, 0xE2, s.vib])
        if ci == 1: pre += bytes([0xE0, s.harm_env, 0xE1, s.harm_duty])
        if ci == 2: pre += bytes([0xE0, s.bass_vol, 0xE6, s.wave])
        pats = {}; patbytes = bytearray(); calls = []
        for bar in bars[ci]:
            eb = encode_bar(bar, ci == 3) + bytes([0xE8])
            if eb not in pats: pats[eb] = len(patbytes); patbytes += eb
            calls.append(pats[eb])
        start = base + len(body)
        # layout: pre | patterns | stream(E3 loop, calls, FE/FF)
        seg_pre_pat = bytes(pre) + bytes(patbytes)
        stream_off = start + len(seg_pre_pat)
        pat_base = start + len(pre)
        stream = bytearray([0xE3]) if s.loop else bytearray()
        for c in calls: stream += bytes([0xE7]) + struct.pack('<H', pat_base + c)
        stream += bytes([0xFE if s.loop else 0xFF])
        # channel entry point must run the 'pre' commands first, then jump over patterns to stream
        entry = bytearray(pre) + bytes([0xE7]) if False else None
        # entry: pre bytes then a CALL-less jump: emulate using E7 to stream? use layout pre | stream | patterns
        seg = bytes(pre) + bytes(stream) + bytes(patbytes)
        stream_start = start + len(pre)
        pat_base = start + len(pre) + len(stream)
        stream = bytearray([0xE3]) if s.loop else bytearray()
        for c in calls: stream += bytes([0xE7]) + struct.pack('<H', pat_base + c)
        stream += bytes([0xFE if s.loop else 0xFF])
        seg = bytes(pre) + bytes(stream) + bytes(patbytes)
        offs.append(start); body += seg
    hdr = bytes([4, s.speed, 0, 0]) + b''.join(struct.pack('<H', o) for o in offs)
    return hdr + bytes(body), bars

# ------------------------------------------------------------- SFX
def sfx_chunk(defs):
    """defs: list of (ch, speed, [cmds], [(note,len)...]); cmds raw bytes"""
    n = len(defs); out = bytearray([n]); offs = []
    body = bytearray()
    base = 1 + 2 * n
    for ch, speed, cmds, notes in defs:
        offs.append(base + len(body))
        body += bytes([ch, speed]) + bytes(cmds)
        for m, l in notes: body += bytes([m if ch == 3 else (0 if m == 0 else note_idx(m)), l])
        body += bytes([0xFF])
    for o in offs: out += struct.pack('<H', o)
    out += body
    assert len(out) < 300, len(out)
    return bytes(out)

# ------------------------------------------------------------- preview renderer (mirrors audio.c / hardware model)
import numpy as np
SR = 22050
def period(n, ch):
    midi = 36 + n - 1; f = 440 * 2 ** ((midi - 69) / 12); idx = n + (12 if ch == 2 else 0); idx = min(idx, 84)
    m = 36 + idx - 1; fp = 440 * 2 ** ((m - 69) / 12)
    return max(0, min(2047, round(2048 - 131072 / fp)))
DR_NR43 = [0x93, 0x43, 0x20, 0x20, 0x31, 0x73, 0x10, 0x53]; DR_ENV = [0xF1, 0xC2, 0x61, 0x93, 0xA4, 0xB2, 0x41, 0x71]
WAVES = [[0x01,0x23,0x45,0x67,0x89,0xAB,0xCD,0xEF,0xFE,0xDC,0xBA,0x98,0x76,0x54,0x32,0x10], [0x01,0x12,0x23,0x34,0x45,0x56,0x67,0x78,0x89,0x9A,0xAB,0xBC,0xCD,0xDE,0xEF,0xF0], [0xFF]*8+[0]*8, [0x00,0x44,0xAA,0xEE,0xFF,0xEE,0xAA,0x44]*2]
def render_note(ch, n, env, duty, dur_s, wave=0):
    N = int(dur_s * SR); t = np.arange(N) / SR
    if ch in (0, 1):
        p = period(n, ch); f = 131072.0 / (2048 - p)
        duties = [.125, .25, .5, .75]; ph = (t * f) % 1.0; s = np.where(ph < duties[duty & 3], 1.0, -1.0)
        vol = env >> 4; step = env & 7; up = (env >> 3) & 1
        v = np.full(N, float(vol))
        if step:
            k = np.floor(t * 64 / step); v = np.clip(vol + (k if up else -k), 0, 15)
        return s * v / 15
    if ch == 2:
        p = period(n, 2); f = 65536.0 / (2048 - p); w = []
        for b in WAVES[wave & 3]: w += [b >> 4, b & 15]
        w = np.array(w); idx = ((t * f * 32).astype(int)) % 32; sm = w[idx] / 7.5 - 1
        return sm * 0.9
    d = n & 7; nr = DR_NR43[d]; e = DR_ENV[d]; sh = nr >> 4; r = nr & 7; f = 524288.0 / (r if r else .5) / (2 ** (sh + 1))
    steps = int(f * dur_s) + 2; lf = 0x7FFF; bits = np.zeros(steps)
    for i in range(steps):
        x = (lf ^ (lf >> 1)) & 1; lf = (lf >> 1) | (x << 14)
        if nr & 8: lf = (lf & ~0x40) | (x << 6)
        bits[i] = -1.0 if lf & 1 else 1.0
    s = bits[np.minimum((t * f).astype(int), steps - 1)]
    vol = e >> 4; step = e & 7; k = np.floor(t * 64 / step) if step else np.zeros(N)
    return s * np.clip(vol - k, 0, 15) / 15
def render_song(s, seconds=40, path=None):
    bars = s.build_bars(); frames_per_row = s.speed; rowdur = frames_per_row / 60.0
    total = sum(l for m, l in bars[0][0] and [(0, 16)] * len(bars[0])) * rowdur
    total = len(bars[0]) * 16 * rowdur; total = min(total, seconds)
    N = int(total * SR) + SR; mix = np.zeros(N)
    for ci in range(4):
        pos = 0.0; env = [s.lead_env, s.harm_env, s.bass_vol, 0xF1][ci]; duty = [s.lead_duty, s.harm_duty, 0, 0][ci]
        for bar in bars[ci]:
            for m, l in bar:
                dur = l * rowdur
                if pos >= total: break
                if m not in (0, 0x7F):
                    n = note_idx(m) if ci < 3 else m
                    if ci == 2: seg = render_note(2, n, env, 0, dur, s.wave)
                    else: seg = render_note(ci, n, env, duty, dur)
                    i0 = int(pos * SR); mix[i0:i0 + len(seg)] += seg[:max(0, N - i0)] * (0.5 if ci < 2 else 0.6 if ci == 2 else 0.5)
                pos += dur
    mix = np.clip(mix * 0.5, -1, 1)
    if path:
        import wave
        with wave.open(path, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix[:int(total * SR)] * 30000).astype(np.int16).tobytes())
    return mix
