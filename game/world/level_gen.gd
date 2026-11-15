class_name LevelGen
extends RefCounted
## Deterministic procedural kingdom builder. Same seed => same level (coin ids stay stable for saves).

var w: Node3D
var kid := "forest"
var kd: Dictionary
var pal: Dictionary
var theme := "forest"
var rng := RandomNumberGenerator.new()
var coin_n := 0
var spawn_pos := Vector3(0, 1.0, 6)
var arena_center := Vector3.ZERO
var arena: BossArena = null
var counts := {"coins": 0, "stars": 0, "npcs": 0, "enemies": 0, "creatures": 0}
var water_y := -9999.0

func _init(world: Node3D, kingdom: String) -> void:
	w = world
	kid = kingdom
	kd = Kingdoms.DATA[kid]
	pal = kd["pal"]
	theme = kd["theme"]
	rng.seed = int(kd["seed"])

static func pol(deg: float, dist: float, y := 0.0) -> Vector3:
	var a := deg_to_rad(deg)
	return Vector3(cos(a) * dist, y, sin(a) * dist)

func g(c := "ground") -> Color:
	return pal[c]

# ================================================================== entry
func build() -> void:
	match theme:
		"hub": _hub()
		"ocean": _ocean()
		"volcano": _volcano()
		"final": _final()
		_: _land()
	if theme != "hub":
		_common_pickups()

# ---------------------------------------------------------------- helpers
func star(id: String, pos: Vector3) -> StarPickup:
	var s := StarPickup.new()
	s.star_id = id
	w.add_child(s)
	s.position = pos
	counts["stars"] += 1
	return s

func coin(pos: Vector3, value := 1) -> void:
	var c := CoinPickup.new()
	c.kingdom = kid if kid != "hub" else "hub"
	c.value = value
	c.coin_id = "%s_c%d" % [kid, coin_n]
	coin_n += 1
	w.add_child(c)
	c.position = pos
	counts["coins"] += 1

func coin_line(a: Vector3, b: Vector3, n: int) -> void:
	for i in n:
		coin(a.lerp(b, float(i) / maxf(n - 1, 1)))

func coin_ring(center: Vector3, r: float, n: int) -> void:
	for i in n:
		var an := float(i) / n * TAU
		coin(center + Vector3(cos(an) * r, 0, sin(an) * r))

func npc(id: String, pos: Vector3, face_deg := 0.0) -> Npc:
	var n := Npc.new()
	n.npc_id = id
	n.kingdom = kid
	w.add_child(n)
	n.position = pos
	counts["npcs"] += 1
	return n

func enemy(kind: String, pos: Vector3) -> void:
	var e := Enemy.new()
	e.kind = kind
	e.kingdom = kid if kid != "final" else "volcano"
	w.add_child(e)
	e.position = pos + Vector3(0, 0.6, 0)
	counts["enemies"] += 1

func creature(kind: String, pos: Vector3) -> Capturable:
	var c := Capturable.new()
	c.kind = kind
	w.add_child(c)
	c.position = pos + Vector3(0, 0.6, 0)
	counts["creatures"] += 1
	return c

func crate(pos: Vector3, n := 3) -> void:
	var c := Crate.new()
	c.kingdom = kid if kid != "hub" else "hub"
	c.coins = n
	w.add_child(c)
	c.position = pos + Vector3(0, 0.6, 0)

func spring(pos: Vector3, power := 26.0) -> void:
	var s := Spring.new()
	s.power = power
	w.add_child(s)
	s.position = pos

func checkpoint(pos: Vector3) -> void:
	var c := Checkpoint.new()
	w.add_child(c)
	c.position = pos

func box(pos: Vector3, size: Vector3, c: Color, group := "") -> StaticBody3D:
	return Build.solid_box(w, pos, size, c, group)

func cylinder(pos: Vector3, r: float, h: float, c: Color, group := "") -> StaticBody3D:
	return Build.solid_cyl(w, pos, r, h, c, group)

func moving(from: Vector3, to: Vector3, period := 4.0, size := Vector3(3.5, 0.5, 3.5), phase := 0.0) -> void:
	var m := MovingPlatform.new()
	m.from_pos = from
	m.to_pos = to
	m.period = period
	m.size = size
	m.phase = phase
	m.color = g("accent")
	w.add_child(m)

func sign_at(pos: Vector3, text: String) -> void:
	var s := InfoSign.new()
	s.text = text
	w.add_child(s)
	s.position = pos

