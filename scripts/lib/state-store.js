'use strict';
/**
 * Workflow state persistence for orch.
 * Reads/writes .workflow-state.json and .workflow-eval.json.
 */
const fs = require('fs');
const path = require('path');

function readState(workDir) {
  const file = path.join(workDir, '.workflow-state.json');
  try { return JSON.parse(fs.readFileSync(file, 'utf-8')); }
  catch (_) { return null; }
}

function writeState(workDir, state) {
  const file = path.join(workDir, '.workflow-state.json');
  const tmp = file + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(state, null, 2), 'utf-8');
  fs.renameSync(tmp, file);
}

function readEval(workDir) {
  const file = path.join(workDir, '.workflow-eval.json');
  try { return JSON.parse(fs.readFileSync(file, 'utf-8')); }
  catch (_) { return null; }
}

function appendStage(workDir, stageData) {
  const evalData = readEval(workDir) || { stages: [], events: [] };
  evalData.stages.push({ ...stageData, timestamp: new Date().toISOString() });
  const file = path.join(workDir, '.workflow-eval.json');
  fs.writeFileSync(file, JSON.stringify(evalData, null, 2), 'utf-8');
}

function getCurrentStage(cwd) {
  const workDir = cwd || process.env.PWD || process.cwd();
  const state = readState(workDir);
  if (state && state.current_stage) return state.current_stage;
  return '';
}

function updateStageTokens(workDir, stageTokens) {
  const evalData = readEval(workDir);
  if (!evalData || !evalData.stages) return false;
  const currentStage = getCurrentStage(workDir);
  if (!currentStage) return false;
  // Find the matching stage entry (last one with this stage name)
  for (let i = evalData.stages.length - 1; i >= 0; i--) {
    if (evalData.stages[i].stage === currentStage) {
      evalData.stages[i].actual_tokens = evalData.stages[i].actual_tokens || {};
      Object.assign(evalData.stages[i].actual_tokens, stageTokens);
      // Also update flat fields for backward compat
      if (stageTokens.input_tokens != null) evalData.stages[i].tokens_input = stageTokens.input_tokens;
      if (stageTokens.output_tokens != null) evalData.stages[i].tokens_output = stageTokens.output_tokens;
      const file = path.join(workDir, '.workflow-eval.json');
      fs.writeFileSync(file, JSON.stringify(evalData, null, 2), 'utf-8');
      return true;
    }
  }
  return false;
}

module.exports = { readState, writeState, readEval, appendStage, getCurrentStage, updateStageTokens };
