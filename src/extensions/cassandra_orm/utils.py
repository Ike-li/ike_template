def connect_to_db(app):
    """连接到数据库, 用在 flask command 脚本命令中"""
    import os

    from extensions.cassandra_orm.management import DatabaseManagement

    os.environ["CQLENG_ALLOW_SCHEMA_MANAGEMENT"] = "true"
    DatabaseManagement(app, timeout=60).connect()


def sync_db(app):
    """同步数据库, 添加了新的 model 需要加入到这个函数中"""
    import os

    import apps
    from extensions.cassandra_orm.management import DatabaseManagement

    os.environ["CQLENG_ALLOW_SCHEMA_MANAGEMENT"] = "true"

    for module_name in dir(apps):
        if module_name.startswith("__"):
            continue

        if hasattr(getattr(apps, module_name), "models"):
            _models = getattr(getattr(apps, module_name), "models")
            DatabaseManagement(app, timeout=60).sync_db(_models)
