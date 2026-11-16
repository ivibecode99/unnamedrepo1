from world import W
from lib import *
from util import *

W.mapdef('salt_hamlet', 'salt', [
 "################",
 "#..p........p..#",
 "#..............#",
 "#...y......y...#",
 "#..............#",
 "#..s...........#",
 "#..............,",
 "#...u.....u....#",
 "#..............#",
 "#..,,......,,..#",
 "#..............#",
 "#..l........l..#",
 "#..............#",
 "#######..#######"], 'salt_ruins',
 ents=[NPC('hollis', 'hollis', 4, 4, 'hollis_talk'), NPC('rill', 'rill', 11, 5, 'rill_talk'), NPC('sill', 'sill', 8, 8, 'sill_talk'), NPC('shopper', 'turtlefolk', 3, 9, 'shop_talk'),
       SAVE('post', 12, 10), SPOT('sign', 3, 5, 'sign_talk'), EXIT('toeast', 15, 6, 1, 1, 'ruins1', 1, 6, 'right'), EXIT('tosouth', 7, 13, 2, 1, 'brass_cabin', 7, 1, 'down')],
 script="""
:enter
set zone 3
if z3_intro goto e_end
set z3_intro 1
narr: RIMETON. A town of salt and silence. Every roof is white, every wall a little bit sorry.
wick.neutral: It's so quiet. {p}Is it supposed to hum?
sill.happy: It is! It always is! You'll hear it in a moment. It stopped when the Choir lost its place.
:e_end
end
:hollis_talk
if z3_done goto hollis_after
hollis.neutral: The sea used to leave every night. A soft, long goodbye. Come morning it returned. We called it the Low Tide.
hollis.sad: The lowest the sea goes before it comes home. {p}That's what this country is named for. We forgot. All of us.
hollis.neutral: If you're headed up the ruins, mind the Choir. Statues of our first singers. They sing one lullaby, forever.
hollis.sad: The last verse is missing. Nobody knows why.
end
:hollis_after
hollis.happy: The Choir stopped. Do you hear that? It's the silence between verses. It sounds like waiting.
end
:rill_talk
if z3_rill_done goto rill_done
if rill_ask goto rill_again
set rill_ask 1
rill.happy: Hi hi! I'm Rill! I'm practicing the lullaby. Sill sings, I light the lanterns in time. It's tricky!
rill.sad: I always miss the third lantern. Always the third. Will you try? Press the buttons in time!
:rill_again
choice r "Try the song" "Not now"
if r == 1 goto rill_no
minigame rhythm
if r == 0 goto rill_bad
set z3_rill_done 1
sfx light
rill.surprised: You did it! Right on the beat!
if r == 2 goto rill_shell
rill.happy: I'll practice more! Take this as thanks.
give Whistle
end
:rill_shell
if z3_shell goto rill_ps
set z3_shell 1
inc shells
rill.happy: PERFECT! You have to take this. It was my mum's. A MEMORY SHELL. It hums the third verse.
sfx light
end
:rill_ps
rill.happy: Perfect again! You're the best light-lighter in Rimeton!
end
:rill_bad
rill.sad: That was... a nice try. Let's try again later.
end
:rill_no
rill.neutral: Okay. The lanterns will wait. They're patient. They've had practice.
end
:rill_done
rill.happy: The song's in my head forever now. Thanks, {name}!
end
:sill_talk
if knows_hum goto sill_again
set knows_hum 1
sill.happy: A visitor! Listen. Three notes. Low, high, middle. Hum it. {p}That's the Lullaby's front door.
sill.neutral: It opens a lot of rooms. Even angry ones. The Choir loves it when someone remembers the front door.
sill.sad: I can sing nearly all of it. But the last verse... it slips away, like a tide. Like someone leaving without saying goodbye.
end
:sill_again
sill.neutral: Low, high, middle. {p}Hum it for anyone who frightens you.
end
:shop_talk
turtlefolk.neutral: Salt buns, water, whistles. Hush, please. The salt can hear you.
shop salt
end
:sign_talk
narr: RIMETON. Population: statues and a few of us. Please do not lick the walls.
end
""")

