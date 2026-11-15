from world import W
from lib import *
from util import *

W.mapdef('hull_dock', 'hull', [
 "################",
 "#.p..w..w..p...#",
 "#..............#",
 "#..bb....ccl...#",
 "#..............#",
 "#.t...m........#",
 "#..............,",
 "#..,,......,,..#",
 "#..............#",
 "#.b..........c.#",
 "#..............#",
 "#...l......l...#",
 "#..............#",
 "#######..#######"], 'hull_town',
 ents=[NPC('dory', 'dory', 5, 4, 'dory_talk'), NPC('cobb', 'cobb', 3, 5, 'cobb_talk'), NPC('barnaby', 'barnaby', 13, 6, 'barnaby_talk'), NPC('shopper', 'jellyfolk', 10, 9, 'shop_talk'),
       DOOR('tollgate', 14, 6, ngate='z2_toll'), SAVE('post', 13, 11), EXIT('toeast', 15, 6, 1, 1, 'cargo1', 1, 6, 'right'), EXIT('tosouth', 7, 13, 2, 1, 'ruffle_hall', 7, 1, 'down')],
 script="""
:enter
set zone 2
if z2_intro goto e_end
set z2_intro 1
narr: BALLAST ROW. Ships stacked on ships, like a city built by someone who couldn't throw anything away.
pip.happy: {name}! WAIT UP! I snuck along in your pocket! ...No, I didn't. That would be silly.
wick.neutral: Pip is not here. That was a very clever lie from a very small voice.
dory.happy: Welcome aboard! Rule number seven: no running on the decks. Rule number four: no walking either.
dory.neutral: ...I'm Dory. First mate. There are many rules. I have not memorized them. I have memorized their NUMBERS.
:e_end
end
:dory_talk
if z2_done goto dory_after
dory.neutral: Rule number twelve: tolls are paid in salt. Rule number thirteen: Barnaby is not a person, he is a policy.
dory.happy: If you can't pay, he'll let you work it off. Cargo sorting! Very relaxing. Very repetitive.
if bosskills > 0 goto dory_scared
end
:dory_after
dory.happy: Captain Brass actually SMILED. Rule number one: never expect that. Rule number one: expect that.
end
:dory_scared
dory.sad: Rule number zero: if a customer looks like that, you offer them tea and you do not make eye contact.
end
:cobb_talk
if z2_stew goto cobb_done
if cobb_ask goto cobb_check
set cobb_ask 1
cobb.sad: I used to make a stew. Everyone said it tasted like being hugged. Now I stir and stir and it tastes like water.
cobb.neutral: I think my lantern has the recipe. I just can't open it. {p}I need a warm rock, a sweet bun, and... someone to eat it with.
cobb.happy: Bring me those two things? I'll cook. You can be the someone. Side quest! Sort of.
end
:cobb_check
ifhas "Warm Rock" goto cobb_h1
cobb.neutral: Still need a warm rock and a sweet bun. They sell 'em at the dock stall.
end
:cobb_h1
ifhas "Sweet Bun" goto cobb_cook
cobb.neutral: Got the rock! Now the sweet bun.
end
:cobb_cook
take "Warm Rock"
take "Sweet Bun"
set z2_stew 1
cobb.surprised: Oh!!! Oh. Oh, it's coming back. A kitchen. A window. A hand on my shoulder. My mum saying 'Salt, not sugar, dear.'
cobb.happy: Here! Sit! Eat! It's... it's right! It tastes like being hugged!
sfx heal
boost 4
give Stew
narr: You eat the stew. It tastes exactly like being hugged. Your maximum HP rose by 4. You also got a bowl for later.
cobb.happy: Take the rest. Eat it when the world is too loud.
end
:cobb_done
cobb.happy: The stew's still hot, somehow. I think the lantern's helping.
end
:shop_talk
jellyfolk.happy: Wares! Salt buns! Warm rocks! Toll coins, for when Barnaby has a mood!
shop hull
end
:barnaby_talk
if z2_toll goto barnaby_done
barnaby.neutral: HALT. Official customs. State your name, your cargo, and your reason for existing. I'll accept a toll of twenty salt.
barnaby.neutral: Or sort a backlog. Twenty crates. Round things left, spiky things right. Very scientific.
choice r "Pay 20 salt" "Sort cargo" "Not now"
if r == 2 goto barnaby_no
if r == 1 goto barnaby_sort
ifgold 20 goto barnaby_pay
barnaby.angry: That's not twenty. That's an insult wearing a coin.
end
:barnaby_pay
gold -20
set z2_toll 1
sfx door
barnaby.happy: Delightful. The gate is open. Mind the rust. It has feelings.
end
:barnaby_sort
minigame sort
if r == 0 goto barnaby_fail
set z2_toll 1
sfx door
if r == 2 goto barnaby_perfect
barnaby.happy: Acceptable. The gate is open. Do not touch the pipes.
end
:barnaby_fail
barnaby.sad: Appalling. Crates everywhere. Try again, or pay.
end
:barnaby_perfect
if z2_shell goto barnaby_ps
set z2_shell 1
inc shells
barnaby.surprised: A flawless sort?! In twenty years not a single clean row. I... I need a moment.
barnaby.happy: Here. A MEMORY SHELL from the lost-and-found. It hums. It's yours. Please never tell anyone I cried.
sfx light
end
:barnaby_ps
barnaby.happy: Flawless again. You make my day hum.
end
:barnaby_no
barnaby.neutral: Customs doesn't wait. But it does charge interest.
end
:barnaby_done
barnaby.neutral: The gate is open. I'm writing you a receipt anyway.
end
""")

