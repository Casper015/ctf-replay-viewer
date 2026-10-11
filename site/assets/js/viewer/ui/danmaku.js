// Bullet comments (弹幕): lines from roles with display "danmaku" (the crowd) fly across the
// board as playback passes their turn. Only forward playback and single steps spawn them, so
// seeking never floods the screen. Once spawned a comment finishes its flight, even if
// playback pauses, so comments from single steps are seen too.
//
// Store keys used: commentary (track from ui/commentary.js), danmaku (on/off), hiddenRoles.

import { $, prefersReducedMotion } from '../../core/dom.js';
import { icon } from '../../core/icons.js';
import { onLangChange, t } from '../../core/i18n.js';

const LANES = 6;            // rows in the top ~65% of the board, clear of the caption
const MAX_ON_SCREEN = 14;
const FLY_MS = 7000;        // real time to cross the board, independent of playback speed
const MAX_STEP = 3;         // frames jumped at once that still count as "playing through"

export function mountDanmaku(store) {
  const layer = $('#danmaku');
  const boardBtn = $('#btn-danmaku');
  const reduceMotion = prefersReducedMotion();
  const laneFreeAt = new Array(LANES).fill(0);
  let lastFrame = store.get().frame;

  function spawn(text) {
    if (layer.childElementCount >= MAX_ON_SCREEN) return;
    const now = performance.now();
    const lane = laneFreeAt.indexOf(Math.min(...laneFreeAt));
    if (laneFreeAt[lane] > now + 1200) return; // every lane busy: drop rather than overlap
    const el = document.createElement('span');
    el.className = 'dm';
    el.textContent = text;
    el.style.top = `${4 + lane * (62 / LANES)}%`;
    el.style.setProperty('--w', `${layer.clientWidth}px`);
    el.style.setProperty('--dur', `${FLY_MS}ms`);
    el.addEventListener('animationend', () => el.remove());
    layer.append(el);
    // The lane frees once this comment has moved its own width plus a gap
    const share = (el.offsetWidth + 40) / (layer.clientWidth + el.offsetWidth);
    laneFreeAt[lane] = Math.max(now, laneFreeAt[lane]) + FLY_MS * share;
  }

  function clear() {
    layer.replaceChildren();
    laneFreeAt.fill(0);
  }

  store.subscribe(['frame'], (s) => {
    const prev = lastFrame;
    lastFrame = s.frame;
    const track = s.commentary;
    if (!s.danmaku || reduceMotion || !track) return;
    if (s.frame <= prev || s.frame - prev > MAX_STEP) {
      clear(); // seek or rewind: start fresh
      return;
    }
    const hidden = new Set(s.hiddenRoles);
    const roles = new Set(track.roles.filter((r) => r.display === 'danmaku' && !hidden.has(r.id)).map((r) => r.id));
    if (!roles.size) return;
    const from = s.replay.frames[prev].turn;
    const to = s.replay.frames[s.frame].turn;
    for (const ln of track.lines) {
      if (ln.turn > to) break;
      if (ln.turn > from && roles.has(ln.role)) spawn(ln.text);
    }
  });

  store.subscribe(['commentary'], clear);

  function renderToggle() {
    const s = store.get();
    const has = Boolean(s.commentary?.roles.some((r) => r.display === 'danmaku'));
    boardBtn.hidden = !has || reduceMotion;
    boardBtn.innerHTML = icon('chat', 'icon');
    boardBtn.setAttribute('aria-pressed', String(s.danmaku));
    const label = t(s.danmaku ? 'danmaku.hide' : 'danmaku.show');
    boardBtn.setAttribute('aria-label', label);
    boardBtn.title = label;
    boardBtn.classList.toggle('is-off', !s.danmaku);
  }
  boardBtn.addEventListener('click', () => store.set({ danmaku: !store.get().danmaku }));
  store.subscribe(['danmaku'], (s) => {
    if (!s.danmaku) clear();
    renderToggle();
  });
  store.subscribe(['commentary'], renderToggle);
  onLangChange(renderToggle);
  renderToggle();
}
