#!/usr/bin/env python3
"""
generate-completion-data.py — 工作流完成报告数据提取器

从 .workflow-eval.json / .workflow-baseline.json / preferences.json 中提取
所有结构化数据，预填 completion-table.md 模板的占位符。

用法:
  python3 generate-completion-data.py orch-spec/{req_id}/.workflow-eval.json

输出: JSON (stdout) — report_data 结构，供 completion-reporter Agent 使用
"""

import json
import os
import sys
from pathlib import Path


# ── 阶段名称映射 ──────────────────────────────────────────────
STAGE_NAMES = {
    "0_workflow_control":     ("0",   "初始化",           "workflow"),
    "0.5_socratic_clarify":   ("0.5", "苏格拉底澄清",     "clarify"),
    "1_spec_creation":        ("1",   "Spec",             "spec"),
    "2_test_design":          ("2",   "Test Design",      "test-design"),
    "3_code_design":          ("3",   "Design",           "design"),
    "3.5_api_contract":       ("3.5", "Contract",         "contract"),
    "4_code_task":            ("4",   "Task",             "task"),
    "5_code_execute":         ("5",   "Execute",          "execute"),
    "5.5_exception_handler":  ("5.5", "Exception",        "exception"),
    "6_code_test":            ("6",   "Test",             "test"),
    "7_spec_archive":         ("7",   "Archive",          "archive"),
    "8_evaluation":           ("8",   "Evaluation",       "evaluation"),
    "9_knowledge_continuum":  ("9",   "Continuous-Learning", "continuous-learning"),
}

# 条件触发阶段（未触发时显示 —）
CONDITIONAL_STAGES = {"0.5", "3.5", "5.5"}

# ── 辅助函数 ──────────────────────────────────────────────────

def safe_read_json(path):
    """安全读取 JSON 文件，不存在则返回 None"""
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def get_plugin_root():
    """获取插件根目录"""
    return os.environ.get("CLAUDE_PLUGIN_ROOT", os.getcwd())


def find_baseline():
    """查找 baseline 文件"""
    root = get_plugin_root()
    baseline_path = os.path.join(root, "orch-spec", "context", ".workflow-baseline.json")
    return safe_read_json(baseline_path)


def find_preferences():
    """查找 preferences 文件"""
    root = get_plugin_root()
    prefs_path = os.path.join(root, "orch-spec", "user-preferences", "preferences.json")
    return safe_read_json(prefs_path)