func tree(pos: Vector3, scale := 1.0) -> void:
	var trunk_c := Color(0.5, 0.33, 0.2)
	var leaf := g("ground").darkened(0.15)
	var sb := cylinder(pos + Vector3(0, 1.5 * scale, 0), 0.4 * scale, 3.0 * scale, trunk_c)
	sb.add_child(Build.sphere(1.8 * scale, leaf, Vector3(0, 2.2 * scale, 0)))

func scatter(count: int, min_d: float, max_d: float, fn: Callable) -> void:
	for i in count:
		var p := pol(rng.randf() * 360.0, rng.randf_range(min_d, max_d))
		var tooclose := false
		for avoid in _avoid:
			if Vector2(p.x - avoid.x, p.z - avoid.z).length() < 6.0:
				tooclose = true
		if not tooclose:
			fn.call(p)

var _avoid: Array = []

# ---------------------------------------------------------------- challenge builders
## Ascending spiral of platforms; returns the top position.
func spiral_tower(base: Vector3, steps: int, radius := 5.0, rise := 1.8, size := 3.4, moving_every := 0) -> Vector3:
	var top := base
	for i in steps:
		var a := i * 0.75
		var p := base + Vector3(cos(a) * radius, 0.0 + (i + 1) * rise, sin(a) * radius)
		if moving_every > 0 and i % moving_every == moving_every - 1:
			moving(p - Vector3(2.5, 0, 0), p + Vector3(2.5, 0, 0), 3.2, Vector3(3.0, 0.5, 3.0), i * 0.7)
		else:
			box(p, Vector3(size, 0.6, size), g("accent") if i % 2 == 0 else g("ground2"))
		if i % 2 == 0:
			coin(p + Vector3(0, 1.2, 0))
		top = p
	box(top + Vector3(0, 0.0, 0) + Vector3(cos((steps) * 0.75) * radius, 1.8, sin((steps) * 0.75) * radius), Vector3(5, 0.7, 5), Color(1.0, 0.85, 0.3))
	return top + Vector3(cos(steps * 0.75) * radius, 1.8, sin(steps * 0.75) * radius) + Vector3(0, 1.8, 0)

## Row of small platforms over a gap (void or hazard) ending at a platform with a star.
func gap_course(start: Vector3, dir_deg: float, n: int, spacing: float, hazard := "") -> Vector3:
	var d := pol(dir_deg, 1.0)
	var p := start
	for i in n:
		p = start + d * spacing * (i + 1) + Vector3(0, sin(i * 1.3) * 0.8, 0)
		var sz := 3.0 if i % 3 != 2 else 2.2
		if i % 4 == 3:
			moving(p, p + Vector3(-d.z, 0, d.x) * 3.5, 3.0 + i * 0.1, Vector3(2.8, 0.5, 2.8), i)
		else:
			box(p, Vector3(sz, 0.6, sz), g("accent") if i % 2 == 0 else g("ground2"))
		if i % 2 == 1:
			coin(p + Vector3(0, 1.3, 0))
	var end := p + d * (spacing + 1.5)
	box(end, Vector3(6, 0.7, 6), Color(1.0, 0.85, 0.3))
	return end + Vector3(0, 1.6, 0)

func hill(pos: Vector3, r: float, tiers: int, c: Color) -> void:
	for i in tiers:
		cylinder(pos + Vector3(0, 0.9 * (i + 1) - 0.45, 0), r * (1.0 - i * 0.28), 1.8 + 0.0, c.lightened(i * 0.05))

func make_arena(center: Vector3, boss_id: String) -> void:
	arena_center = center
	cylinder(center + Vector3(0, -0.45, 0), 17.0, 1.0, g("ground2").lightened(0.1))
	for i in 10:
		var a := i / 10.0 * TAU
		var p := center + Vector3(cos(a) * 16.4, 1.5, sin(a) * 16.4)
		cylinder(p, 0.7, 3.0, g("accent"))
	arena = BossArena.new()
	arena.boss_id = boss_id
	arena.kingdom = kid
	arena.center = center
	w.add_child(arena)
	arena.position = center
	arena.setup()

