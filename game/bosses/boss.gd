class_name Boss
extends CharacterBody3D
## Multi-phase boss. Cycle: telegraph -> attack -> exhausted (vulnerable) -> repeat. Each phase has a different attack list.
signal defeated
signal phase_changed(n: int)
signal hp_changed(cur: int, total: int)

var boss_id := "mogul"
var info: Dictionary
var phase_i := 0
var hp_in_phase := 3
var total_hp := 0
var cur_total := 0
var radius := 2.0
var state := "idle"
var state_t := 0.0
var attack := ""
var arena_center := Vector3.ZERO
var arena_radius := 16.0
var player: Player
var active := false
var vis: Node3D
var t := 0.0
var invuln := 0.0
var dir := Vector3.FORWARD
var attack_n := 0
var phase_speed := 1.0
var stomp_height := 3.5
var minions: Array = []
var beam_angle := 0.0
var beam_node: Node3D
var rng := RandomNumberGenerator.new()
var dead := false
var shielded := false

func _ready() -> void:
	info = BossData.DATA[boss_id]
	collision_layer = 4
	collision_mask = 1
	add_to_group("boss")
	radius = 1.1 * float(info["scale"])
	var cs := CollisionShape3D.new()
	var sh := CapsuleShape3D.new()
	sh.radius = radius * 0.6
	sh.height = radius * 2.0
	cs.shape = sh
	cs.position.y = radius
	add_child(cs)
	for ph in info["phases"]:
		total_hp += int(ph["hp"])
	cur_total = total_hp
	hp_in_phase = int(info["phases"][0]["hp"])
	phase_speed = float(info["phases"][0]["speed"])
	vis = Node3D.new()
	add_child(vis)
	BossVisual.build(vis, boss_id, info)
	rng.seed = hash(boss_id)

func activate() -> void:
	active = true
	state = "idle"
	state_t = 0.0
	hp_changed.emit(cur_total, total_hp)

func _get_player() -> Player:
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if not ps.is_empty():
			player = ps[0]
	return player

func _target() -> Node3D:
	var p := _get_player()
	if p and p.state == Player.S.CAPTURED and p.captured_by:
		return p.captured_by
	return p

func _physics_process(delta: float) -> void:
	if dead:
		return
	t += delta
	state_t += delta
	invuln = maxf(invuln - delta, 0.0)
	if not active:
		vis.position.y = sin(t * 2.0) * 0.1
		return
	var tgt := _target()
	if tgt == null:
		return
	velocity.y -= 32.0 * delta
	match state:
		"idle":
			_face(tgt.global_position - global_position)
			velocity.x = 0.0
			velocity.z = 0.0
			if state_t > 1.0 / phase_speed:
				_pick_attack()
		"telegraph":
			_face(tgt.global_position - global_position)
			vis.scale = Vector3.ONE * (1.0 + sin(state_t * 30.0) * 0.04)
			if state_t > _tele_time() / phase_speed:
				vis.scale = Vector3.ONE
				_begin_attack()
		"attack":
			_do_attack(delta, tgt)
		"exhausted":
			velocity.x = move_toward(velocity.x, 0.0, 30.0 * delta)
			velocity.z = move_toward(velocity.z, 0.0, 30.0 * delta)
			vis.rotation.z = sin(t * 6.0) * 0.12
			if state_t > 3.8:
				vis.rotation.z = 0.0
				_go("idle")
		"phase_change":
			vis.scale = Vector3.ONE * (1.0 + sin(state_t * 25.0) * 0.08)
			if state_t > 2.0:
				vis.scale = Vector3.ONE
				_go("idle")
	move_and_slide()
	# keep inside arena
	var off := global_position - arena_center
	off.y = 0.0
	if off.length() > arena_radius - 1.5:
		var n := off.normalized() * (arena_radius - 1.5)
		global_position.x = arena_center.x + n.x
		global_position.z = arena_center.z + n.z
	# contact damage when not exhausted
	if state != "exhausted" and state != "phase_change":
		var d := tgt.global_position - global_position
		if Vector2(d.x, d.z).length() < radius * 0.9 and d.y < radius * 1.6 and d.y > -1.0:
			_hurt_player()
	else:
		# exhausted: Pip can stomp it
		var p := _get_player()
		if p and p.velocity.y < 0.0:
			var d := tgt.global_position - global_position
			if Vector2(d.x, d.z).length() < radius * 1.0 and d.y > radius * 1.2 and d.y < radius * 2.6:
				if take_hit(1):
					p.bounce(16.0)

