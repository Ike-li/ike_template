import importlib
import os


def get_config(config_name: str = None):
    """
    读取 config
    如果没有配置, 就从环境变量读取 config
    """
    if not config_name:
        config_name = os.environ.get("STAGE")

    configs_module = importlib.import_module("configs")
    return getattr(configs_module, config_name.capitalize())
