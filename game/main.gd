extends Node
## Root: swaps between title, intro and world scenes with a fade.
var current: Node = null
var fade: ColorRect
var layer: CanvasLayer

func _ready() -> void:
	Game.main = self
	layer = CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	fade = ColorRect.new()
	fade.color = Color.BLACK
	fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fade.modulate.a = 0.0
	layer.add_child(fade)
	var args := OS.get_cmdline_user_args()
	if "--world" in args:
		var i := args.find("--world")
		Game.new_game(0) if not Game.load_game(0) else null
		Game.goto_world(args[i + 1] if i + 1 < args.size() else "forest")
	else:
		show_title()

func _swap(builder: Callable) -> void:
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, 0.25)
	await tw.finished
	if current:
		current.queue_free()
		await get_tree().process_frame
	current = builder.call()
	add_child(current)
	var tw2 := create_tween()
	tw2.tween_property(fade, "modulate:a", 0.0, 0.35)

func show_title() -> void:
	get_tree().paused = false
	await _swap(func(): return TitleScreen.new())

func show_world(kingdom: String) -> void:
	get_tree().paused = false
	await _swap(func():
		var w := World.new()
		w.kingdom_id = kingdom
		return w)

func show_intro() -> void:
	get_tree().paused = false
	await _swap(func(): return IntroScene.new())
