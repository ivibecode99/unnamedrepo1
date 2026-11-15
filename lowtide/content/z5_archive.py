from world import W
from lib import *
from util import *

W.mapdef('archive_lobby', 'arch', [
 "################",
 "#h.h.h.pp.h.h.h#",
 "#..............#",
 "#.d............#",
 "#..............#",
 "#...ggg........#",
 "................",
 "#...ggg...a....#",
 "#..............#",
 "#.h.h........h.#",
 "#..............#",
 "#.l..........l.#",
 "#..............#",
 "################"], 'archive',
 ents=[NPC('inkling', 'inkling', 4, 3, 'ink_talk'), NPC('clerk', 'clamfolk', 11, 7, 'clerk_talk'), NPC('shopper', 'clamfolk', 10, 3, 'shop_talk'), NPC('skiff', 'skiff', 6, 8, 'skiff_talk', gate='skiff_friend'),
       SAVE('post', 12, 10), EXIT('towest', 0, 6, 1, 1, 'lumen_lair', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'stacks1', 1, 6, 'right')],
 script="""
:enter
set zone 5
if z5_intro goto e_end
set z5_intro 1
narr: THE ARCHIVE OF TIDES. Shelves higher than the sky ought to allow. Every book is slightly damp.
inkling.happy: Welcome, welcome! Please sign in. Please sign out. Please do not sign anything in between.
inkling.neutral: I'm Inkling, junior clerk. Archivist Quill is east, past the stacks. She doesn't take visitors. She takes FORMS.
:e_end
end
:ink_talk
if z5_shell goto ink_done
if z5_pages == 3 goto ink_turn
inkling.sad: I lost three pages in the stacks. A form, a receipt, and a... a ticket stub for a ferry that never sailed.
inkling.neutral: If you find all three, I'll reward you. It's not a bribe. It's a clerical gratitude.
end
:ink_turn
set z5_shell 1
inc shells
inkling.surprised: You found them ALL?! The form, the receipt, the stub!
inkling.happy: This is a MEMORY SHELL. It was filed under 'lost'. It hums the last verse. It does NOT hum the end of the last verse. {p}That's sealed.
sfx light
end
:ink_done
inkling.happy: Everything's filed! We're a model archive! Allegedly.
end
:clerk_talk
clamfolk.neutral: Reading room's closed. Forever. Since the sea left, no one reads anymore. They just remember.
end
:shop_talk
clamfolk.neutral: Salt buns, lamp oil, ink vials. Stationery and sustenance.
shop arch
end
:skiff_talk
skiff.happy: Oh, THERE you are. I did the thing. The 'making friends' thing. It's fine.
skiff.neutral: Quill's chamber is east, past the stacks. She's scarier than the Captain. {p}Well. Equal scary. Different fonts.
if z5_done goto skiff_after
skiff.sad: Whatever you decide about the Warden... I'm in. Even if it's stupid.
end
:skiff_after
skiff.happy: I'll hold the door at the Hollow Light. {p}Don't die. I mean it. Rude.
end
""")

W.mapdef('stacks1', 'arch', [
 "################",
 "#h.h.h.h.h.h.h.#",
 "#..............#",
 "#..xxxx..xxxx..#",
 "#..xxxx..xxxx..#",
 "#..............#",
 "................",
 "#..............#",
 "#..xxxx..xxxx..#",
 "#..............#",
 "#h.h.h.p.h.h.h.#",
 "################"], 'archive', enc=5, rate=3,
 ents=[SPOT('page1', 14, 2, 'page1_get', ngate='z5_p1'), SPOT('book', 2, 4, 'book_talk'), EXIT('towest', 0, 6, 1, 1, 'archive_lobby', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'stacks2', 1, 6, 'right')],
 script="""
:enter
set zone 5
end
:page1_get
sfx item
set z5_p1 1
inc z5_pages
narr: A loose page, wedged behind a shelf: a FORM. It's blank except for a thumbprint. Possibly Inkling's.
end
:book_talk
narr: A book whispers: 'Do not alphabetize me. I am not a list. I am a TIDE.'
end
""")

