class_name IntroScene
extends Node3D
## Opening cutscene: night sky, falling Stars, Baron's airship, then Pip and Capt.
var dlg: DialogueUI
var cam: Camera3D
var ship: Node3D
var stars: Array = []
var t := 0.0

func _ready() -> void:
	Audio.play_music("title")
	var env := Environment.new()
	var sky := Sky.new()
	var sm := ProceduralSkyMaterial.new()
	sm.sky_top_color = Color(0.03, 0.02, 0.15)
	sm.sky_horizon_color = Color(0.4, 0.25, 0.5)
	sm.ground_bottom_color = Color(0.05, 0.05, 0.15)
	sm.ground_horizon_color = Color(0.3, 0.2, 0.4)
	sky.sky_material = sm
	env.sky = sky
	env.background_mode = Environment.BG_SKY
	env.ambient_light_color = Color(0.5, 0.45, 0.8)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-40, 30, 0)
	sun.light_energy = 0.8
	add_child(sun)
	# village
	add_child(Build.cyl(60, 60, 2, Color(0.2, 0.35, 0.3), Vector3(0, -1, 0)))
	for i in 14:
		var p := Vector3(randf_range(-25, 25), 0, randf_range(-30, -5))
		add_child(Build.box(Vector3(3, 2.5, 3), Color(0.8, 0.6, 0.45), p + Vector3(0, 1.25, 0)))
		add_child(Build.prism(Vector3(3.6, 1.4, 3.6), Color(0.7, 0.25, 0.25), p + Vector3(0, 3.2, 0)))
	# Stars in the sky
	for i in 40:
		var s := Build.star(0.8, Color(1, 0.9, 0.3), 1.0)
		s.position = Vector3(randf_range(-40, 40), randf_range(10, 35), randf_range(-60, -20))
		add_child(s)
		stars.append(s)
	# airship
	ship = Node3D.new()
	var hull := Build.box(Vector3(10, 2.5, 4), Color(0.25, 0.15, 0.35))
	ship.add_child(hull)
	var bal := Build.sphere(5.0, Color(0.4, 0.2, 0.5), Vector3(0, 5, 0))
	bal.scale = Vector3(1.7, 1.0, 1.0)
	ship.add_child(bal)
	ship.add_child(Build.torus(0.6, 0.9, Color(1, 0.8, 0.3), Vector3(0, 2.0, 2.2), 0.5))
	ship.position = Vector3(60, 25, -40)
	add_child(ship)
	# hero & hat on the ground
	var pip := Node3D.new()
	pip.add_child(Build.capsule(0.38, 1.0, Color(0.2, 0.55, 0.95), Vector3(0, 0.55, 0)))
	pip.add_child(Build.sphere(0.4, Color(1, 0.82, 0.65), Vector3(0, 1.28, 0)))
	var capt := CaptVisual.build()
	capt.position = Vector3(0, 1.7, 0)
	pip.add_child(capt)
	pip.position = Vector3(0, 0, -2)
	add_child(pip)
	cam = Camera3D.new()
	cam.current = true
	cam.position = Vector3(0, 3, 8)
	add_child(cam)
	cam.look_at(Vector3(0, 12, -30))
	var layer := CanvasLayer.new()
	add_child(layer)
	dlg = DialogueUI.new()
	layer.add_child(dlg)
	_play.call_deferred()

func _process(delta: float) -> void:
	t += delta
	for i in stars.size():
		stars[i].rotation.y += delta * (1.0 + i % 3)
		stars[i].position.y += sin(t + i) * delta * 0.5
	ship.position += (Vector3(0, 22, -45) - ship.position) * delta * 0.15
	ship.position.y += sin(t * 0.7) * delta

func _play() -> void:
	var lines: Array = Cutscenes.INTRO
	# first lines under the night sky, then pan down to Pip
	for i in lines.size():
		if i == 4:
			var tw := create_tween()
			tw.tween_property(cam, "position", Vector3(0, 2.2, 3.5), 2.0)
			tw.parallel().tween_property(self, "_dummy", 1.0, 2.0)
			cam.look_at(Vector3(0, 1.5, -2))
		await dlg.say([lines[i]])
		if dlg.skip_all:
			break
	Game.goto_world("hub")

var _dummy := 0.0
