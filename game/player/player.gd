class_name Player
extends CharacterBody3D
## Pip: run, jump, triple jump, long jump, ground pound, wall jump, swim, hat throw, hat spin, roll, dive.

enum S { GROUND, AIR, LONGJUMP, POUND, POUND_LAND, WALL, SWIM, DIVE, ROLL, CROUCH, SPIN, HURT, CAPTURED, LOCKED, DEAD }

signal died
signal moved_state(s: int)

var state := S.AIR
var cam: Node3D = null              # camera rig (provides yaw for camera-relative movement)
var scripted: Dictionary = {}       # test hook: if non-empty, overrides input
var dir_face := Vector3.FORWARD
var jump_chain := 0
var chain_timer := 0.0
var coyote := 0.0
var jump_buf := 0.0
var invuln := 0.0
var state_t := 0.0
var wall_normal := Vector3.ZERO
var hat: Node3D = null              # active Capt projectile
var hat_cd := 0.0
var captured_by: Node = null
var in_water := false
var water_surface := 0.0
var on_ice := false
var checkpoint := Vector3(0, 2, 0)
var airborne_time := 0.0
var last_floor_y := 0.0
var pound_active := false
var visual: Node3D
var body_mesh: Node3D
var hat_visual: Node3D
var spin_t := 0.0
var interact_target: Node = null
var locked_reason := ""
var stats := {"jumps": 0, "throws": 0, "pounds": 0}
var hat_on_head := true
var _prev_state := S.AIR
var _was_on_floor := false

func _ready() -> void:
	collision_layer = 2
	collision_mask = 1
	floor_snap_length = 0.5
	floor_max_angle = deg_to_rad(50)
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.45
	cap.height = 1.5
	cs.shape = cap
	cs.position.y = 0.75
	add_child(cs)
	add_to_group("player")
	_build_visual()

func _build_visual() -> void:
	visual = Node3D.new()
	add_child(visual)
	var skin := Color(1.0, 0.82, 0.65)
	var shirt := Color(0.2, 0.55, 0.95)
	var outfit: String = Game.data.get("outfit", "") if Game.data.has("outfit") else ""
	if outfit != "":
		var oc = ItemData.outfit_color(outfit)
		if oc != null:
			shirt = oc
	body_mesh = Node3D.new()
	visual.add_child(body_mesh)
	body_mesh.add_child(Build.capsule(0.38, 1.0, shirt, Vector3(0, 0.55, 0)))
	body_mesh.add_child(Build.sphere(0.4, skin, Vector3(0, 1.28, 0)))
	Build.eyes(body_mesh, 0.32, 1.32, 0.15, 0.1)
	body_mesh.add_child(Build.sphere(0.12, Color(1.0, 0.6, 0.55), Vector3(0, 1.2, 0.38)))
	for sx in [-1, 1]:
		body_mesh.add_child(Build.sphere(0.17, Color(0.25, 0.2, 0.3), Vector3(sx * 0.2, 0.08, 0.1)))
		body_mesh.add_child(Build.sphere(0.12, skin, Vector3(sx * 0.46, 0.7, 0.0)))
	# Capt the hat
	hat_visual = Node3D.new()
	hat_visual.position = Vector3(0, 1.62, 0)
	visual.add_child(hat_visual)
	hat_visual.add_child(CaptVisual.build())

func _inp() -> Dictionary:
	if not scripted.is_empty():
		return scripted
	var mv := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	return {
		"move": mv, "jump_p": Input.is_action_just_pressed("jump"), "jump_h": Input.is_action_pressed("jump"),
		"throw_p": Input.is_action_just_pressed("throw"), "spin_p": Input.is_action_just_pressed("spin"),
		"crouch_p": Input.is_action_just_pressed("crouch"), "crouch_h": Input.is_action_pressed("crouch"),
		"roll_p": Input.is_action_just_pressed("roll"), "dive_p": Input.is_action_just_pressed("dive"),
	}

func cam_yaw() -> float:
	return cam.yaw if cam and "yaw" in cam else 0.0

