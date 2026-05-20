# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 92 |

刚做完：task040 Session 2 — wire curriculum sampler into
prepare_m1_agentic_sft (PR #116 / 168406c, merged 2026-05-20).

- 4 new CLI flags on `prepare_m1_agentic_sft.py`:
  `--curriculum-policy {as_is,easy_first,hard_first,shuffle}` /
  `--curriculum-seed` / `--curriculum-pass-rates-json` /
  `--curriculum-solved-threshold`
- New `_apply_curriculum_to_train(train_rows, *, policy, seed,
  pass_rates_path, solved_threshold)` helper — drop-then-reorder;
  val rows NEVER reordered (shadow-eval stability)
- Manifest gains `curriculum` audit block (locked 7-key shape)
- Default `as_is` policy = byte-for-byte back-compat passthrough
- 13 个新 pytest case; sandbox 测试基线 662 → 675 passed + 7 skipped
- Documented divergence from scaffold: M0 prep NOT wired because
  `difficulty_bucket` is populated by the M1 converter (task008), not
  M0 prep — M0 has no meaningful bucket to sample on

## task040 整 task 进展

- Session 1 ✓ (PR #99) — sampler primitives
- Session 2 ✓ (PR #116) — wired into M1 agentic SFT
- Session 3 ☐ — numeric pass-rate filter via task032 rollout store
  (M2 dependency)
- Session 4 ☐ — per-env curriculum policy YAML

## 本轮 sprint 累积 (PR #94 起算)

12 substantive PRs + 11 closeouts:

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

Sandbox baseline 502 → 675 passed (173 new tests across the sprint).

## 下一候选 (sandbox-runnable per roadmap §5b)

- task057 Sessions 2-6 — 5 more tier-2 M0 envs (long_context_qa_smoke /
  sql_text_to_query / terminal-tier2 / safety_reasoning_smoke /
  math_with_tools)
- 已没 sandbox-runnable single-shot picks 剩；下面都需 cluster

Cluster-bound queue (waiting on NemTron access)：task013 Session 2b /
task014 Session 2 cluster / task016 Session 3 / task017 Session 3 /
task018 Sessions 3-4 / task019 Sessions 2-3 / task020 Session 3 /
task021 Session 4 / task040 Sessions 3-4 (待 task032 M2) / task057
Session 1.5 (HF SHA) / task068 Session 4 / task069 Session 3 /
task070 Sessions 2-3。
