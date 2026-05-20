# task040 - task_knowledge

## Plan §6 W1 deliverable

> Create difficulty curricula by filtering samples the current SFT
> model already solves consistently, then sorting the remaining
> samples by pass rate, judge confidence, and rollout length.

Three signals the plan calls out:

1. **Pass rate** (vs prior checkpoint) — drives `drop_solved` policy
2. **Judge confidence** (RLHF GenRM judge) — secondary tie-break
3. **Rollout length** — proxy for difficulty for agentic tasks

Today the M0 layer carries a `difficulty` *bucket* per row (categorical:
`easy`/`medium`/`hard` etc., per task008) but no numeric pass rate or
judge confidence. Session 1 of this task uses buckets only; numeric
signals plug in via Session 3 once the rollout store (task032) is up.

## Sample interface (sketch)

```python
from nemotron.recipes.super3.milestones.m0_data_env.difficulty_sampler import (
    bucket_rows,
    filter_solved,
    weighted_sample,
)

ordered = bucket_rows(rows, policy="easy_first")
unsolved = filter_solved(ordered, pass_rates=last_checkpoint_pass_rates, threshold=0.9)
batch = weighted_sample(unsolved, weights={"easy": 0.2, "medium": 0.5, "hard": 0.3}, n=10_000, rng=rng)
```

## Why not just sort by pass_rate directly?

Because today's M0 rows don't *have* a pass_rate — only a categorical
bucket. Skipping the bucket-aware Session 1 to wait for full numeric
data would block the curriculum work entirely on task032 (M2). Session
1's bucket-only sampler is the pragmatic step that lets curriculum
training start during M1 phase against the bucket signal we already
have.

## Interaction with downstream

- SFT data prep (`prepare_m1_agentic_sft.py`) — apply curriculum at
  data_prep time so the training loader gets re-ordered jsonl
- RLVR data prep — same, applied per mix (rlvr1 / rlvr2 / rlvr3)
- SWE / RLHF — curriculum less impactful (small datasets); skip for
  now, lift in Session 2 if needed

## Pre-existing sandbox issue

`tests/recipes/super3/test_m1_agentic_sft.py` 仍因 pyarrow ImportError
collect-error in sandbox CI; non-sandbox正常跑。
