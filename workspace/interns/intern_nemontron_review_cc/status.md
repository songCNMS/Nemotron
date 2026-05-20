# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 94 |

刚做完：task057 Session 2 — long_context_qa_smoke env + LongAlpaca
converter + long_context_qa_stub verifier (PR #118 / 3ca0b32, merged
2026-05-20).

- 新 M0 env `long_context_qa_smoke` (family `long_context`)
- 新 converter `transform_longalpaca_qa` — Alpaca-format I/O + 32K
  char smoke cap (rejects above-cap rows; truncation would change
  answer-span semantics)
- 新 verifier `long_context_qa_stub` wired into `score_record` (M0
  oracle stub delegating to contains-match; real span-aware verifier
  deferred to M2 task028/task037)
- 17 个新 pytest case; sandbox 测试基线 675 → 692 passed + 7 skipped
- Data_registry row 故意延后 to Session 2.5 (HF SHA pin needed)

## task057 整 task 进展

- Session 1 ✓ (PR #108) — multilingual_instruct (Aya)
- Session 1.5 ☐ — pin Aya SHA + add data_registry row
- Session 2 ✓ (PR #118) — long_context_qa_smoke (LongAlpaca-12k)
- Session 2.5 ☐ — pin LongAlpaca SHA + add data_registry row
- Sessions 3-6 ☐ — sql_text_to_query / terminal-tier2 /
  safety_reasoning_smoke / math_with_tools

## 本轮 sprint 累积 (PR #94 起算)

13 substantive PRs + 13 closeouts:

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
| #116 | task040 Session 2 (curriculum wiring) | 675 |
| #118 | task057 Session 2 (long_context_qa_smoke) | 692 |

Sandbox baseline 502 → 692 passed (190 new tests across the sprint).

## 下一候选 (sandbox-runnable per roadmap §5b)

- task057 Sessions 3-6 — 4 remaining tier-2 M0 envs:
  - Session 3: sql_text_to_query (BIRD; needs new `sql_execution_match` verifier)
  - Session 4: terminal-tier2 (intercode-nl2bash; extends existing
    terminal_basic_shell)
  - Session 5: safety_reasoning_smoke (Nemotron-Safety; needs
    schema verification first)
  - Session 6: math_with_tools (MathCodeInstruct; needs NuminaMath dedup)

Cluster-bound queue 不变 — 接到 NemTron cluster 时 12+ cluster sessions
排队等候。
