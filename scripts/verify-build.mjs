import assert from 'node:assert/strict';
import { access, readFile, readdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { parseFrontmatter } from '@astrojs/markdown-remark';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = path.join(root, 'dist');
const source = path.join(root, 'src/content/posts');

async function files(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map(entry => {
    const filename = path.join(directory, entry.name);
    return entry.isDirectory() ? files(filename) : [filename];
  }));
  return nested.flat();
}

async function exists(filename) {
  try { await access(filename); return true; } catch { return false; }
}

assert(await exists(path.join(output, 'index.html')), 'Run npm run build before npm run verify.');
const generated = await files(output);
const htmlFiles = generated.filter(filename => filename.endsWith('.html'));
const index = await readFile(path.join(output, 'index.html'), 'utf8');
const feed = await readFile(path.join(output, 'rss.xml'), 'utf8');
const sitemaps = (await Promise.all(generated.filter(filename => /sitemap.*\.xml$/.test(filename)).map(filename => readFile(filename, 'utf8')))).join('\n');
let published = 0;
let excluded = 0;

for (const filename of (await files(source)).filter(filename => /\.(md|mdx)$/.test(filename))) {
  const { frontmatter } = parseFrontmatter(await readFile(filename, 'utf8'));
  const id = path.relative(source, filename).replaceAll(path.sep, '/').replace(/\.(md|mdx)$/, '');
  const url = `/writing/${id}/`;
  const ready = frontmatter.draft === false && new Date(frontmatter.date) <= new Date();
  assert.equal(await exists(path.join(output, 'writing', id, 'index.html')), ready, `Incorrect publication state for ${id}`);
  for (const [name, contents] of [['index', index], ['RSS', feed], ['sitemap', sitemaps]]) {
    assert.equal(contents.includes(url), ready, `${name} has incorrect publication state for ${id}`);
  }
  if (ready) published++; else excluded++;
}

// Follow every local HTML link and asset reference against the actual build.
let checkedLinks = 0;
for (const filename of htmlFiles) {
  const html = await readFile(filename, 'utf8');
  for (const [, value] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    if (!value.startsWith('/') || value.startsWith('//')) continue;
    const pathname = decodeURIComponent(new URL(value, 'https://lms21a.github.io').pathname);
    const target = path.join(output, pathname, pathname.endsWith('/') ? 'index.html' : '');
    assert(await exists(target), `Broken local reference ${value} in ${path.relative(output, filename)}`);
    checkedLinks++;
  }
  assert(!html.includes('astro-error-overlay'), `Framework error overlay in ${filename}`);
}
console.log(`Verified ${published} published post(s), ${excluded} excluded draft/future post(s), ${htmlFiles.length} HTML pages, and ${checkedLinks} local references.`);
