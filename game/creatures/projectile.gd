class_name Projectile
extends Node3D
## Generic projectile / hazard. friendly=true hits enemies & breakables, false hits Pip.
var vel := Vector3.ZERO
var grav := 0.0
var radius := 0.5
var life := 4.0
var color := Color(1, 0.4, 0.2)
var friendly := false
var damage := 1
var explode_on_ground := false
var shock_radius := 0.0
var player: Player
var t := 0.0
var pierce := false

func _ready() -> void:
	add_child(Build.sphere(radius, color, Vector3.ZERO, 0.8))

func _physics_process(delta: float) -> void:
	t += delta
	vel.y -= grav * delta
	var from := global_position
	var to := from + vel * delta
	var space := get_world_3d().direct_space_state
	var q := PhysicsRayQueryParameters3D.create(from, to)
	q.collision_mask = 1
	var r := space.intersect_ray(q)
	if not r.is_empty():
		global_position = r["position"]
		_land()
		return
	global_position = to
	life -= delta
	if life <= 0.0:
		queue_free()
		return
	if friendly:
		for g in ["enemy", "breakable"]:
			for e in get_tree().get_nodes_in_group(g):
				if is_instance_valid(e) and e.global_position.distance_to(global_position) < radius + 0.9:
					if e.has_method("hurt"):
						e.hurt(1, null)
					elif e.has_method("on_hat_hit"):
						e.on_hat_hit(null)
					if not pierce:
						queue_free()
						return
		for b in get_tree().get_nodes_in_group("boss"):
			if is_instance_valid(b) and b.global_position.distance_to(global_position) < radius + b.get("radius"):
				b.hit_by_hat(null)
				queue_free()
				return
	else:
		if player == null or not is_instance_valid(player):
			var ps := get_tree().get_nodes_in_group("player")
			if ps.is_empty():
				return
			player = ps[0]
		var pp := player.global_position + Vector3(0, 0.8, 0)
		if player.state == Player.S.CAPTURED and player.captured_by:
			pp = player.captured_by.global_position + Vector3(0, 0.6, 0)
		if pp.distance_to(global_position) < radius + 0.6:
			if player.state == Player.S.CAPTURED and player.captured_by:
				player.captured_by.release()
			player.hurt(global_position, damage)
			queue_free()

func _land() -> void:
	if explode_on_ground:
		Fx.burst(get_parent(), global_position, color, 14)
		Audio.sfx("explosion", 1.2, -6.0)
		if shock_radius > 0.0:
			var s := Shockwave.new()
			s.max_radius = shock_radius
			s.color = color
			get_parent().add_child(s)
			s.global_position = global_position
	queue_free()