func _hurt_player() -> void:
	var p := _get_player()
	if p.state == Player.S.CAPTURED and p.captured_by:
		p.captured_by.release()
	p.hurt(global_position, 1)

func _face(d: Vector3) -> void:
	if d.length() > 0.1:
		vis.rotation.y = lerp_angle(vis.rotation.y, atan2(d.x, d.z), 0.12)

func _go(s: String) -> void:
	state = s
	state_t = 0.0

func _tele_time() -> float:
	return 0.9

func _pick_attack() -> void:
	var list: Array = info["phases"][phase_i]["attacks"]
	attack = list[attack_n % list.size()]
	attack_n += 1
	_go("telegraph")
	Audio.sfx("warn")

func _begin_attack() -> void:
	_go("attack")
	var tgt := _target()
	dir = (tgt.global_position - global_position)
	dir.y = 0.0
	dir = dir.normalized()
	match attack:
		"charge":
			Audio.sfx("boss_roar", 1.2)
		"slam":
			velocity.y = 16.0
			Audio.sfx("boss_roar")
		"rain":
			_spawn_rain()
		"ring":
			_spawn_ring()
		"summon":
			_summon()
		"beam":
			beam_angle = atan2(dir.x, dir.z) - 1.2
			_make_beam()
		"spin":
			Audio.sfx("spin", 0.7)

func _do_attack(delta: float, tgt: Node3D) -> void:
	var sp := phase_speed
	match attack:
		"charge":
			velocity.x = dir.x * 14.0 * sp
			velocity.z = dir.z * 14.0 * sp
			_face(dir)
			var off := global_position - arena_center
			off.y = 0
			if state_t > 1.4 or off.length() > arena_radius - 2.2:
				attack_end(true)
		"slam":
			if state_t < 0.5:
				var d := tgt.global_position - global_position
				d.y = 0
				velocity.x = d.normalized().x * 7.0 * sp
				velocity.z = d.normalized().z * 7.0 * sp
			else:
				velocity.x = 0
				velocity.z = 0
				velocity.y = minf(velocity.y, -25.0)
			if state_t > 0.3 and is_on_floor():
				var s := Shockwave.new()
				s.max_radius = 12.0
				s.speed = 9.0 * sp
				s.color = info["color2"]
				get_parent().add_child(s)
				s.global_position = global_position
				Audio.sfx("pound")
				var cam := get_tree().get_first_node_in_group("camera_rig")
				if cam:
					cam.shake(0.6)
				attack_end(true)
		"rain", "ring", "summon":
			velocity.x = 0.0
			velocity.z = 0.0
			if state_t > 1.6 / sp:
				attack_end(attack == "summon" or attack_n % 2 == 0)
		"beam":
			beam_angle += 1.6 * sp * delta
			if beam_node:
				beam_node.rotation.y = beam_angle
				_beam_hit(tgt)
			if state_t > 2.8 / sp:
				if beam_node:
					beam_node.queue_free()
					beam_node = null
				attack_end(true)
		"spin":
			vis.rotation.y += 14.0 * delta
			var d := tgt.global_position - global_position
			d.y = 0
			velocity.x = d.normalized().x * 5.0 * sp
			velocity.z = d.normalized().z * 5.0 * sp
			# tentacles/arms reach: bigger hit radius
			if Vector2(d.x, d.z).length() < radius * 2.0 and absf(tgt.global_position.y - global_position.y) < 1.2:
				_hurt_player()
			if state_t > 2.6 / sp:
				attack_end(true)

func attack_end(tired: bool) -> void:
	velocity.x = 0.0
	velocity.z = 0.0
	if beam_node:
		beam_node.queue_free()
		beam_node = null
	if tired:
		_go("exhausted")
		Audio.sfx("catch", 0.7)
	else:
		_go("idle")

