extends RefCounted
func run(t) -> void:
	for name in SfxBank.RECIPES:
		var pcm := SfxBank.render(name)
		t.check(pcm.size() > 200, "sfx renders: " + name)
		var peak := 0
		for i in range(0, pcm.size() - 1, 2):
			peak = maxi(peak, absi(pcm.decode_s16(i)))
		t.check(peak > 500 and peak <= 32767, "sfx %s level sane (%d)" % [name, peak])
	for id in MusicGen.TRACKS:
		var pcm := MusicGen.render(id)
		t.check(pcm.size() > Synth.RATE * 8, "music renders: " + id)
		var peak := 0
		var clipped := 0
		for i in range(0, pcm.size() - 1, 40):
			var v := absi(pcm.decode_s16(i))
			peak = maxi(peak, v)
			if v >= 32000:
				clipped += 1
		t.check(peak > 3000, "music %s audible (%d)" % [id, peak])
		t.check(clipped < 20, "music %s not heavily clipped" % id)
