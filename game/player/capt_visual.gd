class_name CaptVisual
extends RefCounted
## Capt: the living hat. Dome + brim + googly eyes + tiny wings.
static func build() -> Node3D:
	var root := Node3D.new()
	var skin := "classic"
	if Game.data.has("hat_skin"):
		skin = str(Game.data["hat_skin"])
	var c := ItemData.hat_color(skin)
	var dome := Build.sphere(0.45, c, Vector3(0, 0.0, 0))
	dome.scale = Vector3(1.0, 0.75, 1.0)
	root.add_child(dome)
	root.add_child(Build.cyl(0.66, 0.66, 0.07, c.darkened(0.25), Vector3(0, -0.2, 0.05)))
	root.add_child(Build.cyl(0.47, 0.47, 0.1, Color(1.0, 0.85, 0.3), Vector3(0, -0.13, 0)))
	# eyes
	for sx in [-1, 1]:
		root.add_child(Build.sphere(0.12, Color.WHITE, Vector3(sx * 0.17, 0.02, 0.38)))
		root.add_child(Build.sphere(0.06, Color(0.05, 0.05, 0.1), Vector3(sx * 0.17, 0.02, 0.48)))
	# tiny wings (they flap when captured/thrown)
	for sx in [-1, 1]:
		var w := Build.prism(Vector3(0.35, 0.3, 0.05), Color(1, 1, 1), Vector3(sx * 0.5, 0.15, -0.1))
		w.rotation_degrees = Vector3(0, 0, sx * -70)
		w.name = "wing" + ("L" if sx < 0 else "R")
		root.add_child(w)
	return root
