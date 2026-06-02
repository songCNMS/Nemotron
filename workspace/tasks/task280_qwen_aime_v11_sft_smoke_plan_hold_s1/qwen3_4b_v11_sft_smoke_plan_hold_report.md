# task280 Qwen3-4B V11 SFT Smoke Plan HOLD

<!-- METADATA:STATUS=PlanningHold,ASSIGNEE=intern_nemotron_worker_1,SESSION=1 -->

Generated: 2026-06-02T04:49:36Z

Disposition: `PLAN_READY_HOLD_TASK278_TASK279_RELEASE`.

This is a no-run planning report only. It does not authorize training,
nonzero-LR smoke execution, live canary, AIME/task243 eval, export, endpoint,
promotion, task255 reuse, AIME2025 train data, shared deletion, merge, main
push, or 30B/8-GPU.

## Release Gate

The bounded smoke command below must remain held until all of these are true:

1. task278 no-training config/import preflight is complete and accepted at an
   exact branch/head/artifact set.
2. task279 independent review processes task278 and returns approval for
   no-training preflight readiness.
3. Lead explicitly releases a nonzero-LR Qwen3-4B SFT smoke execution task and
   provides or confirms the exact task278 accepted pretrained/import checkpoint
   root.

Current review status from this worker:

- task278 and task279 docs are visible only on lead docs branch
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `be45766c6fc127b0ba00e784d84810a378b3e8e4`.
- No task278/task279 PR is visible through `gh pr list --search`.
- Therefore the smoke route is planned but execution remains HOLD.

## Accepted Inputs

### task276 packed root

- PR #344: `MERGED`.
- Merge commit:
  `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`.
- Merged head:
  `07efab4fa0d8367e96f54af3d2cdc70768d73595`.
