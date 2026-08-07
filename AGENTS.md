# Repository instructions

## Product boundary

BraveNewWorld is a teaching, visualization, and lightweight-simulation product. It is also an external JobSlayer testbed, but it does not own JobSlayer workflow state, permissions, approval, or completion decisions.

## Development rules

- Interactive and headless execution must call the same simulation kernel.
- Keep simulation results deterministic for the same version and request.
- Keep domain contracts independent from browser and HTTP implementation details.
- The UI must expose only implemented behavior and values returned by the simulation API.
- Record every material decision and implementation step in `docs/DEVELOPMENT_LOG.md`; use an ADR for durable architectural decisions.
- Do not add a runtime dependency without documenting the need and exit condition.

## Verification

Run the complete local suite before reporting completion:

```bash
./bnw check
```
