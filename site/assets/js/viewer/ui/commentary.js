// Commentary pane + board captions. Lines come from site/data/commentary/<key>/<lang>.json
// (written by tools/commentate.py) or from a JSON file the viewer opens locally ("offline").
// A line only appears once playback reaches its turn, so commentary never spoils the match.
//
// Store keys used: commentary (normalized track or null), commentaryLang ('auto' | code),
// captions (bool), hiddenRoles (role ids).

import { $, escapeHtml, h } from '../../core/dom.js';
import { icon } from '../../core/icons.js';
import { getLang, onLangChange, t } from '../../core/i18n.js';
import { loadCommentary } from '../../core/data.js';

const CAPTION_TURNS = 8;   // how long a caption stays on the board
const KNOWN_ICONS = new Set(['mic', 'chat', 'chart', 'activity', 'swords', 'flag', 'trophy', 'info']);

export function mountCommentary(store, { playback }) {
  const pane = $('#pane-commentary');
  const caption = $('#board-caption');
  const fileInput = h('input', { type: 'file', accept: '.json,application/json', hidden: true });

  const langSelect = h('select', { class: 'select select--sm' });
  const captionsBtn = h('button', { type: 'button', class: 'chip-btn' });
  const openBtn = h('button', { type: 'button', class: 'chip-btn' });
  const roleBar = h('div', { class: 'role-chips', role: 'group' });
  const note = h('p', { class: 'pane-hint commentary-note' });
  const list = h('ol', { class: 'commentary-list', 'aria-live': 'polite' });
  const empty = h('div', { class: 'commentary-empty' });
  pane.replaceChildren(
    h('div', { class: 'commentary-head' }, langSelect, captionsBtn, openBtn, fileInput),
    roleBar, note, list, empty,
  );

  const entry = store.get().entry;
  const fileTracks = new Map(); // lang -> track loaded from a local file

  const available = () => [...new Set([...(entry.commentary || []), ...fileTracks.keys()])];
  const effectiveLang = (s = store.get()) => {
    const langs = available();
    if (s.commentaryLang !== 'auto' && langs.includes(s.commentaryLang)) return s.commentaryLang;
    return langs.includes(getLang()) ? getLang() : langs[0] || null;
  };

  let loadToken = 0;
  async function loadTrack() {
    const lang = effectiveLang();
    const token = ++loadToken;
    if (!lang) {
      store.set({ commentary: null });
      return;
    }
    if (fileTracks.has(lang)) {
      store.set({ commentary: fileTracks.get(lang) });
      return;
    }
    try {
      const data = await loadCommentary(entry, lang);
      if (token === loadToken) store.set({ commentary: data ? normalize(data, lang, 'site') : null });
    } catch (err) {
      console.error(err);
      if (token === loadToken) store.set({ commentary: null });
    }
  }

  // ---- controls
  langSelect.addEventListener('change', () => store.set({ commentaryLang: langSelect.value }));
  captionsBtn.addEventListener('click', () => store.set({ captions: !store.get().captions }));
  openBtn.addEventListener('click', () => fileInput.click());
  roleBar.addEventListener('click', (e) => {
    const b = e.target.closest('[data-role]');
    if (!b) return;
    const hidden = new Set(store.get().hiddenRoles);
    hidden.has(b.dataset.role) ? hidden.delete(b.dataset.role) : hidden.add(b.dataset.role);
    store.set({ hiddenRoles: [...hidden] });
  });
  list.addEventListener('click', (e) => {
    const li = e.target.closest('[data-turn]');
    if (li) playback.seek(frameForTurn(store.get().replay, Number(li.dataset.turn)));
  });

  fileInput.addEventListener('change', async () => {
    const file = fileInput.files?.[0];
    fileInput.value = '';
    if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      if (data.match && data.match !== entry.key) throw new Error(t('commentary.fileWrongMatch', { match: data.match }));
      const lang = String(data.language || effectiveLang() || getLang());
      const track = normalize(data, lang, 'file', store.get().commentary, file.name);
      fileTracks.set(lang, track);
      store.set({ commentaryLang: lang, commentary: track });
      renderControls();
    } catch (err) {
      note.textContent = t('commentary.fileError', { error: err.message });
      note.classList.add('is-error');
    }
  });

  // ---- rendering
  function renderControls() {
    const s = store.get();
    const langs = available();
    const lang = effectiveLang(s);
    let names;
    try {
      names = new Intl.DisplayNames([getLang() === 'zh' ? 'zh-CN' : 'en'], { type: 'language' });
    } catch {
      names = null;
    }
    langSelect.replaceChildren(
      h('option', { value: 'auto' }, t('commentary.langAuto')),
      ...langs.map((code) => h('option', { value: code },
        `${names?.of(code) || code.toUpperCase()}${fileTracks.has(code) ? ` (${t('commentary.fromFile')})` : ''}`)),
    );
    langSelect.value = s.commentaryLang !== 'auto' && langs.includes(s.commentaryLang) ? s.commentaryLang : 'auto';
    langSelect.hidden = langs.length < 1;
    langSelect.setAttribute('aria-label', t('commentary.language'));
    langSelect.title = lang ? t('commentary.showing', { lang: names?.of(lang) || lang }) : '';

    captionsBtn.innerHTML = `${icon('captions', 'icon icon--sm')}<span>${t('commentary.captions')}</span>`;
    captionsBtn.setAttribute('aria-pressed', String(s.captions));
    openBtn.innerHTML = `${icon('upload', 'icon icon--sm')}<span>${t('commentary.openFile')}</span>`;
    openBtn.title = t('commentary.openFileHint');
    roleBar.setAttribute('aria-label', t('commentary.roles'));
  }

  let shownCount = -1;
  function renderList(force = false) {
    const s = store.get();
    const track = s.commentary;
    note.classList.remove('is-error');
    if (!track) {
      roleBar.replaceChildren();
      list.replaceChildren();
      note.textContent = '';
      empty.hidden = false;
      empty.innerHTML = `<p><strong>${t('commentary.noneTitle')}</strong></p><p>${t('commentary.noneBody')}</p>`;
      shownCount = -1;
      return;
    }
    const turn = s.replay.frames[s.frame].turn;
    const hidden = new Set(s.hiddenRoles);
    const visible = track.lines.filter((ln) => ln.turn <= turn && !hidden.has(ln.role));
    if (!force && visible.length === shownCount) return;
    const grow = visible.length > shownCount && shownCount >= 0;
    shownCount = visible.length;

    roleBar.innerHTML = track.roles.map((r) => `
      <button type="button" class="role-chip" data-role="${escapeHtml(r.id)}" aria-pressed="${!hidden.has(r.id)}">
        ${icon(r.icon, 'icon icon--sm')}<span>${escapeHtml(r.name)}</span>
      </button>`).join('');

    note.textContent = sourceNote(track);
    const nearBottom = list.scrollHeight - list.scrollTop - list.clientHeight < 60;
    const roleById = new Map(track.roles.map((r) => [r.id, r]));
    list.innerHTML = visible.map((ln) => {
      const role = roleById.get(ln.role) || { name: ln.role, icon: 'chat' };
      return `<li class="cline cline--${escapeHtml(ln.role)}" data-turn="${ln.turn}">
        <span class="cline__turn num">${ln.turn}</span>
        <span class="cline__role">${icon(role.icon, 'icon icon--sm')}${escapeHtml(role.name)}</span>
        <span class="cline__text">${escapeHtml(ln.text)}</span>
      </li>`;
    }).join('');
    empty.hidden = visible.length > 0;
    if (!visible.length) empty.innerHTML = `<p>${t('commentary.notYet')}</p>`;
    if (!pane.hidden && (grow ? nearBottom || s.playing : true)) list.scrollTop = list.scrollHeight;
  }

  function renderCaption() {
    const s = store.get();
    const track = s.commentary;
    if (!s.captions || !track) {
      caption.hidden = true;
      return;
    }
    const turn = s.replay.frames[s.frame].turn;
    const hidden = new Set(s.hiddenRoles);
    const captionRoles = new Set(track.roles.filter((r) => r.caption && !hidden.has(r.id)).map((r) => r.id));
    let latest = null;
    for (const ln of track.lines) {
      if (ln.turn > turn) break;
      if (captionRoles.has(ln.role) && turn - ln.turn < CAPTION_TURNS) latest = ln;
    }
    if (!latest) {
      caption.hidden = true;
      return;
    }
    const role = track.roles.find((r) => r.id === latest.role);
    const key = `${latest.turn}:${latest.role}`;
    if (caption.dataset.key !== key) {
      caption.dataset.key = key;
      caption.innerHTML = `<span class="board-caption__role">${icon(role.icon, 'icon icon--sm')}${escapeHtml(role.name)}</span>`
        + `<span class="board-caption__text">${escapeHtml(latest.text)}</span>`;
      caption.classList.remove('is-new');
      void caption.offsetWidth;
      caption.classList.add('is-new');
    }
    caption.hidden = false;
  }

  function sourceNote(track) {
    if (track.origin === 'file') return t('commentary.sourceFile', { name: track.fileName || 'JSON' });
    const sources = Object.values(track.sources || {});
    if (sources.length && sources.every((src) => src.provider === 'mock')) return t('commentary.sourceMock');
    const models = [...new Set(sources.map((src) => src.model).filter(Boolean))];
    return models.length ? t('commentary.sourceModel', { model: models.join(', ') }) : '';
  }

  store.subscribe(['commentaryLang'], () => { renderControls(); loadTrack(); });
  store.subscribe(['commentary'], () => { renderList(true); renderCaption(); });
  store.subscribe(['frame', 'hiddenRoles'], (s, changed) => {
    renderList(changed.includes('hiddenRoles'));
    renderCaption();
  });
  store.subscribe(['captions'], () => { renderControls(); renderCaption(); });
  store.subscribe(['tab'], (s) => s.tab === 'commentary' && renderList(true));
  onLangChange(() => {
    renderControls();
    if (store.get().commentaryLang === 'auto') loadTrack();
    else renderList(true);
  });

  renderControls();
  loadTrack();
}

