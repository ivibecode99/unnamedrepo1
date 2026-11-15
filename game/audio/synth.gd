class_name Synth
extends RefCounted
## Tiny software synthesizer: all audio in the game is generated from this.
const RATE := 16000

static func wave(kind: String, phase: float) -> float:
	var p := phase - floorf(phase)
	match kind:
		"sq": return 1.0 if p < 0.5 else -1.0
		"sq25": return 1.0 if p < 0.25 else -1.0
		"sq12": return 1.0 if p < 0.125 else -1.0
		"tri": return 4.0 * absf(p - 0.5) - 1.0
		"saw": return 2.0 * p - 1.0
		"sin": return sin(p * TAU)
	return 0.0

static func mtof(m: float) -> float:
	return 440.0 * pow(2.0, (m - 69.0) / 12.0)

## Mix a note into `buf` (PackedFloat32Array). env = attack/decay/sustain/release in seconds+level.
static func note(buf: PackedFloat32Array, start: int, dur: float, freq: float, kind: String, vol: float, a := 0.005, d := 0.08, s := 0.6, r := 0.06, vib := 0.0, slide := 0.0) -> void:
	var n := int((dur + r) * RATE)
	var ph := 0.0
	for i in n:
		var idx := start + i
		if idx >= buf.size():
			break
		var t := float(i) / RATE
		var env := 1.0
		if t < a:
			env = t / maxf(a, 0.0001)
		elif t < a + d:
			env = lerpf(1.0, s, (t - a) / maxf(d, 0.0001))
		elif t < dur:
			env = s
		else:
			env = s * maxf(0.0, 1.0 - (t - dur) / maxf(r, 0.0001))
		var f := freq * (1.0 + slide * t)
		if vib > 0.0:
			f *= 1.0 + sin(t * 40.0) * vib
		ph += f / RATE
		buf[idx] += wave(kind, ph) * vol * env

static func noise(buf: PackedFloat32Array, start: int, dur: float, vol: float, decay: float, tone := 1.0, rng: RandomNumberGenerator = null) -> void:
	var n := int(dur * RATE)
	var last := 0.0
	var r := rng if rng else RandomNumberGenerator.new()
	for i in n:
		var idx := start + i
		if idx >= buf.size():
			break
		var t := float(i) / RATE
		var x := r.randf() * 2.0 - 1.0
		last = lerpf(last, x, tone)
		buf[idx] += last * vol * exp(-t * decay)

static func to_pcm(buf: PackedFloat32Array, peak := 0.9) -> PackedByteArray:
	var m := 0.0001
	for v in buf:
		m = maxf(m, absf(v))
	var g := peak / m if m > peak else 1.0
	var out := PackedByteArray()
	out.resize(buf.size() * 2)
	for i in buf.size():
		out.encode_s16(i * 2, int(clampf(buf[i] * g, -1.0, 1.0) * 32000.0))
	return out

static func make_stream(pcm: PackedByteArray, loop := false) -> AudioStreamWAV:
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = RATE
	s.stereo = false
	s.data = pcm
	if loop:
		s.loop_mode = AudioStreamWAV.LOOP_FORWARD
		s.loop_begin = 0
		s.loop_end = pcm.size() / 2
	return s
