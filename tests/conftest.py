from __future__ import annotations

import asyncio
import inspect
import json
import sys
import types
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode


@dataclass(slots=True)
class SimpleResponse:
    status_code: int
    headers: dict[str, str]
    content: bytes

    @property
    def text(self) -> str:
        return self.content.decode("utf-8")

    def json(self) -> Any:
        return json.loads(self.text)


class TestClient:
    """Small ASGI test client used when httpx is unavailable in the sandbox."""

    __test__ = False

    def __init__(self, app: Any) -> None:
        self.app = app

    def get(self, path: str, params: dict[str, Any] | None = None) -> SimpleResponse:
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> SimpleResponse:
        body = b"" if json is None else globals()["json"].dumps(json).encode("utf-8")
        headers = [] if json is None else [(b"content-type", b"application/json")]
        return self._request("POST", path, body=body, headers=headers, params=params)

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: bytes = b"",
        headers: list[tuple[bytes, bytes]] | None = None,
        params: dict[str, Any] | None = None,
    ) -> SimpleResponse:
        async def run() -> SimpleResponse:
            query_string = urlencode(params or {}, doseq=True).encode("utf-8")
            response_status = 500
            response_headers: dict[str, str] = {}
            response_body = bytearray()
            request_sent = False

            scope = {
                "type": "http",
                "asgi": {"version": "3.0", "spec_version": "2.3"},
                "http_version": "1.1",
                "method": method,
                "scheme": "http",
                "path": path,
                "raw_path": path.encode("utf-8"),
                "query_string": query_string,
                "headers": headers or [],
                "client": ("testclient", 50000),
                "server": ("testserver", 80),
                "root_path": "",
            }

            async def receive() -> dict[str, Any]:
                nonlocal request_sent
                if not request_sent:
                    request_sent = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return {"type": "http.disconnect"}

            async def send(message: dict[str, Any]) -> None:
                nonlocal response_status, response_headers
                if message["type"] == "http.response.start":
                    response_status = int(message["status"])
                    response_headers = {
                        key.decode("latin-1").lower(): value.decode("latin-1")
                        for key, value in message.get("headers", [])
                    }
                if message["type"] == "http.response.body":
                    response_body.extend(message.get("body", b""))

            await self.app(scope, receive, send)
            return SimpleResponse(response_status, response_headers, bytes(response_body))

        return asyncio.run(run())


fastapi_testclient_module = types.ModuleType("fastapi.testclient")
fastapi_testclient_module.TestClient = TestClient
sys.modules.setdefault("fastapi.testclient", fastapi_testclient_module)


def pytest_configure(config: Any) -> None:
    config.addinivalue_line("markers", "asyncio: run async test functions with asyncio")


def pytest_pyfunc_call(pyfuncitem: Any) -> bool:
    if "asyncio" not in pyfuncitem.keywords:
        return False
    test_function = pyfuncitem.obj
    if not inspect.iscoroutinefunction(test_function):
        return False
    kwargs = {
        name: pyfuncitem.funcargs[name]
        for name in pyfuncitem._fixtureinfo.argnames
        if name in pyfuncitem.funcargs
    }
    asyncio.run(test_function(**kwargs))
    return True
