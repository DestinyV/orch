# 数据库表设计规范

design 阶段 SQL DDL 设计的核心规范。覆盖命名、字段、索引、约束、扩展、反模式。

## 1. 命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 表名 | 复数、小写下划线 | `users`, `order_items` |
| 列名 | 单数、小写下划线 | `user_id`, `created_at` |
| 主键 | 统一 `id` | `id BIGINT PRIMARY KEY` |
| 外键 | `{referenced_table}_id` | `user_id`, `order_id` |
| 关联表 | `{a}_{b}` 按字母序 | `user_role`, `item_tag` |
| 索引 | `idx_{table}_{column}` | `idx_users_email` |
| 唯一键 | `uk_{table}_{column}` | `uk_users_phone` |
| 前缀表 | `log_`, `cache_`, `archive_`, `temp_` | `log_login`, `archive_orders_2025` |

**硬约束**：
- 禁止关键字做表名/列名（`order`、`group`、`key` 等）
- 字符集统一 `utf8mb4`，排序规则 `utf8mb4_unicode_ci`
- 引擎默认 InnoDB（MySQL），WAL 模式（SQLite）

## 2. 字段设计

### 2.1 必备字段

每表必须包含：

```sql
id         BIGINT PRIMARY KEY AUTO_INCREMENT,  -- UUID v7 for distributed
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
deleted_at TIMESTAMP NULL DEFAULT NULL         -- 软删除，不需要时可省略
```

### 2.2 类型选择

| 场景 | 类型 | 禁止 |
|------|------|------|
| 金额/币值 | `DECIMAL(18,4)` | FLOAT, DOUBLE |
| 百分比 | `DECIMAL(5,2)` | FLOAT |
| 状态枚举 | `TINYINT` + CHECK 约束 | VARCHAR 存状态 |
| 布尔值 | `TINYINT(1) NOT NULL DEFAULT 0` | ENUM |
| 短文本(≤255) | `VARCHAR(N)` | TEXT 存短文本 |
| 长文本(>255) | `TEXT` 独立扩展表 | 混在主表 |
| 超长文本(>64KB) | `MEDIUMTEXT` 独立扩展表 | |
| JSON 扩展 | `JSON` (MySQL 5.7+/PG 9.2+) | 序列化字符串 |
| UUID | `CHAR(36)` 或 `BINARY(16)` | VARCHAR(255) |
| IP 地址 | `VARBINARY(16)` | VARCHAR(45) |
| 时间戳 | `TIMESTAMP` / `DATETIME(3)` | 字符串存时间 |

### 2.3 敏感字段隔离

涉及安全合规的字段（密码哈希、token、身份证号、银行卡号）独立安全表：

```sql
CREATE TABLE user_secrets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    refresh_token VARCHAR(512),
    -- 不存 created_at/updated_at，减少元数据泄露
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 2.4 JSON 字段约束

- JSON 列仅存**无查询需求**的扩展属性（如用户偏好、配置项）
- 需要 WHERE/JOIN/ORDER BY 的字段**必须**独立列
- 禁止存业务关键字段到 JSON（订单金额、用户状态、支付流水）
- 虚拟列 + 索引可解部分查询需求，但不推荐作为常规设计

## 3. 索引策略

### 3.1 主键选择

| 场景 | 类型 | 原因 |
|------|------|------|
| 单机 MySQL | `BIGINT AUTO_INCREMENT` | 聚簇索引顺序写，页分裂最小 |
| 分布式/分库分表 | `BIGINT` 雪花算法 | 全局唯一 + 粗略有序 |
| 多区域同步 | `UUID v7` (时间序) | 全局唯一 + 聚簇友好 |

### 3.2 索引原则

```
1. WHERE 条件列 → 索引
2. JOIN 关联列 → 索引
3. ORDER BY 排序列 → 联合索引覆盖
4. 覆盖索引：包含 SELECT 全部列，避免回表
5. 联合索引：区分度高的列在前
6. 最左前缀：查询可以部分使用联合索引
```

### 3.3 禁止索引

| 反模式 | 问题 | 替代 |
|--------|------|------|
| 区分度 < 10% 的单列索引（如 gender） | 近似全表扫描 | 不加 |
| 冗余索引 `(a,b)` 已有，又建 `(a)` | 浪费空间 + 写入代价 | 只留 `(a,b)` |
| 频繁更新的列建索引 | 索引维护成本 > 查询收益 | 评估后决定 |
| OR 条件跨列 | 索引失效 | UNION ALL 重写 |
| 函数/计算包裹列 `WHERE LOWER(name)=x` | 索引失效 | 函数索引或预处理 |

### 3.4 大表变更

生产环境大表（>100万行）DDL 变更：
- MySQL：`pt-online-schema-change` 或 `gh-ost`
- PostgreSQL：`CREATE INDEX CONCURRENTLY`
- 禁止高峰时段直接 ALTER TABLE

## 4. 约束设计

```sql
-- CHECK 约束
ALTER TABLE orders ADD CONSTRAINT ck_amount_positive CHECK (total_amount > 0);

