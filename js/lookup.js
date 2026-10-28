/* Card data + high-quality digital images from free public APIs that allow browser (CORS) access.
   Pokémon: api.pokemontcg.io · Magic: api.scryfall.com · Yu-Gi-Oh!: db.ygoprodeck.com
   Sports cards have no free public database, so those are filled in by hand (or OCR). */
const Lookup = (() => {
  async function getJSON(url, { ms = 20000, soft = false } = {}) {
    const ctl = new AbortController();
    const t = setTimeout(() => ctl.abort(), ms);
    try {
      const r = await fetch(url, { signal: ctl.signal });
      if (soft && (r.status === 404 || r.status === 400)) return null;
      if (!r.ok) throw new Error('Lookup failed (HTTP ' + r.status + ')');
      return await r.json();
    } catch (e) {
      if (e.name === 'AbortError') throw new Error('Lookup timed out – the card database is slow right now, try again');
      throw e;
    } finally { clearTimeout(t); }
  }
  const fieldsOf = () => {
    const f = [];
    const add = (k, v) => { if (v === undefined || v === null || v === '' || (Array.isArray(v) && !v.length)) return; f.push([k, Array.isArray(v) ? v.join(', ') : String(v)]); };
    return { f, add };
  };
  const usd = n => '$' + Number(n).toFixed(2);

  /* ---------- Pokémon ---------- */
  async function pokemon({ name, number }) {
    const clean = (name || '').replace(/["\\]/g, '').trim();
    if (!clean) return [];
    const run = async q => (await getJSON(`https://api.pokemontcg.io/v2/cards?q=${encodeURIComponent(q)}&pageSize=40&orderBy=-set.releaseDate`)).data || [];
    const nq = number ? ` number:"${number}"` : '';
    let list = await run(`name:"${clean}"${nq}`);
    if (!list.length && !/\s/.test(clean)) list = await run(`name:${clean}*${nq}`);
    if (!list.length && number) list = await run(`name:"${clean}"`);
    return list.map(c => {
      const { f, add } = fieldsOf();
      add('Supertype', c.supertype); add('Subtypes', c.subtypes); add('HP', c.hp); add('Type', c.types);
      add('Evolves from', c.evolvesFrom); add('Evolves to', c.evolvesTo);
      add('Retreat cost', c.retreatCost ? c.retreatCost.length + ' (' + c.retreatCost.join(', ') + ')' : '');
      add('Weakness', (c.weaknesses || []).map(w => `${w.type} ${w.value}`));
      add('Resistance', (c.resistances || []).map(w => `${w.type} ${w.value}`));
      add('Set', c.set?.name); add('Series', c.set?.series);
      add('Number', c.number + (c.set?.printedTotal ? '/' + c.set.printedTotal : ''));
      add('Rarity', c.rarity); add('Artist', c.artist); add('Released', c.set?.releaseDate);
      add('Regulation mark', c.regulationMark); add('Pokédex #', c.nationalPokedexNumbers);
      add('Standard', c.legalities?.standard); add('Expanded', c.legalities?.expanded);
      const t = [];
      (c.abilities || []).forEach(a => t.push([`Ability · ${a.name}`, a.text]));
      (c.attacks || []).forEach(a => t.push([`Attack · ${a.name}${a.damage ? ' (' + a.damage + ')' : ''} [${(a.cost || []).join('')}]`, a.text || '—']));
      if (c.rules) t.push(['Rules', c.rules.join(' ')]);
      if (c.flavorText) t.push(['Flavor', c.flavorText]);
      let market = null;
      Object.entries(c.tcgplayer?.prices || {}).forEach(([k, v]) => { if (v.market) { add(`TCGplayer ${k} (market)`, usd(v.market)); if (market == null) market = v.market; } });
      if (c.cardmarket?.prices?.averageSellPrice) add('Cardmarket avg (EUR)', '€' + c.cardmarket.prices.averageSellPrice);
      return { source: 'pokemon', id: c.id, category: 'pokemon', name: c.name, set: c.set?.name, year: (c.set?.releaseDate || '').slice(0, 4), number: c.number, rarity: c.rarity, image: c.images?.large, thumb: c.images?.small, fields: f, texts: t, market, url: c.tcgplayer?.url };
    });
  }

  /* ---------- Magic ---------- */
  async function magic({ name, number }) {
    const nm = (name || '').trim();
    if (!nm) return [];
    const q = nm + (number ? ` cn:${number}` : '');
    const j = await getJSON(`https://api.scryfall.com/cards/search?q=${encodeURIComponent(q)}&unique=prints&order=released&dir=desc`, { soft: true });
    const data = (j && j.data) || [];
    return data.slice(0, 40).map(c => {
      const face = c.card_faces ? c.card_faces[0] : c;
      const imgs = c.image_uris || face.image_uris || {};
      const { f, add } = fieldsOf();
      add('Mana cost', c.mana_cost || face.mana_cost); add('Mana value', c.cmc); add('Type', c.type_line);
      add('Power / Toughness', c.power != null ? `${c.power}/${c.toughness}` : (face.power != null ? `${face.power}/${face.toughness}` : ''));
      add('Loyalty', c.loyalty); add('Colors', c.colors || face.colors); add('Color identity', c.color_identity);
      add('Keywords', c.keywords); add('Set', `${c.set_name} (${(c.set || '').toUpperCase()})`);
      add('Collector #', c.collector_number); add('Rarity', c.rarity); add('Artist', c.artist); add('Released', c.released_at);
      add('Frame / finishes', [c.frame, ...(c.finishes || [])].join(', '));
      const legal = Object.entries(c.legalities || {}).filter(([, v]) => v === 'legal').map(([k]) => k);
      add('Legal in', legal);
      const t = [];
      const faces = c.card_faces || [c];
      faces.forEach(fc => { if (fc.oracle_text) t.push([faces.length > 1 ? 'Text · ' + fc.name : 'Rules text', fc.oracle_text]); });
      if (c.flavor_text || face.flavor_text) t.push(['Flavor', c.flavor_text || face.flavor_text]);
      const p = c.prices || {};
      if (p.usd) add('Price USD', usd(p.usd)); if (p.usd_foil) add('Price USD foil', usd(p.usd_foil)); if (p.usd_etched) add('Price USD etched', usd(p.usd_etched)); if (p.eur) add('Price EUR', '€' + p.eur);
      const market = p.usd ? +p.usd : p.usd_foil ? +p.usd_foil : null;
      return { source: 'magic', id: c.id, category: 'magic', name: c.name, set: c.set_name, year: (c.released_at || '').slice(0, 4), number: c.collector_number, rarity: c.rarity, image: imgs.png || imgs.large, thumb: imgs.small, fields: f, texts: t, market, url: c.scryfall_uri };
    });
  }

  /* ---------- Yu-Gi-Oh! ---------- */
  async function yugioh({ name }) {
    const nm = (name || '').trim();
    if (!nm) return [];
    const j = await getJSON(`https://db.ygoprodeck.com/api/v7/cardinfo.php?fname=${encodeURIComponent(nm)}&misc=yes`, { soft: true });
    const data = (j && j.data) || [];
    return data.slice(0, 40).map(c => {
      const { f, add } = fieldsOf();
      const s0 = (c.card_sets || [])[0];
      add('Type', c.type); add('Race / Type', c.race); add('Attribute', c.attribute); add('Archetype', c.archetype);
      add('Level / Rank', c.level); add('ATK', c.atk); add('DEF', c.def); add('Link rating', c.linkval); add('Pendulum scale', c.scale);
      add('Link markers', c.linkmarkers); add('TCG ban status', c.banlist_info?.ban_tcg); add('OCG ban status', c.banlist_info?.ban_ocg);
      add('TCG release', c.misc_info?.[0]?.tcg_date); add('Set (first print)', s0?.set_name); add('Set code', s0?.set_code); add('Rarity (first print)', s0?.set_rarity);
      add('Views / popularity', c.misc_info?.[0]?.views);
      const t = [['Card text', c.desc]];
      if (c.card_sets) t.push(['Printings', c.card_sets.slice(0, 25).map(s => `${s.set_name} · ${s.set_code} · ${s.set_rarity}${s.set_price && +s.set_price ? ' · $' + s.set_price : ''}`).join('\n')]);
      const p = c.card_prices?.[0] || {};
      if (+p.tcgplayer_price) add('TCGplayer price', usd(p.tcgplayer_price)); if (+p.cardmarket_price) add('Cardmarket price', usd(p.cardmarket_price)); if (+p.ebay_price) add('eBay price', usd(p.ebay_price));
      const market = +p.tcgplayer_price || +p.ebay_price || null;
      return { source: 'yugioh', id: String(c.id), category: 'yugioh', name: c.name, set: s0?.set_name || '', year: (c.misc_info?.[0]?.tcg_date || '').slice(0, 4), number: s0?.set_code || '', rarity: s0?.set_rarity || '', image: c.card_images?.[0]?.image_url, thumb: c.card_images?.[0]?.image_url_small, fields: f, texts: t, market, url: c.ygoprodeck_url };
    });
  }

  const sim = (a, b) => { a = (a || '').toLowerCase(); b = (b || '').toLowerCase(); return a === b ? 3 : b.startsWith(a) || a.startsWith(b) ? 2 : (a && (b.includes(a) || a.includes(b))) ? 1 : 0; };

  async function auto(q) {
    const rs = await Promise.allSettled([pokemon(q), magic(q), yugioh(q)]);
    let best = [], bs = -1;
    rs.forEach(r => {
      if (r.status !== 'fulfilled' || !r.value.length) return;
      const s = Math.max(...r.value.map(x => sim(q.name, x.name)));
      if (s > bs) { bs = s; best = r.value; }
    });
    if (!best.length && rs.every(r => r.status === 'rejected')) throw rs[0].reason;
    return best;
  }

  async function search(category, q) {
    switch (catOf(category).api) {
      case 'pokemon': return pokemon(q);
      case 'magic': return magic(q);
      case 'yugioh': return yugioh(q);
      case 'auto': return auto(q);
      default: return [];
    }
  }

  /* Download a web image into a canvas. Needs the host to allow CORS, otherwise the canvas would be tainted. */
  async function imageCanvas(url) {
    try {
      const r = await fetch(url, { mode: 'cors' });
      if (!r.ok) throw new Error('http');
      return await blobToCanvas(await r.blob());
    } catch (e) {
      const img = await loadImage(url);
      const c = newCanvas(img.naturalWidth, img.naturalHeight);
      const x = c.getContext('2d');
      x.drawImage(img, 0, 0);
      try { x.getImageData(0, 0, 1, 1); } catch { throw new Error('That site blocks reusing its image – download it and use Upload instead'); }
      return c;
    }
  }

  return { search, imageCanvas };
})();
