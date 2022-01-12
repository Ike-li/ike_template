import importlib
import os
import uuid

from rediscluster import RedisCluster


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


def initialize_redis_client():
    RedisCluster.RedisClusterRequestTTL = config.REDIS_CLUSTER_REQUEST_TTL
    client = RedisCluster(
        startup_nodes=config.REDIS_STARTUP_NODES, read_from_replicas=True
    )
    return client


def redis_lock(name, namespace=None, timeout=config.DEFAULT_LOCK_TIMEOUT):
    if namespace:
        key = f"{namespace}:{name}"
    else:
        key = f"{name}"
    return redis_client.lock(name=key, timeout=timeout)


class DuplicateRequest(Exception):
    """重复的请求"""

    def __init__(self):
        self.error_type = "duplicate_request"
        self.error_message = "Duplicate request"


def assert_new_request(
    name: str, request_id: uuid.UUID, life_time_second: int = 60
):
    """
    当需要将 POST 请求转成 PUT 请求时候，需要保证请求的幂等性。

    可以用这个函数来避免重复的创建
    """
    assert isinstance(request_id, uuid.UUID)

    request_key = f"request:{name}:{request_id}"

    if redis_client.exists(request_key):
        raise DuplicateRequest
    else:
        # 如果请求不存在，60秒内就不再接受相同的请求了
        redis_client.set(request_key, value="", ex=life_time_second)


redis_client = initialize_redis_client()
