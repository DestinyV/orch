'use strict';
/**
 * 判定函数库（verdict.js）
 *
 * 集中提供覆盖率/流转率/规则自决的判定逻辑，支撑插件自检（self-check）
 * 与 TDD 闭环验证。设计原则（北极星）：判定只"评"不"堵"，服务能力增强。
 */

const COVERAGE_THRESHOLD = 85;

/**
 * 覆盖率判定——以实测值为准，不接受自我报告。
 * @param {number} claimed 声称值
 * @param {number} actual 实测值
 * @param {number} [threshold] 阈值，默认 85
 * @returns {'VERIFIED'|'PARTIAL'}
 */
function judgeCoverage(claimed, actual, threshold = COVERAGE_THRESHOLD) {
  return actual >= threshold ? 'VERIFIED' : 'PARTIAL';
}

/**
 * 比率达标判定（流转率/达标率/恢复率）。
 * @param {number} value 实测值
 * @param {number} threshold 阈值
 * @returns {{pass: boolean, value: number, threshold: number}}
 */
function judgeRate(value, threshold) {
  return { pass: value >= threshold, value, threshold };
}

// 规则自决（auto-resolve）四类：自动补偿继续
const AUTO_RESOLVE_CASES = ['compile failure', 'test failure', 'missing file', 'step retry'];
// 白名单人工（pause-for-human）四类：暂停等人工（全小写，与 toLowerCase 输入比较）
const PAUSE_FOR_HUMAN_CASES = [
  'requirement conflict', 'acceptance uncertain', 'hard-gate block', 'cross-repo change',
];

/**
 * 智能 gate 裁决——按 errorType 判定自动补偿或暂停人工。
 * @param {string} errorType 错误类型
 * @returns {'auto-resolve'|'pause-for-human'|'unknown'}
 */
function judgeAutoResolve(errorType) {
  const e = (errorType || '').toLowerCase();
  if (AUTO_RESOLVE_CASES.includes(e)) return 'auto-resolve';
  if (PAUSE_FOR_HUMAN_CASES.includes(e)) return 'pause-for-human';
  return 'unknown';
}

module.exports = {
  judgeCoverage,
  judgeRate,
  judgeAutoResolve,
  COVERAGE_THRESHOLD,
  AUTO_RESOLVE_CASES,
  PAUSE_FOR_HUMAN_CASES,
};
