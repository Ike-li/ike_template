# pylava:ignore=E501
from pathlib import Path

base_dir = str(Path(__file__).parent.parent)


class BaseConfig:
    """
    基础设置

    请不要将业务逻辑的配置放在这里, 业务逻辑的 config 请放在 src/config.py 中
    """

    # Flask settings
    PORT = 8000
    DEBUG = True
    SECRET_KEY = "aw(*@#Hha9s8dfy1h2342j349uh123872345234673641!x"
    SERVICE_NAME = "flask_template"

    # cassandra config
    CASSANDRA_NODES = ["cassandra"]
    CASSANDRA_USER = "cassandra"
    CASSANDRA_PASSWORD = "cassandra"
    CASSANDRA_KEYSPACE = "flask_template"
    CASSANDRA_REPLICATION_FACTOR = 1

    # centrifugo
    CENTRIFUGO_URL = "http://centrifugo:8000"
    CENTRIFUGO_API_KEY = "2f281382-c858-4020-bf03-f469ab7512bc"
    # Centrifugo 的库使用 requests，requests 请求的时候，超时设置用 tuple 表示
    # 类型: (connect timeout, read timeout)
    CENTRIFUGO_TIMEOUT = (1.5, 1)

    # kafka
    KAFKA_SERVER = "kafka:9092"
    KAFKA_HEALTHZ_TOPIC = "FlaskTemplateHealthz"
    FLASK_TEMPLATE_TOPIC = "FlaskTemplate"

    # redis cluster
    REDIS_STARTUP_NODES = [{"host": "redis_cluster", "port": 7000}]
    DEFAULT_LOCK_TIMEOUT = 3
    REDIS_CLUSTER_REQUEST_TTL = 2**31

    # i18n
    LANGUAGES = {
        "en": "English",
        "zh": "中文",
        "zh_Hans": "简体中文",
        "zh_Hant": "繁体中文",
    }
    BABEL_TRANSLATION_DIRECTORIES = str(Path(base_dir, "i18n/translations"))

    # OpenTelemetry
    JAEGER_AGENT_HOST = ""
    SAMPLER_RATE = 0

    # logger config
    LOGGING_LEVEL = "INFO"

    @classmethod
    def log_config(cls):
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "root": {
                "level": cls.LOGGING_LEVEL,
                "handlers": ["console"]
            },
            "loggers": {
                # 默认配置, 通过logging.getLogger(__name__)拿到的logger配置
                "": {
                    "handlers": ["console"],
                    "level": cls.LOGGING_LEVEL,
                    "propagate": True,
                },
                # 自定义, 通过logging.getLogger('flask')拿到的logger配置
                # propagate设置为False，关闭向上级logger传递，否则会出现重复输出
                cls.SERVICE_NAME: {
                    "handlers": ["console"],
                    "level": cls.LOGGING_LEVEL,
                    "propagate": False,
                },
                "rediscluster": {
                    "handlers": ["console"],
                    "level": cls.LOGGING_LEVEL,
                    "propagate": False,
                },
                "cassandra": {
                    "handlers": ["console"],
                    "level": cls.LOGGING_LEVEL,
                    "propagate": False,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "generic",
                    "stream": "ext://sys.stdout",
                },
            },
            "formatters": {
                "generic": {
                    "format": (
                        "%(asctime)s [%(process)d] [%(levelname)s] "
                        "[%(name)s] %(message)s"
                    ),
                    "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
                    "class": "logging.Formatter",
                }
            },
        }
