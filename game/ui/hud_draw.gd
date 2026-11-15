class_name HudDraw
extends Control
## Draws hearts, star counter and kingdom coin counter without needing any font glyphs.
var hud: Hud

func _star_poly(c: Vector2, r: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for i in 10:
		var a := -PI / 2.0 + i * PI / 5.0
		var rr := r if i % 2 == 0 else r * 0.45
		pts.append(c + Vector2(cos(a), sin(a)) * rr)
	return pts

func _draw() -> void:
	if hud == null:
		return
	var font := get_theme_default_font()
	var fs := 26
	# health
	var mh := Game.max_health()
	for i in mh:
		var c := Vector2(36 + i * 38, 36)
		var full := i < Game.health
		draw_circle(c, 15, Color(0.1, 0.05, 0.1))
		draw_circle(c, 13, Color(0.95, 0.25, 0.3) if full else Color(0.35, 0.2, 0.3))
		if full:
			draw_circle(c + Vector2(-4, -4), 4, Color(1, 0.8, 0.85))
	# stars
	var sc := Vector2(36, 86)
	draw_colored_polygon(_star_poly(sc, 18), Color(0.1, 0.07, 0.0))
	draw_colored_polygon(_star_poly(sc, 15), Color(1.0, 0.85, 0.2))
	draw_string(font, Vector2(62, 96), "%d / %d" % [Game.star_count(), Kingdoms.total_stars()], HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.WHITE)
	# coins
	var k := Game.current_kingdom
	var cc: Color = Kingdoms.DATA[k]["coin"]["color"]
	var cp := Vector2(36, 134)
	draw_circle(cp, 15, Color(0.1, 0.07, 0.0))
	draw_circle(cp, 12, cc)
	draw_circle(cp, 7, cc.darkened(0.25))
	draw_string(font, Vector2(62, 144), "%s  %d" % [Kingdoms.DATA[k]["coin"]["name"], Game.coins(k)], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color.WHITE)
