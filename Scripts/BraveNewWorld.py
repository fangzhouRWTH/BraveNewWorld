from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE_CONTRACT = json.loads((ROOT / "Config/Engine.json").read_text(encoding="utf-8"))


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def engine_root(args: argparse.Namespace) -> Path:
    value = args.engine_root or os.environ.get("ANYGINE_SOURCE_ROOT")
    if not value:
        raise SystemExit(
            "Anygine source root is required: pass --engine-root or set ANYGINE_SOURCE_ROOT."
        )
    return Path(value).expanduser().resolve()


def toolchain(args: argparse.Namespace, source_root: Path) -> Path:
    value = args.toolchain or os.environ.get("ANYGINE_CONAN_TOOLCHAIN")
    path = (
        Path(value).expanduser().resolve()
        if value
        else source_root / "build/conan/conan_toolchain.cmake"
    )
    if not path.is_file():
        raise SystemExit(
            f"Anygine Conan toolchain is missing: {path}. Prepare Anygine or pass --toolchain."
        )
    return path


def build_dir(args: argparse.Namespace) -> Path:
    return (
        Path(args.build_dir).expanduser().resolve()
        if args.build_dir
        else ROOT / "build/debug"
    )


def verify_engine(source_root: Path) -> None:
    if not (source_root / "CMakeLists.txt").is_file():
        raise SystemExit(f"Not an Anygine source checkout: {source_root}")
    actual = subprocess.check_output(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"], text=True
    ).strip()
    expected = ENGINE_CONTRACT["commit"]
    if actual != expected:
        raise SystemExit(f"Anygine revision mismatch: expected {expected}, found {actual}.")


def doctor(args: argparse.Namespace) -> None:
    source_root = engine_root(args)
    for executable in ("git", "cmake", "ctest"):
        resolved = shutil.which(executable)
        if not resolved:
            raise SystemExit(f"Required executable is missing: {executable}")
        print(f"[ready] {executable}: {resolved}")
    verify_engine(source_root)
    print(f"[ready] Anygine: {source_root}@{ENGINE_CONTRACT['commit']}")
    print(f"[ready] toolchain: {toolchain(args, source_root)}")


def configure(args: argparse.Namespace) -> None:
    source_root = engine_root(args)
    verify_engine(source_root)
    selected_toolchain = toolchain(args, source_root)
    output = build_dir(args)
    generator = "Ninja" if os.name == "nt" else "Unix Makefiles"
    run(
        [
            "cmake",
            "-S",
            str(ROOT),
            "-B",
            str(output),
            "-G",
            generator,
            "-DCMAKE_BUILD_TYPE=Debug",
            f"-DCMAKE_TOOLCHAIN_FILE={selected_toolchain}",
            f"-DANYGINE_SOURCE_ROOT={source_root}",
        ]
    )


def build(args: argparse.Namespace) -> None:
    configure(args)
    run(
        [
            "cmake",
            "--build",
            str(build_dir(args)),
            "--target",
            "BraveNewWorldBuildAll",
            "--parallel",
            str(args.jobs),
        ]
    )


def test(args: argparse.Namespace) -> None:
    build(args)
    run(["ctest", "--test-dir", str(build_dir(args)), "--output-on-failure"])


def contract() -> None:
    run([sys.executable, str(ROOT / "Tests/ManifestContract.py"), str(ROOT)])


def run_app(args: argparse.Namespace) -> None:
    build(args)
    suffix = ".exe" if os.name == "nt" else ""
    executable = (
        build_dir(args) / "Source/Apps/HelloTask" / f"BraveNewWorldHelloTask{suffix}"
    )
    if not executable.is_file():
        raise SystemExit(f"Built application is missing: {executable}")
    run([str(executable)])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BraveNewWorld Anygine App testbed launcher"
    )
    parser.add_argument(
        "command",
        choices=("doctor", "contract", "configure", "build", "test", "check", "run"),
    )
    parser.add_argument("--engine-root")
    parser.add_argument("--toolchain")
    parser.add_argument("--build-dir")
    parser.add_argument("--jobs", type=int, default=max(1, min(os.cpu_count() or 1, 4)))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.jobs < 1:
        raise SystemExit("--jobs must be positive")
    if args.command == "contract":
        contract()
    elif args.command == "doctor":
        doctor(args)
    elif args.command == "configure":
        configure(args)
    elif args.command == "build":
        build(args)
    elif args.command == "test":
        test(args)
    elif args.command == "run":
        run_app(args)
    else:
        contract()
        doctor(args)
        test(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
