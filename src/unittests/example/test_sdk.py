import asyncio
import uuid

import httpx
from a2wsgi import WSGIMiddleware

from sdk.flask_template import AsyncFlaskTemplateService, FlaskTemplateService
from unittests.kong_client import kong_user_header


def test_sdk(app):
    client = httpx.Client(
        app=app,
        base_url="http://local:80",
        headers=kong_user_header(uuid.uuid4())
    )
    FlaskTemplateService.CLIENT = client
    FlaskTemplateService.create_person("elune", "Sunstrider")

    person = FlaskTemplateService.get_person("elune")
    assert person["last_name"] == "Sunstrider"


def test_async_sdk(app):
    client = httpx.AsyncClient(
        app=WSGIMiddleware(app),
        base_url="http://local:80",
        headers=kong_user_header(uuid.uuid4()),
    )
    AsyncFlaskTemplateService.CLIENT = client
    asyncio.run(AsyncFlaskTemplateService.create_person("elune2", "Sunstrider"))

    person = asyncio.run(AsyncFlaskTemplateService.get_person("elune2"))
    assert person["last_name"] == "Sunstrider"
