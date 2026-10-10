// Board camera: maps board cells to screen pixels (CSS px). Zoom 1 fits the whole board.
// Board coordinates: cell (x, y) spans [x, x+1) × [y, y+1); its center is (x + 0.5, y + 0.5).

const MIN_CELL_AT_MAX_ZOOM = 56; // px: max zoom lets one cell grow to at least this size

export class Camera {
  constructor() {
    this.n = 1;
    this.w = 1;
    this.h = 1;
    this.zoom = 1;
    this.cx = 0.5;
    this.cy = 0.5;
  }

  setBoard(n) {
    this.n = n;
    this.reset();
  }

  setViewport(w, h) {
    this.w = Math.max(1, w);
    this.h = Math.max(1, h);
    this.clamp();
  }

  get baseCell() { return Math.min(this.w, this.h) / this.n; }
  get cell() { return this.baseCell * this.zoom; }
  get maxZoom() { return Math.max(3, MIN_CELL_AT_MAX_ZOOM / this.baseCell); }
  get zoomed() { return this.zoom > 1.001; }

  reset() {
    this.zoom = 1;
    this.cx = this.n / 2;
    this.cy = this.n / 2;
  }

  toScreen(x, y) {
    const c = this.cell;
    return [(x - this.cx) * c + this.w / 2, (y - this.cy) * c + this.h / 2];
  }

  toBoard(sx, sy) {
    const c = this.cell;
    return [(sx - this.w / 2) / c + this.cx, (sy - this.h / 2) / c + this.cy];
  }

  /** Zoom by `factor`, keeping the board point under (sx, sy) fixed on screen. */
  zoomAt(sx, sy, factor) {
    const [bx, by] = this.toBoard(sx, sy);
    this.zoom = Math.min(this.maxZoom, Math.max(1, this.zoom * factor));
    const c = this.cell;
    this.cx = bx - (sx - this.w / 2) / c;
    this.cy = by - (sy - this.h / 2) / c;
    this.clamp();
  }

  panBy(dx, dy) {
    const c = this.cell;
    this.cx -= dx / c;
    this.cy -= dy / c;
    this.clamp();
  }

  /** Move the center a fraction k of the way toward (x, y). Used for follow mode. */
  easeTo(x, y, k) {
    this.cx += (x - this.cx) * k;
    this.cy += (y - this.cy) * k;
    this.clamp();
  }

  clamp() {
    const c = this.cell;
    const hw = this.w / 2 / c;
    const hh = this.h / 2 / c;
    this.cx = this.n <= hw * 2 ? this.n / 2 : Math.min(this.n - hw, Math.max(hw, this.cx));
    this.cy = this.n <= hh * 2 ? this.n / 2 : Math.min(this.n - hh, Math.max(hh, this.cy));
  }

  key() {
    return `${this.w}x${this.h}:${this.zoom.toFixed(4)}:${this.cx.toFixed(4)}:${this.cy.toFixed(4)}`;
  }
}
