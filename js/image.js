/* Image processing: card detection / crop, rotate, thumbnails, rounded cut-out */
const ImgTools = {
  /* Find the card's bounding box against a plain background (scanner lid, table, mat). */
  detectCardBox(canvas) {
    const full = { x: 0, y: 0, w: canvas.width, h: canvas.height, ok: false };
    const sc = Math.min(1, 400 / Math.max(canvas.width, canvas.height));
    const w = Math.round(canvas.width * sc), h = Math.round(canvas.height * sc);
    const c = newCanvas(w, h);
    const x = c.getContext('2d', { willReadFrequently: true });
    x.drawImage(canvas, 0, 0, w, h);
    const d = x.getImageData(0, 0, w, h).data;
    const band = Math.max(2, Math.round(Math.min(w, h) * 0.02));
    const sm = [[], [], []];
    for (let yy = 0; yy < h; yy++) for (let xx = 0; xx < w; xx++) {
      if (xx < band || xx >= w - band || yy < band || yy >= h - band) {
        const i = (yy * w + xx) * 4; sm[0].push(d[i]); sm[1].push(d[i + 1]); sm[2].push(d[i + 2]);
      }
    }
    const med = a => { a.sort((p, q) => p - q); return a[a.length >> 1]; };
    const bg = sm.map(med);
    // background must be fairly uniform, otherwise we can't separate it
    let dev = 0;
    for (let k = 0; k < sm[0].length; k += 7) dev += Math.abs(sm[0][k] - bg[0]) + Math.abs(sm[1][k] - bg[1]) + Math.abs(sm[2][k] - bg[2]);
    dev /= Math.ceil(sm[0].length / 7);
    if (dev > 45) return full;
    const rows = new Uint32Array(h), cols = new Uint32Array(w);
    for (let yy = 0; yy < h; yy++) for (let xx = 0; xx < w; xx++) {
      const i = (yy * w + xx) * 4;
      if (Math.abs(d[i] - bg[0]) + Math.abs(d[i + 1] - bg[1]) + Math.abs(d[i + 2] - bg[2]) > 60) { rows[yy]++; cols[xx]++; }
    }
    const rmax = Math.max(...rows), cmax = Math.max(...cols);
    if (!rmax || !cmax) return full;
    let y0 = 0, y1 = h - 1, x0 = 0, x1 = w - 1;
    while (y0 < h && rows[y0] < rmax * 0.3) y0++;
    while (y1 > y0 && rows[y1] < rmax * 0.3) y1--;
    while (x0 < w && cols[x0] < cmax * 0.3) x0++;
    while (x1 > x0 && cols[x1] < cmax * 0.3) x1--;
    const bw = x1 - x0 + 1, bh = y1 - y0 + 1;
    const area = (bw * bh) / (w * h);
    const asp = Math.min(bw, bh) / Math.max(bw, bh);
    if (area > 0.93 || area < 0.12 || asp < 0.55 || asp > 0.95) return full;
    return { x: Math.round(x0 / sc), y: Math.round(y0 / sc), w: Math.round(bw / sc), h: Math.round(bh / sc), ok: true };
  },

  crop(canvas, box, inset = 0.003) {
    const ix = Math.round(box.w * inset), iy = Math.round(box.h * inset);
    const c = newCanvas(box.w - ix * 2, box.h - iy * 2);
    c.getContext('2d').drawImage(canvas, box.x + ix, box.y + iy, c.width, c.height, 0, 0, c.width, c.height);
    return c;
  },

  autoCrop(canvas) {
    const b = this.detectCardBox(canvas);
    return b.ok ? this.crop(canvas, b) : canvas;
  },

  rotate(canvas, cw = true) {
    const c = newCanvas(canvas.height, canvas.width);
    const x = c.getContext('2d');
    x.translate(c.width / 2, c.height / 2);
    x.rotate(cw ? Math.PI / 2 : -Math.PI / 2);
    x.drawImage(canvas, -canvas.width / 2, -canvas.height / 2);
    return c;
  },

  limit(canvas, max = 3000) {
    const m = Math.max(canvas.width, canvas.height);
    if (m <= max) return canvas;
    const s = max / m;
    const c = newCanvas(canvas.width * s, canvas.height * s);
    c.getContext('2d').drawImage(canvas, 0, 0, c.width, c.height);
    return c;
  },

  async thumb(canvas, max = 360) {
    const s = Math.min(1, max / Math.max(canvas.width, canvas.height));
    const c = newCanvas(canvas.width * s, canvas.height * s);
    c.getContext('2d').drawImage(canvas, 0, 0, c.width, c.height);
    return canvasToBlob(c, 'image/jpeg', 0.8);
  },

  /* "Background removal" for a card: tight inset + rounded-corner alpha mask.
     Works fully offline and is exact for rectangular cards on a cropped image. */
  cutout(canvas) {
    const trim = Math.round(canvas.width * 0.004);
    const w = canvas.width - trim * 2, h = canvas.height - trim * 2;
    const c = newCanvas(w, h);
    const x = c.getContext('2d');
    x.drawImage(canvas, trim, trim, w, h, 0, 0, w, h);
    x.globalCompositeOperation = 'destination-in';
    rr(x, 0, 0, w, h, Math.min(w, h) * 0.048);
    x.fillStyle = '#000'; x.fill();
    return c;
  },
};