# ================================================================== LAND (forest/desert/city/snow)
func _land() -> void:
	# main island
	var top := cylinder(Vector3(0, -3.0, 0), 66.0, 6.0, g())
	top.add_child(Build.cyl(0.0, 66.0, 20.0, g("ground2"), Vector3(0, -13, 0)))
	# spawn plaza
	cylinder(Vector3(0, -0.45, 0), 14.0, 0.9, g().lightened(0.12))
	spawn_pos = Vector3(0, 1.0, 5.0)
	_avoid.append(Vector3(0, 0, 0))
	checkpoint(Vector3(-4, 0, 6))
	sign_at(pol(-60, 7.0), _sign_text())
	_beacon(Vector3(7, 0, 5))
	# NPCs ring around plaza
	var ids: Array = kd["npcs"]
	for i in ids.size():
		var a := 20.0 + i * (320.0 / maxi(ids.size(), 1))
		var p := pol(a, 9.5 + (i % 2) * 2.5)
		npc(ids[i], p)
		_avoid.append(p)
	# towers & courses
	var tower_pos := pol(30, 44)
	var top_pos := spiral_tower(tower_pos, 9, 5.2, 1.8, 3.6, 4)
	star(kid + "_tower", top_pos)
	checkpoint(tower_pos + Vector3(-3, 0, 3))
	_avoid.append(tower_pos)
	var gap_start := pol(150, 36)
	cylinder(gap_start + Vector3(0, -0.4, 0), 4.0, 0.9, g("ground2"))
	var gend := gap_course(gap_start + Vector3(0, 0, 0), 175.0, 7, 5.0)
	star(kid + "_gap", gend)
	_avoid.append(gap_start)
	# hidden stars
	var h1 := pol(215, 52)
	for i in 3:
		var rp := h1 + pol(i * 120.0, 3.2)
		cylinder(rp + Vector3(0, 2.0, 0), 1.8, 4.0, g("ground2").darkened(0.15))
	star(kid + "_hidden1", h1 + Vector3(0, 1.2, 0))
	var h2 := pol(325, 54, 7.0)
	for i in 3:
		box(pol(325, 40 + i * 5.0, 1.5 + i * 2.2), Vector3(3.4, 0.6, 3.4), g("accent"))
	box(h2 + Vector3(0, -0.4, 0), Vector3(4.5, 0.8, 4.5), g("ground2"))
	star(kid + "_hidden2", h2 + Vector3(0, 1.3, 0))
	# capture challenge
	_capture_site(pol(95, 38))
	# boss arena
	if kd["boss"] != "":
		make_arena(pol(270, 50), kd["boss"])
		checkpoint(pol(270, 30))
	# quests
	_quests(pol(60, 26), pol(300, 28))
	# theme dressing
	_theme_dressing()
	# enemies and crates
	var ekinds: Array = kd["enemies"]
	scatter(11, 16, 54, func(p): enemy(ekinds[rng.randi() % ekinds.size()], p))
	scatter(7, 8, 50, func(p): crate(p, 3))
	scatter(3, 12, 40, func(p): spring(p))
	for kind in kd["creatures"]:
		var p := pol(rng.randf() * 360.0, rng.randf_range(14, 34))
		creature(kind, p)
	# extra coin trails
	for i in 5:
		var a := i * 72.0 + 15.0
		coin_line(pol(a, 18, 0.8), pol(a + 20.0, 34, 0.8), 8)
	for i in 4:
		coin_ring(pol(i * 90.0 + 45.0, 24, 0.8), 3.0, 8)

func _beacon(pos: Vector3) -> void:
	var b := ReturnBeacon.new()
	w.add_child(b)
	b.position = pos

func _sign_text() -> String:
	return "Welcome to %s! Collect Stars, coins, and make friends. Talk to people with the jump button. Capt can grab creatures with a throw!" % kd["name"]

func _quests(pa: Vector3, pb: Vector3) -> void:
	if not kd.has("quests"):
		return
	var qs: Dictionary = kd["quests"]
	var keys := ["quest1", "quest2"]
	var positions := [pa, pb]
	for i in 2:
		var q: Dictionary = qs[keys[i]]
		var star_id: String = kid + "_" + keys[i]
		var item := QuestItem.new()
		item.item_id = star_id + "_item"
		item.item_name = q["item"]
		w.add_child(item)
		item.position = positions[i] + Vector3(0, 1.0, 0)
		cylinder(positions[i] + Vector3(0, 0.25, 0), 1.2, 0.5, g("ground2").darkened(0.2))
		coin_ring(positions[i] + Vector3(0, 0.8, 0), 3.0, 6)

