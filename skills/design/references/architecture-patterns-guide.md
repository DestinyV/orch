# 架构模式指南

code-design 阶段架构决策参考。

## 理论基础

- **Clean Architecture** (Robert C. Martin)：依赖规则——外层依赖内层，领域层零外部依赖。通过端口/适配器隔离框架和基础设施
- **Hexagonal Architecture** (Alistair Cockburn)：端口-适配器模式，将业务逻辑与外部世界解耦，支持多适配器（HTTP/消息队列/CLI）
- **Layered Architecture** (Buschmann et al.)：层次化分离关注点，上层依赖下层，适合简单 CRUD 应用
- **MVC/MVVM**：表现层模式——MVC 适合服务端渲染，MVVM 适合数据绑定场景

## 架构风格选择

| 风格 | 决策依据 |
|------|---------|
| 分层架构 | 业务逻辑简单（CRUD为主）、团队小、变更频率低 |
| Clean Architecture | 业务逻辑复杂需隔离框架、核心领域需独立测试、长期维护 |
| Hexagonal | 多适配器场景（HTTP+消息+定时任务）、需要替换基础设施 |
| MVC/MVVM | 前端应用，根据数据绑定复杂度选择 |

模型应根据项目复杂度、团队规模和长期维护预期自主选择，不机械套用。
