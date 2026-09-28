# Example Output

Command:

```bash
PYTHONPATH=src python -m supply_chain_agent.cli --scenario data/sample_scenario.json
```

Representative output:

```text
Request: Find the lowest-cost facility network and explain the recommendation.

Recommendation: Open 2 facilities: Jaipur DC (JPR), Lucknow DC (LKO).
Estimated total cost is 23,410 (17,500 fixed + 5,910 transportation).

Allocation plan:
- Jaipur DC -> Bhopal: 10 units at 9/unit = 90
- Jaipur DC -> Gurugram: 300 units at 6/unit = 1,800
- Jaipur DC -> Jaipur: 280 units at 3/unit = 840
- Lucknow DC -> Bhopal: 210 units at 8/unit = 1,680
- Lucknow DC -> Kanpur: 180 units at 4/unit = 720
- Lucknow DC -> Lucknow: 260 units at 3/unit = 780

Managerial readout:
- Jaipur DC uses 590/600 capacity (98% utilization).
- Lucknow DC uses 650/650 capacity (100% utilization).
- The recommendation minimizes cost for the provided data while meeting all demand.
- Assumption: lane costs, demand, and capacity are accurate for this planning run.
```
