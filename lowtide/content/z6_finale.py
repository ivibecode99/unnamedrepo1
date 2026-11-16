from world import W
from lib import *
from util import *

W.mapdef('light_shore', 'light', [
 "#######..#######",
 "#.y..........y.#",
 "#..............#",
 "#..xxxxxxxx....#",
 "#..xxxxxxxx....#",
 "#..............#",
 "................",
 "#..............#",
 "#.l..........l.#",
 "#..............#",
 "#.u..........u.#",
 "################"], 'lighthouse', enc=6, rate=3,
 ents=[NPC('gaff', 'gaff', 3, 9, 'gaff_talk'), NPC('skiff', 'skiff', 12, 9, 'skiff_talk', gate='skiff_friend'), SAVE('post', 12, 5), SPOT('sign', 3, 2, 'sign_talk'),
       EXIT('towest', 0, 6, 1, 1, 'quill_chamber', 14, 6, 'left'), EXIT('toup', 7, 0, 2, 1, 'light_tower1', 7, 10, 'up')],
 script="""
:enter
set zone 6
if z6_intro goto e_end
set z6_intro 1
narr: THE HOLLOW LIGHT. A lighthouse so tall it has weather of its own. At its base, the sand is wet. Just here. Just a little.
wick.surprised: She's close. I can feel her. It's like... when you're sure someone just left the room.
if ng > 0 goto e_ng
end
:e_ng
wick.sad: We've been here before. Haven't we? I keep almost remembering the stairs.
:e_end
end
:gaff_talk
gaff.happy: Ha! There you are, kid. I walked ALL this way, with the bucket. {p}It's no use. But it's company.
gaff.neutral: When the sea comes back, I'm going to fish in it for an hour. Just an hour. No fish. Only the sitting.
if bosskills > 0 goto gaff_sad
gaff.neutral: Kind folk all along the way, they tell me. The lanterns remember that, you know.
end
:gaff_sad
gaff.sad: Folks talk. You left some lights out on the way. {p}I don't hold with that. But I hold with you. Go on.
end
:skiff_talk
skiff.happy: I'll hold the door. You do the thing. If I hear screaming, I'll assume it's the good kind.
end
:sign_talk
narr: A sign, rusted solid: 'TO THE LIGHT. 400 STEPS. NO REFUNDS. (THE LIGHT IS NOT INCLUDED.)'
end
""")

W.mapdef('light_tower1', 'light', [
 "#######.########",
 "#.y..........y.#",
 "#..............#",
 "#..............#",
 "#..........._..#",
 "#..............#",
 "#..............#",
 "#..._..........#",
 "#..............#",
 "#.l..........l.#",
 "#..............#",
 "#######..#######"], 'lighthouse', enc=6, rate=3, plate_var='z6_block', plates=[(4, 7), (12, 4)],
 ents=[BLOCK('b1', 8, 5), BLOCK('b2', 8, 8), DOOR('gate', 7, 1, ngate='z6_block'), EXIT('tosouth', 7, 11, 2, 1, 'light_shore', 7, 1, 'down'), EXIT('tonorth', 7, 0, 1, 1, 'light_tower2', 7, 10, 'up')],
 script=""":enter
set zone 6
end
""")

W.mapdef('light_tower2', 'light', [
 "#######.########",
 "#.e..........e.#",
 "#..............#",
 "#..............#",
 "#..............#",
 "#.y..........y.#",
 "#..............#",
 "#..............#",
 "#..............#",
 "#.e..........e.#",
 "#..............#",
 "#######.########"], 'musicbox',
 ents=[ZONE('f1', 4, 7, 8, 1, 'flash1', ngate='z6_f1'), ZONE('f2', 4, 5, 8, 1, 'flash2', ngate='z6_f2'), ZONE('f3', 4, 3, 8, 1, 'flash3', ngate='z6_f3'),
       SAVE('post', 2, 9), EXIT('tosouth', 7, 11, 1, 1, 'light_tower1', 7, 1, 'down'), EXIT('tonorth', 7, 0, 1, 1, 'lantern_room', 7, 10, 'up', gate='z6_f3')],
 script=""":enter
set zone 6
end
:flash1
set z6_f1 1
narr: The stairs are lined with lamps, and every lamp is a window. In the first one: a hatchling, floating in black water.
narr: A voice that is mostly weather says, very softly: 'There you are.'
marrow.happy: She carried me home. The whole sea carried me home, one tide, in her arms.
end
:flash2
set z6_f2 1
narr: In the second window, an enormous, tired presence lies down beside a lighthouse and does not get up.
narr: 'My love, I'm tired. Let me go out. Let me rest. I'll be a different tide.'
marrow.sad: And I said no. {p}I said no, no, no.
end
:flash3
set z6_f3 1
narr: In the third window, a child with a stray flame stands very still at the edge of the surf. The surf is warm. The flame is small.
narr: The sea whispers: 'Keep this light. Find someone who'll listen. When they do, tell them I'm sorry I took so long.'
wick.surprised: ...That's me. {p}That's... I'm the light she sent. I'm the last spark of her.
wick.sad: I've been trying to remember why I woke up on the dry seabed with you. I was supposed to find the one who'd hear the goodbye.
narr: The child in the window turns. The kid in the window is you.
wick.happy: She carried you home once. That's why the light chose you. {p}She remembered you. She wanted you to remember her.
end
""")

