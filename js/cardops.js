/* Card operations shared by Scan / Collection / Studio: create, identify (OCR → lookup), apply lookup result, export */
const CardOps = (() => {
  async function create({ front, back, category = 'auto-tcg' }) {
    const id = uid();
    const card = { id, createdAt: Date.now(), category, name: '', set: '', year: '', number: '', rarity: '', variant: '', qty: 1, status: 'new', hasBack: !!back };
    front = ImgTools.limit(front);
    await DB.put(imgKey(id, 'front'), await canvasToBlob(front, 'image/jpeg', 0.92));
    await DB.put(imgKey(id, 'thumb'), await ImgTools.thumb(front));
    if (back) await DB.put(imgKey(id, 'back'), await canvasToBlob(ImgTools.limit(back), 'image/jpeg', 0.92));
    Cards.save(card);
    return card;
  }

  async function applyResult(card, r, { fetchImage = true } = {}) {
    card.category = r.category || card.category;
    card.name = r.name || card.name; card.set = r.set || ''; card.year = r.year || card.year;
    card.number = r.number || ''; card.rarity = r.rarity || '';
    card.info = { source: r.source, id: r.id, fields: r.fields, texts: r.texts, url: r.url, imageUrl: r.image };
    if (r.market != null) { card.market = r.market; if (!card.value) card.value = r.market; }
    card.status = 'identified';
    if (fetchImage && r.image) {
      try {
        const c = await Lookup.imageCanvas(r.image);
        Img.invalidate(imgKey(card.id, 'digital'));
        await DB.put(imgKey(card.id, 'digital'), await canvasToBlob(c, 'image/png'));
        card.hasDigital = true;
      } catch { card.hasDigital = !!card.hasDigital; }
    }
    Cards.save(card);
    return card;
  }

  /* OCR the front scan, look the name up, attach the best match. Never throws. */
  async function identify(id) {
    let card = Cards.get(id);
    if (!card) return;
    card.status = 'identifying'; Cards.save(card);
    try {
      const blob = await DB.get(imgKey(id, 'front'));
      const canvas = await blobToCanvas(blob);
      const o = await OCR.identify(canvas, card.category);
      card = Cards.get(id) || card;
      card.ocr = o.lines;
      if (o.year && !card.year) card.year = o.year;
      if (o.name && !card.name) card.name = o.name;
      if (isTCG(card.category) && o.name) {
        let res = await Lookup.search(card.category, { name: o.name, number: o.number });
        if (!res.length && o.number) res = await Lookup.search(card.category, { name: o.name });
        if (res.length) { await applyResult(card, res[0]); return; }
      }
      card.status = 'review';
    } catch (e) {
      card = Cards.get(id) || card;
      card.status = 'review'; card.error = String(e.message || e);
    }
    Cards.save(card);
  }

  /* sequential background queue so fast-scanning doesn't hammer OCR / APIs */
  const q = []; let busy = false;
  async function pump() {
    if (busy) return; busy = true;
    while (q.length) { await identify(q.shift()); }
    busy = false;
  }
  const queue = id => { q.push(id); pump(); };

  /* ---------- export ---------- */
  function gradeText(c) { return c.grade ? `${c.grade.final} ${c.grade.word || ''}`.trim() : ''; }
  function rows(cards) {
    return cards.map(c => ({
      'Name / Player': c.name || '', Category: catOf(c.category).label, Year: c.year || '', Set: c.set || '', 'Card #': c.number || '',
      'Rarity / Parallel': [c.rarity, c.variant].filter(Boolean).join(' / '), Team: c.team || '', Position: c.position || '', 'Serial #': c.serial || '',
      Rookie: c.rookie ? 'Yes' : '', Autograph: c.auto ? 'Yes' : '', Memorabilia: c.relic ? 'Yes' : '',
      Grade: c.grade ? c.grade.final : '', 'Grade label': c.grade?.word || '', 'Centering': c.grade?.subs?.centering ?? '', Corners: c.grade?.subs?.corners ?? '', Edges: c.grade?.subs?.edges ?? '', Surface: c.grade?.subs?.surface ?? '', 'Cert #': c.grade?.cert || '',
      Quantity: c.qty ?? 1, 'Paid ($)': c.paid ?? '', 'Est. value ($)': c.value ?? '', 'Market price ($)': c.market ?? '',
      Listed: c.listed ? `${c.listed.where} ${new Date(c.listed.at).toLocaleDateString()}` : '', Notes: c.notes || '',
      Stats: (c.info?.fields || []).map(([k, v]) => `${k}: ${v}`).join(' | '),
      Added: new Date(c.createdAt).toISOString().slice(0, 10), ID: c.id,
    }));
  }
  function toCSV(data) {
    if (!data.length) return '';
    const cols = Object.keys(data[0]);
    const cell = v => { v = String(v ?? ''); return /[",\n\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
    return '﻿' + [cols.map(cell).join(','), ...data.map(r => cols.map(k => cell(r[k])).join(','))].join('\r\n');
  }
  const stamp = () => new Date().toISOString().slice(0, 10);
  const downloadCSV = (cards, name = 'cardvault-collection') => saveAs(new Blob([toCSV(rows(cards))], { type: 'text/csv;charset=utf-8' }), `${name}-${stamp()}.csv`);
  async function downloadXLSX(cards) {
    await loadScript('https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js');
    const ws = XLSX.utils.json_to_sheet(rows(cards));
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Collection');
    XLSX.writeFile(wb, `cardvault-collection-${stamp()}.xlsx`);
  }

  /* ---------- listing text ---------- */
  function listingTitle(c, brand) {
    const g = c.grade ? `${brand.name} ${c.grade.final}` : '';
    const must = [c.year, c.set, c.name, c.number ? '#' + c.number : ''].filter(Boolean);
    const opt = [c.rarity, c.variant, c.serial ? c.serial : '', c.rookie ? 'RC Rookie' : '', c.auto ? 'Auto' : '', c.relic ? 'Patch' : '', g, catOf(c.category).kind === 'tcg' ? catOf(c.category).label.split(' (')[0] : ''].filter(Boolean);
    let t = must.join(' ');
    for (const o of opt) if ((t + ' ' + o).length <= 80) t += ' ' + o;
    return t.slice(0, 80);
  }
  function listingDescription(c, brand) {
    const L = [];
    L.push(listingTitle(c, brand), '');
    L.push(`Category: ${catOf(c.category).label}`);
    if (c.set) L.push(`Set: ${c.set}`); if (c.year) L.push(`Year: ${c.year}`); if (c.number) L.push(`Card number: ${c.number}`);
    if (c.rarity) L.push(`Rarity: ${c.rarity}`); if (c.variant) L.push(`Variant / parallel: ${c.variant}`);
    if (c.team) L.push(`Team: ${c.team}`); if (c.position) L.push(`Position: ${c.position}`); if (c.serial) L.push(`Serial: ${c.serial}`);
    if (c.rookie) L.push('Rookie card'); if (c.auto) L.push('Autographed'); if (c.relic) L.push('Memorabilia / patch card');
    (c.info?.fields || []).slice(0, 12).forEach(([k, v]) => L.push(`${k}: ${v}`));
    if (c.grade) L.push('', `Condition: self-graded ${c.grade.final} (${c.grade.word}) – centering ${c.grade.subs.centering}, corners ${c.grade.subs.corners}, edges ${c.grade.subs.edges}, surface ${c.grade.subs.surface}. Not graded by PSA/BGS/SGC/CGC.`);
    if (c.notes) L.push('', c.notes);
    L.push('', 'Card ships in a penny sleeve + top loader, tracked shipping. See photos for exact condition.');
    return L.join('\n');
  }

  return { create, applyResult, identify, queue, rows, toCSV, downloadCSV, downloadXLSX, listingTitle, listingDescription, gradeText };
})();
