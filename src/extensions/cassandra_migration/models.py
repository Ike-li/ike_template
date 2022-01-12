from datetime import datetime

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from extensions.project_config import get_config


class MigrationRecord(Model):
    """migration 记录
    每次使用执行 migrate 命令时都与数据库里已执行过的 migrate id 对比
    """

    __table_name__ = "migration_record"

    project = columns.Text(partition_key=True)
    id = columns.Integer(primary_key=True)
    name = columns.Text()
    created_at = columns.DateTime(default=datetime.utcnow)


def run_migration(migration_module, migration_id, migration_name):
    """执行 migration 操作"""
    # 执行 migration 操作
    migration_module.migrate()
    # 保存记录
    config = get_config()
    MigrationRecord.create(
        project=config.CASSANDRA_KEYSPACE, id=migration_id, name=migration_name
    )
