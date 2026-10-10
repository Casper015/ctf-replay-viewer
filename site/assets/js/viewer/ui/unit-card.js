// Card for the selected unit: health, flag, respawn timer, this turn's order, follow toggle.

import { $, escapeHtml } from '../../core/dom.js';
import { icon } from '../../core/icons.js';
import { onLangChange, t } from '../../core/i18n.js';
import { fmtInt } from '../../core/format.js';
import { swatchSvg, teamOfUnit } from '../../core/teams.js';
import { unitLabel } from './board-view.js';

const MOVE_ARROWS = { N: '↑', S: '↓', E: '→', W: '←', WAIT: '·' };

export function mountUnitCard(store) {
  const card = $('#unit-card');

  card.addEventListener('click', (e) => {
    const action = e.target.closest('[data-action]')?.dataset.action;
    if (action === 'close') store.set({ selectedUnit: null, follow: false });
    if (action === 'follow') store.set({ follow: !store.get().follow });
  });

  function render(s) {
    const id = s.selectedUnit;
    if (id === null || id === undefined) {
      card.hidden = true;
      return;
    }
    const { replay, derived, frame } = s;
    const f = replay.frames[frame];
    const u = f.units[id];
    const team = teamOfUnit(id);
    const hpMax = replay.header.rules.hp || 100;
    const order = findOrder(f, team, id);

    let status;
    if (!u.pos) {
      const back = derived.respawnFrame(id, frame);
      status = back === null
        ? t('unit.outForGood')
        : t('unit.respawnsIn', { count: replay.frames[back].turn - f.turn });
    } else if (u.flag !== null && u.flag !== undefined) {
      status = `<span class="unit-card__flag">${icon('flag', 'icon icon--sm')}${t('unit.carrying', { flag: u.flag })}</span>`;
    } else {
      status = t('unit.inPlay');
    }

    let orderHtml = `<span class="muted">${t('unit.noOrder')}</span>`;
    if (order) {
      const parts = [`<span class="unit-card__move" title="${escapeHtml(t('move.' + (order.move || 'WAIT')))}">${MOVE_ARROWS[order.move] || '·'}</span>`];
      if (order.act && order.act !== 'wait') {
        let act = t('act.' + order.act);
        if (order.act === 'attack' && order.target !== undefined) act += ` ${escapeHtml(unitLabel(replay, order.target))}`;
        parts.push(`<span>${act}</span>`);
      }
      if (order.note) parts.push(`<q class="unit-card__note">${escapeHtml(order.note)}</q>`);
      orderHtml = parts.join(' ');
    }

    card.innerHTML = `
      <div class="unit-card__head">
        ${swatchSvg(team, 16)}
        <strong>${escapeHtml(unitLabel(replay, id))}</strong>
        <button class="icon-btn unit-card__close" type="button" data-action="close" aria-label="${escapeHtml(t('common.close'))}">${icon('x', 'icon icon--sm')}</button>
      </div>
      <div class="unit-card__hp" role="meter" aria-valuemin="0" aria-valuemax="${hpMax}" aria-valuenow="${u.hp}" aria-label="${escapeHtml(t('unit.health'))}">
        <span class="unit-card__hp-bar" style="--hp:${Math.max(0, u.hp / hpMax)}"></span>
        <span class="num">${fmtInt(u.hp)}<span class="muted">/${hpMax}</span></span>
      </div>
      <p class="unit-card__status">${status}</p>
      <p class="unit-card__order"><span class="muted">${t('unit.order')}</span> ${orderHtml}</p>
      <button class="btn btn--ghost unit-card__follow" type="button" data-action="follow" aria-pressed="${s.follow}">
        ${icon('crosshair', 'icon icon--sm')}<span>${t(s.follow ? 'unit.following' : 'unit.follow')}</span>
      </button>`;
    card.hidden = false;
  }

  store.subscribe(['selectedUnit', 'frame', 'follow'], render);
  onLangChange(() => render(store.get()));
}

function findOrder(frame, team, id) {
  const raw = frame.orders?.[team] ?? frame.orders?.[String(team)];
  const list = Array.isArray(raw) ? raw : raw?.units;
  return Array.isArray(list) ? list.find((o) => o.id === id) : null;
}

export { findOrder, MOVE_ARROWS };
