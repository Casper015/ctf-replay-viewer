// Two-option language switch (中 / EN). Mount into any element; it keeps itself in sync.
import { LANGS, getLang, setLang, onLangChange, t } from './i18n.js';
import { h } from './dom.js';

export function mountLangSwitch(host) {
  const group = h('div', { class: 'segmented lang-switch', role: 'group' });
  const buttons = LANGS.map((l) =>
    h('button', {
      type: 'button',
      lang: l.htmlLang,
      title: l.label,
      onclick: () => setLang(l.code),
    }, l.short),
  );
  group.append(...buttons);

  const sync = () => {
    group.setAttribute('aria-label', t('common.language'));
    LANGS.forEach((l, k) => buttons[k].setAttribute('aria-pressed', String(l.code === getLang())));
  };
  sync();
  onLangChange(sync);
  host.replaceChildren(group);
  return group;
}
