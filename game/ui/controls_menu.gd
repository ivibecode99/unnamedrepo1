class_name ControlsMenu
extends Control
## Shows bindings; keyboard actions can be rebound; gamepad mapping listed.
signal closed
const LIST := [["move_forward", "Move forward"], ["move_back", "Move back"], ["move_left", "Move left"], ["move_right", "Move right"],
	["jump", "Jump / talk / swim up"], ["crouch", "Crouch / ground pound / dive down"], ["throw", "Throw Capt / release creature"],
	["spin", "Hat spin / creature ability"], ["roll", "Roll"], ["dive", "Dive"], ["pause", "Pause"], ["skip", "Skip text / recenter camera"]]
var waiting := ""
var buttons := {}

func _ready() -> void:
	theme = UiTheme.get_theme()
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.6)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var p := PanelContainer.new()
	p.anchor_left = 0.12
	p.anchor_right = 0.88
	p.anchor_top = 0.05
	p.anchor_bottom = 0.95
	add_child(p)
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	p.add_child(sc)
	var vb := VBoxContainer.new()
	vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(vb)
	var t := UiTheme.label("Controls (click a key to rebind)", 30, Color(1, 0.9, 0.4))
	vb.add_child(t)
	var first: Button = null
	for e in LIST:
		var hb := HBoxContainer.new()
		var l := UiTheme.label(e[1], 20)
		l.custom_minimum_size.x = 380
		hb.add_child(l)
		var b := UiTheme.button(Settings.key_name(e[0]), func(): _begin(e[0]))
		b.custom_minimum_size.x = 260
		hb.add_child(b)
		buttons[e[0]] = b
		vb.add_child(hb)
		if first == null:
			first = b
	vb.add_child(UiTheme.label("Gamepad: Left stick move · A jump · B crouch/pound · X throw · Y spin · R1 roll · L1/R2 dive · Right stick camera · Start pause · Select skip", 16, Color(0.8, 0.9, 1)))
	vb.add_child(UiTheme.button("Reset to defaults", func():
		Settings.reset_bindings()
		_refresh()))
	vb.add_child(UiTheme.button("Back", func():
		closed.emit()
		queue_free()))
	first.call_deferred("grab_focus")

func _begin(action: String) -> void:
	waiting = action
	buttons[action].text = "Press a key..."

func _refresh() -> void:
	for a in buttons:
		buttons[a].text = Settings.key_name(a)

func _input(ev: InputEvent) -> void:
	if waiting == "":
		return
	if ev is InputEventKey and ev.pressed:
		if ev.physical_keycode != KEY_ESCAPE:
			Settings.rebind_key(waiting, ev.physical_keycode)
		waiting = ""
		_refresh()
		get_viewport().set_input_as_handled()
