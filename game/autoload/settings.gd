extends Node
## Settings + input map. Stored in user://settings.json.
const PATH := "user://settings.json"

var master := 0.8
var music := 0.7
var sfx := 0.9
var invert_y := false
var invert_x := false
var sensitivity := 1.0
var quality := "high"        # high / medium / low
var fullscreen := false
var text_speed := 1.0
var auto_skip := false       # dialogue text-skip: show full line instantly
var shake := true
var handheld := false        # R36S/R36H mode (set by --handheld or env CAPT_HANDHELD)
var key_overrides := {}      # action -> physical keycode (keyboard remap)

signal changed

const ACTIONS := {
	# action: [keys, mouse buttons, joy buttons]
	"jump": [[KEY_SPACE], [], [JOY_BUTTON_A]],
	"throw": [[KEY_E], [MOUSE_BUTTON_LEFT], [JOY_BUTTON_X]],
	"spin": [[KEY_Q], [], [JOY_BUTTON_Y]],
	"crouch": [[KEY_C, KEY_CTRL], [], [JOY_BUTTON_B]],
	"roll": [[KEY_SHIFT], [], [JOY_BUTTON_RIGHT_SHOULDER]],
	"dive": [[KEY_V], [MOUSE_BUTTON_RIGHT], [JOY_BUTTON_LEFT_SHOULDER]],
	"pause": [[KEY_ESCAPE, KEY_P], [], [JOY_BUTTON_START]],
	"skip": [[KEY_TAB, KEY_ENTER], [], [JOY_BUTTON_BACK]],
	"cam_left": [[KEY_LEFT], [], []],
	"cam_right": [[KEY_RIGHT], [], []],
	"cam_up": [[KEY_UP], [], []],
	"cam_down": [[KEY_DOWN], [], []],
	"move_left": [[KEY_A], [], [JOY_BUTTON_DPAD_LEFT]],
	"move_right": [[KEY_D], [], [JOY_BUTTON_DPAD_RIGHT]],
	"move_forward": [[KEY_W], [], [JOY_BUTTON_DPAD_UP]],
	"move_back": [[KEY_S], [], [JOY_BUTTON_DPAD_DOWN]],
}
# axis bindings: action -> [axis, sign]
const AXES := {
	"move_left": [JOY_AXIS_LEFT_X, -1.0], "move_right": [JOY_AXIS_LEFT_X, 1.0],
	"move_forward": [JOY_AXIS_LEFT_Y, -1.0], "move_back": [JOY_AXIS_LEFT_Y, 1.0],
	"cam_left": [JOY_AXIS_RIGHT_X, -1.0], "cam_right": [JOY_AXIS_RIGHT_X, 1.0],
	"cam_up": [JOY_AXIS_RIGHT_Y, -1.0], "cam_down": [JOY_AXIS_RIGHT_Y, 1.0],
	"dive": [JOY_AXIS_TRIGGER_RIGHT, 1.0],
	"crouch": [JOY_AXIS_TRIGGER_LEFT, 1.0],
}

func _ready() -> void:
	setup_input()
	load_settings()
	var args := OS.get_cmdline_args() + OS.get_cmdline_user_args()
	if OS.has_environment("CAPT_HANDHELD") or "--handheld" in args or _looks_like_handheld():
		handheld = true
		quality = "low"
	if "--quality=low" in args:
		quality = "low"
	apply()

## Linux arm64 device with a tiny screen => R36S/R36H class handheld.
func _looks_like_handheld() -> bool:
	if DisplayServer.get_name() == "headless" or OS.get_name() != "Linux":
		return false
	if Engine.get_architecture_name() != "arm64":
		return false
	var sz := DisplayServer.screen_get_size()
	return sz.x <= 800 and sz.y <= 600

