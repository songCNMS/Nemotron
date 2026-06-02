# task301 30B Full SFT Training Report

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=15 -->

Generated: 2026-06-02T17:06:07Z

## Disposition

Recommendation:
`TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`.

This is not a training PASS and does not authorize eval, export, endpoint, or
promotion. The bounded Qwen3-30B-A3B V11 SFT training loop reached `35/35`
iterations, saved `iter_0000035`, and recorded skipped iterations `0` plus NaN
iterations `0` through iteration 35. The harness then hung in built-in
validation at `Evaluating on 80 samples` / `Evaluating iter 1/10`.

After lead salvage clearance, I sent SIGTERM to the task301 torchrun parent.
The wrapper wrote `train_rc.txt=1` and
`train_end.txt=2026-06-02T16:58:51Z`. All matching task301 processes exited and
8x H200 memory released to `1 MiB` per GPU with no compute apps. Checkpoint
`iter_0000035` remains present and fully inventoried/checksummed as a salvage
candidate.

## Artifact Roots

| Item | Path |
|---|---|
| Local output root | `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z` |
| Remote run root | `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z` |
| Remote repo sync | `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/Nemotron` |
| Model/tokenizer | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` |
| Pretrained checkpoint | `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0` |
| Packed mirror used for training | `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/input/task299_packed_qwen_30b_deref_mirror` |
| Final checkpoint candidate | `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035` |
| Remote log | `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/logs/train_30b_sft.log` |
| Local copied log | `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/logs/train_30b_sft.log` |
| Local copied manifests | `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests` |

## Launch Command And Config

Command record:

- remote:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests/launch_command.txt`
- local:
  `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/launch_command.txt`

Key launch values:

- `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`
- GPUs: 8x NVIDIA H200
- train script:
  `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`
- config:
  `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml`
- `train.train_iters=35`
- `train.global_batch_size=8`
- `train.micro_batch_size=1`
- `train.eval_interval=1000`
- `optimizer.lr=5e-7`
- `optimizer.min_lr=1e-7`
- `scheduler.lr_warmup_iters=4`
- `scheduler.lr_decay_iters=35`
- `logger.log_interval=1`
- `rng.seed=5678`
- `checkpoint.save_interval=5`
- `checkpoint.load=null`
- TP `4`, PP `2`, EP `4`, ETP `1`; sequence parallel enabled

## Mirror And Preflight Evidence

| Check | Result |
|---|---|
| Dereferenced mirror file count | `391` files |
| Dereferenced mirror symlink count | `0` symlinks |
| Source deref manifest sha256 | `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c` |
| Remote deref manifest sha256 | `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c` |
| Remote source mirror manifest sha256 | `a5b05d1e3a8ea2724e09058e3e7646ae5c1d499adb93be12d28eca78ce73190b` |
| Preflight summary sha256 | `31ee7ec77a7b22d2e4ac7f7edde2fe550df948708392552bd674e9cfa58f1ba0` |
| Launch command sha256 | `6e92c6d9919f4bc7389f6aa52bc75fd997e9b5047f283d7609c6c3caf64ad90e` |

## Metrics Through Iteration 35

| Iteration | LR | LM loss | Skipped | NaN |
|---|---:|---:|---:|---:|
| 21 | `2.697144E-07` | `7.563179E-01` | `0` | `0` |
| 22 | `2.498695E-07` | `8.387560E-01` | `0` | `0` |
| 23 | `2.305389E-07` | `6.281770E-01` | `0` | `0` |
| 24 | `2.119212E-07` | `8.773594E-01` | `0` | `0` |
| 25 | `1.942072E-07` | `6.128101E-01` | `0` | `0` |
| 26 | `1.775788E-07` | `8.853100E-01` | `0` | `0` |
| 27 | `1.622066E-07` | `9.091095E-01` | `0` | `0` |
| 28 | `1.482484E-07` | `9.191547E-01` | `0` | `0` |
| 29 | `1.358473E-07` | `7.257143E-01` | `0` | `0` |
| 30 | `1.251307E-07` | `9.035335E-01` | `0` | `0` |
| 31 | `1.162084E-07` | `8.692110E-01` | `0` | `0` |
| 32 | `1.091721E-07` | `1.019659E+00` | `0` | `0` |
| 33 | `1.040940E-07` | `1.110444E+00` | `0` | `0` |
| 34 | `1.010261E-07` | `9.629388E-01` | `0` | `0` |
| 35 | `1.000000E-07` | `8.325640E-01` | `0` | `0` |

Built-in validation did not finish. No validation metric should be treated as
available.

## Termination Evidence

Lead cleared salvage after the validation quiet threshold passed. Final
pre-termination snapshot at `2026-06-02T16:56:37Z` showed:

- `train_rc.txt`: missing
- `train_end.txt`: missing
- log still stopped at `Evaluating on 80 samples` / `Evaluating iter 1/10`
- `latest_checkpointed_iteration.txt`: `35`
- `iter_0000035`: present, `399G`, `28` files
- no traceback, OOM, or rank-exit evidence before intervention

Signal command used:

