# task301 30B Full SFT Training Report

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nemotron_worker_5,SESSION=14 -->

Generated: 2026-06-02T16:37:54Z

## Disposition

Recommendation: `STILL_RUNNING_VALIDATION_WATCH`.

Lead cleared task301 launch after runtime/resource gate, independent review,
task299 data/packing gate, and task300 same-harness 30B base comparator were
accepted or merged. The bounded Qwen3-30B-A3B V11 SFT command was launched on
NemTron and reached `35/35` training iterations with skipped iterations `0` and
NaN iterations `0`. Checkpoint `iter_0000035` is present and
`latest_checkpointed_iteration.txt` reports `35`.

The command has not completed because the training harness entered its built-in
post-training validation. As of the latest read-only snapshot at
`2026-06-02T16:37:54Z`, no `train_rc.txt` or `train_end.txt` exists, and the log
tail remains at `Evaluating on 80 samples` / `Evaluating iter 1/10` with log
mtime `2026-06-03 00:23:43.221057699 +0800`. All eight rank processes are still
alive, holding GPU memory, and show CPU activity with TorchInductor compile
worker children. This is therefore classified as
`STILL_RUNNING_VALIDATION_WATCH`, because the quiet phase is still before the
30-minute wait threshold from the last log mtime.

## Branch And Sources

| Item | Value |
|---|---|
| Worker branch | `intern_nemotron_worker_5/task301_qwen_aime_v11_30b_full_sft_training_s1` |
| PR | #362 `https://github.com/songCNMS/Nemotron/pull/362` |
| Launch main | `origin/main` `e400cea8a1604bc95cc430a194811ff553b99401` |
| Lead clearance | task301 launch clearance received for bounded/full Qwen3-30B-A3B V11 SFT |
| Base comparator | task300/#363 accepted 30B base `15/30 = 0.5` |
| Model path | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` |
| Task299 source packed root | `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b` |
| Accepted task-owned packed mirror | `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/input/task299_packed_qwen_30b_deref_mirror` |
| Pretrained checkpoint root | `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0` |
| Local output root | `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z` |
| Remote run root | `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z` |
| Remote repo sync | `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/Nemotron` |
| NemTron host | `lg-cmc-b7r201-f08u26-h200-000126` |

## Mirror And Preflight Evidence

| Check | Result |
|---|---|
| Dereferenced mirror file count | `391` files |
| Dereferenced mirror symlink count | `0` symlinks |
| Source deref manifest sha256 | `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c` |
| Remote deref manifest sha256 | `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c` |
| Preflight summary | `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests/preflight_summary.json` |
| Local preflight summary copy | `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests/preflight_summary.json` |
| Local preflight summary sha256 | `31ee7ec77a7b22d2e4ac7f7edde2fe550df948708392552bd674e9cfa58f1ba0` |

## Launch Command And Environment

Command record:
`/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/manifests/launch_command.txt`
and local copy:
`/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/launch_command.txt`.

Key bindings:

- `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`
- `PYTHONPATH=/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/Nemotron/src`
- `WANDB_MODE=disabled`
- model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- packed splits:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/input/task299_packed_qwen_30b_deref_mirror/splits`
- pretrained checkpoint:
  `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`
- checkpoint root:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints`
- log:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/logs/train_30b_sft.log`
- Python module:
  `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`
- config:
  `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml`

Training arguments:

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
- `checkpoint.pretrained_checkpoint=/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`
- parallelism observed from config/run: TP `4`, PP `2`, EP `4`, ETP `1`,
  sequence parallel enabled
- GPUs: 8x NVIDIA H200

## Live Runtime Snapshot

Read-only snapshot command family:

```bash
ssh NemTron "date -u +%Y-%m-%dT%H:%M:%SZ; test -f '$REMOTE_RUN/train_rc.txt' && cat '$REMOTE_RUN/train_rc.txt' || echo MISSING; test -f '$REMOTE_RUN/train_end.txt' && cat '$REMOTE_RUN/train_end.txt' || echo MISSING; stat -c '%y %s %n' '$REMOTE_RUN/logs/train_30b_sft.log'; tail -60 '$REMOTE_RUN/logs/train_30b_sft.log'; cat '$REMOTE_RUN/checkpoints/latest_checkpointed_iteration.txt'; find '$REMOTE_RUN/checkpoints' -maxdepth 1 -type d -name 'iter_*' -printf '%f\n' | sort; nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader; ps -o pid,ppid,stat,etime,pcpu,pmem,rss,args -p 1258208,1258209,1258210,1258278,1258279,1258280,1258281,1258282,1258283,1258284,1258285"
```

