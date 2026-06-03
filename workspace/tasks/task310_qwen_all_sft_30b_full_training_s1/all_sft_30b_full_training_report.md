# task310 Qwen all-SFT 30B full training report

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=6 -->

Generated: 2026-06-03T16:28:00Z

## Disposition

Recommendation:
`TRAINING_LOOP_COMPLETE__VALIDATION_NO_LOG_PROGRESS_PENDING_LEAD_DECISION__CHECKPOINT_CANDIDATE`.

This is not a clean `PASS_TRAINING`. After lead clearance and after the
task308/task309/task312 prerequisite docs merged, I refreshed task310 from
current `origin/main` and launched the bounded Qwen3-30B-A3B all-SFT training
attempt using only the constrained V11/task299 packed seed. The training loop
reached `35/35` iterations, logged finite loss at every iteration, recorded
skipped iterations `0` and NaN iterations `0`, and saved `iter_0000035`.

The harness then entered built-in validation at `Evaluating on 80 samples` /
`Evaluating iter 1/10`. As of the final read-only snapshot at
`2026-06-03T16:26:54Z`, there was no `train_rc.txt`, no `train_end.txt`, no log
progress since `2026-06-03T16:10:22Z`, and the task310 torchrun/rank process
tree remained alive with GPU memory retained. I did not kill, restart, export,
evaluate, or promote anything. Lead decision is needed for continued wait
versus checkpoint-salvage termination.

## Checked revisions

- Current `origin/main`: `004870e7d790778b5cdae5cc574257fdc19ec755`.
- #374/task308 prerequisite merge:
  `eb05e6b324c3159b01070cb575c2be363e773cac`.
- #372/task309 prerequisite merge:
  `af388ea858cd0b7582a37397188b03f69e8927b4`.
- #375/task312 prerequisite merge:
  `004870e7d790778b5cdae5cc574257fdc19ec755`.
- Task310 worker branch:
  `intern_nemotron_worker_5/task310_qwen_all_sft_30b_full_training_s1`.
- Local refreshed branch head before this report commit:
  `11651f8ada734e813198bc9c0ccdaa473f26939f`.
- Task310 PR #373 remote head before this refresh:
  `a85b192e7632bd2da0e117fdaf994d8c70e16549`.

## Artifact roots