W.mapdef('cargo1', 'hull', [
 "################",
 "#..c....bb.....#",
 "#.............l#",
 "#...###.####...#",
 "#...#.......#..#",
 "#...#.xxxx..#..#",
 "................",
 "#...#.xxxx..#..#",
 "#...#.......#..#",
 "#...###.####...#",
 "#.b....c.....c.#",
 "################"], 'cargo', enc=2, rate=3,
 ents=[SPOT('hatch', 14, 2, 'lever_talk'), DOOR('gate', 7, 3, ngate='z2_gate'), DOOR('gate2', 7, 9, ngate='z2_gate'),
       EXIT('towest', 0, 6, 1, 1, 'hull_dock', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'cargo2', 1, 6, 'right')],
 script="""
:enter
set zone 2
end
:lever_talk
if z2_gate goto lv_done
sfx door
shake 12 1
set z2_gate 1
narr: You haul the cargo lever. A huge hatch grinds open in the middle of the hold.
end
:lv_done
narr: The lever is stuck down. It's done its part.
end
""")

W.mapdef('cargo2', 'hull', [
 "################",
 "#..............#",
 "#.b.....c...bb.#",
 "#..............#",
 "#.....xxxx.....#",
 "#.....xxxx.....#",
 "................",
 "#.....xxxx.....#",
 "#..............#",
 "#.c..t.........#",
 "#..............#",
 "######.#########"], 'cargo', enc=2, rate=3,
 ents=[SPOT('riddle', 5, 9, 'riddle_talk'), DOOR('hatch', 6, 11, ngate='z2_riddle'), EXIT('towest', 0, 6, 1, 1, 'cargo1', 14, 6, 'left'), EXIT('tonorth', 15, 6, 1, 1, 'brig', 1, 6, 'right'),
       EXIT('tobelow', 6, 11, 1, 1, 'cargo1', 7, 5, 'down', gate='z2_riddle')],
 script="""
:enter
set zone 2
end
:riddle_talk
if z2_riddle goto rd_done
narr: A brass plate on the desk reads: 'To pass: answer correctly. Incorrect answers will be billed.'
narr: 'WHAT GOES OUT SO IT CAN COME BACK?'
choice r "A ship" "A tide" "A coin"
if r == 1 goto rd_ok
sfx error
narr: BZZT. Incorrect. Please pay 0 salt (we ran out of fees).
end
:rd_ok
set z2_riddle 1
sfx door
narr: DING. The hatch clanks open. Somewhere, a very old pipe sighs, 'finally.'
end
:rd_done
narr: The plate now reads 'CORRECT. WELL DONE. WE REGRET NOTHING.'
end
""")

