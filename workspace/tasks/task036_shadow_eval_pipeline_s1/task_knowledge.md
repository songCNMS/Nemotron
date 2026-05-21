# task036_shadow_eval_pipeline_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

- The Session 1 scaffold lives under `nemotron.recipes.super3.milestones.shadow_eval` and stays sandbox-only.
- `build_synthetic_shadow_plan` defines two canary examples and two shadow examples; callers can also pass a custom `ShadowEvalPlan` for local held-out splits.
- `evaluate_shadow_plan` reads latest candidate/baseline traces from `LocalRolloutStore`, applies canary minimum-score checks, then delegates category regression logic to `evaluate_promotion_gate`.
- Final status precedence is rollback from the promotion gate, then hold for canary failures or missing rollout coverage, otherwise the gate status.
- Real checkpoint promotion, live cluster eval, W&B/lineage publishing, and production shadow split execution remain separate follow-up work.
- Session 2 added no new implementation knowledge; it only confirmed PR #138 post-merge sync and idle status after local `main` fast-forwarded to `156403be8a4cdb8987613ff3787da0629442bcd3`.
