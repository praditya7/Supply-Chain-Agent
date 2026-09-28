import unittest

from supply_chain_agent.models import Customer, Facility, Scenario
from supply_chain_agent.optimizer import NetworkOptimizer


class NetworkOptimizerTests(unittest.TestCase):
    def test_optimizer_selects_lowest_total_cost_network(self) -> None:
        scenario = Scenario(
            name="Test",
            description="Small scenario",
            facilities=(
                Facility(id="A", name="Facility A", fixed_cost=100, capacity=10),
                Facility(id="B", name="Facility B", fixed_cost=20, capacity=10),
            ),
            customers=(
                Customer(id="C1", name="Customer 1", demand=5),
                Customer(id="C2", name="Customer 2", demand=5),
            ),
            transport_costs={
                "A": {"C1": 1, "C2": 1},
                "B": {"C1": 4, "C2": 4},
            },
        )

        result = NetworkOptimizer().solve(scenario)

        self.assertEqual(result.opened_facilities, ("B",))
        self.assertEqual(result.fixed_cost, 20)
        self.assertEqual(result.transportation_cost, 40)
        self.assertEqual(result.total_cost, 60)

    def test_optimizer_opens_multiple_facilities_when_capacity_requires_it(self) -> None:
        scenario = Scenario(
            name="Capacity Test",
            description="Capacity constrained scenario",
            facilities=(
                Facility(id="A", name="Facility A", fixed_cost=10, capacity=5),
                Facility(id="B", name="Facility B", fixed_cost=10, capacity=5),
            ),
            customers=(Customer(id="C1", name="Customer 1", demand=10),),
            transport_costs={
                "A": {"C1": 1},
                "B": {"C1": 1},
            },
        )

        result = NetworkOptimizer().solve(scenario)

        self.assertEqual(set(result.opened_facilities), {"A", "B"})
        self.assertEqual(sum(shipment.quantity for shipment in result.shipments), 10)


if __name__ == "__main__":
    unittest.main()