func _capture_site(center: Vector3) -> void:
	var ck: String = kd["capture_kind"]
	var sid := kid + "_capture"
	checkpoint(center + Vector3(0, 0, -4))
	match ck:
		"hopper", "springbot", "jelly":
			# tall pillar with the star on top; only a high-jump/flying creature gets there
			cylinder(center + Vector3(6, 4.0, 0), 2.2, 8.0, g("ground2").darkened(0.2), "nowall")
			star(sid, center + Vector3(6, 9.3, 0))
			creature(ck, center + Vector3(-2, 0, 0))
		"scarab", "penguin":
			# wide gap that only a dashing/sliding creature can clear
			cylinder(center + Vector3(0, -0.4, 0), 4.5, 0.9, g("ground2"))
			var land := center + Vector3(0, 0, 22.0)
			cylinder(land + Vector3(0, -0.4, 0), 4.5, 0.9, g("ground2"))
			star(sid, land + Vector3(0, 1.5, 0))
			creature(ck, center + Vector3(0, 0, -2))
			_ramp(center + Vector3(0, 0, 4.0))
			if ck == "penguin":
				var ice := box(center + Vector3(0, -0.45, 2.0), Vector3(8, 0.9, 8), Color(0.65, 0.85, 1.0), "ice")
		"lavagolem":
			var hz := Hazard.new()
			hz.kind = "lava"
			hz.size = Vector3(30, 1, 30)
			w.add_child(hz)
			hz.position = center + Vector3(0, -0.2, 0)
			cylinder(center + Vector3(-17.5, -0.4, 0), 4.0, 0.9, g("ground2"))
			cylinder(center + Vector3(0, 0.1, 0), 3.5, 1.2, g("ground2"))
			star(sid, center + Vector3(0, 2.0, 0))
			creature(ck, center + Vector3(-17.5, 0, 0))
		_:
			star(sid, center + Vector3(0, 1.5, 0))
			creature(ck, center)

func _ramp(pos: Vector3) -> void:
	var r := box(pos + Vector3(0, 0.3, 0), Vector3(4.5, 0.6, 3.0), g("accent"))
	r.rotation_degrees.x = -12.0

func _common_pickups() -> void:
	pass

func _theme_dressing() -> void:
	match theme:
		"forest":
			scatter(70, 8, 62, func(p): tree(p, rng.randf_range(0.8, 1.7)))
			scatter(10, 12, 55, func(p):
				var cap := cylinder(p + Vector3(0, 0.9, 0), 1.6, 0.4, Color(0.9, 0.2, 0.25))
				cap.position.y = 1.6
				cylinder(p + Vector3(0, 0.6, 0), 0.5, 1.2, Color(0.95, 0.9, 0.8)))
			scatter(14, 10, 58, func(p):
				cylinder(p + Vector3(0, 0.4, 0), 1.0, 0.8, Color(0.5, 0.35, 0.2)))
		"desert":
			scatter(40, 10, 62, func(p):
				var c := cylinder(p + Vector3(0, 1.3, 0), 0.45, 2.6, Color(0.3, 0.65, 0.3))
				c.add_child(Build.capsule(0.2, 1.0, Color(0.3, 0.65, 0.3), Vector3(0.7, 0.4, 0)))
				c.add_child(Build.capsule(0.2, 1.0, Color(0.3, 0.65, 0.3), Vector3(-0.7, 0.7, 0))))
			# pyramid
			var pp := pol(200, 30)
			for i in 5:
				box(pp + Vector3(0, 0.8 + i * 1.6, 0), Vector3(14 - i * 2.8, 1.6, 14 - i * 2.8), Color(0.9, 0.75, 0.45).darkened(i * 0.03))
			_avoid.append(pp)
			# quicksand
			for i in 4:
				var hz := Hazard.new()
				hz.kind = "quicksand"
				hz.size = Vector3(9, 0.4, 9)
				w.add_child(hz)
				hz.position = pol(60 + i * 90.0, 22, -0.1)
			scatter(18, 20, 60, func(p): hill(p, 3.4, 2, g("ground").darkened(0.05)))
		"city":
			scatter(34, 14, 60, func(p):
				var h := rng.randf_range(5.0, 18.0)
				var s := rng.randf_range(4.0, 7.0)
				var b := box(p + Vector3(0, h * 0.5, 0), Vector3(s, h, s), Color.from_hsv(rng.randf(), 0.25, 0.8))
				# windows
				for i in int(h / 3.0):
					b.add_child(Build.box(Vector3(s * 0.7, 0.8, s + 0.05), Color(1.0, 0.95, 0.6), Vector3(0, -h * 0.5 + 2.0 + i * 3.0, 0), 0.6)))
			scatter(18, 10, 58, func(p):
				cylinder(p + Vector3(0, 2.0, 0), 0.15, 4.0, Color(0.3, 0.3, 0.35))
				w.add_child(Build.sphere(0.35, Color(1, 0.95, 0.6), p + Vector3(0, 4.2, 0), 1.0)))
		"snow":
			scatter(55, 8, 62, func(p):
				var t := cylinder(p + Vector3(0, 1.4, 0), 0.35, 2.8, Color(0.45, 0.32, 0.2))
				t.add_child(Build.cyl(0.0, 1.6, 2.2, Color(0.15, 0.5, 0.35), Vector3(0, 2.2, 0)))
				t.add_child(Build.cyl(0.0, 1.1, 1.6, Color(0.95, 0.98, 1.0), Vector3(0, 3.2, 0))))
			for i in 5:
				var ip := pol(i * 72.0 + 20.0, 26.0)
				box(ip + Vector3(0, -0.42, 0), Vector3(9, 0.9, 9), Color(0.65, 0.85, 1.0), "ice")
			scatter(5, 14, 48, func(p):
				var wall := box(p + Vector3(0, 1.8, 0), Vector3(3.2, 3.6, 1.0), Color(0.7, 0.9, 1.0))
				wall.add_to_group("ice_wall")
				wall.set_script(preload("res://props/ice_wall.gd")))
			scatter(6, 12, 50, func(p):
				var sm := cylinder(p + Vector3(0, 0.6, 0), 0.9, 1.2, Color.WHITE)
				sm.add_child(Build.sphere(0.65, Color.WHITE, Vector3(0, 1.0, 0)))
				sm.add_child(Build.prism(Vector3(0.12, 0.45, 0.12), Color(1, 0.5, 0.1), Vector3(0, 1.0, 0.65))))

