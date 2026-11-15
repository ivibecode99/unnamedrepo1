from world import W
from lib import *
from util import *

W.mapdef('coral_square', 'reef', [
 "################",
 "#oo..,,..,,..oo#",
 "#o..s....l...k.#",
 "#....,,....,,..#",
 "#.k.....t......#",
 "#....l.....l...#",
 "#..,,.......,,..",
 "#..............#",
 "#.o..........k.#",
 "#..,,..b.......#",
 "#..............#",
 "#....,,..,,....#",
 "#..............#",
 "#######..#######"], 'coralline',
 ents=[NPC('pip', 'pip', 7, 11, 'pip_talk'), NPC('tuck', 'tuck', 8, 3, 'tuck_talk'), NPC('tangle', 'tangle', 3, 6, 'tangle_talk'),
       NPC('crab', 'crabfolk', 11, 9, 'crab_talk'), NPC('urchin', 'urchinfolk', 5, 9, 'urchin_talk'),
       SAVE('post', 2, 11), SPOT('sign', 4, 2, 'sign_talk'),
       EXIT('toshore', 7, 13, 2, 1, 'shore2', 7, 2, 'down'), EXIT('toreef', 15, 6, 1, 1, 'reef1', 1, 6, 'right')],
 script="""
:enter
set zone 1
if z1_intro goto enter_end
set z1_intro 1
pip.happy: Welcome to CORALLINE! Population: me, plus some people!
pip.neutral: I'm Pip, official greeter. Unofficial everything else. Is that a lantern? It's tiny. It's adorable.
wick.angry: It's a WICK. And I'm right here.
pip.surprised: It TALKS! Mayor Ruffle's going to LOVE you. She loves anything that glows. She loves it so much she keeps it.
pip.sad: ...Not that that's a worrying thing to say. Pretend I said something cheerful.
if ng > 0 goto pip_ngplus
end
:pip_ngplus
pip.surprised: Wait, hold on. Haven't I greeted you before? I feel like I've said all this and you were nicer about it.
end
:enter_end
if z1_done goto enter_after
end
:enter_after
pip.happy: The lamps are back! Look at them all! Welcome to CORALLINE, where the lights are on and someone is home!
end
:pip_talk
if z1_done goto pip_after
if bosskills > 0 goto pip_scared
pip.neutral: The mayor's hall is past the Sponge Warren, east gate. {p}Don't touch the walls. They're alive. Allegedly.
pip.happy: Also: my lantern's been flickering. If you see the mayor, ask about the Lottery. Everyone gets picked eventually!
end
:pip_after
pip.happy: Mayor Ruffle gave my lantern back! Look, it's brighter than before! Here, a thank-you.
if z1_pip_gift goto pip_gifted
set z1_pip_gift 1
give "Brine Tea"
pip.surprised: Take the tea! It's warm. It's the only warm thing in the whole reef.
end
:pip_gifted
pip.happy: Population: me, plus MORE people now! Allegedly. I counted.
end
:pip_scared
pip.sad: You... did something, didn't you. I can tell. Your lantern flickers when you walk. {p}Please don't look at me like that.
end
:tuck_talk
tuck.neutral: Salt-bun? Kelp wrap? Pearls for the lonely? I've got a little of everything and a lot of opinions.
tuck.happy: Welcome, dearie. Browse. Weep. Buy something small.
shop coral
tuck.neutral: Mind the gap in the reef wall, east side. Skiff's been racing through it all week, scaring the barnacles.
end
:tangle_talk
if z1_shell goto tangle_shell
tangle.neutral: Allegedly the Mayor takes your lantern if it gets too dim. Allegedly it keeps it safe. Allegedly.
tangle.happy: Allegedly, a shell was hidden in the warren where the tide used to pool. Past the gate, northeast corner.
tangle.neutral: Allegedly I don't gossip. I just narrate.
end
:tangle_shell
tangle.surprised: A Memory Shell! You found it! Hold it to your ear. {p}Allegedly it hums a song the sea used to sing.
end
:crab_talk
if z1_done goto crab_after
crabfolk.sad: My lantern went to the vault last week. I keep reaching for it, like a pocket. {p}It's quiet in here without it.
end
:crab_after
crabfolk.happy: Got my lantern back! I remembered my mother's birthday. It was in March. Or Tuesday.
end
:urchin_talk
urchinfolk.neutral: They say the sea left because it got tired of us. {p}I say it left because we never wrote.
end
:sign_talk
narr: CORALLINE. Founded by someone, someday. Ask the mayor.
end
""")

