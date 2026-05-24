# SQL DDL 模板

> code-design 阶段生成 SQL 文件的模板

## 输出目录

`spec-dev/{req}/design/sql/`

## 模板结构

```sql
-- 场景：{scenario_name}
-- 生成日期：{date}
-- SQL 方言：{dialect}

-- 1. 创建表
CREATE TABLE {table_name} (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    {columns...}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 索引
CREATE INDEX idx_{table}_{column} ON {table}({column});

-- 3. 外键
ALTER TABLE {table} ADD CONSTRAINT fk_{table}_{ref}
    FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column}) ON DELETE CASCADE;

-- 4. 回滚脚本（注释）
-- DROP TABLE IF EXISTS {table_name};
```
