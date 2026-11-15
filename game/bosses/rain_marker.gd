class_name RainMarker
extends Node3D
## Boss rain attack: a warning circle, then a falling blast.
var delay := 1.0
var color := Color(1, 0.5, 0.2)
var t := 0.0
var disc: MeshInstance3D
var fired := false
var player: Player

func _ready() -> void:
	disc = Build.cyl(1.6, 1.6, 0.05, Color(1, 0.2, 0.2), Vector3.ZERO, 0.8)
	disc.material_override = Build.mat(Color(1, 0.25, 0.2), 0.6, 0.6)
	add_child(disc)

func _physics_process(delta: float) -> void:
	t += delta
	disc.scale = Vector3.ONE * (0.4 + 0.6 * clampf(t / delay, 0.0, 1.0))
	if t >= delay and not fired:
		fired = true
		Fx.burst(get_parent(), global_position + Vector3(0, 0.5, 0), color, 18, 7.0)
		Audio.sfx("explosion", 1.3, -6.0)
		var ps := get_tree().get_nodes_in_group("player")
		if not ps.is_empty():
			var p: Player = ps[0]
			var tgt: Node3D = p
			if p.state == Player.S.CAPTURED and p.captured_by:
				tgt = p.captured_by
			var d := tgt.global_position - global_position
			if Vector2(d.x, d.z).length() < 1.8 and d.y < 2.5:
				if p.state == Player.S.CAPTURED and p.captured_by:
					p.captured_by.release()
				p.hurt(global_position, 1)
		disc.visible = false
	if t >= delay + 0.3:
		queue_free()
