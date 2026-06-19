#!/usr/bin/env node
/**
 * Cost Tracker Hook (Stop event)
 *
 * Reads transcript_path from Stop hook stdin, sums token usage across all
 * assistant turns in the session JSONL, and writes to JSONL + SQLite.
 *
 * Stop hook stdin: { session_id, transcript_path, cwd, hook_event_name, ... }
 *
 * Transcript JSONL assistant entry shape:
 *   { type: "assistant", message: { model, usage: { input_tokens, output_tokens,
 *     cache_creation_input_tokens, cache_read_input_tokens } } }
 *
 * Cumulative: Stop fires per assistant response. Each row = cumulative session
 * totals to that point. Last row per session_id = full session cost.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const { readStdinSync } = require('../lib/stdin');
const { isHookEnabled } = require('../lib/hook-flags');
const {
  getProjectFromCwd, estimateCost,
  sumUsageFromTranscript, writeRecord,
} = require('../lib/cost-db');

const HOOK_ID = 'stop:cost-tracker';

function main() {
  const raw = readStdinSync();
  if (!isHookEnabled(HOOK_ID)) { process.stdout.write(raw); return; }

  let input;
  try { input = JSON.parse(raw); } catch { process.stdout.write(raw); return; }

  const transcriptPath = input.transcript_path || process.env.CLAUDE_TRANSCRIPT_PATH || null;
  const sessionId = input.session_id || process.env.CLAUDE_SESSION_ID || 'default';

  if (!transcriptPath || !fs.existsSync(transcriptPath)) {
    process.stdout.write(raw);
    return;
  }

  const usage = sumUsageFromTranscript(transcriptPath);
  if (!usage) { process.stdout.write(raw); return; }

  const { inputTokens, outputTokens, cacheWrite, cacheRead, model } = usage;
  const costUsd = estimateCost(inputTokens, outputTokens, cacheWrite, cacheRead, model);

  writeRecord({
    timestamp:   new Date().toISOString(),
    session_id:  sessionId,
    project:     getProjectFromCwd(),
    stage:       getCurrentStage(),
    model:       model,
    input_tokens:  inputTokens,
    output_tokens: outputTokens,
    cache_write:   cacheWrite,
    cache_read:    cacheRead,
    cost_usd:      costUsd,
    tool_name:     'session',
  });

  process.stdout.write(raw);
}

try { main(); } catch (_) { /* fail-open */ }
