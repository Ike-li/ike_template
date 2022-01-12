import importlib
import os
import uuid
from typing import Union

import requests
from cent import Client
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def get_config(config_name: str = None):
    """
    读取 config
    如果没有配置, 就从环境变量读取 config
    """
    if not config_name:
        config_name = os.environ.get("STAGE")

    configs_module = importlib.import_module("configs")
    return getattr(configs_module, config_name.capitalize())


def user_channel(user_id: Union[str, uuid.UUID]) -> str:
    if isinstance(user_id, uuid.UUID):
        return f"user#{user_id!s}"
    return f"user#{user_id}"


def initialize_centrifugo():
    config = get_config()
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[429, 500, 503, 504],
        allowed_methods=["POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount(prefix="http://", adapter=adapter)

    return Client(
        config.CENTRIFUGO_URL,
        api_key=config.CENTRIFUGO_API_KEY,
        timeout=config.CENTRIFUGO_TIMEOUT,
        session=session,
    )


centrifugo = initialize_centrifugo()
