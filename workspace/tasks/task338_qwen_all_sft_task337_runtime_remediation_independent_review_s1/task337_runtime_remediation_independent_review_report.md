# task338 independent review of task337/#400

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=APPROVE_TASK337_RUNTIME_REMEDIATION_EVIDENCE,SESSION=88 -->

Generated: 2026-06-04T10:46:31Z

## Decision

`APPROVE_TASK337_RUNTIME_REMEDIATION_EVIDENCE` for #400 exact head
`fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`.

The reviewed evidence supports accepting #400/task337 as task-owned,
no-training runtime import remediation evidence only. The prior missing
`megatron.energon` blocker is reproduced in baseline artifacts and the final
task-owned `PYTHONPATH` route proves both `megatron.energon` and
`megatron.bridge.recipes.qwen.qwen3_moe` imports pass.

This does not release task310, training/optimizer steps, eval, export,
endpoint, promotion, task255 reuse, AIME2025 train rows, shared deletion,
main push, merge, self-merge, or any 30B launch. A separate lead-assigned
task335-equivalent no-training launch preflight rerun is still required before
any training task.

## Target Reviewed

- PR: #400 `https://github.com/songCNMS/Nemotron/pull/400`
- Exact head reviewed: `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`
- PR state observed: `OPEN`, non-draft, base `main`, `CLEAN`/`MERGEABLE`
- Base observed: `origin/main` `373d162d63a66f2dac6b94c43917be9c249cd83f`
- Local artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z`
- Runtime target recorded by artifacts:
  `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`
- Report reviewed:
  `workspace/tasks/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/qwen3_moe_runtime_remediation_report.md`
- Report sha256 verified:
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`

## Commands And Checks

Commands were run from
`/work-agents/intern_nemotron_worker_4/Nemotron_task338` unless noted.

```bash
git fetch origin main +pull/400/head:refs/remotes/origin/pr/400
gh pr view 400 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
git rev-parse origin/pr/400 origin/main
git diff --name-status origin/main...origin/pr/400
git diff --check origin/main...origin/pr/400
git diff --stat origin/main...origin/pr/400
git log --oneline --decorate --max-count=6 origin/main..origin/pr/400
git show origin/pr/400:workspace/tasks/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/qwen3_moe_runtime_remediation_report.md | sha256sum
```

Artifact-root commands:

```bash
cd /work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z
find . -maxdepth 3 -type f | sort
sha256sum -c manifests/artifact_checksums.sha256
jq . manifests/final_summary.json
jq . manifests/baseline_import_inventory.json
jq . manifests/final_after_filetype_import_inventory.json
jq . manifests/qwen3_moe_symbol_probe.json
tail -n 80 logs/final_remediated_import_inventory_after_filetype.log
tail -n 80 logs/qwen3_moe_symbol_probe.log
tail -n 80 logs/baseline_import_inventory.log
sed -n '1,220p' manifests/remediation_wheel_checksums.txt
sed -n '1,260p' manifests/runtime_site_inventory.txt
wc -l manifests/runtime_site_inventory.txt manifests/remediation_wheel_checksums.txt manifests/artifact_checksums.sha256
grep -vc '^/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site' manifests/runtime_site_inventory.txt
cat source_head.txt
```

Results:

- #400 exact head is
  `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`.
- #400 observed state is `OPEN`, non-draft, base `main`, `CLEAN`/`MERGEABLE`.
- PR diff scope is worker_2 status plus task337 README/history/task_knowledge
  and task337 report only; no product/source code changes.
- `git diff --check origin/main...origin/pr/400`: clean.
- Report sha256 matches the required
  `441bd4b3c46d923f880fe3ce55298bc810e03e730819b16405b8b3b5a995cd49`.
- `sha256sum -c manifests/artifact_checksums.sha256`: `PASS`, 48 entries.
- Runtime inventory has 224 entries and all are under the task-owned
  `runtime_site` path.
- Wheel checksum manifest has 20 lines covering 10 wheels and sha256 entries.

## Artifact And Checksum Verdict

The task337 artifact root is present and checksum-backed. Important artifact
hashes validated through `artifact_checksums.sha256` include:

- `manifests/final_summary.json`:
  `5b7c07da370e70e9947a61bdc70b36a7529a5eda2da2c4c81c67fceb28adab8f`
- `manifests/artifact_checksums.sha256`:
  `11c59ced7edf69fedcdcaca17a542f36520a720e7eb7bd4b7ecf5b9b46f871bc`
- `manifests/final_after_filetype_import_inventory.json`:
  `239456b25d117cdcfcfd5118c6fc383a359ec6c4d9c91282aaba0be977195dac`
- `manifests/qwen3_moe_symbol_probe.json`:
  `9b678dc8d89b2b8d30fdd69c7b4155a741d586dfdc4dfa0694f832d13a167a02`
- `manifests/remediation_wheel_checksums.txt`:
  `e08143a7571f260b440133a340a6a3908aa269668781f4e978fe74a18b342336`
- `manifests/runtime_site_inventory.txt`:
  `ac6fd4555442fd6cc5fc4dd6e4c551d303fb97fd78b952d83deb6db5ce944c92`
