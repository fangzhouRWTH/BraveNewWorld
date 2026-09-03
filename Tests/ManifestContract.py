from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    engine = json.loads(read_text(root / "Config/Engine.json"))
    manifest_paths = sorted((root / "Config/Apps").glob("*.json"))
    apps = [json.loads(read_text(path)) for path in manifest_paths]
    apps_by_id = {app["app_id"]: app for app in apps}

    cmake = read_text(root / "CMakeLists.txt")
    hello_cmake = read_text(root / "Source/Apps/HelloTask/CMakeLists.txt")
    life_cmake = read_text(root / "Source/Apps/LifeGame/CMakeLists.txt")
    life_header = read_text(
        root
        / "Source/Apps/LifeGame/Include/BraveNewWorld/LifeGame/LifeGameModel.hpp"
    )
    life_model = read_text(root / "Source/Apps/LifeGame/Source/LifeGameModel.cpp")
    life_main = read_text(root / "Source/Apps/LifeGame/Source/Main.cpp")
    life_tests = read_text(root / "Source/Apps/LifeGame/Tests/LifeGameModelTests.cpp")
    launcher = read_text(root / "Scripts/BraveNewWorld.py")
    readme = read_text(root / "README.md")
    architecture = read_text(root / "docs/ARCHITECTURE.md")
    development_log = read_text(root / "docs/DEVELOPMENT_LOG.md")

    assert engine["schema_version"] == "1.0"
    assert engine["integration"] == "supported-build-tree-consumer"
    assert re.fullmatch(r"[0-9a-f]{40}", engine["commit"])
    assert engine["commit"] in cmake

    assert len(apps_by_id) == len(apps), "Every App manifest must have a unique app_id."
    assert len({app["cmake_target"] for app in apps}) == len(
        apps
    ), "Every App manifest must have a unique CMake target."
    assert set(apps_by_id) == {"hello-task", "life-game"}

    hello = apps_by_id["hello-task"]
    assert hello["cmake_target"] == "BraveNewWorldHelloTask"
    assert hello["bounded_run"]["frames"] == 3
    assert hello["cmake_target"] in hello_cmake

    life = apps_by_id["life-game"]
    assert life["schema_version"] == "1.0"
    assert life["cmake_target"] == "BraveNewWorldLifeGame"
    assert life["model_test_target"] == "BraveNewWorldLifeGameModelTests"
    assert life["entrypoint"] == "./bnw run"
    assert life["grid"] == {
        "rows": 24,
        "columns": 24,
        "topology": "toroidal",
        "rules": "B3/S23",
        "seed": "fixed-glider",
    }
    assert set(life["controls"]) == {"pause/resume", "single-step", "reset"}
    assert life["bounded_run"]["frames"] == 12
    assert life["bounded_run"]["requires_input"] is False
    for marker in (
        "validation=requested/enabled",
        "errors=0",
        "presented=12",
        "generation=12",
        "live=5",
        "grid=24x24",
    ):
        assert marker in life["bounded_run"]["success_marker"]

    assert "add_subdirectory(Source/Apps/LifeGame)" in cmake
    assert life["cmake_target"] in cmake
    assert life["model_test_target"] in cmake
    assert "BraveNewWorldLifeGameModel" in life_cmake
    assert life["cmake_target"] in life_cmake
    assert life["model_test_target"] in life_cmake
    assert "BraveNewWorldLifeGameModel" in cmake

    for target in engine["public_targets"]:
        assert target in hello_cmake
        assert target in life_cmake
    assert set(re.findall(r"Anygine::[A-Za-z0-9_]+", life_cmake)) == set(
        engine["public_targets"]
    )

    life_sources = "\n".join((life_cmake, life_header, life_model, life_main, life_tests))
    assert not re.search(r"#include\s*[<\"][^>\"]*Private", life_sources)
    assert "FetchContent" not in life_sources
    assert "ExternalProject" not in life_sources
    assert "file(DOWNLOAD" not in life_sources
    assert "Source/Apps" not in " ".join(engine["public_targets"])

    for token in ("kRows = 24U", "kColumns = 24U", "SingleStep", "Reset", "Advance"):
        assert token in life_header
    for token in ("neighbors == 3U", "alive && neighbors == 2U", "Wrap"):
        assert token in life_model
    for case in (
        "TestBlinker",
        "TestGlider",
        "TestReset",
        "TestToroidalWrap",
        "TestPauseResumeAndSingleStep",
    ):
        assert case in life_tests

    for token in (
        "Generation:",
        "Live:",
        '"Pause"',
        '"Resume"',
        '"Single Step"',
        '"Reset"',
        "VulkanValidationMode::Required",
        "GetValidationDiagnostics",
        "kSmokeFrameCount = 12U",
    ):
        assert token in life_main

    run_app_body = launcher.split("def run_app", maxsplit=1)[1].split(
        "def parse_args", maxsplit=1
    )[0]
    assert "Source/Apps/LifeGame" in run_app_body
    assert "BraveNewWorldLifeGame" in run_app_body
    assert "HelloTask" not in run_app_body

    for document in (readme, architecture, development_log):
        assert "life-game" in document
        assert "B3/S23" in document
        assert "./bnw run" in document

    print(
        json.dumps(
            {
                "schema": "brave-new-world-manifest-contract-v1",
                "engine_commit": engine["commit"],
                "app_ids": sorted(apps_by_id),
                "default_app_id": "life-game",
                "life_game_model": "24x24-toroidal-B3/S23",
                "public_target_count": len(engine["public_targets"]),
                "passed": True,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
