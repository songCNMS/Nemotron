# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task013_super3_sft_two_stage_loss -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task013_super3_sft_two_stage_loss |
| PR | pending push |
| Session | 31 |

正在做：task013 Session 1 — plan §5.1 两阶段 SFT loss 的 dispatch hook +
sample-level loss math + adapter skeleton。这是 critical-path 第 9 条 +
REVIEW #9 (✗ 至今)。审计 omni3 `_STEP_FUNCTIONS` dispatch 模式后落地 4 个
模块：

- `sample_level_loss.py` — 纯 torch helper (per-sequence mean → batch
  mean over non-empty samples)，边界处理 fully-masked → 0、bf16 → float32
- `sample_level_step.py` — Megatron-Bridge forward_step adapter (cluster
  verify 等 Session 2)
- `step_dispatch.py` — 独立模块 `_STEP_FUNCTIONS` + `_load_forward_step`
  （不引重 deps，sandbox 直测）
- `train.py` 接入 dispatch：默认 `gpt_step` → 现有 YAML byte-for-byte 同
  行为

12 个新 pytest case (7 loss math + 5 dispatch)，sandbox 测试基线 125
→ 129 passed + 2 skipped (torch 缺时 sample_level_loss 整文件跳；adapter
解析那条也跳)。Session 2 (driver + stage-a/stage-b YAML + cluster verify)
不在本 PR。
