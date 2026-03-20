"""Structured trace capture and JSON saving for poker games."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class HandTrace:
    """Trace for a single hand."""

    hand_number: int
    button_seat: int
    raw_history: str
    stacks_after: dict[str, int] = field(default_factory=dict)


@dataclass
class GameTrace:
    """Trace for a full game (multiple hands)."""

    game_id: str
    timestamp: str
    config: dict[str, Any]
    players: list[dict[str, Any]]
    hands: list[HandTrace]
    final_stacks: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "timestamp": self.timestamp,
            "config": self.config,
            "players": self.players,
            "hands": [
                {
                    "hand_number": h.hand_number,
                    "button_seat": h.button_seat,
                    "raw_history": h.raw_history,
                    "stacks_after": h.stacks_after,
                }
                for h in self.hands
            ],
            "final_stacks": self.final_stacks,
        }


def save_trace(trace: GameTrace, output_dir: Path) -> Path:
    """Save game trace to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"game_{trace.game_id}.json"
    with open(path, "w") as f:
        json.dump(trace.to_dict(), f, indent=2)
    return path
