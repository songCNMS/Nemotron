# History Log

## 2026-05-30

- Created evidence-only branch
  `intern_nem_dev_2/task220_qwen_sft_8gpu_full_data_one_iter_live_s1` from
  exact product commit `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Probed full task208 data visibility. NemTron did not see
  `/mnt/cephfs/data/processing/nemotron-live-validation/task208/packed_qwen_full/splits`,
  while local CPU did.
- Staged dereferenced full split data to NemTron-visible
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/input_task208_full`.
  The staged copy is `489M` and includes `blend.json`, `splits/metadata.json`,
  16 train parquet shards, 1 validation shard, and 1 test shard. Local and
  remote hashes matched in `00_full_data_staging.log`.
- Staged task-owned code checkout and config under task220 artifact root. Commit
  marker is `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Resource preflight passed: no SGLang/task210 process, no `:13000`, no H200
  compute apps, all 8 H200 visible, master port `29591` free, and `:8000`
  documented/untouched.
- Data/config probe passed with PYTHONPATH order:
  task218 `pip_target`, task209 Mamba target, task209 session4 venv
  site-packages, and task220 staged `src`. Probe confirmed
  `qwen3_30b_a3b_local_train.py`, `super3_packed_seq_compat_gpt_step`,
  Qwen training contract validation, `train_iters=1`, `global_batch_size=8`,
  `micro_batch_size=1`, and checkpoint `finetune=false`.
- Launched exactly one canonical 8-GPU torchrun. Result: `task220_torchrun_rc=0`.
- Run reached iteration `1/1`, consumed 8 samples, reported
  `lm loss: 1.226097E+01`, `load_balancing_loss: 3.226302E+00`,
  skipped/nan `0/0`, and validation loss `1.043498E+01`.
- Checkpoint saved at
  `/mnt/cephfs/data/processing/nemotron-live-validation/task220/session1/checkpoints_one_iter`.
  Size is `399G`; `latest_checkpointed_iteration.txt` is `1`.
- Post-run cleanup found no task220 torchrun/Qwen processes, no H200 compute
  apps, `:13000` clear, master port `29591` clear, and `:8000`
  documented/untouched.
