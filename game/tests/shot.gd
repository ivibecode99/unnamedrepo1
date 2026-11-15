extends Node
## Screenshot harness:  xvfb-run godot --path game --rendering-driver opengl3 res://tests/shot.tscn -- --world=forest --out=/tmp/x.png [--frames=90] [--cam=yaw,pitch,dist] [--pos=x,y,z]
func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var kid := "forest"
	var out := "/tmp/shot.png"
	var frames := 90
	var pos = null
	var camp = null
	for a in args:
		if a.begins_with("--world="): kid = a.substr(8)
		if a.begins_with("--out="): out = a.substr(6)
		if a.begins_with("--frames="): frames = int(a.substr(9))
		if a.begins_with("--quality="): Settings.quality = a.substr(10)
		if a.begins_with("--pos="):
			var p := a.substr(6).split(",")
			pos = Vector3(float(p[0]), float(p[1]), float(p[2]))
		if a.begins_with("--cam="):
			var c := a.substr(6).split(",")
			camp = [float(c[0]), float(c[1]), float(c[2])]
	Game.save_enabled = false
	Game.data = Game.blank_data()
	Game.data["stars"] = ["forest_boss"] if false else []
	var w := World.new()
	w.kingdom_id = kid
	add_child(w)
	for i in 5:
		await get_tree().physics_frame
	if pos != null:
		w.player.global_position = pos
	if camp != null:
		w.cam.yaw = camp[0]
		w.cam.pitch = camp[1]
		w.cam.dist = camp[2]
	for i in frames:
		await get_tree().physics_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(out)
	print("saved ", out, " ", img.get_size())
	get_tree().quit()
