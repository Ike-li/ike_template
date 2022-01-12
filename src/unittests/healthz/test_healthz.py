from flask.testing import FlaskClient


def test_healthz(client: FlaskClient):
    """k8s healthz 检测"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json["result"] == "ok"


def test_readiness(client: FlaskClient):
    """k8s readiness 检测"""
    response = client.get("/readiness")
    assert response.status_code == 200
    assert response.json["result"] == "ok"
