class_name SfxBank
extends RefCounted
## Sound-effect recipes. Each: array of segments [kind, f0, f1, dur, vol] or ["noise", dur, vol, decay, tone].
const RECIPES := {
	"jump": [["sq", 330.0, 660.0, 0.14, 0.5]],
	"jump2": [["sq", 400.0, 800.0, 0.16, 0.5]],
	"jump3": [["sq", 500.0, 1100.0, 0.22, 0.5], ["tri", 250.0, 550.0, 0.22, 0.4]],
	"longjump": [["saw", 300.0, 900.0, 0.25, 0.35]],
	"walljump": [["sq25", 600.0, 900.0, 0.12, 0.45]],
	"land": [["noise", 0.08, 0.5, 40.0, 0.3]],
	"pound": [["tri", 300.0, 60.0, 0.25, 0.7], ["noise", 0.2, 0.6, 18.0, 0.2]],
	"dive": [["saw", 700.0, 250.0, 0.2, 0.35]],
	"roll": [["noise", 0.18, 0.3, 10.0, 0.15]],
	"throw": [["sq12", 700.0, 1200.0, 0.1, 0.4], ["sq12", 1200.0, 700.0, 0.1, 0.3]],
	"catch": [["tri", 500.0, 900.0, 0.08, 0.5]],
	"spin": [["saw", 400.0, 700.0, 0.3, 0.3]],
	"hit": [["noise", 0.12, 0.7, 25.0, 0.5], ["sq", 220.0, 80.0, 0.12, 0.4]],
	"hurt": [["sq", 500.0, 120.0, 0.35, 0.5]],
	"coin": [["sq", 988.0, 988.0, 0.06, 0.4], ["sq", 1319.0, 1319.0, 0.22, 0.4]],
	"coin_big": [["sq", 784.0, 784.0, 0.06, 0.4], ["sq", 1047.0, 1047.0, 0.06, 0.4], ["sq", 1568.0, 1568.0, 0.25, 0.4]],
	"star": [["tri", 523.0, 523.0, 0.1, 0.5], ["tri", 659.0, 659.0, 0.1, 0.5], ["tri", 784.0, 784.0, 0.1, 0.5], ["tri", 1047.0, 1047.0, 0.1, 0.5], ["tri", 1319.0, 1319.0, 0.5, 0.5]],
	"capture": [["sq", 200.0, 1000.0, 0.15, 0.4], ["tri", 1000.0, 400.0, 0.2, 0.4]],
	"release": [["tri", 800.0, 200.0, 0.2, 0.5]],
	"spring": [["sq", 200.0, 900.0, 0.25, 0.5]],
	"splash": [["noise", 0.3, 0.5, 8.0, 0.4]],
	"swim": [["noise", 0.12, 0.25, 12.0, 0.2]],
	"menu_move": [["sq", 600.0, 600.0, 0.04, 0.3]],
	"menu_ok": [["sq", 600.0, 900.0, 0.1, 0.35]],
	"menu_back": [["sq", 600.0, 400.0, 0.1, 0.35]],
	"talk": [["sq25", 300.0, 300.0, 0.03, 0.25]],
	"checkpoint": [["tri", 440.0, 440.0, 0.1, 0.5], ["tri", 660.0, 660.0, 0.2, 0.5]],
	"explosion": [["noise", 0.6, 0.9, 5.0, 0.35], ["tri", 120.0, 30.0, 0.5, 0.6]],
	"boss_hit": [["noise", 0.2, 0.8, 14.0, 0.5], ["sq", 150.0, 60.0, 0.25, 0.6]],
	"boss_roar": [["saw", 120.0, 60.0, 0.6, 0.5], ["noise", 0.6, 0.4, 4.0, 0.15]],
	"warn": [["sq", 880.0, 880.0, 0.08, 0.3], ["sq", 0.0, 0.0, 0.05, 0.0], ["sq", 880.0, 880.0, 0.08, 0.3]],
	"shoot": [["sq12", 900.0, 200.0, 0.15, 0.4]],
	"win": [["sq", 523.0, 523.0, 0.12, 0.4], ["sq", 523.0, 523.0, 0.12, 0.4], ["sq", 523.0, 523.0, 0.12, 0.4], ["sq", 659.0, 659.0, 0.3, 0.4], ["sq", 587.0, 587.0, 0.12, 0.4], ["sq", 784.0, 784.0, 0.5, 0.4]],
	"fall": [["tri", 700.0, 100.0, 0.7, 0.4]],
	"buy": [["sq", 800.0, 800.0, 0.05, 0.4], ["sq", 1200.0, 1200.0, 0.05, 0.4], ["sq", 600.0, 600.0, 0.15, 0.4]],
	"deny": [["sq", 200.0, 150.0, 0.2, 0.4]],
	"ping": [["sin", 1500.0, 1500.0, 0.3, 0.3]],
}

static func render(name: String) -> PackedByteArray:
	var segs: Array = RECIPES.get(name, RECIPES["menu_move"])
	var total := 0.0
	for s in segs:
		total += s[3] if s[0] != "noise" else s[1]
	var buf := PackedFloat32Array()
	buf.resize(int(total * Synth.RATE) + 32)
	var t := 0
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(name)
	# noise segments overlay from the start; tonal segments play sequentially unless first is noise
	var cursor := 0
	for s in segs:
		if s[0] == "noise":
			Synth.noise(buf, 0, s[1], s[2], s[3], s[4], rng)
		else:
			var dur: float = s[3]
			var f0: float = s[1]
			var f1: float = s[2]
			var vol: float = s[4]
			var n := int(dur * Synth.RATE)
			var ph := 0.0
			for i in n:
				var u := float(i) / n
				var f := lerpf(f0, f1, u)
				ph += f / Synth.RATE
				var env := minf(1.0, minf(u * 20.0, (1.0 - u) * 4.0))
				if cursor + i < buf.size():
					buf[cursor + i] += Synth.wave(s[0], ph) * vol * env
			cursor += n
	return Synth.to_pcm(buf, 0.8)
