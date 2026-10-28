/* In-browser OCR (Tesseract.js, loaded on demand from a CDN, runs locally) to read the name / number / year off a scan. */
const OCR = (() => {
  let worker = null;
  async function load() {
    if (!window.Tesseract) await loadScript('https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js');
    if (!worker) worker = await Tesseract.createWorker('eng');
    return worker;
  }
  async function text(canvas) {
    const w = await load();
    const { data } = await w.recognize(canvas);
    return data.text || '';
  }
  function strip(canvas, y0, y1) {
    const H = canvas.height, W = canvas.width, sh = Math.max(8, (y1 - y0) * H);
    const sc = Math.max(1, 1100 / W);
    const c = newCanvas(W * sc, sh * sc);
    const x = c.getContext('2d');
    x.filter = 'grayscale(1) contrast(1.4)';
    x.drawImage(canvas, 0, y0 * H, W, sh, 0, 0, c.width, c.height);
    return c;
  }
  const clean = t => t.split('\n').map(l => l.replace(/[^A-Za-z0-9'’\-.,:&é ]/g, ' ').replace(/\s+/g, ' ').trim()).filter(l => l.replace(/[^A-Za-z]/g, '').length >= 3);

  /* → { name, number, year, lines } */
  async function identify(canvas, category) {
    const top = clean(await text(strip(canvas, 0, 0.14)));
    const bottomRaw = await text(strip(canvas, 0.84, 1));
    const bottom = clean(bottomRaw);
    const pick = arr => {
      const lines = arr.map(l => l.replace(/\bHP\s*\d+.*$/i, '').replace(/^(basic|stage\s*[12]|mega)\s+/i, '').replace(/\b\d+\s*$/, '').trim());
      return lines.sort((a, b) => b.replace(/[^A-Za-z]/g, '').length - a.replace(/[^A-Za-z]/g, '').length)[0] || '';
    };
    let name = isTCG(category) ? pick(top) : pick(bottom.length ? bottom : top);
    if (!isTCG(category)) name = name.replace(/\s+/g, ' ');
    const nm = (bottomRaw.match(/(\d{1,3})\s*\/\s*(\d{1,3})/) || [])[1] || '';
    const year = ((top.join(' ') + ' ' + bottomRaw).match(/\b(19[5-9]\d|20[0-3]\d)\b/) || [])[1] || '';
    return { name, number: nm, year, lines: [...top, ...bottom].slice(0, 10) };
  }
  return { identify };
})();
