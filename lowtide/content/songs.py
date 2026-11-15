"""All LOWTIDE songs (original). Melodies are written as scale-degree phrases; see tools/music.py."""
from music import Song, sfx_chunk
LANTERN_A = "1:4 3:4 5:4 6:2 5:2|8:6 6:2 5:4 3:4|4:4 6:4 8:4 6:2 5:2|3:8 2:4 1:4"      # the Lantern leitmotif
LANTERN_B = "5:4 6:4 8:4 9:2 8:2|9:6 8:2 6:4 5:4|4:8 6:4 5:4|3:12 r:4"
def fast(a): return a.replace(':4', ':2').replace(':6', ':3').replace(':8', ':4').replace(':12', ':6').replace(':2 ', ':2 ')
S = []
def add(*a, **k): S.append(Song(*a, **k))
add('title', key=62, mode='minor', speed=10, prog=(1, 6, 4, 5), A=LANTERN_A, B=LANTERN_B, form='AB', lead_env=0x72, lead_duty=0, vib=2, harm='slow', harm_env=0x42, bass='half', drums='none')
add('shore', key=57, mode='minor', speed=12, prog=(1, 1, 6, 5), A="1:8 r:4 3:4|5:12 r:4|4:8 3:4 2:4|1:16", B="3:6 5:2 3:4 2:4|1:8 r:8|6-:4 1:4 3:4 2:4|1:12 r:4", form='AB', lead_duty=1, vib=3, harm='drone', harm_env=0x32, bass='long', drums='none', lead_env=0x92)
add('coralline', key=60, mode='lydian', speed=6, prog=(1, 5, 6, 4), A="5:2 6:2 5:2 3:2 5:4 r:2 3:2|6:2 8:2 6:2 5:2 3:4 r:4|4:2 5:2 6:2 8:2 9:4 8:4|6:2 5:2 3:2 2:2 1:8", B="8:2 9:2 8:2 6:2 5:4 3:4|2:2 3:2 5:2 3:2 2:4 r:4|4:2 6:2 8:2 6:2 4:2 5:2 6:4|5:2 3:2 2:2 3:2 1:8", form='AABA', harm='off', bass='walk', drums='four', vib=1)
add('reefcave', key=52, mode='phrygian', speed=9, prog=(1, 2, 1, 7), A="1:4 r:4 2:2 1:2 r:4|3:4 2:4 1:4 r:4|1:2 2:2 3:2 5:2 4:4 3:4|2:8 1:4 r:4", B="5:4 4:4 3:4 2:4|1:8 r:8|2:2 3:2 5:2 6:2 5:4 r:4|4:4 3:4 2:8", form='AB', lead_duty=0, vib=2, harm='trem', harm_env=0x32, bass='long', drums='calm')
add('battle', key=57, mode='minor', speed=6, prog=(1, 6, 7, 5), A="1:2 1:2 3:2 5:2 8:4 7:2 5:2|6:2 6:2 8:2 6:2 5:4 3:4|1:2 1:2 3:2 5:2 8:2 9:2 8:2 7:2|6:2 5:2 3:2 2:2 1:8", B="8:2 7:2 6:2 5:2 6:4 5:4|3:2 5:2 6:2 8:2 7:4 r:4|8:2 7:2 6:2 5:2 3:2 5:2 6:2 7:2|8:8 5:4 r:4", form='AABA', harm='arp16', bass='eighth', drums='four')
add('boss_ruffle', key=55, mode='minor', speed=6, prog=(1, 4, 6, 5), A="1:1 3:1 5:1 3:1 8:2 5:2 3:2 5:2 1:2 3:2|6:1 8:1 9:1 8:1 6:2 5:2 3:2 5:2 6:4|4:1 6:1 8:1 6:1 9:2 8:2 6:2 8:2 9:4|7:2 6:2 5:2 3:2 2:2 3:2 5:2 r:2", B="8:2 8:2 9:2 8:2 6:4 5:4|6:2 6:2 8:2 6:2 5:4 3:4|4:2 4:2 6:2 4:2 3:4 2:4|5:2 6:2 7:2 8:2 9:6 r:2", form='AABA', harm='arp16', bass='sync', drums='boss', lead_env=0xB2, vib=1, chroma={4: 1})
add('hull_town', key=57, mode='mixo', speed=8, prog=(1, 4, 1, 5), A="1:4 1:2 2:2 3:4 5:4|6:4 6:2 5:2 3:4 1:4|4:4 4:2 5:2 6:4 8:4|5:4 3:2 2:2 1:8", B="8:4 8:2 7:2 6:4 5:4|6:4 5:2 3:2 5:8|4:4 6:4 8:4 6:4|5:6 3:2 1:8", form='AABA', harm='off', bass='half', drums='march', vib=1)
add('cargo', key=50, mode='dorian', speed=9, prog=(1, 1, 4, 5), A="1:2 r:2 1:2 r:2 3:2 r:2 5:2 r:2|6:2 r:2 5:2 r:2 3:2 r:2 2:2 r:2|1:2 r:2 1:2 r:2 3:2 r:2 5:2 r:2|4:2 3:2 2:2 1:2 2:8", B="5:2 5:2 r:2 6:2 5:2 r:2 3:4|4:2 4:2 r:2 5:2 4:2 r:2 2:4|1:2 3:2 5:2 8:2 7:4 5:4|6:4 5:4 3:8", form='AB', harm='off', bass='eighth', drums='tom', lead_duty=1, lead_env=0xA1)
add('boss_brass', key=52, mode='hminor', speed=6, prog=(1, 4, 5, 1), A="1:3 1:1 3:2 5:2 8:4 7:2 5:2|6:3 6:1 5:2 3:2 5:6 r:2|4:3 4:1 6:2 8:2 9:4 8:2 6:2|7:2 5:2 3:2 2:2 1:8", B="8:2 8:2 9:2 8:2 7:4 5:4|6:2 6:2 7:2 6:2 5:4 3:4|8:2 9:2 10:2 9:2 8:4 7:4|5:2 6:2 7:2 8:2 8:8", form='AABA', harm='block', bass='sync', drums='march', lead_duty=1, lead_env=0xB2)
add('salt_ruins', key=59, mode='lydian', speed=10, prog=(1, 5, 2, 1), A="8:4 7:4 5:4 3:4|5:4 3:4 2:8|8:4 9:4 8:4 7:4|5:8 3:8", B="1:4 3:4 5:4 7:4|8:8 7:4 5:4|9:4 8:4 7:4 5:4|3:12 r:4", form='AB', lead_duty=0, vib=2, harm='slow', harm_env=0x42, bass='long', drums='calm', lead_env=0x82)
add('boss_choir', key=60, mode='minor', speed=7, prog=(1, 6, 4, 5), A="5:8 8:8|7:8 5:8|6:8 8:8|9:6 8:2 7:8", B="1:2 3:2 5:2 8:2 9:4 8:4|7:2 8:2 9:2 10:2 9:4 7:4|8:2 6:2 4:2 6:2 8:4 6:4|5:8 r:8", form='AABA', harm='block', bass='half', drums='half', lead_duty=2, vib=3, lead_env=0xA0)
add('depths_town', key=58, mode='dorian', speed=9, prog=(1, 4, 6, 5), A="5:3 3:1 5:4 6:4 5:4|3:3 2:1 3:4 5:8|6:3 5:1 6:4 8:4 6:4|5:12 r:4", B="8:4 6:4 5:4 3:4|2:4 3:4 5:8|6:4 8:4 9:4 8:4|6:8 5:8", form='AABA', harm='arp', bass='walk', drums='waltz', lead_duty=1, vib=2, lead_env=0x92)
add('depths_dark', key=47, mode='phrygian', speed=10, prog=(1, 2, 1, 5), A="1:6 r:2 2:4 1:4|r:4 5:4 4:4 2:4|1:2 2:2 3:2 2:2 1:8|r:16", B="5:8 4:4 3:4|2:8 1:4 r:4|3:4 2:4 1:4 7-:4|1:16", form='AB', lead_duty=0, vib=3, harm='drone', harm_env=0x32, bass='long', drums='none', lead_env=0x82)
add('boss_lumen', key=53, mode='minor', speed=6, prog=(1, 1, 6, 5), A="1:2 3:2 1:2 3:2 5:2 3:2 1:2 3:2|1:2 3:2 1:2 3:2 6:2 5:2 3:2 5:2|8:2 6:2 8:2 6:2 5:2 3:2 5:2 3:2|1:2 3:2 5:2 6:2 5:4 r:4", B="6:2 8:2 9:2 8:2 6:4 5:4|3:2 5:2 6:2 5:2 3:4 2:4|6:2 8:2 9:2 11:2 9:4 8:4|7:2 6:2 5:2 3:2 5:8", form='AABA', harm='trem', bass='oct', drums='boss', lead_duty=0, vib=2, lead_env=0xA1, harm_env=0x52)
add('archive', key=62, mode='mixo', speed=8, prog=(1, 5, 4, 1), A="1:2 3:2 5:2 3:2 1:2 3:2 5:4|2:2 4:2 6:2 4:2 2:2 4:2 6:4|3:2 5:2 7:2 5:2 3:2 5:2 7:4|8:8 5:4 3:4", B="5:2 5:2 6:2 5:2 3:4 5:4|4:2 4:2 5:2 4:2 2:4 4:4|3:2 3:2 4:2 3:2 1:4 3:4|2:8 1:8", form='AABA', harm='arp', bass='oct', drums='click', lead_duty=2, lead_env=0x92)
add('boss_quill', key=62, mode='minor', speed=6, prog=(1, 7, 6, 5), A="1:1 1:1 3:1 1:1 5:1 1:1 3:1 1:1 8:1 8:1 7:1 8:1 5:1 3:1 5:1 3:1|6:1 6:1 8:1 6:1 9:1 6:1 8:1 6:1 8:2 5:2 3:2 5:2|7:1 7:1 9:1 7:1 11:1 7:1 9:1 7:1 9:2 7:2 5:2 7:2|8:2 7:2 6:2 5:2 3:2 2:2 1:4", B="8:2 7:2 8:2 9:2 8:4 6:4|5:2 6:2 5:2 3:2 5:4 3:4|6:2 5:2 6:2 8:2 6:4 5:4|3:2 2:2 3:2 5:2 1:8", form='AABA', harm='arp16', bass='eighth', drums='boss', lead_env=0xA1)
add('lighthouse', key=57, mode='dorian', speed=8, prog=(1, 4, 6, 5), A="1:4 3:4 5:4 8:4|7:4 5:4 3:4 5:4|6:4 8:4 9:4 11:4|10:8 8:4 5:4", B="8:2 9:2 10:2 11:2 12:4 10:4|9:2 10:2 11:2 12:2 13:4 11:4|8:4 6:4 5:4 3:4|1:12 r:4", form='AB', harm='arp', bass='walk', drums='half', vib=1)
add('boss_marrow', key=57, mode='minor', speed=6, prog=(1, 6, 4, 5), A=LANTERN_A.replace(':4', ':2').replace(':6', ':3').replace(':8', ':4').replace(':2 6:2 5:2', ':2 6:2 5:2'), B="8:2 9:2 10:2 9:2 8:4 6:4|7:2 8:2 9:2 8:2 7:4 5:4|6:2 8:2 10:2 8:2 6:4 4:4|5:2 6:2 7:2 8:2 9:8", form='AABABA', harm='arp16', bass='sync', drums='boss', lead_env=0xB2, vib=1, chroma={})
add('musicbox', key=65, mode='major', speed=11, prog=(1, 5, 6, 4), A="5:4 3:4 5:4 8:4|7:4 5:4 3:8|6:4 4:4 6:4 9:4|8:8 r:8", B="3:4 5:4 8:4 10:4|9:4 8:4 6:8|5:4 6:4 8:4 6:4|5:12 r:4", form='AB', lead_duty=0, lead_env=0x61, harm='slow', harm_env=0x31, bass='half', drums='none', vib=0)
add('shop', key=60, mode='major', speed=8, prog=(1, 6, 4, 5), A="5:2 5:2 6:2 5:2 3:4 1:4|2:2 2:2 3:2 2:2 1:4 5-:4|4:2 4:2 5:2 4:2 6:4 4:4|5:2 3:2 2:2 3:2 1:8", B="8:2 8:2 9:2 8:2 6:4 5:4|6:2 6:2 8:2 6:2 5:4 3:4|4:4 6:4 8:4 6:4|5:8 1:8", form='AABA', harm='off', bass='walk', drums='shuf')
add('save', key=62, mode='major', speed=12, prog=(1, 5, 6, 4), A="3:8 5:8|2:8 3:8|1:8 4:8|5:16", form='A', lead_duty=0, lead_env=0x71, harm='slow', harm_env=0x31, bass='long', drums='none')
add('rhythm', key=64, mode='major', speed=6, prog=(1, 5, 6, 4), A="1:2 3:2 5:2 3:2 1:2 3:2 5:4|2:2 4:2 6:2 4:2 2:2 4:2 6:4|3:2 5:2 8:2 5:2 3:2 5:2 8:4|7:2 5:2 3:2 5:2 1:8", B="8:2 8:2 7:2 8:2 5:4 5:4|6:2 6:2 5:2 6:2 3:4 3:4|4:2 4:2 3:2 4:2 2:4 2:4|1:2 3:2 5:2 8:2 8:8", form='AABA', harm='arp16', bass='eighth', drums='four')
add('sorting', key=60, mode='mixo', speed=6, prog=(1, 4, 1, 5), A="1:2 1:2 r:2 3:2 5:2 r:2 5:2 3:2|4:2 4:2 r:2 6:2 8:2 r:2 8:2 6:2|1:2 1:2 r:2 3:2 5:2 r:2 5:2 7:2|8:4 5:4 3:2 2:2 1:4", form='AABA', harm='off', bass='eighth', drums='hat', lead_duty=1)
add('rival', key=59, mode='minor', speed=6, prog=(1, 7, 6, 7), A="5:2 r:2 5:2 r:2 8:2 7:2 5:2 3:2|6:2 r:2 6:2 r:2 8:2 7:2 6:2 5:2|5:2 r:2 5:2 r:2 9:2 8:2 7:2 5:2|6:2 5:2 3:2 2:2 3:8", B="8:2 8:2 10:2 8:2 7:4 5:4|6:2 6:2 8:2 6:2 5:4 3:4|8:2 8:2 10:2 11:2 10:4 8:4|7:4 6:4 5:8", form='AABA', harm='off', bass='sync', drums='four', lead_env=0xA1)
add('mystery', key=54, mode='hminor', speed=10, prog=(1, 5, 1, 4), A="1:4 r:4 7:4 r:4|1:2 2:2 3:4 r:8|5:4 4:4 3:4 2:4|1:12 r:4", B="8:4 r:4 7:4 6:4|5:8 3:8|4:4 3:4 2:4 1:4|1:16", form='AB', lead_duty=0, vib=3, harm='trem', harm_env=0x32, bass='long', drums='none', lead_env=0x82)
add('end_peace', key=62, mode='major', speed=8, prog=(1, 5, 6, 4), A=LANTERN_A, B=LANTERN_B, form='AABA', harm='arp', bass='half', drums='calm', lead_env=0xA2, vib=1)
add('end_neutral', key=62, mode='minor', speed=9, prog=(1, 6, 4, 5), A=LANTERN_A, B="5:4 6:4 8:4 9:2 8:2|7:6 6:2 5:4 3:4|4:8 2:4 3:4|1:12 r:4", form='ABA', harm='slow', bass='half', drums='calm', lead_duty=1, lead_env=0x92)
add('end_fight', key=57, mode='phrygian', speed=11, prog=(1, 2, 1, 5), A="1:4 4:4 5:4 6:2 5:2|8:6 6:2 5:4 2:4|4:4 6:4 8:4 6:2 5:2|2:8 1:8", B="5:4 6:4 8:4 9:2 8:2|9:6 8:2 6:4 2:4|2:8 6:4 5:4|1:16", form='ABA', lead_duty=3, vib=4, harm='trem', harm_env=0x52, bass='long', drums='tom', chroma={3: -1, 5: 1})
add('end_true', key=62, mode='major', speed=8, prog=(1, 5, 6, 4), A=LANTERN_A + "|" + LANTERN_B.split('|')[0], B=LANTERN_B, form='AB', harm='arp', bass='walk', drums='four', lead_env=0xB2, vib=1)
add('credits', key=60, mode='major', speed=8, prog=(1, 6, 4, 5), A=LANTERN_A, B="5:2 6:2 8:2 6:2 5:4 3:4|2:2 3:2 5:2 3:2 2:4 1:4|4:2 6:2 8:2 6:2 4:4 6:4|5:8 1:8", form='ABAB', harm='arp', bass='half', drums='shuf')
add('marrow_final', key=62, mode='major', speed=5, prog=(1, 5, 6, 4), A=fast(LANTERN_A), B="8:2 9:2 10:2 9:2 8:4 6:4|7:2 8:2 9:2 8:2 7:4 5:4|8:2 10:2 12:2 10:2 8:4 6:4|9:8 8:8", form='AABA', harm='arp16', bass='sync', drums='boss', lead_env=0xB2, vib=1)
SONGS = S
SONG_ID = {s.name: i for i, s in enumerate(S)}

