// Static board layer: floor, bases, flag spots and walls. Drawn into a cache canvas and
// only redrawn when the camera or size changes. Also used by the lobby's map thumbnails.

import { teamColor, teamShape, traceShape, withAlpha } from '../core/teams.js';

/** Board colors from CSS tokens (tokens.css), read once per page. */
let cachedPalette = null;
export function boardPalette() {
  if (cachedPalette) return cachedPalette;
  const css = getComputedStyle(document.documentElement);
  const v = (name, fallback) => css.getPropertyValue(name).trim() || fallback;
  cachedPalette = {
    floor: v('--board-floor', '#151b3d'),
    floorAlt: v('--board-floor-alt', '#171e43'),
    grid: v('--board-grid', 'rgba(190,200,255,0.045)'),
    wall: v('--board-wall', '#2c3466'),
    wallTop: v('--board-wall-top', '#3e4884'),
    wallShade: v('--board-wall-shade', '#0a0d24'),
    flag: v('--flag', '#ffc24b'),
  };
  return cachedPalette;
}

/**
 * @param {CanvasRenderingContext2D} ctx  already scaled so 1 unit = 1 CSS px
 * @param {{ size:number, map:string[], bases:number[][][], flagSpots:number[][] }} board
 * @param {import('./camera.js').Camera} camera
 */
export function drawTerrain(ctx, board, camera, { detail = true } = {}) {
  const pal = boardPalette();
  const n = board.size;
  const cs = camera.cell;
  const [ox, oy] = camera.toScreen(0, 0);
  const [vx0, vy0] = camera.toBoard(0, 0);
  const [vx1, vy1] = camera.toBoard(camera.w, camera.h);
  const x0 = Math.max(0, Math.floor(vx0)), y0 = Math.max(0, Math.floor(vy0));
  const x1 = Math.min(n - 1, Math.ceil(vx1)), y1 = Math.min(n - 1, Math.ceil(vy1));
  const cellX = (x) => ox + x * cs;
  const cellY = (y) => oy + y * cs;

  // Floor with a faint checker so distance reads at a glance
  ctx.fillStyle = pal.floor;
  ctx.fillRect(ox, oy, n * cs, n * cs);
  ctx.fillStyle = pal.floorAlt;
  for (let y = y0; y <= y1; y++) {
    for (let x = x0 + ((x0 + y) % 2 ? 0 : 1); x <= x1; x += 2) {
      ctx.fillRect(cellX(x), cellY(y), cs + 0.5, cs + 0.5);
    }
  }

  if (detail && cs >= 9) {
    ctx.strokeStyle = pal.grid;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = x0; x <= x1 + 1; x++) {
      const sx = Math.round(cellX(x)) + 0.5;
      ctx.moveTo(sx, cellY(y0));
      ctx.lineTo(sx, cellY(y1 + 1));
    }
    for (let y = y0; y <= y1 + 1; y++) {
      const sy = Math.round(cellY(y)) + 0.5;
      ctx.moveTo(cellX(x0), sy);
      ctx.lineTo(cellX(x1 + 1), sy);
    }
    ctx.stroke();
  }

  board.bases.forEach((cells, team) => drawBase(ctx, cells, team, cs, cellX, cellY, detail));

  // Flag spots: where flags spawn and return to
  if (board.flagSpots) {
    ctx.strokeStyle = withAlpha(pal.flag, 0.32);
    ctx.lineWidth = Math.max(1, cs * 0.06);
    for (const [x, y] of board.flagSpots) {
      const cx = cellX(x) + cs / 2, cy = cellY(y) + cs / 2, r = cs * 0.34;
      ctx.beginPath();
      ctx.moveTo(cx, cy - r); ctx.lineTo(cx + r, cy); ctx.lineTo(cx, cy + r); ctx.lineTo(cx - r, cy);
      ctx.closePath();
      ctx.stroke();
    }
  }

  // Walls as raised blocks: drop shadow, body, lit top edge
  const map = board.map;
  const sh = Math.max(1, cs * 0.12);
  ctx.fillStyle = pal.wallShade;
  for (let y = y0; y <= y1; y++) {
    const row = map[y];
    for (let x = x0; x <= x1; x++) if (row[x] === '#') ctx.fillRect(cellX(x) + sh * 0.5, cellY(y) + sh, cs, cs);
  }
  ctx.fillStyle = pal.wall;
  for (let y = y0; y <= y1; y++) {
    const row = map[y];
    for (let x = x0; x <= x1; x++) if (row[x] === '#') ctx.fillRect(cellX(x), cellY(y), cs + 0.5, cs + 0.5);
  }
  if (detail && cs >= 5) {
    ctx.fillStyle = pal.wallTop;
    const lip = Math.max(1, cs * 0.22);
    for (let y = y0; y <= y1; y++) {
      const row = map[y];
      for (let x = x0; x <= x1; x++) {
        // Only light the top edge when the cell above is open, so wall runs read as one mass
        if (row[x] === '#' && (y === 0 || map[y - 1][x] !== '#')) ctx.fillRect(cellX(x), cellY(y), cs + 0.5, lip);
      }
    }
  }

  // Vignette pulls the eye toward the middle
  if (detail) {
    const cx = ox + (n * cs) / 2, cy = oy + (n * cs) / 2;
    const g = ctx.createRadialGradient(cx, cy, n * cs * 0.25, cx, cy, n * cs * 0.75);
    g.addColorStop(0, 'rgba(6,8,26,0)');
    g.addColorStop(1, 'rgba(6,8,26,0.35)');
    ctx.fillStyle = g;
    ctx.fillRect(ox, oy, n * cs, n * cs);
  }
}

