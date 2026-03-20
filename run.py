#!/usr/bin/env python3
"""
Run a poker game with 3 players. Uses RandomPlayer by default (no API needed).
Use --models to switch to LLM players (requires OPENAI_API_KEY or LiteLLM config).
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import argparse
import random
from datetime import datetime
from pathlib import Path

from llm_poker.environment import PokerTable
from llm_poker.llm_player import LLMPlayer

from pokerbench.personas import PersonaPlayer, get_persona_names
from pokerbench.random_player import RandomPlayer
from pokerbench.tracing import GameTrace, HandTrace, save_trace


def run_game(
    players: int = 3,
    rounds: int = 5,
    stack: int = 10000,
    small_blind: int = 50,
    big_blind: int = 100,
    min_raise: int = 500,
    use_random: bool = True,
    models: list[str] | None = None,
    personas: list[str] | None = None,
    seed: int | None = None,
    output_dir: Path = Path("traces"),
    quiet: bool = False,
    game_id: str | None = None,
) -> GameTrace:
    """Run a poker game and return the trace."""
    if seed is not None:
        random.seed(seed)

    if use_random or not models:
        if personas:
            player_list = [
                PersonaPlayer(
                    name=f"Player_{i+1}",
                    persona=personas[i % len(personas)],
                    stack=stack,
                    seed=seed,
                )
                for i in range(players)
            ]
            model_ids = [f"persona:{personas[i % len(personas)]}" for i in range(players)]
        else:
            player_list = [
                RandomPlayer(name=f"Player_{i+1}", stack=stack, seed=seed)
                for i in range(players)
            ]
            model_ids = ["random"] * players
    else:
        player_list = [
            LLMPlayer(name=f"Player_{i+1}", model_id=models[i % len(models)], stack=stack)
            for i in range(players)
        ]
        model_ids = [models[i % len(models)] for i in range(players)]

    table = PokerTable(
        players=player_list,
        min_raise=min_raise,
        small_blind=small_blind,
        big_blind=big_blind,
    )

    game_id = game_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    hand_traces: list[HandTrace] = []

    for r in range(rounds):
        # Only count players with chips (folded is per-hand, resets each hand)
        alive = sum(1 for p in player_list if p.stack > 0)
        if alive < 2:
            break

        history = table.play_hand()
        stacks_after = {p.name: p.stack for p in player_list}
        hand_traces.append(
            HandTrace(
                hand_number=r + 1,
                button_seat=table.button_position,
                raw_history=history,
                stacks_after=stacks_after,
            )
        )
        if not quiet:
            print(history, "\n----- END HAND -----\n")
        table.remove_busted()

    final_stacks = {p.name: p.stack for p in player_list}
    trace = GameTrace(
        game_id=game_id,
        timestamp=datetime.now().isoformat(),
        config={
            "rounds": rounds,
            "stack": stack,
            "small_blind": small_blind,
            "big_blind": big_blind,
            "min_raise": min_raise,
            "use_random": use_random,
            "personas": personas,
        },
        players=[
            {"seat": i, "name": p.name, "model": model_ids[i], "starting_stack": stack}
            for i, p in enumerate(player_list)
        ],
        hands=hand_traces,
        final_stacks=final_stacks,
    )

    path = save_trace(trace, output_dir)
    if not quiet:
        print(f"\nTrace saved to {path}")
        ranking = sorted(player_list, key=lambda x: x.stack, reverse=True)
        print("\n=== FINAL STANDINGS ===")
        for i, p in enumerate(ranking, start=1):
            print(f"  {i}. {p.name}: {p.stack} chips")

    return trace


def main():
    parser = argparse.ArgumentParser(description="Run poker benchmark game")
    parser.add_argument("--players", "-p", type=int, default=3, help="Number of players")
    parser.add_argument("--rounds", "-r", type=int, default=5, help="Number of hands")
    parser.add_argument("--small-blind", type=int, default=50, help="Small blind")
    parser.add_argument("--big-blind", type=int, default=100, help="Big blind")
    parser.add_argument("--stack", "-s", type=int, default=10000, help="Starting stack per player")
    parser.add_argument(
        "--models",
        "-m",
        nargs="+",
        help="Model names for LLM players (e.g. gpt-4o). If omitted, uses RandomPlayer (no API).",
    )
    parser.add_argument(
        "--personas",
        nargs="+",
        choices=get_persona_names(),
        help="Persona per seat: tag, lag, passive, nit, random. E.g. --personas tag lag passive",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("traces"),
        help="Directory for trace JSON files",
    )
    args = parser.parse_args()

    use_random = not args.models
    if use_random:
        if args.personas:
            print(f"Using PersonaPlayer: {args.personas}\n")
        else:
            print("Using RandomPlayer (no API needed). Use --models gpt-4o for LLM play.\n")

    if args.players < 2:
        parser.error("--players must be at least 2")
    if args.rounds < 1:
        parser.error("--rounds must be at least 1")

    run_game(
        players=args.players,
        rounds=args.rounds,
        stack=args.stack,
        small_blind=args.small_blind,
        big_blind=args.big_blind,
        use_random=use_random,
        models=args.models,
        personas=args.personas,
        seed=args.seed,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
