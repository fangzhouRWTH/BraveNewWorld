# Development Log

This file is append-only from the Anygine testbed reset. Earlier web/simulation history remains
recoverable from Git history and the offline pre-reset archive.

## 2026-09-01 — Reset as an Anygine small-App testbed

- Retired the Python/browser mechatronic-simulation product direction.
- Defined BraveNewWorld as a collection of bounded native Apps used to validate JobSlayer planning,
  serialized execution, verification, and feedback.
- Selected Anygine's reviewed source/build-tree consumer contract instead of copying engine code or
  using private include paths.
- Pinned Anygine `main` at `28b4934c24fdad6b8f45b945a89a6ada51703f5d`.
- Added `hello-task`, a minimal public Engine/Vulkan/Renderer/UI consumer with a three-frame smoke.
- Added a cross-platform Python dispatcher, manifest contract check, project documentation, and
  ADR-0001.

### Reset and archive evidence

- Fast-forwarded the local `main` from `fb43878c9f0164deef272e55969c0fc134a6d6a3` to the existing
  remote `main` commit `fb49bf6322b0935dd8e0006015df1c63543bb249` before replacement.
- Archived all refs, committed suspension work, and the three registered JobSlayer worktrees at
  `/home/fangzhou/projects/JobSlayer/TestProjects/Archive/BraveNewWorld-pre-anygine-20260901`.
- `repository.bundle` SHA-256:
  `8ce7aa8f9d24aadd54fa9904e009f38b538682b872138247055090bb91a27273`; `git bundle verify`
  reported a complete history with 10 refs.
- `worktrees.tar.gz` SHA-256:
  `c5db1692b236717b09d3a0f0d55e9d955968b497e658322631d5064a129792fc`; this retains the two
  dirty legacy worktrees before their explicit removal.

### Verification

- `./bnw contract`: passed and reported the fixed engine commit, `hello-task`, five public targets,
  and `passed=true`.
- `./bnw doctor --engine-root /home/fangzhou/projects/Anygine/Anygine_JobSlayer --toolchain
  /home/fangzhou/projects/Anygine/Anygine/build/conan/conan_toolchain.cmake`: passed; Git, CMake,
  CTest, the exact Anygine commit, and Conan toolchain were ready.
- `./bnw test` with the same engine/toolchain arguments and `--jobs 4`: cold configure/build passed;
  `BraveNewWorldHelloTask` and `BraveNewWorldBuildAll` reached 100%, and CTest passed 1/1 manifest
  contract test.
- `./bnw run` with the same arguments: incremental build passed; the real RTX 5080 Vulkan run used
  Required validation, initialized the public Renderer and ImGui UI context, presented exactly three
  frames, and reported zero validation errors.
- `python3 -m py_compile Scripts/BraveNewWorld.py Tests/ManifestContract.py` and
  `git diff --check`: passed.

### Limitations and next step

- The supported Anygine boundary is currently a source/build-tree consumer, so builders must provide
  a prepared engine checkout and compatible Conan toolchain; it is not yet a relocatable package.
- `Anygine::RendererCore` currently pulls a broad Scene/Generation dependency closure, making the
  first clean build much larger than the App itself. This is visible engine dependency debt, not a
  reason for BraveNewWorld to reach into private targets.
- `hello-task` is a build/runtime contract fixture rather than a user-facing experiment. The next
  JobSlayer trial should plan one genuinely small interactive App against this baseline.
