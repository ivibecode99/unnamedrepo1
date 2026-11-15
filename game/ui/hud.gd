class_name Hud
extends CanvasLayer
## In-game HUD, dialogue host, shop, map and pause menu.
var world: Node
var player: Player
var dialogue: DialogueUI
var root: Control
var draw_ctl: Control
var toast_label: Label
var toast_t := 0.0
var toast_queue: Array = []
var banner: Label
var banner_t := 0.0
var prompt: Label
var capture_label: Label
var boss_bar: ProgressBar
var boss_name: Label
var boss_panel: Control
var hint_label: Label
var menu_layer: Control
var pause_menu: Control
var menu_open := false
var info_capture := {}
var fps_label: Label

func _ready() -> void:
	layer = 10
	add_to_group("hud")
	process_mode = Node.PROCESS_MODE_ALWAYS
	root = Control.new()
	root.theme = UiTheme.get_theme()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	draw_ctl = HudDraw.new()
	draw_ctl.hud = self
	draw_ctl.set_anchors_preset(Control.PRESET_FULL_RECT)
	draw_ctl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(draw_ctl)
	toast_label = UiTheme.label("", 26, Color(1, 1, 0.7))
	toast_label.set_anchors_preset(Control.PRESET_CENTER_TOP)
	toast_label.anchor_left = 0.0
	toast_label.anchor_right = 1.0
	toast_label.offset_top = 90
	toast_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(toast_label)
	banner = UiTheme.label("", 44, Color(1, 0.9, 0.2))
	banner.anchor_left = 0.0
	banner.anchor_right = 1.0
	banner.anchor_top = 0.25
	banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(banner)
	prompt = UiTheme.label("", 24, Color.WHITE)
	prompt.anchor_left = 0.0
	prompt.anchor_right = 1.0
	prompt.anchor_top = 0.78
	prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(prompt)
	capture_label = UiTheme.label("", 20, Color(1, 0.8, 1))
	capture_label.anchor_left = 0.0
	capture_label.anchor_right = 1.0
	capture_label.anchor_top = 0.9
	capture_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(capture_label)
	boss_panel = Control.new()
	boss_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	boss_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	boss_panel.visible = false
	root.add_child(boss_panel)
	boss_name = UiTheme.label("", 24, Color(1, 0.5, 0.5))
	boss_name.anchor_left = 0.0
	boss_name.anchor_right = 1.0
	boss_name.offset_top = 8
	boss_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	boss_panel.add_child(boss_name)
	boss_bar = ProgressBar.new()
	boss_bar.anchor_left = 0.25
	boss_bar.anchor_right = 0.75
	boss_bar.offset_top = 42
	boss_bar.offset_bottom = 62
	boss_bar.show_percentage = false
	boss_panel.add_child(boss_bar)
	fps_label = UiTheme.label("", 14, Color(1, 1, 1, 0.6))
	fps_label.position = Vector2(8, 8)
	fps_label.visible = false
	root.add_child(fps_label)
	dialogue = DialogueUI.new()
	root.add_child(dialogue)
	menu_layer = Control.new()
	menu_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	menu_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(menu_layer)
	Game.toast.connect(_on_toast)
	Game.star_collected.connect(_on_star)

func _on_toast(text: String) -> void:
	if text != "":
		toast_queue.append(text)

func _on_star(id: String) -> void:
	banner.text = "STAR GET!\n" + Kingdoms.star_title(id)
	banner_t = 3.0

func set_capture(info: Dictionary) -> void:
	info_capture = info
	if info.is_empty():
		capture_label.text = ""
	else:
		capture_label.text = "%s — %s   [%s] ability   [%s] release" % [info["name"], info["desc"], Settings.key_name("spin").split(" / ")[0], Settings.key_name("throw").split(" / ")[0]]

func show_boss(bname: String, total: int) -> void:
	boss_panel.visible = true
	boss_name.text = bname
	boss_bar.max_value = total
	boss_bar.value = total

func update_boss(cur: int, total: int) -> void:
	boss_bar.max_value = total
	boss_bar.value = cur

func hide_boss() -> void:
	boss_panel.visible = false

func say(lines: Array, default_speaker := "") -> void:
	await dialogue.say(lines, default_speaker)

func confirm(text: String) -> bool:
	return await dialogue.ask(text)

