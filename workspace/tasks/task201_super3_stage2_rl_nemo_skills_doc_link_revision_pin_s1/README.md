# task201_super3_stage2_rl_nemo_skills_doc_link_revision_pin_s1

<!-- METADATA:STATUS=Merged,ASSIGNEE=intern_nem_dev_1,SESSION=2 -->

## Scope

- Pin the NeMo-Skills Dockerfile sandbox link in
  `src/nemotron/recipes/super3/stage2_rl/stage1_rlvr/README.md` from mutable
  `main` to exact NeMo-Skills revision
  `f53fb0b9d84a09411b0d13c21ea08a3ae9141d2a`.
- Add one focused static test under `tests/recipes/super3/`.
- Update dev_1 status and this task's docs only.

## Boundaries

- Static README/test/docs only.
- Do not touch task200 Safety Guard notebook, task199 SDG long-document files,
  task198 Embed recipe files, task197 Super3 LoRA Text2SQL files, deployment
  guides/task196, nvidia-stack/task194, quantization/task195, application
  examples, Omni3 docs, Nano-Omni notebooks, unrelated recipe files, or
  dev_2/dev_3 docs.
- No live URL probe, NeMo-Skills clone/build/download, recipe execution,
  data-prep/train/eval, endpoint, W&B, cluster, deploy, artifact operation,
  direct `main`/`master` push, or self-merge.

## Status

- Base: `ea252765464a50d3b2fc46a5ab7922bf8285a6aa`
- Branch: `intern_nem_dev_1/task201_super3_stage2_rl_nemo_skills_doc_link_revision_pin_s1`
- Closeout branch:
  `intern_nem_dev_1/task201_super3_stage2_rl_nemo_skills_doc_link_revision_pin_s1_closeout`
- PR: https://github.com/songCNMS/Nemotron/pull/308
- Tested/merged head: `0f1820a6c972e0b2fa257628bc488fa09e62f1da`
- Merge SHA: `0460c1f0262875fb27ae530d30cd80d805752851`
- Validated implementation head: `65f95f85532b3fda71aa9625f49e553e93189830`
- PM merged-main verification: PR #308 independently gated, squash-merged, and
  verified on main `0460c1f0262875fb27ae530d30cd80d805752851`.
- Checks:
  - `PYTHONPATH=src /work-agents/.venv/bin/python -m pytest -q tests/recipes/super3/test_stage2_rl_nemo_skills_doc_link_revision_pin.py`
    -> 2 passed.
  - `/work-agents/.venv/bin/python -m py_compile tests/recipes/super3/test_stage2_rl_nemo_skills_doc_link_revision_pin.py`
    -> passed.
  - `/work-agents/.venv/bin/ruff check tests/recipes/super3/test_stage2_rl_nemo_skills_doc_link_revision_pin.py`
    -> passed.
  - Structured static probe -> `STRUCTURED_STAGE2_RLVR_NEMO_SKILLS_LINK_PIN_PROBE_PASS`.
  - Scoped stale mutable NeMo-Skills Dockerfile link grep -> no matches.
  - Added-line live-surface scan -> hits limited to the static pinned
    NeMo-Skills URL, test constants/assertions, and task/status docs.
  - `git diff --check` -> passed.
  - `git diff --cached --check` -> passed.
- Blockers: none for PM gate.
- Residual risk: static README/test/docs-only coverage; no live URL probe,
  NeMo-Skills clone/build/download, recipe execution, data-prep/train/eval,
  endpoint, W&B, cluster, deploy, artifact operation, direct `main`/`master`
  push, or self-merge was performed.
