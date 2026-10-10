// Stats pane: four live leader tiles and the full per-team table, both cumulative to the
// current turn.

import { $, escapeHtml, h } from '../../core/dom.js';
import { icon } from '../../core/icons.js';
import { onLangChange, t } from '../../core/i18n.js';
import { fmtDec, fmtPct } from '../../core/format.js';
import { swatchSvg, teamName } from '../../core/teams.js';

const TILES = [
  { key: 'captures', icon: 'trophy', value: (r) => r.score, cls: 'is-flag' },
  { key: 'kills', icon: 'swords', value: (r) => r.kills },
  { key: 'carrierKills', icon: 'flag', value: (r) => r.carrierKills },
  { key: 'kda', icon: 'activity', value: (r) => r.kda, fmt: (v) => fmtDec(v) },
];

export function mountStats(store) {
  const pane = $('#pane-stats');
  const tiles = h('div', { class: 'stat-tiles' });
  const tableWrap = h('div', { class: 'stat-table-wrap', tabindex: '0' });
  const formula = h('p', { class: 'pane-hint' });
  pane.replaceChildren(tiles, tableWrap, formula);

  function render(s) {
    const rows = s.derived.ranking(s.frame);
    const name = (team) => escapeHtml(teamName(s.replay.names[team]));

    tiles.innerHTML = TILES.map((tile) => {
      const best = [...rows].sort((a, b) => tile.value(b) - tile.value(a) || a.team - b.team)[0];
      const v = tile.value(best);
      return `
        <div class="stat-tile ${tile.cls || ''}">
          <span class="stat-tile__label">${icon(tile.icon, 'icon icon--sm')}${t('stats.top.' + tile.key)}</span>
          <span class="stat-tile__value num">${tile.fmt ? tile.fmt(v) : v}</span>
          <span class="stat-tile__team">${v > 0 ? `${swatchSvg(best.team, 12)}${name(best.team)}` : '<span class="muted">—</span>'}</span>
        </div>`;
    }).join('');

    const cols = ['rank', 'team', 'captures', 'pickups', 'conversion', 'kills', 'assists', 'deaths', 'kda'];
    tableWrap.setAttribute('aria-label', t('stats.tableLabel'));
    tableWrap.innerHTML = `
      <table class="stat-table">
        <thead><tr>${cols.map((c) => `<th scope="col" class="col-${c}" title="${escapeHtml(t('stats.colTitle.' + c))}">${t('stats.col.' + c)}</th>`).join('')}</tr></thead>
        <tbody>${rows.map((r, k) => `
          <tr class="${s.focusTeam === r.team ? 'is-focus' : ''}">
            <td class="col-rank num">${k + 1}</td>
            <th scope="row" class="col-team">${swatchSvg(r.team, 12)}<span>${name(r.team)}</span></th>
            <td class="col-captures num">${r.score}</td>
            <td class="num">${r.pickups}</td>
            <td class="num">${r.pickups ? fmtPct(r.conversion) : '—'}</td>
            <td class="num">${r.kills}</td>
            <td class="num">${r.assists}</td>
            <td class="num">${r.deaths}</td>
            <td class="num">${fmtDec(r.kda)}</td>
          </tr>`).join('')}
        </tbody>
      </table>`;
    formula.textContent = t('stats.kdaFormula');
  }

  store.subscribe(['frame', 'focusTeam'], (s) => {
    if (s.tab === 'stats') render(s);
  });
  store.subscribe(['tab'], (s) => s.tab === 'stats' && render(s));
  onLangChange(() => render(store.get()));
  render(store.get());
}
