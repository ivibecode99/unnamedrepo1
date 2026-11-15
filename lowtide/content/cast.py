"""Tilesets, cast, items, shops."""
from world import W
Z = {  # zone palettes: ground, wall, props(3), accent(3), special(3), water
 0: dict(g=['#D8C49A', '#B8A27A', '#8A7658', '#3A3040'], w=['#9A98A8', '#6E6C82', '#46445E', '#1A1824'], p=['#E8E0CC', '#8A5A44', '#2E2434'], a=['#7AA08A', '#4A6E62', '#223A36'], s=['#F2C46A', '#C0763A', '#4A2A22'], wt=['#7AA8C0', '#5088A8', '#306488', '#1E4468']),
 1: dict(g=['#BFE3D4', '#8CC8B8', '#5FA39A', '#274E56'], w=['#F2A6A0', '#D8707C', '#A8465E', '#4E1E3A'], p=['#F4E7C8', '#C9825A', '#3A2A3A'], a=['#5FC49A', '#2E8A6E', '#16423A'], s=['#FFD66B', '#E8903A', '#6A3A22'], wt=['#7FE0E8', '#4CB8D8', '#2C86B8', '#1E5890']),
 2: dict(g=['#E6C48A', '#C99A5E', '#9A6A3A', '#4A2E1E'], w=['#B8864E', '#8A5A32', '#5E3A22', '#2A1810'], p=['#F0D890', '#B8603A', '#2A1A12'], a=['#8CA88A', '#5E7A6A', '#2A3A34'], s=['#FFE08A', '#D8902A', '#6A3A12'], wt=['#8AC0C8', '#5E98A8', '#3E7088', '#284860']),
 3: dict(g=['#EAF0F0', '#CAD8E0', '#9AB0C8', '#4A5878'], w=['#F6F8FA', '#C8D6E4', '#8AA0BE', '#3A4868'], p=['#B8C8E0', '#7A8CB0', '#2A3450'], a=['#9ADCD0', '#5AAAB0', '#2A5A6A'], s=['#F4D8A0', '#D8905A', '#5A3A3A'], wt=['#B8E4F0', '#88C4E0', '#5898C8', '#3A6498']),
 4: dict(g=['#6A5A98', '#4E4278', '#352E5A', '#1A1630'], w=['#8A6AB8', '#654A98', '#43307A', '#1E1440'], p=['#C8A8F0', '#8A58C8', '#1A1030'], a=['#58E0D0', '#2AA8B8', '#144868'], s=['#FF8AD0', '#D04898', '#5A1A4A'], wt=['#7A68C8', '#5848A8', '#3C2E88', '#261C60']),
 5: dict(g=['#E8DCC0', '#C8B898', '#988468', '#4A3A2E'], w=['#5A6A9A', '#40507E', '#2C3A62', '#161E3A'], p=['#F4EEDC', '#8A6A4A', '#2A1E16'], a=['#B84A4A', '#7A2A3A', '#3A1426'], s=['#E8C858', '#B88A2A', '#5A3A12'], wt=['#9AB0D0', '#7090B8', '#486898', '#2E4470']),
 6: dict(g=['#4A4880', '#38366A', '#262452', '#12102E'], w=['#F0E0A8', '#D8B868', '#A07A38', '#4A3418'], p=['#FFF2C8', '#F2A33C', '#241A30'], a=['#8AF0E0', '#48B0C0', '#1A5068'], s=['#FF9AA8', '#D8587A', '#601A3A'], wt=['#6AA0E0', '#4878C8', '#3050A8', '#1C3478']),
}
def pals(z):
    d = Z[z]; g0 = d['g'][0]
    return [d['g'], d['w'], [g0] + d['p'], [g0] + d['a'], [g0] + d['s'], d['wt']]
PROPKIND = {'p': 'pillar', 'b': 'barrel', 'c': 'crate', 'l': 'lamp', 'k': 'kelp', 'o': 'coralc', 'r': 'rock', 'D': 'door', 's': 'sign', 'g': 'rug', 'h': 'shelf', 't': 'table',
            'S': 'stairs', 'y': 'crystal', 'u': 'statue', 'm': 'mast', 'n': 'tank', 'e': 'glow', 'd': 'desk', 'G': 'gate', 'a': 'seat', 'w': 'window', 'i': 'chain', 'z': 'bed'}
