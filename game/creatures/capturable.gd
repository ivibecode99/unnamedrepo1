class_name Capturable
extends CharacterBody3D
## A creature/object Pip can possess by throwing Capt at it. Each kind has its own movement/ability.
## Controls while captured: stick = move, A = jump, Y(spin) = ability, X(throw) = release.
var kind := "hopper"
var info: Dictionary
var controlled := false
var player: Player
var capture_radius := 1.0
var t := 0.0
var state_t := 0.0
var cooldown := 0.0          # re-capture cooldown after release
var vis: Node3D
var hat_vis: Node3D
var ability_t := 0.0
var ability_cd := 0.0
var burrowed := false
var sliding := false
var rolling := false
var hop_n := 0
var glide := false
var wander_dir := Vector3.ZERO
var wander_t := 0.0
var aim_yaw := 0.0
var aim_pitch := 0.9
var home := Vector3.ZERO
var face := Vector3.FORWARD
var launched_flag := false

func _ready() -> void:
	info = CreatureData.DATA[kind]
	collision_layer = 4
	collision_mask = 1
	add_to_group("capturable")
	home = global_position
	var cs := CollisionShape3D.new()
	var sh := CapsuleShape3D.new()
	sh.radius = 0.6
	sh.height = 1.4
	cs.shape = sh
	cs.position.y = 0.7
	add_child(cs)
	vis = Node3D.new()
	add_child(vis)
	_build_visual()
	capture_radius = 1.1
	if kind == "cannon":
		capture_radius = 1.6
	# a little "capture me" shimmer
	add_child(Build.label3d(info["name"], Vector3(0, 2.1, 0), 0.32, Color(1, 0.9, 0.6)))