W.mapdef('ruins1', 'salt', [
 "################",
 "#.y..........y.#",
 "#..............#",
 "#.....##.......#",
 "#.....#.#...p..#",
 "#..............#",
 "................",
 "#..............#",
 "#..#....#......#",
 "#..............#",
 "#.l...x..xx.l..#",
 "################"], 'salt_ruins', enc=3, rate=3, plate_var='z3_block', plates=[(11, 4), (12, 8)],
 ents=[BLOCK('b1', 4, 3), BLOCK('b2', 6, 7), DOOR('gate', 14, 6, ngate='z3_block'), SPOT('sign', 3, 8, 'sign_talk'),
       EXIT('towest', 0, 6, 1, 1, 'salt_hamlet', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'ruins2', 1, 6, 'right')],
 script="""
:enter
set zone 3
end
:sign_talk
narr: Carved in the salt: 'Where the salt lies thickest, the song begins. Fill the hollows.'
end
""")
W.mapdef('ruins2', 'salt', [
 "################",
 "#..y........y..#",
 "#..............#",
 "#.l.xxxxxx.l...#",
 "#..xxxxxxxx....#",
 "#..............#",
 "................",
 "#..............#",
 "#...y..y..y....#",
 "#..............#",
 "#.p..........p.#",
 "################"], 'salt_ruins', enc=3, rate=3,
 ents=[SPOT('c0', 4, 8, 'crys0'), SPOT('c1', 7, 8, 'crys1'), SPOT('c2', 10, 8, 'crys2'), DOOR('gate', 14, 6, ngate='z3_crystals'),
       EXIT('towest', 0, 6, 1, 1, 'ruins1', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'choir_hall', 1, 6, 'right')],
 script="""
:enter
set zone 3
end
""" + lantern_puzzle('crys', [2, 0, 1], 'z3_crystals', 'z3_seq', ['low', 'middle', 'high'],
   ["The crystal hums low. A tiny voice: 'Hum the front door: low, high, middle. But light me... last, last of all.'",
    "The crystal hums high. 'I'm high! Light me in the MIDDLE. After the low one!'",
    "The crystal hums middle. 'The song starts at the bottom. Light me first. I'm the low one.'"][::-1],
   "The salt gate groans open, and a faint, sad hum drifts through it."))

W.mapdef('choir_hall', 'salt', [
 "################",
 "#.y..u....u..y.#",
 "#..............#",
 "#..............#",
 "#.l..........l.#",
 "#..............#",
 "................",
 "#..............#",
 "#..............#",
 "#..,,......,,..#",
 "#..............#",
 "################"], 'salt_ruins',
 ents=[NPC('choir', 'choir', 7, 4, 'choir_talk', ngate='z3_boss_gone'), ZONE('intro', 3, 5, 1, 3, 'choir_intro', ngate='z3_boss_seen'), SAVE('post', 2, 9),
       EXIT('towest', 0, 6, 1, 1, 'ruins2', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'lumen_gate', 1, 6, 'right', gate='z3_done')],
 script="""
:enter
set zone 3
end
:choir_intro
set z3_boss_seen 1
music mystery
narr: Three statues, shoulder to shoulder, mouths open. Every few seconds, they lose their place and start over.
choir.neutral: LA... LA... LA... {p}la... la...
choir.sad: We do not know how it ends. We do not know why we began. We know the front door. We cannot find the room.
choir.angry: AND THIS IS WHY WE DO NOT LIKE INTRUDERS WHO DO NOT KNOW THE SONG!
music boss_choir
sfx boss
battle choir
if lastbt == 1 goto spared
goto killed
:spared
set z3_done 1
set z3_boss_gone 1
music musicbox
choir.happy: ...la. {p}la. {p}La.
choir.neutral: Oh. Oh, THAT'S how the second-to-last verse goes. We remember.
choir.sad: The last verse... the one that was missing. The Warden never let us finish it. He said it would hurt too much.
wick.sad: Hurt who?
choir.neutral: The one who sang the lullaby first. The one who always, always left, and always came home. {p}The one he couldn't let go.
wick.surprised: ...the sea.
set zone 4
end
:killed
set z3_done 1
set z3_boss_gone 1
music reefcave
narr: Three statues, three small piles of salt. The silence they leave is unbearable.
end
:choir_talk
choir.neutral: la... la... la...
end
""")