# ================================================================== HUB (airship)
func _hub() -> void:
	var wood := Color(0.62, 0.42, 0.26)
	var deck := box(Vector3(0, -0.5, 0), Vector3(46, 1.0, 14), wood)
	deck.add_child(Build.sphere(9.0, Color(0.95, 0.9, 0.8), Vector3(0, 12, 0)))
	# bow and stern
	box(Vector3(26, -0.5, 0), Vector3(8, 1.0, 8), wood.lightened(0.1))
	box(Vector3(-26, -0.5, 0), Vector3(8, 1.0, 8), wood.lightened(0.1))
	# railings
	for side in [-1, 1]:
		box(Vector3(0, 0.6, side * 7.2), Vector3(46, 1.4, 0.4), wood.darkened(0.2))
		for i in 12:
			box(Vector3(-22 + i * 4.0, 1.0, side * 7.2), Vector3(0.4, 2.2, 0.5), wood.lightened(0.2))
	# balloon (decor, up high)
	var bal := Build.sphere(14.0, Color(0.9, 0.25, 0.3), Vector3(0, 30, 0))
	bal.scale = Vector3(2.2, 1.0, 1.2)
	w.add_child(bal)
	for sx in [-8, 8]:
		w.add_child(Build.cyl(0.08, 0.08, 20.0, Color(0.9, 0.8, 0.5), Vector3(sx, 13.0, 0)))
	# mast + crow's nest (hidden star)
	var mast := cylinder(Vector3(-14, 5.0, 0), 0.5, 10.0, wood.darkened(0.3), "nowall")
	for i in 4:
		box(Vector3(-17.5 + i * -0.0, 1.2 + i * 1.8, -3.0 + i * 0.0 + 6.0 * 0.0), Vector3(2.5, 0.5, 2.5), wood.lightened(0.15))
	# cargo crates stair up to the nest
	box(Vector3(-17, 0.8, 4.5), Vector3(2.2, 1.6, 2.2), wood.lightened(0.25))
	box(Vector3(-14.5, 1.9, 4.5), Vector3(2.2, 0.5, 2.2), wood.lightened(0.2))
	box(Vector3(-12.0, 3.1, 4.5), Vector3(2.2, 0.5, 2.2), wood.lightened(0.2))
	box(Vector3(-11.8, 4.7, 1.8), Vector3(2.2, 0.5, 2.2), wood.lightened(0.2))
	box(Vector3(-12.5, 6.3, -1.0), Vector3(2.2, 0.5, 2.2), wood.lightened(0.2))
	box(Vector3(-14.0, 7.9, -1.5), Vector3(4.0, 0.5, 4.0), Color(0.9, 0.7, 0.3))
	star("hub_deck", Vector3(-14.0, 9.4, -1.5))
	spawn_pos = Vector3(2, 1.0, 3.0)
	_beacon_hub()
	# map table
	var mt := MapTable.new()
	w.add_child(mt)
	mt.position = Vector3(4, 0, 0)
	# NPCs
	var ids: Array = kd["npcs"]
	var spots := [Vector3(-3, 0, -3.5), Vector3(8, 0, -3.5), Vector3(14, 0, 3.0), Vector3(-6, 0, 3.5), Vector3(-9, 0, -4.0), Vector3(18, 0, -2.0), Vector3(22, 0, 3.0)]
	for i in ids.size():
		npc(ids[i], spots[i])
	# quest items
	var items := [["hub_cat", "Cat Treat", Vector3(27, 0.8, 0)], ["hub_soup", "Soup Ladle", Vector3(-27, 0.8, 0)]]
	for it in items:
		var qi := QuestItem.new()
		qi.item_id = it[0] + "_item"
		qi.item_name = it[1]
		w.add_child(qi)
		qi.position = it[2]
	for i in 6:
		coin(Vector3(-20 + i * 8.0, 0.9, 0))
	checkpoint(Vector3(1, 0, 4))