func _spawn_rain() -> void:
	var tgt := _target()
	var n := 6 + phase_i * 2
	for i in n:
		var ang := rng.randf() * TAU
		var r := rng.randf() * (arena_radius - 3.0)
		var pos := arena_center + Vector3(cos(ang) * r, 0, sin(ang) * r)
		if i == 0:
			pos = tgt.global_position
		var m := RainMarker.new()
		m.delay = 0.9 + i * 0.12
		m.color = info["color2"]
		get_parent().add_child(m)
		m.global_position = Vector3(pos.x, arena_center.y + 0.05, pos.z)

func _spawn_ring() -> void:
	var n := 10 + phase_i * 2
	for i in n:
		var a := float(i) / n * TAU + t
		var pr := Projectile.new()
		pr.color = info["color2"]
		pr.radius = 0.4
		pr.vel = Vector3(cos(a), 0.0, sin(a)) * 8.5 * phase_speed
		pr.life = 2.5
		get_parent().add_child(pr)
		pr.global_position = global_position + Vector3(0, 1.0, 0)
	Audio.sfx("shoot", 0.7)

func _summon() -> void:
	minions = minions.filter(func(m): return is_instance_valid(m))
	var n := 2 if minions.size() < 3 else 0
	for i in n:
		var e := Enemy.new()
		e.kind = "walker" if i % 2 == 0 else "charger"
		e.kingdom = _kingdom_for_visuals()
		get_parent().add_child(e)
		var a := rng.randf() * TAU
		e.global_position = arena_center + Vector3(cos(a) * 8.0, 1.0, sin(a) * 8.0)
		minions.append(e)
	Audio.sfx("boss_roar", 1.4)

func _kingdom_for_visuals() -> String:
	var k: String = info["kingdom"]
	return k if k != "final" else "volcano"

func _make_beam() -> void:
	beam_node = Node3D.new()
	var len := arena_radius * 1.1
	var m := Build.box(Vector3(0.7, 0.5, len), Color(1, 0.3, 0.3), Vector3(0, 0.6, len * 0.5), 1.2)
	beam_node.add_child(m)
	add_child(beam_node)
	beam_node.top_level = false

func _beam_hit(tgt: Node3D) -> void:
	var local := tgt.global_position - global_position
	var fwd := Vector3(sin(beam_angle), 0, cos(beam_angle))
	var along := local.dot(fwd)
	var side := (local - fwd * along).length()
	if along > 0.0 and along < arena_radius * 1.1 and side < 0.8 and local.y < 1.6:
		_hurt_player()

# ---------------------------------------------------------------- damage
func can_stomp() -> bool:
	return false

func hit_by_hat(p) -> void:
	if state == "exhausted":
		take_hit(1)
	else:
		Audio.sfx("hit", 0.6, -4.0)

func hit_by_pound(p) -> void:
	if state == "exhausted":
		take_hit(1)

func take_hit(n: int) -> bool:
	if invuln > 0.0 or dead or not active or state != "exhausted":
		return false
	invuln = 0.8
	hp_in_phase -= n
	cur_total -= n
	Audio.sfx("boss_hit")
	Fx.burst(get_parent(), global_position + Vector3(0, radius, 0), Color(1, 0.9, 0.4), 20, 7.0)
	var cam := get_tree().get_first_node_in_group("camera_rig")
	if cam:
		cam.shake(0.5)
	hp_changed.emit(cur_total, total_hp)
	_go("exhausted")
	state_t = 1.5
	if hp_in_phase <= 0:
		phase_i += 1
		if phase_i >= info["phases"].size():
			_die()
		else:
			hp_in_phase = int(info["phases"][phase_i]["hp"])
			phase_speed = float(info["phases"][phase_i]["speed"])
			attack_n = 0
			phase_changed.emit(phase_i)
			_go("phase_change")
			Audio.sfx("boss_roar", 0.8)
			for m in minions:
				if is_instance_valid(m):
					m.queue_free()
			minions.clear()
	return true

func _die() -> void:
	dead = true
	state = "dead"
	for m in minions:
		if is_instance_valid(m):
			m.hurt(9, null)
	Audio.sfx("explosion")
	Fx.burst(get_parent(), global_position + Vector3(0, radius, 0), info["color"], 40, 10.0, 1.2)
	defeated.emit()
	var tw := create_tween()
	tw.tween_property(vis, "scale", Vector3(0.01, 0.01, 0.01), 1.2)
	tw.tween_callback(queue_free)
