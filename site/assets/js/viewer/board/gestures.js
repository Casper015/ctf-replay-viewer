// Pointer input for the board: tap, double-tap, drag-to-pan, pinch, wheel zoom and hover.
// Works the same for mouse, pen and touch via Pointer Events.

const TAP_SLOP = 8;          // px a pointer may move and still count as a tap
const DOUBLE_TAP_MS = 300;
const DOUBLE_TAP_ZOOM = 2.5;

/**
 * @param {HTMLCanvasElement} el
 * @param {import('./camera.js').Camera} camera
 * @param {{ onTap?:(x:number,y:number)=>void, onHover?:(x:number|null,y?:number)=>void,
 *           onCamera?:()=>void, onUserPan?:()=>void }} cb
 */
export function attachGestures(el, camera, cb) {
  const pointers = new Map();
  let start = null;      // first pointer down position for tap detection
  let moved = false;
  let pinch = null;      // { dist, mx, my }
  let lastTap = { t: 0, x: 0, y: 0 };

  const local = (e) => {
    const r = el.getBoundingClientRect();
    return [e.clientX - r.left, e.clientY - r.top];
  };

  el.addEventListener('pointerdown', (e) => {
    if (e.button !== undefined && e.button > 0) return;
    el.setPointerCapture?.(e.pointerId);
    const [x, y] = local(e);
    pointers.set(e.pointerId, { x, y });
    if (pointers.size === 1) {
      start = { x, y };
      moved = false;
    } else if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      pinch = { dist: Math.hypot(a.x - b.x, a.y - b.y), mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2 };
      moved = true;
      cb.onUserPan?.();
    }
  });

  el.addEventListener('pointermove', (e) => {
    const [x, y] = local(e);
    if (!pointers.has(e.pointerId)) {
      if (e.pointerType === 'mouse') cb.onHover?.(x, y);
      return;
    }
    const last = pointers.get(e.pointerId);
    pointers.set(e.pointerId, { x, y });

    if (pointers.size === 1) {
      if (!moved && Math.hypot(x - start.x, y - start.y) > TAP_SLOP) {
        moved = true;
        if (camera.zoomed) cb.onUserPan?.();
      }
      if (moved && camera.zoomed) {
        camera.panBy(x - last.x, y - last.y);
        cb.onCamera?.();
      }
    } else if (pointers.size === 2 && pinch) {
      const [a, b] = [...pointers.values()];
      const dist = Math.hypot(a.x - b.x, a.y - b.y);
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      camera.panBy(mx - pinch.mx, my - pinch.my);
      if (pinch.dist > 0) camera.zoomAt(mx, my, dist / pinch.dist);
      pinch = { dist, mx, my };
      cb.onCamera?.();
    }
  });

  const end = (e) => {
    if (!pointers.has(e.pointerId)) return;
    const [x, y] = local(e);
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinch = null;
    if (pointers.size === 0 && start && !moved && e.type === 'pointerup') {
      const now = performance.now();
      if (now - lastTap.t < DOUBLE_TAP_MS && Math.hypot(x - lastTap.x, y - lastTap.y) < 30) {
        camera.zoomed ? camera.reset() : camera.zoomAt(x, y, DOUBLE_TAP_ZOOM);
        cb.onUserPan?.();
        cb.onCamera?.();
        lastTap = { t: 0, x, y };
      } else {
        cb.onTap?.(x, y);
        lastTap = { t: now, x, y };
      }
    }
    if (pointers.size === 0) start = null;
  };
  el.addEventListener('pointerup', end);
  el.addEventListener('pointercancel', end);
  el.addEventListener('pointerleave', (e) => {
    if (e.pointerType === 'mouse' && !pointers.size) cb.onHover?.(null);
  });

  el.addEventListener('wheel', (e) => {
    e.preventDefault();
    const [x, y] = local(e);
    // Trackpad pinch arrives as ctrl+wheel with small deltas
    const speed = e.ctrlKey ? 0.012 : 0.0018;
    camera.zoomAt(x, y, Math.exp(-e.deltaY * speed));
    cb.onUserPan?.();
    cb.onCamera?.();
  }, { passive: false });
}
