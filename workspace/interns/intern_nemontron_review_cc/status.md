# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 90 |

刚做完：task068 Session 3 — CLI dispatch + RLHF env registry flip to
active (PR #114 / 6cc0f4c, merged 2026-05-20).

- 新 M0 env `rlhf_toolcall_paired` in environment_registry
- Converter env-name updated to M0 name (bridge maps to NeMo-Gym)
- 新 CLI `scripts/prepare_rlhf_toolcall_pairing.py` — stream pipeline
  writing paired.jsonl + manifest.json with lineage
- RLHF env_registry `single_step_tool_use_with_argument_comparison`
  row flipped m0_missing → **active**; `RLHF_ENV_MAP` lights up
- 3 RLHF bridge today-tests flipped (parallel task016/017/018 S2 pattern)
- 11 个新 CLI test + 3 修改; sandbox 测试基线 651 → 662 passed + 7 skipped

## task068 整 task 进展

- Session 1 ✓ (PR #110) — design doc
- Session 2 ✓ (PR #112) — converter implementation
- Session 3 ✓ (PR #114) — CLI dispatch + env flip
- Session 4 ☐ — cluster smoke (needs task018 Session 3 judge service +
  end-to-end RLHF pipeline)

**task068 sandbox part 100% 落地** — RLHF parallel tool-call validity
env is now wired end-to-end (data layer + converter + CLI + env_registry).
真 launch 需 cluster + judge service.

## 本轮 sprint 累积 (PR #94 起算)

11 substantive PRs + 9 closeouts:

| PR | 内容 | sandbox baseline |
|---|---|---|
| #94 | Roadmap refresh + 4 gap-task scaffolds | 502 |
| #95 | task067 → task070 rename | 506 |
| #97 | task013 Session 2a (two-stage SFT driver) | 520 |
| #99 | task040 Session 1 (curriculum sampler) | 543 |
| #101 | task070 Session 1 (OpenHands wrapper) | 559 |
| #104 | task069 Session 1 (W&B publisher + CLI) | 577 |
| #106 | task069 Session 2 (publisher wiring) | 592 |
| #108 | task057 Session 1 (multilingual_instruct) | 620 |
| #110 | task068 Session 1 (design doc) | 620 |
| #112 | task068 Session 2 (converter) | 651 |
| #114 | task068 Session 3 (CLI + env flip) | 662 |

Sandbox baseline 502 → 662 passed (160 new tests across the sprint).

## 下一候选 (sandbox-runnable per roadmap §5b)

- task040 Session 2 — wire sampler into prepare_m0_assets.py /
  prepare_m1_agentic_sft.py via `--curriculum-policy` CLI flag
- task057 Session 2 — long_context_qa_smoke env via `THUDM/LongAlpaca-12k`
- task057 Sessions 3-6 — sql / terminal-tier2 / safety / math_with_tools

Cluster-bound queue (waiting on NemTron access)：task013 Session 2b /
task014 Session 2 cluster / task016 Session 3 / task017 Session 3 /
task018 Sessions 3-4 / task019 Sessions 2-3 / task020 Session 3 /
task021 Session 4 / task057 Session 1.5 (HF SHA) / task068 Session 4 /
task069 Session 3 / task070 Sessions 2-3。
