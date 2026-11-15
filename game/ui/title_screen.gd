class_name TitleScreen
extends Control
## Title screen + 3-slot save select.
var vb: VBoxContainer
var stars_bg: Array = []
var t := 0.0
var menu: Control

func _ready() -> void:
	theme = UiTheme.get_theme()
	set_anchors_preset(Control.PRESET_FULL_RECT)
	process_mode = Node.PROCESS_MODE_ALWAYS
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	for i in 60:
		stars_bg.append([Vector2(randf(), randf()), randf() * 6.0, randf_range(0.5, 1.5)])
	Audio.play_music("title")
	_main_menu()

func _clear() -> void:
	if menu:
		menu.queue_free()
	menu = Control.new()
	menu.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(menu)

func _main_menu() -> void:
	_clear()
	var box := VBoxContainer.new()
	box.anchor_left = 0.35
	box.anchor_right = 0.65
	box.anchor_top = 0.5
	box.anchor_bottom = 0.92
	box.add_theme_constant_override("separation", 12)
	menu.add_child(box)
	var play := UiTheme.button("Play", _slots)
	box.add_child(play)
	box.add_child(UiTheme.button("Settings", func():
		var s := SettingsMenu.new()
		s.closed.connect(_main_menu)
		menu.queue_free()
		menu = s
		add_child(s)))
	box.add_child(UiTheme.button("Controls", func():
		var s := ControlsMenu.new()
		s.closed.connect(_main_menu)
		menu.queue_free()
		menu = s
		add_child(s)))
	if not OS.has_feature("web"):
		box.add_child(UiTheme.button("Quit", func(): get_tree().quit()))
	play.call_deferred("grab_focus")

func _slots() -> void:
	_clear()
	var box := VBoxContainer.new()
	box.anchor_left = 0.25
	box.anchor_right = 0.75
	box.anchor_top = 0.42
	box.anchor_bottom = 0.95
	box.add_theme_constant_override("separation", 10)
	menu.add_child(box)
	var first: Button = null
	for s in Game.SLOTS:
		var info := Game.slot_info(s)
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 8)
		var label := ""
		if info.is_empty():
			label = "Slot %d — New Game" % (s + 1)
		elif info.get("corrupt", false):
			label = "Slot %d — Corrupt save (overwrite)" % (s + 1)
		else:
			label = "Slot %d — %d Stars — %s%s" % [s + 1, info["stars"], Game.format_time(info["time"]), "  ★END" if info.get("ending", false) else ""]
		var b := UiTheme.button(label, func(): _choose(s, info))
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(b)
		if not info.is_empty():
			row.add_child(UiTheme.button("Delete", func(): _confirm_delete(s)))
		box.add_child(row)
		if first == null:
			first = b
	box.add_child(UiTheme.button("Back", _main_menu))
	first.call_deferred("grab_focus")

func _confirm_delete(s: int) -> void:
	_clear()
	var box := VBoxContainer.new()
	box.anchor_left = 0.3
	box.anchor_right = 0.7
	box.anchor_top = 0.5
	box.anchor_bottom = 0.8
	menu.add_child(box)
	box.add_child(UiTheme.label("Delete slot %d? This cannot be undone." % (s + 1), 24))
	var no := UiTheme.button("No, keep it", _slots)
	box.add_child(no)
	box.add_child(UiTheme.button("Yes, delete", func():
		Game.delete_slot(s)
		_slots()))
	no.call_deferred("grab_focus")

func _choose(s: int, info: Dictionary) -> void:
	if info.is_empty() or info.get("corrupt", false):
		Game.new_game(s)
		Game.goto_intro()
	else:
		if Game.load_game(s):
			Game.goto_world("hub" if Game.current_kingdom == "" else Game.current_kingdom)
		else:
			Game.new_game(s)
			Game.goto_intro()

func _process(delta: float) -> void:
	t += delta
	queue_redraw()

func _draw() -> void:
	var sz := get_viewport_rect().size
	draw_rect(Rect2(Vector2.ZERO, sz), Color(0.12, 0.1, 0.3))
	for i in 12:
		var y := sz.y * i / 12.0
		draw_rect(Rect2(0, y, sz.x, sz.y / 12.0 + 1), Color(0.12 + i * 0.03, 0.1 + i * 0.025, 0.3 + i * 0.03))
	for s in stars_bg:
		var p: Vector2 = Vector2(s[0].x * sz.x, s[0].y * sz.y * 0.6)
		var a := 0.5 + 0.5 * sin(t * s[2] + s[1])
		draw_circle(p, 2.0 * s[2], Color(1, 1, 0.8, a))
	# hills
	for i in 3:
		var pts := PackedVector2Array()
		for x in range(0, int(sz.x) + 40, 40):
			pts.append(Vector2(x, sz.y * (0.78 + i * 0.07) + sin(x * 0.01 + i * 2.0 + t * 0.2) * 30.0))
		pts.append(Vector2(sz.x, sz.y))
		pts.append(Vector2(0, sz.y))
		draw_colored_polygon(pts, Color(0.1 + i * 0.05, 0.3 + i * 0.1, 0.25 + i * 0.05))
	# title
	var font := get_theme_default_font()
	var title := "CAPT & CO."
	var fs := int(sz.y * 0.13)
	var w := font.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var pos := Vector2((sz.x - w) * 0.5, sz.y * 0.28 + sin(t * 2.0) * 6.0)
	draw_string(font, pos + Vector2(4, 5), title, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(0.05, 0.02, 0.15))
	draw_string(font, pos, title, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1.0, 0.85, 0.25))
	var sub := "A hat-tossing, star-collecting, snack-fuelled adventure"
	var sw := font.get_string_size(sub, HORIZONTAL_ALIGNMENT_LEFT, -1, int(sz.y * 0.035)).x
	draw_string(font, Vector2((sz.x - sw) * 0.5, sz.y * 0.36), sub, HORIZONTAL_ALIGNMENT_LEFT, -1, int(sz.y * 0.035), Color(0.85, 0.9, 1.0))
	# Capt hat icon
	var hc := Vector2(sz.x * 0.5, sz.y * 0.43)
	draw_circle(hc + Vector2(0, 8), 34, Color(0.6, 0.1, 0.2))
	draw_circle(hc, 32, Color(0.9, 0.2, 0.35))
	draw_rect(Rect2(hc + Vector2(-48, 12), Vector2(96, 10)), Color(0.6, 0.1, 0.25))
	draw_circle(hc + Vector2(-10, 0), 9, Color.WHITE)
	draw_circle(hc + Vector2(12, 0), 9, Color.WHITE)
	draw_circle(hc + Vector2(-8, 1), 4, Color.BLACK)
	draw_circle(hc + Vector2(14, 1), 4, Color.BLACK)
