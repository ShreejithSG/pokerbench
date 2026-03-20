# Changelog

## 0.2.1

- GitHub Actions CI (Python 3.11 / 3.12): pytest + ruff
- Smoke tests: hand strength, personas, seed reproducibility

## 0.2.0

- Persona suite (tag, lag, bluffer, conservative, tilt, etc.) with hand-strength-aware play
- `hand_strength`, `evaluation` modules; `scripts/evaluate.py`
- Deterministic deals via `--seed` + `random.seed`
- Traces, benchmark runner, API check script
- Docs: `docs/PERSONAS.md`, `docs/PROPOSAL_ALIGNMENT.md`
