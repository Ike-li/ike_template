import logging

from extensions.cassandra_orm.management import DatabaseManagement

logger = logging.getLogger("flask")


class CassandraSessionBuilder:

    def __init__(self, app):
        self.app = app

    def setup_db_session(self):
        """创建cassandra连接"""
        db_management = DatabaseManagement(self.app)
        db_management.create_keyspace_if_not_exist()
        db_management.connect()
        logger.info("Cassandra session prepared")

    def register_cassandra_session(self):
        """启动 Cassandra db session"""
        self.setup_db_session()