W.mapdef('reef1', 'reef', [
 "################",
 "#..o..xx#..k...#",
 "#..k..xx#......#",
 "#.....xx#..,,..#",
 "#..xxxxx#......#",
 "#..xxxxx.......#",
 "...xxxxx#.......",
 "#.....xx#..o...#",
 "#..k..xx#......#",
 "#.l....x#..l...#",
 "#.......#......#",
 "################"], 'reefcave', enc=1, rate=3,
 ents=[SPOT('lever', 5, 10, 'lever_talk'), DOOR('door', 8, 5, ngate='z1_gate'), SPOT('shell', 14, 1, 'shell_get', ngate='z1_shell'), NPC('skiff', 'skiff', 12, 5, 'skiff_cave', gate='z1_skiff_cave'),
       ZONE('skiffzone', 9, 4, 1, 3, 'skiff_meet', ngate='z1_skiff_met'), EXIT('towest', 0, 6, 1, 1, 'coral_square', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'reef2', 1, 10, 'right')],
 script="""
:enter
set zone 1
end
:lever_talk
if z1_gate goto lever_done
narr: A rusty lever sticks out of the coral. It looks like it has opinions about being pulled.
sfx door
shake 12 1
set z1_gate 1
narr: CLUNK. Somewhere, a coral gate groans open.
end
:lever_done
narr: The lever is stuck. Fair enough. It did its job.
end
:skiff_meet
set z1_skiff_met 1
set z1_skiff_cave 1
show skiff
skiff.happy: Too slow again! I already pulled the lever. Twice.
skiff.neutral: Hey, got a question. Your lantern: does it ever feel... heavy?
wick.angry: He asked me something rude.
skiff.sad: Mine doesn't flicker. Ever. Everyone says that's lucky. I don't remember getting it. {p}Weird, right?
skiff.angry: Anyway! Race you to the vault! Loser buys the winner a bun.
hide skiff
set z1_skiff_cave 0
end
:skiff_cave
end
:shell_get
sfx light
set z1_shell 1
inc shells
narr: Wedged in the coral: a MEMORY SHELL. It hums, very faintly, in a voice like a long breath out.
wick.surprised: It remembers the sea. {p}Keep it. Keep it close. I have a feeling about it.
end
""")

W.mapdef('reef2', 'reef', [
 "#######.########",
 "#..............#",
 "#..o..........o#",
 "#..s...........#",
 "#.........._...#",
 "#..............#",
 "#..............#",
 "#.........._...#",
 "#..............#",
 "#..k.......k...#",
 "................",
 "################"], 'reefcave', plate_var='z1_block', plates=[(10, 4), (10, 7)],
 ents=[BLOCK('b1', 5, 4), BLOCK('b2', 5, 7), DOOR('door', 7, 1, ngate='z1_block'), SPOT('sign', 3, 3, 'sign_talk'),
       EXIT('towest', 0, 10, 1, 1, 'reef1', 14, 6, 'left'), EXIT('tonorth', 7, 0, 1, 1, 'reef3', 7, 10, 'up')],
 script="""
:enter
set zone 1
end
:sign_talk
narr: CARVED IN THE WALL: 'Two stones, two hollows. Push, don't pull. (Pulling is for fish.)'
end
""")

W.mapdef('reef3', 'reef', [
 "#######.########",
 "#..............#",
 "#..k........k..#",
 "#...l...l...l..#",
 "#..............#",
 "#..xxxxxxxx....#",
 "#..xxxxxxxx....#",
 "#..............#",
 "#..o........o..#",
 "#..............#",
 "#..............#",
 "#######.########"], 'reefcave', enc=1, rate=3,
 ents=[SPOT('l0', 4, 3, 'lamp0'), SPOT('l1', 8, 3, 'lamp1'), SPOT('l2', 12, 3, 'lamp2'), DOOR('door', 7, 1, ngate='z1_lamps'),
       EXIT('tonorth', 7, 0, 1, 1, 'ruffle_hall', 7, 10, 'up'), EXIT('tosouth', 7, 11, 1, 1, 'reef2', 7, 1, 'down')],
 script="""
:enter
set zone 1
end
""" + lantern_puzzle('lamp', [1, 2, 0], 'z1_lamps', 'z1_seq', ['shy', 'loud', 'proud'],
   ["I'm shy... {p}please light me first. Light the loud one second. Never light the proud one before the others.",
    "I'M LOUD! I'M THE MIDDLE ONE! LIGHT ME AFTER THE SHY ONE! (The proud one goes last.)",
    "I'm the proud one. Obviously I go last. {p}Obviously."][::-1] if False else
   ["Quiet, and a little scared: 'Light me last. I'm proud, but only when the others are lit.'",
    "Soft: 'Please, me first. I'm shy. The loud one comes after me.'",
    "Booming: 'THE LOUD ONE GOES IN THE MIDDLE! AFTER THE SHY ONE!'"],
   "A gate groans open to the north. It smells like old lamp oil and someone's perfume."))