W.mapdef('lantern_room', 'light', [
 "################",
 "#.e..........e.#",
 "#..............#",
 "#..............#",
 "#......uu......#",
 "#..............#",
 "#..............#",
 "#..............#",
 "#..............#",
 "#.l..........l.#",
 "#..............#",
 "#######.########"], 'lighthouse',
 ents=[NPC('marrow', 'marrow', 7, 3, 'marrow_talk', ngate='z6_boss_gone'), ZONE('intro', 5, 7, 5, 1, 'marrow_intro', ngate='z6_boss_seen'), EXIT('tosouth', 7, 11, 1, 1, 'light_tower2', 7, 1, 'down')],
 script=""":enter
set zone 6
end
:marrow_intro
set z6_boss_seen 1
music mystery
narr: At the top of the Hollow Light: a lantern the size of a house. Inside it, a tide, standing very still. A turtle, hunched at its base, hums under his breath.
marrow.neutral: You came up the stairs. They never do. Most turn back at the tenth landing.
if ng > 0 goto m_ng
:m_cont
marrow.sad: You've seen the windows. You know. The Sea is tired and I am selfish.
marrow.neutral: She carried me home once. When I was too small to know I was lost. I lit this lamp for her. I've kept it lit since.
marrow.angry: I will NOT hold the door while she leaves. I WILL NOT.
wick.sad: Please. She asked. She asked so nicely.
marrow.angry: Then I will ask nicer. With a LAMP.
music boss_marrow
sfx boss
battle marrow
chunk ending_router
:m_ng
marrow.surprised: ...You've been here. I know the shape of your light.
if prev_ending == 1 goto m_ng1
if prev_ending == 2 goto m_ng2
if prev_ending == 3 goto m_ng3
marrow.sad: Last time, the sea went out. I thought I'd know what to do the second time.
goto m_cont
:m_ng1
marrow.sad: Last time you were kind. I thought about it for a long time. I'm still here. {p}I'm still stuck.
goto m_cont
:m_ng2
marrow.sad: Last time, half of it went right. Half of it didn't. I keep dreaming of the half.
goto m_cont
:m_ng3
marrow.sad: Last time you broke her lantern. I remember the sound. I'd like to not hear it again.
goto m_cont
:marrow_talk
marrow.neutral: The Sea is waiting. So am I.
end
""")

