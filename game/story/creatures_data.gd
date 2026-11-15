class_name CreatureData
extends RefCounted
## Capturable creatures/objects. Movement/ability parameters are interpreted by Capturable.gd.
## speed: run speed; jump: jump velocity; fly: can fly/hover; ability: special on throw-less "action" button.
const DATA := {
	"hopper":    {"name": "Hopper",     "kingdom": "forest", "color": Color(0.35, 0.8, 0.3),  "speed": 6.0,  "jump": 24.0, "fly": false, "ability": "superjump", "desc": "Boing! Each hop goes higher."},
	"buzzer":    {"name": "Buzzer",     "kingdom": "forest", "color": Color(1.0, 0.85, 0.2),  "speed": 8.0,  "jump": 10.0, "fly": true,  "ability": "flap",      "desc": "Flap to fly. Wobbly but free."},
	"stumpling": {"name": "Stumpling",  "kingdom": "forest", "color": Color(0.6, 0.4, 0.22),  "speed": 5.0,  "jump": 9.0,  "fly": false, "ability": "stomp",     "desc": "Stomp! Smashes crates and enemies."},
	"scarab":    {"name": "Scarab",     "kingdom": "desert", "color": Color(0.2, 0.55, 0.7),  "speed": 13.0, "jump": 12.0, "fly": false, "ability": "dash",      "desc": "Skitter-dash at crazy speed."},
	"cactoid":   {"name": "Cactoid",    "kingdom": "desert", "color": Color(0.3, 0.7, 0.35),  "speed": 6.0,  "jump": 11.0, "fly": false, "ability": "spines",    "desc": "Fires spines in every direction."},
	"sandworm":  {"name": "Sandworm",   "kingdom": "desert", "color": Color(0.85, 0.65, 0.4), "speed": 9.0,  "jump": 14.0, "fly": false, "ability": "burrow",    "desc": "Burrow under sand, pop out high."},
	"zipbot":    {"name": "Zipbot",     "kingdom": "city",   "color": Color(1.0, 0.7, 0.15),  "speed": 16.0, "jump": 9.0,  "fly": false, "ability": "boost",     "desc": "A tiny taxi. Zoooom."},
	"pigeon":    {"name": "Pigeon",     "kingdom": "city",   "color": Color(0.6, 0.62, 0.7),  "speed": 9.0,  "jump": 11.0, "fly": true,  "ability": "glide",     "desc": "Glide across rooftops. Coo."},
	"springbot": {"name": "Springbot",  "kingdom": "city",   "color": Color(0.9, 0.3, 0.4),   "speed": 6.0,  "jump": 26.0, "fly": false, "ability": "superjump", "desc": "Always bouncing, always sproing."},
	"jelly":     {"name": "Jellyfloat", "kingdom": "ocean",  "color": Color(0.9, 0.5, 0.9),   "speed": 5.0,  "jump": 14.0, "fly": true,  "ability": "float",     "desc": "Bobs upward. Swim-sky champion."},
	"crab":      {"name": "Pinchy",     "kingdom": "ocean",  "color": Color(0.95, 0.35, 0.25),"speed": 10.0, "jump": 10.0, "fly": false, "ability": "pinch",     "desc": "Scuttle fast, pinch hard."},
	"angler":    {"name": "Glowfin",    "kingdom": "ocean",  "color": Color(0.3, 0.5, 0.9),   "speed": 12.0, "jump": 8.0,  "fly": false, "ability": "swimfast",  "desc": "Torpedo through water."},
	"penguin":   {"name": "Waddlebelly","kingdom": "snow",   "color": Color(0.2, 0.25, 0.35), "speed": 11.0, "jump": 10.0, "fly": false, "ability": "slide",     "desc": "Belly-slide forever."},
	"yeti":      {"name": "Yeti Jr.",   "kingdom": "snow",   "color": Color(0.95, 0.97, 1.0), "speed": 7.0,  "jump": 11.0, "fly": false, "ability": "smash",     "desc": "Smash ice walls with a mighty fist."},
	"snowball":  {"name": "Rolly",      "kingdom": "snow",   "color": Color(0.85, 0.92, 1.0), "speed": 12.0, "jump": 9.0,  "fly": false, "ability": "roll",      "desc": "Rolls, grows, flattens things."},
	"fireflea":  {"name": "Fireflea",   "kingdom": "volcano","color": Color(1.0, 0.5, 0.1),   "speed": 9.0,  "jump": 18.0, "fly": false, "ability": "dash",      "desc": "Flaming dash, hops over lava."},
	"lavagolem": {"name": "Lava Golem", "kingdom": "volcano","color": Color(0.5, 0.2, 0.15),  "speed": 6.0,  "jump": 20.0, "fly": false, "ability": "lavawalk",  "desc": "Strolls through lava. Rocky jumps."},
	"cannon":    {"name": "Cannon",     "kingdom": "volcano","color": Color(0.3, 0.3, 0.35),  "speed": 0.0,  "jump": 0.0,  "fly": false, "ability": "cannon",    "desc": "Aim and fire yourself skyward."},
}

static func count() -> int:
	return DATA.size()
