---
name: exception
description: |
  在代码生成中处理异常。自动识别可能失败的操作（数据库查询、RPC调用、JSON解析、类型转换等），
  生成合适的异常代码。通过项目约定扫描发现项目的异常规范（异常类名、错误码格式、错误码文件位置），
  避免硬编码项目特定内容。

  触发条件：后端/全栈项目，代码中存在可能失败的操作
---

# exception

## 职责

在后端/全栈代码生成中，自动识别异常场景，通过扫描项目现有约定生成正确的异常处理代码。

## 何时使用

- 用户明确要求"处理异常"、"添加异常校验"时
- execute 编码阶段，后端/全栈 Task 涉及以下操作时自动触发

## 工作流程

### 步骤1-4: 派遣 exception Agent

**工具优先**：使用 `Skill("orch:scripts")` 调用 `scan-exceptions.py` 扫描项目异常类名/错误码/RPC 模式，替代 AI 逐文件 Grep。

<HARD-GATE>必须通过 Agent 派遣 exception 执行异常处理，不允许主上下文直接扫描和生成。</HARD-GATE>

```bash
Agent(
  subagent_type="orch:exception",
  prompt="
    为项目代码执行异常处理：
    - 项目源码: src/
    - 当前 Task 上下文: 需要异常处理的文件路径
    
    执行步骤：
    1. 项目约定扫描：异常类名/错误码格式/RPC调用模式/模块划分（禁止硬编码）
    2. 异常场景识别：数据库查询/RPC调用/JSON解析/参数校验/并发锁冲突
    3. 错误码查询与创建：先查现有错误码→再创建新错误码→按module维护
    4. 生成异常代码：使用扫描发现的类名+查询的错误码+正确的import
    
    详见 references/exception-pattern-discovery.md
  ",
  run_in_background=false
)
```

## 特殊场景处理

### RPC/外部服务调用

当识别到 RPC 调用时，自动使用远程异常（RR）而非业务异常：

```java
// 外部接口调用 → 使用远程异常
BaseResponse<Res> response = client.call(request);
// 如果 response.getCode() != 0，抛出远程异常
```

### 数据不存在检查

```java
// 查询返回 null → 业务异常
Entity entity = dao.queryById(id);
if (entity == null) {
    throw new BizException("错误码");
}
```

### 参数校验

```java
// 参数非法 → 参数异常
if (!StringUtils.hasText(name)) {
    throw new ParamException("错误码");
}
```

### JSON/类型转换

```java
// JSON 解析失败 → 系统异常
try {
    JsonNode node = mapper.readTree(jsonStr);
} catch (Exception e) {
    throw new SystemException("错误码");
}
```

## 关键约束

<HARD-GATE>禁止硬编码项目特定异常类名或错误码格式，必须通过扫描动态发现</HARD-GATE>

1. 先用现有错误码，避免重复
2. RPC 调用一律用远程异常
3. 异常类型按场景选择：业务/参数/系统/远程
4. 零硬编码：所有约定通过扫描发现

## 如何判断异常类型

| 判断条件 | 异常类型 |
|---------|---------|
| 数据库查询结果不符合预期、权限不足、数据不存在 | 业务异常 |
| 用户输入的参数格式不正确、必填字段为空、参数值不在允许范围 | 参数异常 |
| JSON 解析失败、类型转换失败、IO 错误 | 系统异常 |
| RPC/外部服务调用失败 | 远程异常 |

## Output

- `src/` — 添加异常处理后的代码
## 多语言支持

本 Skill 支持多种后端语言的异常处理：

| 语言 | 业务异常 | 参数异常 | 系统异常 | 远程异常 |
|------|---------|---------|---------|---------|
| Java | BizException | ParamException | SystemException | RemoteException |
| TypeScript | BusinessError | ParamError | SystemError | RemoteError |
| Python | BusinessException | ParamException | SystemException | RemoteException |
| Go | BusinessError | ParamError | SystemError | RemoteError |

**注意**：具体异常类名通过项目约定扫描动态发现，上表仅为通用示例。
