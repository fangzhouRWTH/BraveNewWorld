import unittest

from brave_new_world.contracts import ContractError, Scenario, SimulationRequest


class SimulationRequestTests(unittest.TestCase):
    def test_accepts_a_valid_request(self) -> None:
        request = SimulationRequest.from_mapping({"duration_s": 2, "dt_s": 0.1})
        self.assertEqual(request.step_count, 20)

    def test_rejects_unknown_fields(self) -> None:
        with self.assertRaisesRegex(ContractError, "unknown request fields"):
            SimulationRequest.from_mapping({"renderer": "fake"})

    def test_rejects_non_integral_step_count(self) -> None:
        with self.assertRaisesRegex(ContractError, "integer multiple"):
            SimulationRequest.from_mapping({"duration_s": 1, "dt_s": 0.3})

    def test_rejects_excessive_trace(self) -> None:
        with self.assertRaisesRegex(ContractError, "5000-step"):
            SimulationRequest.from_mapping({"duration_s": 10, "dt_s": 0.001})

    def test_direct_request_rejects_non_finite_value_at_simulation_boundary(self) -> None:
        with self.assertRaisesRegex(ContractError, "finite number"):
            SimulationRequest(input_amplitude=float("nan")).validate()


class ScenarioTests(unittest.TestCase):
    def test_accepts_a_versioned_scenario(self) -> None:
        scenario = Scenario.from_mapping(
            {
                "schema_version": "1.0",
                "scenario_id": "default-step",
                "title": "Default step",
                "request": {"duration_s": 1, "dt_s": 0.1},
            }
        )
        self.assertEqual(scenario.request.step_count, 10)

    def test_rejects_unknown_scenario_version(self) -> None:
        with self.assertRaisesRegex(ContractError, "schema_version"):
            Scenario.from_mapping(
                {
                    "schema_version": "2.0",
                    "scenario_id": "future",
                    "title": "Future",
                    "request": {},
                }
            )


if __name__ == "__main__":
    unittest.main()
