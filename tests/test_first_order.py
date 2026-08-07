import math
import unittest

from brave_new_world.contracts import SimulationRequest
from brave_new_world.simulation.first_order import simulate_first_order


class FirstOrderSimulationTests(unittest.TestCase):
    def test_matches_analytic_step_response(self) -> None:
        request = SimulationRequest(duration_s=2.0, dt_s=0.1, time_constant_s=0.5)
        trace = simulate_first_order(request)
        expected = 1.0 - math.exp(-2.0 / 0.5)
        self.assertAlmostEqual(trace.points[-1].output, expected, places=14)

    def test_response_is_monotonic_toward_positive_target(self) -> None:
        trace = simulate_first_order(SimulationRequest())
        outputs = [point.output for point in trace.points]
        self.assertTrue(all(left <= right for left, right in zip(outputs, outputs[1:])))
        self.assertLess(outputs[-1], 1.0)

    def test_same_request_has_same_trace_hash(self) -> None:
        request = SimulationRequest(gain=2.0, input_amplitude=-0.5)
        self.assertEqual(
            simulate_first_order(request).trace_hash,
            simulate_first_order(request).trace_hash,
        )

    def test_trace_includes_initial_and_final_samples(self) -> None:
        trace = simulate_first_order(SimulationRequest(duration_s=1.0, dt_s=0.25))
        self.assertEqual(len(trace.points), 5)
        self.assertEqual(trace.points[0].time_s, 0.0)
        self.assertEqual(trace.points[-1].time_s, 1.0)


if __name__ == "__main__":
    unittest.main()
