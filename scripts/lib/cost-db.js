'use strict';
/**
 * Cost DB library — JSONL + SQLite dual-write for token tracking.
 *
 * JSONL: primary store, zero dependencies.
 * SQLite: secondary store for querying via `cost` skill (sqlite3 CLI).
 *
 * Security: uses execFileSync (no shell) for SQLite operations.
 * User-supplied values are escaped via single-quote doubling.
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { ensureDir } = require('./utils');

function getDbDir() {
  const dir = path.join(require('os').homedir(), '.claude', 'orch-costs');
  ensureDir(dir);
  return dir;
}

function jsonlPath() {
  return path.join(getDbDir(), 'costs.jsonl');
}

function sqlitePath() {
  return path.join(getDbDir(), 'usage.db');
}

function getProjectFromCwd() {
  try {
    const cwd = process.env.PWD || process.cwd();
    const git = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8', timeout: 3000 }).trim();
    return git ? path.basename(git) : path.basename(cwd);
  } catch {
    return 'unknown';
  }
}

function getRates(model) {
  const m = String(model || '').toLowerCase();
  if (m.includes('haiku')) return { in: 0.80, out: 4.0, cacheWrite: 1.00, cacheRead: 0.08 };
  if (m.includes('opus'))  return { in: 15.00, out: 75.0, cacheWrite: 18.75, cacheRead: 1.50 };
  return { in: 3.00, out: 15.0, cacheWrite: 3.75, cacheRead: 0.30 };
}

function estimateCost(inputTokens, outputTokens, cacheWrite, cacheRead, model) {
  const r = getRates(model);
  return Math.round((
    (inputTokens  / 1e6) * r.in +
    (outputTokens / 1e6) * r.out +
    (cacheWrite   / 1e6) * r.cacheWrite +
    (cacheRead    / 1e6) * r.cacheRead
  ) * 1e6) / 1e6;
}

function sumUsageFromTranscript(transcriptPath) {
  let content;
  try { content = fs.readFileSync(transcriptPath, 'utf8'); } catch { return null; }

  let inputTokens = 0, outputTokens = 0, cacheWrite = 0, cacheRead = 0;
  let model = 'unknown';

  for (const line of content.split('\n')) {
    if (!line.trim()) continue;
    let entry;
    try { entry = JSON.parse(line); } catch { continue; }
    if (entry.type !== 'assistant') continue;
    const msg = entry.message;
    if (!msg || !msg.usage) continue;
    const u = msg.usage;
    inputTokens  += Number(u.input_tokens)  || 0;
    outputTokens += Number(u.output_tokens) || 0;
    cacheWrite   += Number(u.cache_creation_input_tokens) || 0;
    cacheRead    += Number(u.cache_read_input_tokens) || 0;
    if (msg.model && msg.model !== 'unknown') model = msg.model;
  }

  return { inputTokens, outputTokens, cacheWrite, cacheRead, model };
}

function appendJsonl(row) {
  try {
    fs.appendFileSync(jsonlPath(), JSON.stringify(row) + '\n', 'utf8');
  } catch (_) {}
}

function esc(val) {
  return String(val).replace(/'/g, "''");
}

function runSqlite(sql) {
  try {
    execFileSync('sqlite3', [sqlitePath(), sql], { encoding: 'utf8', timeout: 5000 });
    return true;
  } catch { return false; }
}

function initSqlite() {
  return runSqlite(
    'CREATE TABLE IF NOT EXISTS usage (' +
    'id INTEGER PRIMARY KEY AUTOINCREMENT,' +
    'timestamp TEXT NOT NULL,' +
    'session_id TEXT NOT NULL,' +
    'project TEXT DEFAULT \'\',' +
    'stage TEXT DEFAULT \'\',' +
    'model TEXT DEFAULT \'unknown\',' +
    'input_tokens INTEGER DEFAULT 0,' +
    'output_tokens INTEGER DEFAULT 0,' +
    'cache_write INTEGER DEFAULT 0,' +
    'cache_read INTEGER DEFAULT 0,' +
    'cost_usd REAL DEFAULT 0.0,' +
    'tool_name TEXT DEFAULT \'\');' +
    'CREATE INDEX IF NOT EXISTS idx_usage_session ON usage(session_id);'
  );
}

function appendSqlite(row) {
  return runSqlite(
    "INSERT INTO usage " +
    "(timestamp, session_id, project, stage, model, " +
    "input_tokens, output_tokens, cache_write, cache_read, cost_usd, tool_name) " +
    "VALUES(" +
    "'" + esc(row.timestamp) + "','" + esc(row.session_id) + "','" + esc(row.project) + "'," +
    "'" + esc(row.stage) + "','" + esc(row.model) + "'," +
    Number(row.input_tokens) + "," + Number(row.output_tokens) + "," +
    Number(row.cache_write) + "," + Number(row.cache_read) + "," +
    Number(row.cost_usd) + ",'" + esc(row.tool_name) + "')"
  );
}

function writeRecord(record) {
  appendJsonl(record);
  const hasSqlite = initSqlite();
  if (hasSqlite) appendSqlite(record);
}

module.exports = {
  getDbDir, jsonlPath, sqlitePath,
  getProjectFromCwd, getRates, estimateCost,
  sumUsageFromTranscript,
  appendJsonl, initSqlite, appendSqlite, writeRecord,
};
