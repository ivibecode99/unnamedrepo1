class_name CameraRig
extends Node3D
## Third-person orbit camera with collision, mouse/stick look, invert options, shake, cutscene poses.
var target: Node3D
var yaw := 0.0
var pitch := -0.35
var dist := 7.5
var cam: Camera3D
var shake_t := 0.0
var shake_amt := 0.0
var cut_pos = null
var cut_look = null
var _smooth_pos := Vector3.ZERO
var look_offset := Vector3(0, 1.4, 0)
var enabled := true
var scripted_look := Vector2.ZERO   # tests

func _ready() -> void:
	cam = Camera3D.new()
	cam.current = true
	cam.fov = 70.0
	cam.far = Settings.view_distance()
	cam.near = 0.1
	add_child(cam)
	top_level = true
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(ev: InputEvent) -> void:
	if not enabled:
		return
	if ev is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		var s := 0.0035 * Settings.sensitivity
		yaw -= ev.relative.x * s * (-1.0 if Settings.invert_x else 1.0)
		pitch -= ev.relative.y * s * (-1.0 if Settings.invert_y else 1.0)
		pitch = clampf(pitch, -1.35, 0.6)

func shake(a: float) -> void:
	if Settings.shake:
		shake_amt = maxf(shake_amt, a)
		shake_t = 0.3

func cutscene_pose(pos: Vector3, look: Vector3) -> void:
	cut_pos = pos
	cut_look = look

func release_cutscene() -> void:
	cut_pos = null
	cut_look = null

func _process(delta: float) -> void:
	if cut_pos != null:
		global_position = global_position.lerp(cut_pos, minf(1.0, 3.0 * delta))
		var tgt: Vector3 = cut_look
		var xf := global_transform.looking_at(tgt, Vector3.UP)
		global_transform.basis = global_transform.basis.slerp(xf.basis, minf(1.0, 4.0 * delta))
		return
	if target == null or not is_instance_valid(target):
		return
	if enabled:
		var look := Input.get_vector("cam_left", "cam_right", "cam_up", "cam_down") + scripted_look
		var inv_x := -1.0 if Settings.invert_x else 1.0
		var inv_y := -1.0 if Settings.invert_y else 1.0
		yaw -= look.x * 2.6 * delta * Settings.sensitivity * inv_x
		pitch -= look.y * 1.8 * delta * Settings.sensitivity * inv_y
		pitch = clampf(pitch, -1.35, 0.6)
		if Input.is_action_just_pressed("skip") and not get_tree().paused:
			# recenter behind the player
			if target is Player:
				yaw = atan2(target.dir_face.x, target.dir_face.z) + PI
	var focus := target.global_position + look_offset
	_smooth_pos = _smooth_pos.lerp(focus, minf(1.0, 12.0 * delta))
	var basis := Basis.from_euler(Vector3(pitch, yaw, 0))
	var back := basis * Vector3(0, 0, 1)
	var want := _smooth_pos + back * dist
	# collision pull-in
	var space := get_world_3d().direct_space_state
	var q := PhysicsRayQueryParameters3D.create(_smooth_pos, want)
	q.collision_mask = 1
	var r := space.intersect_ray(q)
	if not r.is_empty():
		want = r["position"] + (_smooth_pos - want).normalized() * 0.3
	global_position = want
	global_transform.basis = basis
	if shake_t > 0.0:
		shake_t -= delta
		cam.h_offset = randf_range(-1, 1) * shake_amt * 0.3
		cam.v_offset = randf_range(-1, 1) * shake_amt * 0.3
		if shake_t <= 0.0:
			shake_amt = 0.0
			cam.h_offset = 0.0
			cam.v_offset = 0.0

func snap_to_target() -> void:
	if target:
		_smooth_pos = target.global_position + look_offset
