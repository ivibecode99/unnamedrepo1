extends Node
## Headless test runner:  godot --headless --path game res://tests/runner.tscn [-- --only=name]
## Exits non-zero when any check fails.
const SUITES := [
	"res://tests/test_data.gd", "res://tests/test_input.gd", "res://tests/test_save.gd", "res://tests/test_movement.gd",
	"res://tests/test_capture.gd", "res://tests/test_boss.gd", "res://tests/test_world.gd", "res://tests/test_ui.gd", "res://tests/test_flow.gd", "res://tests/test_audio.gd",
]
var checks := 0
var failures := 0
var current := ""

var root: Window

func _ready() -> void:
	root = get_tree().root
	call_deferred("_run")

func get_nodes_in_group(g: String) -> Array:
	return get_tree().get_nodes_in_group(g)

func check(cond: bool, msg: String) -> void:
	checks += 1
	if not cond:
		failures += 1
		print("  FAIL [%s] %s" % [current, msg])

func frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame

func _run() -> void:
	var g = root.get_node("Game")
	g.save_enabled = false
	var only := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--only="):
			only = a.substr(7)
	for path in SUITES:
		if only != "" and not path.contains(only):
			continue
		current = path.get_file().get_basename()
		print("== %s" % current)
		var scr = load(path)
		if scr == null or not scr.can_instantiate():
			check(false, "suite failed to load: " + path)
			continue
		var suite = scr.new()
		await suite.run(self)
	print("\n%d checks, %d failures" % [checks, failures])
	get_tree().quit(1 if failures > 0 else 0)

# ---- helpers for suites
func flat_world(extra_wall := false) -> Node3D:
	var w := Node3D.new()
	root.add_child(w)
	var floor_body := StaticBody3D.new()
	var cs := CollisionShape3D.new()
	var sh := BoxShape3D.new()
	sh.size = Vector3(400, 2, 400)
	cs.shape = sh
	floor_body.add_child(cs)
	floor_body.position = Vector3(0, -1, 0)
	w.add_child(floor_body)
	return w

func make_player(w: Node3D, pos := Vector3(0, 0.1, 0)) -> Player:
	var p := Player.new()
	w.add_child(p)
	p.position = pos
	return p

func inp(o := {}) -> Dictionary:
	var d := {"move": Vector2.ZERO, "jump_p": false, "jump_h": false, "throw_p": false, "spin_p": false,
		"crouch_p": false, "crouch_h": false, "roll_p": false, "dive_p": false}
	for k in o:
		d[k] = o[k]
	return d
