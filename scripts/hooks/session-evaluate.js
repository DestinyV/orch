#!/usr/bin/env node
/**
 * Stop hook — session evaluation and workflow continuation detection.
 * Uses safe stdin reading with timeout and hook-flags gating.
 */
const fs = require('fs');
const path = require('path');
const { isHookEnabled } = require('../lib/hook-flags');
const { readStdinSync } = require('../lib/stdin');

const HOOK_ID = 'stop:evaluate';

function checkIncompleteWorkflows(rootDir) {
  const specDev = path.join(rootDir, 'orch-spec');
  if (!fs.existsSync(specDev)) return;

  const entries = fs.readdirSync(specDev);
  for (const entry of entries) {
    const stateFile = path.join(specDev, entry, '.workflow-state.json');
    if (!fs.existsSync(stateFile)) continue;

    try {
      const state = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
      if (state.status === 'in_progress') {
        const stage = state.current_stage || 'unknown';
        console.log(`[orch] 工作流未完成: ${entry} (阶段: ${stage})`);
        // 检测是否 learnings 已有但报告未生成
        if (stage === '9_knowledge_continuum' && !state.completion_report_generated) {
          console.log(`[orch] ⚠️ 知识提取已完成但完成报告未生成！派遣 completion-reporter: Agent(subagent_type="orch:completion-reporter", prompt="为需求 ${entry} 生成工作流完成报告")`);
        } else {
          console.log(`[orch] 继续请运行: /start-dev`);
        }
      }
    } catch (_) { /* ignore invalid JSON */ }
  }
}

function main() {
  // Consume stdin regardless (required by Stop hook protocol)
  readStdinSync();

  if (!isHookEnabled(HOOK_ID)) return;

  const root = process.env.CLAUDE_PLUGIN_ROOT || process.cwd();
  checkIncompleteWorkflows(root);
}

try { main(); } catch (_) { /* fail-open */ }
