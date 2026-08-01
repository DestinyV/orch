    {
      "path": "scripts",
      "name": "根级脚本",
      "files": [
        {"path": "scripts/generate-completion-data.py", "role": "完成报告数据提取", "used_by": "agents/completion-reporter.md"},
        {"path": "scripts/sync-prompt-defense.py", "role": "Prompt Defense同步", "issue": "F5 重复插入bug"},
        {"path": "scripts/__pycache__/generate-completion-data.cpython-312.pyc", "role": "编译缓存", "issue": "F11 已提交git"}
      ],
      "dependencies": [],
      "api_routes": []
    },
    {
      "path": "skills",
      "name": "Skills 指令(22个)",
      "files": [
        {"path": "skills/workflow/SKILL.md", "role": "入口编排(13步)"},
        {"path": "skills/workflow/references/agent-dispatch-code.md", "role": "Agent派遣代码"},
        {"path": "skills/workflow/references/flow-execution-reference.md", "role": "阶段输入/输出契约"},
        {"path": "skills/workflow/references/context-inheritance-protocol.md", "role": "上下文继承"},
        {"path": "skills/design/SKILL.md", "role": "设计", "issue": "F1 project-map.md误引用"},
        {"path": "skills/execute/SKILL.md", "role": "TDD执行"},
        {"path": "skills/test/SKILL.md", "role": "测试闭环"},
        {"path": "skills/continuous-learning/SKILL.md", "role": "知识复利"},
        {"path": "skills/exception/SKILL.md", "role": "异常处理"},
        {"path": "skills/contract/SKILL.md", "role": "接口契约"},
        {"path": "skills/ralph-loop/SKILL.md", "role": "自主循环"}
      ],
      "dependencies": ["agents", "scripts"],
      "api_routes": []
    }
  ],
  "api_routes": [],
  "data_models": [
    {"name": "workflow-state", "path": "orch-spec/{req_id}/.workflow-state.json", "schema_ref": "skills/workflow/references/workflow-data-schema.md"},
    {"name": "workflow-eval", "path": "orch-spec/{req_id}/.workflow-eval.json", "role": "效果评估+Token"},
    {"name": "baseline-context", "path": "orch-spec/context/.baseline-context.json", "role": "增量探索基线"},
    {"name": "project-map", "path": "orch-spec/{req_id}/req-context/project-map.json", "role": "结构化项目地图"},
    {"name": "preferences-rules", "path": "orch-spec/user-preferences/preferences.json", "role": "优化规则 optimization.rules[]"},
    {"name": "cost-record", "path": "~/.claude/orch-costs/costs.jsonl + usage.db", "role": "成本记录"}
  ],
  "test_targets": []
}
