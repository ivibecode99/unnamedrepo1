/* Collection page, card detail modal, picker and listing helper */
const Collection = (() => {
  const sel = new Set();
  const F = { q: '', cat: '', status: '', sort: 'new' };

  function filtered() {
    let l = Cards.list();
    const q = F.q.trim().toLowerCase();
    if (q) l = l.filter(c => [c.name, c.set, c.year, c.number, c.team, c.rarity, c.variant, c.notes].join(' ').toLowerCase().includes(q));
    if (F.cat) l = l.filter(c => c.category === F.cat || (F.cat === 'tcg' && isTCG(c.category)) || (F.cat === 'sport' && isSport(c.category)));
    if (F.status === 'graded') l = l.filter(c => c.grade);
    if (F.status === 'ungraded') l = l.filter(c => !c.grade);
    if (F.status === 'review') l = l.filter(c => c.status === 'review' || c.status === 'new');
    if (F.status === 'listed') l = l.filter(c => c.listed);
    const s = {
      new: (a, b) => b.createdAt - a.createdAt, old: (a, b) => a.createdAt - b.createdAt,
      name: (a, b) => (a.name || '').localeCompare(b.name || ''), value: (a, b) => (b.value || 0) - (a.value || 0),
      grade: (a, b) => (b.grade?.final || 0) - (a.grade?.final || 0),
    }[F.sort];
    return l.sort(s);
  }

  function tile(c, onClick, selectable = true) {
    const d = document.createElement('div');
    d.className = 'tile' + (sel.has(c.id) ? ' sel' : '');
    d.innerHTML = `
      ${selectable ? `<label class="tsel"><input type="checkbox" ${sel.has(c.id) ? 'checked' : ''}></label>` : ''}
      <div class="timg"><img alt=""></div>
      <div class="tmeta"><b>${esc(c.name || 'Unidentified card')}</b>
        <span>${esc([c.year, c.set, c.number && '#' + c.number].filter(Boolean).join(' · ') || catOf(c.category).label)}</span>
        <div class="badges">
          <i class="b cat">${esc(catOf(c.category).label.split(' (')[0])}</i>
          ${c.grade ? `<i class="b grade">${c.grade.final}</i>` : ''}
          ${c.status === 'identifying' ? '<i class="b wait">reading…</i>' : (c.status === 'review' || c.status === 'new') && !c.name ? '<i class="b warn">needs info</i>' : ''}
          ${c.listed ? `<i class="b ok">${esc(c.listed.where)}</i>` : ''}
          ${c.value ? `<i class="b val">${money(c.value)}</i>` : ''}
        </div></div>`;
    Img.url(imgKey(c.id, 'thumb')).then(u => { if (u) $('img', d).src = u; });
    d.onclick = e => {
      if (e.target.closest('.tsel')) return;
      onClick(c);
    };
    const cb = $('input', d);
    if (cb) cb.onchange = () => { cb.checked ? sel.add(c.id) : sel.delete(c.id); d.classList.toggle('sel', cb.checked); updateBar(); };
    return d;
  }

  function updateBar() {
    $('#selCount').textContent = sel.size ? `${sel.size} selected` : '';
    $$('.needsel').forEach(b => b.disabled = !sel.size);
  }

  function render() {
    const all = Cards.list(), l = filtered();
    $('#collStats').innerHTML = `<b>${all.length}</b> cards · <b>${all.filter(c => c.grade).length}</b> graded · est. value <b>${money(all.reduce((a, c) => a + (+c.value || 0) * (c.qty || 1), 0)) || '$0.00'}</b>`;
    const g = $('#collGrid');
    g.innerHTML = '';
    if (!l.length) { g.innerHTML = `<div class="empty">${all.length ? 'No cards match your filters.' : 'Nothing here yet – scan or upload some cards on the <a href="#scan">Scan</a> page.'}</div>`; updateBar(); return; }
    l.forEach(c => g.appendChild(tile(c, c => openCard(c.id))));
    updateBar();
  }

  const target = () => { const l = filtered(); return sel.size ? l.filter(c => sel.has(c.id)) : l; };

  function listingCSV(cards) {
    const brand = Brand.get();
    const data = cards.map(c => ({
      Title: CardOps.listingTitle(c, brand), Description: CardOps.listingDescription(c, brand).replace(/\n/g, ' | '),
      Price: c.value ?? '', Quantity: c.qty ?? 1, Category: catOf(c.category).label,
      Condition: c.grade ? `Graded (self) ${c.grade.final}` : 'Ungraded', Grade: c.grade?.final ?? '', 'Card #': c.number || '', Set: c.set || '', Year: c.year || '',
    }));
    saveAs(new Blob([CardOps.toCSV(data)], { type: 'text/csv;charset=utf-8' }), 'cardvault-listing-sheet.csv');
  }

  function init() {
    fillCatSelect($('#fCat'), { includeAuto: false });
    $('#fCat').insertAdjacentHTML('afterbegin', '<option value="">All categories</option><option value="tcg">All TCG</option><option value="sport">All sports</option>');
    $('#fCat').value = '';
    $('#fQ').oninput = debounce(e => { F.q = e.target.value; render(); }, 150);
    $('#fCat').onchange = e => { F.cat = e.target.value; render(); };
    $('#fStatus').onchange = e => { F.status = e.target.value; render(); };
    $('#fSort').onchange = e => { F.sort = e.target.value; render(); };
    $('#selAll').onclick = () => { const l = filtered(); const all = l.every(c => sel.has(c.id)); l.forEach(c => all ? sel.delete(c.id) : sel.add(c.id)); render(); };
    $('#exCSV').onclick = () => { const t = target(); if (!t.length) return toast('Nothing to export'); CardOps.downloadCSV(t); };
    $('#exXLSX').onclick = async () => { const t = target(); if (!t.length) return toast('Nothing to export'); try { await CardOps.downloadXLSX(t); } catch (e) { toast(e.message, 'err'); } };
    $('#exList').onclick = () => { const t = target(); if (!t.length) return toast('Nothing to export'); listingCSV(t); };
    $('#delSel').onclick = async () => { if (!sel.size || !confirm(`Delete ${sel.size} card(s)? This can't be undone.`)) return; for (const id of [...sel]) await Cards.remove(id); sel.clear(); };
    document.addEventListener('cards-changed', () => { if ($('#page-collection').classList.contains('active')) render(); });
  }
  return { init, render, tile, sel };
})();

