/* Small shared helpers (no dependencies) */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const money = n => (n == null || n === '' || isNaN(n)) ? '' : '$' + Number(n).toFixed(2);
const slug = s => String(s || 'card').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'card';
const debounce = (fn, ms = 200) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

function toast(msg, kind = '') {
  const t = document.createElement('div');
  t.className = 'toast ' + kind;
  t.textContent = msg;
  $('#toasts').appendChild(t);
  setTimeout(() => t.classList.add('out'), 3400);
  setTimeout(() => t.remove(), 3900);
}

function newCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = Math.max(1, Math.round(w));
  c.height = Math.max(1, Math.round(h));
  return c;
}
const canvasToBlob = (c, type = 'image/png', q = 0.92) => new Promise(r => c.toBlob(r, type, q));

async function blobToCanvas(blob) {
  const bmp = await createImageBitmap(blob);
  const c = newCanvas(bmp.width, bmp.height);
  c.getContext('2d').drawImage(bmp, 0, 0);
  if (bmp.close) bmp.close();
  return c;
}

function loadImage(src) {
  return new Promise((res, rej) => {
    const i = new Image();
    i.crossOrigin = 'anonymous';
    i.onload = () => res(i);
    i.onerror = () => rej(new Error('Image failed to load'));
    i.src = src;
  });
}

function saveAs(blob, name) {
  const a = document.createElement('a');
  const u = URL.createObjectURL(blob);
  a.href = u; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(u), 5000);
}

const _scripts = {};
function loadScript(src) {
  if (!_scripts[src]) {
    _scripts[src] = new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = src; s.onload = res;
      s.onerror = () => { delete _scripts[src]; rej(new Error('Could not load ' + src + ' (offline?)')); };
      document.head.appendChild(s);
    });
  }
  return _scripts[src];
}

const blobToDataURL = b => new Promise(r => { const f = new FileReader(); f.onload = () => r(f.result); f.readAsDataURL(b); });
const dataURLToBlob = async u => (await fetch(u)).blob();

function hex2rgb(h) {
  h = h.replace('#', '');
  if (h.length === 3) h = h.split('').map(x => x + x).join('');
  const n = parseInt(h, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
const contrastOn = hex => { const [r, g, b] = hex2rgb(hex); return (r * 299 + g * 587 + b * 114) / 1000 > 150 ? '#111111' : '#ffffff'; };

/* canvas helpers */
function rr(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}
function wrapText(ctx, text, maxW) {
  const out = [];
  String(text ?? '').split('\n').forEach(par => {
    let line = '';
    par.split(/\s+/).forEach(w => {
      const t = line ? line + ' ' + w : w;
      if (ctx.measureText(t).width > maxW && line) { out.push(line); line = w; } else line = t;
    });
    out.push(line);
  });
  return out;
}
function fitFont(ctx, text, maxW, size, weight, family) {
  let s = size;
  ctx.font = `${weight} ${s}px ${family}`;
  while (ctx.measureText(text).width > maxW && s > size * 0.4) { s -= 1; ctx.font = `${weight} ${s}px ${family}`; }
  return s;
}
function flatten(canvas, bg = '#ffffff') {
  const c = newCanvas(canvas.width, canvas.height);
  const x = c.getContext('2d');
  x.fillStyle = bg; x.fillRect(0, 0, c.width, c.height);
  x.drawImage(canvas, 0, 0);
  return c;
}

/* Modal */
const Modal = {
  open(html, cls = '') {
    this.close();
    const m = document.createElement('div');
    m.className = 'modal-bg';
    m.innerHTML = `<div class="modal ${cls}"><button class="modal-x" aria-label="Close">✕</button><div class="modal-body">${html}</div></div>`;
    m.addEventListener('mousedown', e => { if (e.target === m) this.close(); });
    $('.modal-x', m).onclick = () => this.close();
    document.body.appendChild(m);
    document.body.classList.add('noscroll');
    this.el = m;
    return $('.modal-body', m);
  },
  close() {
    if (this.el) { this.el.remove(); this.el = null; document.body.classList.remove('noscroll'); }
    if (this.onClose) { const f = this.onClose; this.onClose = null; f(); }
  }
};
document.addEventListener('keydown', e => { if (e.key === 'Escape') Modal.close(); });
