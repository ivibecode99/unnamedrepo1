/* Brand + rendering of labels, slabs and info sheets (all canvas, all local) */
const Brand = {
  DEF: { name: 'Quantum Optical Grading', tagline: 'QOG · Precision Card Grading', c1: '#8b5cf6', c2: '#1c1c1f', c3: '#c4a7ff', labelBg: '#1c1c1f', labelFg: '#ffffff', font: 'Montserrat' },
  _logo: undefined,
  get() { return Object.assign({}, this.DEF, Store.get('brand', {})); },
  save(b) { const { logo, ...rest } = b; Store.set('brand', rest); },
  async logoBitmap() {
    if (this._logo === undefined) {
      const blob = await DB.get('brand:logo');
      this._logo = blob ? await createImageBitmap(blob) : null;
    }
    return this._logo;
  },
  async setLogo(blob) { if (blob) await DB.put('brand:logo', blob); else await DB.del('brand:logo'); this._logo = undefined; },
  async loadCustomFont() {
    const blob = await DB.get('brand:font');
    if (!blob) return false;
    try { const ff = new FontFace('BrandCustom', await blob.arrayBuffer()); await ff.load(); document.fonts.add(ff); return true; } catch { return false; }
  },
  /* brand + decoded logo, with the font guaranteed loaded */
  async resolve() {
    const b = this.get();
    b.logo = await this.logoBitmap();
    try { await document.fonts.load(`700 24px "${b.font}"`); await document.fonts.load(`400 24px "${b.font}"`); } catch { }
    return b;
  },
};

