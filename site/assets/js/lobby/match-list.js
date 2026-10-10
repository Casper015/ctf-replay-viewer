// Match list: one row per catalog entry with a map thumbnail, the score race of the top
// three, and the final podium. Filtering and search toggle rows instead of rebuilding them.

import { $, escapeHtml, h } from '../core/dom.js';
import { onLangChange, pick, t } from '../core/i18n.js';
import { EN_NAMES, swatchSvg, teamColor, teamName } from '../core/teams.js';
import { Camera } from '../board/camera.js';
import { drawTerrain } from '../board/terrain.js';

const RACE_W = 168;
const RACE_H = 48;

export function mountMatchList(catalog) {
  const list = $('#match-list');
  const filtersEl = $('#filters');
  const search = $('#search');
  const empty = $('#list-empty');
  let filter = 'all';
  let query = '';
  let rows = [];

  // One filter per team count present in the catalog, largest first
  const counts = [...new Set(catalog.matches.map((m) => m.teams))].sort((a, b) => b - a);
  const filters = ['all', ...counts];

  function renderFilters() {
    filtersEl.replaceChildren(...filters.map((f) => {
      const n = f === 'all' ? catalog.matches.length : catalog.matches.filter((m) => m.teams === f).length;
      const label = f === 'all' ? t('lobby.filterAll') : t('match.teams', { count: f });
      const b = h('button', { type: 'button', 'aria-pressed': String(f === filter) }, label, ' ', h('span', { class: 'count' }, String(n)));
      b.addEventListener('click', () => {
        filter = f;
        renderFilters();
        apply();
      });
      return b;
    }));
  }

  function renderRows() {
    rows = catalog.matches.map((m) => {
      const canvas = h('canvas', { class: 'match-row__map', width: '96', height: '96', 'aria-hidden': 'true' });
      const top = m.standings.slice(0, Math.min(3, m.teams));
      const lead = top[0].score;
      const a = h('a', { class: 'match-row', href: `match.html?m=${encodeURIComponent(m.key)}` });
      a.innerHTML = `
        <div class="match-row__body">
          <div class="match-row__chips">
            <span class="chip">${t('match.teams', { count: m.teams })}</span>
            <span class="chip chip--outline">${t('match.map', { size: m.size })}</span>
            <span class="match-row__tag">${escapeHtml(pick(m.tag))}</span>
          </div>
          <h3 class="match-row__title">${escapeHtml(pick(m.title))}</h3>
          <p class="match-row__desc">${escapeHtml(pick(m.desc))}</p>
        </div>
        <div class="match-row__facts">
          <div class="match-row__race">
            ${raceSvg(m)}
            <span class="match-row__race-caption">${t('lobby.captures', { count: m.totalCaptures })}${t('common.listSep')}${t('lobby.leadChanges', { count: m.leadChanges })}</span>
          </div>
          <ol class="match-row__podium" aria-label="${escapeHtml(t('lobby.podiumLabel'))}">
            ${top.map((r) => `
              <li class="podium-row${r.score === lead ? ' is-lead' : ''}">
                ${swatchSvg(r.team, 12)}
                <span class="podium-row__name">${escapeHtml(teamName(r.name))}</span>
                <span class="podium-row__score num">${r.score}</span>
              </li>`).join('')}
          </ol>
        </div>`;
      a.prepend(canvas);
      drawMinimap(canvas, m);
      const li = h('li', {}, a);
      return { li, m, text: searchText(m) };
    });
    list.replaceChildren(...rows.map((r) => r.li));
    apply();
  }

  function apply() {
    const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const r of rows) {
      const ok = (filter === 'all' || r.m.teams === filter) && terms.every((term) => r.text.includes(term));
      r.li.hidden = !ok;
      if (ok) shown++;
    }
    empty.hidden = shown > 0;
  }

  search.addEventListener('input', () => {
    query = search.value;
    apply();
  });
  $('#clear-filters').addEventListener('click', () => {
    filter = 'all';
    query = '';
    search.value = '';
    renderFilters();
    apply();
  });

  renderFilters();
  renderRows();
  onLangChange(() => {
    renderFilters();
    renderRows();
  });
}

function searchText(m) {
  const names = m.standings.flatMap((s) => [s.name, EN_NAMES[s.name] || '']);
  return [m.key, m.id, ...['tag', 'title', 'desc'].flatMap((f) => [m[f].zh, m[f].en]), ...names]
    .join(' ').toLowerCase();
}

/** Step lines for the top three teams, built from the catalog's capture log. */
function raceSvg(m) {
  const top = m.standings.slice(0, Math.min(3, m.teams)).map((s) => s.team);
  const max = Math.max(1, m.standings[0].score);
  const x = (turn) => ((turn / m.turns) * RACE_W).toFixed(1);
  const y = (score) => (RACE_H - (score / max) * (RACE_H - 4) - 2).toFixed(1);
  const paths = top.map((team, k) => {
    let score = 0;
    let d = `M0 ${y(0)}`;
    for (const [turn, tm] of m.captures) {
      if (tm !== team) continue;
      d += `H${x(turn)}V${y(++score)}`;
    }
    d += `H${RACE_W}`;
    return { team, d, k };
  }).reverse(); // leader drawn last, on top
  const label = t('lobby.raceLabel');
  return `<svg viewBox="0 0 ${RACE_W} ${RACE_H}" preserveAspectRatio="none" role="img" aria-label="${escapeHtml(label)}">
    ${paths.map((p) => `<path d="${p.d}" fill="none" stroke="${teamColor(p.team)}" stroke-width="${p.k === 0 ? 2.25 : 1.5}" stroke-linejoin="round" vector-effect="non-scaling-stroke" opacity="${p.k === 0 ? 1 : 0.75}"/>`).join('')}
  </svg>`;
}

function drawMinimap(canvas, m) {
  const css = 96;
  const dpr = Math.min(window.devicePixelRatio || 1, 3);
  canvas.width = Math.round(css * dpr);
  canvas.height = Math.round(css * dpr);
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const cam = new Camera();
  cam.setBoard(m.size);
  cam.setViewport(css, css);
  drawTerrain(ctx, { size: m.size, map: m.map, bases: m.bases, flagSpots: m.flagSpots }, cam);
}

