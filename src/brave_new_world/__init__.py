"""BraveNewWorld deterministic teaching simulation package."""

from brave_new_world.contracts import (
    DemoManifest,
    Scenario,
    SimulationRequest,
    SimulationTrace,
    TracePoint,
)
from brave_new_world.simulation.first_order import simulate_first_order

__all__ = [
    "DemoManifest",
    "Scenario",
    "SimulationRequest",
    "SimulationTrace",
    "TracePoint",
    "simulate_first_order",
]

__version__ = "0.0.1"
