// Team identity: every team gets a color AND a shape, so 15-team matches stay readable
// (and colorblind viewers can tell teams apart by shape). Gold is intentionally absent:
// gold is reserved for flags and scores.

import { getLang } from './i18n.js';

export const TEAM_COLORS = [
  '#ff5a6e', // coral
  '#4c9bff', // azure
  '#3ddc84', // green
  '#b98cff', // lavender
  '#ff8f40', // orange
  '#22d3ee', // cyan
  '#f06ad0', // magenta
  '#b4e04a', // lime
  '#7c83ff', // indigo
  '#e4e7ee', // pearl
  '#ff9aa8', // blush
  '#25b39e', // teal
  '#9db4d4', // steel
  '#d4a373', // tan
  '#a3a86a', // olive
];

export const TEAM_SHAPES = ['circle', 'diamond', 'hexagon', 'square', 'pentagon'];

export const teamColor = (team) => TEAM_COLORS[team % TEAM_COLORS.length];
export const teamShape = (team) => TEAM_SHAPES[team % TEAM_SHAPES.length];
export const teamOfUnit = (unitId) => Math.floor(unitId / 3);
export const unitSlot = (unitId) => unitId % 3;

// Team names come from the engine. Only non-English names need an English display form.
export const EN_NAMES = { '基准': 'Baseline' };
export function teamName(raw) {
  if (getLang() === 'en' && EN_NAMES[raw]) return EN_NAMES[raw];
  return raw;
}

/** Vertices for a shape of "radius" r centered at 0,0 (circle returns null). */
function vertices(shape, r) {
  const poly = (n, rot, scale) =>
    Array.from({ length: n }, (_, k) => {
      const a = rot + (k * 2 * Math.PI) / n;
      return [Math.cos(a) * r * scale, Math.sin(a) * r * scale];
    });
  switch (shape) {
    case 'diamond': return poly(4, -Math.PI / 2, 1.2);
    case 'hexagon': return poly(6, 0, 1.06);
    case 'square': return poly(4, -Math.PI / 4, 1.2);
    case 'pentagon': return poly(5, -Math.PI / 2, 1.1);
    default: return null;
  }
}

/** Trace a team shape on a canvas path (caller fills/strokes). */
export function traceShape(ctx, shape, cx, cy, r) {
  ctx.beginPath();
  const pts = vertices(shape, r);
  if (!pts) {
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    return;
  }
  // Slightly rounded corners read as "game piece" rather than "icon"
  const round = r * 0.18;
  const n = pts.length;
  for (let k = 0; k < n; k++) {
    const [x0, y0] = pts[(k - 1 + n) % n];
    const [x1, y1] = pts[k];
    const [x2, y2] = pts[(k + 1) % n];
    const mx0 = (x0 + x1) / 2, my0 = (y0 + y1) / 2;
    const mx1 = (x1 + x2) / 2, my1 = (y1 + y2) / 2;
    if (k === 0) ctx.moveTo(cx + mx0, cy + my0);
    ctx.arcTo(cx + x1, cy + y1, cx + mx1, cy + my1, round);
  }
  ctx.closePath();
}

/** Inline SVG swatch for DOM lists (standings, legends, menus). */
export function swatchSvg(team, size = 14) {
  const r = size * 0.36;
  const c = size / 2;
  const color = teamColor(team);
  const pts = vertices(teamShape(team), r);
  const body = pts
    ? `<polygon points="${pts.map(([x, y]) => `${(c + x).toFixed(2)},${(c + y).toFixed(2)}`).join(' ')}" fill="${color}" stroke="${color}" stroke-width="${(size * 0.08).toFixed(2)}" stroke-linejoin="round"/>`
    : `<circle cx="${c}" cy="${c}" r="${r * 1.05}" fill="${color}"/>`;
  return `<svg class="swatch" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" aria-hidden="true">${body}</svg>`;
}

/** Mix a hex color toward white (amt > 0) or black (amt < 0). */
export function shade(hex, amt) {
  const n = parseInt(hex.slice(1), 16);
  let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
  const target = amt > 0 ? 255 : 0;
  const k = Math.abs(amt);
  r = Math.round(r + (target - r) * k);
  g = Math.round(g + (target - g) * k);
  b = Math.round(b + (target - b) * k);
  return `rgb(${r},${g},${b})`;
}

export function withAlpha(hex, alpha) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${alpha})`;
}
