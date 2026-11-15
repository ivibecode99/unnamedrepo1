class_name BossVisual
extends RefCounted
## Procedural boss bodies. Each boss has a distinct silhouette.
static func build(vis: Node3D, id: String, info: Dictionary) -> void:
	var s: float = info["scale"]
	var c: Color = info["color"]
	var c2: Color = info["color2"]
	match info["shape"]:
		"tree":
			vis.add_child(Build.cyl(0.9 * s * 0.5, 1.1 * s * 0.5, 1.8 * s, c2, Vector3(0, 0.9 * s, 0)))
			var crown := Build.sphere(1.0 * s, c, Vector3(0, 2.2 * s, 0))
			vis.add_child(crown)
			for a in 6:
				var ang := a / 6.0 * TAU
				vis.add_child(Build.sphere(0.5 * s, c.lightened(0.1), Vector3(cos(ang) * 0.9 * s, 2.0 * s + (a % 2) * 0.3, sin(ang) * 0.9 * s)))
			vis.add_child(Build.cyl(0.4, 0.5, 0.35, Color(1, 0.85, 0.2), Vector3(0, 3.1 * s, 0)))
			Build.eyes(vis, 0.85 * s, 1.5 * s, 0.35 * s, 0.2)
			for sx in [-1, 1]:
				vis.add_child(Build.capsule(0.25 * s, 1.4 * s, c2, Vector3(sx * 1.1 * s, 1.0 * s, 0.2)))
		"beetle":
			var b := Build.sphere(1.1 * s, c, Vector3(0, 0.9 * s, 0))
			b.scale = Vector3(1.0, 0.7, 1.4)
			vis.add_child(b)
			vis.add_child(Build.sphere(0.6 * s, c.darkened(0.3), Vector3(0, 1.0 * s, 1.2 * s)))
			vis.add_child(Build.prism(Vector3(0.8 * s, 1.2 * s, 0.4 * s), c2, Vector3(0, 1.9 * s, 0.9 * s)))
			vis.add_child(Build.prism(Vector3(0.5 * s, 1.0 * s, 0.3 * s), c2, Vector3(0.4 * s, 1.7 * s, 0.9 * s)))
			vis.add_child(Build.prism(Vector3(0.5 * s, 1.0 * s, 0.3 * s), c2, Vector3(-0.4 * s, 1.7 * s, 0.9 * s)))
			Build.eyes(vis, 1.7 * s, 1.1 * s, 0.25 * s, 0.15)
			for sx in [-1, 1]:
				for i in 3:
					vis.add_child(Build.capsule(0.12 * s, 1.2 * s, c.darkened(0.4), Vector3(sx * 1.2 * s, 0.3 * s, (i - 1) * 0.7 * s)))
		"mech":
			vis.add_child(Build.box(Vector3(1.6 * s, 1.6 * s, 1.2 * s), c, Vector3(0, 1.2 * s, 0)))
			vis.add_child(Build.box(Vector3(1.0 * s, 0.8 * s, 0.9 * s), c.lightened(0.1), Vector3(0, 2.4 * s, 0)))
			vis.add_child(Build.box(Vector3(0.9 * s, 0.25 * s, 0.1), Color(1, 0.3, 0.3), Vector3(0, 2.4 * s, 0.46 * s), 1.0))
			for sx in [-1, 1]:
				vis.add_child(Build.cyl(0.35 * s, 0.35 * s, 0.4 * s, c2, Vector3(sx * 1.2 * s, 1.6 * s, 0)))
				vis.get_child(vis.get_child_count() - 1).rotation_degrees.z = 90
				vis.add_child(Build.box(Vector3(0.5 * s, 1.0 * s, 0.5 * s), c.darkened(0.3), Vector3(sx * 0.5 * s, 0.4 * s, 0)))
			vis.add_child(Build.cyl(0.25 * s, 0.25 * s, 0.4 * s, c2, Vector3(0, 3.0 * s, 0)))
		"octo":
			vis.add_child(Build.sphere(1.2 * s, c, Vector3(0, 1.8 * s, 0)))
			for a in 8:
				var ang := a / 8.0 * TAU
				var t := Build.capsule(0.22 * s, 1.8 * s, c.lightened(0.1), Vector3(cos(ang) * 0.9 * s, 0.6 * s, sin(ang) * 0.9 * s))
				t.rotation = Vector3(sin(ang) * 0.5, 0, -cos(ang) * 0.5)
				vis.add_child(t)
			vis.add_child(Build.cyl(0.9 * s, 0.9 * s, 0.1, Color(0.15, 0.15, 0.3), Vector3(0, 3.0 * s, 0)))
			vis.add_child(Build.cyl(0.55 * s, 0.55 * s, 0.6 * s, Color(0.15, 0.15, 0.3), Vector3(0, 3.3 * s, 0)))
			Build.eyes(vis, 1.1 * s, 1.9 * s, 0.4 * s, 0.22)
		"yeti":
			vis.add_child(Build.sphere(1.3 * s, c, Vector3(0, 1.4 * s, 0)))
			vis.add_child(Build.sphere(0.8 * s, c, Vector3(0, 2.7 * s, 0)))
			for sx in [-1, 1]:
				vis.add_child(Build.sphere(0.55 * s, c.darkened(0.08), Vector3(sx * 1.6 * s, 1.2 * s, 0.3 * s)))
				vis.add_child(Build.box(Vector3(0.5 * s, 0.5 * s, 0.5 * s), c2, Vector3(sx * 0.6 * s, 0.1 * s, 0.2)))
			vis.add_child(Build.box(Vector3(1.0 * s, 0.25 * s, 0.1), Color(1, 0.2, 0.2), Vector3(0, 2.8 * s, 0.75 * s), 1.2))
			vis.add_child(Build.prism(Vector3(0.4 * s, 0.7 * s, 0.4 * s), c2, Vector3(0, 3.6 * s, 0)))
		"baron":
			vis.add_child(Build.capsule(0.9 * s * 0.6, 2.4 * s, c, Vector3(0, 1.3 * s, 0)))
			vis.add_child(Build.sphere(0.7 * s * 0.6, Color(0.95, 0.82, 0.7), Vector3(0, 2.8 * s, 0)))
			vis.add_child(Build.cyl(0.8 * s * 0.6, 0.8 * s * 0.6, 0.05, Color(0.1, 0.05, 0.2), Vector3(0, 3.1 * s, 0)))
			vis.add_child(Build.cyl(0.5 * s * 0.6, 0.55 * s * 0.6, 0.9 * s * 0.6, Color(0.1, 0.05, 0.2), Vector3(0, 3.5 * s, 0)))
			Build.eyes(vis, 0.4 * s, 2.85 * s, 0.2 * s, 0.14)
			vis.add_child(Build.box(Vector3(0.7 * s, 0.1 * s, 0.1), Color(0.2, 0.05, 0.05), Vector3(0, 2.6 * s, 0.4 * s)))
			# the giant key on his back
			var key := Node3D.new()
			key.name = "Key"
			key.position = Vector3(0, 1.8 * s, -0.6 * s)
			vis.add_child(key)
			key.add_child(Build.cyl(0.08 * s, 0.08 * s, 1.0 * s, c2, Vector3(0, 0, -0.5 * s)))
			key.get_child(0).rotation_degrees.x = 90
			key.add_child(Build.torus(0.3 * s, 0.5 * s, c2, Vector3(0, 0, -1.1 * s), 0.5))
			key.add_child(Build.box(Vector3(0.8 * s, 0.1, 0.1), c2, Vector3(0, 0, -1.1 * s)))
		_:
			vis.add_child(Build.sphere(1.0 * s, c, Vector3(0, 1.0 * s, 0)))
