"""Poker player personas: parameterized opponent styles for benchmark evaluation.

Aligned with the proposal: explicit parameterization, fixed behavioral archetypes
that LLM agents must detect, adapt to, and exploit. Personas adjust fold/call/raise
weights based on game context (street, facing bet, pot size).

Persona definitions are versioned and documented for reproducibility.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

from llm_poker.player import Player


@dataclass
class PersonaSpec:
    """Explicit parameterization of a persona. Versioned for reproducibility."""

    name: str
    description: str
    base_weights: tuple[float, float, float]  # (fold, call, raise)
    context_adjuster: Optional[str] = None  # e.g. "bluffer", "conservative"
    version: str = "1.0"


# Base (fold, call, raise) weights. Context adjusters modify these per decision.
PERSONA_SPECS: dict[str, PersonaSpec] = {
    "tag": PersonaSpec(
        name="tag",
        description="Tight-Aggressive: selective, raises when in, folds to aggression",
        base_weights=(0.30, 0.25, 0.45),
        context_adjuster="tight_aggressive",
    ),
    "lag": PersonaSpec(
        name="lag",
        description="Loose-Aggressive: plays many hands, very aggressive",
        base_weights=(0.08, 0.22, 0.70),
        context_adjuster=None,
    ),
    "passive": PersonaSpec(
        name="passive",
        description="Calling station: calls everything, rarely raises",
        base_weights=(0.12, 0.70, 0.18),
        context_adjuster=None,
    ),
    "nit": PersonaSpec(
        name="nit",
        description="Rock: very tight, folds most hands, only plays premiums",
        base_weights=(0.50, 0.35, 0.15),
        context_adjuster=None,
    ),
    "bluffer": PersonaSpec(
        name="bluffer",
        description="Bluffs aggressively: raises often when no bet, folds to aggression",
        base_weights=(0.25, 0.25, 0.50),
        context_adjuster="bluffer",
    ),
    "conservative": PersonaSpec(
        name="conservative",
        description="Conservative: folds to any bet, never bluffs, only calls with strength",
        base_weights=(0.45, 0.45, 0.10),
        context_adjuster="conservative",
    ),
    "maniac": PersonaSpec(
        name="maniac",
        description="Maniac: raises constantly, ignores pot odds",
        base_weights=(0.02, 0.18, 0.80),
        context_adjuster=None,
    ),
    "calling_station": PersonaSpec(
        name="calling_station",
        description="Extreme calling station: almost never folds or raises",
        base_weights=(0.05, 0.85, 0.10),
        context_adjuster=None,
    ),
    "rock": PersonaSpec(
        name="rock",
        description="Ultra-tight rock: folds unless premium hand (proxy: very high fold)",
        base_weights=(0.65, 0.25, 0.10),
        context_adjuster=None,
    ),
    "random": PersonaSpec(
        name="random",
        description="Baseline: uniform-ish fold/call/raise, no context awareness",
        base_weights=(0.15, 0.45, 0.40),
        context_adjuster=None,
    ),
}


def _adjust_bluffer(
    base: list[float],
    community_cards: List,
    pot: int,
    call_amount: int,
    hole_cards: Optional[List[str]] = None,
) -> list[float]:
    """
    Strategic bluffer: value bet when strong, bluff when weak + good spot.
    Avoids blind bluffing: only bluffs when (weak hand + no bet + fold equity).
    """
    fold, call, raise_w = base[0], base[1], base[2]
    strength, is_draw = 0.5, False
    if hole_cards and len(hole_cards) == 2:
        from pokerbench.hand_strength import hand_strength_from_cards
        strength, is_draw = hand_strength_from_cards(hole_cards, community_cards)

    if call_amount == 0:
        # Can bet. Value bet when strong; bluff when weak + good spot (early street).
        street = len(community_cards)
        good_bluff_spot = street <= 3  # preflop/flop: more fold equity
        if strength >= 0.6:
            return [fold * 0.5, call * 0.5, raise_w * 2.0]  # value bet
        if strength <= 0.4 and good_bluff_spot:
            return [fold * 0.7, call * 0.6, raise_w * 1.5]  # bluff
        if is_draw:
            return [fold * 0.6, call * 0.7, raise_w * 1.4]  # semi-bluff
        return [fold * 0.8, call * 1.0, raise_w * 1.0]  # marginal: check/call
    if pot > 0 and call_amount > pot:
        # Facing big bet: fold weak, call/raise strong
        if strength >= 0.6:
            return [fold * 0.5, call * 1.0, raise_w * 1.2]
        return [fold * 2.0, call * 0.6, raise_w * 0.2]
    return base


def _adjust_conservative(
    base: list[float],
    community_cards: List,
    pot: int,
    call_amount: int,
    hole_cards: Optional[List[str]] = None,
) -> list[float]:
    """Conservative: fold to any bet, never bluff when we can check."""
    fold, call, raise_w = base[0], base[1], base[2]
    if call_amount == 0:
        # Can check. Don't bluff - prefer call (check) over raise.
        return [fold, call * 1.5, raise_w * 0.3]
    # Facing bet - fold more
    return [fold * 1.5, call * 0.8, raise_w * 0.5]


def _adjust_tight_aggressive(
    base: list[float],
    community_cards: List,
    pot: int,
    call_amount: int,
    hole_cards: Optional[List[str]] = None,
) -> list[float]:
    """
    TAG: value bet when strong, selective bluff when weak + good spot.
    Folds to aggression without a hand.
    """
    fold, call, raise_w = base[0], base[1], base[2]
    strength, is_draw = 0.5, False
    if hole_cards and len(hole_cards) == 2:
        from pokerbench.hand_strength import hand_strength_from_cards
        strength, is_draw = hand_strength_from_cards(hole_cards, community_cards)

    if call_amount == 0:
        if strength >= 0.55:
            return [fold * 0.6, call * 0.6, raise_w * 1.5]  # value
        if strength <= 0.35 and is_draw:
            return [fold * 0.8, call * 0.8, raise_w * 1.2]  # semi-bluff only
        return [fold * 1.0, call * 1.2, raise_w * 0.6]  # check/fold marginal
    if strength >= 0.6:
        return [fold * 0.5, call * 1.0, raise_w * 1.0]
    return [fold * 1.3, call * 0.9, raise_w * 0.5]


def _get_context_weights(
    persona: str,
    base_weights: tuple[float, float, float],
    community_cards: List,
    pot: int,
    call_amount: int,
    hole_cards: Optional[List[str]] = None,
) -> list[float]:
    """Apply context adjustment and return (fold, call, raise) weights."""
    base = list(base_weights)
    spec = PERSONA_SPECS.get(persona)
    if not spec or not spec.context_adjuster:
        return base
    adj = spec.context_adjuster
    kwargs = {"hole_cards": hole_cards}
    if adj == "bluffer":
        return _adjust_bluffer(base, community_cards, pot, call_amount, **kwargs)
    if adj == "conservative":
        return _adjust_conservative(base, community_cards, pot, call_amount, **kwargs)
    if adj == "tight_aggressive":
        return _adjust_tight_aggressive(base, community_cards, pot, call_amount, **kwargs)
    return base


class PersonaPlayer(Player):
    """
    Player with a fixed persona. Uses context-aware fold/call/raise weights.
    Personas are explicitly parameterized for reproducibility (see PERSONA_SPECS).
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
        spec = PERSONA_SPECS.get(self.persona, PERSONA_SPECS["random"])
        self._base_weights = spec.base_weights
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
        weights = _get_context_weights(
            self.persona,
            self._base_weights,
            community_cards,
            pot,
            call_amount,
            hole_cards=getattr(self, "hole_cards", None) or [],
        )
        # Normalize (avoid zeros)
        total = sum(weights)
        if total <= 0:
            weights = [1 / 3, 1 / 3, 1 / 3]
        else:
            weights = [w / total for w in weights]
        action = self._rng.choices(["fold", "call", "raise"], weights=weights, k=1)[0]
        raise_amount = None
        if action == "raise":
            target = call_amount + min_raise
            raise_amount = min(target, self.stack)
        return {"action": action, "raise_amount": raise_amount}


def get_persona_names() -> list[str]:
    """Return available persona names."""
    return list(PERSONA_SPECS.keys())


def get_persona_spec(persona: str) -> Optional[PersonaSpec]:
    """Return spec for a persona, or None."""
    return PERSONA_SPECS.get(persona.lower())
