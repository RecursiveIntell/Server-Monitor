from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse


class SimpleResponse:
    def __init__(self, status_code: int, body: bytes, headers: Dict[str, str]) -> None:
        self.status_code = status_code
        self._body = body
        self.headers = headers

    def json(self) -> Any:
        return json.loads(self._body.decode("utf-8"))

    @property
    def text(self) -> str:
        return self._body.decode("utf-8")


class SimpleTestClient:
    def __init__(self, app, base_url: str = "http://testserver", **_kwargs) -> None:
        self.app = app
        self.base_url = base_url

    def get(self, url: str, headers: Dict[str, str] | None = None) -> SimpleResponse:
        return self.request("GET", url, headers=headers)

    def post(
        self, url: str, json: Any | None = None, headers: Dict[str, str] | None = None
    ) -> SimpleResponse:
        return self.request("POST", url, json_body=json, headers=headers)

    def request(
        self,
        method: str,
        url: str,
        json_body: Any | None = None,
        headers: Dict[str, str] | None = None,
    ) -> SimpleResponse:
        parsed = urlparse(url)
        path = parsed.path or url
        body = b""
        header_items: List[Tuple[bytes, bytes]] = []
        if headers:
            header_items.extend([(k.lower().encode("latin1"), v.encode("latin1")) for k, v in headers.items()])
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            header_items.append((b"content-type", b"application/json"))

        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": method,
            "path": path,
            "raw_path": path.encode("utf-8"),
            "query_string": parsed.query.encode("utf-8"),
            "headers": header_items,
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
        }

        messages = [
            {"type": "http.request", "body": body, "more_body": False}
        ]
        response_status = 500
        response_headers: Dict[str, str] = {}
        response_body = bytearray()

        async def receive():
            if messages:
                return messages.pop(0)
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            nonlocal response_status, response_headers
            if message["type"] == "http.response.start":
                response_status = message["status"]
                for key, value in message.get("headers", []):
                    response_headers[key.decode("latin1")] = value.decode("latin1")
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

        asyncio.run(self.app(scope, receive, send))
        return SimpleResponse(response_status, bytes(response_body), response_headers)


def apply_fastapi_testclient_patch() -> None:
    try:
        import fastapi.testclient as testclient
    except Exception:
        return
    testclient.TestClient = SimpleTestClient
