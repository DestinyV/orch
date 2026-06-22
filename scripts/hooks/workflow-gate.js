'use strict';
/**
 * GATE Workflow Validator (PostToolUse hook)
 *
 * 在每次 Skill/Agent 调用后自动校验工作流状态：
 * - 阶段顺序合规（禁止跳过）
 * - stages[] 非空
 * - 必要产出文件存在
 *
 * 设计原则：fail-open。违规时写入 .workflow-eval.json 的 events[] 并
 * 输出 stderr 警告，但不阻断执行。用户可在 evaluation 阶段查看 GATE 报告。
 *
 * 注册方式：hooks.json → PostToolUse → matcher: "Skill|Agent"
 */

const fs = require('fs');
const path = require('path');

const PLUGIN_ROOT = process.env.CLAUDE_PLUGIN_ROOT || process.cwd();

// 阶段序号映射：用于校验顺序
const STAGE_ORDER = {
  '0_workflow_control': 0,
  '0.5_socratic_clarify': 0.5,
  '1_spec_creation': 1,
  '2_test_design': 2,
  '3_code_design': 3,
  '3.5_api_contract': 3.5,
  '4_code_task': 4,
  '5_code_execute': 5,
  '5.5_exception_handler': 5.5,
  '6_code_test': 6,
  '7_spec_archive': 7,
  '8_evaluation': 8,
  '9_knowledge_continuum': 9,
};

// 各阶段必须的产出文件（相对 orch-spec/{req_id}/）
const STAGE_OUTPUTS = {
  '0_workflow_control': ['.workflow-state.json', '.workflow-eval.json'],
  '1_spec_creation': ['spec/requirement.md', 'spec/scenarios'],
  '4_code_task': ['tasks/tasks.md'],
  '7_spec_archive': ['archive-log.md'],
};

function findWorkflowStates() {
  const specDir = path.join(PLUGIN_ROOT, 'orch-spec');
  if (!fs.existsSync(specDir)) return [];
  const states = [];
  for (const entry of fs.readdirSync(specDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const stateFile = path.join(specDir, entry.name, '.workflow-state.json');
    if (fs.existsSync(stateFile)) {
      try {
        const data = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
        states.push({ reqId: entry.name, state: data, statePath: stateFile });
      } catch (_) { /* skip invalid JSON */ }
    }
  }
  return states;
}

function validateSequence(currentStage, doneStages) {
  const cur = STAGE_ORDER[currentStage];
  if (cur === undefined) return [];

  const issues = [];
  const doneNames = new Set(doneStages.map(s => s.stage));

  for (const [stageName, order] of Object.entries(STAGE_ORDER)) {
    if (order >= cur) break;
    if (order !== 0.5 && !doneNames.has(stageName) && order < cur) {
      issues.push(`GATE: stage "${stageName}" (order ${order}) not completed before "${currentStage}" (${cur})`);
    }
  }

  // 步骤7完成但8/9未执行 → 输出警告（上下文切分检测）
  if (currentStage === '7_spec_archive' && doneNames.has('7_spec_archive')) {
    const hasEval = doneNames.has('8_evaluation');
    const hasLearn = doneNames.has('9_knowledge_continuum');
    if (!hasEval && !hasLearn) {
      issues.push('GATE: step 7 (archive) complete — steps 8 (evaluation) and 9 (continuous-learning) must execute. Resume from step 8 to continue.');
    }
  }
  return issues;
}

function validateOutputs(stageName, reqId) {
  const required = STAGE_OUTPUTS[stageName];
  if (!required) return [];
  const issues = [];
  for (const out of required) {
    const outPath = path.join(PLUGIN_ROOT, 'orch-spec', reqId, out);
    if (!fs.existsSync(outPath)) {
      issues.push(`GATE: required output missing: ${out}`);
    }
  }
  return issues;
}

function appendEvalEvent(reqId, event) {
  const evalPath = path.join(PLUGIN_ROOT, 'orch-spec', reqId, '.workflow-eval.json');
  try {
    const data = JSON.parse(fs.readFileSync(evalPath, 'utf8'));
    data.events = data.events || [];
    data.events.push(event);
    fs.writeFileSync(evalPath, JSON.stringify(data, null, 2), 'utf8');
  } catch (_) { /* fail-open: skip if eval file unavailable */ }
}

function main() {
  const stdin = fs.readFileSync(process.stdin.fd, 'utf8').trim();
  if (!stdin) return;

  let input;
  try { input = JSON.parse(stdin); } catch { return; }

  // 只校验 Skill/Agent 调用
  const toolName = (input.tool || input.name || '').toLowerCase();
  if (!toolName.includes('skill') && !toolName.includes('agent')) return;

  const workflows = findWorkflowStates();
  if (workflows.length === 0) return;

  let hasIssues = false;

  for (const { reqId, state, statePath } of workflows) {
    if (state.status !== 'in_progress') continue;

    const currentStage = state.current_stage || '';
    const doneStages = state.stages || [];

    // 校验阶段顺序
    const seqIssues = validateSequence(currentStage, doneStages);
    // 校验产出文件
    const outIssues = validateOutputs(currentStage, reqId);

    // 步骤9 learnings 已写入但 completion_report 未生成
    if (currentStage === '9_knowledge_continuum' && !state.completion_report_generated) {
      seqIssues.push('GATE: step 9 learnings written but completion_report_generated is not true. Dispatch completion-reporter Agent to generate the final report.');
    }

    const allIssues = [...seqIssues, ...outIssues];
    if (allIssues.length === 0) continue;

    hasIssues = true;
    for (const msg of allIssues) {
      console.error(`[GATE] ${msg}`); // stderr doesn't block
      appendEvalEvent(reqId, {
        type: 'hard_gate',
        stage: currentStage,
        message: msg,
        timestamp: new Date().toISOString(),
      });
    }
  }

  // 新增：Agent 参数校验 + 串行降级检测
  if (toolName.includes('agent')) {
    const agentInput = (input.tool_input || input.arguments || {});

    // Agent 参数校验
    const agentType = agentInput.subagent_type || agentInput.agent || '';
    if (agentType && !agentType.startsWith('orch:')) {
      console.error('[GATE] Warning: Agent type not under orch namespace. This may not follow workflow conventions.');
    }

    // 串行降级检测：Agent 调用未设置 run_in_background=true
    const isBackground = agentInput.run_in_background === true ||
                         (typeof agentInput.run_in_background === 'string' &&
                          agentInput.run_in_background === 'true');

    if (!isBackground) {
      for (const { reqId, state } of workflows) {
        if (state.status !== 'in_progress') continue;

        // 检查当前批次是否有多个待执行的并行 Task
        const executeStage = (state.stages || []).find(s => s.stage === '5_code_execute');
        if (executeStage && executeStage.status === 'in_progress') {
          const progress = executeStage.progress || {};
          const batch = executeStage.batches ?
            executeStage.batches.find(b => b.status === 'in_progress') : null;

          if (batch && Array.isArray(batch.tasks) && batch.tasks.length >= 2) {
            const msg = `GATE: Agent dispatched without run_in_background=true in batch with ${batch.tasks.length} parallel tasks. This may indicate serial degradation.`;
            console.error(`[GATE] ${msg}`);
            appendEvalEvent(reqId, {
              type: 'warning',
              stage: '5_code_execute',
              message: msg,
              timestamp: new Date().toISOString(),
            });
          }
        }
      }
    }
  }

  if (hasIssues) {
    console.error('[GATE] Validation completed with warnings (fail-open). Check .workflow-eval.json events[] for details.');
  }
}

main();
