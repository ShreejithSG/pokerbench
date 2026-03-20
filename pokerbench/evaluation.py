"""Evaluation metrics for strategic play vs blind/random play.

Distinguishes:
- Value betting: betting with strong hands (expected)
- Bluffing: betting with weak hands when fold equity exists (strategic)
- Blind bluffing: random aggression (no hand awareness)

Metrics:
- EV / BB per 100: chips won normalized by big blind
- Exploitability delta: LLM win rate vs Random baseline on same opponent
- Adaptation score: early-hand vs late-hand performance (improvement over time)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GameEval:
    """Evaluation of a single game trace."""

    game_id: str
    big_blind: int
    starting_stack: int
    players: list[str]
    chips_won: dict[str, int]
    bb_per_100: dict[str, float]
    hands_played: int


def load_trace(path: Path) -> dict:
    """Load game trace JSON."""
    with open(path) as f:
        return json.load(f)


def eval_trace(trace: dict) -> GameEval:
    """Compute evaluation metrics from a game trace."""
    game_id = trace.get("game_id", "unknown")
    config = trace.get("config", {})
    big_blind = config.get("big_blind", 100)
    stack = config.get("stack", 10000)
    players = [p["name"] for p in trace.get("players", [])]
    final_stacks = trace.get("final_stacks", {})
    hands = trace.get("hands", [])
    hands_played = len(hands)

    chips_won = {p: final_stacks.get(p, 0) - stack for p in players}
    bb_per_100 = {}
    for p in players:
        net_bb = chips_won[p] / big_blind if big_blind else 0
        bb_per_100[p] = (net_bb / hands_played * 100) if hands_played else 0

    return GameEval(
        game_id=game_id,
        big_blind=big_blind,
        starting_stack=stack,
        players=players,
        chips_won=chips_won,
        bb_per_100=bb_per_100,
        hands_played=hands_played,
    )


def adaptation_score(trace: dict, big_blind: int = 100) -> dict[str, float]:
    """
    Early vs late performance. Positive = improved over time (adaptation).
    Returns per-player: (late_bb_per_100 - early_bb_per_100).
    """
    hands = trace.get("hands", [])
    players = [p["name"] for p in trace.get("players", [])]
    stack = trace.get("config", {}).get("stack", 10000)
    if len(hands) < 4:
        return {p: 0.0 for p in players}

    mid = len(hands) // 2
    early_stacks = hands[mid - 1]["stacks_after"]
    late_stacks = hands[-1]["stacks_after"]
    early_hands = mid
    late_hands = len(hands) - mid

    result = {}
    for p in players:
        early_chips = early_stacks.get(p, stack) - stack
        late_chips = late_stacks.get(p, stack) - early_stacks.get(p, stack)
        early_bb = (early_chips / big_blind) / early_hands * 100 if early_hands else 0
        late_bb = (late_chips / big_blind) / late_hands * 100 if late_hands else 0
        result[p] = late_bb - early_bb
    return result


def aggregate_evals(evals: list[GameEval]) -> dict[str, dict[str, float]]:
    """Aggregate across games: mean chips, mean BB/100, std."""
    if not evals:
        return {}
    all_players = set()
    for e in evals:
        all_players.update(e.players)
    result = {}
    for p in all_players:
        chips = [e.chips_won.get(p, 0) for e in evals]
        bb100 = [e.bb_per_100.get(p, 0) for e in evals]
        result[p] = {
            "mean_chips": sum(chips) / len(chips),
            "mean_bb_per_100": sum(bb100) / len(bb100),
            "total_hands": sum(e.hands_played for e in evals if p in e.players),
        }
    return result
