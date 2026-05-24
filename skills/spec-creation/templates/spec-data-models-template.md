# 数据模型定义

> 💡 **交叉引用**：完整的可执行 SQL DDL/DML 脚本见 `sql-ddl.md`（由 code-design 阶段生成）。
> 本文件定义逻辑数据模型，sql-ddl.md 定义物理 SQL 实现。

---

## 关系型数据库（SQL）

### 表: [table_name]

**描述**：[表的主要用途]

| 字段名 | 类型 | 必需 | 约束 | 说明 |
|--------|------|------|------|------|
| id | uuid | Y | PRIMARY KEY | 唯一标识 |
| created_at | timestamp | Y | DEFAULT NOW() | 创建时间 |
| updated_at | timestamp | Y | DEFAULT NOW() ON UPDATE NOW() | 更新时间 |

**索引**：
- PRIMARY KEY: id
- INDEX: [column_name] ([用途说明])

---

## 非关系型数据库（NoSQL）

### 集合: [collection_name]

**描述**：[集合的主要用途]

**文档结构**：
```json
{
  "_id": "ObjectId",
  "createdAt": "ISODate",
  "updatedAt": "ISODate"
}
```

**验证规则**：
- [字段名]: [验证条件]

**索引**：
- _id (自动)
- [字段名] ([用途说明])
