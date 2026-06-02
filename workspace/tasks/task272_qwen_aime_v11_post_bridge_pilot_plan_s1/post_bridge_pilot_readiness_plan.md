# task272 Post-Bridge Qwen3-4B V11 Pilot Readiness Plan

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

Generated: 2026-06-02T02:10:39Z

Disposition: `PLAN_READY_HOLD_TASK271_LEAD_GATE`.

This is a no-training readiness plan and dependency classification only. It does
not authorize SFT training, nonzero-LR smoke execution, live AIME/task243 eval,
export, endpoint launch, promotion, task255 reuse, AIME2025 train data,
30B/8-GPU, merge/main push, or shared deletion.

## Inputs Reviewed

Primary task docs and artifacts:

- task272 lead docs imported from
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `b7e58017ce2324ef24bf130e7ad84082b5271d1f`.
- Session 40 coordinator evidence root:
  `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/`.
- Session 40 remote run path from `remote_run.txt`:
  `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z`.
- Qwen3-4B base:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- task262 output root:
  `/work-agents/intern_nemotron_worker_1/outputs/task262_qwen_aime_v11_data_split_sidecar_s1/`.
- task266 runbook:
  `workspace/tasks/task266_qwen_aime_v11_runbook_repro_gate_s1/v11_runbook_repro_gate_report.md`.
- task270 runtime route audit:
  `workspace/tasks/task270_qwen_aime_v11_nemtron_runtime_route_audit_s1/nemtron_runtime_route_audit_report.md`.
- task268 blocker-evidence report:
  `workspace/tasks/task268_qwen_aime_v11_nemtron_bridge_runtime_probe_s1/runtime_probe_report.md`.

Task271 remains an external gate input. The Session 40 proof can be used for
planning, but must not be treated as accepted Bridge proof until task271 and
lead explicitly accept it.

## Read-Only Evidence

Session 40 evidence markers observed from local files:

- `logs/symbol_preflight.log`: `TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS`.
- `logs/bridge_import_probe.log`: `IMPORT_DONE`.
- `logs/bridge_import_probe.log`: `BRIDGE_IMPORT_RC=0`.
- `logs/fail_closed_preflight.log`: `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`.

Session 40 checkpoint/import output from `remote_checkpoint_manifest.txt`:

- Output root:
  `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/qwen3_4b_bridge_import_iter0`.
- Size: `7.5G`.
- Key files include `latest_checkpointed_iteration.txt`,
  `iter_0000000/common.pt`, `iter_0000000/run_config.yaml`,
  `iter_0000000/__0_0.distcp`, `iter_0000000/__0_1.distcp`, and tokenizer
  files under `iter_0000000/tokenizer/`.

Session 40 evidence hashes:

| Artifact | sha256 |
| --- | --- |
| `logs/bridge_import_probe.log` | `170b51d0c846c374a82badf780d478d64a946d3131cdc7032808d7c53db21756` |
| `logs/fail_closed_preflight.log` | `60db59059560304dc18a6e28498f6be1a08cbc24c26abd6e82241f6e1729c440` |
| `logs/symbol_preflight.log` | `bfa15c5b26849ef2c802c03b0303d57ada11922c4872068bd17de2c7d0081534` |
| `remote_checkpoint_manifest.txt` | `51b4ab937a5be23f1391cddd5c5c1425a3f8860e84fe81827fc5ebdee2afb522` |
| `session40_evidence.sha256` | `fdcc40d9d1a68a9eb5b08ab55679025a50c7f95e001e8661cb1237ca268aecf7` |

Current worker_2 could not replay SSH probes against the Session 40 host name
`lg-cmc-b7r201-f08u26-h200-000126`: SSH returned rc `255`,
`Could not resolve hostname`. Therefore this task records the local artifacts as
read-only evidence and keeps task271/lead acceptance as a hard gate.

## Dependency Classification

| Dependency | State | Classification |
| --- | --- | --- |
| Task271 independent review | Pending external gate | HOLD. Do not treat Session 40 proof as accepted until task271 and lead approve it. |
| Bridge import proof | Promising read-only evidence | Observed `IMPORT_DONE` and `BRIDGE_IMPORT_RC=0`; enough for planning, not enough for worker_2 to clear execution. |
| Fail-closed preflight | Promising read-only evidence | Observed `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`; still task271/lead-gated. |
| Qwen3-4B base path | Present by scope | Use only `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`. |
| V11 packed Qwen train/valid root | Not ready | task262 provides plan/audit evidence, but no accepted fresh V11 packed root exists. Older task253 audit exposes 8 train shards / 79 rows vs 15 intended shards / 113 rows. |
| Planner scripts | Help works locally | `plan_qwen_scaleup_run.py --help` and `plan_m1_agentic_sft_training.py --help` ran with `PYTHONPATH=src`; no launch was executed. |
| `hydra` | Not current planner/Bridge blocker | Local worker has `hydra` and `omegaconf`; local worker lacks `megatron`, `megatron.bridge`, and `nemo`. The observed Session 40 Bridge import succeeded without `hydra` being an exposed blocker. Any future training CLI path that uses Hydra-style overrides still needs an authorized no-training config/import preflight. |
| Nonzero-LR smoke/training | Not authorized | Requires task271+lead proof acceptance, fresh accepted V11 packed root, explicit lead clearance, and a fail-closed config/import preflight. |
| Live AIME/task243 eval | Not authorized | Requires a future candidate artifact and separate gate. |
| Promotion / 30B / 8-GPU | Not authorized | Global Qwen AIME gate remains `NO-GO/HOLD`. |