/* Pick one card from the collection (used by the Slab Studio) */
function pickCard(cb) {
  const body = Modal.open(`<h2>Choose a card</h2><input id="pkQ" placeholder="Search your collection…" class="full"><div class="grid" id="pkGrid"></div>`, 'wide');
  const draw = () => {
    const q = $('#pkQ', body).value.toLowerCase();
    const g = $('#pkGrid', body); g.innerHTML = '';
    const l = Cards.list().filter(c => !q || [c.name, c.set, c.year, c.number].join(' ').toLowerCase().includes(q));
    if (!l.length) g.innerHTML = '<div class="empty">No cards yet.</div>';
    l.forEach(c => g.appendChild(Collection.tile(c, c => { Modal.close(); cb(c); }, false)));
  };
  $('#pkQ', body).oninput = draw; draw();
}

/* ---------- card detail modal ---------- */
function openCard(id) {
  let card = Cards.get(id);
  if (!card) return;
  const body = Modal.open('<div class="mc"></div>', 'wide');
  const root = $('.mc', body);
  let side = 'front';
  const ocrBusy = () => card.status === 'identifying';

  async function draw() {
    card = Cards.get(id);
    if (!card) return Modal.close();
    const cat = catOf(card.category);
    const sport = cat.kind === 'sport';
    const hasApi = !!cat.api;
    const sides = [['front', 'Front'], ...(card.hasBack ? [['back', 'Back']] : []), ...(card.hasDigital ? [['digital', 'HQ digital']] : [])];
    if (!sides.some(s => s[0] === side)) side = 'front';
    root.innerHTML = `
    <div class="mc-left">
      <div class="mc-img"><img id="mcImg" alt=""></div>
      <div class="chips">${sides.map(([k, l]) => `<button class="chip ${k === side ? 'on' : ''}" data-side="${k}">${l}</button>`).join('')}</div>
      <div class="row wrap">
        <button class="btn" id="mcRot">⟳ Rotate</button>
        <button class="btn" id="mcDl">⬇ Images</button>
      </div>
    </div>
    <div class="mc-right">
      <h2>${esc(card.name || 'Unidentified card')} ${card.grade ? `<span class="gbadge">${card.grade.final}</span>` : ''}</h2>
      <p class="muted">${esc([card.year, card.set, card.number && '#' + card.number, card.rarity].filter(Boolean).join(' · ') || cat.label)} ${card.value ? ' · est. ' + money(card.value) : ''}</p>
      ${ocrBusy() ? '<div class="note wait">Reading the card with OCR… this fills itself in when done.</div>' : ''}
      ${card.error ? `<div class="note warn">Auto-identify problem: ${esc(card.error)}</div>` : ''}
      <div class="actions">
        <button class="btn primary" id="mcSlab">🏷 Grade &amp; slab</button>
        <button class="btn" id="mcEbay">List on eBay</button>
        <button class="btn" id="mcCollx">List on CollX</button>
        <button class="btn" id="mcId" ${ocrBusy() ? 'disabled' : ''}>↻ Re-read scan</button>
        <button class="btn danger" id="mcDel">Delete</button>
      </div>

      <section><h3>Identify / look up</h3>
        <div class="row wrap">
          <select id="mcCat" class="cat-select"></select>
          <input id="mcQ" placeholder="Card / player name" value="${esc(card.name)}">
          <input id="mcN" placeholder="# (opt.)" size="6" value="${esc(card.number)}">
          <button class="btn primary" id="mcSearch">${hasApi ? 'Search' : 'Search web'}</button>
        </div>
        ${card.ocr?.length ? `<div class="chips small"><span class="muted">OCR saw:</span> ${card.ocr.map(t => `<button class="chip" data-ocr="${esc(t)}">${esc(t)}</button>`).join('')}</div>` : ''}
        <div id="mcRes" class="results"></div>
        ${!hasApi ? '<p class="muted small">No free public database exists for this category – fill the details below. “Search web” opens an image/price search.</p>' : ''}
      </section>

      <section><h3>Details</h3>
        <div class="form">
          ${fld('name', sport ? 'Player' : 'Name')}${fld('set', sport ? 'Set / brand' : 'Set')}${fld('year', 'Year')}${fld('number', 'Card #')}
          ${fld('rarity', sport ? 'Parallel / insert' : 'Rarity')}${fld('variant', sport ? 'Variation' : 'Variant (holo, 1st Ed…)')}
          ${sport ? fld('team', 'Team') + fld('position', 'Position') + fld('serial', 'Serial # (e.g. 12/99)') : ''}
          ${fld('qty', 'Quantity', 'number')}${fld('paid', 'Paid ($)', 'number')}${fld('value', 'Est. value ($)', 'number')}
        </div>
        ${sport ? `<div class="row wrap checks">${chk('rookie', 'Rookie card')}${chk('auto', 'Autograph')}${chk('relic', 'Memorabilia / patch')}</div>` : ''}
        <label class="lab">Notes<textarea id="f_notes" rows="2">${esc(card.notes || '')}</textarea></label>
      </section>

      ${card.info ? `<section><h3>Card stats <small class="muted">· ${esc({ pokemon: 'pokemontcg.io', magic: 'Scryfall', yugioh: 'YGOPRODeck' }[card.info.source] || '')}</small></h3>
        <div class="stats">${(card.info.fields || []).map(([k, v]) => `<div><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join('')}</div>
        ${(card.info.texts || []).map(([k, v]) => `<div class="textblock"><h4>${esc(k)}</h4><p>${esc(v)}</p></div>`).join('')}
        ${card.info.url ? `<a href="${esc(card.info.url)}" target="_blank" rel="noopener">Open source page ↗</a>` : ''}</section>` : ''}
      ${card.grade ? `<section><h3>Grade</h3><p><b>${card.grade.final} ${esc(card.grade.word || '')}</b> · centering ${card.grade.subs.centering} · corners ${card.grade.subs.corners} · edges ${card.grade.subs.edges} · surface ${card.grade.subs.surface} · cert ${esc(card.grade.cert || '')}</p></section>` : ''}
    </div>`;
    fillCatSelect($('#mcCat', root), { value: card.category });
    Img.url(imgKey(id, side)).then(u => { if (u) $('#mcImg', root).src = u; });
    wire();
  }
  const fld = (k, label, type = 'text') => `<label class="lab">${label}<input id="f_${k}" type="${type}" ${type === 'number' ? 'step="any"' : ''} value="${esc(card[k] ?? '')}"></label>`;
  const chk = (k, label) => `<label class="chk"><input type="checkbox" id="f_${k}" ${card[k] ? 'checked' : ''}> ${label}</label>`;

  function wire() {
    $$('[data-side]', root).forEach(b => b.onclick = () => { side = b.dataset.side; draw(); });
    $$('[data-ocr]', root).forEach(b => b.onclick = () => { $('#mcQ', root).value = b.dataset.ocr; $('#mcSearch', root).click(); });
    // live-saving fields
    ['name', 'set', 'year', 'number', 'rarity', 'variant', 'team', 'position', 'serial', 'qty', 'paid', 'value'].forEach(k => {
      const e = $('#f_' + k, root); if (!e) return;
      e.onchange = () => { const c = Cards.get(id); c[k] = e.type === 'number' ? (e.value === '' ? '' : +e.value) : e.value.trim(); Cards.save(c); if (k === 'name') { $('h2', root).firstChild.textContent = (c.name || 'Unidentified card') + ' '; } };
    });
    ['rookie', 'auto', 'relic'].forEach(k => { const e = $('#f_' + k, root); if (e) e.onchange = () => { const c = Cards.get(id); c[k] = e.checked; Cards.save(c); }; });
    $('#f_notes', root).onchange = e => { const c = Cards.get(id); c.notes = e.target.value; Cards.save(c); };
    $('#mcCat', root).onchange = e => { const c = Cards.get(id); c.category = e.target.value; Cards.save(c); draw(); };

    $('#mcSearch', root).onclick = async () => {
      const cat = $('#mcCat', root).value, name = $('#mcQ', root).value.trim(), number = $('#mcN', root).value.trim();
      const res = $('#mcRes', root);
      if (!name) return toast('Type a name first');
      if (!catOf(cat).api) { window.open('https://www.google.com/search?tbm=isch&q=' + encodeURIComponent([name, number, card.year, card.set, catOf(cat).label.split(' (')[0], 'card'].filter(Boolean).join(' ')), '_blank'); return; }
      res.innerHTML = '<div class="muted">Searching…</div>';
      try {
        const list = await Lookup.search(cat, { name, number });
        if (!list.length) { res.innerHTML = '<div class="muted">No matches. Try fewer words, or check the spelling.</div>'; return; }
        res.innerHTML = '';
        list.forEach(r => {
          const d = document.createElement('div'); d.className = 'rtile2';
          d.innerHTML = `<img src="${esc(r.thumb || '')}" alt="" loading="lazy"><b>${esc(r.name)}</b><span>${esc([r.set, r.number && '#' + r.number].filter(Boolean).join(' · '))}</span>${r.market != null ? `<i>${money(r.market)}</i>` : ''}`;
          d.onclick = async () => { res.innerHTML = '<div class="muted">Applying + downloading the HQ image…</div>'; await CardOps.applyResult(Cards.get(id), r); toast('Card info applied', 'ok'); draw(); };
          res.appendChild(d);
        });
      } catch (e) { res.innerHTML = `<div class="note warn">${esc(e.message)}</div>`; }
    };
    $('#mcSlab', root).onclick = () => { Modal.close(); location.hash = '#studio'; Studio.loadCard(id); };
    $('#mcEbay', root).onclick = () => openListing(id, 'eBay');
    $('#mcCollx', root).onclick = () => openListing(id, 'CollX');
    $('#mcId', root).onclick = () => { CardOps.queue(id); toast('Reading scan…'); setTimeout(draw, 300); };
    $('#mcDel', root).onclick = async () => { if (confirm('Delete this card?')) { await Cards.remove(id); Modal.close(); } };
    $('#mcRot', root).onclick = async () => {
      const key = imgKey(id, side);
      const b = await DB.get(key); if (!b) return;
      const c = ImgTools.rotate(await blobToCanvas(b));
      await DB.put(key, await canvasToBlob(c, side === 'digital' ? 'image/png' : 'image/jpeg', 0.92)); Img.invalidate(key);
      if (side === 'front') { await DB.put(imgKey(id, 'thumb'), await ImgTools.thumb(c)); Img.invalidate(imgKey(id, 'thumb')); }
      draw(); document.dispatchEvent(new CustomEvent('cards-changed', { detail: id }));
    };
    $('#mcDl', root).onclick = async () => {
      const c = Cards.get(id);
      for (const s of ['front', 'back', 'digital']) { const b = await DB.get(imgKey(id, s)); if (b) saveAs(b, `${slug(c.name)}-${s}.${s === 'digital' ? 'png' : 'jpg'}`); }
    };
  }

  const onChange = e => { if (e.detail === id && Modal.el && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) draw(); };
  document.addEventListener('cards-changed', onChange);
  const prevClose = Modal.onClose;
  Modal.onClose = () => { document.removeEventListener('cards-changed', onChange); prevClose && prevClose(); };
  draw();
}

/* ---------- listing helper ---------- */
async function openListing(id, where) {
  const card = Cards.get(id);
  const brand = Brand.get();
  const body = Modal.open(`
    <h2>List on ${where}</h2>
    <div class="note">${where} doesn't let a website with no server post listings (it needs account keys and a secret that can't live safely in a static page).
    So this builds the whole listing for you: copy the title + description, download the photos, then open ${where}'s listing page and paste.</div>
    <label class="lab">Title <small id="ltN"></small><input id="ltT" class="full"></label>
    <div class="row wrap">
      <label class="lab">Price ($)<input id="ltP" type="number" step="0.01" value="${card.value ?? ''}"></label>
      <label class="lab">Quantity<input id="ltQ" type="number" value="${card.qty ?? 1}"></label>
    </div>
    <label class="lab">Description<textarea id="ltD" rows="9" class="full"></textarea></label>
    <div class="row wrap">
      <button class="btn" id="ltCT">Copy title</button><button class="btn" id="ltCD">Copy description</button><button class="btn" id="ltPh">⬇ Download photos</button>
      <button class="btn" id="ltComps">Check sold prices</button>
      <button class="btn primary" id="ltGo">Copy all &amp; open ${where} ↗</button>
    </div>
    <label class="chk"><input type="checkbox" id="ltMark" ${card.listed ? 'checked' : ''}> Mark this card as listed on ${where} in my collection</label>`, '');
  $('#ltT', body).value = CardOps.listingTitle(card, brand);
  $('#ltD', body).value = CardOps.listingDescription(card, brand);
  const cnt = () => $('#ltN', body).textContent = `(${$('#ltT', body).value.length}/80)`;
  $('#ltT', body).oninput = cnt; cnt();
  const copy = async t => { try { await navigator.clipboard.writeText(t); toast('Copied', 'ok'); } catch { toast('Copy failed – select the text and copy it manually', 'err'); } };
  $('#ltCT', body).onclick = () => copy($('#ltT', body).value);
  $('#ltCD', body).onclick = () => copy($('#ltD', body).value);
  $('#ltPh', body).onclick = async () => { for (const s of ['front', 'back', 'digital']) { const b = await DB.get(imgKey(id, s)); if (b) saveAs(b, `${slug(card.name)}-${s}.${s === 'digital' ? 'png' : 'jpg'}`); } };
  $('#ltComps', body).onclick = () => window.open('https://www.ebay.com/sch/i.html?LH_Sold=1&LH_Complete=1&_nkw=' + encodeURIComponent($('#ltT', body).value.split(' ').slice(0, 8).join(' ')), '_blank');
  $('#ltGo', body).onclick = async () => {
    await copy($('#ltT', body).value + '\n\n' + $('#ltD', body).value);
    const c = Cards.get(id);
    c.value = $('#ltP', body).value === '' ? c.value : +$('#ltP', body).value; c.qty = +$('#ltQ', body).value || 1;
    if ($('#ltMark', body).checked) c.listed = { where, at: Date.now() }; else delete c.listed;
    Cards.save(c);
    window.open(where === 'eBay' ? 'https://www.ebay.com/sl/sell' : 'https://collx.app/', '_blank');
  };
}
