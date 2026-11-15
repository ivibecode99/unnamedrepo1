extends Node
## Pre-renders every music track to res://audio/music/<id>.pcm  (16 kHz mono s16).
## godot --headless --path game res://tests/render_music.tscn
func _ready() -> void:
	for id in MusicGen.TRACKS:
		var pcm := MusicGen.render(id)
		var f := FileAccess.open("res://audio/music/%s.pcm" % id, FileAccess.WRITE)
		f.store_buffer(pcm)
		f.close()
		print("rendered ", id, " ", pcm.size(), " bytes")
	get_tree().quit()