func _process(delta: float) -> void:
	if toast_t > 0.0:
		toast_t -= delta
		toast_label.modulate.a = clampf(toast_t, 0.0, 1.0)
		if toast_t <= 0.0:
			toast_label.text = ""
	elif not toast_queue.is_empty():
		toast_label.text = toast_queue.pop_front()
		toast_t = 2.2
	if banner_t > 0.0:
		banner_t -= delta
		banner.modulate.a = clampf(banner_t, 0.0, 1.0)
		if banner_t <= 0.0:
			banner.text = ""
	# interact prompt
	var show := ""
	if player and is_instance_valid(player) and not dialogue.active and not menu_open and player.state in [Player.S.GROUND, Player.S.CROUCH]:
		for n in get_tree().get_nodes_in_group("interactable"):
			if is_instance_valid(n) and n.has_method("can_interact") and n.can_interact(player):
				show = "[%s] Talk / Use" % Settings.key_name("jump").split(" / ")[0]
				break
	prompt.text = show
	if OS.is_debug_build():
		fps_label.visible = Input.is_key_pressed(KEY_F3)
		fps_label.text = "%d FPS" % Engine.get_frames_per_second()
	draw_ctl.queue_redraw()

# ---------------------------------------------------------------- menus
func _clear_menu() -> void:
	for c in menu_layer.get_children():
		c.queue_free()

func _make_panel(title: String, w := 0.5) -> VBoxContainer:
	_clear_menu()
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.55)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	menu_layer.add_child(dim)
	var p := PanelContainer.new()
	p.anchor_left = 0.5 - w * 0.5
	p.anchor_right = 0.5 + w * 0.5
	p.anchor_top = 0.12
	p.anchor_bottom = 0.88
	menu_layer.add_child(p)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 10)
	p.add_child(vb)
	var tl := UiTheme.label(title, 34, Color(1, 0.9, 0.4))
	tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(tl)
	return vb

func open_shop(kingdom: String) -> void:
	menu_open = true
	var closed := false
	var is_hub := kingdom == "hub"
	var coin_name: String = Kingdoms.DATA[kingdom]["coin"]["name"]
	var rebuild: Callable
	rebuild = func():
		var vb := _make_panel("Wardrobe" if is_hub else "Shop", 0.62)
		var bal := UiTheme.label("" if is_hub else "You have %d %s" % [Game.coins(kingdom), coin_name], 22, Color(1, 0.9, 0.5))
		bal.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		vb.add_child(bal)
		var first: Button = null
		if is_hub:
			var def_btn := UiTheme.button("Default look", func():
				Game.data["outfit"] = ""
				Game.data["hat_skin"] = "classic"
				Game.toast.emit("Back to the classic look!")
				_refresh_player_look()
				rebuild.call())
			vb.add_child(def_btn)
			first = def_btn
			for pid in Game.data["purchases"]:
				if str(pid).begins_with("outfit_") or str(pid).begins_with("hat_"):
					var kind := str(pid).split("_")[0]
					var k := str(pid).substr(kind.length() + 1)
					var nm := ""
					if kind == "outfit":
						nm = ItemData.OUTFITS.get(k, {"name": k})["name"] if ItemData.OUTFITS.has(k) else k
					else:
						nm = ItemData.HAT_SKINS[k]["name"] if ItemData.HAT_SKINS.has(k) else k
					var b := UiTheme.button("Wear: " + nm, func():
						if kind == "outfit":
							Game.data["outfit"] = k
						else:
							Game.data["hat_skin"] = k
						_refresh_player_look()
						rebuild.call())
					vb.add_child(b)
		else:
			for it in ItemData.shop_items(kingdom):
				var owned: bool = it["kind"] in ["outfit", "hat"] and (it["id"] in Game.data["purchases"])
				if it["kind"] == "star" and Game.has_star(it["value"]):
					owned = true
				if it["kind"] == "heart" and Game.max_health() >= Game.MAX_HEALTH:
					owned = true
				if it["kind"] == "heart" and it["id"] in Game.data["purchases"]:
					owned = true
				var label := "%s — %d %s%s" % [it["name"], it["price"], Kingdoms.DATA[kingdom]["coin"]["short"], "  (owned)" if owned else ""]
				var b := UiTheme.button(label, func():
					if owned:
						Audio.sfx("deny")
						return
					if not Game.spend_coins(kingdom, it["price"]):
						Audio.sfx("deny")
						Game.toast.emit("Not enough %s!" % coin_name)
						return
					Audio.sfx("buy")
					_apply_purchase(it)
					rebuild.call())
				b.tooltip_text = it["desc"]
				b.disabled = false
				vb.add_child(b)
				var d := UiTheme.label(it["desc"], 16, Color(0.8, 0.85, 1))
				vb.add_child(d)
				if first == null:
					first = b
		var back := UiTheme.button("Close", func(): closed = true)
		vb.add_child(back)
		(first if first else back).call_deferred("grab_focus")
	rebuild.call()
	while not closed:
		await get_tree().process_frame
		if Input.is_action_just_pressed("ui_cancel") or (dialogue.auto_advance):
			closed = true
	_clear_menu()
	menu_open = false

