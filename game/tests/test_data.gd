extends RefCounted
func run(t) -> void:
	var ids := Kingdoms.star_ids()
	t.check(ids.size() >= 60, "at least 60 stars (have %d)" % ids.size())
	var seen := {}
	for i in ids:
		t.check(not seen.has(i), "unique star id " + i)
		seen[i] = true
	t.check(NpcData.count() >= 25, "25+ NPCs (have %d)" % NpcData.count())
	t.check(CreatureData.count() >= 15, "15+ capturables (have %d)" % CreatureData.count())
	t.check(BossData.DATA.size() >= 6, "5 bosses + final")
	for k in Kingdoms.ORDER:
		var kd: Dictionary = Kingdoms.DATA[k]
		t.check(kd["coin"]["name"] != "", k + " has coin currency")
		t.check(kd["stars"].size() >= 8, k + " has 8+ stars")
		var kinds := {}
		for s in kd["stars"]:
			kinds[s["kind"]] = true
		for must in ["challenge", "hidden", "quest", "coins", "shop", "capture"]:
			t.check(kinds.has(must), "%s has a %s star" % [k, must])
		for n in kd["npcs"]:
			t.check(NpcData.DATA.has(n), "npc exists: " + n)
		if kd.has("quests"):
			for q in kd["quests"]:
				var nid: String = kd["quests"][q]["npc"]
				t.check(NpcData.DATA[nid].has("quest"), "quest npc has quest block: " + nid)
				t.check(NpcData.DATA[nid]["quest"]["star"] == k + "_" + q, "quest star id matches for " + nid)
		for c in kd["creatures"]:
			t.check(CreatureData.DATA.has(c), "creature exists " + c)
		t.check(MusicGen.TRACKS.has(kd["music"]), k + " has music track")
		if kd["boss"] != "":
			t.check(BossData.DATA.has(kd["boss"]), k + " boss defined")
		t.check(kd.has("capture_kind") and CreatureData.DATA.has(kd["capture_kind"]), k + " capture challenge creature")
	for id in NpcData.DATA:
		var n: Dictionary = NpcData.DATA[id]
		t.check(n["lines"].size() >= 1, id + " has dialogue")
		for l in n["lines"]:
			t.check(str(l).length() > 3, id + " has non-empty line")
		if n.has("quest"):
			for key in ["ask", "thanks", "after", "star", "item"]:
				t.check(n["quest"].has(key), id + " quest has " + key)
		t.check(Kingdoms.DATA.has(n["kingdom"]), id + " belongs to a kingdom")
	# every NPC in data is placed in exactly one kingdom
	var placed := {}
	for k in Kingdoms.DATA:
		for n in Kingdoms.DATA[k]["npcs"]:
			t.check(not placed.has(n), "npc placed once: " + n)
			placed[n] = true
	t.check(placed.size() == NpcData.count(), "every NPC is placed somewhere")
	# shops
	for k in Kingdoms.ORDER:
		var items := ItemData.shop_items(k)
		t.check(items.size() >= 3, k + " shop has items")
	t.check(Cutscenes.INTRO.size() >= 8, "intro cutscene has lines")
	t.check(Cutscenes.ENDING.size() >= 5, "ending cutscene has lines")
	for b in BossData.DATA:
		t.check(Cutscenes.BOSS_DEFEAT.has(b), "boss defeat lines " + b)
		t.check(Cutscenes.BOSS_INTRO.has(b), "boss intro lines " + b)
