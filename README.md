# PokerBench

LLM strategic reasoning benchmark via Texas Hold'em. Built on [llm-poker](https://github.com/strangeloopcanon/llm-poker).

## Quick Start

```bash
# Install
pip install -e .

# Run with RandomPlayer (no API needed)
python run.py --rounds 5

# Run with personas (bluffer, conservative, tag, lag, etc.)
python run.py --personas bluffer conservative tag --rounds 10

# Run with LLM players (requires API key)
export OPENAI_API_KEY=sk-your-key
python run.py --models gpt-4o --rounds 5
```

## Configuration

Copy `.env.example` to `.env` and set:

- `OPENAI_API_KEY` – for direct OpenAI API
- `LITELLM_API_KEY` + `LITELLM_BASE_URL` – for LiteLLM proxy

## Personas

Parameterized opponent styles (explicit, versioned). LLM agents must detect, adapt to, and exploit these. Context-aware personas adjust behavior based on game state (facing bet, pot size).

| Persona | Behavior | Context-aware |
|---------|----------|---------------|
| **tag** | Tight-Aggressive: selective, raises when in | Yes: bets when can check, folds to aggression |
| **lag** | Loose-Aggressive: plays many hands, very aggressive | No |
| **bluffer** | Strategic: value bets strong hands, bluffs weak only in good spots | Yes |
| **conservative** | Folds to any bet, never bluffs | Yes |
| **maniac** | Raises constantly, ignores pot odds | No |
| **passive** | Calling station: calls everything, rarely raises | No |
| **calling_station** | Extreme: almost never folds or raises | No |
| **nit** | Very tight: folds most hands | No |
| **rock** | Ultra-tight: only plays premiums | No |
| **random** | Baseline: uniform fold/call/raise | No |
| **tilt** | Nonstationary: looser when losing chips (adaptation test) | Yes (stack vs start) |

See `docs/PERSONAS.md` for full parameterization.

**Nonstationarity:** `tilt` persona increases aggression when the stack is down vs starting stack (proposal: behavioral drift).

**Proposal alignment:** `docs/PROPOSAL_ALIGNMENT.md` maps Robert’s benchmark doc to what’s implemented vs roadmap.

## CLI

```
python run.py [OPTIONS]

  -p, --players N     Number of players (default: 3)
  -r, --rounds N      Number of hands (default: 5)
  -s, --stack N       Starting stack per player (default: 10000)
  -m, --models ...    Model names for LLM players (e.g. gpt-4o). Omit for RandomPlayer.
  --personas ...      Personas per seat (e.g. bluffer conservative tag)
  --seed N            Random seed for reproducibility
  -o, --output-dir    Directory for trace JSON files (default: traces/)
```

## Benchmark Runner

Run multiple games and aggregate results:

```bash
python scripts/run_benchmark.py --games 10 --rounds 20 --personas tag lag passive
```

Outputs `benchmark_summary.json` with winner counts and final stacks per game.

## API Check

```bash
python scripts/check_api.py
```

Verifies your API key against OpenAI and/or LiteLLM proxy. Loads `.env` automatically.

## Evaluation

```bash
python scripts/evaluate.py traces/
```

Reports: chips won, BB/100, adaptation score (late vs early hands). Use to compare strategic play vs random baseline.

## Output

- **`traces/`** – Game traces from `run.py` (hand history, stacks, config)
- **`test_results/`** – Benchmark results with behavioral stats and adaptation curves
