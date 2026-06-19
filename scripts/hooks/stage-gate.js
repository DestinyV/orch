'use strict';
/**
 * Stage Gate Validator (PreToolUse hook)
 *
 * 在 Claude 调用 Skill 之前校验工作流阶段前置条件。
 * 与 PostToolUse workflow-gate.js 的区别：
 *   - 本钩子：事前阻断（PreToolUse），拒绝跳过阶段
 *   - workflow-gate.js：事后警告（PostToolUse），fail-open
 *
 * 阻断逻辑：
 *   1. 检查调用的 Skill 名称
 *   2. 查找对应的 orch-spec/{req_id}/.workflow-state.json
 *   3. 确定该 Skill 的前置阶段
 *   4. 前置未完成 → 返回 deny 决策 + 缺失阶段信息
 *   5. 前置已完成 → allow
 *
 * 注册方式：hooks.json → PreToolUse → matcher: "Skill"
 */

const fs = require('fs');
const path = require('path');

const PLUGIN_ROOT = process.env.CLAUDE_PLUGIN_ROOT || process.cwd();

// Skill → 前置阶段映射
// 格式: "skill-name": { stage: "前置阶段key", name: "中文名", outputs: ["必要产物"] }
const SKILL_PREREQUISITES = {
  'spec': {
    stage: '0_workflow_control',
    name: '工作流初始化(步骤0)',
    outputs: ['.workflow-state.json'],
  },
  'clarify': null, // 无前置，在 workflow 步骤0.5 内触发
  'test-design': {
    stage: '1_spec_creation',
    name: '规范生成(步骤1)',
    outputs: ['spec/requirement.md'],
  },
  'design': {
    stage: '1_spec_creation',
    name: '规范生成(步骤1)',
    outputs: ['spec/requirement.md'],
  },
  'contract': {
    stage: '3_code_design',
    name: '架构设计(步骤3)',
    outputs: ['design/design.md'],
  },
  'task': {
    stage: '3_code_design',
    name: '架构设计(步骤3)',
    outputs: ['design/design.md'],
  },
  'execute': {
    stage: '4_code_task',
    name: '任务拆解(步骤4)',
    outputs: ['tasks/tasks.md'],
  },
  'exception': {
    stage: '5_code_execute',
    name: '代码执行(步骤5)',
    outputs: [], // exception 是 execute 子过程，产出在 execute 中
  },
  'test': {
    stage: '5_code_execute',
    name: '代码执行(步骤5)',
    outputs: ['execution/execution-report.md'],
  },
  'archive': {
    stage: '6_code_test',
    name: '测试验证(步骤6)',
    outputs: ['testing/testing-report.md'],
  },
  'continuous-learning': {
    stage: '8_evaluation',
    name: '效果评估(步骤8)',
    outputs: ['.workflow-eval.json'],
  },
};

// 阶段 key → 序号
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

// 这些 Skill 不参与阶段门控（工具类/辅助类 Skill）
const EXEMPT_SKILLS = [
  'scripts', 'context-budget', 'depth', 'compact', 'cost',
  'ralph-loop', 'using-orch', 'debug', 'req-change', 'spec-migrate',
  'checkpoint', 'code-review', 'cost-report', 'plan', 'quality-gate',
  'session-resume', 'session-save', 'start-dev',
];