func _build_visual() -> void:
	var c: Color = info["color"]
	var darker := c.darkened(0.35)
	var white := Color.WHITE
	match kind:
		"hopper":
			vis.add_child(Build.sphere(0.6, c, Vector3(0, 0.6, 0)))
			for sx in [-1, 1]:
				vis.add_child(Build.sphere(0.22, white, Vector3(sx * 0.3, 1.1, 0.25)))
				vis.add_child(Build.sphere(0.1, Color.BLACK, Vector3(sx * 0.3, 1.12, 0.42)))
				vis.add_child(Build.sphere(0.25, darker, Vector3(sx * 0.45, 0.2, -0.1)))
		"buzzer":
			vis.add_child(Build.sphere(0.5, c, Vector3(0, 0.7, 0)))
			vis.add_child(Build.box(Vector3(0.9, 0.14, 0.2), Color(0.15, 0.1, 0.05), Vector3(0, 0.7, 0)))
			for sx in [-1, 1]:
				var w := Build.sphere(0.35, Color(1, 1, 1, 1), Vector3(sx * 0.5, 1.1, -0.1))
				w.scale = Vector3(1, 0.2, 1)
				w.name = "wing%d" % sx
				vis.add_child(w)
			Build.eyes(vis, 0.4, 0.8, 0.16, 0.1)
		"stumpling":
			vis.add_child(Build.cyl(0.55, 0.65, 1.0, c, Vector3(0, 0.5, 0)))
			vis.add_child(Build.cyl(0.5, 0.5, 0.08, c.lightened(0.3), Vector3(0, 1.02, 0)))
			Build.eyes(vis, 0.5, 0.65, 0.2, 0.12)
			vis.add_child(Build.sphere(0.25, Color(0.3, 0.7, 0.3), Vector3(0, 1.2, 0)))
		"scarab":
			var b := Build.sphere(0.65, c, Vector3(0, 0.55, 0))
			b.scale = Vector3(1, 0.7, 1.3)
			vis.add_child(b)
			vis.add_child(Build.sphere(0.3, darker, Vector3(0, 0.55, 0.8)))
			vis.add_child(Build.prism(Vector3(0.3, 0.5, 0.2), Color(1, 0.9, 0.4), Vector3(0, 0.55, 1.15)))
		"cactoid":
			vis.add_child(Build.capsule(0.45, 1.4, c, Vector3(0, 0.75, 0)))
			vis.add_child(Build.capsule(0.2, 0.7, c, Vector3(0.55, 0.9, 0)))
			vis.add_child(Build.capsule(0.2, 0.7, c, Vector3(-0.55, 0.9, 0)))
			vis.add_child(Build.sphere(0.15, Color(1, 0.4, 0.7), Vector3(0, 1.55, 0)))
			Build.eyes(vis, 0.4, 1.0, 0.16, 0.1)
		"sandworm":
			for i in 4:
				vis.add_child(Build.sphere(0.5 - i * 0.07, c if i % 2 == 0 else darker, Vector3(0, 0.5 + i * 0.35, -i * 0.15)))
			Build.eyes(vis, 0.4, 1.7, 0.2, 0.1)
		"zipbot":
			vis.add_child(Build.box(Vector3(1.1, 0.5, 1.8), c, Vector3(0, 0.55, 0)))
			vis.add_child(Build.box(Vector3(0.9, 0.4, 0.9), c.lightened(0.2), Vector3(0, 0.95, -0.1)))
			for sx in [-1, 1]:
				for sz in [-1, 1]:
					vis.add_child(Build.cyl(0.25, 0.25, 0.2, Color(0.15, 0.15, 0.15), Vector3(sx * 0.6, 0.25, sz * 0.6)))
					vis.get_child(vis.get_child_count() - 1).rotation_degrees.z = 90
			Build.eyes(vis, 0.9, 0.7, 0.3, 0.12)
		"pigeon":
			vis.add_child(Build.sphere(0.55, c, Vector3(0, 0.6, 0)))
			vis.add_child(Build.sphere(0.3, c.lightened(0.15), Vector3(0, 1.1, 0.35)))
			vis.add_child(Build.prism(Vector3(0.2, 0.2, 0.3), Color(1, 0.7, 0.2), Vector3(0, 1.08, 0.7)))
			for sx in [-1, 1]:
				var w := Build.sphere(0.4, c.darkened(0.2), Vector3(sx * 0.55, 0.7, -0.1))
				w.scale = Vector3(0.4, 0.15, 1.0)
				w.name = "wing%d" % sx
				vis.add_child(w)
		"springbot":
			vis.add_child(Build.cyl(0.2, 0.2, 0.7, Color(0.7, 0.7, 0.75), Vector3(0, 0.35, 0)))
			for i in 3:
				vis.add_child(Build.torus(0.22, 0.3, Color(0.85, 0.85, 0.9), Vector3(0, 0.15 + i * 0.22, 0)))
			vis.add_child(Build.sphere(0.55, c, Vector3(0, 1.1, 0)))
			Build.eyes(vis, 0.45, 1.2, 0.2, 0.13)
		"jelly":
			var b := Build.sphere(0.65, c, Vector3(0, 1.0, 0))
			b.scale = Vector3(1, 0.8, 1)
			vis.add_child(b)
			for i in 5:
				var a := i / 5.0 * TAU
				vis.add_child(Build.capsule(0.07, 0.8, c.lightened(0.2), Vector3(cos(a) * 0.4, 0.3, sin(a) * 0.4)))
			Build.eyes(vis, 0.5, 1.05, 0.2, 0.1)
		"crab":
			var b := Build.sphere(0.6, c, Vector3(0, 0.5, 0))
			b.scale = Vector3(1.3, 0.7, 1.0)
			vis.add_child(b)
			for sx in [-1, 1]:
				vis.add_child(Build.sphere(0.3, c.lightened(0.1), Vector3(sx * 0.9, 0.7, 0.4)))
				vis.add_child(Build.prism(Vector3(0.3, 0.4, 0.15), Color(1, 0.9, 0.9), Vector3(sx * 0.9, 1.0, 0.5)))
			Build.eyes(vis, 0.5, 0.95, 0.2, 0.1)
		"angler":
			var b := Build.sphere(0.65, c, Vector3(0, 0.65, 0))
			b.scale = Vector3(0.9, 0.9, 1.3)
			vis.add_child(b)
			vis.add_child(Build.cyl(0.03, 0.03, 0.8, darker, Vector3(0, 1.3, 0.5)))
			vis.add_child(Build.sphere(0.15, Color(1, 1, 0.5), Vector3(0, 1.75, 0.7), 1.2))
			Build.eyes(vis, 0.75, 0.8, 0.2, 0.12)
		"penguin":
			vis.add_child(Build.sphere(0.65, c, Vector3(0, 0.7, 0)))
			var bel := Build.sphere(0.5, white, Vector3(0, 0.65, 0.3))
			bel.scale = Vector3(0.9, 1.0, 0.7)
			vis.add_child(bel)
			vis.add_child(Build.prism(Vector3(0.25, 0.2, 0.3), Color(1, 0.7, 0.1), Vector3(0, 0.95, 0.65)))
			Build.eyes(vis, 0.5, 1.05, 0.2, 0.1)
		"yeti":
			vis.add_child(Build.sphere(0.8, c, Vector3(0, 0.85, 0)))
			vis.add_child(Build.sphere(0.45, c.darkened(0.05), Vector3(0, 1.7, 0)))
			for sx in [-1, 1]:
				vis.add_child(Build.sphere(0.3, c, Vector3(sx * 0.95, 0.8, 0.1)))
			Build.eyes(vis, 0.35, 1.75, 0.18, 0.1)
		"snowball":
			vis.add_child(Build.sphere(0.8, c, Vector3(0, 0.8, 0)))
			Build.eyes(vis, 0.65, 1.0, 0.25, 0.14)
			vis.add_child(Build.sphere(0.1, Color(0.2, 0.2, 0.2), Vector3(0.3, 0.5, 0.7)))
		"fireflea":
			vis.add_child(Build.sphere(0.5, c, Vector3(0, 0.55, 0), 0.8))
			vis.add_child(Build.prism(Vector3(0.5, 0.8, 0.3), Color(1, 0.85, 0.2), Vector3(0, 1.2, 0), ))
			for sx in [-1, 1]:
				vis.add_child(Build.sphere(0.18, darker, Vector3(sx * 0.35, 0.15, 0)))
			Build.eyes(vis, 0.4, 0.7, 0.17, 0.1)
		"lavagolem":
			vis.add_child(Build.box(Vector3(1.4, 1.2, 1.0), c, Vector3(0, 0.9, 0)))
			vis.add_child(Build.box(Vector3(0.9, 0.7, 0.8), c.lightened(0.15), Vector3(0, 1.9, 0)))
			vis.add_child(Build.box(Vector3(1.0, 0.2, 0.1), Color(1, 0.5, 0.1), Vector3(0, 1.0, 0.52), 1.0))
			for sx in [-1, 1]:
				vis.add_child(Build.box(Vector3(0.45, 0.9, 0.5), darker, Vector3(sx * 0.4, 0.3, 0)))
				vis.add_child(Build.box(Vector3(0.45, 1.0, 0.45), c, Vector3(sx * 1.0, 1.0, 0)))
			Build.eyes(vis, 0.4, 1.95, 0.2, 0.1)
		"cannon":
			vis.add_child(Build.cyl(0.9, 1.1, 0.5, Color(0.25, 0.25, 0.3), Vector3(0, 0.25, 0)))
			var barrel := Node3D.new()
			barrel.name = "Barrel"
			barrel.position = Vector3(0, 0.9, 0)
			vis.add_child(barrel)
			var bm := Build.cyl(0.6, 0.75, 1.8, c, Vector3(0, 0.0, 0))
			bm.rotation_degrees.x = 90
			bm.position = Vector3(0, 0, 0.5)
			barrel.add_child(bm)
			barrel.add_child(Build.torus(0.55, 0.7, Color(1.0, 0.6, 0.2), Vector3(0, 0, 1.4)))
			barrel.get_child(barrel.get_child_count() - 1).rotation_degrees.x = 90
		_:
			vis.add_child(Build.sphere(0.6, c, Vector3(0, 0.6, 0)))
	# the little capture "tell": a tiny ring above idle creatures
	var ring := Build.torus(0.18, 0.24, Color(1, 0.9, 0.4), Vector3(0, 2.4 if kind in ["yeti", "lavagolem"] else 2.0, 0), 1.0)
	ring.name = "Tell"
	vis.add_child(ring)