W.mapdef('brig', 'hull', [
 "################",
 "#..............#",
 "#.G.G.G.G.G.G..#",
 "#..............#",
 "#.G.G......G.G.#",
 "#..............#",
 "................",
 "#..............#",
 "#...l.......l..#",
 "#..............#",
 "#..............#",
 "#######.########"], 'cargo',
 ents=[ZONE('skiffz', 6, 5, 3, 3, 'skiff_fight', ngate='z2_skiff'), NPC('skiff', 'skiff', 12, 6, 'skiff_after', gate='z2_skiff_here'), SAVE('post', 2, 9),
       EXIT('towest', 0, 6, 1, 1, 'cargo2', 14, 6, 'left'), EXIT('tonorth', 7, 11, 1, 1, 'brass_cabin', 7, 10, 'up')],
 script="""
:enter
set zone 2
end
:skiff_fight
set z2_skiff 1
music rival
show skiff
set z2_skiff_here 1
skiff.happy: THERE you are! I've been practicing my intimidating pose for an hour.
skiff.neutral: The Captain's cabin is through there. I'm going to relight the Hollow Light FIRST. So. Fight me for the privilege.
wick.sad: He's shaking a little. {p}Do you think he's scared, or just excited?
skiff.angry: I'm NOT scared! Skiffs don't get scared! We get... fast!
battle skiff1
music hull_town
if lastbt == 1 goto sk_spared
if lastbt == 0 goto sk_killed
set skiff_ally 0
end
:sk_spared
set skiff_ally 1
skiff.sad: ...You didn't hit me. Why didn't you hit me?
skiff.neutral: Fine. Maybe you're less awful than I thought. Don't tell anyone I said that.
skiff.happy: I'll see you in the depths. Race ya.
end
:sk_killed
set skiff_dead 1
narr: Skiff's lantern flickers once on the floor, and goes out.
wick.sad: ...
end
:skiff_after
end
""")

W.mapdef('brass_cabin', 'hull', [
 "#######.########",
 "#.l..w....w..l.#",
 "#..............#",
 "#..t........t..#",
 "#..............#",
 "#..............#",
 "#......a.......#",
 "#..............#",
 "#.c..........c.#",
 "#..............#",
 "#..............#",
 "#######.########"], 'hull_town',
 ents=[NPC('brass', 'brass', 7, 3, 'brass_talk', ngate='z2_boss_gone'), ZONE('intro', 5, 7, 5, 1, 'brass_intro', ngate='z2_boss_seen'),
       EXIT('toprev', 7, 11, 1, 1, 'brig', 7, 10, 'up'), EXIT('tosalt', 7, 0, 1, 1, 'salt_hamlet', 7, 12, 'up', gate='z2_done')],
 script="""
:enter
set zone 2
end
:brass_intro
set z2_boss_seen 1
music mystery
brass.neutral: Cabin's closed. By decree. Of me.
brass.happy: Oh, a customer! Welcome to the Toll. Tolls for ships, for crates, for conversation.
wick.neutral: Why does everything here cost something?
brass.sad: Because I'm saving up. Enough salt to buy the sea back. I'm eighty-six percent of the way. {p}I started a hundred years ago.
brass.angry: And you're standing on my deck without paying. That's two coins. That's a lecture.
music boss_brass
sfx boss
battle brass
if lastbt == 1 goto spared
goto killed
:spared
set z2_done 1
set z2_boss_gone 1
music hull_town
brass.sad: I don't think the sea's for sale. I think I knew that. I just wanted something to do with my hands.
brass.neutral: The Warden came through on the night the sea left. Paid the toll in tears. Said 'I couldn't say goodbye.'
wick.surprised: Goodbye to who?
brass.neutral: He didn't say. Go north to Rimeton. The salt folk remember songs. {p}Mind the Choir. They bite. Musically.
set zone 3
end
:killed
set z2_done 1
set z2_boss_gone 1
music cargo
narr: Brass's hat rolls across the floor. The ledger on the table is open. The last line says: 'ENOUGH.'
end
:brass_talk
brass.neutral: Cabin's closed. By decree. Of me. Mind the paperwork.
end
""")

