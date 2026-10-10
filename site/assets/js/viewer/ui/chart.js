// Score race chart. Two views of the same data:
//   lines: score (y) over turns (x), step lines per team
//   orbit: turns run clockwise around a dial, score is distance from the center
// Played turns are solid, the rest of the match is drawn faintly. Tap or drag to seek.

import { $, escapeHtml, h } from '../../core/dom.js';
import { icon } from '../../core/icons.js';
import { onLangChange, t } from '../../core/i18n.js';
import { swatchSvg, teamColor, teamName, withAlpha } from '../../core/teams.js';

const PAD = { l: 30, r: 12, t: 12, b: 24 };
const INK_TEXT = '#8188b6';
const GRID = 'rgba(160, 170, 255, 0.10)';

export function mountChart(store, { playback }) {
  const pane = $('#pane-chart');
  const modeBar = h('div', { class: 'segmented segmented--sm', role: 'group' });
  const canvas = h('canvas', { class: 'chart-canvas' });
  const tip = h('div', { class: 'chart-tip', hidden: true });
  const box = h('div', { class: 'chart-box' }, canvas, tip);
  const legend = h('div', { class: 'chart-legend' });
  const caption = h('p', { class: 'pane-hint' });
  pane.replaceChildren(h('div', { class: 'pane-head' }, modeBar), box, legend, caption);

  const modes = [['lines', 'chart'], ['orbit', 'orbit']].map(([mode, ic]) => {
    const b = h('button', { type: 'button', dataset: { mode } });
    b.addEventListener('click', () => store.set({ chartMode: mode }));
    b.innerHTML = `${icon(ic, 'icon icon--sm')}<span data-i18n="chart.${mode}"></span>`;
    return b;
  });
  modeBar.append(...modes);

  legend.addEventListener('click', (e) => {
    const b = e.target.closest('[data-team]');
    if (!b) return;
    const team = Number(b.dataset.team);
    store.set({ focusTeam: store.get().focusTeam === team ? -1 : team });
  });

  // Score change points per team: [[frame, score], ...]
  const { replay, derived } = store.get();
  const last = replay.frames.length - 1;
  const steps = replay.names.map(() => [[0, 0]]);
  for (const c of derived.captures) steps[c.team].push([c.frame, derived.stats[c.frame][c.team].score]);
  const maxScore = Math.max(3, derived.maxScore);

  const ctx = canvas.getContext('2d');
  let W = 0, H = 0, dpr = 1;
  new ResizeObserver(() => {
    const r = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 3);
    W = r.width;
    H = r.height;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    draw(store.get());
  }).observe(box);

  // Geometry helpers for both modes
  const lineX = (frame) => PAD.l + (frame / last) * (W - PAD.l - PAD.r);
  const lineY = (score) => PAD.t + (1 - score / maxScore) * (H - PAD.t - PAD.b);
  const orbit = () => {
    const R = Math.min(W, H) / 2 - 18;
    return { cx: W / 2, cy: H / 2, R, r0: Math.max(10, R * 0.16) };
  };
  const orbitPoint = (frame, score) => {
    const { cx, cy, R, r0 } = orbit();
    const a = -Math.PI / 2 + (frame / last) * Math.PI * 2;
    const r = r0 + (score / maxScore) * (R - r0);
    return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
  };
  const scoreTicks = () => {
    const step = maxScore <= 8 ? 2 : maxScore <= 20 ? 5 : 10;
    const out = [];
    for (let v = 0; v <= maxScore; v += step) out.push(v);
    return out;
  };
  const turnTicks = () => {
    const turns = replay.frames[last].turn;
    const step = turns > 250 ? 100 : 50;
    const out = [];
    for (let v = 0; v <= turns; v += step) out.push(v);
    return out;
  };
  const frameOfTurn = (turn) => Math.round((turn / replay.frames[last].turn) * last);

  function tracePath(team, upto, mode) {
    const pts = steps[team];
    const point = mode === 'lines' ? (f, s) => [lineX(f), lineY(s)] : orbitPoint;
    ctx.beginPath();
    let [px, py] = point(0, 0);
    ctx.moveTo(px, py);
    let score = 0;
    const stepTo = (frame) => {
      if (mode === 'lines') {
        [px, py] = point(frame, score);
        ctx.lineTo(px, py);
      } else {
        // Arc along the ring of constant score
        const from = (frame0 / last), to = (frame / last);
        const n = Math.max(1, Math.ceil((to - from) * 120));
        for (let k = 1; k <= n; k++) {
          [px, py] = point(frame0 + ((frame - frame0) * k) / n, score);
          ctx.lineTo(px, py);
        }
      }
    };
    let frame0 = 0;
    for (let k = 1; k < pts.length; k++) {
      const [f, s] = pts[k];
      if (f > upto) break;
      stepTo(f);
      score = s;
      [px, py] = point(f, score);
      ctx.lineTo(px, py);
      frame0 = f;
    }
    stepTo(upto);
  }

  function draw(s) {
    if (pane.hidden || !W) return;
    const mode = s.chartMode;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    ctx.font = '600 10px Archivo, system-ui, sans-serif';
    ctx.fillStyle = INK_TEXT;
    ctx.strokeStyle = GRID;
    ctx.lineWidth = 1;

    if (mode === 'lines') {
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      for (const v of scoreTicks()) {
        const y = Math.round(lineY(v)) + 0.5;
        ctx.beginPath(); ctx.moveTo(PAD.l, y); ctx.lineTo(W - PAD.r, y); ctx.stroke();
        ctx.fillText(String(v), PAD.l - 8, y);
      }
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      for (const v of turnTicks()) ctx.fillText(String(v), lineX(frameOfTurn(v)), H - PAD.b + 8);
    } else {
      const { cx, cy, R, r0 } = orbit();
      for (const v of scoreTicks()) {
        ctx.beginPath();
        ctx.arc(cx, cy, r0 + (v / maxScore) * (R - r0), 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      for (const v of turnTicks()) {
        if (v === replay.frames[last].turn) continue;
        const a = -Math.PI / 2 + (frameOfTurn(v) / last) * Math.PI * 2;
        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0);
        ctx.lineTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R);
        ctx.stroke();
        ctx.fillText(String(v), cx + Math.cos(a) * (R + 10), cy + Math.sin(a) * (R + 10));
      }
    }

    // Teams: unfocused first so the focused team draws on top
    const order = replay.names.map((_, team) => team)
      .sort((a, b) => (a === s.focusTeam) - (b === s.focusTeam) || derived.stats[s.frame][a].score - derived.stats[s.frame][b].score);
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    for (const team of order) {
      const color = teamColor(team);
      const on = s.focusTeam < 0 || s.focusTeam === team;
      ctx.strokeStyle = withAlpha(color, on ? 0.22 : 0.08);
      ctx.lineWidth = 1.25;
      tracePath(team, last, mode);
      ctx.stroke();
      ctx.strokeStyle = on ? color : withAlpha(color, 0.18);
      ctx.lineWidth = s.focusTeam === team ? 3 : 2;
      tracePath(team, s.frame, mode);
      ctx.stroke();
    }

    // Capture dots that have happened
    for (const c of derived.captures) {
      if (c.frame > s.frame) break;
      const on = s.focusTeam < 0 || s.focusTeam === c.team;
      if (!on) continue;
      const sc = derived.stats[c.frame][c.team].score;
      const [x, y] = mode === 'lines' ? [lineX(c.frame), lineY(sc)] : orbitPoint(c.frame, sc);
      ctx.fillStyle = teamColor(c.team);
      ctx.beginPath();
      ctx.arc(x, y, 2.4, 0, Math.PI * 2);
      ctx.fill();
    }

    // Playhead (neutral: time isn't a team or a flag)
    ctx.strokeStyle = 'rgba(238, 240, 255, 0.7)';
    ctx.lineWidth = 1.25;
    ctx.beginPath();
    if (mode === 'lines') {
      const x = Math.round(lineX(s.frame)) + 0.5;
      ctx.moveTo(x, PAD.t - 4);
      ctx.lineTo(x, H - PAD.b);
    } else {
      const { cx, cy, R } = orbit();
      const a = -Math.PI / 2 + (s.frame / last) * Math.PI * 2;
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + Math.cos(a) * (R + 4), cy + Math.sin(a) * (R + 4));
    }
    ctx.stroke();

    // Current score markers
    for (const team of order) {
      const on = s.focusTeam < 0 || s.focusTeam === team;
      const sc = derived.stats[s.frame][team].score;
      const [x, y] = mode === 'lines' ? [lineX(s.frame), lineY(sc)] : orbitPoint(s.frame, sc);
      ctx.fillStyle = on ? teamColor(team) : withAlpha(teamColor(team), 0.25);
      ctx.strokeStyle = '#0c1029';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, s.focusTeam === team ? 5 : 3.6, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }
  }

  function renderLegend(s) {
    const ranking = derived.ranking(s.frame);
    legend.innerHTML = ranking.map((r) => `
      <button type="button" class="legend-item${s.focusTeam >= 0 && s.focusTeam !== r.team ? ' is-dim' : ''}" data-team="${r.team}" aria-pressed="${s.focusTeam === r.team}">
        ${swatchSvg(r.team, 12)}<span>${escapeHtml(teamName(replay.names[r.team]))}</span><b class="num">${r.score}</b>
      </button>`).join('');
  }

  function renderChrome(s) {
    modes.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === s.chartMode)));
    modeBar.setAttribute('aria-label', t('chart.modeLabel'));
    caption.textContent = t(s.chartMode === 'lines' ? 'chart.captionLines' : 'chart.captionOrbit');
    canvas.setAttribute('aria-label', t('chart.label'));
    canvas.setAttribute('role', 'img');
  }

  // Pointer: seek on press/drag, tooltip on hover
  const frameAt = (e) => {
    const r = canvas.getBoundingClientRect();
    const x = e.clientX - r.left, y = e.clientY - r.top;
    if (store.get().chartMode === 'lines') {
      return Math.round(Math.min(1, Math.max(0, (x - PAD.l) / (W - PAD.l - PAD.r))) * last);
    }
    const { cx, cy } = orbit();
    let a = Math.atan2(y - cy, x - cx) + Math.PI / 2;
    if (a < 0) a += Math.PI * 2;
    return Math.round((a / (Math.PI * 2)) * last);
  };
  let dragging = false;
  canvas.addEventListener('pointerdown', (e) => {
    dragging = true;
    canvas.setPointerCapture?.(e.pointerId);
    playback.seek(frameAt(e));
  });
  canvas.addEventListener('pointermove', (e) => {
    const frame = frameAt(e);
    if (dragging) playback.seek(frame);
    if (e.pointerType !== 'mouse') return;
    const f = replay.frames[frame];
    const top = derived.ranking(frame).slice(0, 3);
    tip.innerHTML = `<b>${t('viewer.turnShort')} ${f.turn}</b>${top.map((r) => `<span>${swatchSvg(r.team, 10)}${escapeHtml(teamName(replay.names[r.team]))} <b class="num">${r.score}</b></span>`).join('')}`;
    tip.hidden = false;
    const r = canvas.getBoundingClientRect();
    const x = e.clientX - r.left;
    tip.style.left = `${Math.min(W - tip.offsetWidth - 4, Math.max(4, x + 12))}px`;
    tip.style.top = `${Math.max(4, e.clientY - r.top - tip.offsetHeight - 8)}px`;
  });
  const stop = () => { dragging = false; };
  canvas.addEventListener('pointerup', stop);
  canvas.addEventListener('pointercancel', stop);
  canvas.addEventListener('pointerleave', () => { tip.hidden = true; });

  store.subscribe(['frame', 'focusTeam', 'chartMode', 'tab'], (s, changed) => {
    if (changed.includes('chartMode')) renderChrome(s);
    if (s.tab !== 'chart') return;
    draw(s);
    renderLegend(s);
  });
  onLangChange(() => {
    renderChrome(store.get());
    renderLegend(store.get());
  });
  renderChrome(store.get());
  renderLegend(store.get());
}
