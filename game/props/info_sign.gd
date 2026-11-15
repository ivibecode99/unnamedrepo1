class_name InfoSign
extends Node3D
## Wooden sign with a hint. Interactable.
var text := ""
var player: Player
var talking := false

func _ready() -> void:
	add_to_group("interactable")
	add_child(Build.box(Vector3(0.15, 1.4, 0.15), Color(0.5, 0.33, 0.2), Vector3(0, 0.7, 0)))
	add_child(Build.box(Vector3(1.4, 0.9, 0.12), Color(0.85, 0.65, 0.4), Vector3(0, 1.5, 0)))
	add_child(Build.label3d("?", Vector3(0, 1.5, 0.1), 1.0, Color(0.3, 0.15, 0.05)))

func can_interact(p: Player) -> bool:
	return not talking and global_position.distance_to(p.global_position) < 2.6

func interact(p: Player) -> void:
	talking = true
	p.lock("talk")
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		await hud.say([["Sign", text]], "Sign")
	talking = false
	p.unlock()
