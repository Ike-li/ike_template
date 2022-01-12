"""
migrate 流程:
1. 使用 sync_db 命令同步数据库, 尽量保证对数据库的修改不影响这个版本的服务
2. 部署新版本的服务, 需要做好数据库修改的处理, 比如添加字段: cassandra 添加的字段默认值为 null, 需要在代码中做好 None 值的处理
3. 执行 migrate, 迁移之前的数据记录

migration 脚本:
1. 添加脚本, 格式为: 0002_yyy.py
2. migration 函数:
    def migrate():
        result = MigrationResult()
        # 记录 migration 结果
        result.append({})
        return result
"""
import importlib
import pkgutil

import click
from cassandra.cqlengine import management

import migrations
from extensions.cassandra_migration.models import (
    MigrationRecord,
    run_migration,
)
from extensions.project_config import get_config


def migrate():
    """
    migration 入口流程:
    1. 获取所有没有执行过的 migration 脚本
    2. 依次执行 migration 脚本
    """
    # 更新 MigrationRecord 表
    management.sync_table(MigrationRecord)

    # 已经执行过的 migrate id 记录
    config = get_config()
    migrated_record = set(
        MigrationRecord.objects.filter(project=config.CASSANDRA_KEYSPACE
                                      ).values_list("id", flat=True)
    )
    unexecuted_migrations = get_newest_migration(migrated_record)

    # 执行 migration
    for index, migration_module in enumerate(unexecuted_migrations):
        migration_name = migration_module.__name__
        run_migration(
            migration_module=migration_module,
            migration_id=int(migration_name.split(".")[-1][:4]),
            migration_name=migration_module.__name__,
        )
        click.echo(f"Applied migration: {migration_name}")

    click.echo("Migrations completed")


def get_newest_migration(migrated_record):
    """获取没有执行过的 migration 脚本"""
    # 获取最新的 migration 模块
    unexecuted_migrations = list()
    for module in pkgutil.iter_modules(migrations.__path__):
        # 跳过 example
        if "example" in module.name:
            continue
        if len(module.name) < 4:
            continue
        if module.name[:4].isdigit():
            module_id = int(module.name[:4])
            if module_id not in migrated_record:
                unexecuted_migrations.append(
                    importlib.import_module("migrations." + module.name)
                )
    return unexecuted_migrations
