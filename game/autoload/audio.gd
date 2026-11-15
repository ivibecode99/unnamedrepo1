extends Node
## Audio manager: SFX pool, synthesized music (pre-rendered PCM in res://audio/music or generated on demand).
const MUSIC_DIR := "res://audio/music/"

var _sfx_cache := {}
var _sfx_players: Array[AudioStreamPlayer] = []
var _music_player: AudioStreamPlayer
var _music_cache := {}
var current_music := ""
var _thread: Thread
var _pending := ""
var muted := false

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for b in ["Music", "SFX"]:
		if AudioServer.get_bus_index(b) == -1:
			AudioServer.add_bus()
			var i := AudioServer.bus_count - 1
			AudioServer.set_bus_name(i, b)
			AudioServer.set_bus_send(i, "Master")
	for i in 10:
		var p := AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_sfx_players.append(p)
	_music_player = AudioStreamPlayer.new()
	_music_player.bus = "Music"
	add_child(_music_player)
	apply_volumes()

func apply_volumes() -> void:
	var s = get_node_or_null("/root/Settings")
	if s == null:
		return
	var vals := {"Master": s.master, "Music": s.music, "SFX": s.sfx}
	for b in vals:
		var i := AudioServer.get_bus_index(b)
		if i >= 0:
			AudioServer.set_bus_volume_db(i, linear_to_db(maxf(vals[b], 0.0001)))

func sfx(name: String, pitch := 1.0, vol_db := 0.0) -> void:
	if DisplayServer.get_name() == "headless":
		return
	var st: AudioStreamWAV = _sfx_cache.get(name)
	if st == null:
		st = Synth.make_stream(SfxBank.render(name))
		_sfx_cache[name] = st
	for p in _sfx_players:
		if not p.playing:
			p.stream = st
			p.pitch_scale = pitch
			p.volume_db = vol_db
			p.play()
			return

func load_track(id: String) -> AudioStreamWAV:
	var path := MUSIC_DIR + id + ".pcm"
	var pcm: PackedByteArray
	if FileAccess.file_exists(path):
		pcm = FileAccess.get_file_as_bytes(path)
	else:
		pcm = MusicGen.render(id)
	return Synth.make_stream(pcm, true)

func play_music(id: String, fade := true) -> void:
	if id == current_music:
		return
	current_music = id
	if DisplayServer.get_name() == "headless":
		return
	if id == "":
		_music_player.stop()
		return
	if _music_cache.has(id):
		_start(_music_cache[id])
		return
	# render in a thread if no pre-rendered file exists
	if FileAccess.file_exists(MUSIC_DIR + id + ".pcm"):
		var st := load_track(id)
		_music_cache[id] = st
		_start(st)
	else:
		_pending = id
		if _thread and _thread.is_started():
			_thread.wait_to_finish()
		_thread = Thread.new()
		_thread.start(_render_bg.bind(id))

func _render_bg(id: String) -> void:
	var st := load_track(id)
	call_deferred("_done_bg", id, st)

func _done_bg(id: String, st: AudioStreamWAV) -> void:
	_music_cache[id] = st
	if current_music == id:
		_start(st)

func _start(st: AudioStreamWAV) -> void:
	_music_player.stream = st
	_music_player.volume_db = 0.0
	_music_player.play()

func stop_music() -> void:
	current_music = ""
	_music_player.stop()

func duck(on: bool) -> void:
	if DisplayServer.get_name() == "headless":
		return
	_music_player.volume_db = -10.0 if on else 0.0
