import importlib
import os

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

tracer = None


def get_config(config_name: str = None):
    """
    读取 config
    如果没有配置, 就从环境变量读取 config
    """
    if not config_name:
        config_name = os.environ.get("STAGE")

    configs_module = importlib.import_module("configs")
    return getattr(configs_module, config_name.capitalize())


class TracingMiddleware:

    @staticmethod
    def init_tracer():
        """如果设置了 debug，则会将 tracing 信息打印出来"""
        config = get_config()
        sampler = sampling.TraceIdRatioBased(config.SAMPLER_RATE)
        resource = Resource.create({"service.name": config.SERVICE_NAME})
        trace.set_tracer_provider(
            TracerProvider(resource=resource, sampler=sampler)
        )

        if os.environ.get("STAGE") == "testing":
            trace.get_tracer_provider().add_span_processor(
                SimpleSpanProcessor(ConsoleSpanExporter())
            )

        jaeger_exporter = JaegerExporter(
            agent_host_name=config.JAEGER_AGENT_HOST
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )

        global tracer
        tracer = trace.get_tracer(__name__)