W.mapdef('ruffle_hall', 'reef', [
 "#######.########",
 "#.l..........l.#",
 "#..............#",
 "#.o.........o..#",
 "#..............#",
 "#......,.......#",
 "#..............#",
 "#.k..........k.#",
 "#..............#",
 "#..............#",
 "#..............#",
 "#######.########"], 'coralline',
 ents=[NPC('ruffle', 'ruffle', 7, 3, 'ruffle_talk', ngate='z1_boss_gone'), ZONE('intro', 5, 7, 5, 1, 'ruffle_intro', ngate='z1_boss_seen'), SAVE('post', 2, 9),
       EXIT('toprev', 7, 11, 1, 1, 'reef3', 7, 2, 'down'), EXIT('tohull', 7, 0, 1, 1, 'hull_dock', 7, 12, 'up', gate='z1_done')],
 script="""
:enter
set zone 1
if z1_boss_seen goto e1
end
:e1
end
:ruffle_intro
set z1_boss_seen 1
music mystery
ruffle.happy: Ooh! A visitor! And a little lantern! Come in, come in, mind the pile.
narr: Behind her, thousands of lanterns hang from the ceiling like a frozen rain. They glow so softly it looks like breathing.
ruffle.neutral: The Lamp Lottery! Everyone donates a lantern. They're just resting here. Safe and warm. {p}Forever.
wick.sad: They're all... very quiet.
ruffle.sad: Dearie. Dimming lamps mean forgetting. I couldn't let my town forget. Nobody remembers why the sea left. If the lamps go out, we go out too.
ruffle.angry: So no. I won't give them back. And I do NOT like it when people try to take the nice quiet lights away!
music boss_ruffle
sfx boss
battle ruffle
if lastbt == 1 goto spared
goto killed
:spared
set z1_done 1
set z1_boss_gone 1
music coralline
ruffle.sad: ...Oh. Oh dear. I've been holding them so tight. They don't even glow when I squeeze.
ruffle.happy: Go on, everyone. Go home. Go be remembered.
sfx release
flash 10
narr: The lanterns drift out through the hall's windows like a slow, bright tide.
ruffle.neutral: Little lantern. Child. {p}The Warden at the Hollow Light collected our FIRST lamps, long ago. For the Tide, he said. Nobody remembers what for.
ruffle.neutral: Find him. And mind the next town. They take tolls down at the hull docks. Of EVERYTHING.
set zone 2
end
:killed
set z1_done 1
set z1_boss_gone 1
music reefcave
wick.sad: The lanterns are still hanging. They aren't glowing anymore.
narr: A single lamp falls and rolls to your feet. It's cold.
wick.sad: ...Come on. Let's get out of here.
end
:ruffle_talk
ruffle.neutral: Hm? Oh, you're back. Do try the lantern shop. It's open until the sea returns.
end
""")

W.battle('spitwink', shown='Spitwink', gfx='spitwink', hp=20, atk=2, exp=5, gold=7, music='battle',
 pal=['#D8F0C8', '#8CC878', '#3E7A4A', '#0C0B14'],
 patterns=[aimed(5, 22, 24, gfx='bubble'), side(5, 22, 12, gfx='bubble'), rain(5, 18, 10, gfx='bubble'), ring(5, 14, 46, 8, gfx='bubble')],
 listen=[('Check', 'check'), ('Cheer', 'cheer'), ('Catch', 'catch')],
 script="""
:intro
flavor "A Spitwink pops out of the sand. It looks awfully embarrassed to be here."
end
""" + turn(4, {0: "Bubbles. Lots of bubbles. All of them aimed at you.", 1: "The Spitwink spits sideways. Showing off.", 2: "It rains bubbles. Technically a weather event.", 3: "A ring of bubbles. A tiny party, uninvited."},
   pre="""if bt_f0 == 0 goto tpre_skip
if bt_shield < 2 goto tpre_skip
spareable 1
flavor "It's out of breath and smiling. It would love a hug. (It'll settle for RELEASE.)"
end
:tpre_skip
""") + """
:check
flavor "SPITWINK. ATK 2. Spits when nervous. Always nervous."
end
:cheer
bflag 0
flavor "You cheer for its aim! It blushes mud. It wants to play catch (shield its bubbles!)."
end
:catch
if bt_f0 goto catch_ok
flavor "It doesn't know what you mean. Maybe cheer first? Cheerleaders go first."
end
:catch_ok
flavor "You nod. It spits. Block twice with B and it'll know you're playing."
end
:win
flavor "The Spitwink goes pop. A small cloud of water vapour. Oh. It was thirsty."
end
:spared
flavor "It spits a goodbye bubble. It shines like a promise."
end
""")

