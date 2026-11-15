extends RefCounted
## Capture system: throw Capt at a creature, control it, use its ability, release.
func run(t) -> void:
	var w = t.flat_world()
	var cam := CameraRig.new()
	cam.add_to_group("camera_rig")
	w.add_child(cam)
	var p: Player = t.make_player(w)
	cam.target = p
	p.cam = cam
	var hop := Capturable.new()
	hop.kind = "hopper"
	w.add_child(hop)
	hop.position = Vector3(0, 0.6, -4)
	await t.frames(20)
	t.check(hop.can_be_captured(), "hopper can be captured")
	p.dir_face = Vector3.FORWARD
	p.scripted = t.inp({"throw_p": true})
	await t.frames(1)
	p.scripted = t.inp()
	var got := false
	for i in 60:
		await t.frames(1)
		if p.state == Player.S.CAPTURED:
			got = true
			break
	t.check(got, "throwing Capt at creature captures it")
	t.check(hop.controlled, "creature now controlled")
	t.check(cam.target == hop, "camera follows creature")
	# controlled hop: jump height larger than Pip
	await t.frames(10)
	var y0 := hop.global_position.y
	hop.state_t = 1.0
	p.scripted = t.inp({"jump_p": true, "jump_h": true})
	await t.frames(1)
	p.scripted = t.inp({"jump_h": true})
	var peak := y0
	for i in 90:
		await t.frames(1)
		peak = maxf(peak, hop.global_position.y)
	var pip_h := Tuning.jump_height(Tuning.JUMP_V[2])
	t.check(peak - y0 > pip_h + 0.5, "hopper out-jumps Pip's triple jump (%.2f > %.2f)" % [peak - y0, pip_h])
	# movement
	p.scripted = t.inp({"move": Vector2(1, 0)})
	var x0 := hop.global_position.x
	await t.frames(40)
	t.check(hop.global_position.x > x0 + 2.0, "controlled creature moves")
	# release with throw button
	p.scripted = t.inp({"throw_p": true})
	await t.frames(1)
	p.scripted = t.inp()
	await t.frames(5)
	t.check(p.state != Player.S.CAPTURED and not hop.controlled, "release returns control to Pip")
	t.check(cam.target == p, "camera back on Pip")
	t.check(not hop.can_be_captured(), "release cooldown prevents instant recapture")
	# every creature kind can be built and controlled for a few frames without errors
	var kinds := CreatureData.DATA.keys()
	for k in kinds:
		var c := Capturable.new()
		c.kind = k
		w.add_child(c)
		c.position = Vector3(20, 0.6, 20)
		await t.frames(3)
		c.capture(p)
		p.scripted = t.inp({"move": Vector2(0, -1), "jump_p": true, "spin_p": true})
		await t.frames(3)
		p.scripted = t.inp({"move": Vector2(0, -1), "jump_h": true})
		await t.frames(8)
		t.check(c.controlled, "kind %s stays controlled" % k)
		c.release()
		await t.frames(2)
		c.queue_free()
		p.scripted = t.inp()
		await t.frames(2)
	# scarab dash is faster than normal speed
	var sc := Capturable.new()
	sc.kind = "scarab"
	w.add_child(sc)
	sc.position = Vector3(40, 0.6, 40)
	await t.frames(5)
	sc.capture(p)
	sc.state_t = 1.0
	p.scripted = t.inp({"move": Vector2(0, -1), "spin_p": true})
	await t.frames(1)
	p.scripted = t.inp({"move": Vector2(0, -1)})
	await t.frames(5)
	var sp := Vector2(sc.velocity.x, sc.velocity.z).length()
	t.check(sp > sc.info["speed"] * 1.8, "scarab dash speed %.1f" % sp)
	sc.release()
	# cannon launches Pip
	var cn := Capturable.new()
	cn.kind = "cannon"
	w.add_child(cn)
	cn.position = Vector3(60, 0.6, 60)
	await t.frames(5)
	cn.capture(p)
	cn.state_t = 1.0
	cn.aim_pitch = 1.0
	p.scripted = t.inp({"jump_p": true})
	await t.frames(1)
	p.scripted = t.inp()
	await t.frames(3)
	t.check(p.state == Player.S.AIR and p.velocity.length() > 20.0, "cannon fires Pip (v=%.1f)" % p.velocity.length())
	w.queue_free()
	await t.frames(2)
