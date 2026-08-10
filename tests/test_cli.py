from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch

from brave_new_world.cli import main


class _ImmediateServer:
    server_address = ("127.0.0.1", 43123)

    def __init__(self) -> None:
        self.served = False
        self.closed = False

    def serve_forever(self, poll_interval: float) -> None:
        self.served = poll_interval == 0.25

    def server_close(self) -> None:
        self.closed = True


class UiCommandTests(unittest.TestCase):
    def test_browser_failure_keeps_ui_available_at_printed_url(self) -> None:
        server = _ImmediateServer()
        stdout = StringIO()
        stderr = StringIO()
        with (
            patch("brave_new_world.cli.create_server", return_value=server),
            patch("brave_new_world.cli.webbrowser.open", return_value=False),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            result = main(["ui", "--port", "0", "--open-browser"])

        self.assertEqual(result, 0)
        self.assertTrue(server.served)
        self.assertTrue(server.closed)
        self.assertIn("http://127.0.0.1:43123/", stdout.getvalue())
        self.assertIn("open this URL manually", stderr.getvalue())

    def test_bind_failure_returns_actionable_error(self) -> None:
        stderr = StringIO()
        with (
            patch(
                "brave_new_world.cli.create_server",
                side_effect=OSError(10048, "address already in use"),
            ),
            redirect_stderr(stderr),
        ):
            result = main(["ui", "--port", "8080"])

        self.assertEqual(result, 1)
        self.assertIn("unable to start the teaching UI", stderr.getvalue())
        self.assertIn("--port 0 --open-browser", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
