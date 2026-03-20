"""Hand strength and draw detection for strategic play (value vs bluff).

Parses cards from game_history, computes strength heuristic for personas.
Used to distinguish value betting (strong hand) from bluffing (weak hand, good spot).
"""

from __future__ import annotations

import re
from typing import Optional


# Card rank: 2-10, J=11, Q=12, K=13, A=14
RANK_MAP = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
            "10": 10, "11": 11, "12": 12, "13": 13, "14": 14,
            "J": 11, "Q": 12, "K": 13, "A": 14}
SUITS = {"♥", "♠", "♦", "♣", "h", "s", "d", "c"}


def parse_card(s: str) -> Optional[tuple[int, str]]:
    """Parse '13♥' or '7♥' (llm-poker format: rank 2-14, suit) -> (rank, suit)."""
    s = str(s).strip().strip("[]'\"")
    if not s or len(s) < 2:
        return None
    rank_str = s[:-1]
    suit = s[-1]
    if suit.lower() in ("h", "s", "d", "c"):
        suit = {"h": "♥", "s": "♠", "d": "♦", "c": "♣"}[suit.lower()]
    if suit not in SUITS:
        return None
    rank = RANK_MAP.get(rank_str) or (int(rank_str) if rank_str.isdigit() else None)
    if rank is None or not (2 <= rank <= 14):
        return None
    return (rank, suit)


def parse_hole_cards(game_history: str, player_name: str) -> Optional[list[tuple[int, str]]]:
    """Extract player's hole cards from game_history. Returns [(rank,suit),(rank,suit)] or None."""
    # Match "Player_1 hole cards: ['13♥', '8♣']" or "TAG_Bot hole cards: ['Kh', '9c']"
    pattern = rf"{re.escape(player_name)}\s+hole cards:\s*\[([^\]]+)\]"
    m = re.search(pattern, game_history)
    if not m:
        return None
    raw = m.group(1)
    cards = [parse_card(c.strip()) for c in raw.replace("'", "").split(",")]
    cards = [c for c in cards if c is not None]
    return cards if len(cards) == 2 else None


def parse_community_cards(community_cards: list) -> list[tuple[int, str]]:
    """Parse community cards from llm-poker format."""
    out = []
    for c in community_cards:
        parsed = parse_card(str(c)) if isinstance(c, str) else None
        if parsed:
            out.append(parsed)
    return out


def preflop_strength(hole: list[tuple[int, str]]) -> float:
    """Preflop strength 0-1. Pair > high cards > low cards."""
    if not hole or len(hole) != 2:
        return 0.5
    r1, r2 = hole[0][0], hole[1][0]
    s1, s2 = hole[0][1], hole[1][1]
    suited = s1 == s2
    high = max(r1, r2)
    low = min(r1, r2)
    gap = high - low
    if r1 == r2:  # pair
        return 0.5 + (high - 2) / 24  # 22=0.5, AA=1.0
    # high card
    base = (high - 2) / 24 * 0.6
    if suited:
        base += 0.05
    if gap <= 2:  # connected
        base += 0.05
    return min(0.95, base + 0.2)


def postflop_strength(hole: list[tuple[int, str]], board: list[tuple[int, str]]) -> float:
    """Postflop strength 0-1. Simple heuristic: pairs, high cards, draws."""
    if not hole or len(hole) != 2 or len(board) < 3:
        return 0.5
    all_cards = hole + board
    ranks = [c[0] for c in all_cards]
    # Count pairs/trips
    from collections import Counter
    cnt = Counter(ranks)
    max_count = max(cnt.values())
    if max_count >= 3:
        return 0.85 + (max(ranks) - 10) / 40
    if max_count == 2:
        pair_rank = max(r for r, c in cnt.items() if cnt[r] >= 2)
        return 0.5 + pair_rank / 28
    # High card
    return 0.3 + max(ranks) / 28


def has_draw(hole: list[tuple[int, str]], board: list[tuple[int, str]]) -> bool:
    """Semi-bluff: flush draw (4 same suit) or straight draw."""
    if not hole or len(hole) != 2 or len(board) < 3:
        return False
    all_cards = hole + board
    suits = [c[1] for c in all_cards]
    ranks = sorted([c[0] for c in all_cards], reverse=True)
    from collections import Counter
    suit_cnt = Counter(suits)
    if max(suit_cnt.values()) >= 4:
        return True
    # Simple straight draw: 4 cards in sequence
    for i in range(len(ranks) - 3):
        if ranks[i] - ranks[i + 3] <= 4:
            return True
    return False


def hand_strength_from_cards(
    hole_cards: list[str],
    community_cards: list,
) -> tuple[float, bool]:
    """
    Returns (strength 0-1, is_draw) from raw card strings.
    Cards: llm-poker format e.g. ['7♥', '11♠'] (rank 2-14, suit).
    strength: 0=weak (bluff candidate), 1=strong (value bet).
    is_draw: True if semi-bluff candidate (has equity).
    """
    hole = [parse_card(c) for c in hole_cards if parse_card(c)]
    board = parse_community_cards(community_cards)
    if not hole or len(hole) != 2:
        return 0.5, False
    if len(board) < 3:
        return preflop_strength(hole), False
    draw = has_draw(hole, board)
    strength = postflop_strength(hole, board)
    if draw:
        strength = max(strength, 0.4)  # draws have equity
    return strength, draw


def hand_strength(
    game_history: str,
    player_name: str,
    community_cards: list,
) -> tuple[float, bool]:
    """
    Returns (strength 0-1, is_draw) by parsing hole cards from game_history.
    Fallback when hole_cards not available (e.g. post-hoc analysis).
    """
    hole = parse_hole_cards(game_history, player_name)
    if not hole:
        return 0.5, False
    return hand_strength_from_cards(
        [f"{r}{s}" for r, s in hole],
        community_cards,
    )
