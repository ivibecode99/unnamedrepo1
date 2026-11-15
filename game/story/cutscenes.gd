class_name Cutscenes
extends RefCounted
## All story text. Cutscene = list of lines [speaker, text]; shown with the dialogue box.
const INTRO := [
	["", "Long ago, the world was held together by a song. A gentle little tune, played by a giant music box in the sky."],
	["", "Every note of that song was a Star. Hundreds of them, floating over six wonderful kingdoms."],
	["Baron Von Grumblebelt", "HAHAHA! Wind it up! Wind it up! If I own every Star, I own the SONG. And if I own the song, everybody dances to MY tune!"],
	["Baron Von Grumblebelt", "Pack them in, my Clockworkers! Leave nothing but dust and awkward silence!"],
	["", "In the quiet little village of Hiccup Hollow, a young hero was having a perfectly nice nap."],
	["Capt", "PIP! WAKE UP! Stars are falling! Giant villain! Dramatic music! I'd say this is a big deal!"],
	["Pip", "Mmmf... five more minutes?"],
	["Capt", "NO. I'm your hat. I'm basically your boss. UP. WE HAVE A WORLD TO SAVE."],
	["Pip", "...Okay, but I'm bringing snacks."],
	["Skipper Mabel", "Ahoy! The Airship Hiccup can chase that Baron, but our engine's dry. Gather Stars and she'll fly!"],
]
const HUB_ARRIVE := [["Skipper Mabel", "Welcome back aboard, Pip! Take the map table and pick a kingdom. Don't touch the red lever."]]
const KINGDOM_ARRIVE := {
	"forest": [["Capt", "Fernwhistle Forest! The trees here gossip about everyone. Do NOT ask them about me."], ["Pip", "Why? What did you do?"], ["Capt", "Nothing! Allegedly."]],
	"desert": [["Capt", "Sizzle Sands. It's hot. I don't sweat, but I'm judging the sun."], ["Pip", "You're a hat."], ["Capt", "Exactly. I take all the heat and none of the credit."]],
	"city": [["Capt", "Tinkertown! Everything is a little clockwork. Even the pigeons."], ["Pip", "Is that pigeon staring at me?"], ["Capt", "It's always staring. That's the tick-tock."]],
	"ocean": [["Capt", "Splashbottom Bay. Please do not make me swim. I'm a hat. I get SOGGY."], ["Pip", "You can hold your breath."], ["Capt", "I'm not a lung, Pip! I'm a hat!"]],
	"snow": [["Capt", "Frostnip Peaks! Brr! My brim is already frozen. This is a personal attack."], ["Pip", "Wear a scarf."], ["Capt", "Pip, I AM the headgear. There is no scarf."]],
	"volcano": [["Capt", "Cinder Skies. Floating rocks and angry lava. The Baron really knows how to decorate."], ["Pip", "Are you scared?"], ["Capt", "I'm a hat. Fear isn't a feature. ...Okay, a little."]],
	"final": [["Capt", "This is it. The Music Box. Everything ends here. Or begins. Or, you know, plays."], ["Pip", "Ready, Capt?"], ["Capt", "Always. Let's make some noise."]],
}
const BOSS_DEFEAT := {
	"mogul": [["Mossback Mogul", "Zzz... huh? Did I smash something? Sorry. I get cranky when napping. Take this Star."], ["Capt", "Apology accepted. Naps are important."]],
	"scarabella": [["Madame Scarabella", "My hair! My glorious, sandy, windblown hair! You win, tiny hero. Take your Star and leave me to my mirror."]],
	"gus": [["Gearhead Gus", "Squeak... power... down... Please... oil... me..."], ["Pip", "Aw. Let's fix him later."]],
	"brinebeard": [["Captain Brinebeard", "Arr! Ye've outsmarted me! I'll go back to me knitting. Octopus knitting is a calming hobby."]],
	"frank": [["Frostbite Frank", "Brrr... I'm just... a lonely robot... who wanted friends... Okay. Here's your Star."], ["Pip", "Next time, send a postcard."]],
	"baron": [["Baron Von Grumblebelt", "NO! The song! It's ruined! ...Wait. It sounds... better without me?"], ["Capt", "Funny how that works."], ["Baron Von Grumblebelt", "Fine. Take the Stars. I'll go... take up the triangle. Quietly."]],
}
const BOSS_INTRO := {
	"mogul": [["Capt", "Pip, that tree is giant. And snoring. And possibly dangerous."], ["Pip", "Let's wake him up gently."], ["Capt", "With a hat? That's the opposite of gentle."]],
	"scarabella": [["Madame Scarabella", "Who dares to disturb my beauty sleep? Do you know what a dune does to a hairstyle?!"]],
	"gus": [["Gearhead Gus", "SQUEAK. INTRUDERS. RECYCLING MODE ACTIVATED. SQUEAK."]],
	"brinebeard": [["Captain Brinebeard", "Arr! A landlubber in me bay! Walk the plank! ...Or just fall in. Either way, splash."]],
	"frank": [["Frostbite Frank", "CHILLY GREETINGS. I WILL FREEZE YOU INTO A VERY RUDE STATUE."]],
	"baron": [["Baron Von Grumblebelt", "So, the little hero and the talking hat. Come to ruin my symphony? HOW DARE YOU BE ON TIME."], ["Capt", "Nice hat, Baron. Mine's better."], ["Baron Von Grumblebelt", "WE'LL SEE ABOUT THAT. WIND THE KEY!"]],
}
const ENDING := [
	["", "The Music Box fell silent. Then, slowly, a new tune began to play. A friendlier one."],
	["Baron Von Grumblebelt", "...It's catchy. Is that a triangle I hear?"],
	["Skipper Mabel", "We did it! The engine's purring! And only slightly on fire!"],
	["Capt", "Pip, I have to say. For a sleepy kid with snacks, you did okay."],
	["Pip", "Thanks, Capt. Want to go again?"],
	["Capt", "Always. But first: snacks."],
	["", "THE END. Thanks for playing! (You can keep collecting Stars. The hat insists.)"],
]
const STAR_FIRST := [["Capt", "A Star! It tingles! In a good way!"]]
