extends Node
## Global game state, 3-slot save system and scene routing.
signal stars_changed
signal coins_changed
signal health_changed
signal toast(text: String)
signal star_collected(id: String)

const SAVE_VERSION := 2
const SLOTS := 3
const SAVE_DIR := "user://"
const STARTING_HEALTH := 3
const MAX_HEALTH := 6

var slot := -1
var data := {}
var health := STARTING_HEALTH
var main: Node = null          # set by Main
var current_kingdom := "hub"
var spawn_name := ""
var play_start_msec := 0
var save_enabled := true       # tests turn this off

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS

# ------------------------------------------------------------------ save data
static func blank_data() -> Dictionary:
	return {
		"version": SAVE_VERSION, "stars": [], "coins": {}, "coins_total": {}, "collected": {},
		"flags": {}, "health_max": STARTING_HEALTH, "bosses": [], "seen": [], "kingdom": "hub",
		"outfit": "", "time": 0.0, "purchases": [], "items": [], "unlocked": ["hub", "forest"],
		"created": 0, "ending": false,
	}

func slot_path(s: int) -> String:
	return "%ssave_%d.json" % [SAVE_DIR, s]

func new_game(s: int) -> void:
	slot = s
	data = blank_data()
	data["created"] = int(Time.get_unix_time_from_system())
	health = STARTING_HEALTH
	current_kingdom = "hub"
	play_start_msec = Time.get_ticks_msec()
	save_game()

func _checksum(d: Dictionary) -> String:
	var c := d.duplicate(true)
	c.erase("sum")
	# normalise through a JSON round trip so int/float differences don't matter
	var norm = JSON.parse_string(JSON.stringify(c, "", true))
	return JSON.stringify(norm, "", true).md5_text()

func serialize() -> String:
	_flush_time()
	var d := data.duplicate(true)
	d["sum"] = _checksum(d)
	return JSON.stringify(d, "\t", true)

func save_game() -> bool:
	if not save_enabled or slot < 0:
		return false
	var path := slot_path(slot)
	var tmp := path + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(serialize())
	f.close()
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)
	var err := DirAccess.rename_absolute(tmp, path)
	return err == OK

func _flush_time() -> void:
	if play_start_msec > 0:
		data["time"] = float(data.get("time", 0.0)) + (Time.get_ticks_msec() - play_start_msec) / 1000.0
		play_start_msec = Time.get_ticks_msec()

## Parses and validates a save string; returns {} if corrupt.
func parse_save(text: String) -> Dictionary:
	var p = JSON.parse_string(text)
	if not (p is Dictionary):
		return {}
	var sum: String = str(p.get("sum", ""))
	if sum != "" and sum != _checksum(p):
		return {}
	return migrate(p)

func migrate(d: Dictionary) -> Dictionary:
	var out := blank_data()
	for k in d:
		out[k] = d[k]
	var v := int(d.get("version", 1))
	if v < 2:
		# v1 had no coins_total / unlocked
		if not d.has("coins_total"):
			out["coins_total"] = d.get("coins", {}).duplicate()
		if not d.has("unlocked"):
			out["unlocked"] = ["hub", "forest"]
	out["version"] = SAVE_VERSION
	# sanitize types
	out["stars"] = _uniq(out["stars"])
	out["health_max"] = clampi(int(out["health_max"]), STARTING_HEALTH, MAX_HEALTH)
	out.erase("sum")
	return out

func _uniq(a: Array) -> Array:
	var seen := {}
	var out: Array = []
	for x in a:
		if not seen.has(x):
			seen[x] = true
			out.append(x)
	return out

func load_game(s: int) -> bool:
	var path := slot_path(s)
	if not FileAccess.file_exists(path):
		return false
	var f := FileAccess.open(path, FileAccess.READ)
	var d := parse_save(f.get_as_text())
	if d.is_empty():
		return false
	slot = s
	data = d
	health = int(data["health_max"])
	current_kingdom = str(data.get("kingdom", "hub"))
	play_start_msec = Time.get_ticks_msec()
	return true

func slot_info(s: int) -> Dictionary:
	var path := slot_path(s)
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	var d := parse_save(f.get_as_text())
	if d.is_empty():
		return {"corrupt": true}
	return {"stars": d["stars"].size(), "time": d["time"], "kingdom": d["kingdom"], "ending": d.get("ending", false)}

func delete_slot(s: int) -> void:
	var p := slot_path(s)
	if FileAccess.file_exists(p):
		DirAccess.remove_absolute(p)

# ------------------------------------------------------------------ progress API
func star_count() -> int:
	return data["stars"].size()

func has_star(id: String) -> bool:
	return id in data["stars"]

func collect_star(id: String) -> bool:
	if has_star(id):
		return false
	data["stars"].append(id)
	stars_changed.emit()
	star_collected.emit(id)
	_unlock_by_stars()
	save_game()
	return true

func _unlock_by_stars() -> void:
	for k in Kingdoms.ORDER + ["final"]:
		if star_count() >= int(Kingdoms.DATA[k]["need"]) and not (k in data["unlocked"]):
			data["unlocked"].append(k)
			toast.emit("%s unlocked!" % Kingdoms.DATA[k]["name"])

func is_unlocked(k: String) -> bool:
	return k in data["unlocked"] or star_count() >= int(Kingdoms.DATA[k]["need"])

func coins(k: String) -> int:
	return int(data["coins"].get(k, 0))

func coins_total(k: String) -> int:
	return int(data["coins_total"].get(k, 0))

func add_coins(k: String, n: int) -> void:
	data["coins"][k] = coins(k) + n
	if n > 0:
		data["coins_total"][k] = coins_total(k) + n
	coins_changed.emit()

func spend_coins(k: String, n: int) -> bool:
	if coins(k) < n:
		return false
	data["coins"][k] = coins(k) - n
	coins_changed.emit()
	return true

func is_collected(id: String) -> bool:
	return data["collected"].has(id)

func mark_collected(id: String) -> void:
	data["collected"][id] = true

func flag(f: String) -> bool:
	return bool(data["flags"].get(f, false))

func set_flag(f: String, v := true) -> void:
	data["flags"][f] = v

func boss_defeated(b: String) -> bool:
	return b in data["bosses"]

func defeat_boss(b: String) -> void:
	if not (b in data["bosses"]):
		data["bosses"].append(b)
	save_game()

func seen(id: String) -> bool:
	return id in data["seen"]

func mark_seen(id: String) -> void:
	if not (id in data["seen"]):
		data["seen"].append(id)

func max_health() -> int:
	return int(data["health_max"])

func heal(n: int) -> void:
	health = mini(health + n, max_health())
	health_changed.emit()

func damage(n: int) -> void:
	health = maxi(health - n, 0)
	health_changed.emit()

func full_heal() -> void:
	health = max_health()
	health_changed.emit()

# ------------------------------------------------------------------ routing
func goto_title() -> void:
	if main:
		main.show_title()

func goto_world(kingdom: String, spawn := "") -> void:
	current_kingdom = kingdom
	data["kingdom"] = kingdom
	spawn_name = spawn
	if main:
		main.show_world(kingdom)

func goto_intro() -> void:
	if main:
		main.show_intro()

func format_time(sec: float) -> String:
	var s := int(sec)
	return "%d:%02d:%02d" % [s / 3600, (s / 60) % 60, s % 60]
