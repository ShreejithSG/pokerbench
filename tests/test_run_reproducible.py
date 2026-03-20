"""Deterministic runs: same seed => same hand history."""

from pathlib import Path

from run import run_game


def test_same_seed_same_history():
    out = Path("/tmp/pokerbench_test_traces")
    t1 = run_game(
        players=2,
        rounds=3,
        personas=["tag", "tag"],
        seed=12345,
        output_dir=out,
        quiet=True,
    )
    t2 = run_game(
        players=2,
        rounds=3,
        personas=["tag", "tag"],
        seed=12345,
        output_dir=out,
        quiet=True,
    )
    assert len(t1.hands) == len(t2.hands)
    for h1, h2 in zip(t1.hands, t2.hands, strict=True):
        assert h1.raw_history == h2.raw_history