W.scene('ending_router', """
if lastbt == 0 goto end_fight
if bosskills > 0 goto end_neutral
if kills > 3 goto end_neutral
if true_sing == 0 goto end_peace
if kills > 0 goto end_peace
if skiff_friend == 0 goto end_peace
goto end_true
:end_peace
chunk ending_peace
:end_neutral
chunk ending_neutral
:end_fight
chunk ending_fight
:end_true
chunk ending_true
""")
W.scene('ending_peace', """
fade out
music end_peace
warpk sea_shore 7 9 up
fade in
narr: The Great Lantern dims, softly, and the tide inside it breathes out.
marrow.sad: Go on, then. {p}Go home.
sea.neutral: There you are. Little lamp. Old friend. I'm so tired. Thank you for waiting.
marrow.happy: Thank you for carrying me.
flash 12
narr: The sea comes back like a held breath let go, one soft wave at a time. It touches every dry stone on its way to the sky.
gaff.happy: She's in the bucket! KID! THE SEA IS IN MY BUCKET!
narr: Across LOWTIDE, every lantern glows. Pip counts the town again. This time it comes out right.
narr: The tide goes out at dusk and returns at dawn. The sea is tired, and has gone to rest, and will be a different kind of tide.
wick.happy: It's all right. It's the kind of goodbye you can come back from.
ending 1
""")
W.scene('ending_neutral', """
fade out
music end_neutral
warpk sea_shore 7 9 up
fade in
narr: The Great Lantern cracks open. The tide inside it staggers out, tired and slow, and does not quite reach everyone.
sea.sad: I'm here. I'm here. I'm... I'm not all here.
marrow.sad: I'm sorry. I should have said goodbye properly. {p}I think I forgot how.
narr: Some lanterns glow. Some stay dark. Some people hug each other without knowing why.
gaff.neutral: There's water in the bucket. A little. It's... enough to hold one fish's worth of hope.
wick.sad: I'm still here. I'm still lit. Some of us aren't. {p}I wish we'd done more. I wish we'd listened more.
narr: The tide goes out at dusk and sometimes it comes back. Sometimes it doesn't. It's a different kind of waiting now.
ending 2
""")
W.scene('ending_fight', """
fade out
music end_fight
warpk sea_shore 7 9 up
fade in
narr: You break the Great Lantern.
narr: The sea breaks out of it, not as a tide, but as a blow. Water screams across every road in LOWTIDE.
sea.angry: WHAT. HAVE. YOU. DONE.
narr: Every lantern in the country goes out, one by one, in the order you passed them.
marrow.sad: ...You didn't have to. {p}I would have... I might have...
narr: The Warden's lamp falls quiet. The sea takes him. The sea takes everything, gently, afterwards.
wick.sad: ...
wick.sad: I'm still lit. I'm so small and I'm still lit. {p}Why am I still lit?
narr: You stand at the top of the Hollow Light. Below you the sea is finally back. The only lamp left burning is yours.
ending 3
""")
W.scene('ending_true', """
fade out
music end_true
warpk sea_shore 7 9 up
fade in
narr: You sing. Every verse. From every shell. The one about the cradle of dark water, the one about the town on the hull.
narr: The last verse comes through you like a tide through a door. It's the verse Marrow could never let her finish.
marrow.surprised: ...That's the end of it. {p}That's how the song ends.
sea.happy: THERE you are. All of you. {p}Hello, hello. And goodbye, goodbye. And hello.
sea.neutral: I'm so tired. And so glad. Marrow, my love, my small lost lamp, thank you for the long wait.
marrow.happy: Go home. I'll see you in the morning.
flash 14
narr: The tide comes back not as a flood but as a lullaby. Everything wet. Everything warm. Everything remembered.
sea.neutral: Child. Wick. Little light. You listened. {p}You were the one I carried, you know. You were always going to be the one.
wick.happy: I knew it. I KNEW it. I'm going to be so insufferable.
gaff.happy: The bucket's full! And there's a fish in it! I don't even have a hook!
pip.happy: Welcome to CORALLINE! Population: me, plus EVERYONE!
dory.happy: Rule number one: don't let anyone leave without saying goodbye. {p}Rule number one: say hello when they return.
skiff.happy: ...Not gonna cry. Not gonna. {p}Okay, I'm gonna.
narr: The sea goes out at dusk, singing. It comes home at dawn, singing. Every tide is a goodbye and a hello. That's all a tide has ever been.
ending 4
""")

W.mapdef('sea_shore', 'light', [
 "~~~~~~~~~~~~~~~~",
 "~~~~~~~~~~~~~~~~",
 "~~~~~~~~~~~~~~~~",
 "~~~~~~~~~~~~~~~~",
 "................",
 "................",
 "................",
 "................",
 "................",
 "................",
 "################"], 'end_peace',
 ents=[], script=":enter\nend")

W.battle('echo', shown='Echo', gfx='echo', hp=34, atk=3, exp=10, gold=12, music='battle',
 pal=['#E8F0FF', '#98A8E0', '#3A4488', '#0C0B14'],
 patterns=[closing(5, 14, 46, 8, 44, gfx='star'), aimed(5, 22, 20, n=3, spread=28, gfx='star'), rain(5, 18, 9, gfx='star'), ring(5, 14, 42, 10, gfx='star', spiral=10), wall(5, 14, 36, 8, gfx='star')],
 listen=[('Check', 'check'), ('Recall', 'recall'), ('Listen', 'listen')],
 script="""
:intro
flavor "An Echo flickers, a child-shaped memory with no one inside it. It repeats a single word."
end
""" + turn(5, {0: "The Echo's memories close in.", 1: "It points. Memories follow.", 2: "Old memories fall like rain.", 3: "A spiral of forgotten names.", 4: "A wall of yesterday."}) + """
:check
flavor "ECHO. ATK 3. A memory looking for its owner. It only remembers one word."
end
:listen
flavor "You listen. It says 'wa...ter.' It says 'wa... ter... wa...'"
end
:recall
choice r "Hello" "Goodbye" "Wait"
if r == 1 goto recall_ok
sfx error
flavor "The Echo shudders. That wasn't the word. It tries again, quieter."
end
:recall_ok
spareable 1
flavor "'Goodbye.' The Echo brightens. 'Goodbye,' it says back, like a thank-you. (Ready to let go.)"
end
:win
flavor "The Echo shatters. The word it was holding rolls across the floor, unsaid."
end
:spared
flavor "The Echo exhales one word: 'hello.' Then it fades, content."
end
""")

