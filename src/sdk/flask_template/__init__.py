import os

import httpcore
import httpx
import ujson

from sdk.exception import SDKException

# 在部署时，该服务的 Service 需要在业务 Pod 之前部署
SERVICE_HOST = os.environ.get("FLASK_TEMPLATE_SERVICE_HOST")
SERVICE_PORT = os.environ.get("FLASK_TEMPLATE_SERVICE_PORT")
if SERVICE_HOST is not None:
    BASE_URL = f"http://{SERVICE_HOST}:{SERVICE_PORT}"
else:
    BASE_URL = "https://api.shafayouxi.org"


async def _async(func, *args, **kwargs):
    response = await func(*args, **kwargs)
    response.raise_for_status()
    payload = response.json()
    if payload["ok"]:
        return payload["result"]

    if payload.get("error_type"):
        error_message = payload.get("error_message") or payload.get("message")
        raise SDKException(
            error_type=payload["error_type"], error_message=error_message
        )

    # service request params validation error
    raise Exception(ujson.dumps(payload))


def _sync(func, *args, **kwargs):
    response = func(*args, **kwargs)
    response.raise_for_status()
    payload = response.json()
    if payload["ok"]:
        return payload["result"]

    if payload.get("error_type"):
        error_message = payload.get("error_message") or payload.get("message")
        raise SDKException(
            error_type=payload["error_type"], error_message=error_message
        )

    # service request params validation error
    raise Exception(ujson.dumps(payload))


def deserialize(func):

    def wrapper(*args, **kwargs):
        cls = args[0]
        return cls.hook(func, *args, **kwargs)

    return wrapper


class FlaskTemplate:
    CLIENT = None

    @classmethod
    @deserialize
    def create_person(cls, first_name, last_name):
        return cls.CLIENT.post(
            "/v1/example/",
            json={
                "first_name": first_name,
                "last_name": last_name,
            },
        )

    @classmethod
    @deserialize
    def get_person(cls, first_name):
        return cls.CLIENT.get(f"/v1/example/class/{first_name}")


class FlaskTemplateService(FlaskTemplate):
    # 除了 retries 的参数来自于默认值
    transport = httpcore.SyncConnectionPool(
        retries=3,
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=5
    )
    CLIENT = httpx.Client(transport=transport, base_url=BASE_URL)
    hook = _sync


class AsyncFlaskTemplateService(FlaskTemplate):
    # 除了 retries 的参数来自于默认值
    transport = httpcore.AsyncConnectionPool(
        retries=3,
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=5
    )
    CLIENT = httpx.AsyncClient(transport=transport, base_url=BASE_URL)
    hook = _async
