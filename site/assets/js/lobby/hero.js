// Lobby hero: copy plus a live, looping preview of a random match on the real board renderer.
// A different match is picked on every visit (never the same one twice in a row), and the
// shuffle button swaps to another. Clicking the board opens the viewer at the turn shown.

import { $, escapeHtml, prefersReducedMotion } from '../core/dom.js';
import { icon } from '../core/icons.js';
import { onLangChange, pick, t } from '../core/i18n.js';
import { loadReplay } from '../core/data.js';
import { getPref, setPref } from '../core/prefs.js';
import { swatchSvg, teamName } from '../core/teams.js';
import { BoardRenderer } from '../board/renderer.js';
import { deriveMatch } from '../viewer/derive.js';

const TURN_MS = 110;      // a bit under 2× speed: lively without being a blur
const START_FRAME = 120;  // skip the opening walk out of the bases
const END_HOLD_MS = 2500;

/** Random match, avoiding `avoid` (the one shown last time / right now) when possible. */
export function randomEntry(matches, avoid) {
  const pool = matches.length > 1 ? matches.filter((m) => m.key !== avoid) : matches;
  return pool[Math.floor(Math.random() * pool.length)];
}

export function mountHero(catalog) {
  const lede = $('#hero-lede');
  const browse = $('#hero-browse');
  const watch = $('#hero-watch');
  const link = $('#hero-board-link');
  const hud = $('#hero-hud');
  const caption = $('#hero-caption');
  const canvas = $('#hero-board');
  const renderer = new BoardRenderer(canvas);
  const still = prefersReducedMotion();

  let entry = randomEntry(catalog.matches, getPref('heroLast'));
  let replay = null;
  let frame = 0;
  let enteredAt = 0;
  let visible = true;
  let loadToken = 0;
  let looping = false;

  const href = (turn) => `match.html?m=${encodeURIComponent(entry.key)}${turn ? `&t=${turn}` : ''}`;

  function renderCopy() {
    lede.textContent = t('lobby.heroLede', { count: catalog.matches.length });
    browse.textContent = t('lobby.browseAll', { count: catalog.matches.length });
    watch.href = href(replay ? replay.frames[frame].turn : 0);
    link.setAttribute('aria-label', t('lobby.heroBoardLabel', { title: pick(entry.title) }));
    caption.innerHTML = `
      <span class="hero__caption-meta">
        <span class="chip">${t('match.teams', { count: entry.teams })}</span>
        <span class="chip chip--outline">${t('match.map', { size: entry.size })}</span>
        <span class="match-row__tag">${escapeHtml(pick(entry.tag))}</span>
        <button type="button" class="chip-btn hero__shuffle" id="hero-shuffle" title="${escapeHtml(t('lobby.shuffleHint'))}">
          ${icon('restart', 'icon icon--sm')}<span>${t('lobby.shuffle')}</span>
        </button>
      </span>
      <span class="hero__caption-title"><a href="${href(0)}">${escapeHtml(pick(entry.title))}</a></span>`;
    $('#hero-shuffle').addEventListener('click', () => show(randomEntry(catalog.matches, entry.key)));
  }

  function renderHud(k) {
    const f = replay.frames[k];
    const top = f.score.map((score, team) => ({ score, team })).sort((a, b) => b.score - a.score).slice(0, 3);
    hud.innerHTML = `<span><span class="hud-label">${t('viewer.turnShort')}</span><b class="num">${f.turn}</b></span>`
      + top.map((r, i) => `<span class="${i === 0 && r.score > 0 ? 'is-lead' : ''}">${swatchSvg(r.team, 12)}${escapeHtml(teamName(replay.names[r.team]))}<b class="num">${r.score}</b></span>`).join('');
    link.href = href(f.turn);
    watch.href = href(f.turn);
  }

  function draw(now) {
    if (!replay) return;
    renderer.render({ frame, progress: still ? 1 : Math.min(1, (now - enteredAt) / TURN_MS), now: still ? 0 : now, focusTeam: -1 });
  }

  function loop(now) {
    if (replay && visible && !document.hidden) {
      const last = replay.frames.length - 1;
      const wait = frame === last ? END_HOLD_MS : TURN_MS;
      if (now - enteredAt >= wait) {
        frame = frame === last ? Math.min(START_FRAME, last) : frame + 1;
        enteredAt = now;
        renderHud(frame);
      }
      draw(now);
    }
    requestAnimationFrame(loop);
  }

  async function show(next) {
    entry = next;
    setPref('heroLast', entry.key);
    const token = ++loadToken;
    replay = null;
    hud.innerHTML = '';
    link.href = href(0);
    renderCopy();
    let data;
    try {
      data = await loadReplay(entry);
    } catch {
      return; // the hero stays an empty board frame; the list still works
    }
    if (token !== loadToken) return; // a newer shuffle won
    replay = data;
    renderer.setMatch(replay, deriveMatch(replay));
    renderer.resize();
    const last = replay.frames.length - 1;
    // Reduced motion: show the decisive final capture instead of animating
    frame = still
      ? (entry.captures.length ? frameOfTurn(replay, entry.captures.at(-1)[0]) : last)
      : Math.min(START_FRAME, last);
    enteredAt = performance.now();
    renderHud(frame);
    renderCopy();
    draw(enteredAt);
    if (!still && !looping) {
      looping = true;
      requestAnimationFrame(loop);
    }
  }

  new ResizeObserver(() => { renderer.resize(); draw(performance.now()); }).observe(link);
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(link);
  onLangChange(() => {
    renderCopy();
    if (replay) renderHud(frame);
  });

  renderCopy();
  // Let the list render first; the preview is a nice-to-have
  ('requestIdleCallback' in window ? requestIdleCallback : setTimeout)(() => show(entry), { timeout: 800 });
}

function frameOfTurn(replay, turn) {
  const k = replay.frames.findIndex((f) => f.turn >= turn);
  return k < 0 ? replay.frames.length - 1 : k;
}
