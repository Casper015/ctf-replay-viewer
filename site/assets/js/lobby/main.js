// Lobby entry point (index.html).

import { $, onReady } from '../core/dom.js';
import { applyI18n, onLangChange, t } from '../core/i18n.js';
import { hydrateIcons } from '../core/icons.js';
import { mountLangSwitch } from '../core/lang-switch.js';
import { loadCatalog } from '../core/data.js';
import { mountHero } from './hero.js';
import { mountMatchList } from './match-list.js';
import { mountLegend } from './legend.js';

onReady(async () => {
  hydrateIcons();
  applyI18n();
  mountLangSwitch($('#lang-switch'));
  onLangChange(() => {
    applyI18n();
    document.title = t('site.name');
  });
  document.title = t('site.name');
  mountLegend();

  const status = $('#list-status');
  let catalog;
  try {
    catalog = await loadCatalog();
  } catch (err) {
    console.error(err);
    status.innerHTML = `<h3>${t('lobby.loadErrorTitle')}</h3><p>${t(location.protocol === 'file:' ? 'viewer.errorFile' : 'viewer.errorBody')}</p>`;
    return;
  }
  status.hidden = true;

  const featured = catalog.matches.find((m) => m.featured) || catalog.matches[0];
  mountMatchList(catalog);
  if (featured) mountHero(featured, catalog);
});