func move_dir(mv: Vector2) -> Vector3:
	var basis := Basis(Vector3.UP, cam_yaw())
	return (basis * Vector3(mv.x, 0, mv.y)).limit_length(1.0)

func set_state(s: int) -> void:
	if s == state:
		return
	_prev_state = state
	state = s
	state_t = 0.0
	moved_state.emit(s)

func can_control() -> bool:
	return state != S.CAPTURED and state != S.LOCKED and state != S.DEAD

func lock(reason := "talk") -> void:
	locked_reason = reason
	velocity = Vector3.ZERO
	set_state(S.LOCKED)

func unlock() -> void:
	if state == S.LOCKED:
		set_state(S.GROUND if is_on_floor() else S.AIR)

func _physics_process(delta: float) -> void:
	state_t += delta
	invuln = maxf(invuln - delta, 0.0)
	hat_cd = maxf(hat_cd - delta, 0.0)
	if is_on_floor():
		chain_timer = maxf(chain_timer - delta, 0.0)
		if chain_timer <= 0.0:
			jump_chain = 0
	if state == S.CAPTURED or state == S.LOCKED or state == S.DEAD:
		_update_visual(delta)
		if state == S.LOCKED:
			velocity.y -= Tuning.GRAVITY * delta
			velocity.x = 0.0
			velocity.z = 0.0
			move_and_slide()
		return
	var inp := _inp()
	_update_environment()
	if inp["jump_p"]:
		jump_buf = Tuning.JUMP_BUFFER
	else:
		jump_buf = maxf(jump_buf - delta, 0.0)
	var mv: Vector2 = inp["move"]
	var wish := move_dir(mv)
	if wish.length() > 0.1 and state != S.POUND and state != S.POUND_LAND:
		dir_face = dir_face.lerp(wish.normalized(), minf(1.0, 18.0 * delta)).normalized() if state != S.DIVE and state != S.ROLL and state != S.LONGJUMP else dir_face
	# hat actions available in most states
	if state != S.HURT:
		if inp["throw_p"]:
			_try_throw()
		if inp["spin_p"] and state != S.SPIN and state != S.SWIM:
			_start_spin()
	match state:
		S.GROUND: _ground(delta, inp, wish)
		S.CROUCH: _crouch(delta, inp, wish)
		S.AIR: _air(delta, inp, wish)
		S.LONGJUMP: _longjump(delta, inp, wish)
		S.POUND: _pound(delta, inp)
		S.POUND_LAND: _pound_land(delta, inp)
		S.WALL: _wall(delta, inp, wish)
		S.SWIM: _swim(delta, inp, wish)
		S.DIVE: _dive(delta, inp, wish)
		S.ROLL: _roll(delta, inp, wish)
		S.SPIN: _spin(delta, inp, wish)
		S.HURT: _hurt(delta)
	move_and_slide()
	_post_move(delta)
	_update_visual(delta)

# ---------------------------------------------------------------- environment
func _update_environment() -> void:
	in_water = false
	for w in get_tree().get_nodes_in_group("water"):
		if w.has_method("contains") and w.contains(global_position):
			in_water = true
			water_surface = w.surface_y()
			break
	on_ice = false
	if is_on_floor():
		for i in get_slide_collision_count():
			var c := get_slide_collision(i)
			var col = c.get_collider()
			if col and col.is_in_group("ice"):
				on_ice = true

func _post_move(delta: float) -> void:
	var floor_now := is_on_floor()
	if floor_now:
		last_floor_y = global_position.y
		coyote = Tuning.COYOTE
		if not _was_on_floor and velocity.y <= 0.1:
			_on_land()
	else:
		coyote = maxf(coyote - delta, 0.0)
		airborne_time += delta
	if floor_now:
		airborne_time = 0.0
	_was_on_floor = floor_now
	if global_position.y < -40.0 and state != S.DEAD:
		fall_into_void()
	# step on enemies
	if velocity.y < 0.0 and state != S.SWIM:
		_check_stomp()

