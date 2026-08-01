#!/usr/bin/env node
/**
 * SessionStart hook.
 * Checks for incomplete workflows and restores state.
 */
const fs = require('fs');
const path = require('path');
const { isHookEnabled } = require('../lib/hook-flags');
const { STAGE_ORDER, STAGE_OUTPUTS } = require('../lib/stage-contracts');

const HOOK_ID = 'session:init';

// 阶段显示名映射（可选，用于恢复建议更友好）
const STAGE_NAMES = {
  '0_workflow_control': '步骤0 初始化',
  '0.5_socratic_clarify': '步骤0.5 澄清',
  '1_spec_creation': '步骤1 spec',
  '2_test_design': '步骤2 test-design',
  '3_code_design': '步骤3 design',
  '3.5_api_contract': '步骤3.5 contract',
  '4_code_task': '步骤4 task',
  '5_code_execute': '步骤5 execute',
  '5.5_exception_handler': '步骤5.5 exception',
  '6_code_test': '步骤6 test',
  '7_spec_archive': '步骤7 archive',
  '8_evaluation': '步骤8 evaluation',
  '9_knowledge_continuum': '步骤9 continuous-learning',
};

// 从 done 阶段推导下一待续接阶段
function findNextStage(state) {
  const stages = state.stages || [];
  const doneNames = new Set(
    stages.filter(s => s.status === 'done' || s.status === 'completed').map(s => s.stage)
  );
  // 取所有已 done 阶段的最大 order
  let lastDoneOrder = -1;
  for (const name of doneNames) {
    const order = STAGE_ORDER[name];
    if (order !== undefined && order > lastDoneOrder) lastDoneOrder = order;
  }
  // 下一个 order 最小且 > lastDoneOrder 且未 done 的阶段
  // 跳过无独立 gate 产出的阶段（5.5 exception 是 execute 子过程，8 写 eval.json 由 0 覆盖）
  let nextStage = null;
  let nextOrder = Infinity;
  for (const [stageName, order] of Object.entries(STAGE_ORDER)) {
    if (order > lastDoneOrder && order < nextOrder && !doneNames.has(stageName)) {
      const hasOwnOutputs = STAGE_OUTPUTS[stageName] && STAGE_OUTPUTS[stageName].length > 0;
      if (!hasOwnOutputs) continue; // 跳过子过程/无独立产出阶段
      nextStage = stageName;
      nextOrder = order;
    }
  }
  return nextStage;
}

// 检查下一阶段的前置产出，返回缺失清单
function checkMissingOutputs(rootDir, reqId, stageName) {
  const required = STAGE_OUTPUTS[stageName];
  if (!required || required.length === 0) return [];
  const missing = [];
  for (const out of required) {
    if (out === 'completion-report') continue; // 状态标志，session-start 不校验
    const outPath = path.join(rootDir, 'orch-spec', reqId, out);
    if (!fs.existsSync(outPath)) missing.push(out);
  }
  return missing;
}

function checkWorkflowState(rootDir) {
  const specDev = path.join(rootDir, 'orch-spec');
  if (!fs.existsSync(specDev)) return;

  const entries = fs.readdirSync(specDev);
  for (const entry of entries) {
    const stateFile = path.join(specDev, entry, '.workflow-state.json');
    if (!fs.existsSync(stateFile)) continue;

    try {
      const state = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
      if (state.status !== 'in_progress') continue;

      console.log(`[orch] 工作流进行中: ${entry} (阶段: ${state.current_stage || '未知'})`);

      const nextStage = findNextStage(state);
      if (nextStage) {
        const name = STAGE_NAMES[nextStage] || nextStage;
        const missing = checkMissingOutputs(rootDir, entry, nextStage);
        if (missing.length === 0) {
          console.log(`[orch] 建议从 ${name} 续接 (resume-from-${nextStage})`);
        } else {
          console.log(`[orch] 续接 ${name} (resume-from-${nextStage}) 但前置产出缺失: ${missing.join(', ')}`);
        }
        // 不静默自动续接（北极星：模型自主决策，但提供完整恢复信息）
        console.log('[orch] 继续请运行: /start-dev');
      } else {
        console.log('[orch] 继续请运行: /start-dev');
      }
    } catch (_) { /* ignore */ }
  }
}

function main() {
  if (!isHookEnabled(HOOK_ID)) return;

  const root = process.env.CLAUDE_PLUGIN_ROOT
    || process.env.INIT_CWD
    || process.cwd();

  checkWorkflowState(root);
}

try { main(); } catch (_) { /* fail-open */ }
