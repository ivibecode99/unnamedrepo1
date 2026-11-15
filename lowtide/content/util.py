"""Helpers for writing battle scripts and patterns compactly."""
from lib import E_, PAT
def turn(n, per=None, pre=''):
    """random turn script over n patterns. per: dict pattern-> flavor text shown after the attack. pre: script lines run first."""
    s = ':turn\n' + pre + f'rnd r {n}\n'
    for i in range(n): s += f'if r == {i} goto turn_{i}\n'
    s += 'goto turn_0\n'
    for i in range(n):
        s += f':turn_{i}\nattack {i}\n'
        if per and i in per: s += f'flavor "{per[i]}"\n'
        s += 'end\n'
    return s
def cyc(n, per=None, pre=''):
    """cycle through patterns by turn counter"""
    s = ':turn\n' + pre
    for i in range(n): s += f'if bt_turn == {i} goto turn_{i}\n'
    s += f'rnd r {n}\n'
    for i in range(n): s += f'if r == {i} goto turn_{i}\n'
    s += 'goto turn_0\n'
    for i in range(n):
        s += f':turn_{i}\nattack {i}\n'
        if per and i in per: s += f'flavor "{per[i]}"\n'
        s += 'end\n'
    return s
# common pattern builders (box in tiles)
def aimed(secs=5, sp=22, every=26, n=1, spread=0, box=(12, 5), gfx='orb', dmg=0, at=(128, 20)):
    return PAT(secs, box, [E_('aimed', at=at, sp=sp, n=n, spread=spread, every=every, gfx=gfx)], dmg)
def rain(secs=5, sp=18, every=12, n=1, box=(12, 5), gfx='drop', dmg=0, beh=0):
    return PAT(secs, box, [E_('rain', sp=sp, n=n, every=every, gfx=gfx, beh=beh)], dmg)
def ring(secs=5, sp=16, every=40, n=10, box=(12, 5), gfx='orb', dmg=0, at=(128, 128), spiral=0):
    return PAT(secs, box, [E_('spiral' if spiral else 'fan', at=at, sp=sp, n=n, every=every, spread=255, param=spiral, gfx=gfx)], dmg)
def wall(secs=5, sp=14, every=34, n=8, box=(12, 5), gfx='orb', ang=64, dmg=0):
    return PAT(secs, box, [E_('wall', sp=sp, n=n, every=every, ang=ang, gfx=gfx)], dmg)
def side(secs=5, sp=20, every=14, n=1, box=(12, 5), gfx='bubble', left=True, dmg=0):
    return PAT(secs, box, [E_('side', sp=sp, n=n, every=every, ang=0 if left else 128, gfx=gfx)], dmg)
def closing(secs=5, sp=14, every=50, n=8, r=44, box=(12, 5), gfx='orb', dmg=0):
    return PAT(secs, box, [E_('ring', sp=sp, n=n, every=every, param=r, gfx=gfx)], dmg)

def lantern_puzzle(p, order, done, seq, names, hints, solved_text):
    """script text for an ordered-lantern puzzle. order: indices in required order. names[i]: label text, hints[i]: what lantern i says"""
    n = len(order); s = ''
    for i in range(n):
        s += f':{p}{i}\nif {done} goto {p}_done\nchoice r "Light it" "Listen"\nif r == 1 goto {p}{i}_hint\n'
        for k in range(n): s += f'if {seq} == {k} goto {p}{i}_s{k}\n'
        s += f':{p}{i}_hint\nnarr: {hints[i]}\nend\n'
        for k in range(n):
            s += f':{p}{i}_s{k}\n'
            if order[k] == i:
                s += f'inc {seq}\nsfx light\nnarr: The {names[i]} lantern kindles.\n'
                if k == n - 1: s += f'goto {p}_solved\n'
                else: s += 'end\n'
            else:
                s += f'set {seq} 0\nsfx error\nshake 10 1\nnarr: The {names[i]} lantern sputters. Every lantern winks out. Wrong order!\nend\n'
    s += f':{p}_solved\nset {done} 1\nsfx door\nshake 20 2\nnarr: {solved_text}\nend\n:{p}_done\nnarr: The lanterns glow steadily. Whatever they were guarding has opened.\nend\n'
    return s
