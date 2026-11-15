extends RefCounted
## UI smoke tests: every menu builds, shop/map/pause work, intro plays to the end.
func run(t) -> void:
	var g = t.root.get_node("Game")
	g.data = g.blank_data()
	var holder := Control.new()
	holder.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	t.root.add_child(holder)
	# settings + controls menus
	var sm := SettingsMenu.new()
	holder.add_child(sm)
	await t.frames(3)
	t.check(sm.get_child_count() > 1, "settings menu builds")
	sm.queue_free()
	var cm := ControlsMenu.new()
	holder.add_child(cm)
	await t.frames(3)
	t.check(cm.buttons.size() >= 10, "controls menu lists actions")
	cm.queue_free()
	# title screen
	var ts := TitleScreen.new()
	holder.add_child(ts)
	await t.frames(3)
	ts._slots()
	await t.frames(3)
	t.check(ts.menu != null, "title screen slot select builds")
	ts.queue_free()
	# world with HUD: shop, map, pause
	var w := World.new()
	w.kingdom_id = "forest"
	t.root.add_child(w)
	await t.frames(5)
	var hud: Hud = w.hud
	hud.dialogue.auto_advance = true
	for k in Kingdoms.ORDER:
		g.add_coins(k, 100)
		await hud.open_shop(k)
	await hud.open_shop("hub")
	t.check(not hud.menu_open, "shop closes")
	var dest: String = await hud.open_map()
	t.check(dest == "", "map closes with no destination in auto mode")
	hud._open_pause()
	t.check(t.get_tree().paused, "pause pauses the tree")
	await t.frames(3)
	hud._resume()
	t.check(not t.get_tree().paused, "resume unpauses")
	# purchase every kind
	for k in ["forest", "desert", "city"]:
		for it in ItemData.shop_items(k):
			hud._apply_purchase(it)
	t.check(g.has_star("forest_shop") and g.has_star("desert_shop"), "shop stars purchasable")
	t.check(g.max_health() == 6, "heart snacks reach max health 6")
	t.check(g.data["outfit"] != "", "outfit equipped after purchase")
	# confirm dialog
	var yes: bool = await hud.confirm("Test?")
	t.check(yes, "confirm returns answer (auto)")
	# dialogue with skip-all and normal
	await hud.say([["A", "hello"], ["B", "world"]])
	t.check(not hud.dialogue.active, "dialogue finishes")
	w.queue_free()
	await t.frames(3)
	# intro scene plays through
	var intro := IntroScene.new()
	t.root.add_child(intro)
	await t.frames(3)
	intro.dlg.auto_advance = true
	var timeout := 0
	while intro.dlg.active or timeout < 5:
		await t.frames(5)
		timeout += 1
		if timeout > 600:
			break
	t.check(timeout <= 600, "intro cutscene completes (%d)" % timeout)
	intro.queue_free()
	holder.queue_free()
	await t.frames(2)
