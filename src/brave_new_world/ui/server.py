from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any

from brave_new_world.contracts import ContractError, SimulationRequest
from brave_new_world.demos.registry import DEMOS
from brave_new_world.simulation.first_order import simulate_first_order


ASSET_ROOT = Path(__file__).with_name("assets")
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
MAX_BODY_BYTES = 16_384


class TeachingServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class TeachingRequestHandler(BaseHTTPRequestHandler):
    server_version = "BraveNewWorld/0.0.1"

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path == "/api/demos":
            self._send_json(
                HTTPStatus.OK,
                {"schema_version": "1.0", "demos": [demo.to_dict() for demo in DEMOS]},
            )
            return
        asset = ASSETS.get(self.path)
        if asset is None:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        name, content_type = asset
        try:
            body = (ASSET_ROOT / name).read_bytes()
        except OSError:
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "UI asset unavailable"}
            )
            return
        self._send(HTTPStatus.OK, body, content_type)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path != "/api/simulate":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0]
        if content_type != "application/json":
            self._send_json(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                {"error": "Content-Type must be application/json"},
            )
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY_BYTES:
            self._send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "body too large"})
            return
        try:
            payload: Any = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ContractError("request body must be a JSON object")
            request = SimulationRequest.from_mapping(payload)
            trace = simulate_first_order(request)
        except (json.JSONDecodeError, UnicodeDecodeError, ContractError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return
        self._send_json(HTTPStatus.OK, trace.to_dict())

    def _send_json(self, status: HTTPStatus, payload: Any) -> None:
        body = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, allow_nan=False
        ).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'",
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def create_server(port: int = 8080) -> TeachingServer:
    if not 0 <= port <= 65535:
        raise ValueError("port must be between 0 and 65535")
    return TeachingServer(("127.0.0.1", port), TeachingRequestHandler)
