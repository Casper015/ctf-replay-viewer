// Drawing primitives for everything that moves: unit tokens, flags and turn effects.
// All functions draw in CSS pixels on a context already scaled for devicePixelRatio.
// Sizes scale with the cell size `cs`; fine detail is dropped when cells get small.

import { shade, teamColor, teamShape, traceShape, withAlpha } from '../../core/teams.js';

const INK = 'rgba(6, 8, 28, 0.92)';
const GOLD = '#ffc24b';
const GOLD_DEEP = '#c98a12';
const KILL = '#ff7a87';
const HP_COLORS = [[0.67, '#4fd6a0'], [0.34, '#ffa25a'], [0, '#ff5a6e']];

const hpColor = (ratio) => HP_COLORS.find(([min]) => ratio >= min)[1];

/**
 * A unit token: shadow, shaded team shape, slot pips, facing notch, health ring, carried flag.
 * @param {object} o
 * @param {number} o.x, o.y   center in CSS px
 * @param {number} o.cs       cell size in CSS px
 * @param {number} o.team, o.slot (0..2), o.hp (0..1), o.facing (radians)
 * @param {boolean} o.carrying
 * @param {number} o.alpha    0..1 (focus dimming, spawn fade)
 * @param {number} o.scale    extra scale (spawn pop)
 * @param {number} o.now      ms clock for idle animation (0 = static)
 */
