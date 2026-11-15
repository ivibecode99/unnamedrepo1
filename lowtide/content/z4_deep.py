from world import W
from lib import *
from util import *

W.mapdef('glimmer_town', 'deep', [
 "################",
 "#.e..y....y..e.#",
 "#..............#",
 "#...k......k...#",
 "#..............#",
 "#..,,..s.......#",
 "................",
 "#..............#",
 "#..e........e..#",
 "#..............#",
 "#...,,..,,.....#",
 "#.l..........l.#",
 "#..............#",
 "################"], 'depths_town',
 ents=[NPC('nell', 'nell', 4, 4, 'nell_talk'), NPC('fenn', 'fenn', 11, 4, 'fenn_talk'), NPC('mop', 'mop', 6, 9, 'mop_talk'), NPC('bucket', 'bucket', 8, 9, 'bucket_talk'),
       NPC('eel', 'eelfolk', 12, 9, 'eel_talk'), SAVE('post', 2, 10), SPOT('sign', 7, 5, 'sign_talk'), EXIT('towest', 0, 6, 1, 1, 'lumen_gate', 14, 6, 'left'),
       EXIT('toeast', 15, 6, 1, 1, 'depths1', 1, 6, 'right')],
 script="""
:enter
set zone 4
if z4_town goto e_end
set z4_town 1
narr: GLIMMER HOLLOW. Houses hung from the ceiling like fruit, each window a small violet sunset.
mop.happy: A visitor!
bucket.happy: Two visitors! If you count the little lantern.
wick.angry: I count. I always count.
mop.neutral: I'm Mop. And this is--
bucket.neutral: --Bucket. We're twins.
mop.happy: We finish each other's--
bucket.happy: --sentences! Isn't that neat?
:e_end
end
:nell_talk
if z4_done goto nell_after
nell.neutral: The Hushmother keeps the depths dim. Lamps here don't flicker. They SLEEP. It's not cruel. It's kind. {p}They remember things that hurt.
nell.sad: I keep a library of the things the lamps remember. Gentle things only. I read them out loud at night. It helps.
nell.neutral: The Hushmother's lair is east. She'll want you to whisper. I recommend whispering.
end
:nell_after
nell.happy: The lamps are glowing. They remember! Some of it hurts. Some of it is the best thing I've ever read.
end
:fenn_talk
fenn.neutral: Tea, oil, rocks, buns. Whisper your order.
shop deep
end
:mop_talk
mop.happy: Bucket and I have a game.
bucket.happy: We pretend we're not twins. Then we both laugh and it ruins everything.
end
:bucket_talk
bucket.neutral: Mop thinks the Hushmother's scary. I think she's lonely.
mop.sad: ...Same. We always agree, eventually.
end
:eel_talk
eelfolk.neutral: Whisper. Whisper. Shh. Shh. The lamps are dreaming.
end
:sign_talk
narr: A violet sign, whisper-soft: 'Quiet hours: always. Fines: gentle.'
end
""")

W.mapdef('depths1', 'deep', [
 "################",
 "#.e..........e.#",
 "#..............#",
 "#...xxxxxx.....#",
 "#...xxxxxx.....#",
 "#..............#",
 "................",
 "#..............#",
 "#..k...xxxx....#",
 "#......xxxx....#",
 "#.e..........e.#",
 "################"], 'depths_dark', enc=4, rate=3,
 ents=[SPOT('sign', 3, 2, 'sign_talk'), EXIT('towest', 0, 6, 1, 1, 'glimmer_town', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'depths2', 1, 6, 'right')],
 script="""
:enter
set zone 4
end
:sign_talk
narr: A whisper-sign: 'The lamps here sleep. Please don't wake the lamps. Wake the people, if you must.'
end
""")

