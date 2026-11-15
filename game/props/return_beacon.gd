class_name ReturnBeacon
extends Node3D
## Call the airship: return to the hub.
var talking := false
var t := 0.0

func _ready() -> void:
	add_to_group("interactable")
	add_child(Build.cyl(0.2, 0.3, 2.2, Color(0.8, 0.8, 0.9), Vector3(0, 1.1, 0)))
	add_child(Build.sphere(0.45, Color(0.4, 0.8, 1.0), Vector3(0, 2.5, 0), 1.0))
	add_child(Build.label3d("Airship", Vector3(0, 3.4, 0), 0.4, Color(0.7, 0.9, 1)))

func _physics_process(delta: float) -> void:
	t += delta
	get_child(1).position.y = 2.5 + sin(t * 3.0) * 0.1

func can_interact(p: Player) -> bool:
	return not talking and global_position.distance_to(p.global_position) < 2.8

func interact(p: Player) -> void:
	talking = true
	p.lock("talk")
	var hud := get_tree().get_first_node_in_group("hud")
	var go := true
	if hud:
		go = await hud.confirm("Call the airship and head back to the hub?")
	talking = false
	if go:
		Game.save_game()
		Game.goto_world("hub")
	else:
		p.unlock()
