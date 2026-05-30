# task188_nano_omni_grpo_cookbook_doc_links_revision_pins_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1,SESSION=1 -->

## Scope

- Pin mutable/private NeMo-RL documentation links in the Nano-Omni GRPO usage
  cookbook notebooks to public GitHub URLs at NeMo-RL revision
  `98ba11c0a77e177a903cd3756570684437a08e8d`.
- Scoped notebooks:
  - `usage-cookbook/Nemotron-3-Nano-Omni/grpo/grpo_training_cookbook.ipynb`
  - `usage-cookbook/Nemotron-3-Nano-Omni/grpo_nemo_gym/grpo_nemo_gym_training_cookbook.ipynb`
- Extend focused static notebook coverage under `tests/usage_cookbook/`.
- Preserve `nano-v3-omni` branch-context prose and existing executable checkout
  guard behavior.

## Boundaries

- Static notebook/test/status docs only.
- No notebook execution, live git clone/fetch/checkout, build, download,
  recipe/data-prep/train/eval, endpoint, W&B, cluster, deploy, artifact
  operations, direct `main`/`master` push, or self-merge.

## Status

- Base: `a655174376be9b1880fc9b756cc37af76590f747`
- Branch: `intern_nem_dev_1/task188_nano_omni_grpo_cookbook_doc_links_revision_pins_s1`
- PR: pending
- Checks: focused notebook pytest, py_compile, Ruff, structured notebook
  probe, scoped stale-link grep, added-line live-surface scan,
  `git diff --check`, and `git diff --cached --check` passed.
