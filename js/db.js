/* Storage: everything stays in this browser.
   - localStorage  : settings, brand, card records (small JSON)
   - IndexedDB     : image blobs (scans, thumbnails, logo, custom font) – too big for localStorage */

const CATS = [
  { id: 'auto-tcg', label: 'Auto-detect TCG', group: 'Trading card games', kind: 'tcg', api: 'auto' },
  { id: 'pokemon', label: 'Pokémon', group: 'Trading card games', kind: 'tcg', api: 'pokemon' },
  { id: 'magic', label: 'Magic: The Gathering', group: 'Trading card games', kind: 'tcg', api: 'magic' },
  { id: 'yugioh', label: 'Yu-Gi-Oh!', group: 'Trading card games', kind: 'tcg', api: 'yugioh' },
  { id: 'othertcg', label: 'Other TCG (Lorcana, One Piece, DBS…)', group: 'Trading card games', kind: 'tcg' },
  { id: 'baseball', label: 'Baseball', group: 'Sports', kind: 'sport' },
  { id: 'basketball', label: 'Basketball', group: 'Sports', kind: 'sport' },
  { id: 'football', label: 'Football', group: 'Sports', kind: 'sport' },
  { id: 'hockey', label: 'Hockey', group: 'Sports', kind: 'sport' },
  { id: 'soccer', label: 'Soccer', group: 'Sports', kind: 'sport' },
  { id: 'golf', label: 'Golf', group: 'Sports', kind: 'sport' },
  { id: 'othersport', label: 'Other sport (UFC, F1, wrestling…)', group: 'Sports', kind: 'sport' },
  { id: 'nonsport', label: 'Non-sport / other', group: 'Other', kind: 'other' },
];
const catOf = id => CATS.find(c => c.id === id) || CATS[CATS.length - 1];
const isTCG = id => catOf(id).kind === 'tcg';
const isSport = id => catOf(id).kind === 'sport';

function fillCatSelect(sel, { includeAuto = true, value } = {}) {
  sel.innerHTML = '';
  const groups = {};
  CATS.forEach(c => {
    if (!includeAuto && c.id === 'auto-tcg') return;
    if (!groups[c.group]) { groups[c.group] = document.createElement('optgroup'); groups[c.group].label = c.group; sel.appendChild(groups[c.group]); }
    const o = document.createElement('option'); o.value = c.id; o.textContent = c.label; groups[c.group].appendChild(o);
  });
  if (value) sel.value = value;
}

const DB = (() => {
  let db;
  const open = () => new Promise((res, rej) => {
    const r = indexedDB.open('cardvault', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('blobs');
    r.onsuccess = () => { db = r.result; res(); };
    r.onerror = () => rej(r.error);
  });
  const tx = (mode, fn) => new Promise((res, rej) => {
    const t = db.transaction('blobs', mode);
    const req = fn(t.objectStore('blobs'));
    t.oncomplete = () => res(req && req.result);
    t.onerror = () => rej(t.error);
    t.onabort = () => rej(t.error);
  });
  return {
    open,
    put: (k, b) => tx('readwrite', s => s.put(b, k)),
    get: k => tx('readonly', s => s.get(k)),
    del: k => tx('readwrite', s => s.delete(k)),
    keys: () => tx('readonly', s => s.getAllKeys()),
    clear: () => tx('readwrite', s => s.clear()),
  };
})();

const Store = {
  get(k, d) { try { const v = localStorage.getItem('cv.' + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem('cv.' + k, JSON.stringify(v)); } catch (e) { toast('Browser storage is full – export a backup and free some space', 'err'); } },
  del(k) { try { localStorage.removeItem('cv.' + k); } catch { } },
};

/* Image blob cache → object URLs */
const Img = {
  cache: {},
  async url(key) {
    if (this.cache[key]) return this.cache[key];
    const b = await DB.get(key);
    if (!b) return null;
    return (this.cache[key] = URL.createObjectURL(b));
  },
  invalidate(key) { if (this.cache[key]) { URL.revokeObjectURL(this.cache[key]); delete this.cache[key]; } },
};
const imgKey = (id, side) => `c:${id}:${side}`;

const Cards = {
  list() { return Store.get('cards', []); },
  get(id) { return this.list().find(c => c.id === id); },
  save(card) {
    const l = this.list();
    const i = l.findIndex(c => c.id === card.id);
    if (i >= 0) l[i] = card; else l.unshift(card);
    Store.set('cards', l);
    document.dispatchEvent(new CustomEvent('cards-changed', { detail: card.id }));
  },
  async remove(id) {
    Store.set('cards', this.list().filter(c => c.id !== id));
    for (const s of ['front', 'back', 'thumb', 'digital']) { Img.invalidate(imgKey(id, s)); await DB.del(imgKey(id, s)); }
    document.dispatchEvent(new CustomEvent('cards-changed', { detail: id }));
  },
};