SOLID = set('pbclkorDshtyumndGaiz')
PALOF = {'k': 3, 'o': 3, 'e': 4, 'l': 4, 'y': 4, 'g': 2, 'i': 2}
def ts(name, z, floor='sand', floor2='moss', wall='brick', props='', plate='tile', dmg=0xE4):
    defs = {'.': ('floor', floor, 0, 0), ',': ('floor', floor2, 0, 0), 'x': ('floor', floor, 0, 4), '#': ('wall', wall, 1, 1), '~': ('water', '', 5, 1), '_': ('floor', plate, 0, 0)}
    for ch in props:
        fl = 1 if ch in SOLID else 0
        defs[ch] = ('prop', PROPKIND[ch], PALOF.get(ch, 2), fl)
    return W.tileset(name, pals(z), defs, dmg_bgp=dmg)
ts('shore', 0, 'sand', 'moss', 'cave', 'rbmDsl')
ts('reef', 1, 'sand', 'moss', 'coral', 'oklbsDrct', plate='stone')
ts('hull', 2, 'plank', 'stone', 'hull', 'bcmplDsGtaw', plate='tile')
ts('salt', 3, 'tile', 'stone', 'salt', 'pyulsDeG', plate='sand')
ts('deep', 4, 'dark', 'moss', 'cave', 'yeklsDuGr', plate='stone', dmg=0xE4)
ts('arch', 5, 'tile', 'carpet', 'book', 'hdtpaslDgzS', plate='stone')
ts('light', 6, 'stone', 'tile', 'salt', 'pyluelsDGSg', plate='tile')

