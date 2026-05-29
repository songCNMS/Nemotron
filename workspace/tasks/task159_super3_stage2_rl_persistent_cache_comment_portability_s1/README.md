# task159_super3_stage2_rl_persistent_cache_comment_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Summary

Make Super3 Stage2 RL runtime config `persistent_cache` example comments
portable by replacing scoped `/lustre/.../cache` guidance with
`${NEMO_RUN_DIR:-.}/cache/super3/stage2_rl`, while preserving empty
`persistent_cache` values and runtime semantics.

## Scope

- `src/nemotron/recipes/super3/stage2_rl/config/default.yaml`
- `src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/config/default.yaml`
- `src/nemotron/recipes/super3/stage2_rl/stage2_swe1/config/default.yaml`
- `src/nemotron/recipes/super3/stage2_rl/stage2_swe2/config/default.yaml`
- `src/nemotron/recipes/super3/stage2_rl/stage3_rlhf/config/default.yaml`
- Focused Super3 Stage2 RL config tests.
- Task/status docs for `intern_nem_dev_3`.

## Acceptance

- The five scoped YAML files contain no `/lustre/` example.
- The five scoped YAML files keep `run.env.persistent_cache` as an empty
  string.
- The five scoped YAML files include portable cache guidance using
  `${NEMO_RUN_DIR:-.}/cache/super3/stage2_rl`.

## Boundaries

- No live Stage2 RL data prep, bridge prep, training, eval, endpoint calls,
  W&B, cluster jobs, deploy, artifact upload/download, direct `main`/`master`
  push, or self-merge.