func _on_land() -> void:
	Audio.sfx("land", 1.0, -8.0)
	chain_timer = Tuning.JUMP_CHAIN_TIME
	if state == S.AIR or state == S.DIVE or state == S.LONGJUMP:
		pass

func _check_stomp() -> void:
	for e in get_tree().get_nodes_in_group("stompable"):
		if not is_instance_valid(e) or not e.has_method("stomped"):
			continue
		var d: Vector3 = e.global_position - global_position
		var top: float = e.get("stomp_height") if e.get("stomp_height") != null else 1.0
		if absf(d.x) < 1.1 and absf(d.z) < 1.1 and d.y < -0.1 and d.y > -top - 0.5 and e.has_method("can_stomp") and e.can_stomp():
			if e.stomped(self):
				velocity.y = 13.0 if Input.is_action_pressed("jump") else 10.0
				if state == S.POUND:
					set_state(S.AIR)
				return

# ---------------------------------------------------------------- states
func _hmove(delta: float, wish: Vector3, speed: float, accel: float, decel: float) -> void:
	var target := wish * speed
	var h := Vector3(velocity.x, 0, velocity.z)
	var a := accel if wish.length() > 0.05 else decel
	if on_ice:
		a = Tuning.ICE_ACCEL if wish.length() > 0.05 else Tuning.ICE_DECEL
	h = h.move_toward(target, a * delta)
	velocity.x = h.x
	velocity.z = h.z

func _gravity(delta: float, mult := 1.0) -> void:
	velocity.y = maxf(velocity.y - Tuning.GRAVITY * mult * delta, -Tuning.MAX_FALL)

func _ground(delta: float, inp: Dictionary, wish: Vector3) -> void:
	if in_water and global_position.y < water_surface - 0.5:
		set_state(S.SWIM)
		return
	if not is_on_floor() and coyote <= 0.0:
		set_state(S.AIR)
		return
	var speed := Tuning.RUN_SPEED * _speed_mult()
	_hmove(delta, wish, speed, Tuning.ACCEL, Tuning.DECEL)
	velocity.y = -2.0
	if inp["crouch_p"]:
		set_state(S.CROUCH)
		return
	if inp["roll_p"]:
		_start_roll(wish)
		return
	if inp["dive_p"]:
		_start_dive()
		return
	if jump_buf > 0.0:
		if _try_interact():
			jump_buf = 0.0
			return
		_do_jump()

func _speed_mult() -> float:
	var m := 1.0
	for q in get_tree().get_nodes_in_group("quicksand"):
		if q.has_method("contains") and q.contains(global_position):
			m = 0.45
	return m

func _do_jump() -> void:
	jump_buf = 0.0
	coyote = 0.0
	var idx := mini(jump_chain, 2)
	if Vector3(velocity.x, 0, velocity.z).length() < 2.0:
		idx = 0
	velocity.y = Tuning.JUMP_V[idx]
	Audio.sfx(["jump", "jump2", "jump3"][idx])
	jump_chain = mini(idx + 1, 3) if idx < 2 else 0
	if idx == 2:
		jump_chain = 0
	stats["jumps"] += 1
	set_state(S.AIR)

func _crouch(delta: float, inp: Dictionary, wish: Vector3) -> void:
	_hmove(delta, wish, Tuning.CROUCH_SPEED, Tuning.ACCEL, Tuning.DECEL)
	velocity.y = -2.0
	if not is_on_floor():
		set_state(S.AIR)
		return
	if jump_buf > 0.0:
		jump_buf = 0.0
		var hv := Vector3(velocity.x, 0, velocity.z)
		if hv.length() > 0.5 or wish.length() > 0.3:
			var d := (wish.normalized() if wish.length() > 0.1 else dir_face)
			dir_face = d
			velocity = d * Tuning.LONG_JUMP_SPEED
			velocity.y = Tuning.LONG_JUMP_V
			Audio.sfx("longjump")
			set_state(S.LONGJUMP)
		else:
			# backflip
			velocity = -dir_face * 3.0
			velocity.y = 17.0
			Audio.sfx("jump3")
			set_state(S.AIR)
		return
	if not inp["crouch_h"]:
		set_state(S.GROUND)

