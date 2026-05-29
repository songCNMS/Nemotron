# task151_super3_stage0_pretrain_tiny_blend_contract_s1 history

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-29

- Created branch
  `intern_nem_dev_3/task151_super3_stage0_pretrain_tiny_blend_contract_s1`
  from `origin/main` at `17ed7b0e5195878030ff09118fb79caee200b824`.
- Updated Super3 Stage0 pretrain `tiny.yaml` to use
  `src/nemotron/recipes/super3/stage0_pretrain/config/data_prep/data_blend_raw_small.json`.
- Replaced the empty Super3 small blend placeholder with four compact
  Super3-owned Phase 1-derived rows.
- Extended focused config tests for tiny blend ownership, non-empty datasets,
  non-repo CWD resolution, and dataclass override preservation.
- Verified focused pytest, py_compile, Ruff, structured YAML/dataclass probe,
  static Nano3 stale-path grep, and diff check before staging.
- Opened PR #257 to `main`: https://github.com/songCNMS/Nemotron/pull/257.
