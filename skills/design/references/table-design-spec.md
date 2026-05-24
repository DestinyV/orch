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
- 字符集统一 `utf8mb4`，排序规则 `utf8mb4_unicode_ci`，必须**建表语句显式声明**
- MySQL 引擎**必须显式** `ENGINE=InnoDB`，不依赖默认值
- 行格式 `ROW_FORMAT=DYNAMIC`（兼容大字段 + 索引）

## 2. 字段设计

### 2.1 必备字段

每表必须包含，且严格遵循类型和约束：

```sql
-- MySQL 标准表（含软删）
id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
deleted_at TIMESTAMP NULL DEFAULT NULL,

-- PostgreSQL
id         BIGSERIAL PRIMARY KEY,
created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
deleted_at TIMESTAMPTZ NULL DEFAULT NULL,

-- 分布式场景 MySQL
id         BIGINT UNSIGNED NOT NULL,  -- 应用层雪花算法赋值
```

**主键硬约束**：
- 必须 `UNSIGNED` | 禁止 `INT`（空间浪费且可能溢位） | 禁止 SIGNED（自增永不赋值负数）
- UNIQUE KEY / PRIMARY KEY 即索引禁止显式创建重复索引

### 2.2 类型选择

| 场景 | 类型 | 禁止 |
|------|------|------|
| 金额/币值 | `DECIMAL(18,4)` | FLOAT, DOUBLE |
| 百分比 | `DECIMAL(5,2)` | FLOAT |
| 状态枚举 | `TINYINT UNSIGNED NOT NULL` + CHECK + COMMENT 文档化 | VARCHAR 存状态、ENUM 类型 |
| 布尔值 | `TINYINT(1) NOT NULL DEFAULT 0` | ENUM |
| 短文本(≤50) | `CHAR(N)` | VARCHAR 浪费长度追踪 |
| 变长文本(≤255) | `VARCHAR(N)` — 精确上限×1.2 余量 | VARCHAR(255) 万能长度、VARCHAR 不设长度 |
| 长文本(>255) | `TEXT` 独立扩展表 `xxx_contents` | 混在主表 |
| 超长文本(>64KB) | `MEDIUMTEXT` 独立扩展表 | |
| JSON 扩展 | `JSON` (MySQL 5.7+/PG 9.2+) | 序列化字符串 |
| UUID | `CHAR(36)` 或 `BINARY(16)` | VARCHAR(255) |
| IP 地址 | `VARBINARY(16)` | VARCHAR(45) |
| 秒级时间 | `TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP` | 字符串/INT 存时间 |
| 毫秒时间 | `DATETIME(3)` | TIMESTAMP 小数秒 |
| 仅日期 | `DATE` | DATETIME |
| 未来时间 | `DATETIME` (避免 2038 问题) | TIMESTAMP |
| 创建/更新 | `TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP` | 应用层手动赋值 |

#### VARCHAR 长度规范

- 禁止 `VARCHAR(255)` 万能兜底 → 评估真实业务上限 × 1.2 取整
- 禁止 `VARCHAR` 不指定长度
- 示例：姓名最大 20 中文 → VARCHAR(64)；邮箱最大 254 → VARCHAR(320)；手机号 11 位 → CHAR(11)

#### TEXT 族约束

- TEXT / MEDIUMTEXT 必须独立 `xxx_contents` 表，1:1 关联主表
- TINYTEXT(255B) ≤ VARCHAR(255) → 一律用 VARCHAR
- LONGTEXT(4GB) → 禁止，存对象存储路径
- TEXT 列不能设 DEFAULT（MySQL 限制）→ 代码层处理

#### ENUM 禁止

| 问题 | 说明 |
|------|------|
| 扩展需 ALTER TABLE | 大表锁表风险 |
| 排序按索引序非字母序 | ORDER BY 结果不可预期 |
| 移植性差 | PostgreSQL 无 ENUM 或行为不同 |
| 替代 | `TINYINT UNSIGNED NOT NULL DEFAULT 1` + CHECK 约束 + COMMENT 完整映射 |

