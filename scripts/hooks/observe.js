#!/usr/bin/env node
/**
 * Instinct observation hook (PreToolUse + PostToolUse).
 *
 * 将 hook JSON 中的工具调用事件追加到观察日志，供 continuous-learning 的
 * instinct 学习层消费。观测数据仅供分析，不干预执行（fail-open）。
 *
 * 设计原则（北极星）：观察是能力增强（自主进化数据源），不限制模型能力。
 * 可通过 SDD_DISABLED_HOOKS 或 hook-flags profile 关闭。
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { readStdin, TIMEOUT_MS } = require('../lib/stdin');
const { isHookEnabled } = require('../lib/hook-flags');

const OBS_LOG_DIR = path.join(os.homedir(), '.claude', 'orch-instincts');
const OBS_LOG_FILE = path.join(OBS_LOG_DIR, 'observations.jsonl');

async function main() {
  // 读取 hook JSON（2s 超时，fail-open）
  const raw = await readStdin(TIMEOUT_MS);
  if (!raw || !raw.trim()) return;

  let input;
  try { input = JSON.parse(raw.trim()); } catch { return; }

  const toolName = (input.tool_name || input.tool || input.name || '').toString().toLowerCase();
  const toolInput = input.tool_input || input.arguments || {};

  // 提取 skill/agent 名（若为 Skill/Agent 调用）
  let skill = null;
  if (typeof toolInput === 'string') {
    const m = toolInput.match(/orch:([\w-]+)/);
    if (m) skill = m[1];
  } else if (toolInput && typeof toolInput === 'object') {
    skill = toolInput.skill || toolInput.subagent_type || toolInput.agent || null;
    if (skill && skill.startsWith('orch:')) skill = skill.slice(5);
  }

  // 观察事件（紧凑格式）
  const event = {
    ts: new Date().toISOString(),
    tool: toolName,
    skill: skill || null,
    stage: toolInput.stage || input.current_stage || null,
    project: process.env.INIT_CWD || process.cwd(),
    hook: input.hook_event_name || null,
  };

  try {
    fs.mkdirSync(OBS_LOG_DIR, { recursive: true });
    fs.appendFileSync(OBS_LOG_FILE, JSON.stringify(event) + '\n', 'utf8');
  } catch (_) { /* fail-open: 观察失败不影响执行 */ }
}

main().catch(() => { /* fail-open */ });
