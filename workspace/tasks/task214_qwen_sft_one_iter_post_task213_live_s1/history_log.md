# History Log

<!-- METADATA:SESSION=1 -->

## Session 1 - 2026-05-30

- Accepted PM task214 on branch
  `intern_nem_dev_2/task214_qwen_sft_one_iter_post_task213_live_s1` from
  exact merged main commit `4fe9454e46343821f68e43c47cdeba1aaf0fef84`.
- Staged a task-owned code checkout on NemTron at
  `/mnt/cephfs/data/processing/nemotron-live-validation/task214/Nemotron` and
  wrote `.task214_commit` with the exact product commit.
- Created a task-owned Qwen smoke config with
  `step_function: super3_packed_seq_compat_gpt_step` and Qwen train-entrypoint
  metadata.
- Reused the task209 train stack:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session4/venv`
  and
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/session5/build_mamba_force/pip_target`.
- Reused task208 sample packed data staged for task209 under
  `/mnt/cephfs/data/processing/nemotron-live-validation/task209/input_task208_sample4`.
- Probed data hashes, imports, and step-function resolution; the probe
  confirmed the registry maps `super3_packed_seq_compat_gpt_step` to
  `nemotron.recipes.super3.stage1_sft.packed_compat_step:forward_step`.
- Ran preflight: no SGLang/task210 process, no `:13000` listener, no H200
  compute apps, torchrun master port `29561` free, and `:8000` left untouched.
- Launched exactly one canonical single-GPU Qwen-contract torchrun with
  `CUDA_VISIBLE_DEVICES=0`, `train.train_iters=1`,
  `checkpoint.save_interval=1`, W&B disabled, and manifest root null.
- The run reached training loop iteration 0 and failed with
  `TypeError: forward_step() missing 1 required positional argument: 'model'`
  from the two-argument branch of `packed_compat_step.py`.
- Ran post-run state probe: checkpoint path missing, no H200 compute apps,
  `:13000` and `:29561` clear, and `:8000` still documented-only.
- Copied remote logs/config/commit marker into the local-visible task214
  artifact root and recorded a local visibility manifest.
- Stopped live validation per PM one-run boundary; no second launch or
  workaround was attempted.
