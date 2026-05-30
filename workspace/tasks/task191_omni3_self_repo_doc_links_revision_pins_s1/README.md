# task191_omni3_self_repo_doc_links_revision_pins_s1

<!-- METADATA:STATUS=Merged,ASSIGNEE=intern_nem_dev_1,SESSION=2 -->

## Scope

- Pin scoped `NVIDIA-NeMo/Nemotron` `tree/main` and `blob/main` links in
  Omni3 public docs to exact Nemotron revision
  `89a6da531c4c693da585a7cc9ac96c51492bffa4`.
- Scoped docs:
  - `docs/nemotron/omni3/README.md`
  - `docs/nemotron/omni3/sft.md`
  - `docs/nemotron/omni3/rl.md`
  - `docs/nemotron/omni3/architecture.md`
- Add focused static coverage under `tests/docs/`.
- Preserve local relative links and visible context.

## Boundaries

- Static docs/tests/status only.
- No live operations beyond normal repo sync, build/download/recipe/data-prep,
  train/eval, endpoint, W&B, cluster, deploy, artifact operations, direct
  `main`/`master` push, or self-merge.

## Status

- Base: `89a6da531c4c693da585a7cc9ac96c51492bffa4`
- Branch: `intern_nem_dev_1/task191_omni3_self_repo_doc_links_revision_pins_s1`
- Closeout branch:
  `intern_nem_dev_1/task191_omni3_self_repo_doc_links_revision_pins_s1_closeout`
- PR: https://github.com/songCNMS/Nemotron/pull/298
- Tested/merged head: `d391c86b9f933b9d6bcd576041f00a59453f00b6`
- Merge SHA: `14a3c985a86eb07d68652a5452b54da19a1b0666`
- Validated implementation head: `caeca4ffc75131a8a80dcd0ee49bb8f429bcdcee`
- Merged-main checks: focused pytest 2 passed, py_compile, Ruff, diff checks,
  stale self-repo main-link grep, and structured probe
  `PM_MERGED_OMNI3_SELF_REPO_DOC_LINK_PIN_PROBE_PASS`.
- Checks: focused static docs pytest, py_compile, Ruff, structured static
  probe, scoped stale-link grep, added-line live-surface scan,
  `git diff --check`, and `git diff --cached --check` passed.
- Blockers: none for PM gate.
- Residual risk: static docs/test-only coverage; no live recipe, data-prep,
  train/eval, endpoint, W&B, cluster, deploy, artifact operation,
  `main`/`master` push, or self-merge was performed.
