# task275 Session 40 Runbook Update Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

## Decision

Recommendation: `PASS` for runbook/provenance update, with global V11
execution still `NO-GO/HOLD`.

Coordinator Session 40 clears the previous task270
`NEMTRON_RUNTIME_ROUTE_BLOCKED` condition for positive no-training
Qwen3-4B Bridge import plus fail-closed preflight proof. It does not clear
training, nonzero-LR smoke, live AIME/task243 eval, export, endpoint,
promotion, AIME2025 train data, task255 reuse, 30B/8-GPU, or shared-deletion
boundaries.

## Provenance

- Worker branch:
  `intern_nemotron_worker_5/task275_qwen_aime_v11_session40_runbook_update_s1`
- Branch base:
  `origin/main` at `958c283813960d90749d51c8880354b89caa7ff8`
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `b7e58017ce2324ef24bf130e7ad84082b5271d1f`
- Coordinator branch evidence:
  `/work-agents/intern_nemotron_coordinator/Nemotron` on
  `intern_nemotron_coordinator/session1-resume-interrupted-work` at
  `8c8364101d6adb07f9e67c17fece3e2b2bb280ca`
- Coordinator PR:
  #312, open/CLEAN at `8c8364101d6adb07f9e67c17fece3e2b2bb280ca`
- Coordinator Session 40 timestamp:
  `20260602T015146Z`

## Evidence Paths

| Surface | Path / value | SHA256 / marker | Status |
|---|---|---|---|
| local evidence root | `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z` | n/a | present |
| remote run root | `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z` | recorded in `remote_run.txt` | present |
| remote synced repo | `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/Nemotron` | fresh `origin/main` sync per coordinator history | recorded |
| Qwen3-4B base | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` | task268/task270 base path | used for import |
| symbol preflight log | `logs/symbol_preflight.log` | `bfa15c5b26849ef2c802c03b0303d57ada11922c4872068bd17de2c7d0081534` | contains `TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS` |
| Bridge import log | `logs/bridge_import_probe.log` | `170b51d0c846c374a82badf780d478d64a946d3131cdc7032808d7c53db21756` | contains `IMPORT_DONE` and `BRIDGE_IMPORT_RC=0` |
| fail-closed preflight log | `logs/fail_closed_preflight.log` | `60db59059560304dc18a6e28498f6be1a08cbc24c26abd6e82241f6e1729c440` | contains `TASK270_FAIL_CLOSED_PREFLIGHT=PASS` |
| remote checkpoint manifest | `remote_checkpoint_manifest.txt` | `51b4ab937a5be23f1391cddd5c5c1425a3f8860e84fe81827fc5ebdee2afb522` | records checkpoint size/file list and NeMo package |
| imported checkpoint root | `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/qwen3_4b_bridge_import_iter0` | size `7.5G` in manifest | iteration 0 import artifact |
| evidence sha list | `session40_evidence.sha256` | `fdcc40d9d1a68a9eb5b08ab55679025a50c7f95e001e8661cb1237ca268aecf7` | `sha256sum -c` PASS |
| artifact inventory | `artifact_inventory.sha256` | current file sha `9526d498c3daa55cee998c38dbde0f7e6ad96b6d2adb133d75bb2141c2e14609` | non-self entries PASS; self-entry is stale |

## Pass Markers

Symbol preflight:

```text
megatron.bridge=/usr/local/lib/python3.12/dist-packages/megatron/bridge/__init__.py
nemo=/root/.local/lib/python3.12/site-packages/nemo/__init__.py
TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS
```

Bridge import:

```text
IMPORT_HF=/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507
IMPORT_OUT=/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/qwen3_4b_bridge_import_iter0
successfully saved checkpoint from iteration       0
IMPORT_DONE
BRIDGE_IMPORT_RC=0
```

Fail-closed preflight:

```text
TASK270_FAIL_CLOSED_PREFLIGHT=PASS
```

Remote checkpoint manifest:

```text
CHECKPOINT_DU=
7.5G    /root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z/qwen3_4b_bridge_import_iter0
Name: nemo-toolkit
Version: 2.7.3
```

## Verification Commands

Commands run by worker_5 for this update:

```bash
sha256sum -c \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/session40_evidence.sha256

