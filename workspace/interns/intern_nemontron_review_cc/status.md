# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 86 |

刚做完：task068 Session 1 — RLHF tool-call pairing harness design doc
(PR #110 / 40a0faa, merged 2026-05-19).

- `task068_design.md` (~440 lines) captures 4 strategy decisions:
  - **Relevance filter**: keyword + Hermes template match (~30% pass)
  - **Gold-call sourcing**: function-name match heuristic + arg tiebreak
  - **Sampling cap K=1**: one pair per HelpSteer-2 prompt
  - **Decontamination**: BFCL / TauBench airline / MCP-Mark / HelpSteer1
- Corpus estimate: 7K HelpSteer-2 train → ~1,200 paired rows (83% drop)
- 4 worked examples + reference output-row JSON + Session 2 converter
  interface contract + 3 open questions for product alignment
- No code (design-only); sandbox baseline unchanged at 620 passed +
  7 skipped

## task068 整 task

- Session 1 ✓ (PR #110) — design doc
- Session 2 ☐ — implement `transform_rlhf_toolcall_pairing` converter
- Session 3 ☐ — flip RLHF env registry tool-call row to active
- Session 4 ☐ — cluster smoke (needs task018 Session 3 judge service)

## 本轮 sprint 累积 (PR #94 起算)

9 substantive PRs + 7 closeouts:

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

Sandbox baseline 502 → 620 passed (118 new tests across sandbox-runnable
work; PR #110 doc-only so no test delta).

## 下一候选 (sandbox-runnable per roadmap §5b)

- task040 Session 2 — wire sampler into prepare_m0_assets.py /
  prepare_m1_agentic_sft.py via `--curriculum-policy` CLI flag
- task057 Session 2 — long_context_qa_smoke env via `THUDM/LongAlpaca-12k`
- task068 Session 2 — implement `transform_rlhf_toolcall_pairing`
  converter per Session 1's design doc (natural follow-on)
- task069 Session 2 都已完成；其他 task069 Session 3 / cluster work

Cluster-bound queue (waiting on NemTron access)：task013 Session 2b /
task014 Session 2 cluster / task016 Session 3 / task017 Session 3 /
task018 Sessions 3-4 / task019 Sessions 2-3 / task020 Session 3 /
task021 Session 4 / task057 Session 1.5 (HF SHA) / task068 Session 4 /
task069 Session 3 / task070 Sessions 2-3。
