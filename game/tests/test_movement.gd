extends RefCounted
## Physics-driven tests: movement, jumps, wall jump, ground pound, swim, collision.
func run(t) -> void:
	var w = t.flat_world()
	var p: Player = t.make_player(w)
	await t.frames(20)
	t.check(p.is_on_floor(), "player lands and is on floor")
	t.check(p.state == Player.S.GROUND, "state GROUND at rest (%d)" % p.state)
	# --- run
	p.scripted = t.inp({"move": Vector2(0, -1)})
	await t.frames(60)
	var sp := Vector2(p.velocity.x, p.velocity.z).length()
	t.check(absf(sp - Tuning.RUN_SPEED) < 0.5, "reaches run speed (%.2f)" % sp)
	t.check(p.global_position.z < -3.0, "moved forward (-Z) (z=%.2f)" % p.global_position.z)
	p.scripted = t.inp()
	await t.frames(30)
	t.check(Vector2(p.velocity.x, p.velocity.z).length() < 0.2, "stops when no input")
	# --- single jump height
	p.global_position = Vector3(0, 0.05, 0)
	p.velocity = Vector3.ZERO
	await t.frames(10)
	var y0 := p.global_position.y
	p.scripted = t.inp({"jump_p": true, "jump_h": true})
	await t.frames(1)
	p.scripted = t.inp({"jump_h": true})
	var peak := y0
	for i in 60:
		await t.frames(1)
		peak = maxf(peak, p.global_position.y)
	var expect := Tuning.jump_height(Tuning.JUMP_V[0])
	t.check(absf((peak - y0) - expect) < expect * 0.2, "single jump height %.2f ~ %.2f" % [peak - y0, expect])
	p.scripted = t.inp()
	await t.frames(40)
	# --- variable jump: tap is lower than hold
	p.global_position = Vector3(0, 0.05, 0)
	await t.frames(10)
	y0 = p.global_position.y
	p.scripted = t.inp({"jump_p": true, "jump_h": true})
	await t.frames(1)
	p.scripted = t.inp({"jump_h": false})
	var tap_peak := y0
	for i in 60:
		await t.frames(1)
		tap_peak = maxf(tap_peak, p.global_position.y)
	t.check(tap_peak - y0 < peak - y0 - 0.2, "tap jump lower than held jump (%.2f < %.2f)" % [tap_peak - y0, peak - y0])
	await t.frames(40)
	# --- triple jump: 3 consecutive jumps while running get higher
	p.global_position = Vector3(0, 0.05, 0)
	p.velocity = Vector3.ZERO
	p.jump_chain = 0
	p.chain_timer = 0.0
	await t.frames(10)
	var peaks: Array = []
	for j in 3:
		p.scripted = t.inp({"move": Vector2(0, -1), "jump_p": true, "jump_h": true})
		await t.frames(1)
		p.scripted = t.inp({"move": Vector2(0, -1), "jump_h": true})
		var pk := 0.0
		var base_y := 0.0
		for i in 120:
			await t.frames(1)
			pk = maxf(pk, p.global_position.y)
			if p.is_on_floor() and i > 5:
				break
		peaks.append(pk)
	t.check(peaks[2] > peaks[0] + 1.5, "triple jump higher than first (%s)" % str(peaks))
	t.check(peaks[1] > peaks[0] + 0.2, "double jump higher than first")
	p.scripted = t.inp()
	await t.frames(60)
	# --- long jump travels farther than normal jump
	p.global_position = Vector3(0, 0.05, 0)
	p.velocity = Vector3.ZERO
	p.dir_face = Vector3.FORWARD
	await t.frames(10)
	p.scripted = t.inp({"crouch_p": true, "crouch_h": true})
	await t.frames(2)
	t.check(p.state == Player.S.CROUCH, "crouch state")
	p.scripted = t.inp({"crouch_h": true, "move": Vector2(0, -1), "jump_p": true})
	await t.frames(1)
	t.check(p.state == Player.S.LONGJUMP, "long jump started (state %d)" % p.state)
	var z0 := p.global_position.z
	p.scripted = t.inp({"move": Vector2(0, -1)})
	for i in 90:
		await t.frames(1)
		if p.is_on_floor() and i > 5:
			break
	var dist := z0 - p.global_position.z
	t.check(dist > 8.0, "long jump covers distance (%.1f)" % dist)
	p.scripted = t.inp()
	await t.frames(30)
	# --- ground pound
	p.global_position = Vector3(0, 6.0, 0)
	p.velocity = Vector3.ZERO
	await t.frames(14)
	p.scripted = t.inp({"crouch_p": true})
	await t.frames(1)
	t.check(p.state == Player.S.POUND, "ground pound state (%d)" % p.state)
	p.scripted = t.inp()
	var landed := false
	for i in 90:
		await t.frames(1)
		if p.state == Player.S.POUND_LAND or p.state == Player.S.GROUND:
			landed = true
			break
	t.check(landed and p.is_on_floor(), "ground pound lands")
	await t.frames(30)
	# --- roll and dive
	p.global_position = Vector3(0, 0.05, 0)
	p.velocity = Vector3.ZERO
	p.dir_face = Vector3.FORWARD
	await t.frames(5)
	p.scripted = t.inp({"roll_p": true, "move": Vector2(0, -1)})
	await t.frames(2)
	t.check(p.state == Player.S.ROLL, "roll state")
	t.check(Vector2(p.velocity.x, p.velocity.z).length() > Tuning.RUN_SPEED, "roll is faster than run")
	p.scripted = t.inp()
	await t.frames(60)
	p.scripted = t.inp({"dive_p": true})
	await t.frames(2)
	t.check(p.state == Player.S.DIVE, "dive state")
	p.scripted = t.inp()
	await t.frames(80)
	t.check(p.state == Player.S.GROUND, "recovers from dive (%d)" % p.state)
	# --- collision: cannot run through a wall
	var wall := StaticBody3D.new()
	var cs := CollisionShape3D.new()
	var sh := BoxShape3D.new()
	sh.size = Vector3(20, 10, 0.3)
	cs.shape = sh
	wall.add_child(cs)
	wall.position = Vector3(0, 5, -30)
	w.add_child(wall)
	p.global_position = Vector3(0, 0.05, -10)
	p.velocity = Vector3.ZERO
	await t.frames(5)
	p.scripted = t.inp({"move": Vector2(0, -1)})
	await t.frames(240)
	t.check(p.global_position.z > -30.0, "wall blocks player (z=%.2f)" % p.global_position.z)
	# --- wall jump
	p.global_position = Vector3(0, 0.05, -26)
	p.velocity = Vector3.ZERO
	p.set_state(Player.S.GROUND)
	await t.frames(5)
	p.scripted = t.inp({"move": Vector2(0, -1), "jump_p": true, "jump_h": true})
	await t.frames(1)
	p.scripted = t.inp({"move": Vector2(0, -1), "jump_h": true})
	var on_wall := false
	for i in 60:
		await t.frames(1)
		if p.state == Player.S.WALL:
			on_wall = true
			break
	t.check(on_wall, "enters wall-slide against wall")
	if on_wall:
		var y_before := p.global_position.y
		p.scripted = t.inp({"move": Vector2(0, -1), "jump_p": true, "jump_h": true})
		await t.frames(1)
		p.scripted = t.inp({"jump_h": true})
		await t.frames(10)
		t.check(p.velocity.z > 2.0 or p.global_position.z > -29.0, "wall jump pushes away from wall (vz=%.2f)" % p.velocity.z)
		t.check(p.global_position.y > y_before - 0.1, "wall jump goes up")
	wall.queue_free()
	p.scripted = t.inp()
	# --- no tunnelling through thin floor at terminal velocity
	var thin := StaticBody3D.new()
	var cs2 := CollisionShape3D.new()
	var sh2 := BoxShape3D.new()
	sh2.size = Vector3(10, 0.2, 10)
	cs2.shape = sh2
	thin.add_child(cs2)
	thin.position = Vector3(100, 20, 100)
	w.add_child(thin)
	p.global_position = Vector3(100, 80, 100)
	p.velocity = Vector3.ZERO
	p.set_state(Player.S.AIR)
	await t.frames(200)
	t.check(p.global_position.y > 19.5 and p.global_position.y < 21.5, "no tunnelling through thin floor (y=%.2f)" % p.global_position.y)
	# --- swimming
	var water := Water.new()
	water.size = Vector3(60, 10, 60)
	w.add_child(water)
	water.position = Vector3(-100, -4.0, 0)
	# deep floor under water so the player can sink
	p.global_position = Vector3(-100, 3.0, 0)
	p.velocity = Vector3.ZERO
	p.set_state(Player.S.AIR)
	await t.frames(60)
	t.check(p.in_water, "detects water")
	t.check(p.state == Player.S.SWIM or p.is_on_floor(), "enters swim state (%d)" % p.state)
	if p.state == Player.S.SWIM:
		p.scripted = t.inp({"move": Vector2(1, 0)})
		var x0 := p.global_position.x
		await t.frames(60)
		t.check(p.global_position.x > x0 + 3.0, "swims horizontally")
	p.scripted = t.inp()
	# --- hat throw and return
	p.global_position = Vector3(0, 0.05, 0)
	p.velocity = Vector3.ZERO
	p.set_state(Player.S.GROUND)
	await t.frames(10)
	p.scripted = t.inp({"throw_p": true})
	await t.frames(2)
	p.scripted = t.inp()
	t.check(p.hat != null and is_instance_valid(p.hat), "hat thrown")
	await t.frames(240)
	t.check(p.hat == null, "hat returned to Pip")
	# --- damage + invulnerability
	t.root.get_node("Game").health = 3
	p.invuln = 0.0
	p.hurt(Vector3(0, 0, 5), 1)
	t.check(t.root.get_node("Game").health == 2, "damage applied")
	p.hurt(Vector3(0, 0, 5), 1)
	t.check(t.root.get_node("Game").health == 2, "invulnerability prevents double hit")
	# --- fall into void respawns
	t.root.get_node("Game").health = 3
	p.checkpoint = Vector3(0, 2, 0)
	p.invuln = 0.0
	p.global_position = Vector3(500, -50, 500)
	await t.frames(5)
	t.check(p.global_position.distance_to(Vector3(0, 3, 0)) < 5.0, "void fall respawns at checkpoint (%s)" % str(p.global_position))
	w.queue_free()
	await t.frames(2)
