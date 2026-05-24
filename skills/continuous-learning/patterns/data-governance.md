# 数据治理模式

## 理论框架

数据治理关注数据的生命周期（创建→使用→归档→销毁）、一致性保障、性能优化和合规要求。

## 数据建模原则

| 原则 | 说明 | 常见违反表现 |
|------|------|------------|
| **单一真相源** | 每个数据实体只有一个权威存储 | 多处冗余、数据不一致 |
| **生命周期管理** | 明确数据从创建到销毁的完整路径 | 无归档策略、历史数据无限增长 |
| **审计追溯** | 关键变更可追溯操作人和时间 | 无法追踪数据变更原因 |
| **最小权限** | 数据访问按需授权 | 过度授权导致数据泄露风险 |

## 存储选型指南

| 场景 | 推荐存储 | 理由 |
|------|---------|------|
| 结构化事务数据 | 关系型数据库（MySQL/PostgreSQL） | ACID、事务支持 |
| 文档/半结构化数据 | 文档数据库（MongoDB） | Schema 灵活 |
| 高频读写缓存 | 内存数据库（Redis） | 低延迟、高吞吐 |
| 全文搜索 | 搜索引擎（Elasticsearch） | 倒排索引、分词 |
| 时序数据 | 时序数据库（InfluxDB） | 时间窗口聚合优化 |

## 常见审计字段

```sql
created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
created_by BIGINT DEFAULT 0,
updated_by BIGINT DEFAULT 0,
is_deleted TINYINT DEFAULT 0,
version INT DEFAULT 0  -- 乐观锁
```

## 历史教训

- 未定义字符集导致乱码（应使用 utf8mb4）
- 金额字段精度不足（DECIMAL(10,2) 不够，需 DECIMAL(16,4)）
- 未建复合索引导致列表查询慢
- 软删除未加唯一索引导致重复数据

## 常见遗漏

1. 未定义数据保留期和归档策略
2. 未考虑并发写入的冲突解决（乐观锁/悲观锁）
3. 未规划数据迁移方案（历史数据处理）
4. 状态字段未加注释说明各值含义
5. 未定义外键级联策略
