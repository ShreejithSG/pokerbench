"""Poker player personas: different strategic styles for benchmark opponents.

Personas use weighted fold/call/raise probabilities to simulate distinct play styles:
- TAG (Tight-Aggressive): Selective, raises when in
- LAG (Loose-Aggressive): Plays many hands, very aggressive
- Passive: Calling station, rarely raises
- Nit: Very tight, folds often
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from llm_poker.player import Player


# (fold, call, raise) weights per persona
PERSONA_WEIGHTS: dict[str, tuple[float, float, float]] = {
    "tag": (0.30, 0.25, 0.45),   # Tight-Aggressive
    "lag": (0.08, 0.22, 0.70),   # Loose-Aggressive
    "passive": (0.12, 0.70, 0.18),  # Calling station
    "nit": (0.50, 0.35, 0.15),   # Very tight
    "random": (0.15, 0.45, 0.40),   # Baseline random
}


class PersonaPlayer(Player):
    """
    Player with a fixed persona (fold/call/raise weights).
    Used to create varied opponents for LLM evaluation.
    """

    def __init__(
        self,
        name: str,
        persona: str = "random",
        stack: int = 10000,
        seed: Optional[int] = None,
    ):
        super().__init__(name, stack)
        self.persona = persona.lower()
        weights = PERSONA_WEIGHTS.get(self.persona, PERSONA_WEIGHTS["random"])
        self._weights = list(weights)
        self.model_id = f"persona:{persona}"
        self._rng = random.Random(seed)

    def request_action(
        self,
        community_cards: List[str],
        pot: int,
        call_amount: int,
        min_raise: int,
        game_history: str,
    ) -> Dict:
        action = self._rng.choices(
            ["fold", "call", "raise"],
            weights=self._weights,
            k=1,
        )[0]
        raise_amount = None
        if action == "raise":
            target = call_amount + min_raise
            raise_amount = min(target, self.stack)
        return {"action": action, "raise_amount": raise_amount}


def get_persona_names() -> list[str]:
    """Return available persona names."""
    return list(PERSONA_WEIGHTS.keys())
