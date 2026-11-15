class_name QuestItem
extends Node3D
## Item to return to an NPC. Stored in Game.data["items"].
var item_id := ""
var item_name := "Thing"
var player: Player
var t := 0.0
var vis: Node3D

func _ready() -> void:
	if item_id in Game.data["items"]:
		queue_free()
		return
	vis = Node3D.new()
	add_child(vis)
	vis.add_child(Build.box(Vector3(0.5, 0.5, 0.5), Color(1.0, 0.45, 0.8), Vector3.ZERO, 0.7))
	vis.add_child(Build.sphere(0.25, Color(1, 1, 1), Vector3(0, 0.45, 0), 0.9))
	add_child(Build.label3d(item_name, Vector3(0, 1.1, 0), 0.5, Color(1, 1, 0.7)))

func _physics_process(delta: float) -> void:
	t += delta
	vis.rotation.y += delta * 2.0
	vis.position.y = sin(t * 3.0) * 0.12
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if ps.is_empty():
			return
		player = ps[0]
	if player.global_position.distance_to(global_position) < 1.8:
		Game.data["items"].append(item_id)
		Audio.sfx("coin_big")
		Game.toast.emit("Found: " + item_name)
		Fx.burst(get_parent(), global_position, Color(1, 0.6, 0.9), 14)
		queue_free()
