# PokerBench

LLM strategic reasoning benchmark via Texas Hold'em. Built on [llm-poker](https://github.com/strangeloopcanon/llm-poker).

## Quick Start

```bash
# Install
pip install -e .

# Run with RandomPlayer (no API needed)
python run.py --rounds 5

# Run with personas (TAG, LAG, passive, nit)
python run.py --personas tag lag passive --rounds 10

# Run with LLM players (requires API key)
export OPENAI_API_KEY=sk-your-key
python run.py --models gpt-4o --rounds 5
```

## Configuration

Copy `.env.example` to `.env` and set:

- `OPENAI_API_KEY` – for direct OpenAI API
- `LITELLM_API_KEY` + `LITELLM_BASE_URL` – for LiteLLM proxy

## Personas

Opponent styles for benchmark evaluation (no API needed):

| Persona | Style | Fold | Call | Raise |
|---------|-------|------|------|-------|
| tag | Tight-Aggressive | 30% | 25% | 45% |
| lag | Loose-Aggressive | 8% | 22% | 70% |
| passive | Calling station | 12% | 70% | 18% |
| nit | Very tight | 50% | 35% | 15% |

## CLI

```
python run.py [OPTIONS]

  -p, --players N     Number of players (default: 3)
  -r, --rounds N      Number of hands (default: 5)
  -s, --stack N       Starting stack per player (default: 10000)
  -m, --models ...    Model names for LLM players (e.g. gpt-4o). Omit for RandomPlayer.
  --personas ...      Personas per seat: tag, lag, passive, nit, random
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

## Output

- **`traces/`** – Game traces from `run.py` (hand history, stacks, config)
- **`test_results/`** – Benchmark results with behavioral stats and adaptation curves