W.mapdef('lumen_gate', 'deep', [
 "################",
 "#..............#",
 "#.e..........e.#",
 "#..............#",
 "#..............#",
 "#.......k......#",
 "................",
 "#..............#",
 "#..............#",
 "#.e..........e.#",
 "#..............#",
 "################"], 'depths_dark',
 ents=[SPOT('sign', 8, 5, 'sign_talk'), EXIT('towest', 0, 6, 1, 1, 'choir_hall', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'glimmer_town', 1, 6, 'right')],
 script="""
:enter
set zone 4
if z4_intro goto e_end
set z4_intro 1
narr: The light fades as you descend. Salt gives way to velvet dark and a faint violet glow.
wick.surprised: I-I'm very bright in here. Is that okay? I feel like a lantern at a funeral.
:e_end
end
:sign_talk
narr: Written in glowing paint: 'GLIMMER HOLLOW AHEAD. Please whisper. The lamps sleep lightly.'
end
""")

W.battle('brinebell', shown='Brinebell', gfx='brinebell', hp=26, atk=3, exp=7, gold=9, music='battle',
 pal=['#D8F4F8', '#88C8E0', '#3A6898', '#0C0B14'],
 patterns=[ring(5, 14, 38, 10, gfx='note'), aimed(5, 22, 20, n=3, spread=28, gfx='note'), rain(5, 18, 9, gfx='note'), side(5, 22, 10, gfx='note'), wall(5, 14, 34, 8, gfx='bar')],
 listen=[('Check', 'check'), ('Ring', 'ring'), ('Hush', 'hush'), ('Hum', 'hum')],
 script="""
:intro
flavor "A Brinebell rings once. The ring goes on a long time after it should have ended."
end
""" + turn(5, {0: "A ring of notes. Round and round.", 1: "Aimed notes. It's trying to teach you the scale.", 2: "Notes fall like rain. Very musical rain.", 3: "Notes from the side. A call and response.", 4: "A bar of sound. A rest, then a bar."}) + """
:check
flavor "BRINEBELL. ATK 3. A bell with a heart. Rings what it can't say."
end
:ring
if bt_f0 goto ring2
bflag 0
flavor "You ring along. Ding. It rings back, delighted."
end
:ring2
if bt_f1 goto ring3
bflag 1
flavor "You ring again. Ding-ding. It's matching you now. Maybe rest?"
end
:ring3
flavor "Ding-ding-ding. It's gotten confused. Hush before it spins."
end
:hush
if bt_f1 goto hush_ok
set bt_f0 0
set bt_f1 0
flavor "You hush it too early. It startles and rings alarm. Start over: ring, ring, then hush."
end
:hush_ok
spareable 1
flavor "Ding. Ding. {rest} The bell hangs, listening. It loves a good rest. (Ready to let go.)"
end
:hum
flavor "You hum the lullaby's front door. The bell shivers. It remembers something."
end
:win
flavor "The Brinebell cracks. The last note takes a long time to fade."
end
:spared
flavor "It rings a soft goodbye and drifts off."
end
""".replace("{rest}", "..."))

