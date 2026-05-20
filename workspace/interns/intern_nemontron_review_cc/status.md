# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 84 |

刚做完：task057 Session 1 — M0 tier-2 expansion 第一个 env
(`multilingual_instruct` via `CohereLabs/aya_dataset`) (PR #108 /
d5d215c, merged 2026-05-19)。

- 整 task scaffold 拆 6 sessions (一 session 一 env)
- 新 M0 env `multilingual_instruct` (family `multilingual`, verifier
  `multilingual_exact_or_contains`)
- 新 converter `transform_aya_multilingual` — 6-lang scope filter
  (de/es/fr/it/ja/zh)，supports `inputs/targets` + `instruction/response`
  aliases
- 新 verifier `multilingual_exact_or_contains` — Unicode NFC + casefold；
  preserves CJK punctuation；不 strip English articles
- 28 个新 pytest case；sandbox 测试基线 592 → 620 passed + 7 skipped
- Data_registry row deferred to Session 1.5 (需 HF access 拿真 Aya
  commit SHA — task065 加 `tbd` to FLOATING_REVISION_REFS 后 unpinned
  rows correctly 被 audit 阻挡)

## task057 整 task 进展

- Session 1 ✓ (PR #108) — multilingual_instruct env + converter + verifier
- Session 1.5 ☐ — pin Aya SHA + add data_registry row (HF access)
- Sessions 2-6 ☐ — 5 envs more (long_context / sql / terminal /
  safety / math_with_tools)

## 本轮 sprint 累积 (PR #94 起算)

8 substantive PRs + 6 closeouts:
- #94 roadmap refresh + 4 gap-task scaffolds
- #95 task067 → task070 rename
- #97 task013 Session 2a (two-stage SFT driver)
- #99 task040 Session 1 (curriculum sampler)
- #101 task070 Session 1 (OpenHands wrapper)
- #104 task069 Session 1 (W&B publisher + CLI)
- #106 task069 Session 2 (publisher wiring into 6 bridges)
- #108 task057 Session 1 (multilingual_instruct env)

Sandbox baseline 502 → 620 passed (114 new tests across the sprint).

## 下一候选 (sandbox-runnable per roadmap §5b)

- task040 Session 2 — wire sampler into prepare_m0_assets.py /
  prepare_m1_agentic_sft.py via `--curriculum-policy` CLI flag
- task057 Session 2 — long_context_qa_smoke env via `THUDM/LongAlpaca-12k`
- task068 Session 1 — RLHF tool-call pairing harness design doc

Cluster-bound queue (waiting on NemTron access)：task013 Session 2b /
task014 Session 2 cluster / task016 Session 3 / task017 Session 3 /
task018 Sessions 3-4 / task019 Sessions 2-3 / task020 Session 3 /
task021 Session 4 / task057 Session 1.5 (HF SHA) / task069 Session 3 /
task070 Sessions 2-3。
