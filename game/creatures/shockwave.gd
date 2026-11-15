class_name Shockwave
extends Node3D
## Expanding ring on the ground; Pip must jump over it.
var max_radius := 8.0
var speed := 9.0
var r := 0.5
var color := Color(1, 0.6, 0.2)
var player: Player
var ring: MeshInstance3D
var hit := false

func _ready() -> void:
	ring = Build.torus(0.85, 1.0, color, Vector3(0, 0.15, 0), 0.9)
	ring.scale = Vector3(r, 1.0, r)
	add_child(ring)

func _physics_process(delta: float) -> void:
	r += speed * delta
	ring.scale = Vector3(r, 1.0, r)
	if r > max_radius:
		queue_free()
		return
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if ps.is_empty():
			return
		player = ps[0]
	var tgt: Node3D = player
	if player.state == Player.S.CAPTURED and player.captured_by:
		tgt = player.captured_by
	var d := tgt.global_position - global_position
	var flat := Vector2(d.x, d.z).length()
	if not hit and absf(flat - r) < 0.7 and d.y < 0.7 and d.y > -1.5:
		hit = true
		if player.state == Player.S.CAPTURED and player.captured_by:
			player.captured_by.release()
		player.hurt(global_position, 1)
