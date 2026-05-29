# task186_omni3_upstream_doc_links_revision_pins_s1 history

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Accepted PM assignment and created branch
  `intern_nem_dev_2/task186_omni3_upstream_doc_links_revision_pins_s1` from
  `origin/main` `c76c51dba5e8796d7b7f12c25fcd172f4c9c8bfa`.
- PM reported PR #291 merged before PR open, so the branch was rebased onto
  corrected `origin/main` `f74e7c05668f96766d10c730fcd14ddec7191350`.
- Replaced scoped Omni3 Megatron-Bridge `blob/tree/nemotron_3_omni` links with
  exact commit links at `648756cb99eed872d9e577243495840b9395a6f7`.
- Replaced scoped Omni3 NeMo-RL `blob/tree/nano-v3-omni` links with exact
  commit links at `98ba11c0a77e177a903cd3756570684437a08e8d`.
- Added focused static docs test coverage that rejects branch-based GitHub
  blob/tree links and confirms exact SHA links plus preserved branch context.
- Verified focused pytest, `py_compile`, Ruff, and structured static probe on
  the corrected base.
- Opened PR #293 to `main`:
  https://github.com/songCNMS/Nemotron/pull/293.
- Boundaries preserved: no live git clone/fetch/checkout, build, download,
  recipe execution, data prep, train/eval, endpoint, W&B, cluster, deploy,
  artifact operation, `main`/`master` push, or self-merge.
