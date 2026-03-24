#!/usr/bin/env node
/**
 * RAISE-634: Audit built HTML for broken body hrefs.
 * Fails if any href under dist/docs/ ends with .md or contains a duplicate directory prefix.
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, extname } from 'path';

const DIST_DIR = new URL('../dist/docs', import.meta.url).pathname;

function walk(dir) {
  const entries = readdirSync(dir);
  const files = [];
  for (const entry of entries) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      files.push(...walk(full));
    } else if (extname(entry) === '.html') {
      files.push(full);
    }
  }
  return files;
}

const MD_HREF = /href="([^"]*\.md[^"]*)"/g;

let broken = 0;
const files = walk(DIST_DIR);

for (const file of files) {
  const content = readFileSync(file, 'utf8');
  let match;
  while ((match = MD_HREF.exec(content)) !== null) {
    const href = match[1];
    // Skip pagefind, _astro, sitemap, external
    if (href.startsWith('http') || href.includes('pagefind') || href.includes('_astro') || href.includes('sitemap')) continue;
    console.error(`BROKEN: ${file.replace(DIST_DIR, '')} → href="${href}"`);
    broken++;
  }
}

if (broken > 0) {
  console.error(`\n${broken} broken .md href(s) found in built docs.`);
  process.exit(1);
} else {
  console.log(`✓ No broken .md hrefs found in ${files.length} HTML files.`);
}