# ------------------------------------------------------------- cast (name, species, palette, accessory, blip, shown, zone)
C = [
 ('wick', 'moth', ('#FFF2C8', '#FFC85A', '#7A3A1A'), None, 62, 'Wick', 0),
 ('gaff', 'gull', ('#F0F0E8', '#B8B8C8', '#3A3A52'), 'cap', 30, 'Gaff', 0),
 ('pip', 'crab', ('#F7A58A', '#D8685A', '#4A1E2A'), 'cap', 52, 'Pip', 1),
 ('tuck', 'urch', ('#C8A8E8', '#8A68B8', '#2E1E4A'), 'glasses', 34, 'Tuck', 1),
 ('skiff', 'angler', ('#8AD8F0', '#4A98C8', '#18304A'), 'scarf', 56, 'Skiff', 1),
 ('ruffle', 'anem', ('#FFB0C8', '#E8608A', '#5A1A3A'), 'crown', 46, 'Mayor Ruffle', 1),
 ('tangle', 'kelp', ('#9AE0A8', '#4AA878', '#1A4A3A'), None, 44, 'Tangle', 1),
 ('brass', 'crab', ('#F0C060', '#C08A2A', '#4A2A0A'), 'hat', 24, 'Capt Brass', 2),
 ('dory', 'jelly', ('#E8D0F8', '#B890E0', '#4A2A6A'), None, 60, 'Dory', 2),
 ('cobb', 'turtle', ('#B8E0A0', '#6AA85A', '#2A4A24'), 'apron', 36, 'Cobb', 2),
 ('barnaby', 'clam', ('#D8D0C0', '#A89880', '#3A3020'), 'cap', 40, 'Barnaby', 2),
 ('hollis', 'turtle', ('#DDE8F0', '#9AB0C8', '#34425E'), 'scarf', 32, 'Hollis', 3),
 ('rill', 'crab', ('#BFE8F0', '#6AB8D0', '#1E4058'), None, 60, 'Rill', 3),
 ('sill', 'bell', ('#F6F8FA', '#B8C8E0', '#4A5878'), None, 64, 'Sill', 3),
 ('choir', 'golem', ('#F6F8FA', '#C0CEE0', '#4A5878'), None, 58, 'The Choir', 3),
 ('nell', 'eel', ('#D8A8F0', '#9868C8', '#321A5A'), 'glasses', 48, 'Nell', 4),
 ('fenn', 'urch', ('#F0A8E8', '#C860B8', '#4A1A48'), None, 50, 'Fenn', 4),
 ('mop', 'jelly', ('#A8F0F0', '#58C0D8', '#1A4458'), None, 58, 'Mop', 4),
 ('bucket', 'jelly', ('#F8D0A8', '#E89A5A', '#5A2E1A'), None, 54, 'Bucket', 4),
 ('lumen', 'angler', ('#C8A0F8', '#8858D0', '#2A1058'), 'lamp', 26, 'Hushmother', 4),
 ('quill', 'clam', ('#F4EEDC', '#B8A888', '#3A2E22'), 'glasses', 42, 'Archivist', 5),
 ('inkling', 'clam', ('#C8D0F0', '#8A98D0', '#2A3468'), 'cap', 56, 'Inkling', 5),
 ('marrow', 'turtle', ('#FFE8A0', '#D8A83A', '#4A3010'), 'lamp', 28, 'Warden', 6),
 ('echo', 'kid', ('#E8F0FF', '#98A8E0', '#2A3068'), None, 66, 'Echo', 6),
 ('sea', 'moth', ('#B8E4F0', '#5898C8', '#1A2A58'), None, 20, 'The Sea', 6),
]
for n, sp, pal, acc, blip, shown, zone in C: W.cast(n, sp, pal, acc, blip, face=(n not in ('sea',)) , zone=zone, shown=shown)
# NPC-only look-alikes (extra overworld actors reusing species): handled by casting extra names
for n, sp, pal, acc, blip, shown, zone in [
 ('crabfolk', 'crab', ('#E8C08A', '#B8824A', '#3A2412'), None, 50, 'Crab', 1), ('urchinfolk', 'urch', ('#B8E0F0', '#78A8C8', '#1E3450'), None, 48, 'Urchin', 1),
 ('jellyfolk', 'jelly', ('#F8E0F0', '#E0A0D0', '#5A2A52'), None, 58, 'Jelly', 2), ('turtlefolk', 'turtle', ('#D8E8B0', '#9AB868', '#34481E'), None, 34, 'Turtle', 3),
 ('eelfolk', 'eel', ('#C0B0F8', '#8068C8', '#2A1E5A'), None, 46, 'Eel', 4), ('clamfolk', 'clam', ('#F0E0D0', '#C8A888', '#4A3426'), None, 44, 'Clam', 5)]:
    W.cast(n, sp, pal, acc, blip, zone=zone, shown=shown)

# ------------------------------------------------------------- items
for it in [('Old Lamp', 'tool', 0, 0), ('Kelp Wrap', 'heal', 8, 10), ('Brine Tea', 'heal', 14, 20), ('Salt Bun', 'heal', 20, 32), ('Stew', 'heal', 40, 0),
           ('Lamp Oil', 'heal', 30, 55), ('Pearl', 'gift', 0, 40), ('Freshwater', 'gift', 0, 25), ('Toll Coin', 'gift', 0, 30), ('Ink Vial', 'gift', 0, 28),
           ('Whistle', 'gift', 0, 35), ('Sweet Bun', 'gift', 0, 22), ('Warm Rock', 'gift', 0, 18), ('Stamp', 'tool', 0, 0), ('Clapper', 'tool', 0, 0)]:
    W.item(*it)
W.shop('coral', ['Kelp Wrap', 'Brine Tea', 'Pearl', 'Sweet Bun'])
W.shop('hull', ['Brine Tea', 'Salt Bun', 'Toll Coin', 'Warm Rock'])
W.shop('salt', ['Salt Bun', 'Freshwater', 'Lamp Oil', 'Whistle'])
W.shop('deep', ['Brine Tea', 'Lamp Oil', 'Warm Rock', 'Sweet Bun'])
W.shop('arch', ['Salt Bun', 'Lamp Oil', 'Ink Vial', 'Brine Tea'])