- Fresh packed root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`.
- Splits root:
  `/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen/splits`.
- Evidence manifest sha256:
  `74f3c58283eef46a3b8f63699d730baa90337b9a7177146822170c22ec29e9ee`.
- Shard checksum list sha256:
  `bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312`.
- Split manifest sha256:
  `65501e0eff31cce77ff2d1e36dd915f66fb6b2fd145e0f59701d251e5b7d02c5`.
- Packed metadata sha256:
  `e4ac2157760dd50e50798a9095bf3ea1fb6834e5f405cac2f877560f42dbafd9`.
- Packed blend sha256:
  `6e64fdaf30582d5d0f6ed78f93759b86148ef21263e2a5d931dad62575234eef`.

task276 split evidence:

| Split | Exposed shards | Packed rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| train | 46 | 279 | 1024646 | 228927 |
| valid | 1 | 1 | 1491 | 1428 |
| test | 1 | 0 | 0 | 0 |

task276 Qwen/data safety evidence:

- Qwen packed-data contract: PASS.
- Tokenizer/model:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Packed chat template: tokenizer-native Qwen template.
- `enable_thinking=false`.
- `truncate_history_thinking=false`.
- AIME pattern mentions: 0.
- Label-like top-level keys: 0.
- task246 heldout prompt-hash overlaps: 0.
- task246 system+user prompt-hash overlaps: 0.
- task262 final-answer blocker rows/pairs: 0.

### Qwen3-4B base and checkpoint

- HF base/tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Pretrained/import checkpoint for the smoke:
  `TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT`.

`TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT` is intentionally not resolved in
this report. It must come from the accepted task278/task279 evidence and must
not be task255 or a task255-derived checkpoint/export.

## Candidate Smoke Settings

The smoke is intentionally small and nonzero-LR:

| Setting | Value |
|---|---|
| Model | Qwen3-4B only |
| Entry point | `src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py` |
| Config | `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml` |
| Packed source | task276 packed root staged into a task280-owned run root |
| Sequence length | 4096 |
| Max train steps | 3 |
| Global batch size | 2 |
| Micro batch size | 1 |
| Nodes | 1 |
| GPUs | 2 H100/H200-class GPUs for Qwen3-4B tensor parallel size 2 |
| Optimizer LR | `1e-6` |
| Optimizer min LR | `1e-6` |
| Warmup iters | 0 |
| LR decay iters | 3 |
| Eval interval | 3 |
| Save interval | 3 |
| WandB | disabled/offline |
| HF export | disabled |
| Live AIME/task243 eval | disabled |

Rationale:

- 3 steps is enough to prove nonzero-LR optimizer/data/checkpoint flow while
  bounding exposure to the sparse V11 pilot data.
- 2 GPUs matches `qwen_local_train.py`, which sets Qwen3-4B tensor model
  parallel size to 2.
- LR `1e-6` is deliberately conservative and nonzero.
- `eval_interval=3` touches the one-row valid split only at the smoke boundary;
  this is a runtime sanity check, not a model-quality claim.

## Task-Owned Output Layout If Released

Use a new run root each time. Never reuse an existing path.

```bash
TASK280_RUN_ID=qwen3_4b_v11_sft_smoke_steps3_lr1e-6_$(date -u +%Y%m%dT%H%M%SZ)
TASK280_ROOT=/work-agents/intern_nemotron_worker_1/outputs/task280_qwen_aime_v11_sft_smoke_plan_hold_s1/${TASK280_RUN_ID}
TASK280_PACKED_ROOT=${TASK280_ROOT}/input/packed_qwen
TASK280_PACKED_SPLITS=${TASK280_PACKED_ROOT}/splits
TASK280_CKPT_DIR=${TASK280_ROOT}/checkpoints/qwen3_4b_v11_sft_smoke_steps3_lr1e-6
TASK280_LOG_DIR=${TASK280_ROOT}/logs
TASK280_MANIFEST=${TASK280_ROOT}/run_manifest.json
```

Expected artifacts if execution is released:

| Artifact | Path |
|---|---|
| Gate precheck log | `${TASK280_LOG_DIR}/gate_precheck.log` |
| task276 source hash log | `${TASK280_LOG_DIR}/task276_hashes.log` |
| Qwen contract log | `${TASK280_LOG_DIR}/qwen_contract_check.log` |
| Torchrun smoke log | `${TASK280_LOG_DIR}/torchrun_sft_smoke.log` |
| Staged packed data | `${TASK280_PACKED_ROOT}` |
| Bridge `.npy` cache | `${TASK280_PACKED_SPLITS}/train_4096_train.npy` and `${TASK280_PACKED_SPLITS}/valid_4096_valid.npy` |
| Bridge packed metadata cache | `${TASK280_PACKED_SPLITS}/packed_4096_metadata.json` |
| Checkpoint dir | `${TASK280_CKPT_DIR}` |
| Expected final checkpoint | `${TASK280_CKPT_DIR}/iter_0000003/` plus `${TASK280_CKPT_DIR}/latest_checkpointed_iteration.txt` |
| Run manifest | `${TASK280_MANIFEST}` |

The staged packed root is required because `stage1_sft/train.py` lazily writes
Bridge `.npy` files next to the packed split directory. Running directly against
worker_2 task276 splits would mutate a prior task artifact tree.

## Fail-Closed Release Script

This script is a candidate for a future execution task. It was not run in
task280.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Required release metadata.
: "${TASK278_STATUS:?set to APPROVED only after accepted task278 evidence}"
: "${TASK279_STATUS:?set to APPROVED only after accepted task279 review}"
: "${LEAD_RELEASE_TASK:?set to the explicit lead release task id}"
: "${TASK278_ACCEPTED_HEAD:?set to accepted task278 head}"
: "${TASK279_REVIEW_ID:?set to accepted task279 review/mailbox/pr id}"
: "${TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT:?set to accepted import/checkpoint root}"

test "${TASK278_STATUS}" = "APPROVED"
test "${TASK279_STATUS}" = "APPROVED"
test -n "${LEAD_RELEASE_TASK}"
test -n "${TASK278_ACCEPTED_HEAD}"
test -n "${TASK279_REVIEW_ID}"

SRC_PACKED_ROOT=/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen
SRC_PACKED_SPLITS=${SRC_PACKED_ROOT}/splits
QWEN_BASE=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507

TASK280_RUN_ID=qwen3_4b_v11_sft_smoke_steps3_lr1e-6_$(date -u +%Y%m%dT%H%M%SZ)
TASK280_ROOT=/work-agents/intern_nemotron_worker_1/outputs/task280_qwen_aime_v11_sft_smoke_plan_hold_s1/${TASK280_RUN_ID}
TASK280_PACKED_ROOT=${TASK280_ROOT}/input/packed_qwen
TASK280_PACKED_SPLITS=${TASK280_PACKED_ROOT}/splits
TASK280_CKPT_DIR=${TASK280_ROOT}/checkpoints/qwen3_4b_v11_sft_smoke_steps3_lr1e-6
TASK280_LOG_DIR=${TASK280_ROOT}/logs

case "${TASK280_ROOT}" in
  /work-agents/intern_nemotron_worker_1/outputs/task280_qwen_aime_v11_sft_smoke_plan_hold_s1/*) ;;
  *) echo "bad task-owned output root: ${TASK280_ROOT}" >&2; exit 10 ;;
esac
test ! -e "${TASK280_ROOT}"
mkdir -p "${TASK280_LOG_DIR}"

case "${TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT}" in
  *task255*) echo "task255 checkpoint/export reuse is forbidden" >&2; exit 11 ;;
esac
test -d "${TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT}"
test -f "${TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT}/latest_checkpointed_iteration.txt"
test -d "${QWEN_BASE}"
test -d "${SRC_PACKED_SPLITS}/train"
test -d "${SRC_PACKED_SPLITS}/valid"

sha256sum \
  "${SRC_PACKED_ROOT}/splits/manifest.json" \
  "${SRC_PACKED_ROOT}/splits/metadata.json" \
  "${SRC_PACKED_ROOT}/blend.json" \
  /work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence/packed_qwen_evidence_manifest.json \
  /work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence/packed_qwen_shard_checksums.sha256 \
  | tee "${TASK280_LOG_DIR}/task276_hashes.log"

grep -q '65501e0eff31cce77ff2d1e36dd915f66fb6b2fd145e0f59701d251e5b7d02c5' "${TASK280_LOG_DIR}/task276_hashes.log"
grep -q 'e4ac2157760dd50e50798a9095bf3ea1fb6834e5f405cac2f877560f42dbafd9' "${TASK280_LOG_DIR}/task276_hashes.log"
grep -q '6e64fdaf30582d5d0f6ed78f93759b86148ef21263e2a5d931dad62575234eef' "${TASK280_LOG_DIR}/task276_hashes.log"
grep -q '74f3c58283eef46a3b8f63699d730baa90337b9a7177146822170c22ec29e9ee' "${TASK280_LOG_DIR}/task276_hashes.log"
grep -q 'bb6107163f366334468b8db9b8e6ca74f8ddbd612f8b90d3e500e0efa3ba0312' "${TASK280_LOG_DIR}/task276_hashes.log"

# Stage a task-owned packed root so Bridge lazy .npy conversion cannot write
# into the task276 artifact tree. Do not use --delete.
mkdir -p "${TASK280_ROOT}/input"
rsync -a "${SRC_PACKED_ROOT}/" "${TASK280_PACKED_ROOT}/"

export TASK280_PACKED_ROOT
export TASK280_PACKED_SPLITS
export QWEN_BASE
export TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT

PYTHONPATH=src python3 - <<'PY' 2>&1 | tee "${TASK280_LOG_DIR}/gate_precheck.log"
import json
import os
from pathlib import Path

root = Path(os.environ["TASK280_PACKED_ROOT"])
evidence = json.loads(Path(
    "/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/evidence/packed_qwen_evidence_manifest.json"
).read_text())
assert evidence["disposition"] == "PACKED_QWEN_READY_FOR_REVIEW"
assert evidence["no_aime2025_train_leakage_decision"]["status"] == "PASS"
assert evidence["no_aime2025_train_leakage_decision"]["aime_pattern_mentions_total"] == 0
assert evidence["no_aime2025_train_leakage_decision"]["label_like_top_level_key_total"] == 0
assert evidence["no_aime2025_train_leakage_decision"]["task246_user_prompt_hash_overlap_total"] == 0
assert evidence["no_aime2025_train_leakage_decision"]["task246_system_user_prompt_hash_overlap_total"] == 0
for value in [
    str(root),
    os.environ["TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT"],
    os.environ["QWEN_BASE"],
]:
    assert "task255" not in value.lower(), value
print("TASK280_GATE_PRECHECK=PASS")
PY

PYTHONPATH=src python3 - <<'PY' 2>&1 | tee "${TASK280_LOG_DIR}/qwen_contract_check.log"
from pathlib import Path
from nemotron.recipes.super3.stage1_sft.qwen_chat_contract import (
    validate_qwen_packed_sft_chat_contract,
    validate_qwen_training_pipeline_contract,
)
splits = Path(__import__("os").environ["TASK280_PACKED_SPLITS"])
qwen = __import__("os").environ["QWEN_BASE"]
entry = "src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py"
validate_qwen_packed_sft_chat_contract(splits, tokenizer_model=qwen)
validate_qwen_training_pipeline_contract(
    splits,
    tokenizer_model=qwen,
    training_profile="qwen",
    model_ref=qwen,
    train_entrypoint=entry,
    recipe_target=None,
)
print("TASK280_QWEN_CONTRACT=PASS")
PY

export PYTHONPATH="${PWD}/src${PYTHONPATH:+:${PYTHONPATH}}"
export WANDB_MODE=offline
export WANDB_DISABLED=true
export TOKENIZERS_PARALLELISM=false
export SUPER3_M1_AGENTIC_PACKED_DIR="${TASK280_PACKED_SPLITS}"
export SUPER3_M1_QWEN_HF_MODEL="${QWEN_BASE}"
export SUPER3_M1_TOKENIZER_MODEL="${QWEN_BASE}"
export SUPER3_M1_PRETRAINED_CHECKPOINT="${TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT}"
export SUPER3_M1_SFT_SAVE="${TASK280_CKPT_DIR}"
export SUPER3_M1_TRAINING_PROFILE=qwen

python -m torch.distributed.run \
  --nproc_per_node=2 \
  src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py \
  --config src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml \
  train.train_iters=3 \
  train.eval_interval=3 \
  train.global_batch_size=2 \
  train.micro_batch_size=1 \
  model.seq_length=4096 \
  dataset.seq_length=4096 \
  dataset.packed_sequence_specs.packed_sequence_size=4096 \
  checkpoint.save_interval=3 \
  logger.log_interval=1 \
  training_contract.model_profile=qwen \
  training_contract.model_ref="${QWEN_BASE}" \
  training_contract.train_entrypoint=src/nemotron/recipes/super3/stage1_sft/qwen_local_train.py \
  ++optimizer.lr=1e-6 \
  ++optimizer.min_lr=1e-6 \
  scheduler.lr_warmup_iters=0 \
  ++scheduler.lr_decay_iters=3 \
  convert_to_hf.enabled=false \
  2>&1 | tee "${TASK280_LOG_DIR}/torchrun_sft_smoke.log"
```

