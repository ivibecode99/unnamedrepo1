class_name Kingdoms
extends RefCounted
## Static data for every kingdom. Star counts etc. are verified by tests/test_data.gd

const ORDER := ["forest", "desert", "city", "ocean", "snow", "volcano"]

const DATA := {
	"hub": {
		"name": "Airship Hiccup", "sub": "Your wobbly home in the clouds", "theme": "hub", "music": "hub", "seed": 1,
		"coin": {"name": "Hiccups", "short": "HP", "color": Color(0.95, 0.85, 0.3)},
		"pal": {"ground": Color(0.72, 0.5, 0.32), "ground2": Color(0.55, 0.38, 0.25), "accent": Color(0.9, 0.3, 0.3), "sky_top": Color(0.35, 0.6, 0.95), "sky_hor": Color(0.85, 0.93, 1.0), "fog": Color(0.8, 0.9, 1.0)},
		"need": 0, "boss": "",
		"stars": [
			{"id": "hub_cat", "title": "Biscuit Goes Missing (Again)", "kind": "quest"},
			{"id": "hub_soup", "title": "Chef Gruntle's Mystery Soup", "kind": "quest"},
			{"id": "hub_deck", "title": "Spotless Deck Hero", "kind": "hidden"},
		],
		"npcs": ["mabel", "nib", "gruntle", "wobbles", "biscuit", "doug", "penny"],
		"creatures": [], "enemies": [],
	},
	"forest": {
		"name": "Fernwhistle Forest", "sub": "Where the trees gossip", "theme": "forest", "music": "forest", "seed": 101,
		"coin": {"name": "Acorns", "short": "AC", "color": Color(0.75, 0.5, 0.2)},
		"pal": {"ground": Color(0.35, 0.72, 0.3), "ground2": Color(0.5, 0.38, 0.22), "accent": Color(0.95, 0.55, 0.2), "sky_top": Color(0.3, 0.6, 0.95), "sky_hor": Color(0.8, 0.95, 0.85), "fog": Color(0.75, 0.92, 0.8)},
		"need": 0, "boss": "mogul",
		"stars": [
			{"id": "forest_boss", "title": "Mossback Mogul Takes a Nap", "kind": "boss"},
			{"id": "forest_tower", "title": "Spiral Stump Climb", "kind": "challenge"},
			{"id": "forest_gap", "title": "Mushroom Hop Marathon", "kind": "challenge"},
			{"id": "forest_hidden1", "title": "Hollow Log Secret", "kind": "hidden"},
			{"id": "forest_hidden2", "title": "Island of Lonely Acorns", "kind": "hidden"},
			{"id": "forest_quest1", "title": "Dale's Dreadful Detour", "kind": "quest"},
			{"id": "forest_quest2", "title": "Bee-hat Rescue", "kind": "quest"},
			{"id": "forest_coins", "title": "Acorn Avalanche (40 Acorns)", "kind": "coins"},
			{"id": "forest_shop", "title": "Nutty Pete's Star Sale", "kind": "shop"},
			{"id": "forest_capture", "title": "Froggy Heights", "kind": "capture"},
		],
		"npcs": ["barkley", "fern", "mossy", "dale", "buzzby", "pete"],
		"quests": {"quest1": {"npc": "dale", "item": "Compass"}, "quest2": {"npc": "buzzby", "item": "Bee Hat"}},
		"creatures": ["hopper", "buzzer", "stumpling"], "enemies": ["walker", "shooter"],
		"capture_kind": "hopper", "shop_npc": "pete", "coin_goal": 40, "shop_price": 25,
	},
	"desert": {
		"name": "Sizzle Sands", "sub": "It's a dry heat. Very dry.", "theme": "desert", "music": "desert", "seed": 202,
		"coin": {"name": "Sunbits", "short": "SB", "color": Color(1.0, 0.8, 0.2)},
		"pal": {"ground": Color(0.95, 0.8, 0.48), "ground2": Color(0.8, 0.55, 0.3), "accent": Color(0.2, 0.7, 0.65), "sky_top": Color(0.35, 0.65, 0.95), "sky_hor": Color(1.0, 0.93, 0.75), "fog": Color(1.0, 0.9, 0.7)},
		"need": 5, "boss": "scarabella",
		"stars": [
			{"id": "desert_boss", "title": "Scarabella's Bad Hair Day", "kind": "boss"},
			{"id": "desert_tower", "title": "Sandstone Staircase", "kind": "challenge"},
			{"id": "desert_gap", "title": "Quicksand Quickstep", "kind": "challenge"},
			{"id": "desert_hidden1", "title": "Pyramid Pocket", "kind": "hidden"},
			{"id": "desert_hidden2", "title": "Mirage? Nope, Star!", "kind": "hidden"},
			{"id": "desert_quest1", "title": "Dr. Dusty's Golden Idol", "kind": "quest"},
			{"id": "desert_quest2", "title": "Tutu's Missing Sandal", "kind": "quest"},
			{"id": "desert_coins", "title": "Sunbit Stash (40 Sunbits)", "kind": "coins"},
			{"id": "desert_shop", "title": "Hump's Oasis Outlet", "kind": "shop"},
			{"id": "desert_capture", "title": "Scarab Sprint Summit", "kind": "capture"},
		],
		"npcs": ["mirage", "sam", "carl", "hump", "dusty", "tutu"],
		"quests": {"quest1": {"npc": "dusty", "item": "Golden Idol"}, "quest2": {"npc": "tutu", "item": "Sandal"}},
		"creatures": ["scarab", "cactoid", "sandworm"], "enemies": ["walker", "charger"],
		"capture_kind": "scarab", "shop_npc": "hump", "coin_goal": 40, "shop_price": 30,
	},
	"city": {
		"name": "Tinkertown", "sub": "Everything is slightly clockwork", "theme": "city", "music": "city", "seed": 303,
		"coin": {"name": "Bolts", "short": "BT", "color": Color(0.75, 0.8, 0.9)},
		"pal": {"ground": Color(0.55, 0.58, 0.68), "ground2": Color(0.4, 0.42, 0.52), "accent": Color(1.0, 0.7, 0.15), "sky_top": Color(0.3, 0.5, 0.85), "sky_hor": Color(0.95, 0.85, 0.9), "fog": Color(0.85, 0.82, 0.92)},
		"need": 12, "boss": "gus",
		"stars": [
			{"id": "city_boss", "title": "Gearhead Gus Powers Down", "kind": "boss"},
			{"id": "city_tower", "title": "Skyscraper Scramble", "kind": "challenge"},
			{"id": "city_gap", "title": "Rooftop Rhythm", "kind": "challenge"},
			{"id": "city_hidden1", "title": "Behind the Billboard", "kind": "hidden"},
			{"id": "city_hidden2", "title": "Sewer Sparkle", "kind": "hidden"},
			{"id": "city_quest1", "title": "Zed's Taxi Keys", "kind": "quest"},
			{"id": "city_quest2", "title": "Mop-3000's Lost Mop", "kind": "quest"},
			{"id": "city_coins", "title": "Bolt Bonanza (40 Bolts)", "kind": "coins"},
			{"id": "city_shop", "title": "Tilly's Discount Star", "kind": "shop"},
			{"id": "city_capture", "title": "Zippy Zipbot Time Trial", "kind": "capture"},
		],
		"npcs": ["gearheart", "bolt", "pigeonpete", "tilly", "zed", "mop"],
		"quests": {"quest1": {"npc": "zed", "item": "Taxi Keys"}, "quest2": {"npc": "mop", "item": "Mop"}},
		"creatures": ["zipbot", "pigeon", "springbot"], "enemies": ["walker", "shooter", "charger"],
		"capture_kind": "springbot", "shop_npc": "tilly", "coin_goal": 40, "shop_price": 35,
	},
	"ocean": {
		"name": "Splashbottom Bay", "sub": "Please do not feed the crabs", "theme": "ocean", "music": "ocean", "seed": 404,
		"coin": {"name": "Pearls", "short": "PL", "color": Color(0.95, 0.95, 1.0)},
		"pal": {"ground": Color(0.95, 0.88, 0.62), "ground2": Color(0.3, 0.55, 0.75), "accent": Color(1.0, 0.45, 0.55), "sky_top": Color(0.25, 0.65, 0.95), "sky_hor": Color(0.75, 0.95, 1.0), "fog": Color(0.55, 0.85, 0.95)},
		"need": 20, "boss": "brinebeard",
		"stars": [
			{"id": "ocean_boss", "title": "Brinebeard's Ink Blot Blues", "kind": "boss"},
			{"id": "ocean_tower", "title": "Lighthouse Leap", "kind": "challenge"},
			{"id": "ocean_gap", "title": "Buoy Bounce Course", "kind": "challenge"},
			{"id": "ocean_hidden1", "title": "Sunken Treasure Chest", "kind": "hidden"},
			{"id": "ocean_hidden2", "title": "Kelp Forest Whisper", "kind": "hidden"},
			{"id": "ocean_quest1", "title": "Diver Dave's Flipper", "kind": "quest"},
			{"id": "ocean_quest2", "title": "Barnacle's Anchor", "kind": "quest"},
			{"id": "ocean_coins", "title": "Pearl Party (40 Pearls)", "kind": "coins"},
			{"id": "ocean_shop", "title": "Clara's Clam Clearance", "kind": "shop"},
			{"id": "ocean_capture", "title": "Jelly Float High", "kind": "capture"},
		],
		"npcs": ["barnacle", "clara", "marla", "crabbycarl", "dave", "kelpie"],
		"quests": {"quest1": {"npc": "dave", "item": "Flipper"}, "quest2": {"npc": "barnacle", "item": "Anchor"}},
		"creatures": ["jelly", "crab", "angler"], "enemies": ["walker", "shooter"],
		"capture_kind": "jelly", "shop_npc": "clara", "coin_goal": 40, "shop_price": 40,
	},
	"snow": {
		"name": "Frostnip Peaks", "sub": "Mind the slippery bits", "theme": "snow", "music": "snow", "seed": 505,
		"coin": {"name": "Flakes", "short": "FL", "color": Color(0.7, 0.9, 1.0)},
		"pal": {"ground": Color(0.93, 0.97, 1.0), "ground2": Color(0.6, 0.8, 0.95), "accent": Color(0.9, 0.25, 0.3), "sky_top": Color(0.4, 0.55, 0.85), "sky_hor": Color(0.9, 0.95, 1.0), "fog": Color(0.88, 0.94, 1.0)},
		"need": 28, "boss": "frank",
		"stars": [
			{"id": "snow_boss", "title": "Frostbite Frank Chills Out", "kind": "boss"},
			{"id": "snow_tower", "title": "Icicle Ascent", "kind": "challenge"},
			{"id": "snow_gap", "title": "Slippery Slalom", "kind": "challenge"},
			{"id": "snow_hidden1", "title": "Igloo Within an Igloo", "kind": "hidden"},
			{"id": "snow_hidden2", "title": "Snowman's Secret", "kind": "hidden"},
			{"id": "snow_quest1", "title": "Bjorn's Runaway Ski", "kind": "quest"},
			{"id": "snow_quest2", "title": "The Cocoa Recipe", "kind": "quest"},
			{"id": "snow_coins", "title": "Flake Frenzy (40 Flakes)", "kind": "coins"},
			{"id": "snow_shop", "title": "Olga's Ice-Fishing Special", "kind": "shop"},
			{"id": "snow_capture", "title": "Penguin Peak Plunge", "kind": "capture"},
		],
		"npcs": ["yolanda", "waddles", "snowbert", "olga", "bjorn", "cocoa"],
		"quests": {"quest1": {"npc": "bjorn", "item": "Ski"}, "quest2": {"npc": "cocoa", "item": "Recipe"}},
		"creatures": ["penguin", "yeti", "snowball"], "enemies": ["walker", "charger"],
		"capture_kind": "penguin", "shop_npc": "olga", "coin_goal": 40, "shop_price": 45,
	},
	"volcano": {
		"name": "Cinder Skies", "sub": "Floating rocks, angry lava", "theme": "volcano", "music": "volcano", "seed": 606,
		"coin": {"name": "Embers", "short": "EM", "color": Color(1.0, 0.45, 0.15)},
		"pal": {"ground": Color(0.35, 0.28, 0.3), "ground2": Color(0.55, 0.2, 0.15), "accent": Color(1.0, 0.55, 0.1), "sky_top": Color(0.45, 0.2, 0.35), "sky_hor": Color(1.0, 0.6, 0.35), "fog": Color(0.9, 0.5, 0.35)},
		"need": 36, "boss": "",
		"stars": [
			{"id": "volcano_summit", "title": "Summit of Snort", "kind": "summit"},
			{"id": "volcano_tower", "title": "Obsidian Obstacle Climb", "kind": "challenge"},
			{"id": "volcano_gap", "title": "Lava Lap Gauntlet", "kind": "challenge"},
			{"id": "volcano_hidden1", "title": "Inside the Cooled Crater", "kind": "hidden"},
			{"id": "volcano_hidden2", "title": "Cloud Nine Cache", "kind": "hidden"},
			{"id": "volcano_quest1", "title": "Gust's Weathervane", "kind": "quest"},
			{"id": "volcano_quest2", "title": "Pyra's Missing Feather", "kind": "quest"},
			{"id": "volcano_coins", "title": "Ember Eruption (40 Embers)", "kind": "coins"},
			{"id": "volcano_shop", "title": "Ember Ed's Hot Deal", "kind": "shop"},
			{"id": "volcano_capture", "title": "Lava Golem Shortcut", "kind": "capture"},
		],
		"npcs": ["pyra", "nimbus", "larry", "gust", "embered", "cinder"],
		"quests": {"quest1": {"npc": "gust", "item": "Weathervane"}, "quest2": {"npc": "pyra", "item": "Feather"}},
		"creatures": ["fireflea", "lavagolem", "cannon"], "enemies": ["walker", "shooter", "charger"],
		"capture_kind": "lavagolem", "shop_npc": "embered", "coin_goal": 40, "shop_price": 50,
	},
	"final": {
		"name": "Grumblebelt's Music Box", "sub": "Please do not wind the key", "theme": "final", "music": "castle", "seed": 707,
		"coin": {"name": "Notes", "short": "NT", "color": Color(0.85, 0.5, 1.0)},
		"pal": {"ground": Color(0.4, 0.3, 0.5), "ground2": Color(0.25, 0.2, 0.35), "accent": Color(1.0, 0.8, 0.3), "sky_top": Color(0.1, 0.05, 0.25), "sky_hor": Color(0.55, 0.3, 0.6), "fog": Color(0.3, 0.2, 0.4)},
		"need": 50, "boss": "baron",
		"stars": [
			{"id": "final_baron", "title": "Grumblebelt's Grand Finale", "kind": "boss"},
			{"id": "final_secret", "title": "Encore!", "kind": "hidden"},
		],
		"npcs": ["tinny"],
		"creatures": ["cannon"], "enemies": ["walker", "shooter", "charger"],
	},
}

static func all_ids() -> Array:
	return ["hub"] + ORDER + ["final"]

static func total_stars() -> int:
	var n := 0
	for k in DATA:
		n += DATA[k]["stars"].size()
	return n

static func star_ids() -> Array:
	var out: Array = []
	for k in DATA:
		for s in DATA[k]["stars"]:
			out.append(s["id"])
	return out

static func star_title(id: String) -> String:
	for k in DATA:
		for s in DATA[k]["stars"]:
			if s["id"] == id:
				return s["title"]
	return id

static func kingdom_of_star(id: String) -> String:
	for k in DATA:
		for s in DATA[k]["stars"]:
			if s["id"] == id:
				return k
	return ""
