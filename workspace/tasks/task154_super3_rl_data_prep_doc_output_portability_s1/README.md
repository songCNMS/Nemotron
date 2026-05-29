# task154_super3_rl_data_prep_doc_output_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

## Scope

- Update `docs/nemotron/super3/rl/data-prep.md` so the M0 data-env
  `--output-dir` example uses a portable `${NEMO_RUN_DIR:-.}`-relative
  Super3 output path instead of a developer-local `/mnt/3fs/...` path.
- Add focused static test coverage proving the stale named-user path is absent
  and the portable example is present.

## Boundaries

- Static docs/test/docs-only.
- No live M0 data prep, HF/dataset download, health baseline, train/eval,
  endpoint, W&B, cluster, deploy, artifact download, direct `main`/`master`
  push, or self-merge.

## Status

- Branch: `intern_nem_dev_1/task154_super3_rl_data_prep_doc_output_portability_s1`
- Base: `795eb92359257ed82816a8685db0f9cae1c751ae`
- PR: pending
