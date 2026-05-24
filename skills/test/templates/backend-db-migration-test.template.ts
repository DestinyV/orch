# 后端数据库迁移测试模板

> code-test 阶段 3.1 后端集成测试中使用此模板验证数据库迁移

## 测试策略

数据库迁移测试验证以下场景：
1. 正向迁移：从上一版本迁移到当前版本成功
2. 回滚迁移：从当前版本回滚到上一版本成功
3. 数据完整性：迁移后数据无丢失、无损坏
4. 并发安全：多实例同时执行迁移不产生冲突

## Node.js + Knex 模板

```typescript
// tests/migrations/migration-{version}.test.ts

import { knex } from '../../src/db/knex';

describe('数据库迁移 V{version}', () => {
  const tableName = '[table_name]';

  beforeEach(async () => {
    // 清理测试数据库
    await knex.raw(`DROP TABLE IF EXISTS ${tableName} CASCADE`);
  });

  afterAll(async () => {
    await knex.destroy();
  });

  it('正向迁移应该成功创建表', async () => {
    await knex.migrate.latest({
      directory: './migrations',
    });

    const hasTable = await knex.schema.hasTable(tableName);
    expect(hasTable).toBe(true);
  });

  it('表应该包含所有预期列', async () => {
    await knex.migrate.latest({ directory: './migrations' });

    const columns = await knex.schema.table(tableName, (table) => {
      // 获取列信息
    });

    // 验证列存在
    const columnInfo = await knex(tableName).columnInfo();
    expect(columnInfo).toHaveProperty('id');
    expect(columnInfo).toHaveProperty('created_at');
    expect(columnInfo).toHaveProperty('updated_at');
  });

  it('索引应该正确创建', async () => {
    await knex.migrate.latest({ directory: './migrations' });

    // 验证索引存在
    const indexes = await knex.raw(`
      SELECT indexname FROM pg_indexes WHERE tablename = '${tableName}'
    `);
    const indexNames = indexes.rows.map((r: any) => r.indexname);
    expect(indexNames).toContain('idx_[table]_[column]');
  });

  it('回滚迁移应该成功', async () => {
    await knex.migrate.latest({ directory: './migrations' });
    await knex.migrate.rollback({ directory: './migrations' });

    const hasTable = await knex.schema.hasTable(tableName);
    expect(hasTable).toBe(false);
  });

  it('多次迁移应该幂等执行', async () => {
    await knex.migrate.latest({ directory: './migrations' });
    // 第二次执行不应该报错
    await knex.migrate.latest({ directory: './migrations' });

    const hasTable = await knex.schema.hasTable(tableName);
    expect(hasTable).toBe(true);
  });
});
```

## Python + Alembic 模板

```python
# tests/migrations/test_migration_{version}.py

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, create_engine

@pytest.fixture
def alembic_cfg():
    return Config("alembic.ini")

@pytest.fixture
def engine():
    return create_engine("sqlite:///:memory:")

def test_migration_up(alembic_cfg, engine):
    """正向迁移应该成功"""
    command.upgrade(alembic_cfg, "head")

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "[table_name]" in tables

def test_columns_exist(alembic_cfg, engine):
    """表应该包含所有预期列"""
    command.upgrade(alembic_cfg, "head")

    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("[table_name]")]

    assert "id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns

def test_migration_down(alembic_cfg, engine):
    """回滚迁移应该成功"""
    command.upgrade(alembic_cfg, "head")
    command.downgrade(alembic_cfg, "-1")

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "[table_name]" not in tables

def test_data_integrity_after_migration(alembic_cfg, engine):
    """迁移后数据完整性验证"""
    command.upgrade(alembic_cfg, "head")

    # 插入测试数据
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO [table_name] (id, name) VALUES (1, 'test')"),
        )
        conn.commit()

    # 验证数据存在
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM [table_name]")
        )
        assert result.scalar() == 1
```

## Java + Flyway 模板

```java
// src/test/java/com/example/migration/Migration{Version}Test.java

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class Migration{Version}Test {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private Flyway flyway;

    @BeforeEach
    void clean() {
        flyway.clean();
    }

    @Test
    void migrationUp_shouldCreateTable() {
        flyway.migrate();

        Integer count = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '[table_name]'",
            Integer.class
        );
        assertThat(count).isEqualTo(1);
    }

    @Test
    void columns_shouldExist() {
        flyway.migrate();

        assertThat(jdbcTemplate.queryForList(
            "SELECT column_name FROM information_schema.columns WHERE table_name = '[table_name]'"
        )).extracting("column_name")
            .contains("id", "created_at", "updated_at");
    }

    @Test
    void migrationDown_shouldDropTable() {
        flyway.migrate();
        flyway.undo();

        Integer count = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '[table_name]'",
            Integer.class
        );
        assertThat(count).isEqualTo(0);
    }
}
```