W.mapdef('stacks2', 'arch', [
 "################",
 "#h.h.h.h.h.h.h.#",
 "#..............#",
 "#.h.h.h.h.h.h..#",
 "#..............#",
 "#...xxxx.......#",
 "................",
 "#...xxxx.......#",
 "#..............#",
 "#.h.h.h.h.h.h..#",
 "#d.............#",
 "################"], 'archive', enc=5, rate=3,
 ents=[SPOT('b0', 3, 3, 'book0'), SPOT('b1', 7, 3, 'book1'), SPOT('b2', 11, 3, 'book2'), SPOT('page2', 2, 9, 'page2_get', ngate='z5_p2'), SPOT('page3', 13, 9, 'page3_get', ngate='z5_p3'),
       DOOR('gate', 14, 6, ngate='z5_books'), EXIT('towest', 0, 6, 1, 1, 'stacks1', 14, 6, 'left'), EXIT('toeast', 15, 6, 1, 1, 'quill_chamber', 1, 6, 'right')],
 script="""
:enter
set zone 5
end
:page2_get
sfx item
set z5_p2 1
inc z5_pages
narr: A RECEIPT, sticky with old tea. It reads: 'ONE (1) MEMORY, LOANED. DUE: NEVER.'
end
:page3_get
sfx item
set z5_p3 1
inc z5_pages
narr: A ferry TICKET STUB. Destination: 'HOME'. Departure: 'IN A MOMENT'.
end
""" + lantern_puzzle('book', [1, 2, 0], 'z5_books', 'z5_seq', ['red', 'blue', 'green'],
   ["A green book, soft-spoken: 'Light me last. Red goes first. Blue second.'",
    "A red book, flushed: 'Me first! I'm the beginning! Then blue!'",
    "A blue book, calm: 'The middle. After red, before green.'"][::-1] if False else
   ["A green book mumbles: 'Last. I'm the end. I'm always the end.'",
    "A red book beams: 'Me first! Always! Don't let the others talk you out of it!'",
    "A blue book hums: 'Second. I'm patient. Red first, then me, then green.'"],
   "The shelves part with a sigh. Beyond them: a hall that smells of ink and old lullabies."))

W.mapdef('quill_chamber', 'arch', [
 "################",
 "#h.l........l.h#",
 "#..............#",
 "#.d..........d.#",
 "#..............#",
 "#..............#",
 "................",
 "#..............#",
 "#..............#",
 "#.l..........l.#",
 "#..............#",
 "################"], 'archive',
 ents=[NPC('quill', 'quill', 7, 3, 'quill_talk', ngate='z5_boss_gone'), ZONE('intro', 3, 5, 1, 3, 'quill_intro', ngate='z5_boss_seen'), SAVE('post', 2, 8),
       EXIT('towest', 0, 6, 1, 1, 'stacks2', 14, 6, 'left'), EXIT('tolight', 15, 6, 1, 1, 'light_shore', 1, 6, 'right', gate='z5_done')],
 script="""
:enter
set zone 5
end
:quill_intro
set z5_boss_seen 1
music mystery
quill.neutral: Appointments are required. Do you have an appointment? No. Do you have a form? ...No.
quill.neutral: Then you've come for the Decree of Ebb. Everyone eventually does. It's in the seal-room. It is sealed.
wick.sad: What does it say?
quill.sad: It says what happened. It says who asked, and who refused. It says it was never anybody's fault, and it was everyone's.
quill.angry: And I swore to the Warden I would never, ever file it as READ. So you will go away. Or you will be PROCESSED.
music boss_quill
sfx boss
battle quill
if lastbt == 1 goto spared
goto killed
:spared
set z5_done 1
set z5_boss_gone 1
music mystery
quill.sad: ...Here. Read it. {p}I've kept it so long my hands know the shape of it.
chunk archive_decree
set zone 6
end
:killed
set z5_done 1
set z5_boss_gone 1
music mystery
narr: Archivist Quill's glasses fall. The seal-room door creaks open on its own.
narr: You read the Decree standing over her desk. The words don't care who reads them.
chunk archive_decree
set zone 6
end
:quill_talk
quill.neutral: Please file all grief in triplicate.
end
""")

W.scene('archive_decree', """
narr: DECREE OF EBB. Filed by the Warden of Lamps, Keeper of the Hollow Light.
narr: 'By my order, the Sea's final tide is SUSPENDED. The lamps shall bear what the people cannot.'
quill.neutral: It's attached to a letter. His wasn't the only one.
narr: ATTACHED: a single wet page, in watery handwriting.
narr: 'Dear everyone. I'm tired. I've been so glad of you. I've gone out and come home every day, and now I'd like to go out and not come home the same.'
narr: 'Please sing me out. Light a lantern so I can find my way. Don't be sad. I'll be a different kind of tide. Love, the Sea.'
wick.sad: ...
quill.sad: The Warden loved her most. He couldn't bear to hear her say goodbye. So he stopped her at the lowest ebb, halfway out, and sealed the farewell inside the first lamps.
quill.sad: The lamps forgot. The people forgot. The sea didn't leave. {p}It was stopped, mid-goodbye. It has been waiting at the edge ever since.
wick.surprised: The sea isn't gone. She's... holding her breath.
quill.neutral: Hollow Light. Top of the stairs. The Great Lantern. He keeps her there.
if shells == 4 goto q_hint
end
:q_hint
quill.happy: Funny. You've collected four of the five Memory Shells. {p}The fifth one is a hint: the Choir's tune is the only thing he can't refuse.
end
""")

