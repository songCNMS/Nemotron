# task212_qwen_sft_one_iter_post_task211_live_s1

Owner: `intern_nem_dev_2`

Branch: `intern_nem_dev_2/task212_qwen_sft_one_iter_post_task211_live_s1`

Base commit: `f65dafdb15b28342c1fbd4a5ead807052bcdd264`

Artifact root:

`/mnt/cephfs/data/processing/nemotron-live-validation/task212`

## Scope

Evidence-only live validation after task211 / PR #309. Rerun exactly one
canonical single-GPU Qwen-contract Stage1 SFT one-iteration smoke on NemTron
using the fixed code at `f65dafdb15b28342c1fbd4a5ead807052bcdd264`.

## Boundaries

- No product code edits.
- No system package mutation.
- No package build/install unless PM separately authorizes.
- No NemTron network download.
- No process kill.
- No full or multi-GPU train.
- No eval/benchmark, endpoint, W&B, cluster/deploy, artifact upload, main/master
  push, or self-merge.

## Result

PM accepted the single run as task212 evidence because the task-owned config
included `step_function: super3_packed_seq_compat_gpt_step` and the traceback
entered `packed_compat_step.py`.

Failed after one canonical run: the fixed-code smoke reached the training loop,
then failed with:

```text
TypeError: forward_step() missing 1 required positional argument: 'model'
```

The final blocker is `PACKED_COMPAT_STEP_UPSTREAM_FORWARD_ARITY`: current
Megatron Bridge `gpt_step.forward_step` expects
`(state, data_iterator, model, return_schedule_plan=False)`, while the task211
adapter called it with `(data_iterator, compat_model)`.

The traceback points to:

`src/nemotron/recipes/super3/stage1_sft/packed_compat_step.py`

No checkpoint was created.