func _air(delta: float, inp: Dictionary, wish: Vector3) -> void:
	if in_water and global_position.y < water_surface - 0.6:
		set_state(S.SWIM)
		Audio.sfx("splash")
		return
	_hmove(delta, wish, Tuning.RUN_SPEED, Tuning.AIR_ACCEL, 6.0)
	_gravity(delta)
	# variable jump height
	if velocity.y > 0.0 and not inp["jump_h"] and state_t > 0.05:
		velocity.y *= 0.88
	# coyote jump
	if jump_buf > 0.0 and coyote > 0.0 and velocity.y <= 0.1:
		_do_jump()
		return
	if is_on_floor() and velocity.y <= 0.0:
		set_state(S.GROUND)
		if jump_buf > 0.0:
			_do_jump()
		return
	# wall slide
	if is_on_wall() and velocity.y < 0.0:
		var n := get_wall_normal()
		if absf(n.y) < 0.2 and wish.length() > 0.2 and wish.dot(-n) > 0.2 and not _wall_blocked():
			wall_normal = n
			set_state(S.WALL)
			return
	if inp["crouch_p"]:
		_start_pound()
		return
	if inp["dive_p"]:
		_start_dive()
		return
	if inp["roll_p"] and false:
		pass

func _wall_blocked() -> bool:
	for i in get_slide_collision_count():
		var col = get_slide_collision(i).get_collider()
		if col and col.is_in_group("nowall"):
			return true
	return false

func _wall(delta: float, inp: Dictionary, wish: Vector3) -> void:
	velocity.y = maxf(velocity.y - Tuning.GRAVITY * 0.35 * delta, -Tuning.WALL_SLIDE)
	velocity.x = 0.0
	velocity.z = 0.0
	dir_face = wall_normal
	if jump_buf > 0.0:
		jump_buf = 0.0
		velocity = wall_normal * Tuning.WALL_JUMP_PUSH
		velocity.y = Tuning.WALL_JUMP_V
		dir_face = wall_normal
		Audio.sfx("walljump")
		set_state(S.AIR)
		return
	if is_on_floor():
		set_state(S.GROUND)
		return
	if not is_on_wall() or wish.dot(-wall_normal) < 0.0 or state_t > 4.0:
		# push off the wall
		velocity += wall_normal * 2.0
		set_state(S.AIR)

func _longjump(delta: float, inp: Dictionary, wish: Vector3) -> void:
	_gravity(delta, 0.8)
	var h := Vector3(velocity.x, 0, velocity.z)
	h = h.move_toward(wish * Tuning.LONG_JUMP_SPEED, 6.0 * delta)
	velocity.x = h.x
	velocity.z = h.z
	if is_on_floor() and velocity.y <= 0.0:
		set_state(S.GROUND)
		return
	if is_on_wall() and state_t > 0.1:
		set_state(S.AIR)
	if inp["crouch_p"]:
		_start_pound()
	elif inp["dive_p"]:
		_start_dive()

func _start_pound() -> void:
	velocity = Vector3.ZERO
	pound_active = true
	stats["pounds"] += 1
	set_state(S.POUND)

func _pound(delta: float, inp: Dictionary) -> void:
	if state_t < Tuning.POUND_HANG:
		velocity = Vector3.ZERO
		return
	if state_t - delta < Tuning.POUND_HANG:
		Audio.sfx("dive", 0.6)
	velocity.x = 0.0
	velocity.z = 0.0
	velocity.y = Tuning.POUND_V
	if is_on_floor():
		_pound_impact()
		set_state(S.POUND_LAND)