## Stop Criteria

Stop before launch and report blocker if any item is true:

- task278/task279 are not approved at exact evidence identifiers.
- Lead has not explicitly released nonzero-LR Qwen3-4B smoke execution.
- `TASK278_ACCEPTED_PRETRAINED_CHECKPOINT_ROOT` is unset, missing, lacks
  `latest_checkpointed_iteration.txt`, or references task255.
- The task276 split manifest, metadata, blend, evidence manifest, or shard
  checksum list hash differs from the accepted hashes above.
- The staged packed data fails Qwen packed-data or Qwen training pipeline
  contract checks.
- The gate precheck finds AIME2025 prompt/label leakage or task255 path use.
- The proposed output root already exists.

Stop during or after launch and report blocker if any item is true:

- Torchrun exits nonzero.
- Log contains `random-init smoke training loop`.
- Log contains NaN/Inf loss or gradient evidence.
- Log lacks Qwen contract validation.
- Log lacks accepted checkpoint/load/import evidence from task278 context.
- Training proceeds beyond 3 steps.
- `${TASK280_CKPT_DIR}/latest_checkpointed_iteration.txt` or
  `${TASK280_CKPT_DIR}/iter_0000003/` is missing after a nominally successful
  run.
- Any export, endpoint, live canary, AIME/task243 eval, promotion, task255
  reuse, AIME2025 train-data use, shared deletion, or 30B/8-GPU action is
  requested as part of the same execution.

