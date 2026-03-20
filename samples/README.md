# Sample Outputs

Example game traces and benchmark results from PokerBench.

- `game_persona_demo.json` – Example game with TAG/LAG/Passive personas
- `benchmark_summary.json` – Aggregated results from `scripts/run_benchmark.py`

Generate new outputs:
- `python run.py --personas tag lag passive --rounds 10`
- `python scripts/run_benchmark.py --games 5 --personas tag lag passive`
