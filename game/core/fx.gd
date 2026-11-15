class_name Fx
extends RefCounted
## Cheap particle helpers.
static func burst(parent: Node, pos: Vector3, color: Color, count := 12, speed := 5.0, life := 0.5) -> void:
	if parent == null or DisplayServer.get_name() == "headless":
		return
	var n := maxi(int(count * Settings.particle_scale()), 2)
	var p := CPUParticles3D.new()
	p.one_shot = true
	p.emitting = true
	p.amount = n
	p.lifetime = life
	p.explosiveness = 1.0
	p.direction = Vector3.UP
	p.spread = 180.0
	p.initial_velocity_min = speed * 0.4
	p.initial_velocity_max = speed
	p.gravity = Vector3(0, -12, 0)
	var m := SphereMesh.new()
	m.radius = 0.09
	m.height = 0.18
	m.radial_segments = 4
	m.rings = 2
	p.mesh = m
	p.material_override = Build.mat(color, 1.0)
	p.position = pos
	parent.add_child(p)
	var t := parent.get_tree().create_timer(life + 0.3)
	t.timeout.connect(func(): if is_instance_valid(p): p.queue_free())

static func ring(parent: Node, pos: Vector3, color: Color, radius := 3.0, time := 0.35) -> void:
	if parent == null or DisplayServer.get_name() == "headless":
		return
	var t := Build.torus(0.8, 1.0, color, pos + Vector3(0, 0.1, 0), 0.8)
	t.scale = Vector3(0.3, 0.3, 0.3)
	parent.add_child(t)
	var tw := t.create_tween()
	tw.tween_property(t, "scale", Vector3(radius, 0.3, radius), time)
	tw.parallel().tween_property(t, "transparency", 1.0, time)
	tw.tween_callback(t.queue_free)
