# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 82 |

刚做完：task069 Session 2 — `maybe_publish_lineage_from_manifest` helper
+ wired into all 6 `prepare_*.py` bridges (PR #106 / ad61d20, merged
2026-05-19).

- `lineage_publisher.py` 加 `_AUTO` sentinel + `_resolve_wandb_run` +
  `maybe_publish_lineage_from_manifest` helper (failure-tolerant)
- 6 个 bridges (M0 / M1 agentic SFT / RLVR / SWE1 / SWE2 / RLHF) main()
  全 wired — sandbox no-op，cluster + active wandb.run → 真 publish
- 15 个新 pytest case 含 critical safety: publisher crash 不 crash prep
- Sandbox 测试基线 577 → 592 passed + 7 skipped

## task069 整 task 进展

- Session 1 ✓ (PR #104) — publisher module + CLI + dry-run + test doubles
- Session 2 ✓ (PR #106) — helper + 6 bridges wired
- Session 3 ☐ — Cluster verify with real W&B credentials in a
  multi-stage pipeline run

## 本轮 sprint summary (PR #94 起算)

| PR | 内容 | sandbox baseline |
|---|---|---|
| #94 | Roadmap refresh + 4 gap-task scaffolds | 502 → 502 |
| #95 | task067 → task070 rename | 506 → 506 |
| #97 | task013 Session 2a (two-stage SFT driver) | 506 → 520 |
| #99 | task040 Session 1 (curriculum sampler) | 520 → 543 |
| #101 | task070 Session 1 (OpenHands wrapper) | 543 → 559 |
| #104 | task069 Session 1 (W&B publisher) | 559 → 577 |
| #106 | task069 Session 2 (publisher wiring) | 577 → 592 |

共 86 new tests / 7 substantive PRs since roadmap refresh.

## 下一候选 (sandbox-runnable per roadmap §5b)

- task040 Session 2 — wire sampler into prepare_m0_assets.py /
  prepare_m1_agentic_sft.py via `--curriculum-policy` CLI flag
- task057 Session 1 — M0 tier2 expansion (lights up RLVR2/RLVR3 active)
- task068 Session 1 — RLHF tool-call pairing harness design doc

Cluster-bound queue (waiting on NemTron access)：task013 Session 2b /
task014 Session 2 cluster / task016 Session 3 / task017 Session 3 /
task018 Sessions 3-4 / task019 Sessions 2-3 / task020 Session 3 /
task021 Session 4 / task069 Session 3 / task070 Sessions 2-3。