func _beacon_hub() -> void:
	pass

# ================================================================== OCEAN
func _ocean() -> void:
	var sand := g()
	# water volume
	var wt := Water.new()
	wt.size = Vector3(220, 11, 220)
	w.add_child(wt)
	wt.position = Vector3(0, -6.5, 0)      # surface at -1.0
	water_y = -1.0
	box(Vector3(0, -12.5, 0), Vector3(240, 2.0, 240), sand.darkened(0.3))   # sea floor
	# central island
	cylinder(Vector3(0, -6.0, 0), 28.0, 12.0, sand)
	cylinder(Vector3(0, -0.45, 0), 12.0, 0.9, sand.lightened(0.12))
	spawn_pos = Vector3(0, 1.0, 5.0)
	checkpoint(Vector3(-4, 0, 6))
	sign_at(pol(-60, 7.0), _sign_text() + " Swim with jump to rise and crouch to dive!")
	_beacon(Vector3(7, 0, 5))
	var ids: Array = kd["npcs"]
	for i in ids.size():
		npc(ids[i], pol(20.0 + i * 55.0, 8.5 + (i % 2) * 3.0))
	for i in 12:
		var a := rng.randf() * 360.0
		var p := pol(a, rng.randf_range(10, 25))
		var pm := cylinder(p + Vector3(0, 1.2, 0), 0.35, 2.4, Color(0.55, 0.38, 0.22))
		pm.add_child(Build.sphere(1.3, Color(0.25, 0.7, 0.35), Vector3(0, 1.6, 0)))
	# islets
	var islets := [[30, 48], [95, 50], [160, 52], [215, 54], [330, 50], [270, 58]]
	for isl in islets:
		var ip: Vector3 = pol(isl[0], isl[1])
		cylinder(ip + Vector3(0, -6.0, 0), 8.0, 12.0, sand)
		# stepping buoys from main island
		for k in range(1, 5):
			var bp := pol(isl[0], 28.0 + k * ((isl[1] - 36.0) / 5.0))
			cylinder(bp + Vector3(0, -1.0, 0), 1.6, 1.6, Color(0.95, 0.35, 0.3) if k % 2 == 0 else Color.WHITE)
	# tower (lighthouse) on islet 0
	var lt := pol(30, 48)
	var lh := cylinder(lt + Vector3(0, 6.0, 0), 2.5, 12.0, Color.WHITE, "nowall")
	lh.add_child(Build.cyl(2.51, 2.51, 2.0, Color(0.9, 0.2, 0.2), Vector3(0, 3, 0)))
	var tp := spiral_tower(lt + Vector3(8, 0, 0), 9, 4.5, 1.6, 3.4, 4)
	star("ocean_tower", tp)
	# buoy bounce course
	var gs := pol(160, 52)
	var gend := gap_course(gs, 180.0, 7, 5.0)
	star("ocean_gap", gend)
	# hidden: sunken chest
	var chest := pol(215, 54)
	star("ocean_hidden1", Vector3(chest.x + 5, -9.5, chest.z))
	box(Vector3(chest.x + 5, -10.4, chest.z), Vector3(2.0, 1.0, 1.4), Color(0.7, 0.5, 0.15))
	# hidden: kelp
	var kelp := pol(330, 50)
	for i in 9:
		var kp := kelp + pol(i * 40.0, 3.0)
		w.add_child(Build.capsule(0.3, 4.0, Color(0.15, 0.55, 0.3), kp + Vector3(0, -6.0, 0)))
	star("ocean_hidden2", kelp + Vector3(0, -7.0, 0))
	# capture: jelly pillar
	var cp := pol(95, 50)
	cylinder(cp + Vector3(6, 4.0, 0), 2.2, 10.0, g("ground2").darkened(0.2), "nowall")
	star("ocean_capture", cp + Vector3(6, 9.8, 0))
	creature("jelly", cp + Vector3(-2, 0, 0))
	creature("crab", pol(60, 20))
	creature("angler", pol(40, 22))
	checkpoint(cp + Vector3(0, 0, -4))
	# boss: arena on an islet
	var ac := pol(270, 62)
	cylinder(ac + Vector3(0, -6.5, 0), 22.0, 13.0, sand.darkened(0.1))
	for k in range(1, 6):
		var bp := pol(270, 28.0 + k * 5.0)
		cylinder(bp + Vector3(0, -1.0, 0), 1.6, 1.6, Color(0.95, 0.35, 0.3) if k % 2 == 0 else Color.WHITE)
	make_arena(ac, "brinebeard")
	checkpoint(pol(270, 31))
	_quests(pol(60, 22), pol(300, 22))
	for i in 7:
		enemy("walker" if i % 2 == 0 else "shooter", pol(i * 51.0, 18.0))
	scatter(6, 8, 24, func(p): crate(p, 3))
	for i in 5:
		coin_ring(pol(i * 72.0, 18, 0.8), 3.0, 8)
	for i in 8:
		coin(pol(i * 45.0, 40.0, -4.0))

