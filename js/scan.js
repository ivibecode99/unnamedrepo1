/* Scan page: camera picker, Fast (auto-capture) mode, Manual mode, Upload mode */
const Scan = (() => {
  const video = () => $('#video');
  const O = Object.assign({ mode: 'fast', sides: '1', category: 'auto-tcg', identify: true, crop: true, rotate: true, sens: 5, hold: 450, cam: '' }, Store.get('scanopts', {}));
  const S = { stream: null, front: null, pending: null, count: 0 };
  const save = () => Store.set('scanopts', O);

  /* ---------- camera ---------- */
  async function refreshCams() {
    const sel = $('#camSelect');
    if (!navigator.mediaDevices?.getUserMedia) { setStatus('Camera API unavailable – open this site over https:// or http://localhost'); return; }
    try { const t = await navigator.mediaDevices.getUserMedia({ video: true }); t.getTracks().forEach(x => x.stop()); }
    catch (e) { setStatus('Camera blocked: ' + (e.message || e.name) + ' – allow camera access in the address bar'); }
    const devs = (await navigator.mediaDevices.enumerateDevices()).filter(d => d.kind === 'videoinput');
    sel.innerHTML = devs.length ? '' : '<option value="">No cameras found</option>';
    devs.forEach((d, i) => { const o = document.createElement('option'); o.value = d.deviceId; o.textContent = d.label || `Camera ${i + 1}`; sel.appendChild(o); });
    if (devs.some(d => d.deviceId === O.cam)) sel.value = O.cam;
  }

  async function startCam() {
    stopCam();
    try {
      const id = $('#camSelect').value;
      const stream = await navigator.mediaDevices.getUserMedia({ video: { deviceId: id ? { exact: id } : undefined, width: { ideal: 4096 }, height: { ideal: 2160 } }, audio: false });
      S.stream = stream;
      const v = video(); v.srcObject = stream; await v.play();
      const tr = stream.getVideoTracks()[0], st = tr.getSettings();
      try { const caps = tr.getCapabilities ? tr.getCapabilities() : {}; if (caps.focusMode && caps.focusMode.includes('continuous')) await tr.applyConstraints({ advanced: [{ focusMode: 'continuous' }] }); } catch { }
      O.cam = id; save();
      $('#camToggle').textContent = 'Stop camera';
      $('#camInfo').textContent = `${st.width || v.videoWidth}×${st.height || v.videoHeight}`;
      await refreshCams();   // labels are now available
      Auto.sync();
      sidePrompt();
    } catch (e) { setStatus('Could not start camera: ' + (e.message || e.name)); toast('Camera error: ' + (e.message || e.name), 'err'); }
  }
  function stopCam() {
    Auto.stop();
    if (S.stream) { S.stream.getTracks().forEach(t => t.stop()); S.stream = null; }
    const v = video(); if (v) v.srcObject = null;
    $('#camToggle').textContent = 'Start camera';
    $('#camInfo').textContent = '';
    setStatus('Camera off');
  }
  const setStatus = t => { $('#camStatus').textContent = t; };
  function grab() {
    const v = video();
    const c = newCanvas(v.videoWidth, v.videoHeight);
    c.getContext('2d').drawImage(v, 0, 0);
    return c;
  }

  /* ---------- fast mode: auto capture when a card is slid in and held still ---------- */
  const Auto = (() => {
    const W = 80, H = 60;
    const sm = newCanvas(W, H), sx = sm.getContext('2d', { willReadFrequently: true });
    let timer = null, prev = null, base = null, last = null, state = 'ready', still = 0, cool = 0;
    const gray = () => {
      sx.drawImage(video(), 0, 0, W, H);
      const d = sx.getImageData(0, 0, W, H).data, g = new Uint8Array(W * H);
      for (let i = 0; i < g.length; i++) g[i] = d[i * 4] * 0.3 + d[i * 4 + 1] * 0.59 + d[i * 4 + 2] * 0.11;
      return g;
    };
    const diff = (a, b) => { let s = 0; for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s / a.length; };
    async function tick() {
      const v = video();
      if (!v.videoWidth || O.mode !== 'fast') return;
      const cur = gray(), now = performance.now();
      const motion = prev ? diff(cur, prev) : 0; prev = cur;
      const moveT = 3 + (10 - O.sens), stillT = Math.max(1.2, moveT * 0.4);
      if (state === 'cooldown') { if (now > cool) { state = 'ready'; setStatus(prompt()); } return; }
      if (state === 'busy') return;
      if (state === 'ready') { if (motion > moveT) { state = 'settling'; still = 0; setStatus('Hold still…'); } return; }
      if (state === 'settling') {
        still = motion < stillT ? still + 100 : 0;
        if (still >= O.hold) {
          const present = base ? diff(cur, base) > 8 : true;
          const dup = last ? diff(cur, last) < 6 : false;
          if (present && !dup) {
            state = 'busy'; last = cur;
            try { await capture(true); } catch (e) { toast(String(e.message || e), 'err'); }
            state = 'cooldown'; cool = performance.now() + 700;
          } else { state = 'ready'; setStatus(dup ? 'Same card – slide the next one' : prompt()); }
        }
      }
    }
    return {
      sync() { if (S.stream && O.mode === 'fast') { if (!timer) { timer = setInterval(tick, 100); state = 'ready'; setStatus(prompt()); } } else this.stop(); },
      stop() { clearInterval(timer); timer = null; prev = null; },
      setBase() { if (!S.stream) return toast('Start the camera first'); base = gray(); toast('Empty background saved – only real cards will trigger now'); },
      clearBase() { base = null; },
      reset() { last = null; },
    };
  })();

  const prompt = () => O.sides === '2' ? (S.front ? 'Show the BACK of this card' : 'Show the FRONT of the next card') : 'Ready – slide a card in';
  function sidePrompt() { $('#sidePrompt').textContent = O.mode === 'upload' ? '' : (O.sides === '2' ? (S.front ? '⟳ Now show the BACK' : 'Show the FRONT') : ''); if (S.stream && O.mode === 'fast') setStatus(prompt()); }

  /* ---------- capture pipeline ---------- */
  function process(canvas, fromCamera) {
    let c = canvas;
    if (O.crop) c = ImgTools.autoCrop(c);
    if (fromCamera && O.rotate && c.width > c.height * 1.1) c = ImgTools.rotate(c);
    return c;
  }
  function flash() { const f = $('#flash'); f.classList.remove('go'); void f.offsetWidth; f.classList.add('go'); beep(); }
  let actx;
  function beep() { try { actx = actx || new AudioContext(); const o = actx.createOscillator(), g = actx.createGain(); o.frequency.value = 880; g.gain.value = 0.05; o.connect(g); g.connect(actx.destination); o.start(); o.stop(actx.currentTime + 0.07); } catch { } }

  async function accept(c, open) {
    if (O.sides === '2') {
      if (!S.front) { S.front = c; sidePrompt(); renderRecent(); return null; }
      const card = await CardOps.create({ front: S.front, back: c, category: O.category });
      S.front = null; sidePrompt(); return done(card, open);
    }
    return done(await CardOps.create({ front: c, category: O.category }), open);
  }
  function done(card, open) {
    S.count++;
    if (O.identify) CardOps.queue(card.id);
    renderRecent();
    if (open) openCard(card.id);
    return card;
  }

  async function capture(auto) {
    if (!S.stream) return toast('Start the camera first');
    flash();
    const c = process(grab(), true);
    if (O.mode === 'manual' && !auto) { showPending(c); return; }
    await accept(c, false);
  }

  function showPending(c) {
    S.pending = c;
    const box = $('#pendingBox'), cv = $('#pendingCv');
    cv.width = c.width; cv.height = c.height; cv.getContext('2d').drawImage(c, 0, 0);
    box.classList.remove('hidden');
    $('#pendingTitle').textContent = O.sides === '2' ? (S.front ? 'Back captured' : 'Front captured') : 'Captured';
  }
  async function usePending() {
    const c = S.pending; if (!c) return;
    S.pending = null; $('#pendingBox').classList.add('hidden');
    await accept(c, true);
  }
  function retake() { S.pending = null; $('#pendingBox').classList.add('hidden'); }

  /* ---------- upload ---------- */
  async function handleFiles(files) {
    files = Array.from(files).filter(f => f.type.startsWith('image/'));
    if (!files.length) return toast('Drop image files (JPG / PNG / WebP)', 'err');
    const step = O.sides === '2' ? 2 : 1;
    let made = 0;
    for (let i = 0; i < files.length; i += step) {
      try {
        const front = process(await blobToCanvas(files[i]), false);
        const back = step === 2 && files[i + 1] ? process(await blobToCanvas(files[i + 1]), false) : null;
        const card = await CardOps.create({ front, back, category: O.category });
        made++; S.count++;
        if (O.identify) CardOps.queue(card.id);
        renderRecent();
        if (files.length <= step) openCard(card.id);
      } catch (e) { toast('Could not read ' + files[i].name, 'err'); }
    }
    if (made > 1) toast(`${made} cards added to your collection`, 'ok');
  }

  /* ---------- recent strip ---------- */
  async function renderRecent() {
    const box = $('#recent');
    const l = Cards.list().slice(0, 14);
    $('#recentCount').textContent = `${Cards.list().length} in collection`;
    box.innerHTML = '';
    if (S.front) { const d = document.createElement('div'); d.className = 'rtile pend'; d.textContent = 'front ✓'; box.appendChild(d); }
    for (const c of l) {
      const d = document.createElement('div');
      d.className = 'rtile'; d.dataset.id = c.id;
      d.innerHTML = `<img alt=""><span class="dot ${c.status || ''}"></span><b>${esc(c.name || '…')}</b>`;
      box.appendChild(d);
      Img.url(imgKey(c.id, 'thumb')).then(u => { if (u) $('img', d).src = u; });
      d.onclick = () => openCard(c.id);
    }
  }

  /* ---------- UI wiring ---------- */
  function applyMode() {
    const m = O.mode;
    $('#viewport').classList.toggle('hidden', m === 'upload');
    $('.cam-row').classList.toggle('hidden', m === 'upload');
    $('#uploadZone').classList.toggle('hidden', m !== 'upload');
    $('#snapBtn').classList.toggle('hidden', m !== 'manual');
    $('#fastOpts').classList.toggle('hidden', m !== 'fast');
    $('#viewport').classList.toggle('guide-on', m === 'manual');
    $('#modeHelp').textContent = {
      fast: 'Slide cards in front of the camera one after another. Each card is captured automatically once it stops moving, then the next one.',
      manual: 'Line the card up in the frame and press Capture (or Space). You review each shot and can retake it.',
      upload: 'Drop scans or photos. With "Front + back", files are used in pairs: front, back, front, back…',
    }[m];
    Auto.sync(); sidePrompt();
    if (m !== 'fast' && S.stream) setStatus('Camera on');
  }

  function init() {
    fillCatSelect($('#scanCat'), { value: O.category });
    $$('input[name=mode]').forEach(r => { r.checked = r.value === O.mode; r.onchange = () => { O.mode = r.value; save(); applyMode(); }; });
    $$('input[name=sides]').forEach(r => { r.checked = r.value === O.sides; r.onchange = () => { O.sides = r.value; S.front = null; save(); applyMode(); renderRecent(); }; });
    $('#scanCat').onchange = e => { O.category = e.target.value; save(); };
    [['optIdentify', 'identify'], ['optCrop', 'crop'], ['optRotate', 'rotate']].forEach(([id, k]) => { const e = $('#' + id); e.checked = O[k]; e.onchange = () => { O[k] = e.checked; save(); }; });
    [['optSens', 'sens'], ['optHold', 'hold']].forEach(([id, k]) => { const e = $('#' + id); e.value = O[k]; const lab = $('#' + id + 'V'); lab.textContent = e.value; e.oninput = () => { O[k] = +e.value; lab.textContent = e.value; save(); }; });
    $('#camRefresh').onclick = refreshCams;
    $('#camToggle').onclick = () => S.stream ? stopCam() : startCam();
    $('#camSelect').onchange = () => { O.cam = $('#camSelect').value; save(); if (S.stream) startCam(); };
    $('#snapBtn').onclick = () => capture(false);
    $('#useBtn').onclick = usePending; $('#retakeBtn').onclick = retake;
    $('#skipBack').onclick = async () => { if (S.front) { const card = await CardOps.create({ front: S.front, category: O.category }); S.front = null; done(card, O.mode !== 'fast'); sidePrompt(); } };
    $('#bgBtn').onclick = () => Auto.setBase();
    $('#bgClear').onclick = () => { Auto.clearBase(); toast('Background cleared'); };
    $('#fileInput').onchange = e => { handleFiles(e.target.files); e.target.value = ''; };
    const dz = $('#uploadZone');
    ['dragenter', 'dragover'].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.add('over'); }));
    ['dragleave', 'drop'].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.remove('over'); }));
    dz.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
    document.addEventListener('keydown', e => {
      if (e.code === 'Space' && O.mode === 'manual' && $('#page-scan').classList.contains('active') && !/INPUT|TEXTAREA|SELECT|BUTTON/.test(document.activeElement.tagName) && !Modal.el) {
        e.preventDefault(); if (S.pending) usePending(); else capture(false);
      }
    });
    document.addEventListener('cards-changed', () => { if ($('#page-scan').classList.contains('active')) renderRecent(); });
    applyMode(); renderRecent();
    if (navigator.mediaDevices?.enumerateDevices) navigator.mediaDevices.enumerateDevices().then(d => {
      const vids = d.filter(x => x.kind === 'videoinput');
      if (vids.length) { $('#camSelect').innerHTML = vids.map((x, i) => `<option value="${esc(x.deviceId)}">${esc(x.label || 'Camera ' + (i + 1))}</option>`).join(''); if (vids.some(x => x.deviceId === O.cam)) $('#camSelect').value = O.cam; }
    });
  }

  return { init, stopCam, renderRecent };
})();
