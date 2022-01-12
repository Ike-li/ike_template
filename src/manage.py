import os

import click

from apps.base import create_app

app = create_app(os.environ.get("STAGE"))


@click.group()
@click.version_option()
def cli():
    """Flask 项目命令行管理工具"""
    click.echo("flask cli")


@cli.command("start")
def start():
    """Run debug server
    在 debug 模式下, 可以在浏览器中访问 API 查看 debug 内容, 须添加 ?_debug:
        http://127.0.0.1:8000/v1/example/?_debug
    """
    from extensions.flask_api.debug import DevToolbar

    DevToolbar(app)
    app.run(host="0.0.0.0", port=app.config.get("PORT"))


@cli.command("sync_db")
def sync_db():
    """同步数据库"""
    from extensions.cassandra_orm.utils import sync_db as _sync_db

    _sync_db(app)


@cli.command("migrate")
def migrate():
    from extensions.cassandra_migration.utils import migrate
    from extensions.cassandra_orm.utils import connect_to_db

    connect_to_db(app)
    migrate()


@cli.command("test")
def test():
    import pytest

    pytest.main(["-s"])


if __name__ == "__main__":
    cli()