const Slab = (() => {
  const DEF = { slabW: 3.15, slabH: 5.28, labelW: 2.75, labelH: 0.78, cardW: 2.5, cardH: 3.5 };
  const spec = () => Object.assign({}, DEF, Store.get('spec', {}));
  const fam = b => `"${b.font}", "Inter", sans-serif`;

  /* data: {line1,line2,line3,grade,word,cert} */
  function drawLabel(ctx, x, y, W, H, b, d) {
    ctx.save();
    ctx.translate(x, y);
    rr(ctx, 0, 0, W, H, H * 0.09); ctx.fillStyle = b.labelBg; ctx.fill(); ctx.clip();
    ctx.fillStyle = b.c1; ctx.fillRect(0, 0, W, H * 0.05);
    ctx.fillStyle = b.c3; ctx.fillRect(0, H * 0.93, W, H * 0.07);
    const pad = H * 0.1, F = fam(b);
    let tx = pad;
    if (b.logo) {
      const s = H * 0.66, r = Math.min(s / b.logo.width, s / b.logo.height);
      const lw = b.logo.width * r, lh = b.logo.height * r;
      ctx.drawImage(b.logo, pad, (H - lh) / 2, lw, lh);
      tx = pad + lw + pad * 1.2;
    }
    // grade box
    const gw = H * 1.12, gx = W - gw - pad, gy = H * 0.14, gh = H * 0.72;
    rr(ctx, gx, gy, gw, gh, H * 0.07); ctx.fillStyle = b.c1; ctx.fill();
    ctx.fillStyle = contrastOn(b.c1); ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    fitFont(ctx, String(d.grade), gw * 0.86, H * 0.44, 800, F);
    ctx.fillText(String(d.grade), gx + gw / 2, gy + gh * 0.6);
    fitFont(ctx, d.word, gw * 0.9, H * 0.12, 600, F);
    ctx.fillText(d.word, gx + gw / 2, gy + gh * 0.88);
    // text block
    const maxW = gx - tx - pad;
    ctx.textAlign = 'left'; ctx.fillStyle = b.labelFg;
    const line = (txt, yy, size, weight, alpha = 1) => {
      if (!txt) return;
      ctx.globalAlpha = alpha;
      fitFont(ctx, txt, maxW, size, weight, F);
      ctx.fillText(txt, tx, yy);
      ctx.globalAlpha = 1;
    };
    if ('letterSpacing' in ctx) ctx.letterSpacing = (H * 0.012) + 'px';
    line((b.name || '').toUpperCase(), H * 0.23, H * 0.105, 600, 0.6);
    if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
    line(d.line1, H * 0.43, H * 0.16, 500);
    line(d.line2, H * 0.68, H * 0.25, 800);
    line([d.line3, d.cert ? 'CERT ' + d.cert : ''].filter(Boolean).join('  •  '), H * 0.86, H * 0.125, 500, 0.8);
    ctx.restore();
    ctx.save();
    rr(ctx, x + 0.5, y + 0.5, W - 1, H - 1, H * 0.09); ctx.strokeStyle = 'rgba(0,0,0,.25)'; ctx.lineWidth = Math.max(1, H * 0.008); ctx.stroke();
    ctx.restore();
  }

  function renderLabel(d, b, dpi = 300) {
    const s = spec(), W = Math.round(s.labelW * dpi), H = Math.round(s.labelH * dpi);
    const c = newCanvas(W, H);
    drawLabel(c.getContext('2d'), 0, 0, W, H, b, d);
    return c;
  }

  /* opts: {cardCanvas, showLabel=true, dpi=300, pad=0.12 (in, transparent margin for the shadow)} */
  function renderSlab(d, b, opts = {}) {
    const s = spec(), dpi = opts.dpi || 300, padIn = opts.pad ?? 0.12, P = Math.round(padIn * dpi);
    const W = Math.round(s.slabW * dpi), H = Math.round(s.slabH * dpi);
    const c = newCanvas(W + P * 2, H + P * 2);
    const x = c.getContext('2d');
    x.translate(P, P);
    const R = 0.17 * dpi;
    // body
    x.save();
    if (P) { x.shadowColor = 'rgba(0,0,0,.35)'; x.shadowBlur = 0.1 * dpi; x.shadowOffsetY = 0.03 * dpi; }
    rr(x, 0, 0, W, H, R);
    const g = x.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, 'rgba(255,255,255,.34)'); g.addColorStop(1, 'rgba(205,220,235,.22)');
    x.fillStyle = g; x.fill();
    x.restore();
    rr(x, 0, 0, W, H, R); x.strokeStyle = 'rgba(0,0,0,.35)'; x.lineWidth = 0.012 * dpi; x.stroke();
    rr(x, 0.012 * dpi, 0.012 * dpi, W - 0.024 * dpi, H - 0.024 * dpi, R); x.strokeStyle = 'rgba(255,255,255,.9)'; x.lineWidth = 0.014 * dpi; x.stroke();
    // inner holder ring
    const m = 0.075 * dpi;
    rr(x, m, m, W - m * 2, H - m * 2, R * 0.7); x.strokeStyle = 'rgba(80,90,105,.45)'; x.lineWidth = 0.01 * dpi; x.stroke();
    rr(x, m + 0.012 * dpi, m + 0.012 * dpi, W - m * 2 - 0.024 * dpi, H - m * 2 - 0.024 * dpi, R * 0.68); x.strokeStyle = 'rgba(255,255,255,.55)'; x.lineWidth = 0.008 * dpi; x.stroke();
    // label
    const lw = s.labelW * dpi, lh = s.labelH * dpi, ly = 0.17 * dpi;
    let top = ly;
    if (opts.showLabel !== false) { drawLabel(x, (W - lw) / 2, ly, lw, lh, b, d); top = ly + lh; }
    // card window
    const wy0 = top + 0.13 * dpi, wy1 = H - 0.19 * dpi;
    if (opts.cardCanvas) {
      const cc = opts.cardCanvas, asp = cc.width / cc.height;
      let cw = s.cardW * dpi, ch = cw / asp;
      const maxH = Math.min(s.cardH * 1.06 * dpi, wy1 - wy0);
      if (ch > maxH) { ch = maxH; cw = ch * asp; }
      const cx = (W - cw) / 2, cy = wy0 + (wy1 - wy0 - ch) / 2;
      x.save();
      rr(x, cx - 0.045 * dpi, cy - 0.045 * dpi, cw + 0.09 * dpi, ch + 0.09 * dpi, 0.1 * dpi);
      x.fillStyle = 'rgba(20,24,30,.14)'; x.fill();
      x.shadowColor = 'rgba(0,0,0,.45)'; x.shadowBlur = 0.07 * dpi; x.shadowOffsetY = 0.02 * dpi;
      x.drawImage(cc, cx, cy, cw, ch);
      x.restore();
    }
    // gloss
    x.save();
    rr(x, 0, 0, W, H, R); x.clip();
    const gl = x.createLinearGradient(0, 0, W, H * 0.7);
    gl.addColorStop(0.18, 'rgba(255,255,255,0)'); gl.addColorStop(0.3, 'rgba(255,255,255,.22)'); gl.addColorStop(0.36, 'rgba(255,255,255,0)');
    gl.addColorStop(0.5, 'rgba(255,255,255,0)'); gl.addColorStop(0.56, 'rgba(255,255,255,.12)'); gl.addColorStop(0.6, 'rgba(255,255,255,0)');
    x.fillStyle = gl; x.fillRect(0, 0, W, H);
    x.restore();
    return c;
  }

  /* Letter-size report: slab + all the card info/stats.  info = card.info, meta = card fields */
  function renderSheet({ meta, info, grade, brand: b, slabCanvas, subs }) {
    const W = 1700, H = 2200, c = newCanvas(W, H), x = c.getContext('2d'), F = fam(b);
    x.fillStyle = b.c2; x.fillRect(0, 0, W, H);
    // header
    x.fillStyle = b.c1; x.fillRect(0, 0, W, 200);
    x.fillStyle = b.c3; x.fillRect(0, 200, W, 12);
    const onC1 = contrastOn(b.c1);
    let hx = 60;
    if (b.logo) { const r = Math.min(150 / b.logo.height, 300 / b.logo.width); const lw = b.logo.width * r, lh = b.logo.height * r; x.drawImage(b.logo, 60, (200 - lh) / 2, lw, lh); hx = 60 + lw + 30; }
    x.fillStyle = onC1; x.textBaseline = 'alphabetic';
    fitFont(x, b.name, 800, 70, 800, F); x.fillText(b.name, hx, 105);
    x.globalAlpha = .8; fitFont(x, b.tagline || '', 800, 34, 400, F); x.fillText(b.tagline || '', hx, 150); x.globalAlpha = 1;
    x.textAlign = 'right'; x.font = `600 34px ${F}`; x.fillText('CARD REPORT', W - 60, 95);
    x.globalAlpha = .8; x.font = `400 26px ${F}`; x.fillText(new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' }), W - 60, 140); x.globalAlpha = 1;
    x.textAlign = 'left';
    // slab (left)
    const sw = 620, sh = sw * slabCanvas.height / slabCanvas.width;
    x.drawImage(slabCanvas, 50, 270, sw, sh);
    // right column
    const rx = 740, rw = W - rx - 60;
    let y = 330;
    x.fillStyle = '#ffffff';
    const title = meta.name || 'Untitled card';
    fitFont(x, title, rw, 78, 800, F); x.fillText(title, rx, y);
    y += 52;
    x.fillStyle = '#b5b5c3'; x.font = `400 34px ${F}`;
    const sub = [meta.year, meta.set, meta.number ? '#' + meta.number : '', meta.variant || meta.rarity].filter(Boolean).join('  •  ');
    fitFont(x, sub, rw, 34, 400, F); x.fillText(sub, rx, y);
    y += 50;
    // grade box + subgrades
    if (grade) {
      rr(x, rx, y, 250, 210, 22); x.fillStyle = b.c1; x.fill();
      x.fillStyle = onC1; x.textAlign = 'center';
      fitFont(x, String(grade.final), 210, 120, 800, F); x.fillText(String(grade.final), rx + 125, y + 125);
      fitFont(x, grade.word, 220, 34, 600, F); x.fillText(grade.word, rx + 125, y + 175);
      x.textAlign = 'left';
      const names = [['centering', 'Centering'], ['corners', 'Corners'], ['edges', 'Edges'], ['surface', 'Surface']];
      names.forEach(([k, lab], i) => {
        const yy = y + 36 + i * 48, bx = rx + 440, bw = rw - 440 - 70;
        x.fillStyle = '#ffffff'; x.font = `500 28px ${F}`; x.fillText(lab, rx + 290, yy + 8);
        rr(x, bx, yy - 14, bw, 20, 10); x.fillStyle = 'rgba(255,255,255,.14)'; x.fill();
        rr(x, bx, yy - 14, Math.max(20, bw * (subs[k] / 10)), 20, 10); x.fillStyle = b.c3; x.fill();
        x.fillStyle = '#ffffff'; x.font = `700 28px ${F}`; x.textAlign = 'right'; x.fillText(String(subs[k]), rx + rw, yy + 8); x.textAlign = 'left';
      });
      y += 240;
      x.fillStyle = '#a0a0b0'; x.font = `400 22px ${F}`;
      x.fillText(`Cert #${grade.cert}  •  Estimated grade, see disclaimer`, rx, y);
      y += 50;
    }
    // fields
    const fields = [];
    const add = (k, v) => { if (v !== undefined && v !== null && String(v) !== '') fields.push([k, String(v)]); };
    add('Category', catOf(meta.category).label);
    if (meta.team) add('Team', meta.team); if (meta.position) add('Position', meta.position);
    if (meta.serial) add('Serial #', meta.serial);
    const flags = [meta.rookie && 'Rookie', meta.auto && 'Autograph', meta.relic && 'Memorabilia'].filter(Boolean).join(', ');
    add('Features', flags);
    if (meta.value) add('Est. value', money(meta.value));
    (info?.fields || []).forEach(([k, v]) => add(k, v));
    x.fillStyle = b.c1; x.fillRect(rx, y, 80, 6); y += 40;
    x.fillStyle = '#ffffff'; x.font = `700 32px ${F}`; x.fillText('CARD STATS & INFO', rx, y); y += 20;
    const colW = rw / 2;
    let col = 0, rowY = y + 40, maxY = rowY;
    const limit = 1500;
    for (const [k, v] of fields) {
      x.font = `400 21px ${F}`; x.fillStyle = '#a0a0b0';
      const kk = k.toUpperCase();
      x.fillText(kk.length > 30 ? kk.slice(0, 29) + '…' : kk, rx + col * colW, rowY);
      x.font = `600 27px ${F}`; x.fillStyle = '#ffffff';
      const lines = wrapText(x, v, colW - 24).slice(0, 2);
      lines.forEach((ln, i) => x.fillText(ln, rx + col * colW, rowY + 32 + i * 30));
      const hgt = 48 + lines.length * 30;
      maxY = Math.max(maxY, rowY + hgt);
      if (col === 1) { rowY = maxY; col = 0; } else col = 1;
      if (rowY > limit) break;
    }
    y = Math.max(maxY, rowY) + 30;
    // long texts (attacks, rules, flavor …) under the slab + stats, full width
    const ty0 = Math.max(y, 270 + sh + 40);
    y = ty0;
    for (const [k, v] of (info?.texts || [])) {
      if (y > 1990) break;
      x.fillStyle = b.c1; x.font = `700 26px ${F}`;
      x.fillText(k.toUpperCase().slice(0, 70), 60, y); y += 34;
      x.fillStyle = '#e8e8ee'; x.font = `400 25px ${F}`;
      const lines = wrapText(x, v, W - 120);
      for (const ln of lines) { if (y > 2000) { x.fillText('…', 60, y); y += 30; break; } x.fillText(ln, 60, y); y += 32; }
      y += 14;
    }
    // footer
    x.fillStyle = 'rgba(255,255,255,.07)'; x.fillRect(0, 2090, W, 110);
    x.fillStyle = '#a0a0b0'; x.font = `400 21px ${F}`;
    const disc = 'Condition grade is an automated estimate produced by this tool. It is not a PSA, BGS, SGC or CGC grade and is not affiliated with any grading company.';
    wrapText(x, disc, W - 120).forEach((ln, i) => x.fillText(ln, 60, 2135 + i * 28));
    if (notesOf(info)) { x.textAlign = 'right'; x.fillText(notesOf(info), W - 60, 2185); x.textAlign = 'left'; }
    return c;
  }
  const notesOf = info => info?.source ? 'Data: ' + ({ pokemon: 'pokemontcg.io', magic: 'Scryfall', yugioh: 'YGOPRODeck' }[info.source] || info.source) : '';

  return { spec, renderLabel, renderSlab, renderSheet, DEF };
})();