```sql
status TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '状态: 0=无效 1=待审核 2=通过 3=拒绝 4=过期',
CONSTRAINT ck_status CHECK (status BETWEEN 0 AND 4)
```

- 0 保留为「无效」、1 为「默认初始」、正数正常流程
- COMMENT 必须写出完整 `数字=含义` 映射

### 2.3 NOT NULL + DEFAULT 强制

除 `id`（自增）和 `deleted_at`（可为空）外，所有列**NOT NULL 必须配 DEFAULT**：

```sql
-- ✅ 正确
status TINYINT NOT NULL DEFAULT 1,
name VARCHAR(64) NOT NULL DEFAULT '',
amount DECIMAL(18,4) NOT NULL DEFAULT 0.0000,

-- ❌ 错误 — INSERT 省略列时报错 或 隐式默认值不可控
status TINYINT NOT NULL,
name VARCHAR(64) NOT NULL,
```

**NULL 允许列仅限**：`deleted_at`、`remark/description/note`、`parent_id`（顶层为 NULL）、`expired_at`（永不过期为 NULL）。

### 2.4 注释强制

```sql
-- 表级注释
CREATE TABLE users (
  ...
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 列级注释
id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
status TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 1=正常 2=禁用 3=注销',
```

**命名和注释即文档**——禁止裸字段、裸表。

### 2.5 敏感字段隔离

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

### 2.6 JSON 字段约束

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

### 3.2 索引命名强制

| 类型 | 格式 | 示例 |
|------|------|------|
| 普通索引 | `idx_{table}_{col}` | `idx_users_email` |
| 复合索引 | `idx_{table}_{col1}_{col2}`（按列序） | `idx_orders_user_status` |
| 唯一索引 | `uk_{table}_{col}` | `uk_users_phone` |
| 主键 | `PRIMARY KEY (id)` | — |

**禁止自动生成名**（`key_name_2` 无意义）。

### 3.3 索引数量约束

- 单表索引总数 ≤ 5（含主键）
- 复合索引列数 ≤ 3
- 超出需在 table comment 中注明业务原因

### 3.4 索引原则

```
1. WHERE 条件列 → 索引
2. JOIN 关联列 → 索引
3. ORDER BY 排序列 → 联合索引覆盖
4. 覆盖索引：包含 SELECT 全部列，避免回表
5. 联合索引：区分度高的列在前
6. 最左前缀：查询可以部分使用联合索引
7. 长 VARCHAR(>100) → 前缀索引: idx_xxx(col(20))
```

### 3.5 禁止索引行为

| 反模式 | 问题 | 替代 |
|--------|------|------|
| 区分度 < 10% 的单列索引（如 gender） | 近似全表扫描 | 不加 |
| 冗余索引 `(a,b)` 已有，又建 `(a)` | 浪费空间 + 写入代价 | 只留 `(a,b)` |
| 频繁更新的列建索引 | 索引维护成本 > 查询收益 | 评估后决定 |
| OR 条件跨列 | 索引失效 | UNION ALL 重写 |
| 函数/计算包裹列 `WHERE LOWER(name)=x` | 索引失效 | 函数索引或预处理 |
| 隐式类型转换 `WHERE phone=13800138000` | 索引失效 | 字符串列用字符串条件 |
| 负向查询 `NOT IN`/`!=`/`NOT EXISTS` | 多数不走索引 | 等价正向重写或覆盖索引补救 |

### 3.6 大表变更

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
| `id INT` 不加 UNSIGNED | 自增浪费一半主键空间 | `BIGINT UNSIGNED` |
| NOT NULL 无 DEFAULT | INSERT 遗漏列直接报错，隐式默认值不可控 | 所有 NOT NULL 列必须有 DEFAULT |
| 表/列无 COMMENT | 数据字典为空，新人无法理解 | 每表每列强制 COMMENT |
| 依赖默认 ENGINE | 不同环境/版本默认值可能不同 | 显式 `ENGINE=InnoDB` |
| 字符集不显式声明 | 可能继承 Server 级 latin1/其他 | `DEFAULT CHARSET=utf8mb4` |
| ENUM 类型 | ALTER 锁表、排序陷阱、移植差 | TINYINT + CHECK + COMMENT 映射 |

