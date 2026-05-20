# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 98 |

刚做完：task057 Session 4 — terminal-tier2 via intercode-nl2bash +
quote normalization enhancement (PR #122 / 7730b8f, merged 2026-05-20).

- 新 converter `transform_intercode_nl2bash` extends existing
  `terminal_basic_shell` env (no new env or verifier needed)
- 200-char smoke cap; field aliases (nl/instruction/prompt + cmd/bash/
  command/response); `source_dataset_kind` tier-1/tier-2 stratification
- `normalize_command_text` 加 double → single quote canonicalization
  (back-compat preserved)
- 26 个新 pytest case; sandbox 测试基线 721 → 747 passed + 7 skipped
- Data_registry row 故意延后 to Session 4.5 (HF SHA pin)

## task057 整 task 进展

- Session 1 ✓ (PR #108) — multilingual_instruct
- Session 2 ✓ (PR #118) — long_context_qa_smoke
- Session 3 ✓ (PR #120) — sql_text_to_query
- Session 4 ✓ (PR #122) — terminal-tier2 (intercode-nl2bash)
- Sessions 1.5/2.5/3.5/4.5 ☐ — HF SHA pins
- Sessions 5-6 ☐ — safety_reasoning_smoke / math_with_tools

## 本轮 sprint 累积 (PR #94 起算)

15 substantive PRs + 15 closeouts:

| PR | 内容 | sandbox baseline |
|---|---|---|
| #94-#106 | (roadmap refresh + 7 substantive sessions) | 502 → 592 |
| #108 | task057 Session 1 (multilingual) | 620 |
| #110-#114 | task068 Sessions 1+2+3 | 662 |
| #116 | task040 Session 2 (curriculum wiring) | 675 |
| #118 | task057 Session 2 (long_context_qa_smoke) | 692 |
| #120 | task057 Session 3 (sql_text_to_query) | 721 |
| #122 | task057 Session 4 (terminal-tier2) | 747 |

Sandbox baseline 502 → 747 passed (245 new tests across the sprint).

## 下一候选 (sandbox-runnable per roadmap §5b)

task057 Sessions 5-6 (2 remaining tier-2 envs):
- Session 5: safety_reasoning_smoke
  (`nvidia/Nemotron-Content-Safety-Reasoning-Dataset`; needs schema
  verification first per README — dataset viewer errors)
- Session 6: math_with_tools (`MathLLMs/MathCodeInstruct`; needs
  NuminaMath dedup)

Cluster-bound queue unchanged.
