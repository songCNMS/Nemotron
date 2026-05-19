# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Idle -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Idle |
| Current Task | - |
| PR | - |
| Session | 64 |

刚做完：task014 Session 2 sandbox part — RLVR1 smoke wiring (PR #78 /
abe2dde, merged 2026-05-19)。3 件事:

1. **Bridge extension** (`prepare_m1_rlvr_jsonl.py`)：加 `combined.jsonl`
   = concat(train_rows, val_rows) — val 在最末；manifest 加
   `combined_path`；lineage outputs 加 `m1_rlvr_combined_jsonl` kind
2. **`data_prep/rlvr1.yaml` 翻面**：input_path 从 `/lustre/.../yifuw/...`
   改成 `${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlvr/rlvr1/combined.jsonl`
3. **`stage1_rlvr/config/smoke.yaml`** 新：2 nodes / 8 prompts/step /
   max_num_steps=10 / val_at_end=true / defaults: default.yaml

12 个新 pytest case；sandbox 测试基线 409 → 421 passed + 7 skipped。

task014 整 task：Session 1 ✓ + Session 2 sandbox 部分 ✓；cluster 真
launch (Ray + vLLM + NeMo-Gym services) 仍待 — 这是任何 task014/015/016/
017/018 真 RL 跑都需要的，等接到 NemTron cluster。

下一候选 (sandbox-runnable):
- **task016 Session 2** — M0 SWE pivot converter unit tests (SWE-Gym-Lite /
  R2E-Gym → single-step shape；HF download skipped)
- **task017 Session 2** — OpenHands loop wrapper + SWE2 trace converter
  (wrapper unit tests；真 Docker run skipped)
- **task018 Session 2** — HelpSteer-2 / UltraFeedback converter unit tests
- 之前 task 的 Session 2+ — 大都需 cluster
