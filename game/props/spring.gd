class_name Spring
extends Node3D
## Bounce pad. Also used for geysers.
var power := 26.0
var player: Player
var squash := 0.0

func _ready() -> void:
	add_child(Build.cyl(0.9, 1.1, 0.35, Color(0.9, 0.25, 0.3), Vector3(0, 0.18, 0)))
	add_child(Build.cyl(0.6, 0.6, 0.15, Color(1.0, 0.9, 0.3), Vector3(0, 0.4, 0)))

func _physics_process(delta: float) -> void:
	scale.y = lerpf(scale.y, 1.0, 10.0 * delta)
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if ps.is_empty():
			return
		player = ps[0]
	var tgt: Node3D = player
	if player.state == Player.S.CAPTURED and player.captured_by:
		tgt = player.captured_by
	var d := tgt.global_position - global_position
	if absf(d.x) < 1.1 and absf(d.z) < 1.1 and d.y > -0.2 and d.y < 0.9 and tgt.velocity.y <= 1.0:
		tgt.velocity.y = power
		if tgt == player:
			player.set_state(Player.S.AIR)
		scale.y = 0.5
		Audio.sfx("spring")
