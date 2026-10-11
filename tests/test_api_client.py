import requests
import pytest

from src.api_client import ApiIntegrationError, fetch_post, make_report


class FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=False):
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error

    @property
    def ok(self):
        return 200 <= self.status_code < 400

    def json(self):
        if self._json_error:
            raise ValueError("bad json")
        return self._payload


VALID_POST = {"userId": 1, "id": 1, "title": "Example title", "body": "Example body"}


def test_fetch_post_success(monkeypatch):
    monkeypatch.setattr("src.api_client.requests.get", lambda *a, **k: FakeResponse(payload=VALID_POST))
    assert fetch_post(1)["title"] == "Example title"


def test_http_error_is_reported(monkeypatch):
    monkeypatch.setattr("src.api_client.requests.get", lambda *a, **k: FakeResponse(status_code=503))
    with pytest.raises(ApiIntegrationError, match="HTTP 503"):
        fetch_post(1)


def test_invalid_json_is_reported(monkeypatch):
    monkeypatch.setattr("src.api_client.requests.get", lambda *a, **k: FakeResponse(json_error=True))
    with pytest.raises(ApiIntegrationError, match="valid JSON"):
        fetch_post(1)


def test_missing_fields_are_reported(monkeypatch):
    monkeypatch.setattr("src.api_client.requests.get", lambda *a, **k: FakeResponse(payload={"id": 1}))
    with pytest.raises(ApiIntegrationError, match="missing"):
        fetch_post(1)


def test_timeout_is_reported(monkeypatch):
    def timeout(*args, **kwargs):
        raise requests.Timeout("slow")
    monkeypatch.setattr("src.api_client.requests.get", timeout)
    with pytest.raises(ApiIntegrationError, match="timed out"):
        fetch_post(1)


def test_post_id_must_be_positive():
    with pytest.raises(ValueError, match="positive"):
        fetch_post(0)


def test_make_report():
    report = make_report(VALID_POST, 42.126)
    assert report["integration_status"] == "success"
    assert report["required_fields_validated"] is True
    assert report["response_time_ms"] == 42.13
