// Viewer entry point (match.html). Loads data, builds the store, mounts every module and
// runs the single animation loop. Modules never talk to each other directly: they read and
// write the store (see store.js for the state contract).

import { $, onReady } from '../core/dom.js';
import { applyI18n, onLangChange, pick, t } from '../core/i18n.js';
import { hydrateIcons, icon } from '../core/icons.js';
import { findEntry, loadCatalog, loadReplay } from '../core/data.js';
import { fmtKB } from '../core/format.js';
import { getPref, setPref } from '../core/prefs.js';
import { createStore } from './store.js';
import { deriveMatch } from './derive.js';
import { createPlayback, SPEEDS } from './playback.js';
import { frameForTurn, readUrlState, syncUrl } from './url-state.js';
import { mountKeyboard } from './keyboard.js';
import { mountBoardView } from './ui/board-view.js';
import { mountTransport } from './ui/transport.js';
import { mountTopbar } from './ui/topbar.js';
import { mountTabs } from './ui/tabs.js';
import { mountStandings } from './ui/standings.js';
import { mountScorebug } from './ui/scorebug.js';
import { mountChart } from './ui/chart.js';
import { mountFeed } from './ui/feed.js';
import { mountStats } from './ui/stats.js';
import { mountUnitCard } from './ui/unit-card.js';

const root = $('#viewer');

function setStatus(state, html = '') {
  root.dataset.state = state;
  $('#board-status').innerHTML = html;
}

async function start() {
  hydrateIcons();
  applyI18n();
  const { key, turn } = readUrlState();
  setStatus('loading', `<div class="spinner" aria-hidden="true"></div><p>${t('viewer.loading')}</p>`);

  let catalog, entry, replay;
  try {
    catalog = await loadCatalog();
    entry = key ? await findEntry(key) : catalog.matches.find((m) => m.featured) || catalog.matches[0];
    if (!entry) return showMissing(key);
    $('#match-title').textContent = pick(entry.title);
    setStatus('loading', `<div class="spinner" aria-hidden="true"></div><p>${t('viewer.loadingSize', { kb: fmtKB(entry.bytes) })}</p>`);
    replay = await loadReplay(entry);
  } catch (err) {
    console.error(err);
    return showError(err);
  }

  const derived = deriveMatch(replay);
  const savedSpeed = getPref('speed', 1);
  const store = createStore({
    entry,
    replay,
    derived,
    frame: turn ? frameForTurn(replay, turn) : 0,
    playing: false,
    speed: SPEEDS.includes(savedSpeed) ? savedSpeed : 1,
    focusTeam: -1,
    selectedUnit: null,
    follow: false,
    tab: getPref('tab', 'standings'),
    chartMode: getPref('chartMode', 'lines'),
    immersive: false,
  });
  store.subscribe(['speed', 'tab', 'chartMode'], (s) => {
    setPref('speed', s.speed);
    setPref('tab', s.tab);
    setPref('chartMode', s.chartMode);
  });

  const playback = createPlayback(store);
  const toggleImmersive = () => setImmersive(store, !store.get().immersive);

  mountTopbar(store, { catalog, toggleImmersive });
  const board = mountBoardView(store, { playback });
  mountTransport(store, { playback });
  mountTabs(store);
  mountScorebug(store);
  mountStandings(store);
  mountChart(store, { playback });
  mountFeed(store, { playback });
  mountStats(store);
  mountUnitCard(store);
  mountKeyboard(store, { playback, board, toggleImmersive });
  syncUrl(store);
  applyI18n();
  onLangChange(() => applyI18n());

  document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement && store.get().immersive) store.set({ immersive: false });
  });
  store.subscribe(['immersive'], (s) => root.classList.toggle('is-immersive', s.immersive));

  setStatus('ready');
  const loop = (now) => {
    playback.tick(now);
    board.draw(now);
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);

  // Handy for debugging from the console; not part of any contract
  window.__viewer = { store, playback, board };
}

function setImmersive(store, on) {
  store.set({ immersive: on });
  const canFullscreen = document.fullscreenEnabled && root.requestFullscreen;
  if (on && canFullscreen && !document.fullscreenElement) {
    root.requestFullscreen().catch(() => { /* CSS layout still applies */ });
  } else if (!on && document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  }
}

function showMissing(key) {
  setStatus('error', `
    <h2>${t('viewer.notFoundTitle')}</h2>
    <p>${t('viewer.notFoundBody', { key: String(key).replace(/[<>&"]/g, '') })}</p>
    <a class="btn btn--primary" href="index.html">${icon('list', 'icon icon--sm')}<span>${t('viewer.browseMatches')}</span></a>`);
}

function showError(err) {
  setStatus('error', `
    <h2>${t('viewer.errorTitle')}</h2>
    <p>${t(location.protocol === 'file:' ? 'viewer.errorFile' : 'viewer.errorBody')}</p>
    <p class="muted">${String(err.message || err).replace(/[<>&"]/g, '')}</p>
    <button class="btn btn--primary" type="button" onclick="location.reload()">${t('viewer.retry')}</button>`);
}

onReady(start);
