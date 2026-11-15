class_name CoinPickup
extends Node3D
## Kingdom-specific coin. Remembers collection by id so coins don't respawn after save/load.
var coin_id := ""
var kingdom := "forest"
var value := 1
var vis: Node3D
var player: Player
var t := 0.0
var _tick := 0
var sticky := false     # dropped coins (enemy drops) are not persisted

func _ready() -> void:
	add_to_group("coin")
	if not sticky and Game.is_collected(coin_id):
		queue_free()
		return
	var col: Color = Kingdoms.DATA[kingdom]["coin"]["color"]
	if value >= 5:
		vis = Build.cyl(0.55, 0.55, 0.12, col, Vector3.ZERO, 0.6)
	else:
		vis = Build.cyl(0.32, 0.32, 0.08, col, Vector3.ZERO, 0.6)
	vis.rotation_degrees.x = 90
	var holder := Node3D.new()
	add_child(holder)
	holder.add_child(vis)
	vis = holder
	t = randf() * 6.0
	_tick = int(abs(hash(coin_id)) % 3)

func _physics_process(delta: float) -> void:
	t += delta
	vis.rotation.y += delta * 3.0
	_tick += 1
	if _tick % 3 != 0:
		return
	if player == null or not is_instance_valid(player):
		var ps := get_tree().get_nodes_in_group("player")
		if ps.is_empty():
			return
		player = ps[0]
	var pos := player.global_position + Vector3(0, 0.8, 0)
	if player.state == Player.S.CAPTURED and player.captured_by:
		pos = player.captured_by.global_position + Vector3(0, 0.6, 0)
	if pos.distance_to(global_position) < 1.3:
		collect()

func collect() -> void:
	if is_queued_for_deletion():
		return
	if not sticky:
		Game.mark_collected(coin_id)
	Game.add_coins(kingdom, value)
	Audio.sfx("coin_big" if value >= 5 else "coin", 1.0, -4.0)
	Fx.burst(get_parent(), global_position, Kingdoms.DATA[kingdom]["coin"]["color"], 5, 3.0, 0.4)
	queue_free()
