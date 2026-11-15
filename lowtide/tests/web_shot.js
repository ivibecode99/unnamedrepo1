// Headless Chromium test for the web build: node tests/web_shot.js <dir> <outprefix> [steps JSON]
// steps: [["wait",ms],["key","Enter",holdMs],["shot","name"]]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const dir = process.argv[2], out = process.argv[3];
const steps = JSON.parse(process.argv[4] || '[["wait",1500],["key","Enter",120],["wait",600],["key","ArrowDown",100],["wait",300],["shot","menu"]]');
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.wasm': 'application/wasm' };
const srv = http.createServer((q, r) => { const f = path.join(dir, q.url === '/' ? 'index.html' : q.url.split('?')[0]); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'content-type': mime[path.extname(f)] || 'application/octet-stream' }); r.end(d); } }); });
srv.listen(0, async () => {
  const port = srv.address().port;
  const b = await chromium.launch({ args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
  const p = await b.newPage({ viewport: { width: 640, height: 576 } });
  const logs = []; p.on('console', m => logs.push(m.text())); p.on('pageerror', e => logs.push('PAGEERROR ' + e.message));
  await p.goto(`http://127.0.0.1:${port}/`);
  await p.mouse.click(300, 300);
  for (const s of steps) {
    if (s[0] === 'wait') await p.waitForTimeout(s[1]);
    else if (s[0] === 'key') { await p.keyboard.down(s[1]); await p.waitForTimeout(s[2] || 100); await p.keyboard.up(s[1]); }
    else if (s[0] === 'shot') { const c = await p.$('canvas'); await c.screenshot({ path: `${out}_${s[1]}.png` }); }
  }
  console.log(logs.slice(0, 10).join('\n') || 'no console output');
  await b.close(); srv.close();
});
