class_name MovingPlatform
extends AnimatableBody3D
## Platform that oscillates between two points; Pip rides it via CharacterBody platform velocity.
var from_pos := Vector3.ZERO
var to_pos := Vector3(6, 0, 0)
var period := 4.0
var size := Vector3(3.5, 0.5, 3.5)
var color := Color(0.9, 0.6, 0.3)
var phase := 0.0
var t := 0.0

func _ready() -> void:
	sync_to_physics = true
	var cs := CollisionShape3D.new()
	var sh := BoxShape3D.new()
	sh.size = size
	cs.shape = sh
	add_child(cs)
	add_child(Build.box(size, color))
	position = from_pos
	t = phase

func _physics_process(delta: float) -> void:
	t += delta
	var u := (sin(t / period * TAU) + 1.0) * 0.5
	position = from_pos.lerp(to_pos, u)
