# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 88 |

刚做完：task068 Session 2 — `transform_rlhf_toolcall_pairing` converter
(PR #112 / 2f85e63, merged 2026-05-19).

- 新 module `m0_data_env/rlhf_toolcall_pairing.py` — pure-Python stream
  converter implementing Session 1's 4-filter design:
  - 16-keyword relevance filter
  - Function-name match gold-call finder with required-arg tiebreak
  - Exact + 5-gram contamination check (`build_eval_prompt_set` helper)
  - Stream orchestrator yielding argument_match-shaped paired rows
  - Both filter functions injectable for operator customization
  - `PAIRED_CONTAMINATION_AGAINST` = (BFCL, TauBench airline, MCP-Mark,
    HelpSteer1) on every output row
- 31 个新 pytest case covering all 4 design-doc worked examples
- Sandbox 测试基线 620 → 651 passed + 7 skipped

## task068 整 task 进展

- Session 1 ✓ (PR #110) — design doc
- Session 2 ✓ (PR #112) — converter implementation
- Session 3 ☐ — flip RLHF env registry tool-call row to active +
  wire CLI dispatch path that calls this converter
- Session 4 ☐ — cluster smoke (needs task018 Session 3 judge service)

## 本轮 sprint 累积 (PR #94 起算)

10 substantive PRs + 8 closeouts:

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

Sandbox baseline 502 → 651 passed (149 new tests).

## 下一候选 (sandbox-runnable per roadmap §5b)

- task040 Session 2 — wire sampler into prepare_m0_assets.py /
  prepare_m1_agentic_sft.py via `--curriculum-policy` CLI flag
- task057 Session 2 — long_context_qa_smoke env via `THUDM/LongAlpaca-12k`
- task068 Session 3 — flip RLHF env registry's tool-call row to active +
  wire CLI dispatch path

Cluster-bound queue (waiting on NemTron access)：task013 Session 2b /
task014 Session 2 cluster / task016 Session 3 / task017 Session 3 /
task018 Sessions 3-4 / task019 Sessions 2-3 / task020 Session 3 /
task021 Session 4 / task057 Session 1.5 (HF SHA) / task068 Session 4 /
task069 Session 3 / task070 Sessions 2-3。
