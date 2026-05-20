# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 96 |

刚做完：task057 Session 3 — sql_text_to_query env + BIRD converter +
sql_execution_match verifier (PR #120 / 8e1e7fe, merged 2026-05-20).

- 新 M0 env `sql_text_to_query` (family `structured_query`)
- 新 converter `transform_bird_sql` — accepts 4 gold-SQL column
  conventions; preserves `db_id` for cross-schema stratification
- 新 verifier `sql_execution_match` with SQL normalization (lowercase +
  whitespace + backticks + trailing semicolon); M0 oracle stub
  delegates to normalized string match; real execution = M2 task024
- 29 个新 pytest case; sandbox 测试基线 692 → 721 passed + 7 skipped
- Data_registry row 故意延后 (HF SHA + CC-BY-SA-4.0 license-cascade
  audit clearance)

## task057 整 task 进展

- Session 1 ✓ (PR #108) — multilingual_instruct (Aya)
- Session 2 ✓ (PR #118) — long_context_qa_smoke (LongAlpaca-12k)
- Session 3 ✓ (PR #120) — sql_text_to_query (BIRD-SQL)
- Sessions 1.5/2.5/3.5 ☐ — pin HF SHAs + add data_registry rows
- Sessions 4-6 ☐ — terminal-tier2 / safety_reasoning_smoke /
  math_with_tools

## 本轮 sprint 累积 (PR #94 起算)

14 substantive PRs + 14 closeouts:

| PR | 内容 | sandbox baseline |
|---|---|---|
| #94 | Roadmap refresh + 4 gap-task scaffolds | 502 |
| #95 | task067 → task070 rename | 506 |
| #97 | task013 Session 2a | 520 |
| #99 | task040 Session 1 | 543 |
| #101 | task070 Session 1 | 559 |
| #104 | task069 Session 1 | 577 |
| #106 | task069 Session 2 | 592 |
| #108 | task057 Session 1 | 620 |
| #110 | task068 Session 1 | 620 |
| #112 | task068 Session 2 | 651 |
| #114 | task068 Session 3 | 662 |
| #116 | task040 Session 2 | 675 |
| #118 | task057 Session 2 | 692 |
| #120 | task057 Session 3 | 721 |

Sandbox baseline 502 → 721 passed (219 new tests across the sprint).

## 下一候选 (sandbox-runnable per roadmap §5b)

task057 Sessions 4-6 (3 remaining tier-2 envs):
- Session 4: terminal-tier2 (`epinnock/intercode-nl2bash-curated`)
- Session 5: safety_reasoning_smoke (`nvidia/Nemotron-Content-Safety-Reasoning-Dataset`;
  needs schema verification)
- Session 6: math_with_tools (`MathLLMs/MathCodeInstruct`; needs
  NuminaMath dedup)

Cluster-bound queue unchanged.
