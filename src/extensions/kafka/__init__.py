import importlib
import os
import signal
from functools import partial

import ujson
from confluent_kafka import Producer

from extensions.sentry import sentry

default_sigint_handler = signal.getsignal(signal.SIGINT)
default_sigterm_handler = signal.getsignal(signal.SIGTERM)


def get_config(config_name: str = None):
    """
    读取 config
    如果没有配置, 就从环境变量读取 config
    """
    if not config_name:
        config_name = os.environ.get("STAGE")

    configs_module = importlib.import_module("configs")
    return getattr(configs_module, config_name.capitalize())


config = get_config()


class KafkaProducer(Producer):

    def send(self, *args, **kwargs):
        """patch produce 方法，如果发送消息失败，记录到 sentry"""
        if "callback" in kwargs:
            return self.produce(*args, **kwargs)
        return partial(self.produce,
                       callback=self.report_failed_msg)(*args, **kwargs)

    @staticmethod
    def report_failed_msg(err, msg):
        if not err:
            return
        sentry.captureMessage(
            message=ujson.dumps({
                "error": str(err),
                "message": str(msg.value())
            })
        )


# config 字段文档
# https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
kafka_producer = KafkaProducer(
    **{
        "bootstrap.servers": config.KAFKA_SERVER,
        "compression.type": "snappy",
        "enable.idempotence": True,
    }
)


def shutdown(signum, frame):
    """清理 kafka producer"""
    global default_sigint_handler
    global default_sigterm_handler

    kafka_producer.flush(timeout=3)

    if signum == signal.SIGTERM:
        default_sigterm_handler(signum, frame)
    if signum == signal.SIGINT:
        default_sigint_handler(signum, frame)


signal.signal(signal.SIGINT, shutdown)