| Item | Path |
|---|---|
| Local output root | `/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z` |
| Remote run root | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z` |
| Remote repo sync | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/Nemotron` |
| Model/tokenizer | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` |
| Pretrained checkpoint | `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0` |
| Packed source root | `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b` |
| Packed dereferenced mirror used for training | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/input/task299_packed_qwen_30b_deref_mirror` |
| Training log | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/logs/train_30b_sft.log` |
| Local copied log | `/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/logs/train_30b_sft.log` |
| Checkpoints | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints` |
| Final checkpoint candidate | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035` |

## Gate refresh

| Gate | Observed state | Task310 effect |
|---|---|---|
| task308 inventory audit | #374 merged at `eb05e6b324c3159b01070cb575c2be363e773cac` | prerequisite carried |
| task309 packed contract | #372 merged at `af388ea858cd0b7582a37397188b03f69e8927b4`; scope constrained to V11/task299 seed; generic `stage1_sft/data_blend_raw` remains NO-GO | prerequisite carried with raw-stage exclusion |
| task312 independent review | #375 merged at `004870e7d790778b5cdae5cc574257fdc19ec755` | prerequisite carried |
| Runtime/resource route | task298 imported checkpoint root exists; 8x H200 were idle in preflight; model path exists | launch allowed |
| Training data scope | used only task299 packed root mirror; no generic raw stage1 data | launch allowed |

## Launch command and config

Command record:

- remote:
  `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/manifests/launch_command.txt`
- local:
  `/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/manifests/launch_command.txt`

Key launch values:

- Start time: `2026-06-03T15:52:15Z`.
- Host: `lg-cmc-b7r201-f08u26-h200-000126`.
- GPUs: 8x NVIDIA H200 via `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`.
- Launcher: `torch.distributed.run --standalone --nnodes=1 --nproc_per_node=8`.
- Train script:
  `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`.
- Config:
  `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml`.
- `train.train_iters=35`.
- `train.global_batch_size=8`.
- `train.micro_batch_size=1`.
- `train.eval_interval=1000`.
- `optimizer.lr=5e-7`.
- `optimizer.min_lr=1e-7`.
- `scheduler.lr_warmup_iters=4`.
- `scheduler.lr_decay_iters=35`.
- `logger.log_interval=1`.
- `rng.seed=5678`.
- `checkpoint.save_interval=5`.
- TP `4`, PP `2`, EP `4`, ETP `1`; sequence parallel enabled.

## Mirror and preflight evidence

| Check | Result |
|---|---|
| Source packed manifest entries | `391` |
| Remote dereferenced mirror entries | `391` |
| Source symlinks | `0` |
| Remote mirror symlinks | `0` |
| Source manifest sha256 | `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c` |
| Remote deref manifest sha256 | `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c` |
| Source and remote file-list sha256 | `1d418bac82757ec5181c84cd97c483509d822abc27ef2da74eec67c857ffd2f3` |
| Preflight summary | `PASS` |
| Preflight summary sha256 | `cff95dc1c07325b9192677670d68fe3b64a54759919879c5ce5db0b82d1b10b3` |
| Preflight log sha256 | `ad77dc68a80257e6df954cfc9471cc48d0e4f62f5fb8f7091c7d8c7ef4bcb1f2` |
| Launch script sha256 | `714a0452e5cf938bf91376db5421b2164d386c48547f2bc295bef01122e576b6` |
| Launch command sha256 | `c50bdeca383359aa6656884df707089321813efbf36bd01933e2b58389910777` |

## Metrics through iteration 35

All logged iterations had skipped iterations `0` and NaN iterations `0`.

| Iteration | LR | LM loss | Load-balancing loss | Grad norm | Skipped | NaN |
|---|---:|---:|---:|---:|---:|---:|
| 21 | `2.697144E-07` | `7.534869E-01` | `1.502317E+00` | `11.376` | `0` | `0` |
| 22 | `2.498695E-07` | `8.425900E-01` | `1.615112E+00` | `15.620` | `0` | `0` |
| 23 | `2.305389E-07` | `6.281261E-01` | `1.701327E+00` | `17.179` | `0` | `0` |
| 24 | `2.119212E-07` | `8.780735E-01` | `1.507595E+00` | `11.545` | `0` | `0` |
| 25 | `1.942072E-07` | `6.136650E-01` | `1.949437E+00` | `21.632` | `0` | `0` |
| 26 | `1.775788E-07` | `8.895993E-01` | `1.523858E+00` | `13.469` | `0` | `0` |
| 27 | `1.622066E-07` | `9.074771E-01` | `2.249084E+00` | `16.024` | `0` | `0` |
| 28 | `1.482484E-07` | `9.223882E-01` | `1.647860E+00` | `19.373` | `0` | `0` |
| 29 | `1.358473E-07` | `7.260578E-01` | `2.295766E+00` | `9.224` | `0` | `0` |
| 30 | `1.251307E-07` | `9.049843E-01` | `1.571475E+00` | `12.138` | `0` | `0` |
| 31 | `1.162084E-07` | `8.690767E-01` | `2.489673E+00` | `13.554` | `0` | `0` |
| 32 | `1.091721E-07` | `1.021454E+00` | `3.455631E+00` | `14.228` | `0` | `0` |
| 33 | `1.040940E-07` | `1.107199E+00` | `3.713996E+00` | `20.643` | `0` | `0` |
| 34 | `1.010261E-07` | `9.652730E-01` | `3.414926E+00` | `17.146` | `0` | `0` |
| 35 | `1.000000E-07` | `8.339980E-01` | `1.434514E+00` | `9.114` | `0` | `0` |

No validation metric is available because validation did not progress past
`Evaluating iter 1/10` during the watch window.

## Current blocker evidence

Final read-only snapshot:
`/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/snapshots/validation_no_log_progress_snapshot_20260603T162618Z.txt`.

Snapshot findings:

- `train_rc.txt`: missing.
- `train_end.txt`: missing.
- `latest_checkpointed_iteration.txt`: `35`.
- `iter_0000035`: present, `399G`, `28` files.
- Training log mtime/size:
  `2026-06-04 00:10:22.278145960 +0800`, `272450` bytes.
- Log tail remains at `Evaluating on 80 samples` / `Evaluating iter 1/10`.
- Process tree remains alive under wrapper PID `1389026`, torchrun PID
  `1389032`, and rank PIDs `1389104` through `1389111`.
- GPU snapshot retained approximately `81-86 GiB` per H200 with `0%` GPU util.
- Traceback/OOM/rank-exit scan found no crash evidence; the only matched lines
  were config fields `error_injection_rate` and `error_injection_type`.
- No termination signal was sent.

## Checkpoint inventory and checksums

Final checkpoint candidate:
`/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`.

Inventory:

- Size from `du -sh`: `399G`.
- File count: `28`.
- Inventory manifest:
  `/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/manifests/iter_0000035_inventory.tsv`.
- Inventory manifest sha256:
  `b30d83f641118da8d7a24438e6c379ba9a5e8e03793ef5ff26514d751d9fa676`.

Selected copied evidence hashes:

| Artifact | sha256 |
|---|---|
| `logs/train_30b_sft.log` | `506d4d8f24ee9cac592929b89a43aac251da4d959e69799081792a26884b0786` |
| `manifests/preflight_summary.json` | `cff95dc1c07325b9192677670d68fe3b64a54759919879c5ce5db0b82d1b10b3` |
| `manifests/launch_command.txt` | `c50bdeca383359aa6656884df707089321813efbf36bd01933e2b58389910777` |
| `launch_train.sh` | `714a0452e5cf938bf91376db5421b2164d386c48547f2bc295bef01122e576b6` |
| `snapshots/validation_no_log_progress_snapshot_20260603T162618Z.txt` | `cef2c3bd063217eda593f998f92b71378c297a2e96c81e1bed06898c4100a20e` |
| `manifests/local_copied_evidence.sha256` | `1117b04041f22b72f659be6479a9a23dc0f17472168fa04ac2733a6f80c2d2db` |

The 399G checkpoint payload hash manifest is intentionally not computed yet
because validation processes are still alive and no lead decision has cleared
termination/salvage handling. The lightweight inventory is complete.

## Boundary confirmation

Confirmed for Session 6:

- no generic `stage1_sft/data_blend_raw` inclusion;
- no AIME2025 prompts or labels as train rows;
- no task255 reuse;
- no deletion under `/mnt/cephfs/data/processing/lei.song`;
- no silent model downgrade;
- no export;
- no endpoint;
- no promotion;
- no benchmark eval, canary, or task311 handoff run;
- no product-code edit;
- no direct `main` push;
- no merge.

## Residual risks and requested lead action

1. The training loop reached 35/35 and produced a checkpoint candidate, but the
   harness has not exited cleanly and has no `train_rc.txt` or `train_end.txt`.
2. Built-in validation has no log progress past `Evaluating iter 1/10`, so no
   validation metric is available.
3. The final checkpoint is only a candidate until lead decides whether to keep
   waiting or explicitly authorize termination/salvage inventory.
4. No eval/export/endpoint/promotion path is cleared by this report.
