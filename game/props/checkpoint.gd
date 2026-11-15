class_name Checkpoint
extends Node3D
var active := false
var flag: Node3D
var player: Player

func _ready() -> void:
	add_child(Build.cyl(0.07, 0.07, 3.0, Color(0.8, 0.8, 0.8), Vector3(0, 1.5, 0)))
	flag = Build.box(Vector3(1.0, 0.7, 0.05), Color(0.9, 0.2, 0.2), Vector3(0.5, 2.6, 0))
	add_child(flag)
	add_child(Build.sphere(0.15, Color(1, 0.9, 0.3), Vector3(0, 3.05, 0), 0.6))

func _physics_process(delta: float) -> void:
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if ps.is_empty():
			return
		player = ps[0]
	if not active and player.global_position.distance_to(global_position) < 2.2:
		active = true
		player.checkpoint = global_position + Vector3(0, 0.5, 0)
		flag.material_override = Build.mat(Color(0.3, 0.9, 0.3), 0.4)
		Audio.sfx("checkpoint")
		Game.toast.emit("Checkpoint!")
		Game.save_game()
	if active:
		flag.rotation.y = sin(Time.get_ticks_msec() * 0.004) * 0.2
