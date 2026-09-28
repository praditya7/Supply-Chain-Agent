from __future__ import annotations

import argparse

from supply_chain_agent.agent import SupplyChainAgent
from supply_chain_agent.models import Scenario


DEFAULT_REQUEST = "Find the lowest-cost facility network and explain the recommendation."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an AI-assisted supply-chain network optimization scenario."
    )
    parser.add_argument(
        "--scenario",
        default="data/sample_scenario.json",
        help="Path to a scenario JSON file.",
    )
    parser.add_argument(
        "--request",
        default=DEFAULT_REQUEST,
        help="Natural-language business request for the agent.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    scenario = Scenario.from_json_file(args.scenario)
    response = SupplyChainAgent().answer(args.request, scenario)
    print(response.explanation)


if __name__ == "__main__":
    main()