# -------- sound effects: (channel, frames_per_row, raw_cmds, notes)
E = lambda v: bytes([0xE0, v])
SFX_DEFS = [
 ('menu_move', (1, 2, E(0x81) + bytes([0xE1, 2]), [(76, 1)])),
 ('select', (1, 2, E(0xA1) + bytes([0xE1, 2]), [(79, 1), (84, 1)])),
 ('cancel', (1, 2, E(0x91) + bytes([0xE1, 2]), [(72, 1), (67, 1)])),
 ('hurt', (3, 2, b'', [(1, 2), (0, 1), (1, 3)])),
 ('shield', (0, 1, E(0xA1) + bytes([0xE1, 1]), [(88, 1), (91, 1), (95, 2)])),
 ('shield_hit', (0, 1, E(0xC1) + bytes([0xE1, 2]), [(96, 1)])),
 ('save', (1, 4, E(0xA1) + bytes([0xE1, 2]), [(72, 1), (76, 1), (79, 1), (84, 3)])),
 ('boss', (0, 3, E(0xF3) + bytes([0xE1, 1]), [(48, 1), (51, 1), (54, 1), (60, 3), (0, 1), (60, 4)])),
 ('enemy_hurt', (3, 2, b'', [(5, 1), (1, 1), (5, 2)])),
 ('release', (1, 3, E(0xA2) + bytes([0xE1, 2]), [(79, 1), (83, 1), (86, 1), (91, 3)])),
 ('light', (1, 2, E(0xA1) + bytes([0xE1, 0]), [(84, 1), (88, 1), (91, 2)])),
 ('door', (3, 3, b'', [(5, 1), (4, 1)])),
 ('item', (1, 2, E(0xA1) + bytes([0xE1, 2]), [(84, 1), (91, 1)])),
 ('heal', (1, 2, E(0x91) + bytes([0xE1, 2]), [(72, 1), (76, 1), (79, 1), (84, 1), (88, 2)])),
 ('error', (1, 2, E(0x91) + bytes([0xE1, 1]), [(48, 2), (45, 2)])),
 ('splash', (3, 2, b'', [(3, 1), (2, 1), (3, 1)])),
 ('encounter', (0, 1, E(0xC1) + bytes([0xE1, 2]), [(72, 1), (79, 1), (72, 1), (79, 1), (84, 2)])),
 ('dead', (0, 4, E(0xB3) + bytes([0xE1, 2]), [(67, 1), (64, 1), (60, 1), (55, 1), (48, 4)])),
 ('victory', (1, 3, E(0xA2) + bytes([0xE1, 2]), [(72, 1), (72, 1), (72, 1), (76, 2), (79, 4)])),
]
SFX_ID = {n: i for i, (n, _) in enumerate(SFX_DEFS)}
def sfx_bytes(): return sfx_chunk([d for _, d in SFX_DEFS])
