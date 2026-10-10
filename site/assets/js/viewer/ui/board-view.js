// Board area: canvas renderer + gestures + HUD pills + zoom tools + hover tip.
// Exposes draw(now) for the main animation loop.

import { BoardRenderer } from '../../board/renderer.js';
import { attachGestures } from '../../board/gestures.js';
import { $, escapeHtml, prefersReducedMotion } from '../../core/dom.js';
import { onLangChange, t } from '../../core/i18n.js';
import { fmtInt } from '../../core/format.js';
import { swatchSvg, teamName, teamOfUnit, unitSlot } from '../../core/teams.js';

const IDLE_FRAME_MS = 33;    // ~30 fps for idle animation (breathing auras, waving flags)
const FOLLOW_EASE = 0.14;
const FOLLOW_ZOOM = 2.6;

export function mountBoardView(store, { playback }) {
  const canvas = $('#board');
  const frame = $('#board-frame');
  const tip = $('#board-tip');
  const renderer = new BoardRenderer(canvas);
  const reduceMotion = prefersReducedMotion();
  let hoverUnit = null;
  let dirty = true;
  let lastDraw = 0;

  const s0 = store.get();
  renderer.setMatch(s0.replay, s0.derived);
  renderer.resize();

  new ResizeObserver(() => {
    renderer.resize();
    dirty = true;
  }).observe(frame);

  attachGestures(canvas, renderer.camera, {
    onTap(x, y) {
      const unit = renderer.unitAt(x, y);
      const s = store.get();
      if (unit === null) store.set({ selectedUnit: null, follow: false });
      else store.set({ selectedUnit: unit === s.selectedUnit ? null : unit, follow: unit === s.selectedUnit ? false : s.follow });
      dirty = true;
    },
    onHover(x, y) {
      const unit = x === null ? null : renderer.unitAt(x, y);
      if (unit !== hoverUnit) {
        hoverUnit = unit;
        canvas.style.cursor = unit === null ? '' : 'pointer';
        dirty = true;
      }
      showTip(unit, x, y);
    },
    onCamera() {
      dirty = true;
      syncTools();
    },
    onUserPan() {
      if (store.get().follow) store.set({ follow: false });
    },
  });

  // Zoom tools
  const zoomBy = (factor) => {
    const cam = renderer.camera;
    cam.zoomAt(cam.w / 2, cam.h / 2, factor);
    dirty = true;
    syncTools();
  };
  $('#zoom-in').addEventListener('click', () => zoomBy(1.5));
  $('#zoom-out').addEventListener('click', () => zoomBy(1 / 1.5));
  $('#zoom-fit').addEventListener('click', () => {
    renderer.camera.reset();
    store.set({ follow: false });
    dirty = true;
    syncTools();
  });

  function syncTools() {
    const cam = renderer.camera;
    $('#zoom-in').disabled = cam.zoom >= cam.maxZoom - 0.01;
    $('#zoom-out').disabled = !cam.zoomed;
    $('#zoom-fit').disabled = !cam.zoomed;
  }
  syncTools();

  function showTip(unit, x, y) {
    if (unit === null || x === null) {
      tip.hidden = true;
      return;
    }
    const s = store.get();
    const u = s.replay.frames[s.frame].units[unit];
    const team = teamOfUnit(unit);
    tip.innerHTML = `${swatchSvg(team, 12)}<span>${escapeHtml(unitLabel(s.replay, unit))}</span>`
      + `<span class="board-tip__hp num">${fmtInt(u.hp)}</span>`;
    tip.hidden = false;
    const fw = frame.clientWidth;
    tip.style.left = `${Math.min(fw - tip.offsetWidth - 8, Math.max(8, x + 14))}px`;
    tip.style.top = `${Math.max(8, y - 36)}px`;
  }

  // HUD
  const hudTurn = $('#hud-turn');
  const hudLeader = $('#hud-leader');
  function renderHud(s) {
    const f = s.replay.frames[s.frame];
    const total = s.replay.frames[s.replay.frames.length - 1].turn;
    hudTurn.innerHTML = `<span class="hud-label">${t('viewer.turnShort')}</span><span class="num">${fmtInt(f.turn)}</span><span class="hud-total">/ ${fmtInt(total)}</span>`;
    const top = Math.max(...f.score);
    const leaders = f.score.map((sc, team) => [sc, team]).filter(([sc]) => sc === top).map(([, team]) => team);
    if (top === 0) {
      hudLeader.innerHTML = `<span class="hud-label">${t('viewer.noScoreYet')}</span>`;
    } else if (leaders.length === 1) {
      hudLeader.innerHTML = `${swatchSvg(leaders[0], 12)}<span class="hud-name">${escapeHtml(teamName(s.replay.names[leaders[0]]))}</span><span class="num hud-score">${top}</span>`;
    } else {
      hudLeader.innerHTML = `${leaders.slice(0, 3).map((team) => swatchSvg(team, 12)).join('')}<span class="hud-label">${t('viewer.tiedAt', { score: top })}</span>`;
    }
  }

  store.subscribe(['frame', 'replay'], (s) => {
    renderHud(s);
    dirty = true;
    if (hoverUnit !== null) tip.hidden = true;
  });
  store.subscribe(['focusTeam', 'selectedUnit'], () => { dirty = true; });
  store.subscribe(['follow'], (s) => {
    if (s.follow && s.selectedUnit !== null && !renderer.camera.zoomed) {
      const cam = renderer.camera;
      cam.zoomAt(cam.w / 2, cam.h / 2, FOLLOW_ZOOM);
      syncTools();
    }
    dirty = true;
  });
  store.subscribe(['immersive'], () => {
    requestAnimationFrame(() => { renderer.resize(); dirty = true; });
  });
  onLangChange(() => {
    renderHud(store.get());
    canvas.setAttribute('aria-label', t('viewer.boardLabel'));
  });
  canvas.setAttribute('aria-label', t('viewer.boardLabel'));
  renderHud(store.get());

  return {
    renderer,
    zoomBy,
    resetView: () => $('#zoom-fit').click(),
    markDirty: () => { dirty = true; },
    draw(now) {
      const s = store.get();
      const progress = playback.progress(now);
      const animating = s.playing || progress < 1;

      if (s.follow && s.selectedUnit !== null) {
        const pos = renderer.positions.get(s.selectedUnit);
        if (pos) {
          const [bx, by] = renderer.camera.toBoard(pos[0], pos[1]);
          renderer.camera.easeTo(bx, by, FOLLOW_EASE);
          dirty = true;
        }
      }

      const idleDue = !reduceMotion && now - lastDraw >= IDLE_FRAME_MS;
      if (!animating && !dirty && !idleDue) return;
      renderer.render({
        frame: s.frame,
        progress,
        now: reduceMotion ? 0 : now,
        focusTeam: s.focusTeam,
        selectedUnit: s.selectedUnit,
        hoverUnit,
      });
      lastDraw = now;
      dirty = false;
    },
  };
}

/** "Player5 #2" / "Player5 2号" */
export function unitLabel(replay, unit) {
  return t('unit.label', { team: teamName(replay.names[teamOfUnit(unit)]), n: unitSlot(unit) + 1 });
}