# ================================================================== VOLCANO (sky + lava)
func _volcano() -> void:
	var rock := g()
	var hz := Hazard.new()
	hz.kind = "lava"
	hz.size = Vector3(260, 2, 260)
	w.add_child(hz)
	hz.position = Vector3(0, -8.0, 0)
	cylinder(Vector3(0, -3.0, 0), 20.0, 6.0, rock)
	cylinder(Vector3(0, -0.45, 0), 9.0, 0.9, rock.lightened(0.1))
	spawn_pos = Vector3(0, 1.0, 5.0)
	checkpoint(Vector3(-4, 0, 6))
	sign_at(pol(-60, 7.0), _sign_text() + " The floor is lava. Really.")
	_beacon(Vector3(7, 0, 5))
	var ids: Array = kd["npcs"]
	for i in ids.size():
		npc(ids[i], pol(20.0 + i * 55.0, 8.5 + (i % 2) * 3.0))
	# summit spiral tower (main objective), then separate challenge courses
	var base := pol(90, 46)
	cylinder(base + Vector3(0, -3.0, 0), 8.0, 6.0, rock)
	for k in range(1, 5):
		box(pol(90, 20.0 + k * 5.5, 0.0), Vector3(3.6, 0.6, 3.6), g("accent") if k % 2 else rock.lightened(0.1))
	var summit := spiral_tower(base, 14, 5.0, 2.4, 3.4, 5)
	star("volcano_summit", summit + Vector3(0, 2.0, 0))
	checkpoint(base + Vector3(-3, 0, 0))
	# tower challenge: obsidian climb
	var b2 := pol(210, 46)
	cylinder(b2 + Vector3(0, -3.0, 0), 8.0, 6.0, rock)
	for k in range(1, 5):
		box(pol(210, 20.0 + k * 5.5, 0.0), Vector3(3.6, 0.6, 3.6), rock.lightened(0.1))
	var tp := spiral_tower(b2, 10, 4.5, 2.0, 3.4, 4)
	star("volcano_tower", tp)
	checkpoint(b2 + Vector3(-3, 0, 0))
	# gap: lava lap gauntlet
	var gs := pol(330, 24)
	for k in range(1, 4):
		box(pol(330, 20.0 + k * 4.0, 0.0), Vector3(3.4, 0.6, 3.4), rock.lightened(0.1))
	var gend := gap_course(gs + pol(330, 14), 330.0, 8, 5.0)
	star("volcano_gap", gend)
	# hidden crater
	var hp := pol(150, 52)
	cylinder(hp + Vector3(0, -3.0, 0), 9.0, 6.0, rock)
	for k in range(1, 5):
		box(pol(150, 20.0 + k * 5.5, 0.0), Vector3(3.6, 0.6, 3.6), rock.lightened(0.1))
	for i in 6:
		cylinder(hp + pol(i * 60.0, 5.0) + Vector3(0, 2.5, 0), 1.2, 5.0, Color(0.15, 0.1, 0.15))
	star("volcano_hidden1", hp + Vector3(0, 1.3, 0))
	# hidden cloud nine: high above, reached by geyser springs
	var cn := pol(30, 40, 13.0)
	spring(pol(30, 36.0), 34.0)
	box(pol(30, 30.0, 0.0), Vector3(5, 0.6, 5), rock.lightened(0.15))
	box(cn + Vector3(0, -0.4, 0), Vector3(5, 0.8, 5), Color(0.95, 0.95, 1.0))
	star("volcano_hidden2", cn + Vector3(0, 1.3, 0))
	# capture: lava golem island
	_capture_site(pol(270, 22))
	_quests(pol(60, 22), pol(300, 22))
	for i in 6:
		enemy("walker" if i % 2 == 0 else "shooter", pol(i * 60.0 + 10, 14.0))
	for k in kd["creatures"]:
		if k != "lavagolem":
			creature(k, pol(rng.randf() * 360.0, 12.0))
	scatter(5, 6, 16, func(p): crate(p, 3))
	scatter(4, 8, 17, func(p): spring(p))
	for i in 5:
		coin_ring(pol(i * 72.0, 14, 0.8), 3.0, 8)