## Residual Risks

- task278/task279 are not yet accepted, so the pretrained/import checkpoint root
  is unresolved by design.
- task276 valid split has one packed hard-math row and test has zero rows. This
  is acceptable only for bounded training-stack smoke, not a quality or eval
  claim.
- The training entry writes Bridge `.npy` cache files near the active packed
  split directory; staging to task-owned task280 output is mandatory.
- A 2-GPU shape is required for the current Qwen3-4B local entrypoint because
  it sets tensor model parallel size to 2. This remains within the 4B bounded
  smoke scope and is not 30B/8-GPU scale.

## Commands Actually Run In task280

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git switch -c intern_nemotron_worker_1/task280_qwen_aime_v11_sft_smoke_plan_hold_s1 origin/main
git checkout origin/intern_nemotron_lead/session1-recovery-task-docs -- workspace/tasks/task280_qwen_aime_v11_sft_smoke_plan_hold_s1
gh pr view 344 --repo songCNMS/Nemotron --json number,url,state,baseRefName,headRefOid,mergeStateStatus,mergedAt,mergeCommit,isDraft
gh pr list --repo songCNMS/Nemotron --state all --search "task278 OR task279" --json number,title,state,url,headRefName,headRefOid,mergedAt,mergeCommit --limit 20
sha256sum <task276 manifest/metadata/blend/evidence/checksum files>
python3 - <<'PY'
# Read-only manifest key inspection for task276 evidence.
PY
sed/rg reads of task276/task278/task279/stage1_sft/qwen_local_train.py/train.py/qwen_chat_contract.py/plan_m1_agentic_sft_training.py
git diff --check
```

No training, nonzero-LR smoke, live canary, AIME/task243 eval, export,
endpoint, promotion, task255 reuse, AIME2025 train data, shared deletion, merge,
main push, or 30B/8-GPU command was run.
