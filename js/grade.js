/* Automatic condition estimate from the image: centering, corners, edges, surface.
   This is a heuristic estimate computed in the browser – NOT a PSA/BGS/SGC grade. Sliders let you override every sub-grade. */
const Grader = (() => {
  const L1 = (d, i, b) => Math.abs(d[i] - b[0]) + Math.abs(d[i + 1] - b[1]) + Math.abs(d[i + 2] - b[2]);
  const median = a => { a = a.slice().sort((x, y) => x - y); return a[a.length >> 1]; };
  const half = v => Math.round(v * 2) / 2;

  function prep(canvas) {
    const W = 600, sc = W / canvas.width;
    const c = newCanvas(W, canvas.height * sc);
    const x = c.getContext('2d', { willReadFrequently: true });
    x.fillStyle = '#808080'; x.fillRect(0, 0, c.width, c.height);
    x.drawImage(canvas, 0, 0, c.width, c.height);
    return { w: c.width, h: c.height, d: x.getImageData(0, 0, c.width, c.height).data };
  }
  function borderColor(im) {
    const { w, h, d } = im, o = Math.round(w * 0.024), s = [[], [], []];
    const push = (x, y) => { const i = (y * w + x) * 4; s[0].push(d[i]); s[1].push(d[i + 1]); s[2].push(d[i + 2]); };
    for (let t = 0.3; t <= 0.7; t += 0.02) {
      push(o, Math.round(h * t)); push(w - 1 - o, Math.round(h * t));
      push(Math.round(w * t), o); push(Math.round(w * t), h - 1 - o);
    }
    return s.map(median);
  }
  // walk inward from an edge until 2 consecutive pixels differ from the border colour
  function walk(im, bc, x0, y0, dx, dy, max, T = 75) {
    const { w, d } = im; let hit = 0;
    for (let k = 0; k < max; k++) {
      const i = ((y0 + dy * k) * w + (x0 + dx * k)) * 4;
      if (L1(d, i, bc) > T) { if (++hit >= 2) return k - 1; } else hit = 0;
    }
    return max;
  }
  function borders(im, bc) {
    const { w, h } = im, s = Math.round(w * 0.006), mx = Math.round(w * 0.35);
    const L = [], R = [], T = [], B = [];
    for (let t = 0.3; t <= 0.7; t += 0.04) {
      const y = Math.round(h * t), x = Math.round(w * t);
      L.push(s + walk(im, bc, s, y, 1, 0, mx)); R.push(s + walk(im, bc, w - 1 - s, y, -1, 0, mx));
      T.push(s + walk(im, bc, x, s, 0, 1, mx)); B.push(s + walk(im, bc, x, h - 1 - s, 0, -1, mx));
    }
    return { l: median(L), r: median(R), t: median(T), b: median(B), max: mx + s };
  }
  const centeringGrade = share => {
    const t = [[0.46, 10], [0.43, 9.5], [0.40, 9], [0.375, 8.5], [0.35, 8], [0.30, 7], [0.20, 6], [0.15, 5], [0.10, 4]];
    for (const [s, g] of t) if (share >= s) return g;
    return 3;
  };
  const fromFrac = (f, k) => clamp(half(10 - f * k), 1, 10);

  function cornerFrac(im, bc, cx, cy, sx, sy, band) {
    const { w, h, d } = im, p = Math.round(w * 0.08), r = w * 0.05;
    let n = 0, bad = 0;
    for (let u = 0; u < p; u++) for (let v = 0; v < p; v++) {
      if (u >= band && v >= band) continue;
      if (u < r && v < r && Math.hypot(u - r, v - r) > r - 1.5) continue; // rounded cut-out
      const x = cx + sx * u, y = cy + sy * v;
      if (x < 0 || y < 0 || x >= w || y >= h) continue;
      n++; if (L1(d, (y * w + x) * 4, bc) > 70) bad++;
    }
    return n ? bad / n : 0;
  }
  function edgeFrac(im, bc, side, depth) {
    const { w, h, d } = im, o = Math.round(w * 0.005);
    let n = 0, bad = 0;
    const horiz = side === 't' || side === 'b';
    const len = horiz ? w : h;
    for (let a = Math.round(len * 0.12); a < len * 0.88; a++) for (let e = o; e < o + depth; e++) {
      const x = horiz ? a : side === 'l' ? e : w - 1 - e;
      const y = horiz ? (side === 't' ? e : h - 1 - e) : a;
      n++; if (L1(d, (y * w + x) * 4, bc) > 70) bad++;
    }
    return n ? bad / n : 0;
  }
  function surfaceMAD(im, bw) {
    const { w, h, d } = im, e0 = Math.max(2, Math.round(bw * 0.4)), e1 = Math.max(e0 + 2, Math.round(bw * 0.9));
    const vals = [];
    const lum = (x, y) => { const i = (y * w + x) * 4; return d[i] * 0.3 + d[i + 1] * 0.59 + d[i + 2] * 0.11; };
    for (let a = Math.round(w * 0.12); a < w * 0.88; a += 2) for (let e = e0; e < e1; e += 2) { vals.push(lum(a, e)); vals.push(lum(a, h - 1 - e)); }
    for (let a = Math.round(h * 0.12); a < h * 0.88; a += 2) for (let e = e0; e < e1; e += 2) { vals.push(lum(e, a)); vals.push(lum(w - 1 - e, a)); }
    const m = median(vals);
    return median(vals.map(v => Math.abs(v - m)));
  }
  function sharpness(im) {
    const { w, h, d } = im; let s = 0, s2 = 0, n = 0;
    const lum = (x, y) => { const i = (y * w + x) * 4; return d[i] * 0.3 + d[i + 1] * 0.59 + d[i + 2] * 0.11; };
    for (let y = Math.round(h * 0.2); y < h * 0.8; y += 2) for (let x = Math.round(w * 0.2); x < w * 0.8; x += 2) {
      const l = 4 * lum(x, y) - lum(x - 1, y) - lum(x + 1, y) - lum(x, y - 1) - lum(x, y + 1);
      s += l; s2 += l * l; n++;
    }
    return s2 / n - (s / n) ** 2;
  }

  /* → { subs:{centering,corners,edges,surface}, notes:[], measures:{} } */
  function analyze(canvas) {
    const im = prep(canvas), notes = [];
    const bc = borderColor(im);
    const b = borders(im, bc);
    const minB = Math.min(b.l, b.r, b.t, b.b);
    const borderless = minB < im.w * 0.012 || [b.l, b.r, b.t, b.b].some(v => v >= b.max * 0.95);
    const subs = {}; const measures = {};
    if (borderless) {
      subs.centering = 9; subs.corners = 9; subs.edges = 9; subs.surface = 9;
      notes.push('Could not find a clean border (full-art / borderless / busy edge) – sub-grades are neutral 9s. Set them by hand.');
    } else {
      const lr = Math.min(b.l, b.r) / (b.l + b.r), tb = Math.min(b.t, b.b) / (b.t + b.b);
      subs.centering = centeringGrade(Math.min(lr, tb));
      measures.centering = `${Math.round(lr * 100)}/${Math.round((1 - lr) * 100)} left-right · ${Math.round(tb * 100)}/${Math.round((1 - tb) * 100)} top-bottom`;
      const band = Math.max(4, Math.round(minB * 0.75));
      const cf = [
        cornerFrac(im, bc, 0, 0, 1, 1, band), cornerFrac(im, bc, im.w - 1, 0, -1, 1, band),
        cornerFrac(im, bc, 0, im.h - 1, 1, -1, band), cornerFrac(im, bc, im.w - 1, im.h - 1, -1, -1, band)];
      const cMean = cf.reduce((a, c) => a + c, 0) / 4;
      subs.corners = fromFrac(0.5 * Math.max(...cf) + 0.5 * cMean, 18);
      const depth = Math.max(3, Math.round(minB * 0.3));
      const ef = ['t', 'b', 'l', 'r'].map(s => edgeFrac(im, bc, s, depth));
      subs.edges = fromFrac(0.5 * Math.max(...ef) + 0.5 * (ef.reduce((a, c) => a + c, 0) / 4), 14);
      const mad = surfaceMAD(im, minB);
      subs.surface = clamp(half(10 - Math.max(0, mad - 3) * 0.6), 1, 10);
      measures.corners = cf.map(f => Math.round(f * 100) + '%').join(' / ') + ' worn pixels (TL/TR/BL/BR)';
    }
    const sh = sharpness(im);
    if (sh < 25) notes.push('Image looks soft/blurry – wear can\'t be judged reliably. Re-scan at higher quality.');
    return { subs, notes, measures };
  }

  function finalGrade(subs, scale = 'int') {
    const v = Object.values(subs).filter(x => x != null && !isNaN(x));
    if (!v.length) return 0;
    const avg = v.reduce((a, b) => a + b, 0) / v.length;
    const g = Math.min(avg, Math.min(...v) + 1);   // can't be more than 1 point above the weakest sub-grade
    return clamp(scale === 'half' ? half(g) : Math.round(g), 1, 10);
  }
  function wordFor(g) {
    return g >= 10 ? 'GEM MINT' : g >= 9.5 ? 'MINT+' : g >= 9 ? 'MINT' : g >= 8.5 ? 'NM-MT+' : g >= 8 ? 'NM-MT' : g >= 7 ? 'NEAR MINT' : g >= 6 ? 'EX-MT' : g >= 5 ? 'EXCELLENT' : g >= 4 ? 'VG-EX' : g >= 3 ? 'VERY GOOD' : g >= 2 ? 'GOOD' : 'POOR';
  }
  const newCert = () => String(Math.floor(10000000 + Math.random() * 89999999));

  return { analyze, finalGrade, wordFor, newCert };
})();
