class_name Build
extends RefCounted
## Procedural mesh/material helpers. Everything visual in the game comes from here.

const TOON := """
shader_type spatial;
uniform vec4 albedo : source_color = vec4(1.0);
uniform float glow = 0.0;
void fragment() {
	ALBEDO = albedo.rgb;
	float rim = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0);
	EMISSION = albedo.rgb * glow + vec3(1.0) * rim * 0.18;
}
void light() {
	float d = dot(NORMAL, LIGHT);
	float s = smoothstep(0.0, 0.08, d) * 0.55 + smoothstep(0.45, 0.55, d) * 0.45;
	DIFFUSE_LIGHT += LIGHT_COLOR * ATTENUATION * s;
}
"""
static var _shader: Shader
static var _cache := {}

static func mat(c: Color, glow := 0.0, alpha := 1.0) -> Material:
	var key := "%s_%s_%s_%s" % [c.to_html(true), glow, alpha, Settings.quality == "low"]
	if _cache.has(key):
		return _cache[key]
	var m: Material
	if Settings.quality == "low" or alpha < 1.0:
		var sm := StandardMaterial3D.new()
		sm.albedo_color = Color(c.r, c.g, c.b, alpha)
		sm.roughness = 1.0
		if alpha < 1.0:
			sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		if glow > 0.0:
			sm.emission_enabled = true
			sm.emission = c
			sm.emission_energy_multiplier = glow
		m = sm
	else:
		if _shader == null:
			_shader = Shader.new()
			_shader.code = TOON
		var sm := ShaderMaterial.new()
		sm.shader = _shader
		sm.set_shader_parameter("albedo", c)
		sm.set_shader_parameter("glow", glow)
		m = sm
	_cache[key] = m
	return m

static func clear_cache() -> void:
	_cache.clear()

static func _mi(mesh: Mesh, c: Color, pos := Vector3.ZERO, glow := 0.0) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat(c, glow)
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if Settings.shadows_on() else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi

static func box(size: Vector3, c: Color, pos := Vector3.ZERO, glow := 0.0) -> MeshInstance3D:
	var m := BoxMesh.new()
	m.size = size
	return _mi(m, c, pos, glow)

static func sphere(r: float, c: Color, pos := Vector3.ZERO, glow := 0.0) -> MeshInstance3D:
	var m := SphereMesh.new()
	m.radius = r
	m.height = r * 2.0
	var seg := 16 if Settings.quality == "high" else (10 if Settings.quality == "medium" else 7)
	m.radial_segments = seg
	m.rings = maxi(seg / 2, 4)
	return _mi(m, c, pos, glow)

static func cyl(r_top: float, r_bot: float, h: float, c: Color, pos := Vector3.ZERO, glow := 0.0) -> MeshInstance3D:
	var m := CylinderMesh.new()
	m.top_radius = r_top
	m.bottom_radius = r_bot
	m.height = h
	m.radial_segments = 16 if Settings.quality == "high" else (10 if Settings.quality == "medium" else 7)
	m.rings = 1
	return _mi(m, c, pos, glow)

static func capsule(r: float, h: float, c: Color, pos := Vector3.ZERO) -> MeshInstance3D:
	var m := CapsuleMesh.new()
	m.radius = r
	m.height = h
	m.radial_segments = 12 if Settings.quality != "low" else 7
	m.rings = 4
	return _mi(m, c, pos)

static func prism(size: Vector3, c: Color, pos := Vector3.ZERO) -> MeshInstance3D:
	var m := PrismMesh.new()
	m.size = size
	return _mi(m, c, pos)

static func torus(inner: float, outer: float, c: Color, pos := Vector3.ZERO, glow := 0.0) -> MeshInstance3D:
	var m := TorusMesh.new()
	m.inner_radius = inner
	m.outer_radius = outer
	m.rings = 12 if Settings.quality != "low" else 8
	m.ring_segments = 8 if Settings.quality != "low" else 5
	return _mi(m, c, pos, glow)

## Solid static box (visual + collision).
static func solid_box(parent: Node, pos: Vector3, size: Vector3, c: Color, group := "") -> StaticBody3D:
	var sb := StaticBody3D.new()
	sb.position = pos
	var cs := CollisionShape3D.new()
	var sh := BoxShape3D.new()
	sh.size = size
	cs.shape = sh
	sb.add_child(cs)
	sb.add_child(box(size, c))
	if group != "":
		sb.add_to_group(group)
	parent.add_child(sb)
	return sb

static func solid_cyl(parent: Node, pos: Vector3, r: float, h: float, c: Color, group := "") -> StaticBody3D:
	var sb := StaticBody3D.new()
	sb.position = pos
	var cs := CollisionShape3D.new()
	var sh := CylinderShape3D.new()
	sh.radius = r
	sh.height = h
	cs.shape = sh
	sb.add_child(cs)
	sb.add_child(cyl(r, r, h, c))
	if group != "":
		sb.add_to_group(group)
	parent.add_child(sb)
	return sb

static func label3d(text: String, pos: Vector3, size := 0.5, c := Color.WHITE) -> Label3D:
	var l := Label3D.new()
	l.text = text
	l.position = pos
	l.pixel_size = 0.01 * size
	l.font_size = 48
	l.modulate = c
	l.outline_size = 12
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.no_depth_test = true
	return l

static func eyes(parent: Node3D, z: float, y: float, spread: float, r := 0.12) -> void:
	for sx in [-1, 1]:
		var e := sphere(r, Color.WHITE, Vector3(sx * spread, y, z))
		parent.add_child(e)
		var p := sphere(r * 0.5, Color(0.05, 0.05, 0.1), Vector3(sx * spread, y, z + r * 0.7))
		parent.add_child(p)

## Extruded 5-point star mesh.
static func star_mesh(r_out := 0.6, r_in := 0.27, depth := 0.22) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var pts: Array[Vector2] = []
	for i in 10:
		var a := -PI / 2.0 + i * PI / 5.0
		var r := r_out if i % 2 == 0 else r_in
		pts.append(Vector2(cos(a) * r, -sin(a) * r))
	var zf := depth * 0.5
	for i in 10:
		var a := pts[i]
		var b := pts[(i + 1) % 10]
		# front
		st.add_vertex(Vector3(0, 0, zf))
		st.add_vertex(Vector3(a.x, a.y, zf))
		st.add_vertex(Vector3(b.x, b.y, zf))
		# back
		st.add_vertex(Vector3(0, 0, -zf))
		st.add_vertex(Vector3(b.x, b.y, -zf))
		st.add_vertex(Vector3(a.x, a.y, -zf))
		# side
		st.add_vertex(Vector3(a.x, a.y, zf))
		st.add_vertex(Vector3(a.x, a.y, -zf))
		st.add_vertex(Vector3(b.x, b.y, zf))
		st.add_vertex(Vector3(b.x, a.y * 0.0 + b.y, zf))
		st.add_vertex(Vector3(a.x, a.y, -zf))
		st.add_vertex(Vector3(b.x, b.y, -zf))
	st.generate_normals()
	return st.commit()

static func star(r: float, c: Color, glow := 0.6) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = star_mesh(r, r * 0.45, r * 0.35)
	mi.material_override = mat(c, glow)
	return mi