# ================================================================== FINAL
func _final() -> void:
	var stone := g()
	cylinder(Vector3(0, -0.5, 0), 12.0, 1.0, stone)
	spawn_pos = Vector3(0, 1.0, 3.0)
	checkpoint(Vector3(-3, 0, 4))
	_beacon(Vector3(5, 0, 5))
	npc("tinny", Vector3(6, 0, -4))
	var hz := Hazard.new()
	hz.kind = "lava"
	hz.size = Vector3(300, 2, 300)
	w.add_child(hz)
	hz.position = Vector3(0, -12.0, 0)
	# gauntlet path along -Z with a mix of platforms, moving platforms, springs, and enemies
	var z := -10.0
	for seg in 12:
		match seg % 4:
			0:
				for i in 4:
					box(Vector3(sin(i * 1.2) * 3.0, 0, z - i * 5.0), Vector3(3.2, 0.6, 3.2), g("accent") if i % 2 else stone.lightened(0.2))
					coin(Vector3(sin(i * 1.2) * 3.0, 1.4, z - i * 5.0))
				z -= 20.0
			1:
				moving(Vector3(-4, 0, z), Vector3(4, 0, z), 3.0, Vector3(3.5, 0.6, 3.5), seg)
				box(Vector3(0, 0, z - 8.0), Vector3(6, 0.6, 6), stone.lightened(0.15))
				enemy("charger", Vector3(0, 0.3, z - 8.0))
				coin_line(Vector3(-4, 1.3, z), Vector3(4, 1.3, z), 5)
				z -= 14.0
			2:
				spring(Vector3(0, 0.2, z))
				box(Vector3(0, 0, z), Vector3(3.0, 0.6, 3.0), stone)
				for i in 3:
					box(Vector3(0, 7.0 + i * 2.0, z - 8.0 - i * 6.0), Vector3(3.4, 0.6, 3.4), g("accent"))
					coin(Vector3(0, 8.4 + i * 2.0, z - 8.0 - i * 6.0))
				box(Vector3(0, 0, z - 28.0), Vector3(6, 0.6, 6), stone.lightened(0.15))
				z -= 28.0
			3:
				box(Vector3(0, 0, z - 4.0), Vector3(9, 0.6, 9), stone.lightened(0.1))
				enemy("shooter", Vector3(-3, 0.3, z - 4.0))
				enemy("walker", Vector3(3, 0.3, z - 4.0))
				crate(Vector3(0, 0.3, z - 4.0), 5)
				if seg == 7:
					checkpoint(Vector3(0, 0.3, z - 2.0))
				z -= 12.0
	# secret: Encore
	var sp := Vector3(30, 8.0, -60)
	for i in 4:
		box(Vector3(8 + i * 6.0, 2.0 + i * 1.8, -50 - i * 3.0), Vector3(3.2, 0.6, 3.2), g("accent"))
	box(sp + Vector3(0, -0.4, 0), Vector3(5, 0.8, 5), Color(1.0, 0.85, 0.3))
	star("final_secret", sp + Vector3(0, 1.3, 0))
	# boss arena at end
	var ac := Vector3(0, 0, z - 28.0)
	box(Vector3(0, 0, z - 12.0), Vector3(6, 0.6, 14), stone.lightened(0.2))
	make_arena(ac, "baron")
	checkpoint(Vector3(0, 0.3, z - 10.0))
	# decorative giant gears
	for i in 8:
		var gear := Build.torus(6.0, 8.0, g("ground2").lightened(0.1), Vector3(rng.randf_range(-40, 40), rng.randf_range(10, 30), rng.randf_range(-120, 0)))
		gear.rotation_degrees.x = 90
		w.add_child(gear)
