// Top bar: match title and facts, match picker, shortcuts, language, immersive mode.

import { $, escapeHtml } from '../../core/dom.js';
import { icon } from '../../core/icons.js';
import { getLang, onLangChange, pick, t } from '../../core/i18n.js';
import { mountLangSwitch } from '../../core/lang-switch.js';
import { swatchSvg, teamName } from '../../core/teams.js';

export function mountTopbar(store, { catalog, toggleImmersive }) {
  const { entry } = store.get();
  const title = $('#match-title');
  const meta = $('#match-meta');
  const pickerBtn = $('#btn-matches');
  const picker = $('#dlg-matches');
  const pickerList = $('#matches-list');
  const shortcutsBtn = $('#btn-shortcuts');
  const shortcuts = $('#dlg-shortcuts');
  const immersiveBtn = $('#btn-immersive');

  mountLangSwitch($('#lang-switch'));

  function renderTitle() {
    title.textContent = pick(entry.title);
    title.title = pick(entry.title);
    meta.innerHTML = [
      `<span class="chip">${t('match.teams', { count: entry.teams })}</span>`,
      `<span class="chip chip--outline">${t('match.map', { size: entry.size })}</span>`,
      `<span class="topbar__id">${escapeHtml(entry.id)}</span>`,
    ].join('');
    document.title = `${pick(entry.title)} | ${t('site.name')}`;
  }

  function renderPicker() {
    pickerList.innerHTML = catalog.matches.map((m) => {
      const winner = m.standings[0];
      const score = m.standings.slice(0, Math.min(3, m.teams)).map((r) => r.score).join(getLang() === 'zh' ? ':' : '–');
      return `
        <li><a class="picker-item${m.key === entry.key ? ' is-current' : ''}" href="match.html?m=${encodeURIComponent(m.key)}"${m.key === entry.key ? ' aria-current="page"' : ''}>
          <span class="picker-item__teams num">${m.teams}</span>
          <span class="picker-item__body">
            <span class="picker-item__title">${escapeHtml(pick(m.title))}</span>
            <span class="picker-item__meta">${swatchSvg(winner.team, 10)}${escapeHtml(teamName(winner.name))} <span class="num">${score}</span></span>
          </span>
        </a></li>`;
    }).join('');
  }

  pickerBtn.addEventListener('click', () => {
    renderPicker();
    picker.showModal();
    picker.querySelector('.is-current')?.scrollIntoView({ block: 'center' });
  });
  shortcutsBtn.addEventListener('click', () => shortcuts.showModal());
  for (const dlg of [picker, shortcuts]) {
    dlg.addEventListener('click', (e) => {
      // Click on the backdrop (the dialog element itself) or a close button closes it
      if (e.target === dlg || e.target.closest('[data-close]')) dlg.close();
    });
  }
  immersiveBtn.addEventListener('click', toggleImmersive);
  $('#btn-exit-immersive').addEventListener('click', toggleImmersive);

  function renderImmersive(s) {
    immersiveBtn.innerHTML = icon(s.immersive ? 'minimize' : 'maximize');
    const label = t(s.immersive ? 'viewer.exitImmersive' : 'viewer.immersive');
    immersiveBtn.setAttribute('aria-label', label);
    immersiveBtn.title = `${label} (F)`;
    immersiveBtn.setAttribute('aria-pressed', String(s.immersive));
  }

  store.subscribe(['immersive'], renderImmersive);
  onLangChange(() => {
    renderTitle();
    renderImmersive(store.get());
    if (picker.open) renderPicker();
  });
  renderTitle();
  renderImmersive(store.get());
}
