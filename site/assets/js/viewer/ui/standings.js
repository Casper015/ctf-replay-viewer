// Standings pane: live ranking, each team's three units, and where the flags are.
// Rows are keyed by team and reordered with CSS `order`, so focus and hover survive updates.

import { $, escapeHtml, h } from '../../core/dom.js';
import { icon } from '../../core/icons.js';
import { onLangChange, t } from '../../core/i18n.js';
import { swatchSvg, teamColor, teamName, teamShape, traceShape } from '../../core/teams.js';

export function mountStandings(store) {
  const pane = $('#pane-standings');
  const flagsEl = h('div', { class: 'flag-strip', 'aria-live': 'off' });
  const list = h('ol', { class: 'standings' });
  const hint = h('p', { class: 'pane-hint', 'data-i18n': 'standings.hint' });
  pane.replaceChildren(flagsEl, list, hint);

  const { replay } = store.get();
  const rows = replay.names.map((_, team) => {
    const btn = h('button', { type: 'button', class: 'standing', dataset: { team: String(team) } });
    btn.addEventListener('click', () => {
      const s = store.get();
      store.set({ focusTeam: s.focusTeam === team ? -1 : team });
    });
    const li = h('li', {}, btn);
    list.append(li);
    return { li, btn, lastScore: 0 };
  });

  let lastFrame = store.get().frame;
  function render(s) {
    const f = s.replay.frames[s.frame];
    const ranking = s.derived.ranking(s.frame);
    const stepped = s.frame === lastFrame + 1; // flash only on forward play/steps, not seeks
    lastFrame = s.frame;
    ranking.forEach((row, rank) => {
      const r = rows[row.team];
      const units = f.units.slice(row.team * 3, row.team * 3 + 3);
      const scored = stepped && row.score > r.lastScore;
      r.li.style.order = String(rank);
      r.btn.setAttribute('aria-pressed', String(s.focusTeam === row.team));
      r.btn.classList.toggle('is-dim', s.focusTeam >= 0 && s.focusTeam !== row.team);
      r.btn.innerHTML = `
        <span class="standing__rank num">${rank + 1}</span>
        ${swatchSvg(row.team, 14)}
        <span class="standing__name">${escapeHtml(teamName(s.replay.names[row.team]))}</span>
        <span class="standing__units">${units.map((u) => unitPip(row.team, u)).join('')}</span>
        <span class="standing__score num">${row.score}</span>`;
      if (scored) {
        r.btn.classList.remove('scored');
        void r.btn.offsetWidth; // restart the flash animation
        r.btn.classList.add('scored');
      }
      r.lastScore = row.score;
    });
    renderFlags(s, f);
  }

  function renderFlags(s, f) {
    flagsEl.innerHTML = f.flags.map((fl) => {
      let text;
      if (fl.status === 'carried' && fl.holder !== null) {
        const team = Math.floor(fl.holder / 3);
        text = `${swatchSvg(team, 10)}${escapeHtml(teamName(s.replay.names[team]))}`;
      } else if (fl.status === 'dropped') {
        text = t('flags.dropped', { count: Math.max(0, fl.return_at - f.turn) });
      } else if (fl.status === 'cooldown') {
        text = t('flags.cooldown', { count: Math.max(0, fl.return_at - f.turn) });
      } else {
        text = t('flags.home');
      }
      return `<span class="flag-chip flag-chip--${fl.status}">${icon('flag', 'icon icon--sm')}<b class="num">${fl.id}</b><span>${text}</span></span>`;
    }).join('');
  }

  store.subscribe(['frame', 'focusTeam'], render);
  onLangChange(() => render(store.get()));
  render(store.get());
}

/** Small unit status mark: filled shape alive, hollow when dead, gold ring while carrying. */
function unitPip(team, u) {
  const color = teamColor(team);
  const shape = teamShape(team);
  const carrying = u.pos && u.flag !== null && u.flag !== undefined;
  const state = !u.pos ? 'dead' : carrying ? 'carrying' : 'alive';
  const d = shapePath(shape, 6, 6, 3.6);
  const fill = state === 'dead' ? 'none' : color;
  const stroke = state === 'carrying' ? '#ffc24b' : color;
  return `<svg class="pip pip--${state}" viewBox="0 0 12 12" aria-hidden="true"><path d="${d}" fill="${fill}" stroke="${stroke}" stroke-width="${state === 'carrying' ? 2 : 1.25}"/></svg>`;
}

const pathCache = new Map();
function shapePath(shape, cx, cy, r) {
  const key = shape + r;
  if (pathCache.has(key)) return pathCache.get(key);
  const rec = new PathRecorder();
  traceShape(rec, shape, cx, cy, r);
  const d = rec.toString();
  pathCache.set(key, d);
  return d;
}

// Records canvas path calls as an SVG path string (only the calls traceShape uses).
class PathRecorder {
  constructor() { this.parts = []; this.x = 0; this.y = 0; }
  beginPath() { this.parts = []; }
  moveTo(x, y) { this.parts.push(`M${x.toFixed(2)} ${y.toFixed(2)}`); this.x = x; this.y = y; }
  lineTo(x, y) { this.parts.push(`L${x.toFixed(2)} ${y.toFixed(2)}`); this.x = x; this.y = y; }
  arc(cx, cy, r) {
    this.parts.push(`M${(cx - r).toFixed(2)} ${cy.toFixed(2)}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0`);
  }
  arcTo(x1, y1, x2, y2) {
    // Approximate the rounded corner with a quadratic curve through the corner point
    this.parts.push(`Q${x1.toFixed(2)} ${y1.toFixed(2)} ${x2.toFixed(2)} ${y2.toFixed(2)}`);
    this.x = x2; this.y = y2;
  }
  closePath() { this.parts.push('Z'); }
  toString() { return this.parts.join(''); }
}
