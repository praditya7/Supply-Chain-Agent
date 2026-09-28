# AI-Assisted Supply Chain Network Optimization Agent

A small, runnable portfolio project that combines deterministic optimization with a lightweight AI-style agent layer. The system reads a supply-chain scenario, chooses which facilities to open, allocates customer demand, and returns a concise managerial explanation.

This project is designed for AI/APM portfolio use cases where the goal is to show practical AI-assisted decision support without requiring paid APIs or proprietary solvers.

## What It Solves

Given:

- Candidate facilities with fixed opening costs and capacity
- Customers with demand
- Per-unit transportation costs from each facility to each customer

The optimizer decides:

- Which facilities to open
- How much demand each open facility should serve
- The minimum total cost, including fixed facility cost and transportation cost

Subject to:

- Every customer's demand must be satisfied
- No facility can exceed its capacity
- Closed facilities cannot ship

## Agent Layer

The agent accepts a business request such as:

> Find the lowest-cost network and explain which facilities we should open.

It then:

1. Loads the structured scenario data.
2. Runs the optimizer.
3. Produces a concise business explanation with cost breakdown, opened facilities, allocation plan, risks, and assumptions.

No LLM is required by default. The explanation layer is deterministic so the project runs locally and in CI. The agent accepts a pluggable explainer object, so an LLM-based explainer can be added later without changing the optimization engine.

## Repository Structure

```text
.
├── data/
│   └── sample_scenario.json
├── examples/
│   └── example_output.md
├── src/
│   └── supply_chain_agent/
│       ├── __init__.py
│       ├── agent.py
│       ├── cli.py
│       ├── explainers.py
│       ├── models.py
│       └── optimizer.py
├── tests/
│   ├── test_agent.py
│   └── test_optimizer.py
├── requirements.txt
└── README.md
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run the sample scenario:

```bash
python -m supply_chain_agent.cli --scenario data/sample_scenario.json
```

Run with a business request:

```bash
python -m supply_chain_agent.cli --scenario data/sample_scenario.json --request "Minimize cost while keeping the explanation executive-friendly"
```

Run tests:

```bash
python -m unittest discover -s tests
```

If you do not install the package and want to run directly from source, set `PYTHONPATH` first:

```bash
$env:PYTHONPATH="src"
python -m supply_chain_agent.cli --scenario data/sample_scenario.json
```

## Example Result

For the included sample scenario, the optimizer opens the lowest-cost feasible network and allocates demand across customers. See [examples/example_output.md](examples/example_output.md) for a representative output.

## Architecture

The project has three layers:

- **Scenario model:** Validates facilities, customers, transportation costs, and feasibility basics.
- **Optimization engine:** Enumerates possible facility-opening combinations and solves customer allocation for each feasible combination using a pure-Python min-cost flow algorithm.
- **Agent interface:** Turns a natural-language request plus structured scenario into a business-facing decision summary.
- **Explainer interface:** Uses a free rule-based explainer by default, while allowing optional LLM explainers through dependency injection.

## Optimization Approach

For a portfolio-scale problem, exhaustive enumeration is simple and explainable:

1. Generate each possible subset of open facilities.
2. Skip subsets whose capacity cannot meet total demand.
3. For each feasible subset, solve the transportation allocation using min-cost flow.
4. Add fixed opening costs to transportation costs.
5. Return the lowest-cost solution.

This is exact for the given scenario size and avoids requiring commercial optimization software.

## Assumptions

- Transportation costs are linear per shipped unit.
- Facility fixed costs are incurred only when a facility is opened.
- Demand must be fully satisfied.
- Facility capacities are hard constraints.
- The sample data uses integer demand and capacity values.
- The optimizer is intended for small to medium demo scenarios, not enterprise-scale production planning.

## Limitations

- Exhaustive facility enumeration grows exponentially with the number of candidate facilities.
- The current model does not include multi-period planning, inventory, service-level constraints, carbon cost, labor availability, or facility opening lead times.
- The default agent explanation is rule-based rather than powered by a live LLM.
- The parser does not infer complete scenarios from free text; structured JSON remains the source of truth.

## Future Extensions

- Add an optional LLM explainer that rewrites the deterministic summary for different audiences using an API key only when explicitly configured.
- Support CSV or spreadsheet uploads for facilities, customers, and lane costs.
- Add service-level constraints such as maximum distance or delivery time.
- Add carbon emissions and sustainability trade-offs.
- Replace enumeration with a MILP backend such as PuLP, OR-Tools, or Gurobi for larger problems.
- Build a Streamlit or FastAPI interface for interactive scenario comparison.

## Why This Fits an AI/APM Portfolio

This project demonstrates how AI can support an operational business decision:

- It combines structured optimization with natural-language interaction.
- It produces explainable recommendations, not just raw model output.
- It is practical for supply-chain, marketplace, logistics, and operations roles.
- It leaves clear room for agentic workflows, RAG over planning documents, and optional LLM-based explanation.
