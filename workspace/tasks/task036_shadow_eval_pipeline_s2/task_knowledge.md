# task036_shadow_eval_pipeline_s2 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

- Session 2 extends the existing sandbox module at `nemotron.recipes.super3.milestones.shadow_eval`; it does not add live benchmark, cluster, Docker, W&B, or checkpoint-promotion dependencies.
- `CanaryPolicy` resolves thresholds with precedence `prompt_id` over `env_id` over `category` over per-example `min_score` over the configured default or legacy plan fallback.
- `ShadowEvalPlan.canary_threshold_for` keeps existing Session 1 defaults compatible while allowing canary policy overrides in local run configs.
- `tune_canary_policy` accepts mapping samples or `ShadowTaskResult` objects and derives deterministic thresholds by category, env, or prompt using the minimum local calibration score minus a non-negative margin.
- Shadow-eval reports now include resolved canary thresholds in JSON and markdown so canary holds are traceable without external services.