func can_be_captured() -> bool:
	return not controlled and cooldown <= 0.0

func immune_to_lava() -> bool:
	return controlled and info["ability"] in ["lavawalk"] or (controlled and info["ability"] == "dash" and kind == "fireflea" and ability_t > 0.0)

func smashes() -> bool:
	return controlled and (info["ability"] in ["stomp", "smash", "pinch", "roll"] and (ability_t > 0.0 or rolling))

func capture(p: Player) -> void:
	player = p
	p.capture(self)
	controlled = true
	state_t = 0.0
	ability_t = 0.0
	vis.get_node("Tell").visible = false
	var cam := get_tree().get_first_node_in_group("camera_rig")
	if cam:
		cam.target = self
	hat_vis = CaptVisual.build()
	hat_vis.scale = Vector3(0.9, 0.9, 0.9)
	hat_vis.position = Vector3(0, 2.0 if kind not in ["yeti", "lavagolem"] else 2.6, 0)
	add_child(hat_vis)
	Game.toast.emit("Captured %s! A: jump  Y: ability  X: release" % info["name"])
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.set_capture(info)
	Fx.burst(get_parent(), global_position + Vector3(0, 1, 0), Color(1, 0.8, 0.9), 16)

func release() -> void:
	if not controlled:
		return
	controlled = false
	cooldown = 1.5
	vis.get_node("Tell").visible = true
	if hat_vis:
		hat_vis.queue_free()
		hat_vis = null
	if kind == "cannon":
		pass
	burrowed = false
	sliding = false
	rolling = false
	vis.position.y = 0.0
	if is_instance_valid(player):
		player.release_capture(global_position + Vector3(0, 1.2, 0))
		var cam := get_tree().get_first_node_in_group("camera_rig")
		if cam:
			cam.target = player
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.set_capture({})

