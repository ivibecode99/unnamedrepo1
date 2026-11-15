class_name Hazard
extends Node3D
## Lava / quicksand volume. kind: "lava" (damage + launch), "quicksand" (slows), "spikes".
var kind := "lava"
var size := Vector3(10, 1, 10)
var player: Player
var cooldown := 0.0

func _ready() -> void:
	var col := Color(1.0, 0.35, 0.1) if kind == "lava" else Color(0.85, 0.7, 0.4)
	var m := Build.box(size, col, Vector3.ZERO, 0.9 if kind == "lava" else 0.0)
	add_child(m)
	if kind == "quicksand":
		add_to_group("quicksand")
	else:
		add_to_group("hazard")

func contains(p: Vector3) -> bool:
	var l := p - global_position
	return absf(l.x) < size.x * 0.5 and absf(l.z) < size.z * 0.5 and l.y < size.y * 0.5 + 0.4 and l.y > -size.y * 0.5 - 2.0

func _physics_process(delta: float) -> void:
	if kind == "quicksand":
		return
	cooldown = maxf(cooldown - delta, 0.0)
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if ps.is_empty():
			return
		player = ps[0]
	var tgt: Node3D = player
	var immune := false
	if player.state == Player.S.CAPTURED and player.captured_by:
		tgt = player.captured_by
		immune = tgt.has_method("immune_to_lava") and tgt.immune_to_lava() and kind == "lava"
	if contains(tgt.global_position) and cooldown <= 0.0 and not immune:
		cooldown = 0.8
		if player.state == Player.S.CAPTURED:
			player.captured_by.release()
		player.hurt(tgt.global_position - Vector3(0, 1, 0), 1)
		player.velocity.y = 15.0
		Fx.burst(get_parent(), tgt.global_position, Color(1, 0.5, 0.1), 14)
