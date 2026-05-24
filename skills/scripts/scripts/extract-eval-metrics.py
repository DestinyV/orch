#!/usr/bin/env python3
"""从 .workflow-eval.json 提取指标并执行诊断规则，回写 diagnosis 字段"""
import sys, json, os, tempfile, shutil
from datetime import datetime


def safe_load(filepath):
    """安全加载 JSON，返回 (data, error)"""
    if not os.path.isfile(filepath):
        return None, 'File not found'
    if os.path.getsize(filepath) == 0:
        return None, 'File is empty'
    try:
        with open(filepath, encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f'JSON 解析失败: {e}'
    except Exception as e:
        return None, f'读取失败: {e}'


def atomic_write(filepath, data):
    """原子写入：先写临时文件，再替换，防止并发损坏"""
    tmp = filepath + '.tmp'
    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        shutil.move(tmp, filepath)
    except Exception as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise e


def validate_stage_data(stages):
    """校验阶段数据是否有效填充（非空模板）"""
    empty_flags = []
    for s in stages:
        if s.get('status', '') == '':
            empty_flags.append(s['stage'])
    return empty_flags  # 返回未填充的阶段列表


def diagnose(stages, events, summary):
    """执行诊断规则"""
    d = {'bottlenecks': [], 'warnings': [], 'suggestions': []}

    if not stages:
        d['warnings'].append('.workflow-eval.json stages 为空，阶段数据未记录')
        return d

    # 空数据诊断
    empty_stages = validate_stage_data(stages)
    if empty_stages:
        d['warnings'].append(f"阶段 {', '.join(empty_stages)} 数据未填充（status 为空），Token 记录可能丢失")

    # 卡点诊断
    total_hg = sum(s.get('hard_gate_triggers', 0) for s in stages)
    if total_hg >= 3:
        d['bottlenecks'].append(f'HARD-GATE 累计触发 {total_hg} 次，检查前置条件设计')
    for s in stages:
        if s.get('hard_gate_triggers', 0) >= 3:
            d['bottlenecks'].append(f"阶段 {s['stage']} HARD-GATE 触发 {s['hard_gate_triggers']} 次")

    total_ui = sum(s.get('user_interactions', 0) for s in stages)
    if total_ui >= 5:
        d['warnings'].append(f'用户交互 {total_ui} 次，需求可能不够清晰')

    # Agent 诊断
    agents_dispatched = sum(1 for s in stages if s.get('agent', {}).get('dispatched'))
    if agents_dispatched == 0 and len(stages) > 1:
        d['warnings'].append('Agent 派遣=0，主上下文替代 Agent 反模式')
    for s in stages:
        agent = s.get('agent', {})
        if agent.get('retries', 0) >= 2:
            d['warnings'].append(f"阶段 {s['stage']} Agent {agent.get('name','?')} 重试 {agent['retries']} 次")

    # 并行调度诊断
    parallel = [s for s in stages if s.get('stage') in ('test-design', 'design') and s.get('status') == 'done']
    if len(parallel) == 2:
        times = []
        for s in parallel:
            t = s.get('completed_at', '')
            if t:
                try:
                    times.append(datetime.fromisoformat(t))
                except ValueError:
                    pass
        if len(times) == 2 and abs((times[0] - times[1]).total_seconds()) > 10:
            d['warnings'].append('test-design/design 疑似串行执行，未启用并行调度')

    # 覆盖率诊断
    exec_stage = next((s for s in stages if s.get('stage') == 'execute'), {})
    if exec_stage.get('coverage', 0) < 85 and exec_stage.get('coverage', 0) > 0:
        d['warnings'].append(f"覆盖率 {exec_stage['coverage']}% < 85%，TDD 执行不严格")

    # 补偿事件诊断
    compensations = [e for e in events if e.get('event') == 'compensation']
    if compensations:
        d['suggestions'].append(f'自动补偿 {len(compensations)} 次，检查上游 spec 流程完整性')

    # 阶段跳过率
    skipped = [s for s in stages if s.get('status') == 'skipped']
    if len(stages) > 0 and len(skipped) / len(stages) > 0.3:
        d['suggestions'].append(f"阶段跳过率 {len(skipped)/len(stages)*100:.0f}% > 30%，考虑 quick 模式")

    return d


def extract_metrics(eval_file):
    data, error = safe_load(eval_file)
    if error:
        return {'error': error, 'metrics': None, 'diagnosis': {'bottlenecks': [error], 'warnings': [], 'suggestions': []}}

    stages = data.get('stages', [])
    summary = data.get('summary', {})
    events = data.get('events', [])

    # Token 汇总（处理 null/None 值）
    token_input = sum((s.get('tokens', {}) or {}).get('input', 0) or 0 for s in stages)
    token_output = sum((s.get('tokens', {}) or {}).get('output', 0) or 0 for s in stages)

    metrics = {
        'requirement_id': data.get('requirement_id', ''),
        'project_mode': data.get('project_mode', ''),
        'mode': data.get('mode', ''),
        'started_at': data.get('started_at', ''),
        'completed_at': data.get('completed_at', ''),
        'total_duration_sec': data.get('total_duration_sec', 0),
        'tokens': {
            'input_total': token_input,
            'output_total': token_output,
            'grand_total': token_input + token_output,
        },
        'stages_done': summary.get('stages_done', len([s for s in stages if s.get('status') == 'done'])),
        'stages_failed': summary.get('stages_failed', len([s for s in stages if s.get('status') == 'failed'])),
        'stages_skipped': summary.get('stages_skipped', len([s for s in stages if s.get('status') == 'skipped'])),
        'agents_dispatched': sum(1 for s in stages if (s.get('agent') or {}).get('dispatched')),
        'events_total': len(events),
    }

    diagnosis = diagnose(stages, events, summary)
    # 回写
    data['diagnosis'] = diagnosis
    atomic_write(eval_file, data)

    return {'metrics': metrics, 'diagnosis': diagnosis}


if __name__ == '__main__':
    eval_file = sys.argv[1] if len(sys.argv) > 1 else 'orch-spec/default/.workflow-eval.json'
    result = extract_metrics(eval_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
