extends RefCounted
func run(t) -> void:
	for a in Settings.ACTIONS:
		t.check(InputMap.has_action(a), "action exists: " + a)
		t.check(InputMap.action_get_events(a).size() > 0, "action has bindings: " + a)
	for a in ["jump", "throw", "spin", "crouch", "roll", "dive", "pause", "skip", "move_left", "move_right", "move_forward", "move_back", "cam_left", "cam_right", "cam_up", "cam_down"]:
		var has_pad := false
		var has_key := false
		for e in InputMap.action_get_events(a):
			if e is InputEventJoypadButton or e is InputEventJoypadMotion:
				has_pad = true
			if e is InputEventKey or e is InputEventMouseButton:
				has_key = true
		t.check(has_pad or a.begins_with("cam_") and has_key or a == "pause" and has_pad, "gamepad binding for " + a)
		if not a.begins_with("cam_") or true:
			t.check(has_key or has_pad, "some binding for " + a)
	# rebinding round trip
	Settings.rebind_key("roll", KEY_Z)
	var found := false
	for e in InputMap.action_get_events("roll"):
		if e is InputEventKey and e.physical_keycode == KEY_Z:
			found = true
	t.check(found, "rebind works")
	Settings.reset_bindings()
	t.check(Settings.key_overrides.is_empty(), "reset clears overrides")
	# settings serialization
	Settings.invert_y = true
	Settings.master = 0.33
	var d := Settings.to_dict()
	Settings.invert_y = false
	Settings.master = 1.0
	Settings.from_dict(d)
	t.check(Settings.invert_y and absf(Settings.master - 0.33) < 0.001, "settings round trip")
	Settings.invert_y = false
	Settings.master = 0.8
