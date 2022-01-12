"""
集群里的相关配置
"""
import ast
import os

from extensions.base_configs import BaseConfig


class Config(BaseConfig):
    pass


class Debug(Config):
    STAGE = "debug"

    CASSANDRA_NODES = ["0.0.0.0"]

    KAFKA_SERVER = "0.0.0.0:9092"

    REDIS_STARTUP_NODES = [{"host": "0.0.0.0", "port": 7000}]

    JAEGER_AGENT_HOST = "0.0.0.0"
    # Jaeger 统计请求的频率
    SAMPLER_RATE = 1


class Development(Config):
    STAGE = "development"

    JAEGER_AGENT_HOST = "jaeger"
    # Jaeger 统计请求的频率
    SAMPLER_RATE = 1


class Testing(Config):
    STAGE = "testing"

    # Jaeger 统计请求的频率
    SAMPLER_RATE = 1

    # logger config
    LOGGING_LEVEL = "DEBUG"


class Staging(Config):
    DEBUG = False
    STAGE = "staging"

    KAFKA_SERVER = os.environ.get("KAFKA_SERVER")

    if os.environ.get("CASSANDRA_NODES", ""):
        CASSANDRA_NODES = ast.literal_eval(
            os.environ.get("CASSANDRA_NODES", "")
        )
    if os.environ.get("CASSANDRA_REPLICATION_FACTOR"):
        CASSANDRA_REPLICATION_FACTOR = ast.literal_eval(
            os.environ.get("CASSANDRA_REPLICATION_FACTOR")
        )
    CASSANDRA_PASSWORD = os.environ.get("CASSANDRA_PASSWORD")

    CENTRIFUGO_URL = os.environ.get("CENTRIFUGO_URL")
    CENTRIFUGO_API_KEY = os.environ.get("CENTRIFUGO_API_KEY")

    if os.environ.get("REDIS_STARTUP_NODES", ""):
        REDIS_STARTUP_NODES = ast.literal_eval(
            os.environ.get("REDIS_STARTUP_NODES", "")
        )

    # jaeger
    JAEGER_AGENT_HOST = os.environ.get("JAEGER_AGENT_HOST")
    # Jaeger 统计请求的频率
    SAMPLER_RATE = 1


class Production(Config):
    DEBUG = False
    STAGE = "production"

    KAFKA_SERVER = os.environ.get("KAFKA_SERVER")

    if os.environ.get("CASSANDRA_NODES", ""):
        CASSANDRA_NODES = ast.literal_eval(
            os.environ.get("CASSANDRA_NODES", "")
        )
    if os.environ.get("CASSANDRA_REPLICATION_FACTOR"):
        CASSANDRA_REPLICATION_FACTOR = ast.literal_eval(
            os.environ.get("CASSANDRA_REPLICATION_FACTOR")
        )
    CASSANDRA_PASSWORD = os.environ.get("CASSANDRA_PASSWORD")

    CENTRIFUGO_URL = os.environ.get("CENTRIFUGO_URL")
    CENTRIFUGO_API_KEY = os.environ.get("CENTRIFUGO_API_KEY")

    if os.environ.get("REDIS_STARTUP_NODES", ""):
        REDIS_STARTUP_NODES = ast.literal_eval(
            os.environ.get("REDIS_STARTUP_NODES", "")
        )

    # logger config
    LOGGING_LEVEL = "INFO"
