class_name MapTable
extends Node3D
## Hub map table: pick a kingdom.
var talking := false

func _ready() -> void:
	add_to_group("interactable")
	add_child(Build.cyl(1.4, 1.6, 0.9, Color(0.5, 0.33, 0.2), Vector3(0, 0.45, 0)))
	add_child(Build.cyl(1.7, 1.7, 0.12, Color(0.95, 0.9, 0.7), Vector3(0, 0.96, 0)))
	var globe := Build.sphere(0.5, Color(0.3, 0.6, 0.9), Vector3(0, 1.7, 0), 0.4)
	add_child(globe)
	add_child(Build.label3d("MAP", Vector3(0, 2.6, 0), 0.6, Color(1, 1, 0.7)))

func can_interact(p: Player) -> bool:
	return not talking and global_position.distance_to(p.global_position) < 3.2

func interact(p: Player) -> void:
	talking = true
	p.lock("talk")
	var hud := get_tree().get_first_node_in_group("hud")
	var dest := ""
	if hud:
		dest = await hud.open_map()
	talking = false
	if dest != "":
		Game.save_game()
		Game.goto_world(dest)
	else:
		p.unlock()
