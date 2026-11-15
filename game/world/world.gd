class_name World
extends Node3D
## One playable kingdom: environment + generated level + Pip + camera + HUD.
var kingdom_id := "forest"
var player: Player
var cam: CameraRig
var hud: Hud
var gen: LevelGen
var kd: Dictionary
var coin_star_spawned := false
var _death_busy := false

func _ready() -> void:
	kd = Kingdoms.DATA[kingdom_id]
	Game.current_kingdom = kingdom_id
	_build_environment()
	gen = LevelGen.new(self, kingdom_id)
	gen.build()
	player = Player.new()
	add_child(player)
	player.position = gen.spawn_pos
	player.checkpoint = gen.spawn_pos
	cam = CameraRig.new()
	cam.add_to_group("camera_rig")
	add_child(cam)
	cam.target = player
	player.cam = cam
	cam.yaw = 0.0 if kingdom_id != "hub" else -PI * 0.5
	player.dir_face = Basis(Vector3.UP, cam.yaw) * Vector3.FORWARD
	hud = Hud.new()
	hud.player = player
	hud.world = self
	add_child(hud)
	player.died.connect(_on_died)
	Game.full_heal()
	Game.coins_changed.connect(_check_coin_star)
	Audio.play_music(kd["music"])
	cam.snap_to_target()
	_check_coin_star()
	_arrival.call_deferred()

func _arrival() -> void:
	await get_tree().create_timer(0.6).timeout
	var key := "arrive_" + kingdom_id
	if not Game.seen(key):
		Game.mark_seen(key)
		var lines: Array = []
		if kingdom_id == "hub":
			lines = Cutscenes.HUB_ARRIVE
		else:
			lines = Cutscenes.KINGDOM_ARRIVE.get(kingdom_id, [])
		if is_instance_valid(player) and lines.size() > 0:
			player.lock("cutscene")
			await hud.say(lines)
			if is_instance_valid(player):
				player.unlock()
	if kingdom_id == "hub" and not Game.seen("controls_tip"):
		Game.mark_seen("controls_tip")
		Game.toast.emit("Move: WASD/Stick · Jump: Space/A · Throw Capt: E/X · Spin: Q/Y · Esc: Pause")

func _build_environment() -> void:
	var pal: Dictionary = kd["pal"]
	var env := Environment.new()
	var sky := Sky.new()
	var sm := ProceduralSkyMaterial.new()
	sm.sky_top_color = pal["sky_top"]
	sm.sky_horizon_color = pal["sky_hor"]
	sm.ground_bottom_color = pal["fog"].darkened(0.3)
	sm.ground_horizon_color = pal["fog"]
	sky.sky_material = sm
	env.sky = sky
	env.background_mode = Environment.BG_SKY
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = pal["sky_hor"].lerp(Color.WHITE, 0.4)
	env.ambient_light_energy = 0.42
	env.fog_enabled = Settings.quality != "low" or true
	env.fog_light_color = pal["fog"]
	env.fog_density = 0.0025
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	if Settings.quality == "high":
		env.glow_enabled = true
		env.glow_intensity = 0.4
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52, -35, 0)
	sun.light_energy = 0.95
	sun.shadow_bias = 0.08
	sun.shadow_normal_bias = 1.6
	sun.shadow_enabled = Settings.shadows_on()
	sun.directional_shadow_max_distance = 90.0
	add_child(sun)

func _check_coin_star() -> void:
	if coin_star_spawned or not kd.has("coin_goal"):
		return
	var sid := kingdom_id + "_coins"
	if Game.has_star(sid) and false:
		return
	if Game.coins_total(kingdom_id) >= int(kd["coin_goal"]):
		coin_star_spawned = true
		var s := StarPickup.new()
		s.star_id = sid
		add_child(s)
		s.global_position = gen.spawn_pos + Vector3(0, 3.5, -2.0)
		if not Game.has_star(sid):
			Game.toast.emit("A Star appeared near the start!")
			Audio.sfx("win")

func _on_died() -> void:
	if _death_busy:
		return
	_death_busy = true
	Audio.sfx("fall")
	Game.toast.emit("Oof! You lost some coins.")
	var lost := mini(5, Game.coins(kingdom_id))
	Game.add_coins(kingdom_id, -lost)
	var tw := create_tween()
	tw.tween_property(Game.main.fade, "modulate:a", 1.0, 0.4) if Game.main else null
	await get_tree().create_timer(0.8).timeout
	if gen and gen.arena:
		gen.arena.reset()
	if is_instance_valid(player):
		if player.state == Player.S.CAPTURED and player.captured_by:
			player.captured_by.release()
		Game.full_heal()
		player.respawn()
		player.invuln = 2.0
		cam.snap_to_target()
	if Game.main:
		var t2 := create_tween()
		t2.tween_property(Game.main.fade, "modulate:a", 0.0, 0.4)
	_death_busy = false

func _exit_tree() -> void:
	if Game.coins_changed.is_connected(_check_coin_star):
		Game.coins_changed.disconnect(_check_coin_star)
	if Game.toast.is_connected(hud._on_toast) if hud else false:
		Game.toast.disconnect(hud._on_toast)
	if hud and Game.star_collected.is_connected(hud._on_star):
		Game.star_collected.disconnect(hud._on_star)
