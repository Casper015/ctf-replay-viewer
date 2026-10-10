// Broadcast-style score strip at the top of the side panel (desktop/tablet).

import { $, escapeHtml } from '../../core/dom.js';
import { onLangChange } from '../../core/i18n.js';
import { swatchSvg, teamName } from '../../core/teams.js';

export function mountScorebug(store) {
  const el = $('#scorebug');
  const { replay } = store.get();
  const shown = replay.header.teams === 2 ? 2 : Math.min(3, replay.header.teams);

  function render(s) {
    const ranking = s.derived.ranking(s.frame);
    const top = ranking[0].score;
    el.innerHTML = ranking.slice(0, shown).map((row) => `
      <div class="scorebug__team${row.score === top && top > 0 ? ' is-lead' : ''}${s.focusTeam >= 0 && s.focusTeam !== row.team ? ' is-dim' : ''}">
        ${swatchSvg(row.team, 14)}
        <span class="scorebug__name">${escapeHtml(teamName(s.replay.names[row.team]))}</span>
        <span class="scorebug__score num">${row.score}</span>
      </div>`).join('');
  }

  store.subscribe(['frame', 'focusTeam'], render);
  onLangChange(() => render(store.get()));
  render(store.get());
}