function drawBase(ctx, cells, team, cs, cellX, cellY, detail) {
  const color = teamColor(team);
  const set = new Set(cells.map(([x, y]) => `${x},${y}`));

  ctx.save();
  ctx.beginPath();
  for (const [x, y] of cells) ctx.rect(cellX(x), cellY(y), cs + 0.5, cs + 0.5);
  ctx.fillStyle = withAlpha(color, 0.16);
  ctx.fill();

  if (detail && cs >= 6) {
    // Diagonal hatch inside the base
    ctx.clip();
    const xs = cells.map(([x]) => x), ys = cells.map(([, y]) => y);
    const bx0 = cellX(Math.min(...xs)), by0 = cellY(Math.min(...ys));
    const bx1 = cellX(Math.max(...xs) + 1), by1 = cellY(Math.max(...ys) + 1);
    const step = Math.max(4, cs * 0.4);
    ctx.strokeStyle = withAlpha(color, 0.14);
    ctx.lineWidth = Math.max(1, cs * 0.05);
    ctx.beginPath();
    for (let d = bx0 - (by1 - by0); d < bx1; d += step) {
      ctx.moveTo(d, by1);
      ctx.lineTo(d + (by1 - by0), by0);
    }
    ctx.stroke();
  }
  ctx.restore();

  // Outline only the outer edge of the base region
  ctx.strokeStyle = withAlpha(color, 0.75);
  ctx.lineWidth = Math.max(1, cs * 0.07);
  ctx.beginPath();
  for (const [x, y] of cells) {
    const sx = cellX(x), sy = cellY(y);
    if (!set.has(`${x},${y - 1}`)) { ctx.moveTo(sx, sy); ctx.lineTo(sx + cs, sy); }
    if (!set.has(`${x},${y + 1}`)) { ctx.moveTo(sx, sy + cs); ctx.lineTo(sx + cs, sy + cs); }
    if (!set.has(`${x - 1},${y}`)) { ctx.moveTo(sx, sy); ctx.lineTo(sx, sy + cs); }
    if (!set.has(`${x + 1},${y}`)) { ctx.moveTo(sx + cs, sy); ctx.lineTo(sx + cs, sy + cs); }
  }
  ctx.stroke();

  // Team emblem in the middle of the base
  if (cs >= 4) {
    const mx = cells.reduce((s, [x]) => s + x, 0) / cells.length;
    const my = cells.reduce((s, [, y]) => s + y, 0) / cells.length;
    traceShape(ctx, teamShape(team), cellX(mx) + cs / 2, cellY(my) + cs / 2, cs * 0.55);
    ctx.fillStyle = withAlpha(color, 0.22);
    ctx.fill();
  }
}
