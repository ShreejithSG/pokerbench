#!/usr/bin/env python3
"""
Run a benchmark: multiple games with configurable personas/models.
Outputs aggregated results to JSON for handover/reporting.
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import argparse
import json
import sys
from datetime import datetime

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from run import run_game


def main():
    parser = argparse.ArgumentParser(description="Run poker benchmark (multiple games)")
    parser.add_argument("--games", "-g", type=int, default=5, help="Number of games to run")
    parser.add_argument("--rounds", "-r", type=int, default=10, help="Hands per game")
    parser.add_argument("--players", "-p", type=int, default=3, help="Players per game")
    parser.add_argument(
        "--personas",
        nargs="+",
        default=None,
        help="Personas per seat (e.g. tag lag passive). Omit for random.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("benchmark_results"),
        help="Output directory",
    )
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    results = []
    base_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    for i in range(args.games):
        seed = (args.seed + i) if args.seed is not None else None
        trace = run_game(
            players=args.players,
            rounds=args.rounds,
            use_random=True,
            models=None,
            personas=args.personas,
            seed=seed,
            output_dir=args.output / "traces",
            quiet=True,
            game_id=f"{base_id}_g{i}",
        )
        winner = max(trace.final_stacks, key=trace.final_stacks.get)
        results.append({
            "game_id": trace.game_id,
            "winner": winner,
            "final_stacks": trace.final_stacks,
            "hands_played": len(trace.hands),
        })

    summary = {
        "benchmark_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "config": {
            "games": args.games,
            "rounds_per_game": args.rounds,
            "players": args.players,
            "personas": args.personas,
            "seed": args.seed,
        },
        "results": results,
        "winner_counts": {},
    }
    for r in results:
        w = r["winner"]
        summary["winner_counts"][w] = summary["winner_counts"].get(w, 0) + 1

    out_path = args.output / "benchmark_summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nBenchmark summary saved to {out_path}")
    print("Winner counts:", summary["winner_counts"])


if __name__ == "__main__":
    main()