func _pound_impact() -> void:
	Audio.sfx("pound")
	if cam and cam.has_method("shake"):
		cam.shake(0.35)
	for n in get_tree().get_nodes_in_group("pound_target"):
		if is_instance_valid(n) and n.has_method("on_pound") and n.global_position.distance_to(global_position) < 3.2:
			n.on_pound(self)
	for n in get_tree().get_nodes_in_group("enemy"):
		if is_instance_valid(n) and n.has_method("hurt") and n.global_position.distance_to(global_position) < 3.4:
			n.hurt(2, self)
	for n in get_tree().get_nodes_in_group("boss"):
		if is_instance_valid(n) and n.has_method("hit_by_pound") and n.global_position.distance_to(global_position) < 4.5 + n.get("radius"):
			n.hit_by_pound(self)
	Fx.burst(get_parent(), global_position, Color(1, 1, 1), 16)

func _pound_land(delta: float, inp: Dictionary) -> void:
	velocity.x = 0.0
	velocity.z = 0.0
	velocity.y = -2.0
	if state_t > 0.25:
		set_state(S.GROUND)
		pound_active = false
	elif jump_buf > 0.0 and state_t > 0.08:
		jump_buf = 0.0
		velocity.y = 20.0
		Audio.sfx("jump3")
		pound_active = false
		set_state(S.AIR)

func _start_dive() -> void:
	var d := dir_face
	velocity = d * Tuning.DIVE_SPEED
	velocity.y = Tuning.DIVE_V
	Audio.sfx("dive")
	set_state(S.DIVE)

func _dive(delta: float, inp: Dictionary, wish: Vector3) -> void:
	_gravity(delta, 0.9)
	if is_on_floor():
		# belly-slide
		var h := Vector3(velocity.x, 0, velocity.z)
		h = h.move_toward(Vector3.ZERO, 22.0 * delta)
		velocity.x = h.x
		velocity.z = h.z
		velocity.y = -2.0
		if inp["jump_p"]:
			# dive-hop
			velocity.y = 12.0
			velocity = dir_face * 11.0 + Vector3(0, 12.0, 0)
			set_state(S.AIR)
			return
		if h.length() < 1.0 or state_t > 1.0:
			set_state(S.GROUND)
	elif in_water:
		set_state(S.SWIM)
	elif state_t > 0.2 and inp["roll_p"]:
		pass

func _start_roll(wish: Vector3) -> void:
	var d := wish.normalized() if wish.length() > 0.1 else dir_face
	dir_face = d
	velocity = d * Tuning.ROLL_SPEED
	Audio.sfx("roll")
	set_state(S.ROLL)

func _roll(delta: float, inp: Dictionary, wish: Vector3) -> void:
	var d := dir_face
	if wish.length() > 0.2:
		d = d.lerp(wish.normalized(), 3.0 * delta).normalized()
		dir_face = d
	var sp := Tuning.ROLL_SPEED * maxf(0.4, 1.0 - state_t / Tuning.ROLL_TIME * 0.4)
	velocity.x = d.x * sp
	velocity.z = d.z * sp
	velocity.y = -2.0 if is_on_floor() else velocity.y - Tuning.GRAVITY * delta
	if jump_buf > 0.0 and is_on_floor():
		jump_buf = 0.0
		velocity.y = 12.5
		velocity.x = d.x * 13.0
		velocity.z = d.z * 13.0
		Audio.sfx("jump2")
		set_state(S.AIR)
		return
	if not is_on_floor() and state_t > 0.15:
		set_state(S.AIR)
		return
	if state_t > Tuning.ROLL_TIME:
		set_state(S.GROUND)

func _start_spin() -> void:
	if hat_cd > 0.0 and false:
		return
	spin_t = 0.0
	Audio.sfx("spin")
	_prev_state = state
	set_state(S.SPIN)
	_spin_hit()

func _spin(delta: float, inp: Dictionary, wish: Vector3) -> void:
	var airborne := not is_on_floor()
	_hmove(delta, wish, Tuning.RUN_SPEED * 0.8, Tuning.AIR_ACCEL if airborne else Tuning.ACCEL, 8.0)
	if airborne:
		velocity.y = maxf(velocity.y - Tuning.GRAVITY * 0.35 * delta, -4.0)   # hat-spin hover
	else:
		velocity.y = -2.0
	if int(state_t * 20.0) != int((state_t - delta) * 20.0):
		_spin_hit()
	if state_t > Tuning.SPIN_TIME:
		set_state(S.AIR if airborne else S.GROUND)
	elif jump_buf > 0.0 and is_on_floor():
		jump_buf = 0.0
		_do_jump()