## 8. SQL 查询编写规范

### 8.1 SELECT 约束

```sql
-- ❌ 禁止：SELECT * → 无法用覆盖索引、列变更不可感知
SELECT * FROM users WHERE id = 1;

-- ✅ 正确：明确列名
SELECT id, name, email, status FROM users WHERE id = 1;
```

- **禁止 `SELECT *`** — 覆盖索引失效、浪费网络带宽、列变更不可感知
- 预期返回 > 1000 行必须加 `LIMIT` + 分页
- OLAP 查询加 `/* OLAP */` 注释标识

### 8.2 WHERE 约束

```sql
-- ❌ 禁止：函数包裹 → 索引失效
WHERE YEAR(created_at) = 2025
WHERE LOWER(email) = 'test@test.com'
WHERE phone = 13800138000  -- 隐式类型转换

-- ✅ 正确
WHERE created_at >= '2025-01-01' AND created_at < '2026-01-01'
WHERE email = 'test@test.com'  -- 存入时已统一小写
WHERE phone = '13800138000'
```

- 禁止 `!=` / `NOT IN` / `<>` / `NOT EXISTS`（多数不走索引），优先等价正向重写
- `OR` 跨列 → 改为 `UNION ALL`
- `IN` 子查询 > 100 值 → JOIN 或临时表
- `LIKE '%xxx'` 左模糊 → 禁止（B+Tree 无法定位）

### 8.3 JOIN 约束

- JOIN 表数 ≤ 3，超过 → 拆多步查询/临时表
- **被驱动表 JOIN 列必须有索引**
- 小表驱动大表原则
- 禁止 CROSS JOIN（显式/隐式）
- 禁止 LEFT JOIN + `WHERE right_table.col IS NOT NULL` 伪装 INNER JOIN

### 8.4 分页约束

```sql
-- ❌ 禁止：大偏移量 OFFSET — 越翻越慢
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;

-- ✅ 正确：游标分页（Keyset Pagination）
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;
```

- `LIMIT OFFSET > 10000` 必须改游标分页
- 游标列必须有唯一索引（避免同值重复/遗漏）
- 禁止每页 COUNT(*) 总数 → 缓存 + 定时刷新

### 8.5 聚合/排序约束

- 大表 `COUNT(*)` 禁止实时查 → 汇总统表 / 近似值 / 缓存
- `GROUP BY` 列无索引 → filesort + tmp table → 加索引
- `ORDER BY RAND()` → 禁止 → 应用层随机 ID + LIMIT
- `DISTINCT` + 大结果集 → 评估能否走索引替代

### 8.6 子查询约束

| 禁止 | 替代 |
|------|------|
| SELECT 中依赖子查询（逐行执行 N+1） | JOIN / 窗口函数 |
| `WHERE col IN (子查询)` 非关联 | `INNER JOIN` 改写 |
| `NOT IN (子查询)` 可能含 NULL | `NOT EXISTS` |
| 多层嵌套 > 3 层 | CTE (`WITH` 递归) |

### 8.7 事务约束

- 禁止事务中调用外部服务（HTTP/RPC）→ 锁持有时间不可控
- 禁止长事务 > 5s → 拆批次
- 批量 UPDATE/DELETE > 1000 行 → `LIMIT 1000` + 循环
- `SELECT ... FOR UPDATE` 禁止范围锁过大 → 精确主键

### 8.8 EXPLAIN 强制

**所有非单表主键 SQL 必须 EXPLAIN 验证：**

```sql
EXPLAIN SELECT ...;
```

| type 值 | 含义 | 允许 |
|---------|------|------|
| `ALL` | 全表扫描 | ❌ 生产禁止（< 100 行参考表除外） |
| `index` | 全索引扫描 | ❌ 禁止（= 另一种全扫描） |
| `range` | 索引范围扫描 | ✅ |
| `ref` / `eq_ref` | 索引查找 | ✅ |
| `const` | 主键单行 | ✅ |

检查项：`type`（ALL/index=禁止）、`key`（NULL=未走索引→禁止）、`rows`（过大→加 LIMIT 或分页）、`Extra`（Using filesort/Using temporary→优化）。