func _refresh_player_look() -> void:
	if player and is_instance_valid(player):
		player.visual.queue_free()
		player._build_visual()

func _apply_purchase(it: Dictionary) -> void:
	match it["kind"]:
		"star":
			Game.collect_star(it["value"])
			Game.toast.emit("Bought a Star!")
		"heal":
			Game.full_heal()
			Game.toast.emit("Yum! Health restored.")
		"heart":
			Game.data["health_max"] = mini(Game.max_health() + 1, Game.MAX_HEALTH)
			Game.data["purchases"].append(it["id"])
			Game.full_heal()
			Game.toast.emit("Max health up!")
		"outfit":
			Game.data["purchases"].append(it["id"])
			Game.data["outfit"] = it["value"]
			_refresh_player_look()
			Game.toast.emit("New outfit!")
		"hat":
			Game.data["purchases"].append(it["id"])
			Game.data["hat_skin"] = it["value"]
			_refresh_player_look()
			Game.toast.emit("Capt looks fancy!")
	Game.save_game()

func open_map() -> String:
	menu_open = true
	var result := ""
	var done := false
	var vb := _make_panel("Kingdom Map", 0.7)
	var sc := UiTheme.label("Stars: %d / %d" % [Game.star_count(), Kingdoms.total_stars()], 22, Color(1, 0.9, 0.4))
	sc.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(sc)
	var first: Button = null
	for k in Kingdoms.ORDER + ["final"]:
		var kd: Dictionary = Kingdoms.DATA[k]
		var have := 0
		for s in kd["stars"]:
			if Game.has_star(s["id"]):
				have += 1
		var unlocked := Game.is_unlocked(k)
		var lbl := "%s   (%d/%d)" % [kd["name"], have, kd["stars"].size()] if unlocked else "%s   — needs %d Stars" % [kd["name"], kd["need"]]
		var b := UiTheme.button(lbl, func():
			result = k
			done = true)
		b.disabled = not unlocked
		vb.add_child(b)
		if first == null and unlocked:
			first = b
	var back := UiTheme.button("Stay on the airship", func(): done = true)
	vb.add_child(back)
	(first if first else back).call_deferred("grab_focus")
	while not done:
		await get_tree().process_frame
		if Input.is_action_just_pressed("ui_cancel") or dialogue.auto_advance:
			done = true
			if dialogue.auto_advance and first:
				result = ""
	_clear_menu()
	menu_open = false
	return result

# ---------------------------------------------------------------- pause
func toggle_pause() -> void:
	if menu_open or dialogue.active:
		return
	if get_tree().paused:
		_resume()
	else:
		_open_pause()

func _open_pause() -> void:
	menu_open = true
	get_tree().paused = true
	Audio.duck(true)
	var vb := _make_panel("Paused", 0.4)
	var resume := UiTheme.button("Resume", _resume)
	vb.add_child(resume)
	vb.add_child(UiTheme.button("Settings", func(): _open_settings()))
	vb.add_child(UiTheme.button("Controls", func(): _open_controls()))
	if Game.current_kingdom != "hub":
		vb.add_child(UiTheme.button("Return to Airship", func():
			_resume()
			Game.save_game()
			Game.goto_world("hub")))
	vb.add_child(UiTheme.button("Save Game", func():
		Game.save_game()
		Game.toast.emit("Game saved!")))
	vb.add_child(UiTheme.button("Save & Quit to Title", func():
		Game.save_game()
		_resume()
		Game.goto_title()))
	resume.call_deferred("grab_focus")

func _resume() -> void:
	_clear_menu()
	menu_open = false
	get_tree().paused = false
	Audio.duck(false)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED if DisplayServer.get_name() != "headless" else Input.MOUSE_MODE_VISIBLE

func _open_settings() -> void:
	_clear_menu()
	var s := SettingsMenu.new()
	s.closed.connect(_open_pause)
	menu_layer.add_child(s)

func _open_controls() -> void:
	_clear_menu()
	var s := ControlsMenu.new()
	s.closed.connect(_open_pause)
	menu_layer.add_child(s)

func _unhandled_input(ev: InputEvent) -> void:
	if ev.is_action_pressed("pause") and not dialogue.active:
		toggle_pause()
		get_viewport().set_input_as_handled()