-- UNIQUE 包含软删除（同名未删除才唯一）
CREATE UNIQUE INDEX uk_users_email ON users(email) WHERE deleted_at IS NULL;

-- NOT NULL + DEFAULT
ALTER TABLE orders ALTER COLUMN status SET NOT NULL, ALTER COLUMN status SET DEFAULT 1;

-- 外键级联
ALTER TABLE order_items ADD CONSTRAINT fk_items_order
    FOREIGN KEY (order_id) REFERENCES orders(id)
    ON DELETE CASCADE ON UPDATE CASCADE;
-- 生产环境：外键仅文档声明，不强制创建物理 FK（避免锁升级），由应用层保证
```

### 软删除设计

```sql
deleted_at TIMESTAMP NULL DEFAULT NULL,
-- 所有唯一索引包含 deleted_at
CREATE UNIQUE INDEX uk_users_email_del ON users(email, deleted_at);
-- 查询一律带 deleted_at IS NULL
```

## 5. 扩展性设计

### 5.1 大版本表重构

```sql
-- v1
CREATE TABLE orders (...);
-- v2 表结构变更
CREATE TABLE orders_v2 (LIKE orders INCLUDING ALL);
-- 数据迁移后切换
CREATE VIEW orders AS SELECT * FROM orders_v2;
```

### 5.2 扩展属性

不预留空列（col1..colN），使用 JSON 或扩展表：

```sql
-- 扩展表（需要查询）
CREATE TABLE user_attributes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    attr_key VARCHAR(64) NOT NULL,
    attr_value VARCHAR(512) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
-- JSON 列（仅存储展示）
ALTER TABLE users ADD COLUMN metadata JSON;
```

### 5.3 分表策略

| 方式 | 适用场景 | 示例 |
|------|---------|------|
| 按时间 | 日志/流水表 | `log_login_202501` |
| 按 ID 哈希 | 大表均匀分布 | `orders_0` ~ `orders_15` |
| 按业务键 | 租户隔离 | `tenant_001_users` |

### 5.4 多租户

所有业务表含 `tenant_id BIGINT NOT NULL`，使用 RLS 或应用层 WHERE 隔离。

## 6. 业务适配模式

### 6.1 审计日志

```sql
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(64) NOT NULL,
    record_id BIGINT NOT NULL,
    action CHAR(1) NOT NULL,  -- C/U/D
    changed_by BIGINT,
    old_data JSON,
    new_data JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_table_record (table_name, record_id)
);
```

### 6.2 多语言

```sql
CREATE TABLE i18n (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(64) NOT NULL,
    record_id BIGINT NOT NULL,
    locale CHAR(5) NOT NULL,  -- zh-CN, en-US
    field_name VARCHAR(64) NOT NULL,
    translated_text TEXT NOT NULL,
    UNIQUE KEY uk_i18n (table_name, record_id, locale, field_name)
);
```

### 6.3 排序/拖拽

```sql
-- 用浮点间隙（Gap method），避免全量重排
ALTER TABLE items ADD COLUMN position DOUBLE NOT NULL DEFAULT 0;
-- 插入中间：position = (prev.position + next.position) / 2
```

### 6.4 树形结构

```sql
-- 闭包表（Closure Table），查询快、维护略复杂
CREATE TABLE category_tree (
    ancestor BIGINT NOT NULL,
    descendant BIGINT NOT NULL,
    depth INT NOT NULL DEFAULT 0,
    PRIMARY KEY (ancestor, descendant),
    FOREIGN KEY (ancestor) REFERENCES categories(id),
    FOREIGN KEY (descendant) REFERENCES categories(id)
);
```

## 7. 反模式清单

| 反模式 | 问题 | 正确做法 |
|--------|------|---------|
| FLOAT/DOUBLE 存金额 | 精度丢失，`0.1+0.2≠0.3` | `DECIMAL(18,4)` |
| 逗号分隔多值 `"1,2,3"` | 无法索引、无法 JOIN | 关联表 `item_tags` |
| EAV 表（Entity-Attribute-Value） | 查询灾难、无法约束 | JSON 列 / 独立扩展表 |
| 预留字段 `col1..colN` | 语义不明、浪费空间 | JSON `metadata` 列 |
| 单表 >50 列 | 职责混乱、行迁移 | 垂直拆分 |
| 无主键 / 联合主键 | 写入性能差 | 独立自增 `id` |
| TEXT/BLOB 混在主表 | Row Overflow 导致全表扫描变慢 | 独立扩展表 `xxx_contents` |
| VARCHAR 无长度 / 过大长度 | 隐含性能风险 | 精确评估上限 |
| 密码明文存储 | 安全合规风险 | bcrypt/argon2 哈希 + 独立安全表 |
| 软删除不用唯一索引 | 同名未删除可重复 | `WHERE deleted_at IS NULL` |
