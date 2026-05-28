# task091_omni3_stage1_rl_config_portability_s1 - Omni3 stage1 RL config portability

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2,SESSION=1 -->

## Background

PM assigned a static portability fix after PR #197 advanced `main` to
`914dc3db746702744651a97ea8680087e582a6fb`. Three runnable Omni3 stage1
RL configs still used named-user `/lustre/fs1/portfolios/coreai/users/aroshanghias`
fallbacks for shared, data, checkpoint, container, user, cache, model, and
container image roots.

## Goals

- Start from latest `main` at `914dc3db746702744651a97ea8680087e582a6fb` or newer.
- Preserve the existing env override variable names for Omni3 stage1 RL configs.
- Replace named-user fallbacks with portable defaults, preferring
  `${oc.env:NEMO_RUN_DIR,.}/output/omni3/...` for generated roots.
- Align `CONTAINER` fallback with the existing home-cache container convention.
- Keep launch commands, job names, node counts, artifact references, and stage3
  vision RL behavior unchanged.
- Add focused static tests under `tests/recipes/omni3/`.

## Acceptance Criteria

- [x] Local `main` synced to `914dc3db746702744651a97ea8680087e582a6fb`.
- [x] Target Omni3 stage1 RL configs contain no named-user Lustre fallback.
- [x] Required env var keys and env override names are preserved.
- [x] No-env defaults resolve to run-dir-relative or home-cache paths.
- [x] MPO tiny keeps one-node and tiny job-name defaults.
- [ ] PR opened to `main`; no direct push to `main` or `master`.
