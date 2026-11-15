class_name BossArena
extends Node3D
## Triggers the boss fight, shows cutscene lines, seals the arena and rewards the Star.
var boss_id := "mogul"
var kingdom := "forest"
var center := Vector3.ZERO
var boss: Boss
var started := false
var finished := false
var barrier: Node3D
var player: Player
var star_id := ""

func setup() -> void:
	for s in Kingdoms.DATA[kingdom]["stars"]:
		if s["kind"] == "boss":
			star_id = s["id"]
	if Game.boss_defeated(boss_id):
		finished = true
		var sp := StarPickup.new()
		sp.star_id = star_id
		get_parent().add_child(sp)
		sp.global_position = center + Vector3(0, 1.8, 0)
		return
	_spawn_boss()

func _spawn_boss() -> void:
	boss = Boss.new()
	boss.boss_id = boss_id
	boss.arena_center = center
	boss.arena_radius = 17.0
	get_parent().add_child(boss)
	boss.global_position = center + Vector3(0, 0.6, -5)
	boss.defeated.connect(_on_defeated)
	boss.hp_changed.connect(_on_hp)

func _on_hp(cur: int, total: int) -> void:
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.update_boss(cur, total)

func _physics_process(delta: float) -> void:
	if finished or started or boss == null or not is_instance_valid(boss):
		return
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if ps.is_empty():
			return
		player = ps[0]
	var d := player.global_position - center
	if Vector2(d.x, d.z).length() < 12.0 and player.state in [Player.S.GROUND, Player.S.AIR, Player.S.LONGJUMP] and player.is_on_floor():
		start_fight()

func start_fight() -> void:
	if started:
		return
	started = true
	var hud := get_tree().get_first_node_in_group("hud")
	player.lock("cutscene")
	if hud:
		var intro: Array = Cutscenes.BOSS_INTRO.get(boss_id, [])
		await hud.say(intro + [["", "BOSS: " + boss.info["name"] + " — " + boss.info["intro"]]])
	if not is_instance_valid(player):
		return
	player.unlock()
	_make_barrier()
	boss.activate()
	Audio.play_music("finalboss" if boss_id == "baron" else "boss")
	if hud:
		hud.show_boss(boss.info["name"], boss.total_hp)

func _make_barrier() -> void:
	barrier = Node3D.new()
	add_child(barrier)
	barrier.global_position = center
	var n := 28
	for i in n:
		var a := float(i) / n * TAU
		var sb := StaticBody3D.new()
		var cs := CollisionShape3D.new()
		var sh := BoxShape3D.new()
		sh.size = Vector3(2.6, 14.0, 1.0)
		cs.shape = sh
		sb.add_child(cs)
		sb.add_child(Build.box(Vector3(2.6, 14.0, 0.2), Color(1, 0.4, 0.4, 0.3), Vector3.ZERO, 0.5))
		sb.get_child(1).material_override = Build.mat(Color(1, 0.4, 0.5), 0.5, 0.25)
		barrier.add_child(sb)
		sb.position = Vector3(cos(a) * 17.6, 6.0, sin(a) * 17.6)
		sb.rotation.y = -a + PI * 0.5

func _on_defeated() -> void:
	finished = true
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.hide_boss()
	Audio.play_music("victory")
	await get_tree().create_timer(1.6).timeout
	if barrier:
		barrier.queue_free()
		barrier = null
	Game.defeat_boss(boss_id)
	if hud:
		await hud.say(Cutscenes.BOSS_DEFEAT.get(boss_id, []))
	var sp := StarPickup.new()
	sp.star_id = star_id
	get_parent().add_child(sp)
	sp.global_position = center + Vector3(0, 1.8, 0)
	Audio.sfx("win")
	Game.set_flag("boss_" + boss_id, true)
	if boss_id == "baron":
		await get_tree().create_timer(1.0).timeout
		if hud:
			await hud.say(Cutscenes.ENDING)
		Game.data["ending"] = true
		Game.save_game()
		Game.toast.emit("You saved the world! Keep collecting Stars!")
		Audio.play_music("hub")
	else:
		Audio.play_music(Kingdoms.DATA[kingdom]["music"])

func reset() -> void:
	if finished:
		return
	started = false
	if barrier:
		barrier.queue_free()
		barrier = null
	if boss and is_instance_valid(boss):
		boss.queue_free()
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.hide_boss()
	_spawn_boss()
	Audio.play_music(Kingdoms.DATA[kingdom]["music"])
