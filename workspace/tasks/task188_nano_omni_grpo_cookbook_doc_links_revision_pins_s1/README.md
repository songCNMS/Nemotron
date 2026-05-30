# task188_nano_omni_grpo_cookbook_doc_links_revision_pins_s1

<!-- METADATA:STATUS=Complete,ASSIGNEE=intern_nem_dev_1,SESSION=3 -->

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

- Base: `512910a3466012fef675dbcb35b93750e0eba4b4`
- Branch: `intern_nem_dev_1/task188_nano_omni_grpo_cookbook_doc_links_revision_pins_s1`
- PR: https://github.com/songCNMS/Nemotron/pull/295
- Tested/merged head: `841850e737af44f9ba8cfb209b65d04c28c426ca`
- Merge SHA: `a1878fa7e48eb43ba1d467fa93c064b41333c01e`
- Validated implementation head: `f28c8fea3571e0c1362d00a2cd9f24f99b46849a`
- Checks: focused notebook pytest, py_compile, Ruff, structured notebook
  probe, scoped stale-link grep, added-line live-surface scan,
  `git diff --check`, and `git diff --cached --check` passed.
- Merged-main verification: PR #295 was merged and verified on main
  `a1878fa7e48eb43ba1d467fa93c064b41333c01e`.
