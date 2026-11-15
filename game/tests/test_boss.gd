extends RefCounted
func run(t) -> void:
	for id in BossData.DATA:
		var w = t.flat_world()
		var cam := CameraRig.new()
		cam.add_to_group("camera_rig")
		w.add_child(cam)
		var p: Player = t.make_player(w, Vector3(0, 0.1, 8))
		p.cam = cam
		cam.target = p
		var b := Boss.new()
		b.boss_id = id
		b.arena_center = Vector3.ZERO
		w.add_child(b)
		b.position = Vector3(0, 0.6, -4)
		var info: Dictionary = BossData.DATA[id]
		var phases: int = info["phases"].size()
		t.check(b.total_hp == phases * 3, "%s total hp = %d" % [id, phases * 3])
		var defeated := [false]
		var phase_changes := [0]
		b.defeated.connect(func(): defeated[0] = true)
		b.phase_changed.connect(func(n): phase_changes[0] += 1)
		b.activate()
		await t.frames(20)
		# let it cycle through each attack of each phase and make sure nothing crashes; invulnerable Pip
		var seen := {}
		var guard := 0
		while not defeated[0] and guard < 5000:
			t.root.get_node("Game").health = 3
			p.invuln = 5.0
			if b.state == "attack":
				seen[b.attack] = true
			if b.state == "exhausted" and b.invuln <= 0.0:
				b.take_hit(1)
			await t.frames(2)
			guard += 2
		t.check(defeated[0], "%s can be defeated by 3 hits per phase (frames=%d)" % [id, guard])
		t.check(phase_changes[0] == phases - 1, "%s has %d phase transitions (%d)" % [id, phases - 1, phase_changes[0]])
		var union := {}
		for ph in info["phases"]:
			for a in ph["attacks"]:
				union[a] = true
		t.check(seen.size() >= 2, "%s used several attack types: %s" % [id, str(seen.keys())])
		# attacks differ between phases (distinct phases)
		t.check(info["phases"][0]["attacks"] != info["phases"][phases - 1]["attacks"], id + " phases have different attack sets")
		w.queue_free()
		await t.frames(3)
