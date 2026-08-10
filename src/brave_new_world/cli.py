from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import webbrowser

from brave_new_world.contracts import ContractError, Scenario, SimulationRequest
from brave_new_world.simulation.first_order import simulate_first_order
from brave_new_world.ui.server import create_server


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _request_from_arguments(arguments: argparse.Namespace) -> SimulationRequest:
    return SimulationRequest.from_mapping(
        {
            "demo_id": "first-order-step",
            "duration_s": arguments.duration,
            "dt_s": arguments.dt,
            "input_amplitude": arguments.input_amplitude,
            "time_constant_s": arguments.tau,
            "gain": arguments.gain,
            "initial_output": arguments.initial_output,
        }
    )


def _cmd_simulate(arguments: argparse.Namespace) -> int:
    try:
        trace = simulate_first_order(_request_from_arguments(arguments))
    except ContractError as exc:
        print(f"invalid simulation request: {exc}", file=sys.stderr)
        return 2
    serialized = json.dumps(
        trace.to_dict(), ensure_ascii=False, indent=2, allow_nan=False
    ) + "\n"
    if arguments.output is None:
        print(serialized, end="")
    else:
        arguments.output.write_text(serialized, encoding="utf-8")
        print(f"trace written to {arguments.output}")
    return 0


def _cmd_run_scenario(arguments: argparse.Namespace) -> int:
    try:
        payload = json.loads(arguments.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ContractError("scenario document must be a JSON object")
        scenario = Scenario.from_mapping(payload)
        trace = simulate_first_order(scenario.request)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"invalid scenario: {exc}", file=sys.stderr)
        return 2
    serialized = json.dumps(
        {
            "scenario": scenario.to_dict(),
            "trace": trace.to_dict(),
        },
        ensure_ascii=False,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if arguments.output is None:
        print(serialized, end="")
    else:
        arguments.output.write_text(serialized, encoding="utf-8")
        print(f"scenario result written to {arguments.output}")
    return 0


def _open_browser(url: str) -> bool:
    try:
        opened = webbrowser.open(url, new=2)
    except (OSError, webbrowser.Error) as exc:
        print(
            f"could not open the browser ({exc}); open this URL manually: {url}",
            file=sys.stderr,
            flush=True,
        )
        return False
    if not opened:
        print(
            f"could not open the browser; open this URL manually: {url}",
            file=sys.stderr,
            flush=True,
        )
    return opened


def _cmd_ui(arguments: argparse.Namespace) -> int:
    try:
        server = create_server(arguments.port)
    except (OSError, ValueError) as exc:
        print(f"unable to start the teaching UI: {exc}", file=sys.stderr, flush=True)
        print(
            "if the port is already in use, retry with: bnw ui --port 0 --open-browser",
            file=sys.stderr,
            flush=True,
        )
        return 1
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}/"
    print(f"BraveNewWorld teaching UI: {url}", flush=True)
    print("press Ctrl+C to stop", flush=True)
    if arguments.open_browser:
        _open_browser(url)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\nUI stopped")
    finally:
        server.server_close()
    return 0


def _cmd_check() -> int:
    root = _repository_root()
    environment = os.environ.copy()
    source_path = str(root / "src")
    existing_python_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        source_path
        if not existing_python_path
        else os.pathsep.join((source_path, existing_python_path))
    )
    commands = (
        (sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"),
        (sys.executable, "-m", "compileall", "-q", "src", "tests"),
        ("git", "diff", "--check"),
        ("git", "diff", "--cached", "--check"),
    )
    passed = 0
    for index, command in enumerate(commands, start=1):
        print(f"[check {index}/{len(commands)}] {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=root, check=False, env=environment)
        if result.returncode != 0:
            print(f"[fail] exit code {result.returncode}", flush=True)
        else:
            passed += 1
            print("[pass]", flush=True)
    print(f"BNW checks: {passed}/{len(commands)} passed", flush=True)
    return 0 if passed == len(commands) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bnw", description="BraveNewWorld deterministic teaching simulator"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    simulate = commands.add_parser("simulate", help="run the first-order demo headlessly")
    simulate.add_argument("--duration", type=float, default=5.0)
    simulate.add_argument("--dt", type=float, default=0.05)
    simulate.add_argument("--input", dest="input_amplitude", type=float, default=1.0)
    simulate.add_argument("--tau", type=float, default=0.8)
    simulate.add_argument("--gain", type=float, default=1.0)
    simulate.add_argument("--initial-output", type=float, default=0.0)
    simulate.add_argument("--output", type=Path)

    scenario = commands.add_parser(
        "run-scenario", help="run a versioned scenario JSON headlessly"
    )
    scenario.add_argument("path", type=Path)
    scenario.add_argument("--output", type=Path)

    ui = commands.add_parser("ui", help="serve the loopback-only teaching UI")
    ui.add_argument("--port", type=int, default=8080)
    ui.add_argument("--open-browser", action="store_true")

    commands.add_parser("check", help="run the complete local verification suite")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "simulate":
        return _cmd_simulate(arguments)
    if arguments.command == "run-scenario":
        return _cmd_run_scenario(arguments)
    if arguments.command == "ui":
        return _cmd_ui(arguments)
    if arguments.command == "check":
        return _cmd_check()
    raise AssertionError(f"unhandled command: {arguments.command}")
