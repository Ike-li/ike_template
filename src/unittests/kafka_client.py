import ujson
from confluent_kafka import (
    OFFSET_BEGINNING,
    Consumer,
    KafkaException,
    TopicPartition,
)

from extensions.kafka import kafka_producer


class KafkaConsumerClient:
    """
    帮助测试用的 kafka consumer
    """

    def __init__(self, topic, server):
        self.consumer = Consumer({
            "bootstrap.servers": server,
            "group.id": "consumer-test-client",
            "enable.auto.commit": False,
        })
        self.topic = topic
        self.consumer.assign([
            TopicPartition(topic=topic, partition=0, offset=OFFSET_BEGINNING)
        ])

    def get_latest(self):
        while True:
            kafka_producer.flush()
            try:
                _, latest = self.consumer.get_watermark_offsets(
                    TopicPartition(self.topic, 0)
                )
            except KafkaException:  # pragma: no cover
                # https://github.com/confluentinc/confluent-kafka-python/issues/1043
                # 等待下一个版本修复该问题
                print("blocking")
                continue
            else:
                self.consumer.seek(
                    TopicPartition(self.topic, partition=0, offset=latest - 1)
                )
                break
        message = self.consumer.poll(timeout=5)
        return ujson.loads(message.value().decode())
