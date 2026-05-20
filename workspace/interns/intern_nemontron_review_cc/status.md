# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task013_super3_sft_two_stage_loss -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task013_super3_sft_two_stage_loss |
| PR | pending push |
| Session | 73 |

正在做：task013 Session 2a — two-stage finetune driver + stage-a/b YAML
chain (sandbox part of Session 2; Session 2b cluster verify deferred to
real nvcr Megatron-Bridge container).

## What's in this PR

### `stage1_sft/two_stage_finetune.py` 新模块

- `StageInvocation` frozen dataclass：stage / config_path /
  step_function / cli_overrides / expected_checkpoint_save
- `TwoStageResult` frozen dataclass：stage_a_checkpoint_save +
  stage_b_checkpoint_save + tuple of two StageInvocations
- `run_two_stage_finetune(stage_a_config_path, stage_b_config_path, *, finetune_fn=None, recipe_builder=None, cli_overrides=None)`:
  - Reads Stage A YAML，assert `step_function` resolves to `gpt_step`
    (or absent → default gpt_step)；reads `checkpoint.save`
  - Reads Stage B YAML，assert `step_function` is
    `super3_sample_level_step`；reads `checkpoint.save`
  - Lazy-imports `train.run_finetune` + `train._default_recipe_builder`
    only when `finetune_fn` / `recipe_builder` are not injected (keeps
    sandbox import light)
  - Invokes finetune_fn twice：Stage A 用 operator overrides；Stage B
    用 operator overrides + `checkpoint.pretrained_checkpoint=<stage_a save>`
  - Tags 各自 `task013 / stage-{a,b} / {token,sample}-level` 给 W&B
    dashboard filter

### `stage1_sft/config/stage_a_default.yaml` 新

- Mirrors default.yaml；explicit `step_function: gpt_step`；
  `checkpoint.save: /nemo_run/super3-sft-stage-a-model`（distinct from
  Stage B path）；`convert_to_hf.enabled: false`（Stage A intermediate）

### `stage1_sft/config/stage_b_default.yaml` 新

- `step_function: super3_sample_level_step`；
  `checkpoint.pretrained_checkpoint: TWO_STAGE_DRIVER_OVERRIDES_THIS`
  placeholder；`checkpoint.save: /nemo_run/super3-sft-stage-b-model`；
  `convert_to_hf.enabled: true`（Stage B final）；`train_iters: 800`
  (vs Stage A 1700 — sample-level loss tighter convergence)

### Tests (`test_two_stage_finetune.py`, 14 cases)

- Driver dispatch 6: 调用两次 / 路径正确 / Stage A → B checkpoint
  override 接好 / Stage A 不被 override / operator overrides 流到两边 /
  tags 各自正确
- Result shape 1: TwoStageResult 字段 + 2 invocations
- step_function 验证 3: Stage A 拒 sample-level / Stage B 拒 gpt_step /
  Stage A 缺 step_function 默认 gpt_step pass
- Error surfaces 2: missing YAML / missing checkpoint.save
- Shipped defaults 3: stage_a_default 满足 driver preconditions /
  stage_b_default uses sample-level step / end-to-end against shipped
  configs

Sandbox 测试基线 506 → **520 passed + 7 skipped** (14 new)。

## task013 状态

- Session 1 ✓ (PR #44 / 10e1393) — dispatch + math
- Session 2a ✓ (this PR) — driver + YAMLs
- Session 2b ☐ — cluster verify in nvcr Megatron-Bridge container

下一候选 (sandbox-runnable per roadmap §5b)：task040 Session 1 (W1
curriculum sampler) / task057 Session 1 (M0 tier2) / task068 Session 1
(RLHF tool-call pairing design) / task069 Session 1 (W&B publisher) /
task070 Session 1 (OpenHands wrapper protocol + fake)。
