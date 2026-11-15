class_name Water
extends Node3D
## Swimmable water volume (AABB). Group "water".
var size := Vector3(40, 10, 40)

func _ready() -> void:
	add_to_group("water")
	var m := Build.box(Vector3(size.x, 0.05, size.z), Color(0.2, 0.6, 0.95), Vector3(0, size.y * 0.5, 0))
	m.material_override = Build.mat(Color(0.2, 0.6, 0.95), 0.2, 0.55)
	add_child(m)
	var deep := Build.box(Vector3(size.x, size.y, size.z), Color(0.1, 0.35, 0.7), Vector3.ZERO)
	deep.material_override = Build.mat(Color(0.1, 0.4, 0.8), 0.1, 0.25)
	add_child(deep)

func surface_y() -> float:
	return global_position.y + size.y * 0.5

func contains(p: Vector3) -> bool:
	var l := p - global_position
	return absf(l.x) < size.x * 0.5 and absf(l.z) < size.z * 0.5 and absf(l.y) < size.y * 0.5
