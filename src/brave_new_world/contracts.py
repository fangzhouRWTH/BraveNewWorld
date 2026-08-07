from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Mapping


class ContractError(ValueError):
    """Raised when a simulation request violates its public contract."""


def _number(payload: Mapping[str, Any], key: str, default: float) -> float:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{key} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ContractError(f"{key} must be a finite number")
    return result


@dataclass(frozen=True, slots=True)
class SimulationRequest:
    """Versioned input for the first-order step-response demo."""

    demo_id: str = "first-order-step"
    duration_s: float = 5.0
    dt_s: float = 0.05
    input_amplitude: float = 1.0
    time_constant_s: float = 0.8
    gain: float = 1.0
    initial_output: float = 0.0

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> SimulationRequest:
        allowed = {
            "demo_id",
            "duration_s",
            "dt_s",
            "input_amplitude",
            "time_constant_s",
            "gain",
            "initial_output",
        }
        unknown = set(payload) - allowed
        if unknown:
            raise ContractError(f"unknown request fields: {', '.join(sorted(unknown))}")
        demo_id = payload.get("demo_id", "first-order-step")
        if demo_id != "first-order-step":
            raise ContractError(f"unsupported demo_id: {demo_id!r}")
        request = cls(
            demo_id=demo_id,
            duration_s=_number(payload, "duration_s", 5.0),
            dt_s=_number(payload, "dt_s", 0.05),
            input_amplitude=_number(payload, "input_amplitude", 1.0),
            time_constant_s=_number(payload, "time_constant_s", 0.8),
            gain=_number(payload, "gain", 1.0),
            initial_output=_number(payload, "initial_output", 0.0),
        )
        request.validate()
        return request

    def validate(self) -> None:
        if self.demo_id != "first-order-step":
            raise ContractError(f"unsupported demo_id: {self.demo_id!r}")
        for key in (
            "duration_s",
            "dt_s",
            "input_amplitude",
            "time_constant_s",
            "gain",
            "initial_output",
        ):
            value = getattr(self, key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ContractError(f"{key} must be a finite number")
            if not math.isfinite(value):
                raise ContractError(f"{key} must be a finite number")
        if self.duration_s <= 0:
            raise ContractError("duration_s must be greater than zero")
        if self.dt_s <= 0:
            raise ContractError("dt_s must be greater than zero")
        if self.time_constant_s <= 0:
            raise ContractError("time_constant_s must be greater than zero")
        ratio = self.duration_s / self.dt_s
        steps = round(ratio)
        if steps < 1:
            raise ContractError("duration_s must include at least one simulation step")
        if steps > 5000:
            raise ContractError("request exceeds the 5000-step teaching limit")
        if not math.isclose(ratio, steps, rel_tol=0.0, abs_tol=1e-9):
            raise ContractError("duration_s must be an integer multiple of dt_s")

    @property
    def step_count(self) -> int:
        return round(self.duration_s / self.dt_s)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TracePoint:
    time_s: float
    input: float
    output: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SimulationTrace:
    schema_version: str
    engine_version: str
    runtime_version: str
    demo_id: str
    request: SimulationRequest
    points: tuple[TracePoint, ...]
    metrics: Mapping[str, float | int]

    def _payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "engine_version": self.engine_version,
            "runtime_version": self.runtime_version,
            "demo_id": self.demo_id,
            "request": self.request.to_dict(),
            "points": [point.to_dict() for point in self.points],
            "metrics": dict(self.metrics),
        }

    @property
    def trace_hash(self) -> str:
        encoded = json.dumps(
            self._payload(), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload["trace_hash"] = self.trace_hash
        return payload


@dataclass(frozen=True, slots=True)
class DemoManifest:
    id: str
    version: str
    title: str
    summary: str
    learning_objectives: tuple[str, ...]
    parameter_names: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["learning_objectives"] = list(self.learning_objectives)
        payload["parameter_names"] = list(self.parameter_names)
        return payload


@dataclass(frozen=True, slots=True)
class Scenario:
    """A named, versioned, reproducible simulation request."""

    schema_version: str
    scenario_id: str
    title: str
    request: SimulationRequest

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> Scenario:
        allowed = {"schema_version", "scenario_id", "title", "request"}
        unknown = set(payload) - allowed
        if unknown:
            raise ContractError(f"unknown scenario fields: {', '.join(sorted(unknown))}")
        schema_version = payload.get("schema_version")
        scenario_id = payload.get("scenario_id")
        title = payload.get("title")
        request_payload = payload.get("request")
        if schema_version != "1.0":
            raise ContractError("scenario schema_version must be '1.0'")
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            raise ContractError("scenario_id must be a non-empty string")
        if not isinstance(title, str) or not title.strip():
            raise ContractError("scenario title must be a non-empty string")
        if not isinstance(request_payload, Mapping):
            raise ContractError("scenario request must be an object")
        return cls(
            schema_version=schema_version,
            scenario_id=scenario_id,
            title=title,
            request=SimulationRequest.from_mapping(request_payload),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "scenario_id": self.scenario_id,
            "title": self.title,
            "request": self.request.to_dict(),
        }