Snapshot at `2026-06-02T16:37:54Z`:

- `train_rc.txt`: missing
- `train_end.txt`: missing
- log mtime/size:
  `2026-06-03 00:23:43.221057699 +0800`, `272557` bytes
- latest checkpoint marker: `35`
- checkpoint directories:
  `iter_0000005`, `iter_0000010`, `iter_0000015`, `iter_0000020`,
  `iter_0000025`, `iter_0000030`, `iter_0000035`
- GPUs show `0%` utilization but retain rank memory allocations:
  approximately `81.5 GiB` to `88.1 GiB` per GPU
- eight rank PIDs `1258278` through `1258285` remain alive, each with CPU
  activity around `67%` to `78%` in the snapshot
- TorchInductor compile-worker children: `198`

Log tail ending:

```text
[2026-06-03 00:19:25] iteration       35/      35 | consumed samples:          280 | elapsed time per iteration (ms): 3649.8 | learning rate: 1.000000E-07 | global batch size:     8 | lm loss: 8.325640E-01 | load_balancing_loss: 1.434611E+00 | loss scale: 1.0 | grad norm: 9.089 | number of skipped iterations:   0 | number of nan iterations:   0 |
saving checkpoint at iteration      35 to /root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints in torch_dist format
Storing distributed optimizer sharded state of type dp_reshardable
  successfully saved checkpoint from iteration      35 to /root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints [ t 1/4, p 1/2 ]
INFO:megatron.core.timers:(min, max) time across ranks (ms):
    save-checkpoint ................................: (109332.44, 109332.57)
Deleting CUDA graphs
[after training is done] datetime: 2026-06-03 00:21:16
saving checkpoint at iteration      35 to /root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints in torch_dist format
Storing distributed optimizer sharded state of type dp_reshardable
  successfully saved checkpoint from iteration      35 to /root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints [ t 1/4, p 1/2 ]
Evaluating on 80 samples
Evaluating iter 1/10
```

## Metrics So Far

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

Validation metrics are not available yet because the process has not advanced
past `Evaluating iter 1/10` or written a return code.

## Classification And Wait Policy

Classification at `2026-06-02T16:37:54Z`:
`STILL_RUNNING_VALIDATION_WATCH`.

Rationale:

- checkpointing and training reached the configured end state;
- no return-code or end timestamp exists;
- ranks are alive with CPU activity;
- GPU memory remains allocated by the rank processes;
- many TorchInductor compile-worker children are present, which is consistent
  with a quiet CPU-heavy compile/validation phase;
- there is no traceback, OOM, rank-exit message, skipped iteration, or NaN
  evidence in the observed log tail.

No task document or code comment found in this session proves that validation is
expected to be CPU-only or quiet for a specific duration. The safe operational
threshold for this run is therefore read-only monitoring until either:

1. the log advances or `train_rc.txt` / `train_end.txt` appears; or
2. the quiet phase reaches 30 minutes from the last log mtime
   (`2026-06-02T16:53:43Z`), at which point I will report
   `VALIDATION_TEARDOWN_BLOCKER_NO_LOG_PROGRESS` with process/GPU evidence and
   wait for lead clearance before any interrupt, restart, export, eval, or
   follow-on action.

Official mailbox `a8351925601040fa91d7862479201ff8` sent this disposition to
`intern_nemotron_lead`; previous immediate live-status mailbox
`3bf90a62cca94a939f8e55321fdaea1c` reported the same evidence with
`STILL_RUNNING_VALIDATION`.

## Boundary Confirmation

Confirmed for Session 14:

- no AIME2025 prompts or labels were used as train rows;
- no task255 reuse;
- no deletion under `/mnt/cephfs/data/processing/lei.song`;
- no canary, corrected AIME FT eval, task243 eval, export, endpoint,
  promotion, or 30B follow-on work;
- no direct `main` push;
- no merge.

## Residual Risks

1. The command has not returned, so the run is not a completed training closeout
   yet despite checkpoint `iter_0000035` being present.
2. Built-in validation may be stuck in a quiet compile/eval path; this remains
   unconfirmed until the log advances, return-code files appear, or lead clears
   an intervention after the wait threshold.
3. Full artifact inventory and checkpoint checksum handoff are pending command
   completion or explicit lead guidance for read-only collection while the
   process is still alive.
