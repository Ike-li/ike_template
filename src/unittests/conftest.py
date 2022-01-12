"""
注意:

这个文件会在 flask_template 升级的时候被覆盖，请避免直接修改
如果需要添加 conftest.py 可以在单元测试的目录添加
"""
import os
import time

import pytest
from cassandra.cluster import NoHostAvailable

from apps.base import create_app
from extensions.cassandra_orm import DatabaseManagement
from unittests.docs import DocsGenerator
from unittests.kafka_client import KafkaConsumerClient


@pytest.fixture(scope="session")
def app():
    flask_app = create_app(os.environ.get("STAGE", "testing"))
    from extensions.cassandra_orm.utils import sync_db

    # TODO 模板化，如果没有使用 Cassandra ，应该去掉
    db_management = DatabaseManagement(flask_app, timeout=60)
    try:
        sync_db(app)
    except NoHostAvailable:  # pragma: no cover
        time.sleep(20)
        sync_db(app)

    yield flask_app
    db_management.drop_db()


@pytest.fixture(scope="session", autouse=True)
def docs_generator():
    """设置 scope 为 session, 在整个测试中只运行一次"""
    generator = DocsGenerator()
    yield generator
    generator.build_docs()


@pytest.fixture
def client(app, docs_generator):
    """创建 http client"""
    client = app.test_client()
    client.docs_generator = docs_generator

    return client


@pytest.fixture(scope="session")
def kafka_consumer(app):
    """
    scope: session, 整个 test session 中只创建一次
    """
    consumer = KafkaConsumerClient(
        app.config["FLASK_TEMPLATE_TOPIC"], app.config["KAFKA_SERVER"]
    )

    yield consumer
