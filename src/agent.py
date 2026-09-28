from __future__ import annotations

from dataclasses import dataclass

from supply_chain_agent.explainers import Explainer, RuleBasedExplainer
from supply_chain_agent.models import Scenario
from supply_chain_agent.optimizer import NetworkOptimizer, OptimizationResult


@dataclass(frozen=True)
class AgentResponse:
    request: str
    result: OptimizationResult
    explanation: str


class SupplyChainAgent:
    def __init__(
        self,
        optimizer: NetworkOptimizer | None = None,
        explainer: Explainer | None = None,
    ) -> None:
        self.optimizer = optimizer or NetworkOptimizer()
        self.explainer = explainer or RuleBasedExplainer()

    def answer(self, request: str, scenario: Scenario) -> AgentResponse:
        result = self.optimizer.solve(scenario)
        explanation = self.explainer.explain(request=request, scenario=scenario, result=result)
        return AgentResponse(request=request, result=result, explanation=explanation)
