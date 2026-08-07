from __future__ import annotations

import math
import platform

from brave_new_world.contracts import SimulationRequest, SimulationTrace, TracePoint


ENGINE_VERSION = "first-order-exact-v1"


def simulate_first_order(request: SimulationRequest) -> SimulationTrace:
    """Simulate tau*dy/dt + y = gain*u with a zero-time step input.

    The state transition is the exact zero-order-hold discretization. Fixed input,
    request, and engine version therefore produce byte-stable JSON values.
    """

    request.validate()
    target = request.gain * request.input_amplitude
    decay = math.exp(-request.dt_s / request.time_constant_s)
    output = request.initial_output
    points = [TracePoint(time_s=0.0, input=request.input_amplitude, output=output)]

    for index in range(1, request.step_count + 1):
        output = target + (output - target) * decay
        points.append(
            TracePoint(
                time_s=round(index * request.dt_s, 12),
                input=request.input_amplitude,
                output=output,
            )
        )

    final_output = points[-1].output
    metrics = {
        "steady_state_target": target,
        "final_output": final_output,
        "final_error": target - final_output,
        "sample_count": len(points),
    }
    return SimulationTrace(
        schema_version="1.0",
        engine_version=ENGINE_VERSION,
        runtime_version=f"Python {platform.python_version()}",
        demo_id=request.demo_id,
        request=request,
        points=tuple(points),
        metrics=metrics,
    )