func _spin_hit() -> void:
	for g in ["enemy", "breakable", "spin_target"]:
		for n in get_tree().get_nodes_in_group(g):
			if is_instance_valid(n) and n.global_position.distance_to(global_position + Vector3(0, 0.8, 0)) < 2.6:
				if n.has_method("hurt"):
					n.hurt(1, self)
				elif n.has_method("on_hat_hit"):
					n.on_hat_hit(self)
	for b in get_tree().get_nodes_in_group("boss"):
		if is_instance_valid(b) and b.has_method("hit_by_hat") and b.global_position.distance_to(global_position) < 3.2 + b.get("radius"):
			b.hit_by_hat(self)
	for c in get_tree().get_nodes_in_group("coin"):
		if is_instance_valid(c) and c.global_position.distance_to(global_position + Vector3(0, 0.8, 0)) < 3.5:
			c.collect()

func _swim(delta: float, inp: Dictionary, wish: Vector3) -> void:
	if not in_water:
		set_state(S.AIR)
		return
	var depth := water_surface - global_position.y
	var up := 0.0
	if inp["jump_h"]:
		up = 1.0
	if inp["crouch_h"]:
		up = -1.0
	var tgt := wish * Tuning.SWIM_SPEED
	velocity.x = move_toward(velocity.x, tgt.x, 14.0 * delta)
	velocity.z = move_toward(velocity.z, tgt.z, 14.0 * delta)
	# buoyancy: float near surface, sink slowly otherwise
	var vy := -1.5
	if depth < 0.9:
		vy = 2.0 + (0.9 - depth) * 4.0
	if up != 0.0:
		vy = up * 5.0
	velocity.y = move_toward(velocity.y, vy, 20.0 * delta)
	if int(state_t * 3.0) != int((state_t - delta) * 3.0) and wish.length() > 0.2:
		Audio.sfx("swim", 1.0, -10.0)
	# leave water via jump at surface
	if depth < 1.0 and inp["jump_p"]:
		velocity.y = 12.0
		set_state(S.AIR)
		Audio.sfx("jump")

func _hurt(delta: float) -> void:
	_gravity(delta)
	velocity.x = move_toward(velocity.x, 0.0, 10.0 * delta)
	velocity.z = move_toward(velocity.z, 0.0, 10.0 * delta)
	if state_t > 0.45 and is_on_floor():
		set_state(S.GROUND)
	elif state_t > 0.9:
		set_state(S.AIR)

# ---------------------------------------------------------------- hat
func _try_throw() -> void:
	if hat != null and is_instance_valid(hat):
		return
	if hat_cd > 0.0:
		return
	hat_cd = 0.15
	stats["throws"] += 1
	var capt := Capt.new()
	capt.owner_player = self
	var d := dir_face
	if cam and cam.has_method("aim_dir"):
		d = cam.aim_dir(self)
	capt.direction = d
	get_parent().add_child(capt)
	capt.global_position = global_position + Vector3(0, 1.3, 0) + d * 0.6
	hat = capt
	hat_visual.visible = false
	hat_on_head = false
	Audio.sfx("throw")

func hat_returned() -> void:
	hat = null
	hat_visual.visible = true
	hat_on_head = true
	Audio.sfx("catch")

func _try_interact() -> bool:
	for n in get_tree().get_nodes_in_group("interactable"):
		if is_instance_valid(n) and n.has_method("can_interact") and n.can_interact(self):
			n.interact(self)
			return true
	return false