/* Exporting + printing at real size */
const Out = {
  async blob(canvas, fmt, q = 0.92) {
    if (fmt === 'png') return canvasToBlob(canvas, 'image/png');
    const flat = flatten(canvas, '#ffffff');
    return canvasToBlob(flat, fmt === 'webp' ? 'image/webp' : 'image/jpeg', q);
  },
  async download(canvas, fmt, name) {
    const ext = fmt === 'jpeg' ? 'jpg' : fmt;
    saveAs(await this.blob(canvas, fmt === 'jpg' ? 'jpeg' : fmt), `${name}.${ext}`);
  },
  async pdf(canvas, name) {
    await loadScript('https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js');
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({ unit: 'in', format: 'letter', orientation: 'portrait' });
    pdf.addImage(flatten(canvas, '#ffffff').toDataURL('image/jpeg', 0.95), 'JPEG', 0, 0, 8.5, 11);
    pdf.save(name + '.pdf');
  },
  /* prints canvas at an exact physical size in inches; copies = repeated tiles */
  print(canvas, wIn, hIn, copies = 1) {
    const area = $('#printArea');
    const url = canvas.toDataURL('image/png');
    area.innerHTML = '';
    for (let i = 0; i < copies; i++) {
      const im = new Image(); im.src = url;
      im.style.cssText = `width:${wIn}in;height:${hIn}in;`;
      area.appendChild(im);
    }
    const imgs = $$('img', area);
    Promise.all(imgs.map(i => i.decode ? i.decode().catch(() => { }) : Promise.resolve())).then(() => {
      document.body.classList.add('printing');
      window.print();
      setTimeout(() => { document.body.classList.remove('printing'); area.innerHTML = ''; }, 500);
    });
  },
};
