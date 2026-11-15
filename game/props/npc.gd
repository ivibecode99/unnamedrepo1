class_name Npc
extends Node3D
## Talkable character with branching-free dialogue, optional fetch quest and shop.
var npc_id := ""
var info: Dictionary
var player: Player
var vis: Node3D
var bubble: Label3D
var t := 0.0
var talking := false
var kingdom := "forest"

func _ready() -> void:
	info = NpcData.DATA[npc_id]
	add_to_group("interactable")
	add_to_group("npc")
	vis = Node3D.new()
	add_child(vis)
	_build()
	bubble = Build.label3d("...", Vector3(0, 2.6, 0), 0.6)
	bubble.visible = false
	add_child(bubble)
	var nm := Build.label3d(info["name"], Vector3(0, 2.2, 0), 0.35, Color(1, 1, 0.85))
	nm.name = "NameTag"
	add_child(nm)

func _build() -> void:
	var c: Color = info["color"]
	var look: String = info.get("look", "round")
	var h := hash(npc_id)
	match look:
		"tall":
			vis.add_child(Build.capsule(0.4, 1.5, c, Vector3(0, 0.85, 0)))
			vis.add_child(Build.sphere(0.38, c.lightened(0.2), Vector3(0, 1.85, 0)))
			Build.eyes(vis, 0.3, 1.9, 0.14, 0.1)
		"small":
			vis.add_child(Build.sphere(0.45, c, Vector3(0, 0.5, 0)))
			Build.eyes(vis, 0.38, 0.62, 0.17, 0.12)
		_:
			vis.add_child(Build.sphere(0.7, c, Vector3(0, 0.75, 0)))
			vis.add_child(Build.sphere(0.12, c.darkened(0.3), Vector3(0, 0.78, 0.7)))
			Build.eyes(vis, 0.58, 1.0, 0.22, 0.14)
	var top := 1.5 if look == "round" else (2.3 if look == "tall" else 1.0)
	match absi(h) % 5:
		0: vis.add_child(Build.cyl(0.0, 0.35, 0.5, c.darkened(0.4), Vector3(0, top + 0.1, 0)))
		1:
			vis.add_child(Build.cyl(0.04, 0.04, 0.4, Color(0.3, 0.3, 0.3), Vector3(0, top + 0.1, 0)))
			vis.add_child(Build.sphere(0.12, Color(1, 0.8, 0.2), Vector3(0, top + 0.35, 0), 0.5))
		2:
			for sx in [-1, 1]:
				vis.add_child(Build.sphere(0.16, c.lightened(0.15), Vector3(sx * 0.3, top - 0.05, 0)))
		3: vis.add_child(Build.cyl(0.4, 0.4, 0.12, Color(0.25, 0.2, 0.35), Vector3(0, top + 0.05, 0)))
		_: pass
	if info.has("quest"):
		vis.add_child(Build.label3d("!", Vector3(0, top + 0.7, 0), 0.9, Color(1, 0.9, 0.2)))
	if info.has("shop"):
		vis.add_child(Build.label3d("$", Vector3(0, top + 0.7, 0), 0.9, Color(0.4, 1, 0.5)))

func _hud() -> Node:
	return get_tree().get_first_node_in_group("hud")

func can_interact(p: Player) -> bool:
	return not talking and global_position.distance_to(p.global_position) < 3.0 and p.state != Player.S.CAPTURED

func _physics_process(delta: float) -> void:
	t += delta
	vis.position.y = sin(t * 2.0 + float(hash(npc_id) % 10)) * 0.04
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if ps.is_empty():
			return
		player = ps[0]
	var near := global_position.distance_to(player.global_position) < 3.2 and not talking
	bubble.visible = near
	if near:
		var d := player.global_position - global_position
		vis.rotation.y = lerp_angle(vis.rotation.y, atan2(d.x, d.z), minf(1.0, 6.0 * delta))

func interact(p: Player) -> void:
	if talking:
		return
	talking = true
	p.lock("talk")
	var hud := _hud()
	Audio.sfx("menu_ok")
	if hud:
		await hud.say(_lines(), info["name"])
	var reward := ""
	if info.has("quest"):
		var q: Dictionary = info["quest"]
		var item_id: String = q["star"] + "_item"
		if not Game.has_star(q["star"]) and item_id in Game.data["items"]:
			reward = q["star"]
			if hud:
				await hud.say(_arr(q["thanks"]), info["name"])
			Game.data["items"].erase(item_id)
			_spawn_reward(reward)
	if info.has("shop") and hud and reward == "":
		await hud.open_shop(info["shop"])
	talking = false
	if is_instance_valid(p):
		p.unlock()

func _arr(a: Array) -> Array:
	var out: Array = []
	for x in a:
		out.append([info["name"], x])
	return out

func _lines() -> Array:
	var out: Array = []
	if info.has("quest"):
		var q: Dictionary = info["quest"]
		var item_id: String = q["star"] + "_item"
		if Game.has_star(q["star"]):
			return _arr(q["after"])
		if item_id in Game.data["items"]:
			return _arr(info["lines"].slice(0, 1))
		out = _arr(info["lines"])
		out.append_array(_arr(q["ask"]))
		return out
	return _arr(info["lines"])

func _spawn_reward(star_id: String) -> void:
	var s := StarPickup.new()
	s.star_id = star_id
	get_parent().add_child(s)
	s.global_position = global_position + Vector3(0, 2.2, 0.8)
	Audio.sfx("win")
