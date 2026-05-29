# task169_usage_cookbook_automodel_cord_v2_revision_pin_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Summary

Pin the Nano-Omni AutoModel training cookbook CORD-v2 `load_dataset` examples
to the PM-verified Hugging Face dataset revision.

## Scope

- `usage-cookbook/Nemotron-3-Nano-Omni/automodel/automodel_training_cookbook.md`
- Focused static cookbook test under `tests/usage_cookbook/`
- Task/status docs for `intern_nem_dev_3`

## Acceptance

- All three `load_dataset("naver-clova-ix/cord-v2")` examples include
  `revision="7f0115a4b758a71d6473b8d085751692da2fef98"`.
- No unpinned direct CORD-v2 `load_dataset` call remains in the cookbook.
- Static tests prove the guard is scoped to the expected AutoModel CORD-v2
  exploration and inference sections.

## Boundaries

- Docs/static-test only.
- No live `load_dataset`, HF/dataset download, AutoModel training/inference,
  endpoint calls, W&B, cluster jobs, deploy, artifact ops, direct
  `main`/`master` push, or self-merge.
