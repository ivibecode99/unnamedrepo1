class_name MusicGen
extends RefCounted
## Procedural composer: turns a small spec into a looping chiptune/orchestral-ish track.

const SCALES := {
	"major": [0, 2, 4, 5, 7, 9, 11],
	"minor": [0, 2, 3, 5, 7, 8, 10],
	"dorian": [0, 2, 3, 5, 7, 9, 10],
	"mixo": [0, 2, 4, 5, 7, 9, 10],
	"lydian": [0, 2, 4, 6, 7, 9, 11],
	"phrygian": [0, 1, 3, 5, 7, 8, 10],
	"harm": [0, 2, 3, 5, 7, 8, 11],
	"pent": [0, 2, 4, 7, 9, 9, 12],
}

const TRACKS := {
	"title":   {"bpm": 104, "root": 60, "scale": "major",   "prog": [0, 4, 5, 3], "lead": "sq25", "bass": "tri", "arp": "sq12", "pat": "bounce", "seed": 11, "bars": 8},
	"hub":     {"bpm": 96,  "root": 57, "scale": "mixo",    "prog": [0, 3, 4, 3], "lead": "tri",  "bass": "tri", "arp": "sq12", "pat": "sway",   "seed": 12, "bars": 8},
	"forest":  {"bpm": 118, "root": 62, "scale": "major",   "prog": [0, 5, 3, 4], "lead": "sq25", "bass": "tri", "arp": "sq12", "pat": "bounce", "seed": 21, "bars": 8},
	"desert":  {"bpm": 108, "root": 57, "scale": "phrygian","prog": [0, 1, 0, 6], "lead": "saw",  "bass": "tri", "arp": "sq25", "pat": "sway",   "seed": 22, "bars": 8},
	"city":    {"bpm": 128, "root": 59, "scale": "dorian",  "prog": [0, 3, 0, 4], "lead": "sq",   "bass": "saw", "arp": "sq12", "pat": "drive",  "seed": 23, "bars": 8},
	"ocean":   {"bpm": 92,  "root": 60, "scale": "lydian",  "prog": [0, 1, 4, 0], "lead": "sin",  "bass": "tri", "arp": "tri",  "pat": "sway",   "seed": 24, "bars": 8},
	"snow":    {"bpm": 100, "root": 64, "scale": "pent",    "prog": [0, 5, 3, 4], "lead": "sin",  "bass": "tri", "arp": "sq12", "pat": "sway",   "seed": 25, "bars": 8},
	"volcano": {"bpm": 138, "root": 55, "scale": "harm",    "prog": [0, 5, 3, 4], "lead": "saw",  "bass": "sq",  "arp": "sq25", "pat": "drive",  "seed": 26, "bars": 8},
	"castle":  {"bpm": 124, "root": 57, "scale": "harm",    "prog": [0, 6, 5, 4], "lead": "sq",   "bass": "saw", "arp": "sq12", "pat": "drive",  "seed": 27, "bars": 8},
	"boss":    {"bpm": 150, "root": 52, "scale": "minor",   "prog": [0, 0, 5, 4], "lead": "saw",  "bass": "sq",  "arp": "sq25", "pat": "drive",  "seed": 31, "bars": 8},
	"finalboss": {"bpm": 160, "root": 50, "scale": "harm",  "prog": [0, 5, 6, 4], "lead": "sq",   "bass": "saw", "arp": "sq12", "pat": "drive",  "seed": 32, "bars": 8},
	"victory": {"bpm": 120, "root": 60, "scale": "major",   "prog": [0, 3, 4, 0], "lead": "sq25", "bass": "tri", "arp": "sq12", "pat": "bounce", "seed": 33, "bars": 4},
}

static func degree_note(root: int, scale: Array, deg: int) -> int:
	var oct := int(floorf(float(deg) / 7.0))
	var idx := ((deg % 7) + 7) % 7
	return root + int(scale[idx]) + oct * 12