W.battle('marrow', shown='Warden Marrow', gfx='marrow', extra_gfx=['marrow2', 'marrow3'], hp=220, atk=5, exp=40, gold=100, music='boss_marrow', flags=1 | 2,
 pal=['#FFF4C8', '#F2B84A', '#8A5418', '#0C0B14'],
 patterns=[aimed(6, 26, 16, n=3, spread=30, gfx='star'), ring(6, 16, 30, 12, gfx='star', spiral=11), rain(6, 20, 6, gfx='drop'), side(6, 26, 8, gfx='orb'),
           wall(6, 16, 30, 9, gfx='orb'), closing(6, 16, 40, 10, 44, gfx='star'),
           PAT(7, (12, 5), [E_('spiral', at=(128, 128), sp=14, n=6, every=14, spread=255, param=9, gfx='star'), E_('rain', sp=18, n=1, every=12, gfx='drop')]),
           PAT(7, (8, 6), [E_('aimed', at=(128, 10), sp=24, n=2, every=20, spread=20, gfx='star'), E_('ring', sp=14, n=8, every=50, param=44, gfx='orb')])],
 listen=[('Check', 'check'), ('Hear Him', 'hear'), ('Lamps', 'lamps'), ('Goodbye', 'bye'), ('Sing', 'sing')],
 script="""
:intro
flavor "Warden Marrow raises the Great Lantern. The tide inside it quivers."
end
""" + """
:turn
if bt_turn == 4 goto ph2
if bt_turn == 8 goto ph3
if bt_turn >= 8 goto go3
if bt_turn >= 4 goto go2
:go1
rnd r 4
if r == 0 goto t0
if r == 1 goto t1
if r == 2 goto t2
goto t3
:go2
rnd r 6
if r == 0 goto t0
if r == 1 goto t3
if r == 2 goto t4
if r == 3 goto t5
if r == 4 goto t1
goto t6
:go3
rnd r 6
if r == 0 goto t6
if r == 1 goto t7
if r == 2 goto t5
if r == 3 goto t2
if r == 4 goto t4
goto t7
:t0
attack 0
flavor "Marrow flings stars. Each one is a song."
end
:t1
attack 1
flavor "A spiral of lamps. It's very beautiful. It will hurt."
end
:t2
attack 2
flavor "Drops of light. The lantern weeps."
end
:t3
attack 3
flavor "Marrow whips the lantern sideways. Light screams."
end
:t4
attack 4
flavor "A wall of lamps. He's building a door he can't hold shut."
end
:t5
attack 5
flavor "The lamps close in. They want to go home."
end
:t6
attack 6
flavor "Spiral and rain, at once. His grief has a lot of hands."
end
:t7
attack 7
flavor "Aimed stars and a closing ring. He can't decide whether to hold on or let go."
end
:ph2
marrow.angry: Every soul in this place BENEFITED from my silence! They have been SAFE! They have been WARM!
gfx marrow2
box 14 4
layers 7
goto go2
:ph3
marrow.sad: Do you think I don't know? Do you think I don't hear her, every night, asking?
gfx marrow3
music marrow_final
box 8 6
layers 15
goto go3
:check
flavor "WARDEN MARROW. ATK 5. Kept the sea from leaving. Fear of: goodbye."
end
:hear
bflag 0
flavor "You ask him why. He tells you, shaking. 'I didn't want her to be alone. I didn't want to be.'"
end
:lamps
if bt_f0 == 0 goto lamps_no
bflag 1
flavor "You say the lamps are tired from holding what he couldn't. He looks at them. They look back."
end
:lamps_no
flavor "You mention the lamps. He bristles. 'Ask me why first.'"
end
:bye
if bt_f1 == 0 goto bye_no
bflag 2
if bt_turn < 6 goto bye_early
spareable 1
flavor "You say: 'Goodbyes aren't endings. They're the door she'll come back through.' He sobs. (Ready to let go.)"
end
:bye_early
flavor "He listens, shaking. He needs a little longer to hear it. (Keep listening; stay on your feet.)"
end
:bye_no
flavor "You say goodbye. He flinches. He's not ready. (Hear him out, then the lamps.)"
end
:sing
if shells < 5 goto sing_no
if bt_f0 == 0 goto sing_early
set true_sing 1
spareable 1
flavor "You sing the whole lullaby, every verse from every shell. He falls to his knees. 'That's... how it ends.' (Ready to let go.)"
end
:sing_early
flavor "You open your mouth. The shells hum, waiting. He needs to be heard first."
end
:sing_no
flavor "You sing the verses you have. The shells hum back, hopeful. But there are verses missing."
end
:win
marrow.sad: ...Thank you. {p}I was never going to be able to do it myself.
flavor "Warden Marrow lowers the lantern. It does not quite break."
end
:spared
marrow.neutral: ...I'll let her go.
end
""")
W.encounters(6, ['echo', 'echo', 'echo', 'paperclam'])
