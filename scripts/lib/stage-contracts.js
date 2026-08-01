'use strict';
/**
 * 阶段契约单一事实源（Stage Contracts）
 *
 * 集中导出 workflow 阶段的顺序映射、产出文件、前置 Skill 要求与豁免清单。
 * workflow-gate.js / stage-gate.js / session-start.js 从此处消费，
 * 消除多处独立维护导致的阶段映射漂移（F10 根因）。
 *
 * 设计原则（北极星）：只约束「流程顺序 / 产出存在 / 派遣完整性」，
 * 不约束模型如何产出。所有 GATE 判定为 guardrail 而非 cage。
 */

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
// 2/3 并行中间产物由 3.5/4 兜底；5.5 为 execute 子过程；8 写 eval.json 由 0 覆盖
const STAGE_OUTPUTS = {
  '0_workflow_control': ['.workflow-state.json', '.workflow-eval.json'],
  '1_spec_creation': ['spec/requirement.md', 'spec/scenarios'],
  '3.5_api_contract': ['contract/contract.md', 'contract/review-report.md'],
  '4_code_task': ['tasks/tasks.md'],
  '5_code_execute': ['execution/execution-report.md'],
  '6_code_test': ['testing/testing-report.md'],
  '7_spec_archive': ['archive-log.md'],
  // continuous-learning 写项目级 context/learnings.md（'..' 归一化到 orch-spec/context/）
  // 'completion-report' 为状态标志伪产出，校验时改查 state.completion_report_generated
  '9_knowledge_continuum': ['../context/learnings.md', 'completion-report'],
};

// Skill → 前置阶段映射（stage-gate 阻断依据）
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

// 豁免 Skill（工具类/辅助类），不参与阶段门控。仅真 Skill 名。
const EXEMPT_SKILLS = [
  'scripts', 'context-budget', 'depth', 'compact', 'cost',
  'ralph-loop', 'using-orch', 'debug', 'req-change', 'spec-migrate',
];

// 命令名（与 Skill 名分离）。PreToolUse matcher=Skill 时命令不会进入门控分支，
// 此处作文档化分离 + 防御（若未来 matcher 扩展）。含新增内部自检命令 self-check。
const EXEMPT_COMMANDS = [
  'checkpoint', 'code-review', 'plan', 'quality-gate',
  'session-resume', 'session-save', 'start-dev', 'cost-report', 'self-check',
];

module.exports = {
  STAGE_ORDER,
  STAGE_OUTPUTS,
  SKILL_PREREQUISITES,
  EXEMPT_SKILLS,
  EXEMPT_COMMANDS,
};
