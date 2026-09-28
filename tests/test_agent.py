import unittest

from supply_chain_agent.agent import SupplyChainAgent
from supply_chain_agent.models import Customer, Facility, Scenario
from supply_chain_agent.optimizer import OptimizationResult


class StaticExplainer:
    def explain(
        self, request: str, scenario: Scenario, result: OptimizationResult
    ) -> str:
        return f"custom explanation for {scenario.name}: {result.total_cost}"


class SupplyChainAgentTests(unittest.TestCase):
    def test_agent_returns_managerial_explanation(self) -> None:
        scenario = Scenario(
            name="Agent Test",
            description="Tiny scenario",
            facilities=(Facility(id="A", name="Facility A", fixed_cost=10, capacity=5),),
            customers=(Customer(id="C1", name="Customer 1", demand=5),),
            transport_costs={"A": {"C1": 2}},
        )

        response = SupplyChainAgent().answer("Open the best network.", scenario)

        self.assertIn("Recommendation", response.explanation)
        self.assertIn("Facility A", response.explanation)
        self.assertEqual(response.result.total_cost, 20)

    def test_agent_accepts_pluggable_explainer(self) -> None:
        scenario = Scenario(
            name="Agent Test",
            description="Tiny scenario",
            facilities=(Facility(id="A", name="Facility A", fixed_cost=10, capacity=5),),
            customers=(Customer(id="C1", name="Customer 1", demand=5),),
            transport_costs={"A": {"C1": 2}},
        )

        response = SupplyChainAgent(explainer=StaticExplainer()).answer(
            "Open the best network.", scenario
        )

        self.assertEqual(response.explanation, "custom explanation for Agent Test: 20")


if __name__ == "__main__":
    unittest.main()
