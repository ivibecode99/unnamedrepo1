/* Slab Studio: pick a card / upload / web image → grade → label + slab + info sheet → download / print */
const Studio = (() => {
  const SUBS = [['centering', 'Centering'], ['corners', 'Corners'], ['edges', 'Edges'], ['surface', 'Surface']];
  const ST = {
    cardId: null, imgs: { scan: null, digital: null, upload: null }, use: null, info: null,
    meta: { category: 'pokemon', name: '', set: '', year: '', number: '', rarity: '', variant: '' },
    subs: { centering: 9, corners: 9, edges: 9, surface: 9 }, scale: Store.get('scale', 'int'), cert: Grader.newCert(), override: '', notes: [], measures: {}, digitalResult: null,
  };
  let cutCache = { src: null, out: null };

  const grade = () => {
    const final = ST.override !== '' && !isNaN(+ST.override) ? clamp(+ST.override, 1, 10) : Grader.finalGrade(ST.subs, ST.scale);
    return { final, word: Grader.wordFor(final), cert: ST.cert, subs: { ...ST.subs }, scale: ST.scale };
  };
  const labelData = () => {
    const m = ST.meta, g = grade();
    const v = id => $('#' + id).value.trim();
    return {
      line1: v('l_1') || [m.year, m.set].filter(Boolean).join(' ') || 'YEAR SET',
      line2: v('l_2') || [m.name, m.number && '#' + m.number].filter(Boolean).join(' ') || 'CARD NAME',
      line3: v('l_3') || [m.variant, m.rarity].filter(Boolean).join(' ') || '',
      grade: g.final, word: g.word, cert: g.cert,
    };
  };
  const cardCanvas = () => {
    const src = ST.imgs[ST.use];
    if (!src) return null;
    if (!$('#stBg').checked) return src;
    if (cutCache.src !== src) cutCache = { src, out: ImgTools.cutout(src) };
    return cutCache.out;
  };

  /* ---------- preview ---------- */
  let token = 0;
  const refresh = debounce(async () => {
    const t = ++token, b = await Brand.resolve();
    if (t !== token) return;
    const d = labelData(), s = Slab.spec();
    const lab = Slab.renderLabel(d, b, 220);
    const lc = $('#labelCv'); lc.width = lab.width; lc.height = lab.height; lc.getContext('2d').drawImage(lab, 0, 0);
    const slab = Slab.renderSlab(d, b, { cardCanvas: cardCanvas(), dpi: 130 });
    const sc = $('#slabCv'); sc.width = slab.width; sc.height = slab.height; sc.getContext('2d').drawImage(slab, 0, 0);
    $('#stDims').textContent = `Label ${s.labelW} × ${s.labelH} in · Slab ${s.slabW} × ${s.slabH} in (change in Settings)`;
    const g = grade();
    $('#stFinal').textContent = `${g.final} · ${g.word}`;
  }, 80);

  /* ---------- source chips ---------- */
  function renderSources() {
    const names = { scan: 'My scan', digital: 'HQ digital (web)', upload: 'Uploaded image' };
    const box = $('#stSources');
    const avail = Object.keys(names).filter(k => ST.imgs[k]);
    if (!avail.length) { box.innerHTML = '<span class="muted">Pick a card, upload an image, or search the web first.</span>'; return; }
    if (!ST.use || !ST.imgs[ST.use]) ST.use = avail[0];
    box.innerHTML = avail.map(k => `<button class="chip ${k === ST.use ? 'on' : ''}" data-use="${k}">${names[k]}</button>`).join('');
    $$('[data-use]', box).forEach(b => b.onclick = () => { ST.use = b.dataset.use; renderSources(); refresh(); });
  }

  function writeMeta() {
    ['name', 'set', 'year', 'number', 'variant', 'rarity'].forEach(k => { const e = $('#m_' + k); if (e) e.value = ST.meta[k] || ''; });
    $('#m_category').value = ST.meta.category;
  }
  function readMeta() { ['name', 'set', 'year', 'number', 'variant', 'rarity'].forEach(k => { const e = $('#m_' + k); if (e) ST.meta[k] = e.value.trim(); }); ST.meta.category = $('#m_category').value; }

  function writeGrade() {
    SUBS.forEach(([k]) => { $('#s_' + k).value = ST.subs[k]; $('#sv_' + k).textContent = ST.subs[k]; });
    $('#stScale').value = ST.scale; $('#stOverride').value = ST.override; $('#stCert').value = ST.cert;
    $('#stNotes').innerHTML = ST.notes.map(n => `<div class="note warn">${esc(n)}</div>`).join('') + (ST.measures.centering ? `<div class="muted small">Measured: ${esc(ST.measures.centering)}${ST.measures.corners ? '<br>' + esc(ST.measures.corners) : ''}</div>` : '');
  }

  /* ---------- loading sources ---------- */
  async function loadCard(id) {
    const card = Cards.get(id);
    if (!card) return;
    ST.cardId = id;
    ST.imgs.scan = await blobToCanvas(await DB.get(imgKey(id, 'front')));
    const db = await DB.get(imgKey(id, 'digital'));
    ST.imgs.digital = db ? await blobToCanvas(db) : null;
    ST.imgs.upload = null;
    ST.use = 'scan'; cutCache = { src: null, out: null };
    ST.info = card.info || null;
    ST.meta = { category: card.category === 'auto-tcg' ? 'pokemon' : card.category, name: card.name || '', set: card.set || '', year: card.year || '', number: card.number || '', rarity: card.rarity || '', variant: card.variant || '', team: card.team, position: card.position, serial: card.serial, rookie: card.rookie, auto: card.auto, relic: card.relic, value: card.value };
    if (card.grade) { ST.subs = { ...card.grade.subs }; ST.cert = card.grade.cert || ST.cert; ST.scale = card.grade.scale || ST.scale; ST.override = card.grade.manual ? card.grade.final : ''; ST.notes = []; ST.measures = {}; }
    else { ST.notes = []; ST.measures = {}; }
    ['l_1', 'l_2', 'l_3'].forEach(i => $('#' + i).value = '');
    $('#stPicked').textContent = `Selected: ${card.name || 'Unidentified card'}`;
    writeMeta(); writeGrade(); renderSources(); refresh();
    if (!card.grade) autoGrade(true);
  }

  async function setUpload(file) {
    try {
      let c = await blobToCanvas(file);
      if ($('#stCrop').checked) c = ImgTools.autoCrop(c);
      ST.imgs.upload = ImgTools.limit(c); ST.use = 'upload'; cutCache = { src: null, out: null };
      renderSources(); refresh(); autoGrade(true);
    } catch { toast('Could not read that image', 'err'); }
  }

  async function searchWeb() {
    const cat = $('#stCat').value, name = $('#stName').value.trim(), number = $('#stNum').value.trim(), res = $('#stResults');
    if (!name) return toast('Type a card name');
    if (!catOf(cat).api) { toast('Sports/other cards have no free database – paste an image URL or upload a picture instead'); window.open('https://www.google.com/search?tbm=isch&q=' + encodeURIComponent(name + ' card'), '_blank'); return; }
    res.innerHTML = '<div class="muted">Searching…</div>';
    try {
      const list = await Lookup.search(cat, { name, number });
      if (!list.length) { res.innerHTML = '<div class="muted">No matches.</div>'; return; }
      res.innerHTML = '';
      list.forEach(r => {
        const d = document.createElement('div'); d.className = 'rtile2';
        d.innerHTML = `<img src="${esc(r.thumb || '')}" alt="" loading="lazy"><b>${esc(r.name)}</b><span>${esc([r.set, r.number && '#' + r.number].filter(Boolean).join(' · '))}</span>`;
        d.onclick = async () => {
          try {
            toast('Downloading HQ image…');
            ST.imgs.digital = await Lookup.imageCanvas(r.image);
            ST.use = 'digital'; cutCache = { src: null, out: null };
            ST.info = { source: r.source, id: r.id, fields: r.fields, texts: r.texts, url: r.url, imageUrl: r.image };
            ST.meta = { ...ST.meta, category: r.category, name: r.name, set: r.set || '', year: r.year || '', number: r.number || '', rarity: r.rarity || '', value: r.market ?? ST.meta.value };
            ST.digitalResult = r;
            writeMeta(); renderSources(); refresh(); autoGrade(true);
            $('#stPicked').textContent = `Web card: ${r.name}`;
          } catch (e) { toast(e.message, 'err'); }
        };
        res.appendChild(d);
      });
    } catch (e) { res.innerHTML = `<div class="note warn">${esc(e.message)}</div>`; }
  }

  async function loadUrl() {
    const u = $('#stUrl').value.trim();
    if (!/^https?:\/\//i.test(u)) return toast('Paste a full https:// image address');
    try { ST.imgs.digital = await Lookup.imageCanvas(u); ST.use = 'digital'; cutCache = { src: null, out: null }; renderSources(); refresh(); autoGrade(true); }
    catch (e) { toast(e.message, 'err'); }
  }

  function autoGrade(quiet) {
    const src = ST.imgs[ST.use];
    if (!src) return quiet ? 0 : toast('Choose an image first');
    const r = Grader.analyze(src);
    ST.subs = r.subs; ST.notes = r.notes; ST.measures = r.measures; ST.override = '';
    if (ST.use === 'digital') ST.notes.push('This is a clean digital render, so it scores near-perfect. Grade your own scan to estimate real wear.');
    writeGrade(); refresh();
    if (!quiet) toast('Estimated – adjust the sliders if you disagree', 'ok');
  }

  /* ---------- outputs ---------- */
  const fname = () => slug(ST.meta.name || 'card');
  async function build(dpi = 300, pad = 0.12) {
    const b = await Brand.resolve(), d = labelData();
    return { b, d, label: Slab.renderLabel(d, b, dpi), slab: Slab.renderSlab(d, b, { cardCanvas: cardCanvas(), dpi, pad }) };
  }
  async function dlSheet() {
    const fmt = $('#sheetFmt').value, g = grade();
    const { b, slab } = await build(200, 0.12);
    const sheet = Slab.renderSheet({ meta: { ...ST.meta, value: ST.meta.value }, info: ST.info, grade: g, brand: b, slabCanvas: slab, subs: g.subs });
    if (fmt === 'pdf') { try { await Out.pdf(sheet, fname() + '-report'); } catch (e) { toast(e.message, 'err'); } }
    else await Out.download(sheet, fmt, fname() + '-report');
  }

  async function save() {
    readMeta();
    let card = ST.cardId ? Cards.get(ST.cardId) : null;
    if (!card) {
      const base = ST.imgs.upload || ST.imgs.scan || ST.imgs.digital;
      if (!base) return toast('Choose an image first', 'err');
      card = await CardOps.create({ front: base, category: ST.meta.category });
      ST.cardId = card.id;
    }
    const m = ST.meta;
    Object.assign(card, { category: m.category, name: m.name, set: m.set, year: m.year, number: m.number, rarity: m.rarity, variant: m.variant, status: m.name ? 'identified' : card.status });
    if (ST.info) card.info = ST.info;
    if (m.value != null && !card.value) card.value = m.value;
    if (ST.imgs.digital && !card.hasDigital) { await DB.put(imgKey(card.id, 'digital'), await canvasToBlob(ST.imgs.digital, 'image/png')); card.hasDigital = true; }
    const g = grade();
    card.grade = { ...g, manual: ST.override !== '' };
    Cards.save(card);
    $('#stPicked').textContent = `Selected: ${card.name || 'Unidentified card'}`;
    toast('Saved to your collection', 'ok');
  }

  function init() {
    fillCatSelect($('#stCat'), { includeAuto: true, value: 'auto-tcg' });
    fillCatSelect($('#m_category'), { includeAuto: false, value: 'pokemon' });
    $('#stSubs').innerHTML = SUBS.map(([k, l]) => `<div class="slider"><label>${l}</label><input type="range" id="s_${k}" min="1" max="10" step="0.5" value="9"><b id="sv_${k}">9</b></div>`).join('');
    SUBS.forEach(([k]) => $('#s_' + k).oninput = e => { ST.subs[k] = +e.target.value; ST.override = ''; $('#stOverride').value = ''; $('#sv_' + k).textContent = e.target.value; refresh(); });
    $$('#stTabs button').forEach(b => b.onclick = () => {
      $$('#stTabs button').forEach(x => x.classList.toggle('on', x === b));
      $$('.tabpane').forEach(p => p.classList.toggle('hidden', p.dataset.pane !== b.dataset.tab));
    });
    $('#stPick').onclick = () => pickCard(c => loadCard(c.id));
    $('#stFile').onchange = e => { if (e.target.files[0]) setUpload(e.target.files[0]); e.target.value = ''; };
    $('#stSearch').onclick = searchWeb;
    $('#stName').onkeydown = e => { if (e.key === 'Enter') searchWeb(); };
    $('#stUrlGo').onclick = loadUrl;
    $('#stBg').onchange = refresh;
    $('#stAuto').onclick = () => autoGrade(false);
    $('#stScale').onchange = e => { ST.scale = e.target.value; Store.set('scale', ST.scale); refresh(); };
    $('#stOverride').oninput = e => { ST.override = e.target.value; refresh(); };
    $('#stCert').oninput = e => { ST.cert = e.target.value.trim(); refresh(); };
    $('#stCertNew').onclick = () => { ST.cert = Grader.newCert(); $('#stCert').value = ST.cert; refresh(); };
    ['name', 'set', 'year', 'number', 'variant', 'rarity'].forEach(k => $('#m_' + k).oninput = () => { readMeta(); refresh(); });
    $('#m_category').onchange = () => { readMeta(); };
    ['l_1', 'l_2', 'l_3'].forEach(i => $('#' + i).oninput = refresh);
    $('#stSave').onclick = save;

    $('#dlLabel').onclick = async () => { const { label } = await build(300); await Out.download(label, 'png', fname() + '-label'); };
    $('#prLabel').onclick = async () => { const { label } = await build(300); const s = Slab.spec(); Out.print(label, s.labelW, s.labelH, clamp(+$('#prCopies').value || 1, 1, 60)); };
    $('#dlSlabPng').onclick = async () => { const { slab } = await build(300); await Out.download(slab, 'png', fname() + '-slab'); };
    $('#dlSlabJpg').onclick = async () => { const { slab } = await build(300); await Out.download(slab, 'jpg', fname() + '-slab'); };
    $('#prSlab').onclick = async () => { const { slab } = await build(300, 0); const s = Slab.spec(); Out.print(slab, s.slabW, s.slabH, 1); };
    $('#dlSheet').onclick = dlSheet;
    document.addEventListener('brand-changed', () => { if ($('#page-studio').classList.contains('active')) refresh(); });
    writeGrade(); renderSources();
  }
  return { init, loadCard, refresh, onShow() { refresh(); } };
})();

/* ---------- Brand page ---------- */
const BrandUI = (() => {
  const FONTS = ['Montserrat', 'Oswald', 'Bebas Neue', 'Anton', 'Poppins', 'Roboto Condensed', 'Rajdhani', 'Orbitron', 'Playfair Display', 'Inter'];
  const ids = { name: 'b_name', tagline: 'b_tag', c1: 'b_c1', c3: 'b_c3', c2: 'b_c2', labelBg: 'b_lbg', labelFg: 'b_lfg', font: 'b_font' };

  async function preview() {
    const b = await Brand.resolve(), s = Slab.spec();
    const d = { line1: '2023 SAMPLE SET', line2: 'PLAYER NAME #12', line3: 'REFRACTOR', grade: 9.5, word: 'MINT+', cert: '12345678' };
    const lab = Slab.renderLabel(d, b, 260), c = $('#brandCv'); c.width = lab.width; c.height = lab.height; c.getContext('2d').drawImage(lab, 0, 0);
    const slab = Slab.renderSlab(d, b, { dpi: 110 }), c2 = $('#brandSlabCv'); c2.width = slab.width; c2.height = slab.height; c2.getContext('2d').drawImage(slab, 0, 0);
    $('#brandDims').textContent = `Label prints at ${s.labelW} × ${s.labelH} in`;
  }
  const changed = debounce(() => { preview(); document.dispatchEvent(new CustomEvent('brand-changed')); }, 120);

  function read() {
    const b = Brand.get();
    Object.entries(ids).forEach(([k, id]) => { const e = $('#' + id); if (e) b[k] = e.value; });
    Brand.save(b);
    changed();
  }
  async function fontOptions() {
    const sel = $('#b_font'), cur = Brand.get().font;
    const hasCustom = !!(await DB.get('brand:font'));
    sel.innerHTML = FONTS.map(f => `<option value="${f}" style="font-family:'${f}'">${f}</option>`).join('') + (hasCustom ? '<option value="BrandCustom">★ My uploaded font</option>' : '');
    sel.value = cur;
  }
  function init() {
    const b = Brand.get();
    Object.entries(ids).forEach(([k, id]) => { const e = $('#' + id); if (e && k !== 'font') { e.value = b[k]; e.oninput = read; } });
    fontOptions().then(() => $('#b_font').onchange = read);
    $('#b_logo').onchange = async e => { const f = e.target.files[0]; if (!f) return; await Brand.setLogo(f); toast('Logo saved', 'ok'); changed(); e.target.value = ''; };
    $('#b_logoClear').onclick = async () => { await Brand.setLogo(null); changed(); };
    $('#b_fontFile').onchange = async e => {
      const f = e.target.files[0]; if (!f) return;
      await DB.put('brand:font', f);
      if (await Brand.loadCustomFont()) { const bb = Brand.get(); bb.font = 'BrandCustom'; Brand.save(bb); await fontOptions(); toast('Custom font loaded', 'ok'); changed(); } else toast('Could not read that font file (use .ttf .otf .woff .woff2)', 'err');
      e.target.value = '';
    };
    $('#b_fontClear').onclick = async () => { await DB.del('brand:font'); const bb = Brand.get(); if (bb.font === 'BrandCustom') { bb.font = 'Oswald'; Brand.save(bb); } await fontOptions(); changed(); };
    $('#b_reset').onclick = () => { Store.del('brand'); init(); changed(); };
    preview();
  }
  return { init, onShow() { preview(); } };
})();

/* ---------- Settings page ---------- */
const SettingsUI = (() => {
  async function backup() {
    const keys = await DB.keys(), blobs = {};
    for (const k of keys) blobs[k] = await blobToDataURL(await DB.get(k));
    const ls = {};
    for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k.startsWith('cv.')) ls[k] = localStorage.getItem(k); }
    saveAs(new Blob([JSON.stringify({ v: 1, ls, blobs })], { type: 'application/json' }), `cardvault-backup-${new Date().toISOString().slice(0, 10)}.json`);
  }
  async function restore(file) {
    try {
      const j = JSON.parse(await file.text());
      if (!j.ls || !j.blobs) throw new Error('bad file');
      for (const k in j.ls) localStorage.setItem(k, j.ls[k]);
      for (const k in j.blobs) await DB.put(k, await dataURLToBlob(j.blobs[k]));
      toast('Backup restored', 'ok'); setTimeout(() => location.reload(), 700);
    } catch { toast('That is not a QOG backup file', 'err'); }
  }
  function init() {
    const keys = ['slabW', 'slabH', 'labelW', 'labelH', 'cardW', 'cardH'];
    const draw = () => { const s = Slab.spec(); keys.forEach(k => $('#sp_' + k).value = s[k]); };
    draw();
    keys.forEach(k => $('#sp_' + k).oninput = e => { const s = Slab.spec(); const v = parseFloat(e.target.value); if (v > 0) { s[k] = v; Store.set('spec', s); document.dispatchEvent(new CustomEvent('brand-changed')); } });
    $('#sp_reset').onclick = () => { Store.del('spec'); draw(); document.dispatchEvent(new CustomEvent('brand-changed')); };
    $('#bkExport').onclick = backup;
    $('#bkImport').onchange = e => { if (e.target.files[0]) restore(e.target.files[0]); };
    $('#wipe').onclick = async () => {
      if (!confirm('Delete ALL cards, images, brand settings and options from this browser?')) return;
      if (!confirm('Really? This cannot be undone (export a backup first if unsure).')) return;
      await DB.clear(); Object.keys(localStorage).filter(k => k.startsWith('cv.')).forEach(k => localStorage.removeItem(k)); location.reload();
    };
    if (navigator.storage?.estimate) navigator.storage.estimate().then(e => { $('#storageInfo').textContent = `Using ${(e.usage / 1048576).toFixed(1)} MB of ~${Math.round(e.quota / 1048576)} MB browser storage.`; });
    if (navigator.storage?.persist) navigator.storage.persist();
  }
  return { init, onShow() { if (navigator.storage?.estimate) navigator.storage.estimate().then(e => { $('#storageInfo').textContent = `Using ${(e.usage / 1048576).toFixed(1)} MB of ~${Math.round(e.quota / 1048576)} MB browser storage.`; }); } };
})();