```bash
ssh NemTron "REMOTE_RUN='/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z' bash -s"
# inside remote shell:
kill -TERM 1258209
```

Signal details:

- timestamp: `2026-06-02T16:58:51Z`
- signal: `SIGTERM`
- target PID: `1258209`
- target role: torchrun parent for the task301 run
- wrapper/root PID: `1258208`
- torchrun propagated SIGTERM to rank PIDs `1258278` through `1258285`
- no SIGKILL was used
- no files or artifacts were deleted

Post-termination state:

- `train_rc.txt`: `1`
- `train_end.txt`: `2026-06-02T16:58:51Z`
- matching task301 processes: none in the `2026-06-02T17:06:07Z` snapshot
- GPU compute apps: none
- GPU memory: `1 MiB` on each of 8x H200 in the final snapshot
- log sha256: `e832845262135dca009d1373f8eeb04a6f3b18e5079f40a6456f20b999b49863`

Snapshot and termination logs:

| Artifact | Local sha256 |
|---|---|
| `final_pre_termination_snapshot.txt` | `9b8f00c1b43e9c9e7be55a1cd8c0e4441b2c41c4eabf28b6736a3c621af62004` |
| `termination_signal_log.txt` | `eb864b2f5d59b499d21acb6ab71c96423b191c312c2679d7bbe8e1a0e0fa1520` |
| `final_post_termination_snapshot.txt` | `37751467429c03d3be121419272fa2405849f82db38ac53bca2b089d7e5f4042` |

## Checkpoint Inventory And Checksums

Final checkpoint candidate:
`/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`.

Inventory:

- size from `du -sh`: `399G`
- file count: `28`
- inventory manifest:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests/iter_0000035_inventory.tsv`
- local copy:
  `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests/iter_0000035_inventory.tsv`
- inventory manifest sha256:
  `7c7e60b5bf9a5e747e3115e37701da00b6643cd1c895e3336bef175dc6d13261`

Checksum manifest:

- remote:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests/iter_0000035.sha256`
- local copy:
  `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests/iter_0000035.sha256`
- checksum entries: `28`
- checksum manifest sha256:
  `c3f2d4b4b5d1c26041d96e5eb8799cf591acef346f75ebfdcdce40a12ec09c03`

The large shard hashes are in `iter_0000035.sha256`; examples:

- `.metadata`:
  `ce48299ffeeef27c010305692c3efc381ae41ed46996ca80715e3f95e720e641`
- `__0_0.distcp`:
  `34e8fbdb0d5cfa15fa0211bc0ae61966d5d4db67d37dee8d4c7184e3ddd57cc5`
- `__7_1.distcp`:
  `8e9e74da7a83bacbb1a025fd93e1f4af584a6d8a69f6f5a21a9fb13624dbe92c`
- `train_state.pt`:
  `e1672b3e3a9a72bb810de9b67a92e695085cdd3eaf2476c22802a3fdb74c8349`

## Salvage Manifest Bundle

| Artifact | Local sha256 |
|---|---|
| `salvage_selected_files.list` | `0f0de7b0d87c314a098fb4221d6a1a251b386cc93d137275a74c53be9b4edbe5` |
| `salvage_artifact_inventory.tsv` | `09d5dc4d1a0184e63fc9aba19126eece23266179c7e4a99e674da8038d33ead0` |
| `salvage_selected_files.sha256` | `1b2a767f72c64764cc481735ac1d2ab1825f92adf6e14ec671a61cae01663692` |
| `iter_0000035_inventory.tsv` | `7c7e60b5bf9a5e747e3115e37701da00b6643cd1c895e3336bef175dc6d13261` |
| `iter_0000035.sha256` | `c3f2d4b4b5d1c26041d96e5eb8799cf591acef346f75ebfdcdce40a12ec09c03` |
| `salvage_manifest_files.sha256` | `bf44b0a0bf4a779c66bb1da7f0e9833a858816d9af1b5b7086d9b6ded65ba04e` |
| `train_rc.txt` | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` |
| `train_end.txt` | `42ffcab01712e58025acf93d78b966fe591b16c1f77e58fd24d33f0c3d22ac36` |
| `train_30b_sft.log` | `e832845262135dca009d1373f8eeb04a6f3b18e5079f40a6456f20b999b49863` |

Full copied-file hash manifest:
`/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests/local_salvage_copied_files.sha256`.

## Boundary Confirmation

Confirmed for Session 15:

- no canary, corrected AIME FT eval, or task243 eval;
- no export;
- no endpoint;
- no promotion;
- no follow-on 30B work;
- no task255 reuse;
- no AIME2025 prompts or labels as train rows;
- no deletion under `/mnt/cephfs/data/processing/lei.song`;
- no direct `main` push;
- no merge.

## Residual Risks

1. The harness did not exit cleanly; it exited after lead-cleared SIGTERM with
   `train_rc=1`.
2. Built-in validation did not finish, so no validation metric is available.
3. Checkpoint `iter_0000035` is a salvage candidate, not an accepted final FT
   artifact, until a checkpoint artifact review explicitly accepts it.
4. No eval/export/endpoint/promotion path is cleared by this report.
