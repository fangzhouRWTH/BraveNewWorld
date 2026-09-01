# Repository instructions

## Product boundary

BraveNewWorld is a small-application testbed for JobSlayer. It consumes Anygine through its public
build-tree interface, but it does not own Anygine internals or JobSlayer workflow truth.

## Development rules

- Keep every experiment as a bounded app with an explicit manifest and deterministic acceptance checks.
- Link only reviewed public `Anygine::*` CMake targets. Do not copy Anygine sources, include private
  engine directories, or mutate the engine checkout from this repository.
- Keep the Anygine source commit pinned in `Config/Engine.json` and in the configure gate.
- Keep applications thin; reusable behavior belongs in a BraveNewWorld library only after two apps
  demonstrate the same need.
- Record every material decision and implementation step append-only in `docs/DEVELOPMENT_LOG.md`;
  use an ADR for durable architectural decisions.
- JobSlayer remains the owner of task state, permissions, retry, approval, verification policy, and
  completion decisions.

## Verification

Run the complete local suite before reporting completion:

```bash
./bnw check --engine-root /absolute/path/to/Anygine
```
