from http.client import HTTPConnection
import json
import os
from pathlib import Path
from threading import Thread
import unittest

from brave_new_world.ui.server import create_server


class TeachingServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = create_server(0)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)

    def tearDown(self) -> None:
        self.connection.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def test_serves_modular_ui_assets(self) -> None:
        for path, content_type in (
            ("/", "text/html"),
            ("/styles.css", "text/css"),
            ("/app.js", "text/javascript"),
        ):
            with self.subTest(path=path):
                self.connection.request("GET", path)
                response = self.connection.getresponse()
                body = response.read()
                self.assertEqual(response.status, 200)
                self.assertIn(content_type, response.getheader("Content-Type"))
                self.assertTrue(body)

    def test_simulation_api_uses_real_kernel_contract(self) -> None:
        payload = json.dumps({"duration_s": 1, "dt_s": 0.25, "time_constant_s": 0.5})
        self.connection.request(
            "POST",
            "/api/simulate",
            body=payload,
            headers={"Content-Type": "application/json"},
        )
        response = self.connection.getresponse()
        result = json.loads(response.read())
        self.assertEqual(response.status, 200)
        self.assertEqual(result["engine_version"], "first-order-exact-v1")
        self.assertEqual(len(result["points"]), 5)
        self.assertEqual(len(result["trace_hash"]), 64)

    def test_rejects_invalid_parameters(self) -> None:
        self.connection.request(
            "POST",
            "/api/simulate",
            body=json.dumps({"time_constant_s": 0}),
            headers={"Content-Type": "application/json"},
        )
        response = self.connection.getresponse()
        result = json.loads(response.read())
        self.assertEqual(response.status, 400)
        self.assertIn("time_constant_s", result["error"])

    def test_server_is_bound_to_loopback(self) -> None:
        self.assertEqual(self.server.server_address[0], "127.0.0.1")


class SourceEntrypointTests(unittest.TestCase):
    def test_source_entrypoint_help(self) -> None:
        import subprocess

        root = Path(__file__).resolve().parents[1]
        launcher = root / ("bnw.cmd" if os.name == "nt" else "bnw")
        result = subprocess.run(
            [str(launcher), "--help"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("deterministic teaching simulator", result.stdout)


if __name__ == "__main__":
    unittest.main()