W.mapdef('depths2', 'deep', [
 "################",
 "#.e..........e.#",
 "#..............#",
 "#..............#",
 "#.........._...#",
 "#..............#",
 "................",
 "#..............#",
 "#.........._...#",
 "#..............#",
 "#.k..........k.#",
 "################"], 'depths_dark', plate_var='z4_block', plates=[(10, 4), (10, 8)],
 ents=[BLOCK('b1', 5, 4), BLOCK('b2', 5, 8), DOOR('gate', 14, 6, ngate='z4_block'), SPOT('secret', 2, 1, 'secret_talk', ngate='z4_shell'),
       EXIT('towest', 0, 6, 1, 1, 'depths1', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'depths3', 1, 6, 'right')],
 script="""
:enter
set zone 4
end
:secret_talk
sfx light
set z4_shell 1
inc shells
narr: Tucked behind a glowing crystal, almost invisible: a MEMORY SHELL. It hums a verse about a cradle of dark water.
wick.sad: It's the oldest one yet. It sounds like... someone tucking someone in.
end
""")

W.mapdef('depths3', 'deep', [
 "################",
 "#..............#",
 "#.y..y....y..y.#",
 "#..............#",
 "#...xxxxxxxx...#",
 "#..............#",
 "................",
 "#..............#",
 "#...y......y...#",
 "#..............#",
 "#.e..........e.#",
 "################"], 'depths_dark', enc=4, rate=3,
 ents=[ZONE('skiffz', 8, 4, 1, 4, 'skiff_scene', ngate='z4_skiff'), NPC('skiff', 'skiff', 11, 6, 'skiff_talk', gate='z4_skiff_here'),
       EXIT('towest', 0, 6, 1, 1, 'depths2', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'lumen_lair', 1, 6, 'right')],
 script="""
:enter
set zone 4
end
:skiff_scene
set z4_skiff 1
if skiff_dead goto sk_gone
set z4_skiff_here 1
show skiff
music rival
skiff.sad: I thought I was ahead of you. Then I got lost. Then I got scared. In that order.
skiff.neutral: My lantern. It doesn't flicker because it isn't mine. A voice gave it to me. Said it'd help me find somebody who'd listen.
wick.surprised: ...
skiff.sad: Is that what you are, too? A borrowed light?
if skiff_ally goto sk_join
skiff.angry: Doesn't matter! I'll still beat you to the Hollow Light!
battle skiff2
if lastbt == 1 goto sk_spared
if lastbt == 0 goto sk_killed
end
:sk_spared
set skiff_ally 1
:sk_join
set skiff_friend 1
skiff.happy: ...Okay. Friends. For now. Don't make it weird.
skiff.neutral: I'll be at the Archive. Come find me when you've done the deep thing.
hide skiff
set z4_skiff_here 0
music depths_dark
end
:sk_killed
set skiff_dead 1
narr: A steady glow gutters, dims, and goes out in the dark.
hide skiff
set z4_skiff_here 0
music depths_dark
end
:sk_gone
narr: The tunnel is empty. A single scorch mark on the floor, in the shape of someone who ran fast.
end
:skiff_talk
end
""")