func setup_input() -> void:
	for a in ACTIONS:
		if not InputMap.has_action(a):
			InputMap.add_action(a, 0.25)
		InputMap.action_erase_events(a)
		var def = ACTIONS[a]
		for k in def[0]:
			var e := InputEventKey.new()
			e.physical_keycode = k
			InputMap.action_add_event(a, e)
		for m in def[1]:
			var e := InputEventMouseButton.new()
			e.button_index = m
			InputMap.action_add_event(a, e)
		for j in def[2]:
			var e := InputEventJoypadButton.new()
			e.button_index = j
			InputMap.action_add_event(a, e)
	for a in AXES:
		if not InputMap.has_action(a):
			InputMap.add_action(a, 0.25)
		var e := InputEventJoypadMotion.new()
		e.axis = AXES[a][0]
		e.axis_value = AXES[a][1]
		InputMap.action_add_event(a, e)

func rebind_key(action: String, keycode: int) -> void:
	key_overrides[action] = keycode
	_apply_overrides()
	save_settings()

func _apply_overrides() -> void:
	for a in key_overrides:
		if not InputMap.has_action(a):
			continue
		for ev in InputMap.action_get_events(a):
			if ev is InputEventKey:
				InputMap.action_erase_event(a, ev)
		var e := InputEventKey.new()
		e.physical_keycode = int(key_overrides[a])
		InputMap.action_add_event(a, e)

func reset_bindings() -> void:
	key_overrides = {}
	setup_input()
	save_settings()

func key_name(action: String) -> String:
	var out: Array = []
	for ev in InputMap.action_get_events(action):
		if ev is InputEventKey:
			out.append(OS.get_keycode_string(ev.physical_keycode))
		elif ev is InputEventMouseButton:
			out.append("Mouse%d" % ev.button_index)
		elif ev is InputEventJoypadButton:
			out.append("Pad%d" % ev.button_index)
	return " / ".join(out)

func to_dict() -> Dictionary:
	return {"master": master, "music": music, "sfx": sfx, "invert_y": invert_y, "invert_x": invert_x,
		"sensitivity": sensitivity, "quality": quality, "fullscreen": fullscreen,
		"text_speed": text_speed, "auto_skip": auto_skip, "shake": shake, "keys": key_overrides}

func from_dict(d: Dictionary) -> void:
	master = clampf(float(d.get("master", master)), 0.0, 1.0)
	music = clampf(float(d.get("music", music)), 0.0, 1.0)
	sfx = clampf(float(d.get("sfx", sfx)), 0.0, 1.0)
	invert_y = bool(d.get("invert_y", invert_y))
	invert_x = bool(d.get("invert_x", invert_x))
	sensitivity = clampf(float(d.get("sensitivity", sensitivity)), 0.2, 3.0)
	quality = str(d.get("quality", quality))
	if not quality in ["high", "medium", "low"]:
		quality = "high"
	fullscreen = bool(d.get("fullscreen", fullscreen))
	text_speed = clampf(float(d.get("text_speed", text_speed)), 0.25, 4.0)
	auto_skip = bool(d.get("auto_skip", auto_skip))
	shake = bool(d.get("shake", shake))
	key_overrides = d.get("keys", {})

func save_settings() -> void:
	var f := FileAccess.open(PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(to_dict()))
	changed.emit()

func load_settings() -> void:
	if FileAccess.file_exists(PATH):
		var f := FileAccess.open(PATH, FileAccess.READ)
		var parsed = JSON.parse_string(f.get_as_text())
		if parsed is Dictionary:
			from_dict(parsed)
	_apply_overrides()

func apply() -> void:
	if DisplayServer.get_name() != "headless":
		var mode := DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED
		DisplayServer.window_set_mode(mode)
	var vp := get_viewport()
	if vp:
		vp.msaa_3d = Viewport.MSAA_2X if quality == "high" else Viewport.MSAA_DISABLED
	Engine.max_fps = 30 if handheld else (60 if quality == "low" else 0)
	if handheld and get_window():
		var w := get_window()
		w.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
		w.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_EXPAND
		w.content_scale_size = Vector2i(640, 480)
	if has_node("/root/Audio"):
		get_node("/root/Audio").apply_volumes()
	changed.emit()

func shadows_on() -> bool:
	return quality == "high"

func particle_scale() -> float:
	return {"high": 1.0, "medium": 0.5, "low": 0.2}[quality]

func view_distance() -> float:
	return {"high": 400.0, "medium": 220.0, "low": 110.0}[quality]
