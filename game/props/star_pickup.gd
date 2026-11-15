class_name StarPickup
extends Node3D
## A collectible Star. Persisted via Game.collect_star(id).
var star_id := ""
var collected_already := false
var vis: Node3D
var t := 0.0
var player: Player
var sparkle_t := 0.0
var announce := true

func _ready() -> void:
	add_to_group("star_pickup")
	collected_already = Game.has_star(star_id)
	vis = Build.star(0.7, Color(1.0, 0.85, 0.2) if not collected_already else Color(0.6, 0.7, 0.8), 0.8)
	add_child(vis)
	if collected_already:
		vis.material_override = Build.mat(Color(0.7, 0.8, 0.95), 0.2, 0.45)
	var halo := Build.torus(0.75, 0.82, Color(1, 1, 0.6), Vector3.ZERO, 1.0)
	halo.rotation_degrees.x = 90
	halo.scale = Vector3(1, 1, 0.4)
	vis.add_child(halo)

func _physics_process(delta: float) -> void:
	t += delta
	vis.rotation.y += delta * 2.2
	vis.position.y = sin(t * 2.5) * 0.15
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if ps.is_empty():
			return
		player = ps[0]
	var d := player.global_position + Vector3(0, 0.8, 0) - global_position
	if d.length() < 1.5 and player.state != Player.S.DEAD:
		collect()
		return
	# proximity ping for hidden stars
	if not collected_already and d.length() < 14.0:
		sparkle_t -= delta
		if sparkle_t <= 0.0:
			sparkle_t = clampf(d.length() / 14.0 * 2.0, 0.4, 2.0)
			Fx.burst(get_parent(), global_position, Color(1, 1, 0.5), 3, 1.5, 0.8)
			if d.length() < 8.0:
				Audio.sfx("ping", 1.0, -14.0 + (8.0 - d.length()))

func collect() -> void:
	if not is_inside_tree() or is_queued_for_deletion():
		return
	if not collected_already:
		Game.collect_star(star_id)
		Audio.sfx("star")
		Game.toast.emit("STAR: " + Kingdoms.star_title(star_id))
		Fx.burst(get_parent(), global_position, Color(1, 0.9, 0.3), 30, 8.0, 1.0)
		Fx.ring(get_parent(), global_position, Color(1, 0.95, 0.4), 6.0)
		if get_tree().root.has_node("Main"):
			pass
	else:
		Audio.sfx("coin")
	queue_free()
