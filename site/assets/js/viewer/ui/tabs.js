// Tab bar for the side panel. Panes are <section id="pane-<name>"> siblings.

import { $$ } from '../../core/dom.js';

export const TABS = ['standings', 'chart', 'feed', 'stats'];

export function mountTabs(store) {
  const buttons = $$('#tabs [role="tab"]');

  buttons.forEach((btn) => {
    btn.addEventListener('click', () => store.set({ tab: btn.dataset.tab }));
    btn.addEventListener('keydown', (e) => {
      const k = buttons.indexOf(btn);
      const next = e.key === 'ArrowRight' ? k + 1 : e.key === 'ArrowLeft' ? k - 1 : null;
      if (next === null) return;
      e.preventDefault();
      const target = buttons[(next + buttons.length) % buttons.length];
      target.focus();
      store.set({ tab: target.dataset.tab });
    });
  });

  function render(s) {
    for (const btn of buttons) {
      const on = btn.dataset.tab === s.tab;
      btn.setAttribute('aria-selected', String(on));
      btn.tabIndex = on ? 0 : -1;
      document.getElementById(btn.getAttribute('aria-controls')).hidden = !on;
    }
  }
  store.subscribe(['tab'], render);
  render(store.get());
}