- `logs/final_remediated_import_inventory_after_filetype.log`:
  `5f49031502b95c105f34ea2fa56be9016bfe1ebf23479ce2d22adeb33277b375`
- `logs/qwen3_moe_symbol_probe.log`:
  `cb00b8e752460548763790f284449f3e7278520ee783eecf12e77e4b12ba07c4`

I did not modify task337 artifacts or the worker_2 branch.

## Runtime Remediation Verdict

The evidence supports the claimed `PASS_RUNTIME_REMEDIATED` disposition.

Baseline reproduction:

- `manifests/baseline_import_inventory.json` disposition:
  `BLOCK_MISSING_MEGATRON_ENERGON`.
- `logs/baseline_import_inventory.log` marker:
  `TASK337_IMPORT_PROBE=BLOCK_MISSING_MEGATRON_ENERGON`.
- Baseline `megatron-energon` distribution status: `MISSING`.
- Baseline `megatron.energon` import fails with
  `ModuleNotFoundError("No module named 'megatron.energon'")`.
- Baseline `megatron.bridge.recipes.qwen.qwen3_moe` fails through the same
  missing `megatron.energon` blocker.

Final import proof:

- `manifests/final_summary.json` disposition:
  `PASS_RUNTIME_REMEDIATED`.
- `final_import_disposition`: `PASS_QWEN3_MOE_IMPORT`.
- `symbol_probe_disposition`: `PASS_QWEN3_MOE_SYMBOL_IMPORT`.
- `logs/final_remediated_import_inventory_after_filetype.log` marker:
  `TASK337_IMPORT_PROBE=PASS_QWEN3_MOE_IMPORT`.
- `logs/qwen3_moe_symbol_probe.log` marker:
  `TASK337_SYMBOL_PROBE=PASS_QWEN3_MOE_SYMBOL_IMPORT`.
- Final `megatron.energon` import status: `PASS`, version `7.3.2`, from
  task-owned `runtime_site`.
- Final `megatron.bridge.recipes.qwen.qwen3_moe` import status: `PASS`, from
  the existing `/usr/local/lib/python3.12/dist-packages/megatron/bridge/...`
  package while `runtime_site` is prepended on `PYTHONPATH`.
- Symbol probe includes `qwen3_30b_a3b_pretrain_config` and
  `qwen3_30b_a3b_finetune_config`, with `model_constructed=false` and
  `weights_loaded=false`.

Installed runtime packages are recorded as task-owned wheels and task-owned
runtime target entries for:

- `megatron-energon` 7.3.2
- `multi-storage-client` 0.49.0
- `xattr` 1.3.0
- `wcmatch` 10.1
- `bracex` 2.6
- `braceexpand` 0.1.7
- `rapidyaml` 0.13.0.post2
- `deprecation` 2.1.0
- `webdataset` 1.0.2
- `filetype` 1.2.0

The final `PYTHONPATH` is:

```text
/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site:/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron/src
```

## Source Head And Drift

- Artifact `source_head.txt`:
  `4db10e0783823c8f6087748718d40e729879554d`.
- `final_summary.source_head` and `remote_synced_head` both match
  `4db10e0783823c8f6087748718d40e729879554d`.
- #400 head is
  `fb6ba0e75c0d3dc4ec3ad47e3d6f27bbecf3e091`.
- Drift `4db10e078..fb6ba0e7` is worker_2 status/task337 docs/report
  publication only, and `git diff --check` over that range is clean.

## Residual Risks

- This is import/symbol runtime remediation evidence only; no model was
  constructed and no weights were loaded.
- No task335-equivalent no-training launch preflight has been rerun with this
  runtime target. That remains the required next gate before any training.
- The final proof still imports the Qwen3 MoE Bridge recipe from the existing
  system Megatron Bridge package; the task-owned runtime target supplies the
  missing dependency chain by `PYTHONPATH` precedence.
- `nvidia-resiliency-ext` remains missing in the inventory. It did not block the
  required qwen3_moe import proof, but later launch/config preflight may still
  need to classify or remediate it.
- The diagnostic import name `multi_storage_client` still fails in the final
  inventory, while the installed distribution is `multi-storage-client` and the
  runtime-site package path is `multistorageclient`. This is non-blocking for
  the reviewed qwen3_moe import proof but should be noted if future gates rely
  on direct import of that module name.
- The task-owned runtime target is under `/root` for this run. A later task must
  either reuse it exactly as lead-approved evidence or recreate equivalent
  task-owned runtime remediation with fresh checksums.

## Boundary Confirmation

Confirmed from the report/manifests and my own actions:

- No task337 artifact or worker_2 branch mutation by worker_4.
- No package installation or runtime mutation by worker_4.
- No model construction, weight load, training, or optimizer steps.
- No benchmark eval, AIME eval, or task243 eval.
- No export, endpoint, promotion, task310 release, or 30B launch release.
- No task255 reuse and no AIME2025 train rows.
- No shared deletion/mutation and no mutation under
  `/mnt/cephfs/data/processing/lei.song`.
- No main push, merge, or self-merge.
