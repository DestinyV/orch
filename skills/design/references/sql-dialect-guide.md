# SQL 方言对照指南

design 阶段数据库方言检测参考。

## 理论基础

- **SQL 标准与方言差异**：SQL:2011 定义了核心标准，但各数据库在数据类型、DDL 语法、分页方式、日期处理上存在差异。选择方言后不可混合使用
- **方言检测原则**：优先从项目现有配置和迁移文件推断，而非主观选择——保持与现有数据库一致

## 检测优先级

1. 项目迁移文件中的方言特征词（如 `SERIAL` → PostgreSQL、`AUTO_INCREMENT` → MySQL）
2. 配置文件（`ormconfig.json`、`database.yml` 等）
3. 无法检测时使用 AskUserQuestion 确认，不假设默认值

## 常用差异速查

| 特性 | MySQL | PostgreSQL | SQLite |
|------|-------|-----------|--------|
| 自增主键 | `AUTO_INCREMENT` | `SERIAL` | `INTEGER PRIMARY KEY` |
| 字符串类型 | `VARCHAR(n)` | `VARCHAR(n)` | `TEXT` |
| 布尔类型 | `TINYINT(1)` | `BOOLEAN` | `INTEGER` |
| 日期类型 | `DATETIME` | `TIMESTAMP` | `TEXT` |
| 分页 | `LIMIT offset, count` | `LIMIT count OFFSET offset` | `LIMIT count OFFSET offset` |

详细的 DDL 生成模板见 `templates/sql-ddl-template.md`。
