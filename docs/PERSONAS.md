# Persona Suite

Explicit, versioned parameterization of poker opponent archetypes. Aligned with the benchmark proposal: fixed behavioral patterns that LLM agents must detect, adapt to, and exploit.

## Design Principles

- **Explicit parameterization**: Each persona has documented base weights and (where applicable) context-adjustment rules
- **Reproducibility**: Same persona + same seed → same behavior
- **Held-out potential**: New personas can be added for generalization tests without changing existing ones

## Persona Definitions (v1.0)

### Base Weights

(fold, call, raise) probabilities before context adjustment:

| Persona | Fold | Call | Raise | Context |
|---------|------|------|-------|---------|
| tag | 0.30 | 0.25 | 0.45 | tight_aggressive |
| lag | 0.08 | 0.22 | 0.70 | — |
| bluffer | 0.25 | 0.25 | 0.50 | bluffer |
| conservative | 0.45 | 0.45 | 0.10 | conservative |
| maniac | 0.02 | 0.18 | 0.80 | — |
| passive | 0.12 | 0.70 | 0.18 | — |
| calling_station | 0.05 | 0.85 | 0.10 | — |
| nit | 0.50 | 0.35 | 0.15 | — |
| rock | 0.65 | 0.25 | 0.10 | — |
| random | 0.15 | 0.45 | 0.40 | — |

### Context Adjusters (Hand-Strength Aware)

Personas use `pokerbench.hand_strength` to distinguish value bets from bluffs:

**bluffer**: Strategic bluffing (not blind).
- Value bet when `strength >= 0.6`
- Bluff when `strength <= 0.4` + good spot (preflop/flop, fold equity)
- Semi-bluff when draw (flush/straight draw)
- Fold when weak + facing big bet

**conservative**: When `call_amount == 0`, reduces raise (never bluff); when facing bet, increases fold.

**tight_aggressive**: Value bet when strong; semi-bluff only with draws; fold marginal when facing aggression.

## Usage

```python
from pokerbench import PersonaPlayer, get_persona_names, get_persona_spec

# List personas
get_persona_names()  # ['tag', 'lag', 'bluffer', ...]

# Get spec
spec = get_persona_spec("bluffer")
# spec.description, spec.base_weights, spec.context_adjuster
```
