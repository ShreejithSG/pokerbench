"""Tests for hand strength heuristics."""

from pokerbench.hand_strength import hand_strength_from_cards, parse_card


def test_parse_card_llm_poker_format():
    assert parse_card("14♥") == (14, "♥")
    assert parse_card("7♠") == (7, "♠")


def test_aa_preflop_strong():
    s, draw = hand_strength_from_cards(["14♥", "14♦"], [])
    assert s > 0.9
    assert not draw


def test_weak_preflop():
    s, _ = hand_strength_from_cards(["2♣", "3♦"], [])
    assert s < 0.5
