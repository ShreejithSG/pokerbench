# PokerBench

LLM strategic reasoning benchmark via Texas Hold'em. Built on [llm-poker](https://github.com/strangeloopcanon/llm-poker).

## Quick Start

```bash
# Install
pip install -e .

# Run with RandomPlayer (no API needed)
python run.py --rounds 5

# Run with LLM players (requires API key)
export OPENAI_API_KEY=sk-your-key
python run.py --models gpt-4o --rounds 5
```

## Configuration

Copy `.env.example` to `.env` and set:

- `OPENAI_API_KEY` – for direct OpenAI API
- `LITELLM_API_KEY` + `LITELLM_BASE_URL` – for LiteLLM proxy

## CLI

```
python run.py [OPTIONS]

  -p, --players N     Number of players (default: 3)
  -r, --rounds N      Number of hands (default: 5)
  -s, --stack N       Starting stack per player (default: 10000)
  -m, --models ...    Model names for LLM players (e.g. gpt-4o). Omit for RandomPlayer.
  --seed N            Random seed for reproducibility
  -o, --output-dir    Directory for trace JSON files (default: traces/)
```

## API Check

```bash
python scripts/check_api.py
```

Verifies your API key against OpenAI and/or LiteLLM proxy. Loads `.env` automatically.

## Output

Game traces are saved as JSON in `traces/` (or `--output-dir`). Each file contains hand history, stacks, and final standings.