W.battle('paperclam', shown='Paperclam', gfx='paperclam', hp=32, atk=3, exp=10, gold=12, music='battle',
 pal=['#F8F4E8', '#C8B8A0', '#6A5A48', '#0C0B14'],
 patterns=[aimed(5, 22, 22, n=3, spread=26, gfx='bar'), wall(5, 14, 36, 8, gfx='bar', ang=0), rain(5, 18, 8, gfx='bar'), ring(5, 14, 40, 10, gfx='bar', spiral=8), side(5, 22, 10, gfx='bar')],
 listen=[('Check', 'check'), ('Form A', 'forma'), ('Form B', 'formb'), ('Sign', 'sign')],
 script="""
:intro
flavor "A Paperclam sorts papers at an astonishing speed. It looks up. 'Do you have an appointment?'"
end
""" + turn(5, {0: "Forms fly at you. Aimed, with passion.", 1: "A wall of forms, stamped with intent.", 2: "Paper rains. It's mostly memos.", 3: "A spiral of staples.", 4: "Forms from the side. It's a bureaucratic ambush."},
   pre="""if bt_gift == 10 goto ink_ok
goto tpre_end
:ink_ok
spareable 1
flavor "You offered a vial of ink. Its eyes shine. 'Fresh ink. For a clerk, that is love.' (Ready to let go.)"
end
:tpre_end
""") + """
:check
flavor "PAPERCLAM. ATK 3. Believes every problem is a missing form."
end
:forma
bflag 0
flavor "You fill out Form A. 'Reason for visit: curiosity.' The Paperclam stamps it. A tiny cheer."
end
:formb
if bt_f0 goto formb_ok
flavor "You fill out Form B. It's rejected. 'Form A first!' it says."
end
:formb_ok
bflag 1
flavor "You fill out Form B. 'Reason for leaving: kindness.' It beams, a little misty."
end
:sign
if bt_f1 goto sign_ok
flavor "You sign. The Paperclam winces. 'Not yet! Forms first!'"
end
:sign_ok
spareable 1
flavor "You sign with a flourish. 'Everything is in order.' It's crying with joy. (Ready to let go.)"
end
:win
flavor "The Paperclam clamps shut. A single form flutters down: 'RELEASED.'"
end
:spared
flavor "It stamps your hand with the word APPROVED. It feels warm."
end
""")
W.battle('quill', shown='Archivist', gfx='quill', hp=150, atk=4, exp=30, gold=65, music='boss_quill', flags=1 | 2,
 pal=['#F8F4E8', '#C8B8A0', '#6A5A48', '#0C0B14'],
 patterns=[aimed(6, 24, 16, n=3, spread=30, gfx='bar'), wall(6, 16, 30, 9, gfx='bar', ang=64), rain(6, 20, 6, gfx='bar'), ring(6, 16, 32, 12, gfx='bar', spiral=12),
           side(6, 24, 8, gfx='bar'), closing(6, 16, 42, 10, 44, gfx='bar')],
 listen=[('Check', 'check'), ('Ask', 'ask'), ('Reassure', 'reassure'), ('Read It', 'read')],
 script="""
:intro
flavor "Archivist Quill adjusts her glasses. The stacks behind her lean in."
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
flavor "Paperwork. Aimed at your feelings."
end
:t1
attack 1
flavor "A wall of file folders. The cabinet is heavy."
end
:t2
attack 2
flavor "A rain of memos. Everything needs a response."
end
:t3
attack 3
flavor "Staples spiral outward. The sound is surprisingly lovely."
end
:t4
attack 4
flavor "Forms from the side. They are very emphatic."
end
:t5
attack 5
flavor "The stacks close in. They have been waiting to be read."
end
:mid1
quill.angry: I SWORE. I SWORE I'D NEVER LET ANYONE READ THE FINAL PAGE. I SWORE. I SWORE!
box 14 4
layers 7
goto go
:mid2
quill.sad: Do you know how heavy a sealed grief is? It doesn't weigh anything. That's what makes it so heavy.
box 8 6
layers 15
goto go
:check
flavor "ARCHIVIST QUILL. ATK 4. Keeper of the Decree. Fear of: the truth being read, and nobody being fair about it."
end
:ask
bflag 0
flavor "You ask what the Decree says. She doesn't tell you. But she doesn't stop you from asking."
end
:reassure
if bt_f0 == 0 goto reassure_no
bflag 1
flavor "You promise to read it gently. She wavers. 'Gently?' 'Gently.'"
end
:reassure_no
flavor "You try to comfort her. She's not ready. She needs to be asked about it first."
end
:read
if bt_f1 == 0 goto read_no
bflag 2
spareable 1
flavor "You offer to read it with her, at her pace. Her stamp drops. She nods. (Ready to let go.)"
end
:read_no
flavor "You reach for the Decree. She slaps your hand away. 'Not yet!' Ask, then reassure."
end
:win
quill.sad: ...It was always going to be read. {p}I'm only tired.
flavor "Archivist Quill falls silent. The stacks sigh, relieved."
end
:spared
quill.neutral: ...Thank you.
end
""")
W.encounters(5, ['paperclam', 'paperclam', 'gloamfin', 'paperclam'])
