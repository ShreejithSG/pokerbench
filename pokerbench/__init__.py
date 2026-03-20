"""PokerBench: LLM strategic reasoning benchmark via Texas Hold'em."""

__version__ = "0.2.0"

from pokerbench.personas import PersonaPlayer, get_persona_names, get_persona_spec
from pokerbench.random_player import RandomPlayer
from pokerbench.tracing import GameTrace, HandTrace, save_trace

__all__ = [
    "RandomPlayer",
    "PersonaPlayer",
    "get_persona_names",
    "get_persona_spec",
    "GameTrace",
    "HandTrace",
    "save_trace",
]