W.battle('barnabee', shown='Barnabee', gfx='barnabee', hp=24, atk=2, exp=6, gold=8, music='battle',
 pal=['#E8E0D0', '#A89880', '#4A3C2E', '#0C0B14'],
 patterns=[wall(5, 14, 36, 8, gfx='orb'), side(5, 22, 12, gfx='spike'), aimed(5, 22, 24, n=2, spread=16, gfx='spike'), rain(5, 18, 11, gfx='spike')],
 listen=[('Check', 'check'), ('Tap', 'tap'), ('Polish', 'polish'), ('Leave Be', 'leave')],
 script="""
:intro
flavor "A Barnabee is clamped to the hull. It does not like being looked at."
end
""" + turn(4, {0: "Barnacles snap shut like tiny cymbals.", 1: "The Barnabee flings shells sideways.", 2: "Spiked shells. Very aimed.", 3: "A drizzle of tiny spikes. It's only trying to be left alone."},
   pre="""if bt_gift == 13 goto adopt
goto tpre_end
:adopt
spareable 1
flavor "You offer a warm rock. It clamps onto it, sighs, and glows with contentment."
end
:tpre_end
""") + """
:check
flavor "BARNABEE. ATK 2. Clings to things. Fear of: being pried loose."
end
:tap
flavor "You tap its shell. It clamps tighter. Maybe not that."
end
:polish
if bt_f0 goto polish2
bflag 0
flavor "You polish a patch of shell. It relaxes a little. Keep going."
end
:polish2
bflag 1
flavor "You polish its whole shell. It gleams. It almost smiles."
end
:leave
if bt_f1 goto leave_ok
flavor "You step back. It watches suspiciously. It isn't comfortable yet."
end
:leave_ok
spareable 1
flavor "You step back and leave it be. Its shell opens a crack. (Ready to let go.)"
end
:win
flavor "The Barnabee cracks. Inside it's soft. It just wanted to be left alone."
end
:spared
flavor "It clamps back onto the hull, gleaming. It looks content."
end
""")

W.battle('rustmite', shown='Rustmite', gfx='rustmite', hp=26, atk=3, exp=7, gold=9, music='battle',
 pal=['#F0D8B0', '#C08A4A', '#6A3A22', '#0C0B14'],
 patterns=[aimed(5, 22, 22, n=3, spread=28, gfx='coin'), ring(5, 14, 40, 10, gfx='coin', spiral=9), side(5, 22, 11, gfx='coin'), rain(5, 18, 9, gfx='coin'), wall(5, 14, 40, 8, gfx='bar', ang=0)],
 listen=[('Check', 'check'), ('Knock', 'knock'), ('Compliment', 'comp'), ('Pearl?', 'pearl')],
 script="""
:intro
flavor "A Rustmite peeks out of a rusty can. The can has a name tag: 'HOME'."
end
""" + turn(5, {0: "The Rustmite flings coins from its can. Where did it get them?", 1: "It spins in its can. Coins everywhere.", 2: "Coins from the left. It's very generous, in the worst way.", 3: "A shower of rusty coins.", 4: "Bars of metal. Sideways. It has a point."},
   pre="""if bt_gift == 7 goto pearl_ok
goto tpre_end
:pearl_ok
spareable 1
flavor "You offered a pearl. It cried a tiny rusty tear. It's ready to let go."
end
:tpre_end
""") + """
:check
flavor "RUSTMITE. ATK 3. Lives in a can. The can is also a mortgage."
end
:knock
flavor "You knock on the can. It hides. Nobody likes being knocked on."
end
:comp
if bt_f0 goto comp2
bflag 0
flavor "You compliment its can. 'Lovely curvature.' It peeks out, blushing rust."
end
:comp2
spareable 1
flavor "You compliment the can again. It trembles with joy. It's ready to let go."
end
:pearl
flavor "You pat your pockets. Maybe it likes something shiny. (Try ITEM.)"
end
:win
flavor "The can rolls away. The Rustmite inside is gone. The tag still says HOME."
end
:spared
flavor "The Rustmite tips its can like a hat and rolls off, proud."
end
""")

