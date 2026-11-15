class_name Capt
extends Node3D
## The thrown hat. Hits enemies, grabs coins, bounces Pip, and captures creatures.
var owner_player: Player
var direction := Vector3.FORWARD
var phase := 0        # 0 out, 1 hover, 2 return
var travelled := 0.0
var t := 0.0
var hit_set := {}
var vis: Node3D
var hover_t := 0.0

func _ready() -> void:
	add_to_group("hat")
	vis = CaptVisual.build()
	add_child(vis)
	vis.scale = Vector3(0.9, 0.9, 0.9)

func _physics_process(delta: float) -> void:
	if not is_instance_valid(owner_player):
		queue_free()
		return
	t += delta
	var wingspin := 20.0
	vis.rotation.y += delta * wingspin
	for w in ["wingL", "wingR"]:
		if vis.has_node(w):
			vis.get_node(w).rotation.x = sin(t * 30.0) * 0.5
	var step := Vector3.ZERO
	match phase:
		0:
			step = direction * Tuning.HAT_SPEED * delta
			travelled += step.length()
			if travelled >= Tuning.HAT_RANGE:
				phase = 1
		1:
			hover_t += delta
			if hover_t > 0.22:
				phase = 2
		2:
			var target := owner_player.global_position + Vector3(0, 1.3, 0)
			var to := target - global_position
			var d := to.length()
			var sp := Tuning.HAT_SPEED * 1.25
			if d < 1.0:
				owner_player.hat_returned()
				queue_free()
				return
			step = to / d * minf(sp * delta, d)
	# world collision
	if step.length() > 0.0:
		var space := get_world_3d().direct_space_state
		var q := PhysicsRayQueryParameters3D.create(global_position, global_position + step + step.normalized() * 0.3)
		q.collision_mask = 1
		var r := space.intersect_ray(q)
		if r.is_empty():
			global_position += step
		elif phase == 0:
			phase = 1
			global_position = r["position"] + r["normal"] * 0.2
			Audio.sfx("hit", 1.4, -6.0)
	if t > 4.0:
		owner_player.hat_returned()
		queue_free()
		return
	_interact()

func _interact() -> void:
	var p := global_position
	# capture
	if not owner_player.state == Player.S.CAPTURED and phase != 2:
		for c in get_tree().get_nodes_in_group("capturable"):
			if is_instance_valid(c) and c.has_method("can_be_captured") and c.can_be_captured() and (c.global_position + Vector3(0, 0.7, 0)).distance_to(p) < c.get("capture_radius") + 0.7:
				c.capture(owner_player)
				queue_free()
				return
	# enemies
	for e in get_tree().get_nodes_in_group("enemy"):
		if is_instance_valid(e) and not hit_set.has(e) and e.global_position.distance_to(p + Vector3(0, -0.5, 0)) < 1.6:
			hit_set[e] = true
			if e.has_method("hurt"):
				e.hurt(1, owner_player)
			if phase == 0:
				phase = 2
			Audio.sfx("hit")
	for b in get_tree().get_nodes_in_group("boss"):
		if is_instance_valid(b) and not hit_set.has(b) and b.global_position.distance_to(p) < 1.4 + b.get("radius"):
			hit_set[b] = true
			if b.has_method("hit_by_hat"):
				b.hit_by_hat(owner_player)
			phase = 2
	for c in get_tree().get_nodes_in_group("coin"):
		if is_instance_valid(c) and c.global_position.distance_to(p) < 1.8:
			c.collect()
	for s in get_tree().get_nodes_in_group("hat_target"):
		if is_instance_valid(s) and s.global_position.distance_to(p) < 1.6 and s.has_method("on_hat_hit"):
			s.on_hat_hit(owner_player)
	for s in get_tree().get_nodes_in_group("breakable"):
		if is_instance_valid(s) and s.global_position.distance_to(p) < 1.6 and s.has_method("on_hat_hit"):
			s.on_hat_hit(owner_player)
	# hat bounce
	var pl := owner_player
	if pl.velocity.y < 0.0 and pl.state != Player.S.CAPTURED:
		var d := pl.global_position - (p - Vector3(0, 0.1, 0))
		if absf(d.x) < 1.0 and absf(d.z) < 1.0 and d.y > -0.2 and d.y < 1.2:
			pl.bounce()
			Audio.sfx("spring", 1.3)
