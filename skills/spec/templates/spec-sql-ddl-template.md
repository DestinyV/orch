# SQL DDL/DML 脚本

> 由 spec-creation 阶段生成（needs-database=是 时）
> SQL 方言：[mysql | postgresql | sqlite | sqlserver]
> 关联数据模型：[data-models.md](./data-models.md)

---

## 第 1 节：DDL（数据定义语言）

### 1.1 新增表

> 每个 CREATE TABLE 后附带回滚语句

```sql
-- 表: [table_name]
-- 描述: [表的主要用途]
CREATE TABLE [table_name] (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,  -- MySQL
  -- id BIGSERIAL PRIMARY KEY,           -- PostgreSQL
  -- [字段定义]
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='[表说明]';

-- ROLLBACK: DROP TABLE IF EXISTS [table_name];
```

### 1.2 现有表变更

```sql
-- 添加列: [table_name].[column]
ALTER TABLE [table_name] ADD COLUMN [column] [type] [constraints] COMMENT '[说明]';
-- ROLLBACK: ALTER TABLE [table_name] DROP COLUMN [column];

-- 添加索引
ALTER TABLE [table_name] ADD INDEX idx_[table]_[column] ([column]);
-- ROLLBACK: ALTER TABLE [table_name] DROP INDEX idx_[table]_[column];
```

### 1.3 索引和约束

```sql
-- 唯一约束
ALTER TABLE [table_name] ADD CONSTRAINT uk_[table]_[column] UNIQUE ([column]);
-- ROLLBACK: ALTER TABLE [table_name] DROP INDEX uk_[table]_[column];

-- 外键约束
ALTER TABLE [table_name] ADD CONSTRAINT fk_[table]_[column]
  FOREIGN KEY ([column]) REFERENCES [ref_table]([ref_column]);
-- ROLLBACK: ALTER TABLE [table_name] DROP FOREIGN KEY fk_[table]_[column];
```

---

## 第 2 节：DML（数据操作语言）

### 2.1 种子数据

```sql
-- 插入初始数据: [table_name]
INSERT INTO [table_name] ([column1], [column2], [created_at], [updated_at])
VALUES
  ('value1', 'value2', NOW(), NOW());
-- ROLLBACK: DELETE FROM [table_name] WHERE [column1] = 'value1';
```

### 2.2 数据迁移

```sql
-- 数据迁移: [描述]
UPDATE [table_name] SET [column] = [expression] WHERE [condition];
-- ROLLBACK: UPDATE [table_name] SET [column] = [original_value] WHERE [condition];
```

### 2.3 数据清理

```sql
-- 清理过期数据: [描述]
DELETE FROM [table_name] WHERE [condition];
-- ROLLBACK: （数据清理操作通常不可回滚，需提前备份）
```

---

## 第 3 节：执行顺序说明

| 序号 | 脚本类型 | 描述 | 预估耗时 | 是否需要停机 |
|------|---------|------|---------|-------------|
| 1 | DDL - 表变更 | 新增列和索引 | [X]min | [是/否] |
| 2 | DDL - 新表 | 创建新表 | [X]min | 否 |
| 3 | DML - 数据迁移 | 历史数据迁移 | [X]min | 否 |
| 4 | DML - 种子数据 | 插入初始数据 | [X]min | 否 |

**执行前置条件**：
- [ ] 数据库备份已完成
- [ ] 回滚脚本已验证
- [ ] 执行窗口已确认

---

## 第 4 节：回滚 SQL

> 按执行顺序的**逆序**执行回滚语句

### 回滚步骤

| 序号 | 回滚操作 | 正向操作对应 |
|------|---------|-------------|
| 1 | 删除种子数据 | 第 2.1 节 |
| 2 | 撤销数据迁移 | 第 2.2 节 |
| 3 | 删除新表 | 第 1.1 节 |
| 4 | 恢复表结构变更 | 第 1.2 节 |

```sql
-- 回滚第 2.1 节：删除种子数据
DELETE FROM [table_name] WHERE [column1] IN ('value1', 'value2');

-- 回滚第 1.2 节：删除新增列
ALTER TABLE [table_name] DROP COLUMN [column];

-- 回滚第 1.1 节：删除新表
DROP TABLE IF EXISTS [table_name];
```