W.mapdef('lumen_lair', 'deep', [
 "################",
 "#.e..........e.#",
 "#..............#",
 "#..............#",
 "#..............#",
 "#..............#",
 "................",
 "#..............#",
 "#..............#",
 "#.k..........k.#",
 "#..............#",
 "################"], 'depths_dark',
 ents=[NPC('lumen', 'lumen', 7, 3, 'lumen_talk', ngate='z4_boss_gone'), ZONE('intro', 3, 5, 1, 3, 'lumen_intro', ngate='z4_boss_seen'), SAVE('post', 2, 8),
       EXIT('towest', 0, 6, 1, 1, 'depths3', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'archive_lobby', 1, 6, 'right', gate='z4_done')],
 script="""
:enter
set zone 4
end
:lumen_intro
set z4_boss_seen 1
music mystery
lumen.neutral: Shh. Shhh. Please. You're so bright. It hurts to look at you.
lumen.sad: I am the Hushmother. I keep the lamps asleep. When a lamp wakes, it remembers. When it remembers, it hurts.
wick.sad: She's... protecting them.
lumen.sad: The Warden asked me, long ago. 'Keep the lamps low, Hushmother, so they won't ask what we did.' I am very good at my job.
lumen.angry: Don't wake them. DON'T WAKE THEM. I won't let you. I'm SORRY.
music boss_lumen
sfx boss
battle lumen
if lastbt == 1 goto spared
goto killed
:spared
set z4_done 1
set z4_boss_gone 1
music depths_town
lumen.sad: ...They're glowing. They remember. It does hurt. But they're singing. Are you hearing that?
lumen.neutral: The Warden kept the Archive's first records. Quill will have them. Ask for the Decree of Ebb.
lumen.happy: Go. Please. And tell them I'm sorry I kept them so quiet.
set zone 5
end
:killed
set z4_done 1
set z4_boss_gone 1
music depths_dark
narr: The Hushmother dims. All across the Hollow, the lamps go out, one by one, like a held breath finally released.
end
:lumen_talk
lumen.neutral: Shh.
end
""")

W.battle('gloamfin', shown='Gloamfin', gfx='gloamfin', hp=30, atk=3, exp=9, gold=11, music='battle',
 pal=['#E8D8FF', '#A878E8', '#5A3A98', '#0C0B14'],
 patterns=[closing(5, 14, 48, 8, 40, gfx='orb'), aimed(5, 22, 22, n=3, spread=28, gfx='orb'), rain(5, 18, 9, gfx='orb'), ring(5, 14, 42, 10, gfx='orb', spiral=9), side(5, 22, 11, gfx='orb')],
 listen=[('Check', 'check'), ('Dim Lamp', 'dim'), ('Ignore', 'ignore'), ('Hold On', 'hold')],
 script="""
:intro
flavor "A Gloamfin hangs in the dark. A little light bobs in front of its face, like bait."
end
""" + turn(5, {0: "The lure closes in. Everything closes in.", 1: "Lights aimed straight at you. It's very honest about it.", 2: "Lights drift down like snow.", 3: "A slow spiral of lights.", 4: "Lights from the side. It's coaxing you."},
   pre="""if bt_f0 == 0 goto tpre_end
if bt_shield < 3 goto tpre_end
spareable 1
flavor "You've shielded every light. The Gloamfin sighs. It wanted to be seen without wanting to catch you. (Ready to let go.)"
end
:tpre_end
""") + """
:check
flavor "GLOAMFIN. ATK 3. Lonely hunter. Its light is its only friend."
end
:dim
bflag 0
flavor "You dim your lantern. The Gloamfin's lure droops. Now shield its lights with B, so it knows you're not hungry."
end
:ignore
flavor "You ignore the lure. The Gloamfin pouts. It was a very good lure."
end
:hold
if bt_f0 goto hold_ok
flavor "You say 'hold on.' It doesn't understand. Dim your lamp first."
end
:hold_ok
flavor "You say 'hold on.' It listens. Shield three lights this round."
end
:win
flavor "The Gloamfin's lure goes out. It was the only light it had."
end
:spared
flavor "The Gloamfin drifts away, its lure bright and unthreatening."
end
""")

