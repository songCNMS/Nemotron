# task038_m2_rl_curriculum

M2 RL curriculum scaffold for per-environment gap estimation and deterministic
dynamic sampling.

Session 1 is sandbox-only. It reads synthetic/local `LocalRolloutStore` traces,
estimates per-env reward gaps, and allocates sampling quota toward failing or
under-covered environments. The landed task034 judge-pool contract can provide
local judge metrics, but no live judge or reward service is called.

Out of scope for Session 1:
- task014 real RLVR cluster smoke
- task021 launch path / scheduler integration
- task034 Session 2+ live judge model/service deployment
- task040 numeric pass-rate production signal beyond synthetic traces
- cluster smoke/full M2 RL run
- W&B/lineage publication
- production rollout store backend
- live reward calibration
