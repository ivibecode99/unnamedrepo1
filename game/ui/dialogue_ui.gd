class_name DialogueUI
extends Control
## Typewriter dialogue box with speaker, skip (current line / whole conversation) and auto-skip setting.
signal finished
var panel: PanelContainer
var name_label: Label
var text_label: RichTextLabel
var hint: Label
var active := false
var auto_advance := false         # tests / cutscene autoplay
var skip_all := false
var yes_no_box: HBoxContainer
var _answer := false
var _answered := false

func _ready() -> void:
	theme = UiTheme.get_theme()
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	process_mode = Node.PROCESS_MODE_ALWAYS
	panel = PanelContainer.new()
	panel.anchor_left = 0.06
	panel.anchor_right = 0.94
	panel.anchor_top = 0.68
	panel.anchor_bottom = 0.96
	add_child(panel)
	var vb := VBoxContainer.new()
	panel.add_child(vb)
	name_label = UiTheme.label("", 24, Color(1, 0.9, 0.4))
	vb.add_child(name_label)
	text_label = RichTextLabel.new()
	text_label.bbcode_enabled = false
	text_label.fit_content = false
	text_label.scroll_active = false
	text_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	text_label.add_theme_font_size_override("normal_font_size", 24)
	vb.add_child(text_label)
	hint = UiTheme.label("", 16, Color(0.8, 0.85, 1.0))
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	vb.add_child(hint)
	yes_no_box = HBoxContainer.new()
	yes_no_box.alignment = BoxContainer.ALIGNMENT_CENTER
	yes_no_box.visible = false
	vb.add_child(yes_no_box)
	panel.visible = false

func say(lines: Array, default_speaker := "") -> void:
	active = true
	skip_all = false
	panel.visible = true
	Audio.duck(true)
	for ln in lines:
		var spk: String = default_speaker
		var txt := ""
		if ln is Array:
			spk = str(ln[0])
			txt = str(ln[1])
		else:
			txt = str(ln)
		await _show_line(spk, txt)
		if skip_all:
			break
	panel.visible = false
	active = false
	Audio.duck(false)
	finished.emit()

func _pressed_advance() -> bool:
	return Input.is_action_just_pressed("jump") or Input.is_action_just_pressed("ui_accept") or Input.is_action_just_pressed("throw")

func _show_line(spk: String, txt: String) -> void:
	name_label.text = spk
	name_label.visible = spk != ""
	text_label.text = txt
	text_label.visible_characters = 0
	hint.text = "%s: next    %s: skip all" % [Settings.key_name("jump").split(" / ")[0], Settings.key_name("skip").split(" / ")[0]]
	var total := txt.length()
	var shown := 0.0
	var t := 0.0
	if Settings.auto_skip:
		shown = total
	while shown < total:
		await get_tree().process_frame
		t += get_process_delta_time()
		shown += get_process_delta_time() * 48.0 * Settings.text_speed
		text_label.visible_characters = int(shown)
		if int(shown) % 3 == 0 and int(shown) != int(shown - 1):
			Audio.sfx("talk", 1.0 + (hash(spk) % 5) * 0.1, -16.0)
		if t > 0.12 and (_pressed_advance() or auto_advance):
			shown = total
		if Input.is_action_just_pressed("skip"):
			skip_all = true
			text_label.visible_characters = -1
			return
	text_label.visible_characters = -1
	var wait := 0.0
	while true:
		await get_tree().process_frame
		wait += get_process_delta_time()
		if auto_advance and wait > 0.02:
			return
		if wait > 0.1 and _pressed_advance():
			return
		if Input.is_action_just_pressed("skip"):
			skip_all = true
			return

## Yes/No question. Returns bool.
func ask(question: String) -> bool:
	active = true
	panel.visible = true
	name_label.visible = false
	text_label.text = question
	text_label.visible_characters = -1
	hint.text = ""
	for c in yes_no_box.get_children():
		c.queue_free()
	_answered = false
	var yes := UiTheme.button("Yes", func(): _answer = true; _answered = true)
	var no := UiTheme.button("No", func(): _answer = false; _answered = true)
	yes_no_box.add_child(yes)
	yes_no_box.add_child(no)
	yes_no_box.visible = true
	yes.grab_focus()
	if auto_advance:
		_answer = true
		_answered = true
	while not _answered:
		await get_tree().process_frame
		if Input.is_action_just_pressed("ui_cancel"):
			_answer = false
			_answered = true
	yes_no_box.visible = false
	panel.visible = false
	active = false
	return _answer
