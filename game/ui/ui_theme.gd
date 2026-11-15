class_name UiTheme
extends RefCounted
## Chunky, friendly UI theme built entirely in code.
static var _theme: Theme

static func get_theme() -> Theme:
	if _theme:
		return _theme
	var t := Theme.new()
	t.default_font_size = 22
	var normal := _box(Color(0.15, 0.2, 0.4, 0.92), Color(1, 0.9, 0.4), 3)
	var hover := _box(Color(0.3, 0.4, 0.8, 0.98), Color(1, 1, 0.7), 4)
	var pressed := _box(Color(0.9, 0.6, 0.15, 1.0), Color.WHITE, 4)
	for s in ["normal", "disabled"]:
		t.set_stylebox(s, "Button", normal)
	t.set_stylebox("hover", "Button", hover)
	t.set_stylebox("focus", "Button", hover)
	t.set_stylebox("pressed", "Button", pressed)
	t.set_color("font_color", "Button", Color.WHITE)
	t.set_color("font_disabled_color", "Button", Color(0.6, 0.6, 0.7))
	t.set_stylebox("panel", "PanelContainer", _box(Color(0.1, 0.12, 0.3, 0.95), Color(1, 0.85, 0.3), 4))
	t.set_stylebox("panel", "Panel", _box(Color(0.1, 0.12, 0.3, 0.95), Color(1, 0.85, 0.3), 4))
	t.set_color("font_color", "Label", Color.WHITE)
	t.set_constant("outline_size", "Label", 4)
	t.set_color("font_outline_color", "Label", Color(0.05, 0.05, 0.2))
	_theme = t
	return t

static func _box(bg: Color, border: Color, bw: int) -> StyleBoxFlat:
	var b := StyleBoxFlat.new()
	b.bg_color = bg
	b.border_color = border
	b.set_border_width_all(bw)
	b.set_corner_radius_all(14)
	b.content_margin_left = 16
	b.content_margin_right = 16
	b.content_margin_top = 8
	b.content_margin_bottom = 8
	return b

static func label(text: String, size := 22, color := Color.WHITE) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	return l

static func button(text: String, cb: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(func():
		Audio.sfx("menu_ok")
		cb.call())
	b.focus_entered.connect(func(): Audio.sfx("menu_move", 1.0, -10.0))
	b.mouse_entered.connect(func(): b.grab_focus())
	return b
