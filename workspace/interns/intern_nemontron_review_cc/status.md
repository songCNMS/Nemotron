# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task014_m1_rlvr_data_bridge -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task014_m1_rlvr_data_bridge |
| PR | pending push |
| Session | 63 |

正在做：task014 Session 2 (sandbox part) — RLVR1 smoke wiring。3 件事:

1. **Bridge extension** (`prepare_m1_rlvr_jsonl.py`)：加 `combined.jsonl`
   = concat(train_rows, val_rows) — val 在最末；manifest 加
   `combined_path`；lineage outputs 加 `m1_rlvr_combined_jsonl` kind
2. **`data_prep/rlvr1.yaml` 翻面**：input_path 从 `/lustre/.../yifuw/...`
   改成 `${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_rlvr/rlvr1/combined.jsonl`
   + 加 M0 → bridge → data_prep pipeline 注释
3. **`stage1_rlvr/config/smoke.yaml`** 新：2 nodes / 8 prompts/step /
   4 train batch / max_num_steps=10 / val_at_end=true / defaults: default.yaml

12 个新 pytest case；sandbox 测试基线 409 → 421 passed + 7 skipped。

真 `nemotron super3 rl rlvr1 -c smoke` 启动 (Ray + vLLM + NeMo-Gym
services) 仍需 cluster — 这是 task014/015/016/017/018 真 RL 跑都需要
的，等接到 NemTron cluster。
