import asyncio
import random
import uuid

from flask.testing import FlaskClient

from extensions.redis_cluster import redis_client
from unittests.centrifugo_client import CentrifugoClient
from unittests.docs import api_docs
from unittests.kafka_client import KafkaConsumerClient
from unittests.kong_client import kong_user_header


class TestExample:

    @api_docs(
        title="Test Get List",
        path="/v1/example/",
        method="GET",
        customized_response={
            "first_name": "名字",
            "last_name": "姓"
        },
    )
    def test_get_list(self, client: FlaskClient, user_id):
        # 先创建一个对象
        client.post(
            "/v1/example/",
            headers=kong_user_header(user_id),
            json={
                "first_name": "Test",
                "last_name": "Name",
            },
        )

        response1 = client.get(
            "/v1/example/", headers=kong_user_header(uuid.uuid4())
        )
        assert response1.json["ok"] is True
        assert len(response1.json["result"]) == 1
        return {
            "正确响应": response1.json,
        }

    def test_get_single(self, client: FlaskClient):
        # 先创建一个对象
        client.post(
            "/v1/example/",
            headers=kong_user_header(uuid.uuid4()),
            json={
                "first_name": "test",
                "last_name": "name",
            },
        )

        response1 = client.get(
            "/v1/example/test", headers=kong_user_header(uuid.uuid4())
        )
        assert response1.json["ok"] is True
        assert "first_name" in response1.json["result"]

        error_response = client.get(
            "/v1/example/error", headers=kong_user_header(uuid.uuid4())
        )
        error_json_result = error_response.json
        assert error_json_result["ok"] is False
        assert error_json_result["error_type"] == "object_not_found"

        return {"正确响应": response1.json, "错误响应": error_json_result}

    def test_validate_error(self, client: FlaskClient):
        response1 = client.post(
            "/v1/example/",
            headers=kong_user_header(uuid.uuid4()),
            json={
                "last_name": "Name",
            },
        )
        assert response1.status_code == 200
        assert response1.json["ok"] is False
        assert len(response1.json["errors"]) == 1

    def test_post(
        self, client: FlaskClient, kafka_consumer: KafkaConsumerClient
    ):
        # Post without kong user header
        response1 = client.post(
            "/v1/example/",
            headers={
                "App-ID": "test",
                "Accept-Language": "en",
            },
            json={
                "first_name": "Test",
                "last_name": "Name",
            },
        )
        assert response1.status_code == 200
        assert response1.json["ok"] is False
        assert response1.json["error_message"] == "Permission denied"

        # 测试多语言
        response5 = client.post(
            "/v1/example/",
            headers={
                "App-ID": "test",
                "Accept-Language": "zh-Hans",
            },
            json={
                "first_name": "Test",
                "last_name": "Name",
            },
        )
        assert response5.status_code == 200
        assert response5.json["ok"] is False
        assert response5.json["error_message"] == "没有权限"

        # Test request with user header
        last_name = "Name" + str(random.randint(0, 2**32))
        response2 = client.post(
            "/v1/example/",
            headers=kong_user_header(uuid.uuid4()),
            json={
                "first_name": "Test",
                "last_name": last_name,
            },
        )
        print(response2.json, response2.status)
        assert response2.json["ok"] is True
        assert response2.json["result"] == {
            "first_name": "Test",
            "last_name": last_name,
        }

        # 等待数据加载
        assert redis_client.get("example") == b"example"

        kafka_message = kafka_consumer.get_latest()
        print(kafka_message)
        assert kafka_message == {"first_name": "Test", "last_name": last_name}

    def test_class_view(self, client: FlaskClient):
        """测试 class view"""
        # Test request with user header
        response = client.post(
            "/v1/example/class",
            headers=kong_user_header(uuid.uuid4()),
            json={
                "first_name": "Test",
                "last_name": "Name",
            },
        )
        print(response.json, response.status)
        assert response.json["ok"] is True
        assert response.json["result"] == {
            "first_name": "Test",
            "last_name": "Name"
        }

        # 获取 Person 对象
        response1 = client.get(
            "/v1/example/class/Test", headers=kong_user_header(uuid.uuid4())
        )
        assert response1.json["ok"] is True
        assert response.json["result"] == {
            "first_name": "Test",
            "last_name": "Name"
        }

        error_response = client.get(
            "/v1/example/class/error", headers=kong_user_header(uuid.uuid4())
        )
        error_json_result = error_response.json
        assert error_json_result["ok"] is False
        assert error_json_result["error_type"] == "object_not_found"

    def test_centrifugo(self, client: FlaskClient):
        user_id = uuid.uuid4()

        async def get_messages():
            async with CentrifugoClient(
                user_id=user_id, channel_name="user"
            ) as ws:
                response = client.post(
                    "/v1/example/class",
                    headers=kong_user_header(user_id),
                    json={
                        "first_name": "Test",
                        "last_name": "Name",
                    },
                )
                assert response.json["ok"] is True
            return ws.messages

        messages = asyncio.run(get_messages())
        assert len(messages) == 1
        assert messages[0] == {
            "channel": f"user#{user_id!s}",
            "data": {
                "data": {
                    "stream": "example",
                    "sent_at": messages[0]["data"]["data"]["sent_at"],
                    "payload": {
                        "action": "notify",
                        "message": {
                            "first_name": "Test",
                            "last_name": "Name"
                        },
                    },
                }
            },
        }

    def test_deprecated_api(self, client: FlaskClient):
        response1 = client.get("/v1/example/deprecated_function_view")
        json_result1 = response1.json
        assert json_result1["ok"] is False
        assert json_result1["error_message"] == "这个API已经标记为弃用, 请联系后端开发人员确认新的api"

        response2 = client.get("/v1/example/deprecated_class_view")
        json_result2 = response2.json
        assert json_result2["ok"] is False
        assert json_result2["error_message"] == "这个API已经标记为弃用, 请联系后端开发人员确认新的api"

        # 修改STAGE
        client.application.config["STAGE"] = "other_stage"

        response3 = client.get("/v1/example/deprecated_function_view")
        json_result3 = response3.json
        assert json_result3["ok"] is True
        assert json_result3["result"] == "ok"

        response4 = client.get("/v1/example/deprecated_class_view")
        json_result4 = response4.json
        assert json_result4["ok"] is True

        client.application.config["STAGE"] = "testing"

    def test_removed_api(self, client: FlaskClient):
        response1 = client.get("/v1/example/removed_function_view")
        json_result1 = response1.json
        assert json_result1["ok"] is False
        assert json_result1["error_message"
                           ] == "您的软件版本已过期了，请尽快升级。给您带来的不便，我们深表歉意"

        response2 = client.get("/v1/example/removed_class_view")
        json_result2 = response2.json
        assert json_result2["ok"] is False
        assert json_result2["error_message"
                           ] == "您的软件版本已过期了，请尽快升级。给您带来的不便，我们深表歉意"

        # 修改STAGE
        client.application.config["STAGE"] = "other_stage"

        response3 = client.get("/v1/example/removed_function_view")
        json_result3 = response3.json
        assert json_result3["ok"] is True
        assert json_result3["result"] == "ok"

        response4 = client.get("/v1/example/removed_class_view")
        json_result4 = response4.json
        assert json_result4["ok"] is True

        client.application.config["STAGE"] = "testing"
