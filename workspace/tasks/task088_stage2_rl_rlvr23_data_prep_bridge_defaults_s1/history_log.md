# task088_stage2_rl_rlvr23_data_prep_bridge_defaults_s1 - History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-28

- Received PM assignment to align RLVR2/RLVR3 data-prep defaults with the M0 to M1 RLVR bridge combined-output contract.
- Fast-forwarded local `main` to `a221b222e2226be8ed8d4258734638199eedf073` and created branch `intern_nem_dev_2/task088_stage2_rl_rlvr23_data_prep_bridge_defaults_s1`.
- Audited `stage2_rl/stage1_rlvr/config/data_prep/rlvr{1,2,3}.yaml`: RLVR1 already pointed at `m1_rlvr/rlvr1/combined.jsonl`; RLVR2/RLVR3 still pointed at developer-local `/lustre/.../yifuw/...` paths.
- Updated RLVR2/RLVR3 defaults to use `${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlvr/{rlvr2,rlvr3}/combined.jsonl` and kept RLVR3 comments clear about the bridge contract despite current inactive registry coverage.
- Expanded `test_rlvr1_smoke_wiring.py` so RLVR1/RLVR2/RLVR3 defaults reject developer-local paths, require bridge combined outputs, and preserve `_data_prep_base` fields.
- Verified locally: focused M1 RLVR bridge and RLVR smoke wiring shard passed with 36 tests, py_compile passed for the touched test, ruff passed for the touched test, whitespace checks passed, and a structured static audit confirmed all three defaults point at bridge combined outputs with no developer-local `/lustre` path.
