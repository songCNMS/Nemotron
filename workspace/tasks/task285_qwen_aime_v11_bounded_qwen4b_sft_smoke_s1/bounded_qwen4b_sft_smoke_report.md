# task285 Bounded Qwen3-4B SFT Smoke Report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=4 -->

## Disposition

`PASS_SMOKE_EVIDENCE_WITH_POST_TRAIN_EVAL_RC1_RISK`.

The bounded Qwen3-4B smoke produced valid smoke evidence: Bridge-approved base
import completed before optimizer execution, retry3 ran exactly two optimizer
iterations on two visible GPUs, both logged nonzero LR and finite loss, and
iteration-2 checkpoint artifacts were written. The retry3 command returned
`SMOKE_RETRY3_COMMAND_RC=1` after bounded training completed because the
framework entered a built-in validation path and the task-owned process received
SIGTERM during `Evaluating iter 1/32`.

This RC=1 is a residual post-train eval/finalization risk. It does not erase the
bounded training/checkpoint evidence, but it means the artifact should be
reviewed as a bounded smoke checkpoint only, not as an end-to-end training/eval
pass, quality claim, promotion signal, export clearance, or task243/AIME
clearance.

## Run Identity

- Task: `task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1`
- Branch at evidence collection: `intern_nemotron_worker_2/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1`
- Source head synced to NemTron: `c53095a639f0ccf8ce34afcec1bdf302cf45add6`
- Local output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`
- Remote run root:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z`
- Remote repo sync path:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/Nemotron`
- Remote venv:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/venv`
- Host: `lg-cmc-b7r201-f08u26-h200-000126`
- GPU visibility for smoke: `CUDA_VISIBLE_DEVICES=0,1`; the host has more GPUs,
  but the task command used only GPUs 0 and 1.

## Inputs

- Qwen3-4B base model:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Task276 accepted packed root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`
- Remote task276 copy used by smoke:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/task276_input/packed_qwen`
- Pre-optimizer manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/manifests/fail_closed_pre_optimizer_preflight_manifest.json`
- Pre-optimizer manifest sha256:
  `3b0a3bf3233eacfe8f727ad74e73c9062a86717be7a8c127e452b9fb6283c83c`
- Pre-optimizer status: `PASS`
- Data counts from preflight: train `279` rows, valid `1` row, test `0` rows.

## Dependency And Import Remediation

Used a task-owned venv with `--system-site-packages` and targeted `--no-deps`
installs. The task283 import stack was present, then the training import
blockers were remediated with:

- `nvidia-resiliency-ext==0.6.0`
- `hydra-core==1.3.2`
- `defusedxml==0.7.1`

Post-remediation import probe showed:

- `nvidia_resiliency_ext.inprocess=PASS`
- `nemotron.recipes.super3.stage1_sft.train=PASS`
- `megatron.bridge.training.finetune=PASS`
- `hydra=PASS`

`lightning` and `nemo.collections.llm` remained failing on `lightning`, but the
bounded Qwen local training path did not require that import route.

## Base Import Proof

Bridge-approved base import ran before optimizer execution:

- Remote checkpoint:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/qwen3_4b_bridge_import_iter0`
- Log:
  `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/logs/bridge_import_base_proof.log`
- Log evidence: `IMPORT_DONE`, `BRIDGE_IMPORT_RC=0`
- Log sha256:
  `cb1523fffcd97d2b9e5e3b76141624d0d67ad9d2fb1d061e150f15fc7fbf66e6`