W.battle('lampfly', shown='Lampfly', gfx='lampfly', hp=18, atk=2, exp=5, gold=6, music='battle',
 pal=['#FFF2C8', '#FFC85A', '#9A5A2A', '#0C0B14'],
 patterns=[rain(5, 16, 14, gfx='star'), ring(5, 14, 40, 10, gfx='star', spiral=7), closing(5, 14, 52, 8, 40, gfx='star'), aimed(5, 20, 22, n=3, spread=24, gfx='star')],
 listen=[('Check', 'check'), ('Hum', 'hum'), ('Dim Light', 'dim')],
 script="""
:intro
flavor "A Lampfly drifts toward your flame. It thinks you're the sun."
end
""" + turn(4, {0: "Glittering dust falls from its wings.", 1: "The Lampfly spirals closer to your flame.", 2: "It circles you. Dizzy, devoted.", 3: "Three sparks. Aimed. Very sincere."}) + """
:check
flavor "LAMPFLY. ATK 2. Loves light. Cannot tell the difference between love and fire."
end
:hum
if bt_f0 goto hum2
bflag 0
flavor "You hum. The Lampfly slows. It likes this."
end
:hum2
if bt_f1 goto hum_ok
bflag 1
flavor "You hum louder. Its wings fold a little. Maybe dim your light now?"
end
:hum_ok
flavor "It's already calm. Let it settle."
end
:dim
if bt_f1 goto dim_ok
flavor "You dim your flame. The Lampfly panics, then calms. It needs the hum first."
end
:dim_ok
spareable 1
flavor "You dim your light. It lands on your shoulder like a very small, very warm hat. (Ready to go.)"
end
:win
flavor "The Lampfly's glow gutters out. It was only trying to be near you."
end
:spared
flavor "It flutters out toward the reef. Every light it passes brightens, just a little."
end
""")

W.battle('ruffle', shown='Mayor Ruffle', gfx='ruffle', hp=90, atk=3, exp=20, gold=40, music='boss_ruffle', flags=1 | 2,
 pal=['#FFE0EC', '#F2789E', '#8A2A5A', '#0C0B14'],
 patterns=[aimed(6, 22, 20, n=3, spread=24, gfx='star'), rain(6, 18, 8, n=1, gfx='drop'), wall(6, 14, 34, 8, gfx='orb'), ring(6, 14, 36, 10, gfx='star', spiral=11),
           side(6, 22, 9, gfx='star'), closing(6, 14, 46, 10, 44, gfx='orb')],
 listen=[('Check', 'check'), ('Admire', 'admire'), ('Ask', 'ask'), ('Reassure', 'reassure')],
 script="""
:intro
flavor "Mayor Ruffle bristles. A thousand lanterns glow behind her."
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
flavor "Ruffle's tentacles ripple. Prettily."
end
:t1
attack 1
flavor "Drops fall. Pink and perfect."
end
:t2
attack 2
flavor "A curtain of lamps. She is very proud of it."
end
:t3
attack 3
flavor "Ruffle spins. Everything glitters."
end
:t4
attack 4
flavor "She hurls stars from the sides. Show-off."
end
:t5
attack 5
flavor "The lamps close in. Gently. Threateningly. Gently."
end
:mid1
ruffle.angry: Stop LOOKING at them! They're mine! They're SAFE with me!
box 14 4
layers 7
goto go
:mid2
ruffle.sad: Do you know what it's like? To be the one who remembers? It's heavy. It's heavy and it hums.
box 8 6
layers 15
goto go
:check
flavor "MAYOR RUFFLE. ATK 3. Collects lanterns so no one forgets. Fears being forgotten most."
end
:admire
bflag 0
flavor "You admire the lantern hall. She glows. She blinks. 'You noticed?'"
end
:ask
bflag 1
flavor "You ask about the Lottery. She goes quiet. 'They were flickering. I couldn't bear it.'"
end
:reassure
if bt_f0 == 0 goto reassure_no
if bt_f1 == 0 goto reassure_no
bflag 2
spareable 1
flavor "You promise lamps don't go out when they're loved, only when they're held too tight. She's trembling. (Ready to let go.)"
end
:reassure_no
flavor "You try to comfort her. She doesn't believe you. Try listening first."
end
:win
ruffle.sad: ...I only wanted everyone to stay. {p}Stay.
flavor "Mayor Ruffle dims. The lanterns around her dim with her."
end
:spared
ruffle.neutral: ...Thank you.
end
""")
W.encounters(1, ['spitwink', 'lampfly', 'spitwink', 'lampfly'])