func _physics_process(delta: float) -> void:
	t += delta
	state_t += delta
	cooldown = maxf(cooldown - delta, 0.0)
	ability_cd = maxf(ability_cd - delta, 0.0)
	ability_t = maxf(ability_t - delta, 0.0)
	if controlled and is_instance_valid(player):
		_control(delta)
	else:
		_idle(delta)
	_animate(delta)

func _in_water() -> bool:
	for w in get_tree().get_nodes_in_group("water"):
		if w.contains(global_position):
			return true
	return false

func _idle(delta: float) -> void:
	if kind == "cannon":
		return
	velocity.y -= 32.0 * delta
	wander_t -= delta
	if wander_t <= 0.0:
		wander_t = randf_range(1.5, 4.0)
		wander_dir = Vector3(randf() - 0.5, 0, randf() - 0.5).normalized() * (0.0 if randf() < 0.4 else 1.0)
		if global_position.distance_to(home) > 6.0:
			wander_dir = (home - global_position).normalized()
	var sp: float = minf(float(info["speed"]), 3.0)
	velocity.x = wander_dir.x * sp
	velocity.z = wander_dir.z * sp
	if wander_dir.length() > 0.1:
		face = wander_dir
	# idle hop for hoppers
	if info["ability"] in ["superjump"] and is_on_floor() and randf() < 0.01:
		velocity.y = 7.0
	move_and_slide()

func _ground_move(delta: float, wish: Vector3, speed: float, accel := 40.0) -> void:
	var h := Vector3(velocity.x, 0, velocity.z)
	h = h.move_toward(wish * speed, accel * delta)
	velocity.x = h.x
	velocity.z = h.z
	if wish.length() > 0.1:
		face = wish.normalized()

func _hit_area(radius: float, dmg := 1) -> void:
	var c := global_position + Vector3(0, 0.8, 0)
	for e in get_tree().get_nodes_in_group("enemy"):
		if is_instance_valid(e) and e.global_position.distance_to(c) < radius + 0.6:
			e.hurt(dmg, player)
	for b in get_tree().get_nodes_in_group("breakable"):
		if is_instance_valid(b) and b.global_position.distance_to(c) < radius + 0.6:
			b.on_hat_hit(player)
	for b in get_tree().get_nodes_in_group("ice_wall"):
		if is_instance_valid(b) and b.global_position.distance_to(c) < radius + 1.4 and b.has_method("shatter"):
			b.shatter()
	for b in get_tree().get_nodes_in_group("boss"):
		if is_instance_valid(b) and b.global_position.distance_to(c) < radius + b.get("radius") and b.has_method("hit_by_hat"):
			b.hit_by_hat(player)