/** Accept the site format or the offline import format; return one shape for rendering. */
function normalize(data, lang, origin, current = null, fileName = '') {
  if (!Array.isArray(data.lines)) throw new Error('"lines" must be a list');
  const lines = data.lines
    .filter((ln) => ln && Number.isFinite(ln.turn) && typeof ln.text === 'string' && ln.text.trim())
    .map((ln) => ({ turn: Math.round(ln.turn), role: String(ln.role || 'caster'), text: ln.text.trim() }))
    .sort((a, b) => a.turn - b.turn);
  if (!lines.length) throw new Error('no usable lines');
  const known = new Map([...(current?.roles || []), ...(Array.isArray(data.roles) ? data.roles : [])].map((r) => [r.id, r]));
  const roles = [...new Set(lines.map((ln) => ln.role))].map((id) => {
    const r = known.get(id) || {};
    return { id, name: r.name || id, icon: KNOWN_ICONS.has(r.icon) ? r.icon : 'chat', caption: r.caption ?? id !== 'analyst' };
  });
  return { language: lang, roles, lines, sources: data.sources || {}, origin, fileName };
}

function frameForTurn(replay, turn) {
  const k = replay.frames.findIndex((f) => f.turn >= turn);
  return k < 0 ? replay.frames.length - 1 : k;
}
