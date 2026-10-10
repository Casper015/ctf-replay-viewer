// Board renderer: draws one replay frame onto a canvas at native device resolution.
// Units tween from the previous frame into the current one using `progress` (0..1),
// so playback looks continuous even though the game moves in whole turns.
//
// Used by the viewer (interactive) and by the lobby hero (ambient, no input).

import { Camera } from './camera.js';
import { drawTerrain } from './terrain.js';
import {
  drawBeam, drawCapture, drawDeath, drawGroundFlag, drawRespawn, drawSelection, drawTrail, drawUnit,
} from './sprites.js';
import { teamOfUnit, unitSlot } from '../core/teams.js';

const TRAIL_FRAMES = 7;
const smooth = (t) => t * t * (3 - 2 * t);

export class BoardRenderer {
  /** @param {HTMLCanvasElement} canvas */
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.camera = new Camera();
    this.terrain = document.createElement('canvas');
    this.terrainKey = '';
    this.dpr = 1;
    this.replay = null;
    this.derived = null;
    this.positions = new Map(); // unit id -> [x, y] in CSS px, from the last render (hit testing)
  }

  setMatch(replay, derived) {
    this.replay = replay;
    this.derived = derived;
    this.board = {
      size: replay.header.size,
      map: replay.header.map,
      bases: replay.header.bases,
      flagSpots: replay.header.flag_spots,
    };
    this.camera.setBoard(replay.header.size);
    this.terrainKey = '';
  }

  /** Match the canvas backing store to its CSS size × devicePixelRatio. */
  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 3);
    const w = Math.max(1, Math.round(rect.width * dpr));
    const h = Math.max(1, Math.round(rect.height * dpr));
    if (this.canvas.width !== w || this.canvas.height !== h || this.dpr !== dpr) {
      this.canvas.width = w;
      this.canvas.height = h;
      this.terrain.width = w;
      this.terrain.height = h;
      this.dpr = dpr;
      this.terrainKey = '';
    }
    this.camera.setViewport(rect.width, rect.height);
  }

  boardPoint(x, y) {
    // Cell (x, y) -> screen center of that cell
    return this.camera.toScreen(x + 0.5, y + 0.5);
  }

  /** Unit id under a screen point (CSS px), or null. */
  unitAt(sx, sy) {
    const reach = Math.max(14, this.camera.cell * 0.6);
    let best = null;
    let bestD = reach * reach;
    for (const [id, [x, y]] of this.positions) {
      const d = (x - sx) ** 2 + (y - sy) ** 2;
      if (d < bestD) { best = id; bestD = d; }
    }
    return best;
  }

  /** Screen position of a unit at a frame, for follow mode and popovers. */
  unitBoardPos(unit, frame) {
    const u = this.replay.frames[frame]?.units[unit];
    return u && u.pos ? [u.pos[0] + 0.5, u.pos[1] + 0.5] : null;
  }

  /**
   * @param {object} v
   * @param {number} v.frame
   * @param {number} v.progress     0..1 tween into `frame`
   * @param {number} v.now          ms clock for idle animation; 0 disables it
   * @param {number} [v.focusTeam]  -1 for none
   * @param {number|null} [v.selectedUnit]
   * @param {number|null} [v.hoverUnit]
   */
  render(v) {
    if (!this.replay) return;
    const { ctx, camera, dpr } = this;
    const frames = this.replay.frames;
    const k = Math.max(0, Math.min(frames.length - 1, v.frame));
    const cur = frames[k];
    const prev = k > 0 ? frames[k - 1] : cur;
    const p = v.progress ?? 1;
    const e = smooth(p);
    const now = v.now || 0;
    const focus = v.focusTeam ?? -1;
    const cs = camera.cell;
    const dim = (team) => (focus < 0 || focus === team ? 1 : 0.22);

    // Static layer (cached until the camera or size changes)
    const key = camera.key() + '|' + dpr;
    if (key !== this.terrainKey) {
      const tctx = this.terrain.getContext('2d');
      tctx.setTransform(1, 0, 0, 1, 0, 0);
      tctx.clearRect(0, 0, this.terrain.width, this.terrain.height);
      tctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      drawTerrain(tctx, this.board, camera);
      this.terrainKey = key;
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.drawImage(this.terrain, 0, 0);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Where every unit is right now (tweened), plus who died / respawned this turn
    const positions = new Map();
    const deaths = new Map();
    for (const ev of cur.events) if (ev.type === 'death') deaths.set(ev.unit, ev);
    const units = [];
    for (let id = 0; id < cur.units.length; id++) {
      const u = cur.units[id];
      const was = prev.units[id];
      const team = teamOfUnit(id);
      if (u.pos) {
        let bx = u.pos[0], by = u.pos[1];
        const spawned = !was.pos && k > 0;
        if (was.pos && !spawned && Math.abs(was.pos[0] - u.pos[0]) + Math.abs(was.pos[1] - u.pos[1]) <= 2) {
          bx = was.pos[0] + (u.pos[0] - was.pos[0]) * e;
          by = was.pos[1] + (u.pos[1] - was.pos[1]) * e;
        }
        const [sx, sy] = this.boardPoint(bx, by);
        positions.set(id, [sx, sy]);
        units.push({ id, u, team, sx, sy, spawned });
      } else if (was.pos && deaths.has(id)) {
        const at = deaths.get(id).pos || was.pos;
        const [sx, sy] = this.boardPoint(at[0], at[1]);
        positions.set(id, [sx, sy]);
      }
    }
    this.positions = new Map([...positions].filter(([id]) => cur.units[id].pos));

    // Flags on the ground
    const flagReturn = this.replay.header.rules.flag_return || 15;
    for (const fl of cur.flags) {
      if (!fl.pos) continue;
      const [sx, sy] = this.boardPoint(fl.pos[0], fl.pos[1]);
      const dropped = fl.status === 'dropped';
      drawGroundFlag(ctx, {
        x: sx, y: sy, cs, id: fl.id, dropped, now,
        returnRatio: dropped && fl.return_at != null ? (fl.return_at - cur.turn) / flagReturn : undefined,
      });
    }

    // Carrier trails
    for (const { id, u, team } of units) {
      if (u.flag === null || u.flag === undefined) continue;
      const pts = [];
      for (let j = Math.max(0, k - TRAIL_FRAMES); j < k; j++) {
        const pu = frames[j].units[id];
        if (pu.pos && pu.flag !== null && pu.flag !== undefined) pts.push(this.boardPoint(pu.pos[0], pu.pos[1]));
        else pts.length = 0;
      }
      pts.push(positions.get(id));
      drawTrail(ctx, pts, cs, dim(team));
    }

    // Attacks this turn
    for (const ev of cur.events) {
      if (ev.type !== 'attack') continue;
      const a = positions.get(ev.unit);
      const b = positions.get(ev.target);
      if (!a || !b) continue;
      const team = teamOfUnit(ev.unit);
      drawBeam(ctx, { x1: a[0], y1: a[1], x2: b[0], y2: b[1], cs, team, now, alpha: dim(team) * (focus < 0 ? 0.85 : 1) });
    }

    // Deaths this turn
    for (const [id, ev] of deaths) {
      const pos = positions.get(id);
      if (!pos) continue;
      const team = teamOfUnit(id);
      drawDeath(ctx, { x: pos[0], y: pos[1], cs, team, slot: unitSlot(id), p, alpha: dim(team) });
    }

    // Units, back to front
    units.sort((a, b) => a.sy - b.sy);
    const hpMax = this.replay.header.rules.hp || 100;
    const facing = this.derived?.facing[k];
    for (const { id, u, team, sx, sy, spawned } of units) {
      const a = dim(team);
      if (spawned) drawRespawn(ctx, { x: sx, y: sy, cs, team, p, alpha: a });
      drawUnit(ctx, {
        x: sx, y: sy, cs, team,
        slot: unitSlot(id),
        hp: u.hp / hpMax,
        facing: facing ? facing[id] : NaN,
        carrying: u.flag !== null && u.flag !== undefined,
        alpha: spawned ? a * Math.min(1, p * 1.4) : a,
        scale: spawned ? 0.6 + 0.4 * e : 1,
        now,
      });
    }

    // Captures this turn
    for (const ev of cur.events) {
      if (ev.type !== 'capture') continue;
      const pos = positions.get(ev.unit) || (cur.units[ev.unit].pos && this.boardPoint(...cur.units[ev.unit].pos));
      if (pos) drawCapture(ctx, { x: pos[0], y: pos[1], cs, team: ev.team, p });
    }

    if (v.hoverUnit != null && v.hoverUnit !== v.selectedUnit && positions.has(v.hoverUnit)) {
      const [x, y] = positions.get(v.hoverUnit);
      drawSelection(ctx, { x, y, cs, now, hover: true });
    }
    if (v.selectedUnit != null && positions.has(v.selectedUnit)) {
      const [x, y] = positions.get(v.selectedUnit);
      drawSelection(ctx, { x, y, cs, now });
    }
  }
}