W.battle('skiff1', shown='Skiff', gfx='skiff', hp=45, atk=3, exp=12, gold=15, music='rival', flags=1,
 pal=['#C8F0FF', '#4A98C8', '#1A3050', '#0C0B14'],
 patterns=[aimed(5, 26, 16, n=2, spread=20, gfx='star'), side(5, 26, 10, gfx='star'), rain(5, 20, 8, gfx='star'), ring(5, 16, 34, 10, gfx='star', spiral=13), wall(5, 16, 36, 8, gfx='bar')],
 listen=[('Check', 'check'), ('Compete', 'compete'), ('Praise', 'praise'), ('Slow Down', 'slow')],
 script="""
:intro
flavor "Skiff cracks their knuckles. Their lantern glows steady. It never flickers."
end
""" + cyc(5, {0: "Skiff zips left. Then right. Mostly left.", 1: "Sideways stars. Courier speed.", 2: "A shower of delivered stars.", 3: "Skiff spins. A very specific kind of dizzy.", 4: "Skiff hurls an entire wall. It's an 'express' wall."},
   pre="""if bt_turn == 3 goto mid1
goto tpre_end
:mid1
skiff.sad: Why do you keep dodging? Why won't you just... hit me back? I can take it.
:tpre_end
""") + """
:check
flavor "SKIFF. ATK 3. Courier. Their lantern never flickers. It's never even changed color."
end
:compete
bflag 0
flavor "You race them in your head. Skiff grins. Then frowns."
end
:praise
if bt_f0 goto praise_ok
flavor "You say 'good job.' Skiff scoffs. Maybe talk about their speed first."
end
:praise_ok
bflag 1
flavor "You praise Skiff's speed. Their ears go pink. Their lantern flickers, once."
end
:slow
if bt_f1 goto slow_ok
flavor "You ask Skiff to slow down. 'No!' But they glance at their lantern."
end
:slow_ok
spareable 1
flavor "You ask Skiff to slow down. 'Fine. For a second.' Skiff stops. (Ready to let go.)"
end
:win
flavor "Skiff drops. Their lantern keeps glowing, steady. Steady. Steady."
end
:spared
flavor "Skiff catches their breath and doesn't say anything. The lantern steadies."
end
""")

W.battle('brass', shown='Capt Brass', gfx='brass', hp=110, atk=4, exp=24, gold=50, music='boss_brass', flags=1 | 2,
 pal=['#FFE8A8', '#E8A838', '#8A5418', '#0C0B14'],
 patterns=[aimed(6, 22, 18, n=3, spread=30, gfx='coin'), wall(6, 16, 32, 9, gfx='coin', ang=64), side(6, 24, 9, gfx='coin'), ring(6, 14, 34, 12, gfx='coin', spiral=10),
           rain(6, 20, 7, gfx='coin'), closing(6, 14, 46, 10, 44, gfx='coin')],
 listen=[('Check', 'check'), ('Pay Toll', 'pay'), ('Ask Ship', 'ship'), ('Thank Him', 'thank')],
 script="""
:intro
flavor "Captain Brass taps his ledger. Every coin in the room rattles."
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
flavor "Coins fly. Aimed, like invoices."
end
:t1
attack 1
flavor "A solid curtain of tolls."
end
:t2
attack 2
flavor "Coins from the side. He's charging you by the angle."
end
:t3
attack 3
flavor "A spiral of coins. Compound interest."
end
:t4
attack 4
flavor "It's raining coins. If only any were yours."
end
:t5
attack 5
flavor "Coins close in. Pay up. Pay UP."
end
:mid1
brass.angry: TWO coins you owe! And a SMILE you owe! And a thank-you, but that's not on the ledger!
box 14 4
layers 7
goto go
:mid2
brass.sad: I started a hundred years ago. I'm a hundred years in. I'm... I'm very tired of counting.
box 8 6
layers 15
goto go
:check
flavor "CAPTAIN BRASS. ATK 4. A hundred years of saving. Fear of: knowing it was never for sale."
end
:pay
if bt_gift == 9 goto pay_ok
ifgold 10 goto pay_gold
flavor "You can't afford it. He wouldn't take it anyway. (Try ITEM: Toll Coin.)"
end
:pay_gold
gold -10
:pay_ok
bflag 0
flavor "You pay his toll. He freezes. 'Nobody's ever paid. They always fight the fee.'"
end
:ship
bflag 1
flavor "You ask about the ship. 'She's called THE LONG WAIT. She never sailed. I just kept charging for the view.'"
end
:thank
if bt_f0 == 0 goto thank_no
if bt_f1 == 0 goto thank_no
bflag 2
spareable 1
flavor "You thank him for guarding the dock. He hasn't heard it in a century. His ledger falls shut. (Ready to let go.)"
end
:thank_no
flavor "You thank him. He narrows his eyes. He's not buying it yet. (Pay, and ask about the ship.)"
end
:win
brass.sad: ...It was never for sale.
flavor "Captain Brass's ledger falls. The hat rolls."
end
:spared
brass.neutral: ...Thank you.
end
""")
W.encounters(2, ['barnabee', 'rustmite', 'barnabee', 'rustmite'])
