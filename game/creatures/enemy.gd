class_name Enemy
extends CharacterBody3D
## Basic enemies: walker (patrols), charger (rushes), shooter (spits). Stompable, hat-able, drops coins.
var kind := "walker"
var kingdom := "forest"
var hp := 1
var home := Vector3.ZERO
var player: Player
var t := 0.0
var stun := 0.0
var state := "patrol"
var dir := Vector3.FORWARD
var stomp_height := 1.1
var dead := false
var shoot_cd := 2.0
var charge_t := 0.0
var vis: Node3D
var body_col: Color

func _ready() -> void:
	collision_layer = 4
	collision_mask = 1
	add_to_group("enemy")
	add_to_group("stompable")
	home = global_position
	var cs := CollisionShape3D.new()
	var sh := SphereShape3D.new()
	sh.radius = 0.55
	cs.shape = sh
	cs.position.y = 0.55
	add_child(cs)
	var pal: Dictionary = Kingdoms.DATA[kingdom]["pal"]
	body_col = pal["accent"] if kind == "charger" else (pal["ground2"].lightened(0.25) if kind == "walker" else pal["ground"].darkened(0.2))
	vis = Node3D.new()
	add_child(vis)
	vis.add_child(Build.sphere(0.6, body_col, Vector3(0, 0.6, 0)))
	vis.add_child(Build.box(Vector3(0.9, 0.12, 0.2), Color(0.1, 0.05, 0.1), Vector3(0, 0.95, 0.5)))
	Build.eyes(vis, 0.5, 0.75, 0.2, 0.13)
	for sx in [-1, 1]:
		vis.add_child(Build.sphere(0.2, body_col.darkened(0.4), Vector3(sx * 0.3, 0.1, 0.1)))
	if kind == "charger":
		vis.add_child(Build.prism(Vector3(0.3, 0.5, 0.3), Color(1, 0.95, 0.8), Vector3(0, 1.3, 0.25)))
	if kind == "shooter":
		vis.add_child(Build.cyl(0.18, 0.25, 0.5, Color(0.2, 0.2, 0.25), Vector3(0, 0.7, 0.6)))
		vis.rotation_degrees.x = 0
	dir = Vector3(randf() - 0.5, 0, randf() - 0.5).normalized()
	t = randf() * 4.0

func _get_player() -> Player:
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if not ps.is_empty():
			player = ps[0]
	return player

func can_stomp() -> bool:
	return not dead

func stomped(p) -> bool:
	hurt(2, p)
	return true

func hurt(n: int, src) -> void:
	if dead:
		return
	hp -= n
	if hp <= 0:
		die()
	else:
		stun = 1.0
		Audio.sfx("hit")

func die() -> void:
	dead = true
	Audio.sfx("hit", 1.2)
	Fx.burst(get_parent(), global_position + Vector3(0, 0.6, 0), body_col, 14)
	var w := get_parent()
	for i in 2:
		var c := CoinPickup.new()
		c.kingdom = kingdom
		c.sticky = true
		w.add_child(c)
		c.global_position = global_position + Vector3(randf_range(-0.6, 0.6), 0.6, randf_range(-0.6, 0.6))
	queue_free()

func _physics_process(delta: float) -> void:
	if dead:
		return
	t += delta
	stun = maxf(stun - delta, 0.0)
	velocity.y -= 32.0 * delta
	var p := _get_player()
	var tgt: Node3D = p
	if p and p.state == Player.S.CAPTURED and p.captured_by:
		tgt = p.captured_by
	var to_p := Vector3.ZERO
	var dist := 999.0
	if tgt:
		to_p = tgt.global_position - global_position
		dist = Vector2(to_p.x, to_p.z).length()
	if stun > 0.0:
		velocity.x = 0.0
		velocity.z = 0.0
		vis.rotation.z = sin(t * 30.0) * 0.2
		move_and_slide()
		return
	vis.rotation.z = 0.0
	match kind:
		"walker": _walk(delta, dist, to_p)
		"charger": _charge(delta, dist, to_p)
		"shooter": _shoot(delta, dist, to_p)
	move_and_slide()
	if is_on_floor() and kind != "shooter":
		pass
	vis.position.y = absf(sin(t * 8.0)) * 0.1
	# contact damage
	if tgt and absf(to_p.y) < 1.4 and dist < 1.0:
		if p.is_attacking():
			hurt(1, p)
		elif p.state != Player.S.POUND:
			if p.state == Player.S.CAPTURED and p.captured_by:
				if p.captured_by.has_method("smashes") and p.captured_by.smashes():
					hurt(2, p)
				else:
					p.captured_by.release()
					p.hurt(global_position, 1)
			else:
				p.hurt(global_position, 1)

func _face(d: Vector3) -> void:
	if d.length() > 0.1:
		vis.rotation.y = lerp_angle(vis.rotation.y, atan2(d.x, d.z), 0.2)

func _walk(delta: float, dist: float, to_p: Vector3) -> void:
	var speed := 2.2
	if dist < 9.0:
		dir = Vector3(to_p.x, 0, to_p.z).normalized()
		speed = 3.0
	elif int(t) % 4 == 0 and fmod(t, 1.0) < delta:
		dir = Vector3(randf() - 0.5, 0, randf() - 0.5).normalized()
	if global_position.distance_to(home) > 12.0:
		dir = (home - global_position).normalized()
		dir.y = 0
	velocity.x = dir.x * speed
	velocity.z = dir.z * speed
	_face(dir)

func _charge(delta: float, dist: float, to_p: Vector3) -> void:
	match state:
		"patrol":
			velocity.x = move_toward(velocity.x, 0, 20 * delta)
			velocity.z = move_toward(velocity.z, 0, 20 * delta)
			if dist < 11.0:
				state = "wind"
				charge_t = 0.6
				dir = Vector3(to_p.x, 0, to_p.z).normalized()
		"wind":
			charge_t -= delta
			vis.scale = Vector3(1.1, 0.8, 1.1)
			_face(dir)
			if charge_t <= 0.0:
				state = "rush"
				charge_t = 1.0
				vis.scale = Vector3.ONE
		"rush":
			charge_t -= delta
			velocity.x = dir.x * 11.0
			velocity.z = dir.z * 11.0
			if charge_t <= 0.0 or is_on_wall():
				state = "rest"
				charge_t = 1.2
		"rest":
			velocity.x = move_toward(velocity.x, 0, 30 * delta)
			velocity.z = move_toward(velocity.z, 0, 30 * delta)
			charge_t -= delta
			if charge_t <= 0.0:
				state = "patrol"

func _shoot(delta: float, dist: float, to_p: Vector3) -> void:
	velocity.x = 0.0
	velocity.z = 0.0
	_face(to_p)
	shoot_cd -= delta
	if dist < 16.0 and shoot_cd <= 0.0:
		shoot_cd = 2.4
		var pr := Projectile.new()
		pr.color = Color(0.9, 0.4, 0.3)
		pr.radius = 0.28
		var d := (to_p + Vector3(0, 0.5, 0)).normalized()
		pr.vel = d * 9.0
		get_parent().add_child(pr)
		pr.global_position = global_position + Vector3(0, 0.9, 0) + d
		Audio.sfx("shoot", 1.0, -8.0)
