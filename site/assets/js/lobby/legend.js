// "How to read the board": each entry is drawn with the same sprite code as the board,
// so the legend always matches what viewers see.

import { $, escapeHtml, h } from '../core/dom.js';
import { onLangChange, t } from '../core/i18n.js';
import { Camera } from '../board/camera.js';
import { drawTerrain } from '../board/terrain.js';
import { drawBeam, drawGroundFlag, drawTrail, drawUnit } from '../board/sprites.js';

const W = 76;
const H = 60;
const CS = 22; // cell size used for the samples

const ENTRIES = [
  {
    key: 'units',
    draw(ctx) {
      drawUnit(ctx, { x: 22, y: 30, cs: 28, team: 1, slot: 0, hp: 1, facing: 0, carrying: false });
      drawUnit(ctx, { x: 54, y: 30, cs: 28, team: 3, slot: 2, hp: 1, facing: Math.PI, carrying: false });
    },
  },
  {
    key: 'carrier',
    draw(ctx) {
      drawTrail(ctx, [[8, 46], [20, 44], [32, 40], [44, 36]], CS);
      drawUnit(ctx, { x: 46, y: 36, cs: CS, team: 2, slot: 1, hp: 1, facing: -0.3, carrying: true });
    },
  },
  {
    key: 'flags',
    draw(ctx) {
      drawGroundFlag(ctx, { x: 22, y: 30, cs: CS, id: 0, dropped: false, now: 0 });
      drawGroundFlag(ctx, { x: 54, y: 30, cs: CS, id: 1, dropped: true, returnRatio: 0.6, now: 0 });
    },
  },
  {
    key: 'attack',
    draw(ctx) {
      drawBeam(ctx, { x1: 18, y1: 36, x2: 56, y2: 26, cs: CS, team: 0, now: 0 });
      drawUnit(ctx, { x: 18, y: 36, cs: CS, team: 0, slot: 0, hp: 1, facing: -0.26, carrying: false });
      drawUnit(ctx, { x: 58, y: 26, cs: CS, team: 4, slot: 1, hp: 0.66, facing: Math.PI, carrying: false });
    },
  },
  {
    key: 'health',
    draw(ctx) {
      drawUnit(ctx, { x: 22, y: 30, cs: 28, team: 5, slot: 0, hp: 0.66, facing: 0, carrying: false });
      drawUnit(ctx, { x: 54, y: 30, cs: 28, team: 5, slot: 1, hp: 0.32, facing: 0, carrying: false });
    },
  },
  {
    key: 'bases',
    draw(ctx) {
      const cam = new Camera();
      cam.setBoard(5);
      cam.setViewport(W, H);
      const base = [];
      for (let y = 1; y <= 3; y++) for (let x = 1; x <= 3; x++) base.push([x, y]);
      drawTerrain(ctx, { size: 5, map: ['.....', '.....', '.....', '.....', '....#'], bases: [[], [], [], [], [], [], [], base], flagSpots: [] }, cam);
    },
  },
];

export function mountLegend() {
  const list = $('#legend');
  const canvases = ENTRIES.map((entry) => {
    const canvas = h('canvas', { 'aria-hidden': 'true' });
    const dpr = Math.min(window.devicePixelRatio || 1, 3);
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    entry.draw(ctx);
    return canvas;
  });

  function render() {
    list.replaceChildren(...ENTRIES.map((entry, k) => {
      const li = h('li', { class: 'legend-entry' }, canvases[k]);
      li.insertAdjacentHTML('beforeend', `<div><h3>${escapeHtml(t(`legend.${entry.key}.title`))}</h3><p>${escapeHtml(t(`legend.${entry.key}.body`))}</p></div>`);
      return li;
    }));
  }
  render();
  onLangChange(render);
}