## Exact Next Route

1. Wait for task271 and lead to accept or reject the Session 40 Bridge evidence.
   If rejected, stop and repair the exact Bridge/runtime issue under a new
   task-owned probe.
2. Produce a fresh V11 packed Qwen train/valid root from task262-approved inputs
   under a future authorized no-training data/packing task. Required evidence:
   root path, split manifest, row counts, shard counts, checksums, intended-vs-
   exposed parity, tokenizer/chat-template packing proof, and no AIME2025
   prompt/label train rows.
3. Run a no-training config/import preflight on the task-owned NemTron/NeMo
   runtime after code is synced to a task-owned `/root/<task>/Nemotron` path.
   Required proof: imports for exact launch module, Bridge checkpoint/base path
   readability, packed split manifest readability, fail-closed checks for
   random init, NaN/Inf, zero LR, missing packed shards, and missing decontam
   evidence.
4. Only after explicit lead clearance, generate or run the bounded nonzero-LR
   smoke plan. Stop for review before any live eval, export, promotion, or
   scale-up.

## Future Command Skeletons

These are planning templates only. They were not executed in task272.

Verify Session 40/task271 gate:

```bash
sha256sum \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/logs/bridge_import_probe.log \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/logs/fail_closed_preflight.log \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/logs/symbol_preflight.log \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/remote_checkpoint_manifest.txt
rg -n 'IMPORT_DONE|BRIDGE_IMPORT_RC=0|TASK270_FAIL_CLOSED_PREFLIGHT=PASS|TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS' \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z
```

Generate a future planner bundle only after a fresh V11 packed root exists:

```bash
PYTHONPATH=src python3 src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py \
  --packed-sft-dir <accepted_v11_packed_qwen_root>/splits \
  --pretrained-checkpoint /root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/qwen3_4b_bridge_import_iter0 \
  --tokenizer-model /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
  --qwen-hf-model /mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507 \
  --output-dir <task_owned_planner_output> \
  --run-name qwen3_4b_v11_bounded_smoke_plan \
  --nodes 1 \
  --gpus-per-node 1 \
  --train-iters <small_positive_iter_count> \
  --global-batch-size 2 \
  --micro-batch-size 1 \
  --seq-length 4096 \
  --eval-interval <greater_than_train_iters> \
  --save-interval <small_positive_iter_count> \
  --optimizer-lr 5e-6 \
  --scheduler-min-lr 5e-7 \
  --lr-warmup-iters 0 \
  --lr-decay-iters <greater_than_train_iters>
```

The values above are placeholders for a later approved task. They must not be
used as implicit clearance to train.

## Commands Actually Run In Task272

Read-only or help-only commands:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git checkout -B intern_nemotron_worker_2/task272_qwen_aime_v11_post_bridge_pilot_plan_s1 origin/main
git checkout origin/intern_nemotron_lead/session1-recovery-task-docs -- workspace/tasks/task272_qwen_aime_v11_post_bridge_pilot_plan_s1
grep -R 'TASK270_RUNTIME_SYMBOL_PREFLIGHT\|BRIDGE_IMPORT_RC\|IMPORT_DONE\|TASK270_FAIL_CLOSED_PREFLIGHT' -n /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z
sha256sum /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/logs/bridge_import_probe.log /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/logs/fail_closed_preflight.log /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/logs/symbol_preflight.log /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/remote_checkpoint_manifest.txt /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/session40_evidence.sha256
python3 - <<'PY'
import importlib.util
for name in ['hydra','omegaconf','megatron','megatron.bridge','nemo','torch','transformers','safetensors']:
    try:
        spec=importlib.util.find_spec(name)
        origin = spec.origin if spec else 'MISSING'
    except ModuleNotFoundError as exc:
        origin = f'MISSING ({exc})'
    print(f'{name}: {origin}')
PY
PYTHONPATH=src python3 src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_qwen_scaleup_run.py --help
PYTHONPATH=src python3 src/nemotron/recipes/super3/milestones/m1_agentic_sft/plan_m1_agentic_sft_training.py --help
ssh -o BatchMode=yes -o ConnectTimeout=8 lg-cmc-b7r201-f08u26-h200-000126 '<read-only import probes>'
```

SSH replay returned rc `255` because the host name could not be resolved.

## Boundaries

Confirmed not performed:

- SFT training or nonzero-LR smoke;
- live AIME/task243 eval;
- export or endpoint launch;
- promotion or go/no-go claim;
- task255 artifact reuse;
- AIME2025 prompt/label train-data use;
- 30B/8-GPU planning or launch;
- merge, main push, or shared deletion.

Global Qwen AIME gate remains `NO-GO/HOLD`.