export function drawUnit(ctx, o) {
  const { x, y, cs, team, slot, hp, facing, carrying, now = 0 } = o;
  const r = cs * 0.38 * (o.scale ?? 1);
  if (r < 1) return;
  const color = teamColor(team);
  const shape = teamShape(team);
  const detail = cs >= 9;

  ctx.save();
  ctx.globalAlpha = o.alpha ?? 1;

  // Carrier aura: a soft gold glow that breathes
  if (carrying) {
    const pulse = now ? 0.75 + 0.25 * Math.sin(now / 260) : 0.9;
    const g = ctx.createRadialGradient(x, y, r * 0.4, x, y, r * 2.3);
    g.addColorStop(0, withAlpha(GOLD, 0.42 * pulse));
    g.addColorStop(1, withAlpha(GOLD, 0));
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r * 2.3, 0, Math.PI * 2);
    ctx.fill();
  }

  // Contact shadow
  if (detail) {
    ctx.fillStyle = 'rgba(2, 3, 16, 0.45)';
    ctx.beginPath();
    ctx.ellipse(x + r * 0.1, y + r * 0.72, r * 0.95, r * 0.34, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  // Facing notch sits behind the body so only its tip shows
  if (detail && Number.isFinite(facing)) {
    const tip = r * 1.5, base = r * 0.75, half = 0.42;
    ctx.fillStyle = shade(color, 0.25);
    ctx.beginPath();
    ctx.moveTo(x + Math.cos(facing) * tip, y + Math.sin(facing) * tip);
    ctx.lineTo(x + Math.cos(facing + half) * base, y + Math.sin(facing + half) * base);
    ctx.lineTo(x + Math.cos(facing - half) * base, y + Math.sin(facing - half) * base);
    ctx.closePath();
    ctx.fill();
  }

  // Body: lit from the top left, rim in ink so tokens separate from any floor color
  traceShape(ctx, shape, x, y, r);
  if (detail) {
    const g = ctx.createRadialGradient(x - r * 0.4, y - r * 0.5, r * 0.08, x, y, r * 1.3);
    g.addColorStop(0, shade(color, 0.6));
    g.addColorStop(0.45, color);
    g.addColorStop(1, shade(color, -0.42));
    ctx.fillStyle = g;
  } else {
    ctx.fillStyle = color;
  }
  ctx.fill();
  ctx.lineWidth = Math.max(1, r * 0.14);
  ctx.strokeStyle = INK;
  ctx.stroke();

  if (detail) {
    // Specular highlight
    ctx.fillStyle = 'rgba(255, 255, 255, 0.28)';
    ctx.beginPath();
    ctx.ellipse(x - r * 0.3, y - r * 0.42, r * 0.36, r * 0.18, -0.5, 0, Math.PI * 2);
    ctx.fill();
    drawPips(ctx, x, y + r * 0.08, r, slot);
  }

  // Health ring, only once damaged, so a healthy board stays calm
  if (hp < 0.999 && cs >= 6) {
    const rr = r * 1.32;
    const lw = Math.max(1.5, r * 0.18);
    ctx.lineCap = 'round';
    ctx.lineWidth = lw;
    ctx.strokeStyle = 'rgba(4, 6, 22, 0.75)';
    ctx.beginPath();
    ctx.arc(x, y, rr, 0, Math.PI * 2);
    ctx.stroke();
    ctx.strokeStyle = hpColor(hp);
    ctx.beginPath();
    ctx.arc(x, y, rr, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * Math.max(0.02, hp));
    ctx.stroke();
  }

  if (carrying) drawPennant(ctx, x + r * 0.55, y - r * 0.15, cs * 0.62, now, false);

  ctx.restore();
}

/** One, two or three dots telling the team's units apart. */
function drawPips(ctx, x, y, r, slot) {
  const d = r * 0.15;
  const gap = r * 0.36;
  const spots = [
    [[0, 0]],
    [[-gap / 2, 0], [gap / 2, 0]],
    [[-gap / 2, gap * 0.32], [gap / 2, gap * 0.32], [0, -gap * 0.55]],
  ][slot] || [[0, 0]];
  ctx.fillStyle = INK;
  for (const [dx, dy] of spots) {
    ctx.beginPath();
    ctx.arc(x + dx, y + dy, d, 0, Math.PI * 2);
    ctx.fill();
  }
}

/** A gold pennant on a pole. (px, py) is the bottom of the pole. */
function drawPennant(ctx, px, py, size, now, drooped, label) {
  const poleH = size;
  const top = py - poleH;
  ctx.lineCap = 'round';
  ctx.strokeStyle = '#f3ecd6';
  ctx.lineWidth = Math.max(1, size * 0.08);
  ctx.beginPath();
  ctx.moveTo(px, py);
  ctx.lineTo(px, top);
  ctx.stroke();

  const w = size * 0.78;
  const h = size * 0.48;
  const t = now / 180;
  ctx.beginPath();
  ctx.moveTo(px, top);
  if (drooped) {
    ctx.quadraticCurveTo(px + w * 0.35, top + h * 0.5, px + w * 0.25, top + h * 1.3);
    ctx.lineTo(px, top + h);
  } else {
    const wave = (k) => (now ? Math.sin(t + k * 2.4) * h * 0.14 : 0);
    ctx.bezierCurveTo(px + w * 0.33, top + wave(0.3), px + w * 0.66, top + wave(0.6), px + w, top + h * 0.5 + wave(1));
    ctx.bezierCurveTo(px + w * 0.66, top + h + wave(0.6), px + w * 0.33, top + h + wave(0.3), px, top + h);
  }
  ctx.closePath();
  ctx.fillStyle = GOLD;
  ctx.fill();
  ctx.lineWidth = Math.max(0.75, size * 0.05);
  ctx.strokeStyle = GOLD_DEEP;
  ctx.stroke();

  if (label !== undefined && size >= 16) {
    ctx.fillStyle = '#2b1f00';
    ctx.font = `800 ${Math.round(h * 0.7)}px Archivo, system-ui, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(label), px + w * 0.4, top + h * 0.52);
  }
}

/**
 * A flag on the ground (at home or dropped).
 * @param {number} returnRatio  for dropped flags: share of the return timer left (1 → 0)
 */
export function drawGroundFlag(ctx, { x, y, cs, id, dropped, returnRatio, now, alpha = 1 }) {
  ctx.save();
  ctx.globalAlpha = alpha;
  const size = cs * 0.78;
  // Base disc
  ctx.fillStyle = 'rgba(2, 3, 16, 0.4)';
  ctx.beginPath();
  ctx.ellipse(x, y + cs * 0.3, cs * 0.3, cs * 0.11, 0, 0, Math.PI * 2);
  ctx.fill();

  if (dropped && returnRatio !== undefined && cs >= 8) {
    // Countdown ring until the flag returns to its spot
    ctx.lineWidth = Math.max(1.25, cs * 0.07);
    ctx.strokeStyle = withAlpha(GOLD, 0.2);
    ctx.beginPath();
    ctx.arc(x, y, cs * 0.46, 0, Math.PI * 2);
    ctx.stroke();
    ctx.strokeStyle = GOLD;
    ctx.beginPath();
    ctx.arc(x, y, cs * 0.46, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * Math.max(0, returnRatio));
    ctx.stroke();
  }
  drawPennant(ctx, x - cs * 0.14, y + cs * 0.3, size, dropped ? 0 : now, dropped, id);
  ctx.restore();
}

/** A unit that died this turn: fades and lifts away, leaving a mark. p = turn progress 0..1. */
export function drawDeath(ctx, { x, y, cs, team, slot, p, alpha = 1 }) {
  ctx.save();
  if (p < 1) {
    drawUnit(ctx, { x, y: y - cs * 0.2 * p, cs, team, slot, hp: 0.01, facing: NaN, carrying: false, alpha: alpha * (1 - p) * 0.85, scale: 1 + 0.25 * p });
  }
  // Cross mark stays for the rest of the turn so a paused frame still shows the kill
  const r = cs * 0.24;
  ctx.globalAlpha = alpha * (0.35 + 0.55 * Math.min(1, p * 1.5));
  ctx.strokeStyle = KILL;
  ctx.lineWidth = Math.max(1.5, cs * 0.1);
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(x - r, y - r); ctx.lineTo(x + r, y + r);
  ctx.moveTo(x + r, y - r); ctx.lineTo(x - r, y + r);
  ctx.stroke();
  ctx.restore();
}

/** Ring that closes in on a unit as it respawns at base. */
export function drawRespawn(ctx, { x, y, cs, team, p, alpha = 1 }) {
  if (p >= 1) return;
  ctx.save();
  ctx.globalAlpha = alpha * (1 - p);
  ctx.strokeStyle = teamColor(team);
  ctx.lineWidth = Math.max(1, cs * 0.08);
  ctx.beginPath();
  ctx.arc(x, y, cs * (1.2 - 0.7 * p), 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

/** Attack: a beam from attacker to target with a bolt travelling along it. */
export function drawBeam(ctx, { x1, y1, x2, y2, cs, team, now, alpha = 1 }) {
  const color = teamColor(team);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.lineCap = 'round';
  // Glow
  ctx.strokeStyle = withAlpha(color, 0.22);
  ctx.lineWidth = Math.max(3, cs * 0.28);
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
  // Core
  const g = ctx.createLinearGradient(x1, y1, x2, y2);
  g.addColorStop(0, withAlpha(color, 0.9));
  g.addColorStop(1, '#ffffff');
  ctx.strokeStyle = g;
  ctx.lineWidth = Math.max(1, cs * 0.07);
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
  // Bolt
  if (now) {
    const k = (now / 420) % 1;
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(x1 + (x2 - x1) * k, y1 + (y2 - y1) * k, Math.max(1.2, cs * 0.08), 0, Math.PI * 2);
    ctx.fill();
  }
  // Impact spark
  const s = Math.max(2, cs * 0.18);
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = Math.max(1, cs * 0.05);
  ctx.beginPath();
  for (let a = 0; a < 4; a++) {
    const ang = Math.PI / 4 + (a * Math.PI) / 2;
    ctx.moveTo(x2 + Math.cos(ang) * s * 0.35, y2 + Math.sin(ang) * s * 0.35);
    ctx.lineTo(x2 + Math.cos(ang) * s, y2 + Math.sin(ang) * s);
  }
  ctx.stroke();
  ctx.restore();
}

/** Capture: gold shockwave and a rising "+1" in the scoring team's color. */
export function drawCapture(ctx, { x, y, cs, team, p }) {
  ctx.save();
  const ring = cs * (0.6 + 2.4 * p);
  ctx.globalAlpha = p < 1 ? 1 - p : 0.45;
  ctx.strokeStyle = GOLD;
  ctx.lineWidth = Math.max(1.5, cs * 0.12 * (1 - p * 0.6));
  ctx.beginPath();
  ctx.arc(x, y, p < 1 ? ring : cs * 0.75, 0, Math.PI * 2);
  ctx.stroke();

  const fs = Math.max(11, Math.round(cs * 0.7));
  ctx.globalAlpha = p < 1 ? Math.min(1, 1.6 - p) : 0.9;
  ctx.font = `800 ${fs}px Archivo, system-ui, sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'bottom';
  const ty = y - cs * (0.55 + 0.6 * p);
  ctx.lineWidth = Math.max(2, fs * 0.22);
  ctx.strokeStyle = INK;
  ctx.strokeText('+1', x, ty);
  ctx.fillStyle = teamColor(team);
  ctx.fillText('+1', x, ty);
  ctx.restore();
}

/** Gold trail behind a flag carrier. points: [[x, y], ...] oldest first. */
export function drawTrail(ctx, points, cs, alpha = 1) {
  if (points.length < 2) return;
  ctx.save();
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  for (let k = 1; k < points.length; k++) {
    const t = k / (points.length - 1);
    ctx.globalAlpha = alpha * t * 0.55;
    ctx.strokeStyle = GOLD;
    ctx.lineWidth = Math.max(1, cs * 0.16 * t);
    ctx.beginPath();
    ctx.moveTo(points[k - 1][0], points[k - 1][1]);
    ctx.lineTo(points[k][0], points[k][1]);
    ctx.stroke();
  }
  ctx.restore();
}

/** Selection marker: rotating dashed ring. */
export function drawSelection(ctx, { x, y, cs, now, hover = false }) {
  ctx.save();
  ctx.strokeStyle = hover ? 'rgba(255,255,255,0.55)' : '#ffffff';
  ctx.lineWidth = Math.max(1.25, cs * 0.06);
  const r = cs * 0.72;
  if (!hover) {
    ctx.setLineDash([r * 0.5, r * 0.32]);
    ctx.lineDashOffset = now ? -now / 40 : 0;
  }
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}