def find_learnings_md(req_id):
    """统计 learnings.md 条目数"""
    root = get_plugin_root()
    learnings_path = os.path.join(root, "orch-spec", req_id, "context", "learnings.md")
    if not os.path.exists(learnings_path):
        # 尝试项目级 learnings
        learnings_path = os.path.join(root, "orch-spec", "context", "learnings.md")
    if not os.path.exists(learnings_path):
        return 0, []
    try:
        with open(learnings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 统计 ## 标题数作为 learnings 条目数
        import re
        items = re.findall(r'^##\s+.+', content, re.MULTILINE)
        return len(items), [i.strip('# ') for i in items[:10]]
    except (IOError, OSError):
        return 0, []


# ── 主数据提取 ────────────────────────────────────────────────

def extract_stages(eval_data, baseline_data, req_id):
    """从 eval.json 提取阶段数据"""
    stages_out = []
    eval_stages = eval_data.get("stages", [])
    
    # 建立 stage name → record 映射
    stage_map = {}
    for s in eval_stages:
        sn = s.get("stage", "")
        stage_map[sn] = s
    
    for stage_name, (step_num, display_name, skill_name) in STAGE_NAMES.items():
        record = stage_map.get(stage_name, {})
        status = record.get("status", "pending")
        tokens = (record.get("tokens_input", 0) or 0) + (record.get("tokens_output", 0) or 0)
        
        # 耗时：优先 completed_at，其次从 events 推算
        duration_sec = record.get("completed_at", 0) or 0
        duration_min = round(duration_sec / 60, 1) if duration_sec else 0
        
        # 产出概要
        summary = _build_summary(step_num, record, eval_data, req_id)
        
        # 条件阶段未触发 → 标 —
        if step_num in CONDITIONAL_STAGES and status in ("pending", "skipped", ""):
            status = "—"
        
        # 状态显示
        if status == "done":
            gate_triggers = record.get("hard_gates", [])
            agent_status = record.get("agent", {}).get("status", "done") if isinstance(record.get("agent"), dict) else "done"
            if gate_triggers or agent_status == "retry":
                display_status = "⚠️"
            else:
                display_status = "✅"
        elif status == "failed":
            display_status = "❌"
        elif status == "—":
            display_status = "—"
        elif status in ("in_progress",):
            display_status = "⏳"
        else:
            display_status = "—" if step_num in CONDITIONAL_STAGES else "⏳"
        
        # Agent 名称
        agent_name = ""
        agent_info = record.get("agent", {})
        if isinstance(agent_info, dict):
            agent_name = agent_info.get("name", "")
        if not agent_name and record.get("agents"):
            agent_names = [a.get("name", "") for a in record.get("agents", [])]
            agent_name = " + ".join(filter(None, agent_names))
        
        stages_out.append({
            "step": step_num,
            "name": display_name,
            "skill": skill_name,
            "agent": agent_name,
            "status": display_status,
            "tokens": tokens,
            "duration_min": duration_min,
            "summary": summary,
        })
    
    return stages_out


def _build_summary(step_num, record, eval_data, req_id):
    """为每个阶段生成产出概要文本"""
    root = get_plugin_root()
    req_dir = os.path.join(root, "orch-spec", req_id)
    
    summaries = {
        "0":   f"project_mode={eval_data.get('req_id', '')[:20]}",
        "0.5": "澄清报告" if record.get("status") == "done" else "跳过",
        "1":   "规范文档已生成",
        "2":   "测试模板+fixtures",
        "3":   "架构蓝图",
        "3.5": "接口契约" if record.get("status") == "done" else "跳过(fullstack-only)",
        "4":   "任务清单(DAG无环)",
        "5":   "TDD实现+review",
        "5.5": "异常处理代码生成" if record.get("status") == "done" else "—",
        "6":   "测试报告",
        "7":   "已合并到主规范库",
        "8":   "诊断报告+baseline对比",
        "9":   "learnings+规则更新",
    }
    
    base = summaries.get(step_num, "")
    
    # 尝试获取更精确的产物统计
    if step_num == "5":
        # 统计 execution 报告
        report_path = os.path.join(req_dir, "execution", "execution-report.md")
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                import re
                completed = len(re.findall(r'✅|PASS|passed', content))
                total = len(re.findall(r'Task[-\s]?\d+', content))
                if total > 0:
                    base = f"{completed}/{total} Task完成"
            except (IOError, OSError):
                pass
    
    if step_num == "9":
        learnings_count, _ = find_learnings_md(req_id)
        prefs = find_preferences()
        rules_count = 0
        if prefs:
            rules = prefs.get("optimization", {}).get("rules", [])
            rules_count = len([r for r in rules if r.get("status") == "active"])
        base = f"{learnings_count} learnings + {rules_count} 优化规则"
    
    return base


def extract_efficiency(eval_data, baseline_data, stages_out):
    """提取效率评估数据"""
    # Token 分布
    token_dist = []
    for s in stages_out:
        if s["step"] in CONDITIONAL_STAGES and s["status"] == "—":
            continue
        total_tokens = sum(x["tokens"] for x in stages_out if not (x["step"] in CONDITIONAL_STAGES and x["status"] == "—"))
        pct = round(s["tokens"] / total_tokens * 100, 1) if total_tokens > 0 else 0
        
        bl_tokens = 0
        deviation = 0
        if baseline_data:
            bl_stage = baseline_data.get("stages", {}).get(s.get("stage_name", ""), {})
            bl_tokens = bl_stage.get("avg_tokens", 0)
            if bl_tokens > 0:
                deviation = round((s["tokens"] - bl_tokens) / bl_tokens * 100, 1)
        
        token_dist.append({
            "stage": s["name"],
            "tokens": s["tokens"],
            "pct": pct,
            "baseline": bl_tokens,
            "deviation": deviation,
            "diagnosis": _deviation_label(deviation) if abs(deviation) > 10 else "",
        })
    
    total_tokens = sum(x["tokens"] for x in stages_out)
    total_duration = sum(x["duration_min"] for x in stages_out)
    
    # 关键指标
    bl_total_tokens = 0
    bl_total_duration = 0
    bl_gates = 0
    bl_interventions = 0
    if baseline_data:
        bl_total = baseline_data.get("project_level", {})
        bl_total_tokens = bl_total.get("avg_total_tokens", 0)
        bl_total_duration = bl_total.get("avg_duration_sec", 0) / 60
        bl_gates = bl_total.get("avg_gate_triggers", 0)
        bl_interventions = bl_total.get("avg_user_interventions", 0)
    
    gate_triggers = sum(len(s.get("hard_gates", [])) for s in eval_data.get("stages", []))
    interventions = len([e for e in eval_data.get("events", []) if e.get("type") == "user_intervention"])
    
    token_dev = round((total_tokens - bl_total_tokens) / bl_total_tokens * 100, 1) if bl_total_tokens > 0 else 0
    dur_dev = round((total_duration - bl_total_duration) / bl_total_duration * 100, 1) if bl_total_duration > 0 else 0
    gate_dev = round((gate_triggers - bl_gates) / bl_gates * 100, 1) if bl_gates > 0 else 0
    int_dev = round((interventions - bl_interventions) / bl_interventions * 100, 1) if bl_interventions > 0 else 0
    
    diagnosis = eval_data.get("diagnosis", {})
    score = diagnosis.get("score", 0)
    
    key_metrics = [
        {"name": "总 Token", "actual": total_tokens, "baseline": bl_total_tokens, "deviation": token_dev, "grade": _grade(token_dev)},
        {"name": "总耗时(min)", "actual": round(total_duration, 1), "baseline": round(bl_total_duration, 1), "deviation": dur_dev, "grade": _grade(dur_dev)},
        {"name": "GATE 触发", "actual": gate_triggers, "baseline": bl_gates, "deviation": gate_dev, "grade": _grade(gate_dev)},
        {"name": "用户干预", "actual": interventions, "baseline": bl_interventions, "deviation": int_dev, "grade": _grade(int_dev)},
        {"name": "综合评分", "actual": f"{score}/100", "baseline": "—", "deviation": 0, "grade": _score_grade(score)},
    ]
    
    bottlenecks = diagnosis.get("bottlenecks", [])
    
    return {
        "token_distribution": token_dist,
        "key_metrics": key_metrics,
        "bottlenecks": bottlenecks,
        "total_tokens": total_tokens,
        "total_duration_min": round(total_duration, 1),
    }


def extract_learnings(eval_data, req_id):
    """提取知识沉淀数据"""
    learnings = eval_data.get("learnings", [])
    count, md_items = find_learnings_md(req_id)
    
    # 分类 learnings
    categorized = []
    for l in learnings:
        source = l.get("source", "未知")
        phase = l.get("phase", "")
        trigger = l.get("trigger", "")
        action = l.get("action", "")
        categorized.append({
            "source": source,
            "detail": f"[{phase}] {trigger} → {action}" if phase else trigger,
        })
    
    return {
        "count": max(count, len(learnings)),
        "items": categorized,
    }


def extract_rules_changes(prefs):
    """提取优化规则变化"""
    if not prefs:
        return []
    
    rules = prefs.get("optimization", {}).get("rules", [])
    changes = []
    for r in rules:
        evolution = r.get("evolution", {})
        changes.append({
            "rule_id": r.get("id", "unknown"),
            "action": "active" if r.get("status") == "active" else r.get("status", "unknown"),
            "confidence": evolution.get("confidence", 0),
            "reason": r.get("hypothesis", {}).get("problem", "")[:80],
        })
    
    return changes


def extract_recommendations(eval_data):
    """提取优化建议"""
    diagnosis = eval_data.get("diagnosis", {})
    recommendations = diagnosis.get("recommendations", [])
    
    # 自动生成补充建议
    result = []
    for i, rec in enumerate(recommendations):
        priority = "⚠️ 高" if i == 0 else ("💡 中" if i == 1 else "ℹ️ 低")
        result.append({
            "priority": priority,
            "recommendation": rec,
            "basis": "",
        })
    
    # 如果 diagnosis 没有 recommendations，从偏差中自动生成
    if not result:
        deviation_data = diagnosis.get("deviation", {})
        items = deviation_data.get("items", [])
        for i, item in enumerate(items[:3]):
            priority = "⚠️ 高" if i == 0 else ("💡 中" if i == 1 else "ℹ️ 低")
            result.append({
                "priority": priority,
                "recommendation": f"{item.get('source', '')} 偏差 {item.get('deviation', 0)}%，建议优化",
                "basis": f"偏差 {item.get('deviation', 0)}%, 基线 {item.get('baseline', 0)}",
            })
    
    return result


def _deviation_label(dev):
    if abs(dev) <= 10:
        return "正常"
    elif abs(dev) <= 30:
        return "注意"
    else:
        return "异常"


def _grade(dev):
    if abs(dev) <= 10:
        return "🟢"
    elif abs(dev) <= 30:
        return "🟡"
    else:
        return "🔴"


def _score_grade(score):
    if score >= 85:
        return "🟢"
    elif score >= 60:
        return "🟡"
    else:
        return "🔴"


# ── 入口 ───────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: generate-completion-data.py <eval.json path>"}, ensure_ascii=False))
        sys.exit(1)
    
    eval_path = sys.argv[1]
    eval_data = safe_read_json(eval_path)
    if not eval_data:
        print(json.dumps({"error": f"eval.json not found or invalid: {eval_path}"}, ensure_ascii=False))
        sys.exit(1)
    
    # 从路径推断 req_id
    req_id = Path(eval_path).parent.name if "orch-spec" in eval_path else "unknown"
    
    baseline_data = find_baseline()
    prefs = find_preferences()
    
    # 提取数据
    stages_out = extract_stages(eval_data, baseline_data, req_id)
    efficiency = extract_efficiency(eval_data, baseline_data, stages_out)
    learnings = extract_learnings(eval_data, req_id)
    rules_changes = extract_rules_changes(prefs)
    recommendations = extract_recommendations(eval_data)
    
    # 总计
    completed = sum(1 for s in stages_out if s["status"] in ("✅", "⚠️"))
    total_stages = len(stages_out)
    agent_count = len(set(s["agent"] for s in stages_out if s["agent"]))
    
    report_data = {
        "req_id": eval_data.get("req_id", req_id),
        "project_mode": eval_data.get("project_mode", "unknown"),
        "stages": stages_out,
        "totals": {
            "completed": completed,
            "total": total_stages,
            "agents": agent_count,
            "tokens": efficiency["total_tokens"],
            "duration_min": efficiency["total_duration_min"],
        },
        "efficiency": efficiency,
        "learnings": learnings,
        "rules_changes": rules_changes,
        "recommendations": recommendations,
        "baseline_available": baseline_data is not None,
        "generated_at": __import__('datetime').datetime.now().isoformat(),
    }
    
    print(json.dumps(report_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
