from world import W
from lib import *
from util import *

W.mapdef('shore1', 'shore', [
 "################",
 "#..............#",
 "#..b....m......#",
 "#......r.......#",
 "#..,,.......s..#",
 "#..,,....r.....#",
 "#.......b......#",
 "#.....,,.......#",
 "#..r...........#",
 "#..........,,..#",
 "#..............#",
 "######..########"], 'shore',
 ents=[NPC('wick', 'wick', 7, 8, 'wick_talk', gate='wick_here'), NPC('gaff', 'gaff', 3, 4, 'gaff_talk'), SPOT('sign', 12, 4, 'sign_talk'),
       EXIT('toshore2', 6, 11, 2, 1, 'shore2', 7, 10, 'up')],
 script="""
:enter
if intro_done goto enter_done
set intro_done 1
set zone 0
set wick_here 0
narr: The sea left on a Tuesday. Nobody remembers why.
narr: Nobody remembers the Monday before it either. That's the strange part.
narr: You woke on the dry seabed with sand in your shoes and no one to ask what to call you.
name
narr: {name}. Good name. It sounds like it knows where it is going.
show wick
set wick_here 1
sfx light
wick.happy: Oh! Oh! You're awake! I have been floating over you for HOURS.{pp} Okay. Nine minutes. It felt like hours.
wick.neutral: I'm Wick. I'm a light. Technically a very small lantern with opinions.
wick.sad: The sea went away and now everything is quiet and I keep saying the wrong thing into it.
wick.happy: But you're here! Lanterns are lonely things. They only really shine when someone's listening.
wick.neutral: Follow me down to the Tide Gate. Past it there's a whole country that's still lit. {p}Probably.
if ng > 0 goto ng_wick
end
:ng_wick
wick.surprised: ...Wait. Have we done this before?
wick.sad: I feel like I already know how this story goes. I just can't remember the ending.
end
:enter_done
end
:wick_talk
wick.happy: Ready? The Tide Gate is south! That's down. Away from the nice big mast.
wick.neutral: Press B to hurry. Press START for your pockets. Press A on anything that looks lonely.
end
:sign_talk
narr: A rotting sign reads: GONE FISHING. {p}(Underneath, someone added: SAME.)
end
:gaff_talk
if ng > 0 goto gaff_ng
if gaff_met goto gaff_again
set gaff_met 1
gaff.neutral: Pull up a bucket. No water in it, but it's the thought that counts.
gaff.happy: Forty years I fished this bay. Then one Tuesday the fish went and so did the bay. Rude.
gaff.neutral: That little light of yours has been sulking in my bucket since dawn.
wick.angry: I was NOT sulking. I was resting. Dramatically.
gaff.sad: Past the Tide Gate folk still carry lanterns. Each one holds what they remember. Be kind to 'em.
gaff.neutral: A lantern remembers who was nice.
end
:gaff_again
gaff.neutral: Go on, kid. The gate's south. I'll keep the bucket warm.
end
:gaff_ng
gaff.surprised: Haven't we... done this? I've got the strangest notion I told you about the bucket.
gaff.sad: Eh. Old birds repeat themselves. Go on. Be kind.
end
""")

W.mapdef('shore2', 'shore', [
 "################",
 "#######..#######",
 "#......,,......#",
 "#.r............#",
 "#..........r...#",
 "#....,,........#",
 "#..............#",
 "#.b.......m....#",
 "#..............#",
 "#.....,,.....l.#",
 "#..............#",
 "#######..#######"], 'shore',
 ents=[ENEMY('crab', 'crabfolk', 7, 5, 'crab_fight', ngate='crab_done'), SAVE('post', 13, 8), DOOR('gate', 7, 1, ngate='crab_done'), DOOR('gate2', 8, 1, ngate='crab_done'),
       EXIT('toreef', 7, 1, 2, 1, 'coral_square', 8, 12, 'up', gate='crab_done'), EXIT('toshore1', 7, 11, 2, 1, 'shore1', 7, 10, 'up'),
       SPOT('sign', 3, 3, 'sign_talk')],
 script="""
:enter
set zone 0
if crab_done goto e_end
wick.surprised: Uh oh. A Dustcrab. It's blocking the Tide Gate.
wick.neutral: Crabs walk sideways because forward is where the water used to be. {p}Sad, honestly.
wick.happy: Use LISTEN to learn about it! Then RELEASE when it's ready. Or ATTACK, if you must. Press B to raise a shield around your flame!
:e_end
end
:crab_fight
battle dustcrab
set crab_done 1
sfx door
shake 20 2
if lastbt == 1 goto crab_spared
if lastbt == 0 goto crab_killed
end
:crab_spared
wick.happy: See? Nobody had to get hurt. I like this plan. I'm going to claim it was mine.
end
:crab_killed
wick.neutral: ...Right. It's gone. {p}I'll remember it though.
end
:sign_talk
narr: TIDE GATE. Beyond: LOWTIDE. No hawkers. No hungry crabs.{p} (Hungry crabs: please see Pip.)
end
""")

W.battle('dustcrab', shown='Dustcrab', gfx='dustcrab', hp=14, atk=2, exp=4, gold=5, music='battle',
 pal=['#F7D9B0', '#E09A6A', '#7A3A2A', '#0C0B14'],
 patterns=[aimed(4, 20, 30), ring(4, 14, 44, 8), rain(4, 16, 14, gfx='drop')],
 listen=[('Check', 'check'), ('Mimic', 'mimic'), ('Sidestep', 'side')],
 script="""
:intro
flavor "A Dustcrab sidles into your path. It looks as lost as you do."
end
""" + turn(3, {0: "The Dustcrab clicks a claw. Still sideways.", 1: "It scuttles in a nervous circle.", 2: "Dust drifts down like old snow."}) + """
:check
flavor "DUSTCRAB. ATK 2. Walks sideways because forward is where the water was."
end
:mimic
bflag 0
flavor "You scuttle sideways. The crab squints, then copies you. A tiny, hopeful claw wave."
end
:side
if bt_f0 goto side_ok
flavor "You sidestep. The Dustcrab has no idea what you're doing. Maybe copy it first?"
end
:side_ok
spareable 1
flavor "You two sidestep in perfect sync. The crab is thrilled! (It looks ready to go.)"
end
:win
flavor "The Dustcrab poofs into a small sad pile of sand."
end
:spared
flavor "It waves a claw and scuttles off to tell its friends about you."
end
""")
