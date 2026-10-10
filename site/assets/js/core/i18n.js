// Internationalisation: one flat dictionary per language in ../locales/.
//
//   t('viewer.turn', { turn: 12, total: 400 })   -> "回合 12 / 400" | "Turn 12 of 400"
//   t('unit.captures', { count: 3 })             -> uses captures_one / captures_other by plural rules
//   pick({ zh: '…', en: '…' })                   -> localized field from catalog data
//
// Static markup is translated with attributes, re-applied whenever the language changes:
//   <span data-i18n="lobby.title"></span>
//   <input data-i18n-attr="placeholder:lobby.searchPlaceholder,aria-label:lobby.search">
//
// Adding a key: add it to BOTH locale files. `node tools/check.mjs` fails on missing keys.

import zh from '../locales/zh-CN.js';
import en from '../locales/en.js';
import { getPref, setPref } from './prefs.js';

const DICTS = { zh, en };
export const LANGS = [
  { code: 'zh', htmlLang: 'zh-CN', short: '中', label: '中文' },
  { code: 'en', htmlLang: 'en', short: 'EN', label: 'English' },
];

const listeners = new Set();
let lang = detectLang();

function detectLang() {
  const fromUrl = new URLSearchParams(location.search).get('lang');
  if (fromUrl && DICTS[normalize(fromUrl)]) return normalize(fromUrl);
  const saved = getPref('lang');
  if (saved && DICTS[saved]) return saved;
  const nav = (navigator.languages && navigator.languages[0]) || navigator.language || 'zh';
  return normalize(nav);
}

function normalize(code) {
  return String(code).toLowerCase().startsWith('zh') ? 'zh' : 'en';
}

export const getLang = () => lang;

export function setLang(code) {
  const next = normalize(code);
  if (next === lang) return;
  lang = next;
  setPref('lang', lang);
  syncDocument();
  applyI18n(document);
  listeners.forEach((fn) => fn(lang));
}

/** Subscribe to language changes. Returns an unsubscribe function. */
export function onLangChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

const plural = {};
function pluralKey(key, count) {
  plural[lang] ??= new Intl.PluralRules(lang === 'zh' ? 'zh-CN' : 'en-US');
  return `${key}_${plural[lang].select(count)}`;
}

export function t(key, vars = {}) {
  const dict = DICTS[lang];
  let str;
  if (typeof vars.count === 'number') {
    const pk = pluralKey(key, vars.count);
    str = dict[pk] ?? dict[`${key}_other`];
  }
  str ??= dict[key] ?? DICTS.zh[key] ?? key;
  return str.replace(/\{(\w+)\}/g, (_, name) => (name in vars ? vars[name] : `{${name}}`));
}

/** Read a localized field ({ zh, en }) with fallback to the other language. */
export function pick(field) {
  if (field == null || typeof field !== 'object') return field ?? '';
  return field[lang] ?? field.zh ?? field.en ?? '';
}

export function applyI18n(root = document) {
  for (const el of root.querySelectorAll('[data-i18n]')) {
    el.textContent = t(el.dataset.i18n);
  }
  for (const el of root.querySelectorAll('[data-i18n-attr]')) {
    for (const pair of el.dataset.i18nAttr.split(',')) {
      const [attr, key] = pair.split(':').map((s) => s.trim());
      if (attr && key) el.setAttribute(attr, t(key));
    }
  }
}

function syncDocument() {
  const meta = LANGS.find((l) => l.code === lang);
  document.documentElement.lang = meta.htmlLang;
  document.documentElement.dataset.lang = lang;
}

syncDocument();
