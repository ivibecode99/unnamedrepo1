class_name Crate
extends StaticBody3D
## Breakable crate. Drops coins. Breaks by hat, spin, ground pound, or creature smash.
var kingdom := "forest"
var coins := 3
var broken := false
var hp := 1

func _ready() -> void:
	add_to_group("breakable")
	add_to_group("pound_target")
	var cs := CollisionShape3D.new()
	var sh := BoxShape3D.new()
	sh.size = Vector3(1.2, 1.2, 1.2)
	cs.shape = sh
	add_child(cs)
	add_child(Build.box(Vector3(1.2, 1.2, 1.2), Color(0.8, 0.55, 0.3)))
	add_child(Build.box(Vector3(1.25, 0.15, 1.25), Color(0.55, 0.35, 0.18), Vector3(0, 0.5, 0)))
	add_child(Build.box(Vector3(1.25, 0.15, 1.25), Color(0.55, 0.35, 0.18), Vector3(0, -0.5, 0)))

func on_hat_hit(p) -> void:
	smash()

func on_pound(p) -> void:
	smash()

func hurt(n: int, src) -> void:
	smash()

func smash() -> void:
	if broken:
		return
	broken = true
	Audio.sfx("hit")
	Fx.burst(get_parent(), global_position, Color(0.8, 0.55, 0.3), 10)
	var w := get_parent()
	for i in coins:
		var c := CoinPickup.new()
		c.kingdom = kingdom
		c.sticky = true
		c.coin_id = ""
		w.add_child(c)
		c.global_position = global_position + Vector3(randf_range(-0.8, 0.8), 0.5 + i * 0.1, randf_range(-0.8, 0.8))
	queue_free()
