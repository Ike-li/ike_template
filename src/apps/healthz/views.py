from flask import Blueprint

from extensions.flask_api.api import route
from extensions.project_config import get_config

blueprint = Blueprint("healthz", __name__)

config = get_config()


@route(blueprint, "/healthz")
def healthz():
    """k8s healtz 检测"""
    return "ok"


@route(blueprint, "/readiness")
def readiness():
    """k8s readiness 检测"""
    return "ok"
