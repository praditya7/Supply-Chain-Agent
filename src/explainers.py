from __future__ import annotations

from typing import Protocol

from supply_chain_agent.models import Scenario
from supply_chain_agent.optimizer import OptimizationResult


class Explainer(Protocol):
    def explain(self, request: str, scenario: Scenario, result: OptimizationResult) -> str:
        """Return a business-facing explanation for an optimization result."""


class RuleBasedExplainer:
    """Free default explainer used when no optional LLM provider is configured."""

    def explain(self, request: str, scenario: Scenario, result: OptimizationResult) -> str:
        facility_names = {facility.id: facility.name for facility in scenario.facilities}
        customer_names = {customer.id: customer.name for customer in scenario.customers}
        capacity_by_facility = {facility.id: facility.capacity for facility in scenario.facilities}

        opened = ", ".join(
            f"{facility_names[facility_id]} ({facility_id})"
            for facility_id in result.opened_facilities
        )

        lines = [
            f"Request: {request}",
            "",
            f"Recommendation: Open {len(result.opened_facilities)} facilities: {opened}.",
            (
                f"Estimated total cost is {result.total_cost:,} "
                f"({result.fixed_cost:,} fixed + {result.transportation_cost:,} transportation)."
            ),
            "",
            "Allocation plan:",
        ]

        for shipment in sorted(
            result.shipments, key=lambda item: (item.facility_id, item.customer_id)
        ):
            lines.append(
                "- "
                f"{facility_names[shipment.facility_id]} -> {customer_names[shipment.customer_id]}: "
                f"{shipment.quantity} units at {shipment.unit_cost}/unit "
                f"= {shipment.cost:,}"
            )

        lines.extend(["", "Managerial readout:"])
        for facility_id in result.opened_facilities:
            used_capacity = sum(
                shipment.quantity
                for shipment in result.shipments
                if shipment.facility_id == facility_id
            )
            utilization = used_capacity / capacity_by_facility[facility_id]
            lines.append(
                "- "
                f"{facility_names[facility_id]} uses {used_capacity}/"
                f"{capacity_by_facility[facility_id]} capacity "
                f"({utilization:.0%} utilization)."
            )

        lines.extend(
            [
                "- The recommendation minimizes cost for the provided data while meeting all demand.",
                "- Assumption: lane costs, demand, and capacity are accurate for this planning run.",
            ]
        )

        return "\n".join(lines)
