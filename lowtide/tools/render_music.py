#!/usr/bin/env python3
"""Render a preview WAV for every track: tools/render_music.py outdir"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'content'))
import songs, music
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for i, s in enumerate(songs.SONGS):
    music.render_song(s, 45, os.path.join(out, f'{i:02d}_{s.name}.wav'))
    print('rendered', i, s.name)