- Checksum manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/manifests/bridge_import_base_proof_checksums.sha256`
- Checksum manifest sha256:
  `8ed6f1d3ce637e4ea2c6742a7fe7d7baea6757f85a19870119e5c659c14f347f`

## Smoke Command

Retry3 script:

`/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/scripts/run_bounded_qwen4b_sft_smoke_retry3.sh`

Script sha256:

`14ec9206372a292486ea2a5fff68ec9d35536b4ff80de5901a6e27ade2f12321`

Effective command:

```bash
CUDA_VISIBLE_DEVICES=0,1 \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
SUPER3_M1_AGENTIC_PACKED_DIR=/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/task276_input/packed_qwen/splits \
SUPER3_M1_TRAINING_PROFILE=qwen \
SUPER3_M1_PRETRAINED_CHECKPOINT=/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/qwen3_4b_bridge_import_iter0 \
SUPER3_M1_SFT_SAVE=/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3 \
/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/venv/bin/python -m torch.distributed.run \
  --standalone --nnodes=1 --nproc_per_node=2 \
  src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py \
  --config src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml \
  train.train_iters=2 train.global_batch_size=2 train.micro_batch_size=1 \
  train.eval_interval=100 optimizer.lr=5e-7 ++optimizer.min_lr=1e-7 \
  scheduler.lr_warmup_iters=0 ++scheduler.lr_decay_iters=2 logger.log_interval=1 \
  checkpoint.save=/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3 \
  checkpoint.load=null checkpoint.save_interval=1 \
  checkpoint.pretrained_checkpoint=/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/qwen3_4b_bridge_import_iter0
```

## Optimizer Evidence

Retry3 log:

`/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/logs/bounded_qwen4b_sft_smoke_retry3.log`

Log sha256:

`096e622a94beae16c114afcf6d6cdd923b01f77d4f5a76200b22eed5fcf0767e`

Logged optimizer evidence:

- Iteration 1: LR `3.000000E-07`, lm loss `1.506399E+00`, grad norm
  `24.782`, skipped iterations `0`, nan iterations `0`.
- Iteration 2: LR `1.000000E-07`, lm loss `8.874496E-01`, grad norm
  `33.138`, skipped iterations `0`, nan iterations `0`.

## Checkpoint Evidence

- Remote checkpoint root:
  `/root/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/smoke_checkpoints_retry3`
- Latest checkpointed iteration: `2`
- Checkpoint size: `105G`
- Inventory file count: `34`
- Inventory:
  `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/manifests/smoke_checkpoints_retry3_inventory.tsv`
- Inventory sha256:
  `d4cc3d1e5a047e321e98896996610f1ace0b5c45acd3cbe11bb0a8389ea97b78`
- Checksum manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task285_qwen_aime_v11_bounded_qwen4b_sft_smoke_s1/run_20260602T061036Z/manifests/smoke_checkpoints_retry3_checksums.sha256`
- Checksum manifest sha256:
  `802ef28a30b7ae5a2359b481fc6c8882d1cc2804d0f1edd25cca84973f7794c4`
- Size file sha256:
  `164ec4a7d609a3dd7b39efeab70867244a1f48e45b7eb21365f3db8eef7274dd`
- Latest-iteration file sha256:
  `d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35`

## Post-Train Eval / SIGTERM Risk

After the iteration-2 checkpoint was saved, the framework entered its built-in
validation path and logged `Evaluating on 64 samples` and `Evaluating iter
1/32`. The task-owned process was then terminated with SIGTERM and the launcher
recorded `SMOKE_RETRY3_COMMAND_RC=1`.

This affects the run as follows:

- It is not a clean end-to-end command pass.
- The built-in validation result is incomplete and should not be used.
- The checkpoint remains reviewable bounded smoke evidence because the task
  acceptance surface is one to two optimizer steps from verified base import,
  nonzero LR, finite loss, and task-owned checkpoint artifacts.

No further retry/training attempt was launched after lead requested pause.

## Boundary Confirmation

Confirmed for task285:

- Qwen3-4B only.
- At most two GPUs used by the smoke command: `CUDA_VISIBLE_DEVICES=0,1`.
- At most two optimizer iterations ran.
- No live canary.
- No AIME/task243 eval.
- No export.
- No endpoint.
- No promotion or go/no-go claim.
- No AIME2025 prompts or labels used as trainable rows.
- No task255 reuse.
- No deletion or overwrite under `/mnt/cephfs/data/processing/lei.song`.
- No main push.
- No 30B or 8-GPU use.

## Recommendation

Treat retry3 as ready for independent review as a bounded Qwen3-4B smoke
checkpoint artifact, with explicit residual risk that the post-train built-in
validation path was interrupted and returned rc `1`. Do not proceed to canary,
AIME/task243 eval, export, endpoint, promotion, or scale without a separate lead
gate.
