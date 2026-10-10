// Feed pane: key moments you can jump to, what happened this turn, and orders for the
// focused team.

import { $, escapeHtml, h } from '../../core/dom.js';
import { icon } from '../../core/icons.js';
import { onLangChange, t } from '../../core/i18n.js';
import { swatchSvg, teamName, teamOfUnit } from '../../core/teams.js';
import { unitLabel } from './board-view.js';
import { findOrder, MOVE_ARROWS } from './unit-card.js';

const FILTERS = ['all', 'capture', 'carrierKill', 'lead'];
const EVENT_ICONS = { capture: 'trophy', pickup: 'flag', drop: 'flag', death: 'skull', attack: 'swords', respawn: 'respawn', return: 'flag' };
const MOMENT_ICONS = { capture: 'trophy', carrierKill: 'swords', lead: 'chart' };

export function mountFeed(store, { playback }) {
  const pane = $('#pane-feed');
  let filter = 'all';

  const filterBar = h('div', { class: 'segmented segmented--sm feed-filter', role: 'group' });
  const momentsList = h('ol', { class: 'moments' });
  const turnHead = h('h3', { class: 'pane-title' });
  const turnList = h('ul', { class: 'events' });
  const ordersHead = h('h3', { class: 'pane-title' });
  const ordersList = h('ul', { class: 'orders' });
  pane.replaceChildren(
    h('section', { class: 'feed-block' }, h('h3', { class: 'pane-title', 'data-i18n': 'feed.moments' }), filterBar, momentsList),
    h('section', { class: 'feed-block' }, turnHead, turnList),
    h('section', { class: 'feed-block' }, ordersHead, ordersList),
  );

  const filterButtons = FILTERS.map((key) => {
    const b = h('button', { type: 'button', 'data-i18n': `feed.filter.${key}` });
    b.addEventListener('click', () => {
      filter = key;
      renderMoments(store.get());
    });
    return b;
  });
  filterBar.append(...filterButtons);

  momentsList.addEventListener('click', (e) => {
    const item = e.target.closest('[data-frame]');
    if (item) playback.seek(Number(item.dataset.frame));
  });

  const name = (s, team) => escapeHtml(teamName(s.replay.names[team]));
  const teamTag = (s, team) => `<span class="team-tag">${swatchSvg(team, 10)}${name(s, team)}</span>`;
  const unitTag = (s, unit) => `<span class="team-tag">${swatchSvg(teamOfUnit(unit), 10)}${escapeHtml(unitLabel(s.replay, unit))}</span>`;

  function momentText(s, m) {
    if (m.kind === 'capture') return t('moment.capture', { team: teamTag(s, m.team), score: s.derived.stats[m.frame][m.team].score });
    if (m.kind === 'carrierKill') {
      return m.by === null
        ? t('moment.carrierDown', { team: teamTag(s, m.team) })
        : t('moment.carrierKill', { by: teamTag(s, m.by), team: teamTag(s, m.team) });
    }
    return t('moment.lead', { team: teamTag(s, m.team) });
  }

  let renderedMoments = [];
  function renderMoments(s) {
    filterBar.setAttribute('aria-label', t('feed.filterLabel'));
    filterButtons.forEach((b, k) => b.setAttribute('aria-pressed', String(FILTERS[k] === filter)));
    renderedMoments = s.derived.moments.filter((m) => (filter === 'all' || m.kind === filter)
      && (s.focusTeam < 0 || m.team === s.focusTeam || m.by === s.focusTeam));
    momentsList.innerHTML = renderedMoments.length
      ? renderedMoments.map((m) => `
        <li><button type="button" class="moment moment--${m.kind}" data-frame="${m.frame}">
          <span class="moment__turn num">${m.turn}</span>
          ${icon(MOMENT_ICONS[m.kind], 'icon icon--sm moment__icon')}
          <span class="moment__text">${momentText(s, m)}</span>
        </button></li>`).join('')
      : `<li class="empty">${t('feed.noMoments')}</li>`;
    markCurrent(s, true);
  }

  // Highlight the latest moment at or before the current frame and keep it in view
  let currentIdx = -1;
  function markCurrent(s, force = false) {
    let idx = -1;
    for (let k = 0; k < renderedMoments.length && renderedMoments[k].frame <= s.frame; k++) idx = k;
    if (idx === currentIdx && !force) return;
    const items = momentsList.querySelectorAll('.moment');
    items[currentIdx]?.classList.remove('is-current');
    currentIdx = idx;
    const el = items[idx];
    if (el) {
      el.classList.add('is-current');
      if (!pane.hidden && s.playing) el.scrollIntoView({ block: 'nearest' });
    }
  }

  function eventText(s, e) {
    switch (e.type) {
      case 'capture': return t('event.capture', { unit: unitTag(s, e.unit), flag: e.flag });
      case 'pickup': return t('event.pickup', { unit: unitTag(s, e.unit), flag: e.flag });
      case 'drop': return t('event.drop', { unit: unitTag(s, e.unit), flag: e.flag });
      case 'attack': return t('event.attack', { unit: unitTag(s, e.unit), target: unitTag(s, e.target) });
      case 'respawn': return t('event.respawn', { unit: unitTag(s, e.unit) });
      case 'return': return t('event.return', { flag: e.flag });
      case 'death': {
        const by = e.by || [];
        let text = by.length
          ? t('event.death', { unit: unitTag(s, e.unit), killer: unitTag(s, by[0]) })
          : t('event.deathNoKiller', { unit: unitTag(s, e.unit) });
        if (by.length > 1) text += t('event.assist', { names: by.slice(1).map((u) => unitTag(s, u)).join(t('common.listSep')) });
        if (e.flag !== null && e.flag !== undefined) text += t('event.droppedFlag', { flag: e.flag });
        return text;
      }
      default: return escapeHtml(JSON.stringify(e));
    }
  }

  const involves = (e, team) => [e.unit, e.target, ...(e.by || [])]
    .some((u) => u !== undefined && u !== null && teamOfUnit(u) === team) || e.team === team;

  function renderTurn(s) {
    const f = s.replay.frames[s.frame];
    turnHead.textContent = t('feed.thisTurn', { turn: f.turn });
    const evs = f.events
      .filter((e) => s.focusTeam < 0 || involves(e, s.focusTeam))
      .sort((a, b) => order(a) - order(b));
    turnList.innerHTML = evs.length
      ? evs.map((e) => `<li class="event event--${e.type}">${icon(EVENT_ICONS[e.type] || 'info', 'icon icon--sm')}<span>${eventText(s, e)}</span></li>`).join('')
      : `<li class="empty">${t('feed.quietTurn')}</li>`;
  }

  function renderOrders(s) {
    const team = s.focusTeam >= 0 ? s.focusTeam : (s.selectedUnit !== null ? teamOfUnit(s.selectedUnit) : -1);
    if (team < 0) {
      ordersHead.textContent = t('feed.orders');
      ordersList.innerHTML = `<li class="empty">${t('feed.ordersHint')}</li>`;
      return;
    }
    ordersHead.innerHTML = `${t('feed.ordersFor')} ${teamTag(s, team)}`;
    const f = s.replay.frames[s.frame];
    const rows = [0, 1, 2].map((slot) => {
      const id = team * 3 + slot;
      const o = findOrder(f, team, id);
      if (!o) return `<li>${unitTag(s, id)} <span class="muted">${t('unit.noOrder')}</span></li>`;
      const act = o.act && o.act !== 'wait'
        ? ` ${t('act.' + o.act)}${o.act === 'attack' && o.target !== undefined ? ' ' + unitTag(s, o.target) : ''}` : '';
      const note = o.note ? ` <q class="order-note">${escapeHtml(o.note)}</q>` : '';
      return `<li>${unitTag(s, id)} <span class="order-move" title="${escapeHtml(t('move.' + (o.move || 'WAIT')))}">${MOVE_ARROWS[o.move] || '·'}</span>${act}${note}</li>`;
    });
    ordersList.innerHTML = rows.join('');
  }

  store.subscribe(['frame'], (s) => {
    renderTurn(s);
    renderOrders(s);
    markCurrent(s);
  });
  store.subscribe(['focusTeam'], (s) => {
    renderMoments(s);
    renderTurn(s);
    renderOrders(s);
  });
  store.subscribe(['selectedUnit'], renderOrders);
  store.subscribe(['tab'], (s) => s.tab === 'feed' && markCurrent(s, true));
  onLangChange(() => {
    const s = store.get();
    renderMoments(s);
    renderTurn(s);
    renderOrders(s);
  });
  const s = store.get();
  renderMoments(s);
  renderTurn(s);
  renderOrders(s);
}

// Show what matters first
const EVENT_ORDER = { capture: 0, death: 1, pickup: 2, drop: 3, return: 4, respawn: 5, attack: 6 };
const order = (e) => EVENT_ORDER[e.type] ?? 9;
