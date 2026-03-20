"""Random player for testing without LLM API."""

from __future__ import annotations

import random
from typing import List, Dict, Optional

from llm_poker.player import Player


class RandomPlayer(Player):
    """
    Player that picks fold/call/raise randomly.
    Used for local testing when no LLM API is available.
    """

    def __init__(self, name: str, stack: int = 10000, seed: Optional[int] = None):
        super().__init__(name, stack)
        self.model_id = "random"
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
            weights=[0.15, 0.45, 0.4],
            k=1,
        )[0]
        raise_amount = None
        if action == "raise":
            # Raise to at least call_amount + min_raise, cap at stack
            target = call_amount + min_raise
            raise_amount = min(target, self.stack)
        return {"action": action, "raise_amount": raise_amount}
