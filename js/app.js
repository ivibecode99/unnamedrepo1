/* Boot + routing */
const PAGES = ['scan', 'collection', 'studio', 'brand', 'settings'];
const PAGE_HOOKS = {
  collection: () => Collection.render(),
  studio: () => Studio.onShow(),
  brand: () => BrandUI.onShow(),
  settings: () => SettingsUI.onShow(),
  scan: () => Scan.renderRecent(),
};

function route() {
  const h = (location.hash || '#scan').slice(1);
  const p = PAGES.includes(h) ? h : 'scan';
  $$('.page').forEach(e => e.classList.toggle('active', e.id === 'page-' + p));
  $$('nav a').forEach(a => a.classList.toggle('on', a.dataset.p === p));
  if (p !== 'scan') Scan.stopCam();
  PAGE_HOOKS[p] && PAGE_HOOKS[p]();
  window.scrollTo(0, 0);
}

(async function boot() {
  try {
    await DB.open();
  } catch (e) {
    toast('This browser blocks local storage (private mode?) – scans can\'t be saved', 'err');
  }
  await Brand.loadCustomFont();
  Scan.init(); Collection.init(); Studio.init(); BrandUI.init(); SettingsUI.init();
  window.addEventListener('hashchange', route);
  route();
})();
