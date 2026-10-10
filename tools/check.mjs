// Static checks for the site. No dependencies: `node tools/check.mjs`.
// CI runs this (plus `python3 tools/build_catalog.py --check`) before every deploy.
//
//  1. zh-CN and en locale files have the same keys
//  2. every literal t('key') in JS and every data-i18n key in HTML exists
//  3. every relative JS import resolves to a file
//  4. every icon name used exists in icons.js
//  5. every local href/src in the HTML pages exists
//  6. catalog.json points at replay files that exist, with unique keys

import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SITE = join(ROOT, 'site');
const errors = [];
const fail = (msg) => errors.push(msg);
const rel = (p) => relative(ROOT, p);

function walk(dir, ext) {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) return walk(p, ext);
    return p.endsWith(ext) ? [p] : [];
  });
}

const jsFiles = walk(join(SITE, 'assets', 'js'), '.js');
const htmlFiles = readdirSync(SITE).filter((f) => f.endsWith('.html')).map((f) => join(SITE, f));

// 1. Locale parity (plural variants key_one / key_other count as the base key)
const zh = (await import(pathToFileURL(join(SITE, 'assets/js/locales/zh-CN.js')))).default;
const en = (await import(pathToFileURL(join(SITE, 'assets/js/locales/en.js')))).default;
const base = (k) => k.replace(/_(zero|one|two|few|many|other)$/, '');
const zhKeys = new Set(Object.keys(zh).map(base));
const enKeys = new Set(Object.keys(en).map(base));
for (const k of zhKeys) if (!enKeys.has(k)) fail(`locale: "${k}" is in zh-CN.js but missing from en.js`);
for (const k of enKeys) if (!zhKeys.has(k)) fail(`locale: "${k}" is in en.js but missing from zh-CN.js`);
for (const [name, dict] of [['zh-CN', zh], ['en', en]]) {
  for (const k of Object.keys(dict)) {
    if (/_(one|few|many)$/.test(k) && !(base(k) + '_other' in dict)) fail(`locale ${name}: "${k}" needs a matching "${base(k)}_other"`);
  }
}

// 2. Keys used in code and markup exist
const used = new Map(); // key -> first file that uses it
const use = (key, file) => { if (!used.has(key)) used.set(key, file); };
// Line comments hold usage examples, not real lookups
const code = (f) => readFileSync(f, 'utf8').replace(/^\s*\/\/.*$/gm, '').replace(/^\s*\*.*$/gm, '');
for (const f of jsFiles) {
  const src = code(f);
  for (const m of src.matchAll(/\bt\(\s*'([\w.]+)'/g)) use(m[1], f);
  for (const m of src.matchAll(/data-i18n="([\w.]+)"/g)) use(m[1], f);
}
for (const f of htmlFiles) {
  const src = readFileSync(f, 'utf8');
  for (const m of src.matchAll(/data-i18n="([\w.]+)"/g)) use(m[1], f);
  for (const m of src.matchAll(/data-i18n-attr="([^"]+)"/g)) {
    for (const pair of m[1].split(',')) use(pair.split(':')[1].trim(), f);
  }
}
for (const [key, file] of used) {
  // t('act.' + name): a dynamic key, so just require that the prefix is in use
  if (key.endsWith('.')) {
    if (![...zhKeys].some((k) => k.startsWith(key))) fail(`i18n: no keys start with "${key}" (used in ${rel(file)})`);
    continue;
  }
  if (!zhKeys.has(key)) fail(`i18n: "${key}" (used in ${rel(file)}) is not defined in the locale files`);
}

// 3. Relative imports resolve
for (const f of jsFiles) {
  const src = readFileSync(f, 'utf8');
  for (const m of src.matchAll(/(?:^|\n)\s*(?:import|export)[^'"`]*?from\s+'(\.[^']+)'/g)) {
    const target = resolve(dirname(f), m[1]);
    if (!existsSync(target)) fail(`import: ${rel(f)} imports "${m[1]}", which does not exist`);
  }
}

// 4. Icon names exist
const iconsSrc = readFileSync(join(SITE, 'assets/js/core/icons.js'), 'utf8');
const iconNames = new Set([...iconsSrc.matchAll(/^\s{2}(\w+):\s*'/gm)].map((m) => m[1]));
for (const f of [...jsFiles, ...htmlFiles]) {
  const src = readFileSync(f, 'utf8');
  const names = [
    ...[...src.matchAll(/\bicon\(\s*'(\w+)'/g)].map((m) => m[1]),
    ...[...src.matchAll(/data-icon="(\w+)"/g)].map((m) => m[1]),
  ];
  for (const n of names) if (!iconNames.has(n)) fail(`icon: "${n}" (used in ${rel(f)}) is not in icons.js`);
}

// 5. Local href/src in HTML exist
for (const f of htmlFiles) {
  const src = readFileSync(f, 'utf8');
  for (const m of src.matchAll(/\s(?:href|src)="([^"#?]+)[^"]*"/g)) {
    const url = m[1];
    if (/^(https?:|mailto:|data:|\/)/.test(url) || url === '') continue;
    if (!existsSync(join(SITE, url))) fail(`link: ${rel(f)} refers to "${url}", which does not exist`);
  }
}

// 6. Catalog consistency
const catalogPath = join(SITE, 'data', 'catalog.json');
if (!existsSync(catalogPath)) {
  fail('catalog: site/data/catalog.json is missing (run python3 tools/build_catalog.py)');
} else {
  const catalog = JSON.parse(readFileSync(catalogPath, 'utf8'));
  const keys = new Set();
  for (const m of catalog.matches) {
    if (keys.has(m.key)) fail(`catalog: duplicate key "${m.key}"`);
    keys.add(m.key);
    if (!existsSync(join(SITE, m.file))) fail(`catalog: ${m.key} points to ${m.file}, which does not exist`);
    for (const field of ['tag', 'title', 'desc']) {
      for (const lang of ['zh', 'en']) if (!m[field]?.[lang]) fail(`catalog: ${m.key}.${field}.${lang} is empty`);
    }
  }
  const contentDir = join(ROOT, 'content', 'matches');
  for (const f of readdirSync(contentDir).filter((n) => n.endsWith('.json'))) {
    const key = f.replace(/\.json$/, '');
    if (!keys.has(key)) fail(`catalog: content/matches/${f} is not in catalog.json (run python3 tools/build_catalog.py)`);
  }
}

if (errors.length) {
  console.error(errors.map((e) => `error: ${e}`).join('\n'));
  console.error(`\n${errors.length} problem(s) found`);
  process.exit(1);
}
console.log(`ok: ${jsFiles.length} modules, ${htmlFiles.length} pages, ${used.size} i18n keys, ${iconNames.size} icons checked`);