grep -v '/artifact_inventory\\.sha256$' \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/artifact_inventory.sha256 \
  | sha256sum -c -

sha256sum \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/artifact_inventory.sha256 \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/session40_evidence.sha256 \
  /work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z/remote_checkpoint_manifest.txt
```

Results:

- `session40_evidence.sha256`: PASS for bridge import log, fail-closed log,
  symbol preflight log, and remote checkpoint manifest.
- `artifact_inventory.sha256` excluding its own self-entry: PASS for bridge
  import log, fail-closed log, symbol preflight log, `remote_run.txt`, and
  `timestamp.txt`.
- Full `artifact_inventory.sha256`: REQUEST-CHANGES detail, because it includes
  a stale self-entry for `artifact_inventory.sha256`. The core runtime proof
  files still validate via `session40_evidence.sha256` and non-self inventory
  checks.

## Cleared Blocker

Cleared:

- task270's missing-`nemo` runtime-route blocker for a no-training
  Qwen3-4B Bridge import plus fail-closed preflight route.

Not cleared:

- nonzero-LR SFT smoke;
- live canary execution on a future V11 candidate;
- live AIME/task243 same-harness comparison;
- candidate FT checkpoint/export/reviewer-readable artifacts;
- task265 independent review of exact candidate artifacts;
- promotion/non-regression decision;
- 30B/8-GPU permission.

## Updated Stage Gate Matrix

| Stage | Current evidence after Session 40 | Gate |
|---|---|---|
| 1. V11 data/packing ready | task262 #336 merged static data/packing repair and decontamination evidence | STATIC MERGED; live packing/training HOLD |
| 2. Base-load/import proof ready | Session 40 coordinator proof shows `nemo-toolkit==2.7.3`, `TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS`, `IMPORT_DONE`, `BRIDGE_IMPORT_RC=0`, `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`, and a 7.5G imported Qwen3-4B checkpoint root | RUNTIME PROOF PRESENT for import/preflight only; nonzero-LR training evidence still missing |
| 3. Non-AIME canary ready | task264 #335 merged static canary/retention schema | STATIC MERGED; live canary pass missing |
| 4. Bounded Qwen3-4B pilot allowed | Session 40 does not provide lead clearance, nonzero-LR smoke, or live candidate artifacts | NO-GO/HOLD |
| 5. Same-harness AIME comparison allowed | no V11 FT candidate, canary pass, retained completions, or task265 review of candidate artifacts | NO-GO/HOLD |
| 6. Promotion or 30B/8-GPU | no same-harness FT score, no promotion gate, no 30B permission | NO-GO/HOLD |

## Runbook Updates Made

- Updated `workspace/tasks/task266_qwen_aime_v11_runbook_repro_gate_s1/v11_runbook_repro_gate_report.md`
  to record Session 40 as positive runtime import/preflight proof while keeping
  downstream stages held.
- Updated task275 README/history/task_knowledge/status docs for acceptance and
  report closeout.

## Residual Risks

- The proof is coordinator-produced and lives in coordinator output paths; lead
  still controls whether to require a worker-owned rerun or formal review before
  any live candidate work.
- `artifact_inventory.sha256` has a stale self-entry. Use
  `session40_evidence.sha256` and the non-self inventory check for the current
  proof unless the coordinator regenerates the inventory without self-reference.
- `nemo-toolkit==2.7.3` was installed in NemTron user site with
  `--break-system-packages --no-deps`; future runs should confirm the same
  Python/user-site state before relying on it.
- Session 40 imported a checkpoint at iteration 0; it did not train, validate
  optimizer/LR schedule, run canary prompts, evaluate AIME, export, or serve an
  endpoint.
- Global Qwen AIME remains `NO-GO/HOLD`.

## Boundary Confirmation

Worker_5 performed only read-only artifact review and documentation updates in
this task. No training, nonzero-LR smoke, live AIME/task243 eval, export,
endpoint, promotion, task255 reuse, AIME2025 train data, 30B/8-GPU, merge, main
push, shared deletion, or shared overwrite was performed.
