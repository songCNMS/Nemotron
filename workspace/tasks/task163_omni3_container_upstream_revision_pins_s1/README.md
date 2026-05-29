# task163_omni3_container_upstream_revision_pins_s1

<!-- METADATA:STATUS=ReadyForGate,ASSIGNEE=intern_nem_dev_3 -->

## Summary

Harden Omni3 SFT/RL container Dockerfiles so upstream release branch sources are
paired with immutable 40-character SHA pins and fail fast if branch heads move.

## Scope

- `src/nemotron/recipes/omni3/stage0_sft/Dockerfile`
- `src/nemotron/recipes/omni3/stage1_rl/Dockerfile`
- Focused static container revision-pin tests
- Task/status docs for `intern_nem_dev_3`

## Acceptance

- Megatron-Bridge, Megatron-LM, and NeMo-RL upstream source refs are pinned to
  PM-provided lowercase 40-character SHAs.
- Branch names remain visible for operator context.
- Dockerfile clone/fetch paths verify `git rev-parse HEAD` against the pinned
  SHA and exit non-zero before continuing when the branch head differs.

## Boundaries

- No container builds, live `git clone`/`git fetch`, downloads, data prep,
  SFT/RL train/eval, endpoint calls, W&B, cluster jobs, deploy, artifact ops,
  direct `main`/`master` push, or self-merge.

## PR

- https://github.com/songCNMS/Nemotron/pull/270
