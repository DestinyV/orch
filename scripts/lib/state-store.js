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

module.exports = { readState, writeState, readEval, appendStage };
