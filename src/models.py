from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Facility:
    id: str
    name: str
    fixed_cost: int
    capacity: int


@dataclass(frozen=True)
class Customer:
    id: str
    name: str
    demand: int


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    facilities: tuple[Facility, ...]
    customers: tuple[Customer, ...]
    transport_costs: dict[str, dict[str, int]]

    @property
    def total_demand(self) -> int:
        return sum(customer.demand for customer in self.customers)

    @classmethod
    def from_json_file(cls, path: str | Path) -> "Scenario":
        with Path(path).open("r", encoding="utf-8") as file:
            return cls.from_dict(json.load(file))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Scenario":
        facilities = tuple(Facility(**item) for item in payload["facilities"])
        customers = tuple(Customer(**item) for item in payload["customers"])
        scenario = cls(
            name=payload.get("name", "Untitled Scenario"),
            description=payload.get("description", ""),
            facilities=facilities,
            customers=customers,
            transport_costs=payload["transport_costs"],
        )
        scenario.validate()
        return scenario

    def validate(self) -> None:
        if not self.facilities:
            raise ValueError("Scenario must include at least one facility.")
        if not self.customers:
            raise ValueError("Scenario must include at least one customer.")

        facility_ids = {facility.id for facility in self.facilities}
        customer_ids = {customer.id for customer in self.customers}

        if len(facility_ids) != len(self.facilities):
            raise ValueError("Facility IDs must be unique.")
        if len(customer_ids) != len(self.customers):
            raise ValueError("Customer IDs must be unique.")

        for facility in self.facilities:
            if facility.fixed_cost < 0:
                raise ValueError(f"Facility {facility.id} has a negative fixed cost.")
            if facility.capacity < 0:
                raise ValueError(f"Facility {facility.id} has a negative capacity.")

        for customer in self.customers:
            if customer.demand < 0:
                raise ValueError(f"Customer {customer.id} has a negative demand.")

        if sum(facility.capacity for facility in self.facilities) < self.total_demand:
            raise ValueError("Total facility capacity is less than total customer demand.")

        for facility_id in facility_ids:
            if facility_id not in self.transport_costs:
                raise ValueError(f"Missing transport costs for facility {facility_id}.")
            missing_customers = customer_ids - set(self.transport_costs[facility_id])
            if missing_customers:
                missing = ", ".join(sorted(missing_customers))
                raise ValueError(f"Missing customer transport costs for {facility_id}: {missing}.")
            for customer_id, cost in self.transport_costs[facility_id].items():
                if customer_id in customer_ids and cost < 0:
                    raise ValueError(
                        f"Transport cost from {facility_id} to {customer_id} is negative."
                    )
