from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster


class CassandraCqlClient:

    def __init__(self, app):
        self.app = app
        auth = PlainTextAuthProvider(
            username=self.app.config["CASSANDRA_USER"],
            password=self.app.config["CASSANDRA_PASSWORD"],
        )

        self.cluster = Cluster(
            self.app.config["CASSANDRA_NODES"], auth_provider=auth
        )

    def setup_cql(self):
        self.app.cql = self.cluster.connect(
            self.app.config["CASSANDRA_KEYSPACE"]
        )

    def register_cassandra_cql(self):
        """启动 Cassandra cql"""
        self.setup_cql()