# ---------------------------------------------------------------- damage / death / capture
func hurt(from: Vector3, dmg := 1) -> void:
	if invuln > 0.0 or state == S.DEAD or state == S.CAPTURED:
		return
	invuln = Tuning.INVULN
	Game.damage(dmg)
	Audio.sfx("hurt")
	var d := (global_position - from)
	d.y = 0.0
	d = d.normalized() if d.length() > 0.01 else -dir_face
	velocity = d * 7.0
	velocity.y = 9.0
	if cam and cam.has_method("shake"):
		cam.shake(0.4)
	if Game.health <= 0:
		die()
	else:
		set_state(S.HURT)

func die() -> void:
	set_state(S.DEAD)
	velocity = Vector3.ZERO
	died.emit()

func fall_into_void() -> void:
	Audio.sfx("fall")
	Game.damage(1)
	if Game.health <= 0:
		die()
	else:
		respawn()

func respawn() -> void:
	global_position = checkpoint + Vector3(0, 1.0, 0)
	velocity = Vector3.ZERO
	invuln = 1.5
	set_state(S.AIR)

func bounce(v := Tuning.HAT_BOUNCE_V) -> void:
	velocity.y = v
	if state != S.AIR:
		set_state(S.AIR)
	jump_chain = 0

func capture(target: Node) -> void:
	if state == S.CAPTURED:
		return
	captured_by = target
	set_state(S.CAPTURED)
	visual.visible = false
	hat_visual.visible = false
	collision_layer = 0
	Audio.sfx("capture")
	if hat and is_instance_valid(hat):
		hat.queue_free()
	hat = null

func release_capture(pos: Vector3) -> void:
	captured_by = null
	global_position = pos
	collision_layer = 2
	visual.visible = true
	hat_visual.visible = true
	velocity = Vector3(0, 12.0, 0)
	invuln = 1.0
	set_state(S.AIR)
	Audio.sfx("release")

# ---------------------------------------------------------------- visuals
func _update_visual(delta: float) -> void:
	if visual == null:
		return
	var yaw := atan2(dir_face.x, dir_face.z)
	visual.rotation.y = lerp_angle(visual.rotation.y, yaw, minf(1.0, 16.0 * delta))
	var flicker := invuln > 0.0 and int(Time.get_ticks_msec() / 80) % 2 == 0
	visual.visible = state != S.CAPTURED and not flicker
	body_mesh.rotation = Vector3.ZERO
	body_mesh.scale = Vector3.ONE
	body_mesh.position = Vector3.ZERO
	var hs := Vector3(velocity.x, 0, velocity.z).length()
	match state:
		S.GROUND:
			body_mesh.position.y = absf(sin(Time.get_ticks_msec() * 0.016 * clampf(hs / 6.0, 0.0, 1.5))) * 0.08 * clampf(hs, 0.0, 1.0)
			body_mesh.rotation.x = clampf(hs / 40.0, 0.0, 0.3)
		S.CROUCH:
			body_mesh.scale = Vector3(1.1, 0.65, 1.1)
		S.ROLL:
			body_mesh.rotation.x = state_t * 22.0
			body_mesh.position.y = 0.5
		S.DIVE:
			body_mesh.rotation.x = 1.2
			body_mesh.position.y = 0.45
		S.LONGJUMP:
			body_mesh.rotation.x = 1.1
			body_mesh.position.y = 0.4
		S.POUND, S.POUND_LAND:
			body_mesh.rotation.x = 0.0
			body_mesh.scale = Vector3(0.9, 1.15, 0.9) if state == S.POUND else Vector3(1.2, 0.7, 1.2)
		S.SPIN:
			visual.rotation.y += state_t * 40.0
		S.WALL:
			body_mesh.rotation.x = -0.3
		S.SWIM:
			body_mesh.rotation.x = 1.2
			body_mesh.position.y = 0.4
		S.AIR:
			body_mesh.rotation.x = clampf(-velocity.y / 60.0, -0.3, 0.3)
	if hat_visual and hat_on_head:
		hat_visual.rotation.y += delta * (30.0 if state == S.SPIN else 0.0)

func is_attacking() -> bool:
	return state == S.SPIN or state == S.ROLL or state == S.POUND or state == S.DIVE