W.battle('saltling', shown='Saltling', gfx='saltling', hp=30, atk=3, exp=8, gold=10, music='battle',
 pal=['#F8FAFC', '#C0D0E4', '#6078A8', '#0C0B14'],
 patterns=[wall(5, 14, 36, 8, gfx='orb'), ring(5, 14, 40, 8, gfx='orb'), aimed(5, 20, 24, n=2, spread=20, gfx='orb'), side(5, 22, 12, gfx='orb')],
 listen=[('Check', 'check'), ('Hold', 'hold'), ('Water?', 'water')],
 script="""
:intro
flavor "A Saltling stands in your way. It shifts slowly, like a small mountain with a headache."
end
""" + turn(4, {0: "A wall of salt. It's mostly decorative.", 1: "Salt crystals spiral outward. Pretty. Sharp.", 2: "Two crystals, aimed. Very slow.", 3: "Crystals from the side. It's practicing."},
   pre="""if bt_gift == 8 goto water_ok
goto tpre_end
:water_ok
spareable 1
flavor "You offered fresh water. It dissolves into a puddle and... smiles?! (It's ready to go.)"
end
:tpre_end
""") + """
:check
flavor "SALTLING. ATK 3. Made of the sea's leftovers. Misses the sea."
end
:hold
bflag 0
flavor "You hold your hand out. It places a little salt crystal on it, ever so gently."
end
:water
if bt_f0 goto water_hint
flavor "Maybe hold its hand first. Then offer something drinkable. (ITEM: Freshwater.)"
end
:water_hint
flavor "It looks longingly at your waterskin. (ITEM: Freshwater.)"
end
:win
flavor "The Saltling collapses into a neat, quiet pile."
end
:spared
flavor "It leaves a small salt heart where it stood, then wanders off."
end
""")

W.battle('choir', shown='The Choir', gfx='choir', hp=120, atk=4, exp=26, gold=55, music='boss_choir', flags=1 | 2,
 pal=['#F8FAFC', '#B8C8E0', '#586890', '#0C0B14'],
 patterns=[ring(6, 14, 36, 10, gfx='note'), aimed(6, 22, 20, n=3, spread=30, gfx='note'), rain(6, 18, 8, gfx='note'), side(6, 22, 9, gfx='note'),
           wall(6, 14, 34, 9, gfx='bar'), closing(6, 14, 46, 10, 44, gfx='note')],
 listen=[('Check', 'check'), ('Hum', 'hum'), ('Join', 'join'), ('Harmonize', 'harm')],
 script="""
:intro
flavor "Three statues open their mouths. A single ancient note fills the hall."
end
""" + """
:turn
if bt_turn == 3 goto mid1
if bt_turn == 6 goto mid2
:go
rnd r 6
if r == 0 goto t0
if r == 1 goto t1
if r == 2 goto t2
if r == 3 goto t3
if r == 4 goto t4
goto t5
:t0
attack 0
flavor "A ring of notes. The first singer."
end
:t1
attack 1
flavor "Notes at you, in harmony. The second singer."
end
:t2
attack 2
flavor "Notes fall like a hymn. The third singer."
end
:t3
attack 3
flavor "A call and response. Left. Right."
end
:t4
attack 4
flavor "A bar of song: sustained, then cut."
end
:t5
attack 5
flavor "The song closes in. It wants you to understand."
end
:mid1
choir.angry: WE WILL NOT STOP SINGING. WE WILL NOT FINISH. WE CANNOT FINISH. THE LAST VERSE IS GONE.
box 14 4
layers 7
goto go
:mid2
choir.sad: We sing so someone, somewhere, remembers the front door. We sing so the sea knows the way home.
box 8 6
layers 15
goto go
:check
flavor "THE CHOIR. ATK 4. Three singers frozen mid-verse. Fear of: the end of the song."
end
:hum
if knows_hum goto hum_ok
flavor "You hum, but you don't know the front door. (Ask Sill in Rimeton.)"
end
:hum_ok
bflag 0
flavor "You hum: low, high, middle. The Choir's mouths snap shut. Silence. Then, softly: la."
end
:join
if bt_f0 goto join_ok
flavor "You try to join in. They don't know you yet. Hum first."
end
:join_ok
bflag 1
flavor "You sing the second-to-last verse with them. They sing louder. They're crying salt."
end
:harm
if bt_f1 goto harm_ok
flavor "You harmonize too early. They flinch. Join in first."
end
:harm_ok
spareable 1
flavor "You hold the final note and let it breathe. The Choir exhales. (Ready to let go.)"
end
:win
choir.sad: ...la. {p}la.
flavor "The Choir cracks. Three statues, silent at last."
end
:spared
choir.happy: ...la.
end
""")
W.encounters(3, ['brinebell', 'saltling', 'brinebell', 'saltling'])