static func render(id: String) -> PackedByteArray:
	var sp: Dictionary = TRACKS.get(id, TRACKS["forest"])
	var rng := RandomNumberGenerator.new()
	rng.seed = int(sp["seed"])
	var scale: Array = SCALES[sp["scale"]]
	var root: int = sp["root"]
	var bars: int = sp["bars"]
	var spb: float = 60.0 / float(sp["bpm"])
	var step: float = spb / 4.0
	var total_steps := bars * 16
	var buf := PackedFloat32Array()
	buf.resize(int(total_steps * step * Synth.RATE) + Synth.RATE / 2)
	var prog: Array = sp["prog"]
	var pat: String = sp["pat"]
	# --- melody motif (2 bars) of scale degrees, repeated AABA with variation
	var motif: Array = []
	var d := 4
	for i in 8:
		d = clampi(d + rng.randi_range(-2, 2), 0, 9)
		motif.append(d)
	var rhythm_options := [[0, 3, 6, 8, 10, 12], [0, 2, 4, 8, 10, 14], [0, 4, 6, 8, 12, 14], [0, 3, 6, 9, 12, 14]]
	var rhythm: Array = rhythm_options[rng.randi() % rhythm_options.size()]
	for bar in bars:
		var chord_deg: int = prog[bar % prog.size()]
		var base_step := bar * 16
		var t0 := func(s: int) -> int: return int((base_step + s) * step * Synth.RATE)
		# bass
		var broot := degree_note(root - 12, scale, chord_deg)
		var bf := Synth.mtof(broot)
		match pat:
			"drive":
				for i in 8:
					Synth.note(buf, t0.call(i * 2), step * 1.6, bf * (2.0 if i % 4 == 3 else 1.0), sp["bass"], 0.22, 0.003, 0.05, 0.7, 0.03)
			"bounce":
				for i in 4:
					var fr := bf if i % 2 == 0 else bf * 1.4983
					Synth.note(buf, t0.call(i * 4), step * 2.5, fr, sp["bass"], 0.26, 0.004, 0.06, 0.6, 0.04)
			_:
				Synth.note(buf, t0.call(0), step * 7.0, bf, sp["bass"], 0.26, 0.01, 0.1, 0.7, 0.1)
				Synth.note(buf, t0.call(8), step * 7.0, bf * 1.4983, sp["bass"], 0.22, 0.01, 0.1, 0.7, 0.1)
		# arpeggio (chord tones)
		var tones := [degree_note(root, scale, chord_deg), degree_note(root, scale, chord_deg + 2), degree_note(root, scale, chord_deg + 4), degree_note(root + 12, scale, chord_deg)]
		var arp_step := 2 if pat != "sway" else 4
		for i in range(0, 16, arp_step):
			var tn: int = tones[(i / arp_step) % 4]
			Synth.note(buf, t0.call(i), step * arp_step * 0.8, Synth.mtof(tn), sp["arp"], 0.07, 0.002, 0.04, 0.5, 0.03)
		# lead (skip on first bar for intro feel? no — always play)
		var phrase := bar % 4
		var tr := 0
		if phrase == 2:
			tr = 2
		for k in rhythm.size():
			var md: int = motif[(k + phrase * 2) % motif.size()] + tr
			var dur: float = step * (2.0 if k % 2 == 0 else 3.0)
			if phrase == 3 and k == rhythm.size() - 1:
				md = chord_deg
				dur = step * 4.0
			var mn := degree_note(root + 12, scale, md)
			Synth.note(buf, t0.call(rhythm[k]), dur, Synth.mtof(mn), sp["lead"], 0.16, 0.006, 0.07, 0.65, 0.07, 0.004)
		# drums
		for i in 16:
			if i % 8 == 0:
				Synth.note(buf, t0.call(i), 0.12, 110.0, "sin", 0.4, 0.001, 0.1, 0.0, 0.01, 0.0, -6.0)
			if i % 8 == 4 and pat != "sway":
				Synth.noise(buf, t0.call(i), 0.1, 0.18, 30.0, 0.5, rng)
			if i % 2 == 0:
				Synth.noise(buf, t0.call(i), 0.03, 0.05, 80.0, 0.9, rng)
	return Synth.to_pcm(buf, 0.85)
