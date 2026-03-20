#!/usr/bin/env python3
"""
Evaluate game traces: EV, BB/100, adaptation score.

Usage:
  python scripts/evaluate.py traces/
  python scripts/evaluate.py traces/game_20260320_104048.json
"""

import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pokerbench.evaluation import (
    adaptation_score,
    aggregate_evals,
    eval_trace,
    load_trace,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/evaluate.py <traces_dir_or_file>")
        sys.exit(1)
    path = Path(sys.argv[1])
    if path.is_file():
        files = [path]
    else:
        files = sorted(path.glob("game_*.json"))
    if not files:
        print(f"No game traces found in {path}")
        sys.exit(1)

    evals = []
    for f in files:
        trace = load_trace(f)
        e = eval_trace(trace)
        evals.append(e)
        print(f"\n{e.game_id} ({e.hands_played} hands)")
        print("  Chips won:", e.chips_won)
        print("  BB/100:   ", {k: f"{v:.1f}" for k, v in e.bb_per_100.items()})
        adapt = adaptation_score(trace, e.big_blind)
        print("  Adaptation (late - early BB/100):", {k: f"{v:.1f}" for k, v in adapt.items()})

    if len(evals) > 1:
        agg = aggregate_evals(evals)
        print("\n=== Aggregate ===")
        for p, v in agg.items():
            print(f"  {p}: mean_chips={v['mean_chips']:.0f}, mean_BB/100={v['mean_bb_per_100']:.1f}")


if __name__ == "__main__":
    main()
