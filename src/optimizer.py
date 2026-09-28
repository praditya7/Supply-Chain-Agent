from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import inf

from supply_chain_agent.models import Facility, Scenario


@dataclass(frozen=True)
class Shipment:
    facility_id: str
    customer_id: str
    quantity: int
    unit_cost: int

    @property
    def cost(self) -> int:
        return self.quantity * self.unit_cost


@dataclass(frozen=True)
class OptimizationResult:
    scenario_name: str
    opened_facilities: tuple[str, ...]
    shipments: tuple[Shipment, ...]
    fixed_cost: int
    transportation_cost: int

    @property
    def total_cost(self) -> int:
        return self.fixed_cost + self.transportation_cost


@dataclass
class _Edge:
    to: int
    reverse: int
    capacity: int
    cost: int


class _MinCostFlow:
    def __init__(self, node_count: int) -> None:
        self.graph: list[list[_Edge]] = [[] for _ in range(node_count)]

    def add_edge(self, source: int, target: int, capacity: int, cost: int) -> None:
        forward = _Edge(target, len(self.graph[target]), capacity, cost)
        reverse = _Edge(source, len(self.graph[source]), 0, -cost)
        self.graph[source].append(forward)
        self.graph[target].append(reverse)

    def solve(self, source: int, sink: int, required_flow: int) -> tuple[int, list[list[_Edge]]]:
        flow = 0
        cost = 0
        node_count = len(self.graph)

        while flow < required_flow:
            distance = [inf] * node_count
            previous_node = [-1] * node_count
            previous_edge = [-1] * node_count
            distance[source] = 0

            # Bellman-Ford is sufficient for this compact demo network.
            for _ in range(node_count - 1):
                updated = False
                for node, edges in enumerate(self.graph):
                    if distance[node] == inf:
                        continue
                    for edge_index, edge in enumerate(edges):
                        if edge.capacity <= 0:
                            continue
                        next_distance = distance[node] + edge.cost
                        if next_distance < distance[edge.to]:
                            distance[edge.to] = next_distance
                            previous_node[edge.to] = node
                            previous_edge[edge.to] = edge_index
                            updated = True
                if not updated:
                    break

            if distance[sink] == inf:
                raise ValueError("Unable to route all demand with the open facilities.")

            increment = required_flow - flow
            node = sink
            while node != source:
                edge = self.graph[previous_node[node]][previous_edge[node]]
                increment = min(increment, edge.capacity)
                node = previous_node[node]

            node = sink
            while node != source:
                edge = self.graph[previous_node[node]][previous_edge[node]]
                edge.capacity -= increment
                reverse_edge = self.graph[node][edge.reverse]
                reverse_edge.capacity += increment
                node = previous_node[node]

            flow += increment
            cost += increment * distance[sink]

        return cost, self.graph


class NetworkOptimizer:
    """Exact optimizer for small facility-location scenarios."""

    def solve(self, scenario: Scenario) -> OptimizationResult:
        best_result: OptimizationResult | None = None
        facilities = scenario.facilities

        for subset_size in range(1, len(facilities) + 1):
            for open_facilities in combinations(facilities, subset_size):
                if sum(facility.capacity for facility in open_facilities) < scenario.total_demand:
                    continue

                result = self._solve_for_open_facilities(scenario, open_facilities)
                if best_result is None or result.total_cost < best_result.total_cost:
                    best_result = result

        if best_result is None:
            raise ValueError("No feasible facility set found.")
        return best_result

    def _solve_for_open_facilities(
        self, scenario: Scenario, open_facilities: tuple[Facility, ...]
    ) -> OptimizationResult:
        facility_count = len(open_facilities)
        customer_count = len(scenario.customers)
        source = 0
        facility_start = 1
        customer_start = facility_start + facility_count
        sink = customer_start + customer_count

        flow = _MinCostFlow(sink + 1)

        for index, facility in enumerate(open_facilities):
            flow.add_edge(source, facility_start + index, facility.capacity, 0)

        lane_edge_refs: dict[tuple[str, str], tuple[int, int]] = {}
        for facility_index, facility in enumerate(open_facilities):
            facility_node = facility_start + facility_index
            for customer_index, customer in enumerate(scenario.customers):
                customer_node = customer_start + customer_index
                cost = scenario.transport_costs[facility.id][customer.id]
                edge_index = len(flow.graph[facility_node])
                flow.add_edge(facility_node, customer_node, scenario.total_demand, cost)
                lane_edge_refs[(facility.id, customer.id)] = (facility_node, edge_index)

        for index, customer in enumerate(scenario.customers):
            flow.add_edge(customer_start + index, sink, customer.demand, 0)

        transportation_cost, residual_graph = flow.solve(source, sink, scenario.total_demand)
        shipments = []
        for facility in open_facilities:
            for customer in scenario.customers:
                node, edge_index = lane_edge_refs[(facility.id, customer.id)]
                edge = residual_graph[node][edge_index]
                quantity = residual_graph[edge.to][edge.reverse].capacity
                if quantity > 0:
                    shipments.append(
                        Shipment(
                            facility_id=facility.id,
                            customer_id=customer.id,
                            quantity=quantity,
                            unit_cost=scenario.transport_costs[facility.id][customer.id],
                        )
                    )

        fixed_cost = sum(facility.fixed_cost for facility in open_facilities)
        return OptimizationResult(
            scenario_name=scenario.name,
            opened_facilities=tuple(facility.id for facility in open_facilities),
            shipments=tuple(shipments),
            fixed_cost=fixed_cost,
            transportation_cost=transportation_cost,
        )