func _control(delta: float) -> void:
	var inp := player._inp()
	var mv: Vector2 = inp["move"]
	var wish := player.move_dir(mv)
	var ab: String = info["ability"]
	var speed: float = info["speed"]
	var in_water := _in_water()
	if inp["throw_p"] and state_t > 0.35:
		release()
		return
	if player.global_position.distance_to(global_position) > 3.0 or true:
		player.global_position = global_position
	if kind == "cannon":
		_control_cannon(delta, mv, inp)
		return
	# --- ability triggers
	var ability_p: bool = inp["spin_p"]
	match ab:
		"dash":
			if ability_p and ability_cd <= 0.0:
				ability_t = 0.55
				ability_cd = 0.8
				var d := wish.normalized() if wish.length() > 0.1 else face
				face = d
				velocity.x = d.x * speed * 2.2
				velocity.z = d.z * speed * 2.2
				Audio.sfx("dive", 1.2)
			if ability_t > 0.0:
				var d := face
				velocity.x = d.x * speed * 2.2
				velocity.z = d.z * speed * 2.2
				velocity.y = maxf(velocity.y, 0.0) if not is_on_floor() else 0.0
				_hit_area(1.4)
				velocity.y -= 12.0 * delta
		"stomp":
			if ability_p and ability_cd <= 0.0 and is_on_floor():
				velocity.y = 12.0
				ability_cd = 0.6
				ability_t = 1.0
			if ability_t > 0.0 and not is_on_floor() and velocity.y < 0.0:
				velocity.y = -30.0
			if ability_t > 0.0 and is_on_floor() and state_t > 0.2 and ability_t < 0.95:
				ability_t = 0.0
				_slam(3.2)
		"smash":
			if ability_p and ability_cd <= 0.0:
				ability_cd = 0.7
				ability_t = 0.3
				_slam(3.4)
		"pinch":
			if ability_p and ability_cd <= 0.0:
				ability_cd = 0.5
				ability_t = 0.25
				Audio.sfx("hit", 1.5)
				_hit_area(2.0)
		"spines":
			if ability_p and ability_cd <= 0.0:
				ability_cd = 0.8
				for i in 8:
					var a := i / 8.0 * TAU
					var pr := Projectile.new()
					pr.friendly = true
					pr.color = Color(0.9, 1.0, 0.5)
					pr.radius = 0.15
					pr.vel = Vector3(cos(a), 0.05, sin(a)) * 14.0
					pr.life = 0.9
					get_parent().add_child(pr)
					pr.global_position = global_position + Vector3(0, 1.0, 0)
				Audio.sfx("shoot")
		"burrow":
			if ability_p and ability_cd <= 0.0:
				burrowed = not burrowed
				ability_cd = 0.4
				Audio.sfx("roll")
				if not burrowed:
					velocity.y = 14.0
			if burrowed:
				speed *= 1.5
				_hit_area(1.0)
		"boost":
			if inp["spin_p"] or Input.is_action_pressed("spin"):
				speed *= 1.8
				ability_t = 0.1
		"slide":
			if ability_p:
				sliding = not sliding
				Audio.sfx("roll")
		"roll":
			if ability_p:
				rolling = not rolling
				Audio.sfx("roll")
			if rolling:
				_hit_area(1.2)
				speed *= 1.6
		"flap":
			pass
	# --- movement
	var accel := 40.0
	if sliding:
		speed *= 2.2
		accel = 6.0
	if ab == "swimfast" and in_water:
		speed *= 1.8
	if in_water and ab != "swimfast" and not info["fly"]:
		speed *= 0.7
	if ability_t > 0.0 and ab in ["dash"]:
		pass
	else:
		_ground_move(delta, wish, speed, accel)
	# --- vertical
	var on_floor := is_on_floor()
	var g := 32.0
	match ab:
		"flap":
			g = 22.0
			if inp["jump_p"]:
				velocity.y = 10.0
				Audio.sfx("jump", 1.5, -6.0)
		"glide":
			if inp["jump_p"] and on_floor:
				velocity.y = info["jump"]
				Audio.sfx("jump")
			elif inp["jump_h"] and velocity.y < 0.0:
				g = 3.0
				velocity.y = maxf(velocity.y, -3.0)
				velocity.x *= 1.0 + 0.4 * delta
				_ground_move(delta, face, speed * 1.5, 20.0)
		"float":
			if inp["jump_h"]:
				velocity.y = move_toward(velocity.y, 6.0, 20.0 * delta)
				g = 0.0
			else:
				g = 8.0
		"swimfast":
			if in_water:
				g = 0.0
				velocity.y = move_toward(velocity.y, 5.0 if inp["jump_h"] else -1.0, 12.0 * delta)
			elif inp["jump_p"] and on_floor:
				velocity.y = info["jump"]
		"superjump":
			if on_floor:
				if inp["jump_p"]:
					hop_n = mini(hop_n + 1, 3)
					velocity.y = info["jump"] * minf(0.6 + 0.2 * hop_n, 1.0)
					Audio.sfx("spring", 0.8 + 0.1 * hop_n)
				elif absf(velocity.x) + absf(velocity.z) > 1.0 and state_t > 0.4 and false:
					pass
			if on_floor and not inp["jump_h"]:
				hop_n = 0
		"burrow":
			if burrowed:
				g = 40.0
		_:
			if inp["jump_p"] and on_floor and not burrowed:
				velocity.y = info["jump"]
				Audio.sfx("jump")
	if not (ab == "float" and inp["jump_h"]):
		velocity.y -= g * delta
	if ab == "stomp" and not on_floor and ability_t > 0.0:
		pass
	if ab == "lavawalk" and inp["jump_p"] and on_floor:
		velocity.y = info["jump"]
	move_and_slide()
	# camera follows; keep player node synced
	player.global_position = global_position
	if kind == "snowball" and rolling:
		vis.rotation.x += delta * 10.0
	_enemy_contact()

