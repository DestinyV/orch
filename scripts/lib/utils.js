'use strict';
/**
 * Shared utilities for orch scripts.
 */
const fs = require('fs');
const path = require('path');

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function glob(pattern, root) {
  const results = [];
  const tokens = pattern.split('*');
  function walk(dir) {
    let entries;
    try { entries = fs.readdirSync(dir); } catch (_) { return; }
    for (const e of entries) {
      const full = path.join(dir, e);
      const stat = fs.statSync(full);
      if (stat.isDirectory()) walk(full);
      else if (full.endsWith(tokens[tokens.length - 1])) results.push(full);
    }
  }
  walk(root);
  return results;
}

function timestamp() {
  return new Date().toISOString();
}

module.exports = { ensureDir, glob, timestamp };