function findInProgressWorkflows() {
  const specDir = path.join(PLUGIN_ROOT, 'orch-spec');
  if (!fs.existsSync(specDir)) return [];
  const wfs = [];
  for (const entry of fs.readdirSync(specDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const stateFile = path.join(specDir, entry.name, '.workflow-state.json');
    if (!fs.existsSync(stateFile)) continue;
    try {
      const data = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
      if (data.status === 'in_progress') {
        wfs.push({ reqId: entry.name, state: data, statePath: stateFile });
      }
    } catch (_) { /* skip */ }
  }
  return wfs;
}

function getSkillName(toolInput) {
  // toolInput 可能是: "Skill(\"orch:spec\", ...)" 或 { skill: "orch:spec", ... }
  if (typeof toolInput === 'string') {
    const m = toolInput.match(/Skill\(["']orch:([^"']+)["']/);
    return m ? m[1] : null;
  }
  if (toolInput && typeof toolInput === 'object') {
    return toolInput.skill || toolInput.name || null;
  }
  return null;
}

function extractSkillFromToolName(toolName, toolInput) {
  // 先从 tool_input 提取
  const fromInput = getSkillName(toolInput);
  if (fromInput) return fromInput;
  // 从 tool_name 提取
  const m = (toolName || '').match(/orch:(\S+)/);
  return m ? m[1] : null;
}

function isStageDone(stages, stageKey) {
  if (!stages || !Array.isArray(stages)) return false;
  const s = stages.find(s => s.stage === stageKey);
  return s && (s.status === 'done' || s.status === 'completed');
}

function checkOutputsExist(reqId, outputs) {
  if (!outputs || outputs.length === 0) return [];
  const missing = [];
  for (const out of outputs) {
    const outPath = path.join(PLUGIN_ROOT, 'orch-spec', reqId, out);
    if (!fs.existsSync(outPath)) {
      missing.push(out);
    }
  }
  return missing;
}

function main() {
  let raw = '';
  try {
    const chunks = [];
    const fd = process.stdin.fd;
    let chunk;
    while ((chunk = fs.readFileSync(fd, 'utf8', 4096))) {
      chunks.push(chunk);
      if (chunks.length > 10) break; // safety limit
    }
    raw = chunks.join('');
  } catch (_) {
    // fallback: try reading from /dev/stdin
    try { raw = fs.readFileSync('/dev/stdin', 'utf8'); } catch (e) { /* ignore */ }
  }

  if (!raw || !raw.trim()) {
    process.stdout.write(JSON.stringify({ decision: 'allow' }));
    return;
  }

  let input;
  try { input = JSON.parse(raw.trim()); } catch {
    process.stdout.write(JSON.stringify({ decision: 'allow' }));
    return;
  }

  const toolName = (input.tool_name || input.tool || '').toLowerCase();
  const toolInput = input.tool_input || input.arguments || {};

  // 只处理 Skill 调用
  if (!toolName.includes('skill')) {
    process.stdout.write(JSON.stringify({ decision: 'allow' }));
    return;
  }

  const skillName = extractSkillFromToolName(toolName, toolInput);
  if (!skillName) {
    process.stdout.write(JSON.stringify({ decision: 'allow' }));
    return;
  }

  // 豁免 Skill 直接放行
  if (EXEMPT_SKILLS.includes(skillName)) {
    process.stdout.write(JSON.stringify({ decision: 'allow' }));
    return;
  }

  const prereq = SKILL_PREREQUISITES[skillName];
  if (!prereq) {
    // unknown skill or clarify-type (no prereq) — allow
    process.stdout.write(JSON.stringify({ decision: 'allow' }));
    return;
  }

  // 查找进行中的工作流
  const wfs = findInProgressWorkflows();
  if (wfs.length === 0) {
    // 无进行中工作流 → 可能是独立 Skill 调用，放行
    process.stdout.write(JSON.stringify({ decision: 'allow' }));
    return;
  }

  const blocks = [];

  for (const { reqId, state } of wfs) {
    const stages = state.stages || [];
    const prereqStage = prereq.stage;

    // 检查前置阶段是否完成
    if (!isStageDone(stages, prereqStage)) {
      // 检查是否因为前置阶段不在 stages 中（未被记录）而非 failed
      const prereqInStages = stages.find(s => s.stage === prereqStage);
      if (!prereqInStages) {
        blocks.push(
          `工作流 "${reqId}": Skill "orch:${skillName}" 需要前置阶段 "${prereq.name}" 但该阶段尚未初始化。请先通过 workflow 步骤0 初始化。`
        );
      } else {
        blocks.push(
          `工作流 "${reqId}": Skill "orch:${skillName}" 需要前置阶段 "${prereq.name}" 完成（当前状态: ${prereqInStages.status}）。请先完成前置阶段。`
        );
      }
    }

    // 检查必要产出文件
    const missing = checkOutputsExist(reqId, prereq.outputs);
    if (missing.length > 0) {
      blocks.push(
        `工作流 "${reqId}": 前置阶段产物缺失: ${missing.join(', ')}`
      );
    }
  }

  if (blocks.length > 0) {
    const reason = [
      '[STAGE-GATE] 阶段门控阻断 — 前置阶段未完成：',
      ...blocks,
      '请先完成前置阶段后再调用此 Skill。使用 /start-dev 恢复中断的工作流。',
    ].join('\n');
    process.stdout.write(JSON.stringify({ decision: 'deny', reason }));
    return;
  }

  process.stdout.write(JSON.stringify({ decision: 'allow' }));
}

try { main(); } catch (e) {
  // fail-open: on any error, allow the call (避免钩子自身故障阻断工作)
  process.stdout.write(JSON.stringify({ decision: 'allow' }));
}