W.battle('skiff2', shown='Skiff', gfx='skiff', hp=60, atk=4, exp=14, gold=20, music='rival', flags=1,
 pal=['#C8F0FF', '#4A98C8', '#1A3050', '#0C0B14'],
 patterns=[aimed(5, 28, 14, n=3, spread=26, gfx='star'), side(5, 28, 9, gfx='star'), ring(5, 18, 30, 12, gfx='star', spiral=15), wall(5, 18, 34, 9, gfx='bar'), closing(5, 16, 44, 10, 44, gfx='star')],
 listen=[('Check', 'check'), ('Lantern', 'lantern'), ('Friend', 'friend'), ('Share', 'share')],
 script="""
:intro
flavor "Skiff clenches their fists. Their lantern flickers, for the first time."
end
""" + cyc(5, {0: "Skiff goes faster. And faster. Faster than makes sense.", 1: "A sideways blitz. Courier express.", 2: "Skiff spins: stars everywhere.", 3: "A moving wall. Skiff is very proud of it.", 4: "Skiff closes the distance. It's not fear. It's longing."}) + """
:check
flavor "SKIFF. ATK 4. A borrowed light, a very real heart."
end
:lantern
bflag 0
flavor "You ask about the lantern. 'It's not mine.' Skiff's hand shakes. 'But it doesn't feel borrowed.'"
end
:friend
if bt_f0 goto friend_ok
flavor "You say 'we could be friends.' Skiff scoffs. Maybe ask about the lantern first."
end
:friend_ok
bflag 1
flavor "You say 'we could be friends.' Skiff's lantern flickers, warm and real."
end
:share
if bt_f1 goto share_ok
flavor "You offer to share your light. Skiff says no. Not yet."
end
:share_ok
spareable 1
flavor "You offer to share your light. Skiff takes your hand. (Ready to let go.)"
end
:win
flavor "Skiff drops. Their lantern, borrowed, fades quietly."
end
:spared
flavor "Skiff exhales. The lantern settles. It looks like theirs now."
end
""")

W.battle('lumen', shown='Hushmother', gfx='lumen', hp=140, atk=4, exp=28, gold=60, music='boss_lumen', flags=1 | 2,
 pal=['#F0E0FF', '#B880F0', '#5A3098', '#0C0B14'],
 patterns=[closing(6, 14, 46, 10, 44, gfx='orb'), aimed(6, 22, 18, n=3, spread=32, gfx='orb'), rain(6, 18, 7, gfx='drop'), ring(6, 14, 36, 12, gfx='orb', spiral=12),
           side(6, 24, 8, gfx='orb'), wall(6, 14, 34, 9, gfx='orb')],
 listen=[('Check', 'check'), ('Dim Lamp', 'dim'), ('Hush', 'hush'), ('Remember', 'remember')],
 script="""
:intro
flavor "The Hushmother's light flickers through a dark so deep it has depth."
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
flavor "The dark closes around you, gently."
end
:t1
attack 1
flavor "Her lures aim carefully. She's sorry. She's aiming anyway."
end
:t2
attack 2
flavor "Drops of light fall, slowly. Each one is a memory."
end
:t3
attack 3
flavor "A spiral of remembered things."
end
:t4
attack 4
flavor "Lights from the side. They don't mean to hurt."
end
:t5
attack 5
flavor "A wall of hush. Very soft. Very final."
end
:mid1
lumen.angry: STOP WAKING THEM! They'll REMEMBER! They'll remember what he DID!
box 14 4
layers 7
goto go
:mid2
lumen.sad: I only wanted them to rest. I only wanted... a quiet place for everyone who ever hurt.
box 8 6
layers 15
goto go
:check
flavor "HUSHMOTHER. ATK 4. Keeps the lamps asleep. Fear of: what they remember."
end
:dim
bflag 0
flavor "You dim your own lantern, low as it goes. She stops, startled. 'You... are not afraid of the dark?'"
end
:hush
bflag 1
flavor "You hush with her. Whisper to the dark. She softens. 'You understand.'"
end
:remember
if bt_f0 == 0 goto remember_no
if bt_f1 == 0 goto remember_no
bflag 2
spareable 1
flavor "You tell her it's okay for the lamps to remember, if someone's there when they do. She's crying light. (Ready to let go.)"
end
:remember_no
flavor "You ask her to remember. She flinches. She needs to trust you first. (Dim, then hush.)"
end
:win
lumen.sad: ...Quiet. Finally. {p}Quiet.
flavor "The Hushmother dims. The depths go silent."
end
:spared
lumen.neutral: ...Thank you.
end
""")
W.encounters(4, ['gloamfin', 'lampfly', 'gloamfin', 'lampfly'])