func _enemy_contact() -> void:
	var p := player
	if p == null:
		return
	for e in get_tree().get_nodes_in_group("enemy"):
		if not is_instance_valid(e):
			continue
		var d: Vector3 = e.global_position - global_position
		if Vector2(d.x, d.z).length() < 1.0 and absf(d.y) < 1.4:
			if smashes() or (info["ability"] == "dash" and ability_t > 0.0):
				e.hurt(2, p)
			elif velocity.y < -2.0 and d.y < 0.1:
				e.hurt(2, p)
				velocity.y = 10.0
			# otherwise the enemy handles the damage itself

func _slam(radius: float) -> void:
	Audio.sfx("pound")
	Fx.burst(get_parent(), global_position, Color(1, 1, 1), 14)
	var cam := get_tree().get_first_node_in_group("camera_rig")
	if cam:
		cam.shake(0.35)
	for n in get_tree().get_nodes_in_group("pound_target"):
		if is_instance_valid(n) and n.has_method("on_pound") and n.global_position.distance_to(global_position) < radius:
			n.on_pound(player)
	_hit_area(radius)

func _control_cannon(delta: float, mv: Vector2, inp: Dictionary) -> void:
	aim_yaw -= mv.x * 1.8 * delta
	aim_pitch = clampf(aim_pitch - mv.y * 1.2 * delta, 0.2, 1.4)
	vis.rotation.y = aim_yaw
	var barrel: Node3D = vis.get_node("Barrel")
	barrel.rotation.x = -aim_pitch
	if (inp["jump_p"] or inp["spin_p"]) and state_t > 0.5:
		var dir := Vector3(sin(aim_yaw) * cos(aim_pitch), sin(aim_pitch), cos(aim_yaw) * cos(aim_pitch))
		var pl := player
		Audio.sfx("explosion", 1.0, -4.0)
		Fx.burst(get_parent(), global_position + Vector3(0, 1.4, 0) + dir * 1.5, Color(1, 0.7, 0.2), 20, 8.0)
		release()
		pl.global_position = global_position + Vector3(0, 1.8, 0) + dir * 1.8
		pl.velocity = dir * 30.0
		pl.invuln = 0.5
		pl.set_state(Player.S.AIR)

func _animate(delta: float) -> void:
	if vis == null:
		return
	if kind != "cannon":
		vis.rotation.y = lerp_angle(vis.rotation.y, atan2(face.x, face.z), minf(1.0, 14.0 * delta))
	var moving := Vector2(velocity.x, velocity.z).length() > 0.6
	vis.scale = Vector3.ONE
	if kind == "snowball" and rolling:
		vis.scale = Vector3.ONE * 1.25
	if burrowed:
		vis.position.y = lerpf(vis.position.y, -0.9, 10.0 * delta)
	elif moving and is_on_floor() and kind != "cannon":
		vis.position.y = absf(sin(t * 12.0)) * 0.12
	else:
		vis.position.y = lerpf(vis.position.y, 0.0, 10.0 * delta)
	for s in [-1, 1]:
		var w := vis.get_node_or_null("wing%d" % s)
		if w:
			w.rotation.z = sin(t * 28.0) * 0.6 * s
	if kind == "hopper" or kind == "springbot":
		vis.scale.y = 1.0 + (0.15 if not is_on_floor() else -0.08)
