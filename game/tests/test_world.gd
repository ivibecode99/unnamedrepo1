extends RefCounted
## Builds every kingdom headless and checks content counts + stability.
func run(t) -> void:
	var g = t.root.get_node("Game")
	g.data = g.blank_data()
	g.slot = -1
	var total_placed := {}
	for k in Kingdoms.all_ids():
		g.data = g.blank_data()
		g.health = 3
		print("  building ", k, " t=", Time.get_ticks_msec())
		var w := World.new()
		w.kingdom_id = k
		t.root.add_child(w)
		await t.frames(8)
		t.check(w.player != null and is_instance_valid(w.player), k + ": player spawned")
		await t.frames(60)
		t.check(w.player.global_position.y > -5.0, "%s: player stands on ground (y=%.2f)" % [k, w.player.global_position.y])
		t.check(w.player.is_on_floor(), k + ": player on floor after spawn")
		var kd: Dictionary = Kingdoms.DATA[k]
		# stars placed in the world
		var star_nodes: Array = t.get_nodes_in_group("star_pickup")
		var ids := {}
		for s in star_nodes:
			if w.is_ancestor_of(s):
				ids[s.star_id] = true
		for s in kd["stars"]:
			var kind: String = s["kind"]
			if kind in ["challenge", "hidden", "capture", "summit"]:
				t.check(ids.has(s["id"]), "%s: star %s is placed in the level" % [k, s["id"]])
				total_placed[s["id"]] = true
		var npcs := 0
		for n in t.get_nodes_in_group("npc"):
			if w.is_ancestor_of(n):
				npcs += 1
		t.check(npcs == kd["npcs"].size(), "%s: %d NPCs placed (want %d)" % [k, npcs, kd["npcs"].size()])
		var coins := 0
		for c in t.get_nodes_in_group("coin"):
			if w.is_ancestor_of(c):
				coins += 1
		if kd.has("coin_goal"):
			t.check(coins >= 50, "%s: enough coins to reach the coin star (%d)" % [k, coins])
		if kd.has("quests"):
			var items := 0
			for c in w.get_children():
				if c is QuestItem:
					items += 1
			t.check(items == 2, k + ": two quest items placed")
		if kd["boss"] != "":
			t.check(w.gen.arena != null and w.gen.arena.boss != null, k + ": boss arena has boss")
		var caps := 0
		for c in t.get_nodes_in_group("capturable"):
			if w.is_ancestor_of(c):
				caps += 1
		if k not in ["hub", "final"]:
			t.check(caps >= 3, "%s: capturable creatures present (%d)" % [k, caps])
		# walk around a bit with input to catch runtime errors
		w.player.scripted = t.inp({"move": Vector2(0.3, -1), "jump_p": true})
		await t.frames(2)
		w.player.scripted = t.inp({"move": Vector2(0.3, -1)})
		await t.frames(60)
		t.check(not w.player.global_position.is_equal_approx(Vector3.ZERO), k + ": player can move")
		w.queue_free()
		await t.frames(3)
	t.check(total_placed.size() >= 25, "many stars placed directly (%d)" % total_placed.size())
	# coin star triggers once coins reach goal
	g.data = g.blank_data()
	var w2 := World.new()
	w2.kingdom_id = "forest"
	t.root.add_child(w2)
	await t.frames(5)
	g.add_coins("forest", 40)
	await t.frames(5)
	t.check(w2.coin_star_spawned, "coin star spawns at 40 coins")
	# collecting the star stores it
	var found: StarPickup = null
	for s in t.get_nodes_in_group("star_pickup"):
		if s.star_id == "forest_coins":
			found = s
	t.check(found != null, "coin star pickup exists")
	if found:
		found.collect()
		t.check(g.has_star("forest_coins"), "collected coin star saved to state")
	w2.queue_free()
	await t.frames(3)
	# NPC fetch quest flow
	g.data = g.blank_data()
	var w3 := World.new()
	w3.kingdom_id = "forest"
	t.root.add_child(w3)
	await t.frames(5)
	w3.hud.dialogue.auto_advance = true
	var dale: Npc = null
	for n in t.get_nodes_in_group("npc"):
		if n.npc_id == "dale" and w3.is_ancestor_of(n):
			dale = n
	t.check(dale != null, "Dale exists")
	w3.player.global_position = dale.global_position + Vector3(1.5, 1, 0)
	await t.frames(30)
	dale.interact(w3.player)
	await t.frames(60)
	t.check(not g.has_star("forest_quest1"), "no star before finding item")
	g.data["items"].append("forest_quest1_item")
	dale.interact(w3.player)
	await t.frames(120)
	var spawned := false
	for s in t.get_nodes_in_group("star_pickup"):
		if s.star_id == "forest_quest1":
			spawned = true
	t.check(spawned or g.has_star("forest_quest1"), "returning the item gives the quest star")
	# shop purchase
	g.add_coins("forest", 100)
	var before: int = g.coins("forest")
	w3.hud._apply_purchase({"kind": "heart", "id": "heart_forest", "value": ""})
	t.check(g.max_health() == 4, "heart purchase raises max health")
	t.check(g.spend_coins("forest", 25), "shop spend")
	w3.queue_free()
	await t.frames(3)
