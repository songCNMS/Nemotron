# task088_stage2_rl_rlvr23_data_prep_bridge_defaults_s1 - RLVR2/RLVR3 data-prep bridge defaults

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2,SESSION=1 -->

## Background

PM assigned a static data/training pipeline audit follow-up after `main`
advanced to `a221b222e2226be8ed8d4258734638199eedf073`. RLVR1 data prep
already consumes the M0 to M1 RLVR bridge output at
`${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlvr/rlvr1/combined.jsonl`.
RLVR2 and RLVR3 still pointed at developer-local `/lustre/.../yifuw/...`
release JSONL files, bypassing the bridge and lineage path.

## Goals

- Sync local `main` to `a221b222e2226be8ed8d4258734638199eedf073` or newer.
- Update RLVR2 and RLVR3 data-prep defaults to consume bridge
  `combined.jsonl` outputs under `m1_rlvr/{rlvr2,rlvr3}`.
- Keep RLVR3 comments explicit that the bridge path is the intended contract
  even when current registry coverage has no active rows.
- Add focused static tests covering RLVR1/RLVR2/RLVR3 defaults: no
  developer-local path, bridge `combined.jsonl` path, correct mix directory,
  and preserved `_data_prep_base` fields.
- Keep scope static config/test/docs only.

## Acceptance Criteria

- [x] Local `main` synced to `a221b222e2226be8ed8d4258734638199eedf073`.
- [x] RLVR2 and RLVR3 defaults use templated bridge `combined.jsonl` paths.
- [x] Focused tests cover all three RLVR data-prep defaults.
- [x] Required validation passes locally.
- [x] PR opened to `main`; no direct push to `main` or `master`.

## PR

- https://github.com/songCNMS/Nemotron/pull/196
