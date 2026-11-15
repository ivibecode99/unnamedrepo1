class_name SettingsMenu
extends Control
## Volume, camera invert, quality, text speed etc.
signal closed

func _ready() -> void:
	theme = UiTheme.get_theme()
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.6)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := PanelContainer.new()
	p.anchor_left = 0.2
	p.anchor_right = 0.8
	p.anchor_top = 0.06
	p.anchor_bottom = 0.94
	add_child(p)
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	p.add_child(sc)
	var vb := VBoxContainer.new()
	vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vb.add_theme_constant_override("separation", 8)
	sc.add_child(vb)
	var t := UiTheme.label("Settings", 34, Color(1, 0.9, 0.4))
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(t)
	var first := _slider(vb, "Master volume", Settings.master, 0.0, 1.0, func(v): Settings.master = v; Settings.apply())
	_slider(vb, "Music volume", Settings.music, 0.0, 1.0, func(v): Settings.music = v; Settings.apply())
	_slider(vb, "SFX volume", Settings.sfx, 0.0, 1.0, func(v): Settings.sfx = v; Settings.apply(); Audio.sfx("coin"))
	_slider(vb, "Camera sensitivity", Settings.sensitivity, 0.2, 3.0, func(v): Settings.sensitivity = v)
	_check(vb, "Invert camera Y", Settings.invert_y, func(v): Settings.invert_y = v)
	_check(vb, "Invert camera X", Settings.invert_x, func(v): Settings.invert_x = v)
	_check(vb, "Camera shake", Settings.shake, func(v): Settings.shake = v)
	_slider(vb, "Text speed", Settings.text_speed, 0.25, 4.0, func(v): Settings.text_speed = v)
	_check(vb, "Instant text (skip typing)", Settings.auto_skip, func(v): Settings.auto_skip = v)
	_check(vb, "Fullscreen", Settings.fullscreen, func(v): Settings.fullscreen = v; Settings.apply())
	var q := OptionButton.new()
	for o in ["high", "medium", "low"]:
		q.add_item(o.capitalize() + " graphics")
	q.selected = ["high", "medium", "low"].find(Settings.quality)
	q.item_selected.connect(func(i):
		Settings.quality = ["high", "medium", "low"][i]
		Build.clear_cache()
		Settings.apply())
	vb.add_child(q)
	vb.add_child(UiTheme.label("(Graphics changes apply to newly loaded areas.)", 14, Color(0.8, 0.85, 1)))
	var back := UiTheme.button("Back", func():
		Settings.save_settings()
		closed.emit()
		queue_free())
	vb.add_child(back)
	first.call_deferred("grab_focus")

func _slider(parent: Control, label: String, value: float, lo: float, hi: float, cb: Callable) -> HSlider:
	var hb := HBoxContainer.new()
	var l := UiTheme.label(label, 20)
	l.custom_minimum_size.x = 280
	hb.add_child(l)
	var s := HSlider.new()
	s.min_value = lo
	s.max_value = hi
	s.step = 0.05
	s.value = value
	s.custom_minimum_size = Vector2(260, 28)
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	s.value_changed.connect(func(v): cb.call(v))
	hb.add_child(s)
	parent.add_child(hb)
	return s

func _check(parent: Control, label: String, value: bool, cb: Callable) -> CheckButton:
	var c := CheckButton.new()
	c.text = label
	c.button_pressed = value
	c.toggled.connect(func(v): Audio.sfx("menu_ok"); cb.call(v))
	parent.add_child(c)
	return c
