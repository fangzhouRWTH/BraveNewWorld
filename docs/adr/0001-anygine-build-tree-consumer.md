# ADR-0001: BraveNewWorld consumes a pinned Anygine build tree

- Status: accepted
- Date: 2026-09-01

## Context

BraveNewWorld is being reset from a browser-based mechatronic simulation into a sequence of small
native Apps for validating JobSlayer task planning and execution feedback. Anygine already owns the
engine, renderer, simulation, and UI foundations and exposes a reviewed external build-tree consumer
boundary.

## Decision

BraveNewWorld remains the top-level CMake project and registers an absolute, pinned Anygine source
worktree with `add_subdirectory`. Apps link only reviewed public `Anygine::*` targets. The engine is
not vendored, fetched implicitly, patched, or accessed through private include paths.

The source commit is fixed in `Config/Engine.json` and checked again during CMake configure. A
revision change is an explicit project decision that must update the contract, validation evidence,
and JobSlayer execution target.

## Consequences

- Small Apps can reuse the real engine without turning BraveNewWorld into an Anygine fork.
- Local and CI builders must supply a prepared Anygine checkout and compatible Conan toolchain.
- The current contract is source/build-tree integration, not a relocatable installed package.
- Anygine private or first-party App APIs remain unavailable to BraveNewWorld.
