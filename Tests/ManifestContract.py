from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    engine = json.loads((root / "Config/Engine.json").read_text(encoding="utf-8"))
    app = json.loads((root / "Config/Apps/hello-task.json").read_text(encoding="utf-8"))
    cmake = (root / "CMakeLists.txt").read_text(encoding="utf-8")
    app_cmake = (root / "Source/Apps/HelloTask/CMakeLists.txt").read_text(encoding="utf-8")

    assert engine["schema_version"] == "1.0"
    assert engine["integration"] == "supported-build-tree-consumer"
    assert re.fullmatch(r"[0-9a-f]{40}", engine["commit"])
    assert engine["commit"] in cmake
    assert app["app_id"] == "hello-task"
    assert app["cmake_target"] == "BraveNewWorldHelloTask"
    assert app["bounded_run"]["frames"] == 3
    assert app["cmake_target"] in app_cmake

    for target in engine["public_targets"]:
        assert target in app_cmake
    assert "/Private" not in app_cmake
    assert "Source/Apps" not in " ".join(engine["public_targets"])

    print(
        json.dumps(
            {
                "schema": "brave-new-world-manifest-contract-v1",
                "engine_commit": engine["commit"],
                "app_id": app["app_id"],
                "public_target_count": len(engine["public_targets"]),
                "passed": True,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
