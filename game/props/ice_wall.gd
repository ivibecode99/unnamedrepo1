extends StaticBody3D
## Ice wall: shattered by Yeti smash / ground pound / hat spin. Script is attached on top of a Build.solid_box.
func on_pound(p) -> void:
	shatter()
func on_hat_hit(p) -> void:
	pass
func hurt(n, s) -> void:
	shatter()
func shatter() -> void:
	Audio.sfx("hit", 0.8)
	Fx.burst(get_parent(), global_position, Color(0.8, 0.95, 1.0), 18)
	queue_free()
