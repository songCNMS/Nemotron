# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 76 |

刚做完：task040 Session 1 — W1 difficulty curriculum sampler (PR #99 /
a090453, merged 2026-05-19)。

- 新 module `m0_data_env/difficulty_sampler.py`：
  - `BUCKET_ORDER = ("trivial", "unknown", "hard")` 对齐 task008 vocabulary
  - `bucket_rows(rows, *, policy, rng=None)` — 4 policies (easy_first /
    hard_first / shuffle / as_is)；stable within bucket
  - `filter_solved(rows, *, pass_rates, threshold=0.9)` — strict >
    threshold；row_id 解析 m0_source_id > source_id > id > instance_id
  - `weighted_sample(rows, *, weights, n, rng, replace=False)` — 替换/
    无替换 / 0-weight 处理 / 负权重 raises
- 23 个新 pytest case；sandbox 测试基线 520 → 543 passed + 7 skipped
- Closes plan §6 W1 long-pending deliverable (sampler 之前 scaffolded
  but never written)

task040 整 task：Session 1 ✓；Sessions 2-4 待 (Session 2 wiring + 3
numeric pass-rate + 4 per-env YAML policy)。

## 平行进展

`intern_nemontron_code_reading` 同步落地 task071_m1_agentic_qwen_scaleup_train_exec
(commit 8336c3e) — Qwen M1 Agentic SFT scale-up 训练执行 follow-on
to their task066 / task067_m1_agentic_qwen_scaleup line. 跟我的工作没
冲突；只是 task ID space 现在 task071 也被占了。

## 下一候选 (sandbox-runnable per roadmap §5b)

- task040 Session 2 — wire sampler into prepare_m0_assets.py /
  prepare_m1_agentic_sft.py via `--curriculum-policy` CLI flag
- task057 Session 1 — M0 tier2 expansion (lights up RLVR2/RLVR3 active)
- task068 Session 1 — RLHF tool-call pairing harness design doc
- task069 Session 1 — W&B lineage publisher (injectable W&B run +
  FakeWandbRun + scripts/publish_lineage.py CLI)
- task070 Session 1 — OpenHands wrapper Protocol + FakeOpenHandsLoop stub

Cluster-bound queue (waiting on NemTron access)：task013 Session 2b /
task014 Session 2 cluster part / task016 Session 3 / task017 Session 3 /
task018 Sessions 3-4 / task019 Sessions 2-3 / task020 Session 3 /
task021 Session 4。
