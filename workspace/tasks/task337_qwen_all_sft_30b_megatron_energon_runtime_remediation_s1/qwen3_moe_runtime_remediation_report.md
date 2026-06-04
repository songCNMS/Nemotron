# task337 Qwen3 MoE runtime remediation report

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=PASS_RUNTIME_REMEDIATED,SESSION=2 -->

Generated: 2026-06-04T10:12:00Z

## Disposition

`PASS_RUNTIME_REMEDIATED`.

The accepted task335 blocker was reproduced on NemTron, then remediated in a
task-owned runtime target path only. With
`PYTHONPATH=/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site:/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron/src`,
both imports now pass:

- `megatron.energon`
- `megatron.bridge.recipes.qwen.qwen3_moe`

This is runtime import remediation only. It does not release task310, training,
optimizer steps, eval, export, endpoint, promotion, task255 reuse, AIME2025
train rows, shared-root mutation, main push, merge, or self-merge. A later
lead-assigned task must rerun task335-equivalent no-training launch preflight
with this runtime target before any training launch can be considered.

## Artifact Roots

| Artifact | Path |
|---|---|
| Local run root | `/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z` |
| Remote run root | `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z` |
| Remote synced repo | `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron` |
| Runtime target | `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site` |
| Wheel cache | `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/wheels` |
| Final summary | `/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/manifests/final_summary.json` |
| Final import inventory | `/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/manifests/final_after_filetype_import_inventory.json` |
| Symbol probe | `/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/manifests/qwen3_moe_symbol_probe.json` |
| Artifact checksums | `/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/manifests/artifact_checksums.sha256` |

Important hashes:

| File | sha256 |
|---|---|
| `manifests/final_summary.json` | `5b7c07da370e70e9947a61bdc70b36a7529a5eda2da2c4c81c67fceb28adab8f` |
| `manifests/artifact_checksums.sha256` | `11c59ced7edf69fedcdcaca17a542f36520a720e7eb7bd4b7ecf5b9b46f871bc` |
| `logs/artifact_checksums_check.log` | `22dccae43204f01976478192651f0dd8fe278d0f1bc99e7b9542b61211188221` |

Checksum validation:

```bash
cd /work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z
sha256sum -c manifests/artifact_checksums.sha256
```

Result: `PASS`.

## Sync And Environment

Branch head used for the remote sync:
`4db10e0783823c8f6087748718d40e729879554d`.

Base main:
`373d162d63a66f2dac6b94c43917be9c249cd83f`.

Remote host:
`lg-cmc-b7r201-f08u26-h200-000126`.

The first sync attempted `rsync`, but remote `rsync` was unavailable. The
successful sync used tar-over-ssh into the task-owned remote repo path. No
shared roots were mutated.

Remote execution environment:

```bash
PYTHONPATH=/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site:/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron/src
WANDB_DISABLED=true
WANDB_MODE=offline
TOKENIZERS_PARALLELISM=false
```

Model path checked by the probe:
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

## Baseline Reproduction

Baseline command used only the synced repo `src` on `PYTHONPATH`:

```bash
cd /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron
PYTHONPATH=/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron/src \
  WANDB_DISABLED=true WANDB_MODE=offline TOKENIZERS_PARALLELISM=false \
  python3 /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/import_inventory_probe.py \
  --label baseline_no_remediation \
  --repo /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron \
  --model /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
  --out /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/baseline_import_inventory.json
```

Result:

- `TASK337_IMPORT_PROBE=BLOCK_MISSING_MEGATRON_ENERGON`
- `megatron-energon`: distribution missing.
- `megatron.energon`: `ModuleNotFoundError("No module named 'megatron.energon'")`.
- `megatron.bridge.recipes.qwen.qwen3_moe`: failed through the same missing
  `megatron.energon` import.

Baseline artifact:
`/work-agents/intern_nemotron_worker_2/outputs/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/manifests/baseline_import_inventory.json`.

## Task-Owned Remediation

All remediation packages were downloaded from the configured internal pip
index `http://10.100.197.13/simple/` and installed with `--no-deps --target`
into the task-owned runtime target:

`/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site`.

No system package, shared root, or global user-site mutation was performed.

Installed wheels:

| Package | Version | Wheel sha256 |
|---|---:|---|
| `megatron-energon` | 7.3.2 | `151aeed2dbdfb1c168529c07dd3d123271658b2e557fc64625b4dbd2f3a9f31a` |
| `multi-storage-client` | 0.49.0 | `1cb7b31d1599149e87504265c16fc5a915e6174a71ee311881cfce439c102c6d` |
| `xattr` | 1.3.0 | `b4345387087fffcd28f709eb45aae113d911e1a1f4f0f70d46b43ba81e69ccdd` |
| `wcmatch` | 10.1 | `5848ace7dbb0476e5e55ab63c6bbd529745089343427caa5537f230cc01beb8a` |
| `bracex` | 2.6 | `0b0049264e7340b3ec782b5cb99beb325f36c3782a32e36e876452fd49a09952` |
| `braceexpand` | 0.1.7 | `91332d53de7828103dcae5773fb43bc34950b0c8160e35e0f44c4427a3b85014` |
| `rapidyaml` | 0.13.0.post2 | `c925290b44a703b7ea50f71399e0abb22d96411317a60ba7ca6c41e891444dcd` |
| `deprecation` | 2.1.0 | `a10811591210e1fb0e768a8c25517cabeabcba6f0bf96564f8ff45189f90b14a` |
| `webdataset` | 1.0.2 | `3dbfced32b25c0d199c6b9787937b6f85742bc3c84f652c846893075c1c082d9` |
| `filetype` | 1.2.0 | `7ce71b6880181241cf7ac8697a2f1eb6a8bd9b429f7ad6d27b8db9ba5f1c2d25` |

The remediation proceeded through exact import blockers in this order:

1. missing `megatron.energon`;
2. missing `multistorageclient`;
3. missing `xattr`;
4. missing `wcmatch`;
5. missing `bracex`;
6. missing `braceexpand`;
7. missing `ryml`;
8. missing `deprecation`;
9. missing `filetype`.

`webdataset` was also absent and was installed because it is an explicit
`megatron-energon` requirement and was part of the inventory probe.

## Final Import Proof

Final command:

```bash
cd /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron
PYTHONPATH=/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site:/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron/src \
  WANDB_DISABLED=true WANDB_MODE=offline TOKENIZERS_PARALLELISM=false \
  python3 /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/import_inventory_probe.py \
  --label final_remediated_after_filetype \
  --repo /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron \
  --model /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
  --out /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/final_after_filetype_import_inventory.json
```

Result:

- `TASK337_IMPORT_PROBE=PASS_QWEN3_MOE_IMPORT`.
- `megatron.energon`: PASS from
  `/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site/megatron/energon/__init__.py`,
  version `7.3.2`.
- `megatron.bridge.recipes.qwen.qwen3_moe`: PASS from
  `/usr/local/lib/python3.12/dist-packages/megatron/bridge/recipes/qwen/qwen3_moe.py`.

Relevant base/runtime distributions:

| Distribution | Version | Location |
|---|---:|---|
| `megatron-bridge` | `0.3.0rc0` | `/usr/local/lib/python3.12/dist-packages/` |
| `megatron-core` | `0.16.0rc0` | `/usr/local/lib/python3.12/dist-packages/` |
| `nemo-toolkit` | `2.7.3` | `/root/.local/lib/python3.12/site-packages/` |
| `torch` | `2.9.1+cu129` | `/usr/local/lib/python3.12/dist-packages/` |
| `transformers` | `4.57.1` | `/usr/local/lib/python3.12/dist-packages/` |
| `omegaconf` | `2.3.0` | `/usr/local/lib/python3.12/dist-packages/` |

## Symbol Probe

Symbol probe:

```bash
TASK337_SYMBOL_OUT=/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/qwen3_moe_symbol_probe.json \
PYTHONPATH=/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site:/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/Nemotron/src \
WANDB_DISABLED=true WANDB_MODE=offline TOKENIZERS_PARALLELISM=false \
python3 /root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/qwen3_moe_symbol_probe.py
```

Result:

- `TASK337_SYMBOL_PROBE=PASS_QWEN3_MOE_SYMBOL_IMPORT`.
- Public symbols included `qwen3_30b_a3b_pretrain_config` and
  `qwen3_30b_a3b_finetune_config`.
- The probe did not construct a model, load weights, run a training loop, run
  optimizer steps, run eval, export, or launch an endpoint.

## Next Gate Recommendation

Use this task only as runtime remediation evidence. Before any lead-gated
training launch, assign a separate no-training rerun/equivalent of task335
using:

```bash
PYTHONPATH=/root/task337_qwen_all_sft_30b_megatron_energon_runtime_remediation_s1/run_20260604T095948Z/runtime_site:<new_task_owned_repo>/src
```

The task335-equivalent rerun should re-check the train-only packed root,
validation fail-closed route, qwen3_moe import, config construction surface,
resource contract, and exact launch handoff. Training remains HOLD until that
gate is accepted by lead.

## Boundary Confirmation

Confirmed:

- no training;
- no optimizer steps;
- no benchmark eval;
- no AIME/task243 eval;
- no export;
- no endpoint;
- no promotion or go/no-go claim;
- no task310 release;
- no task255 reuse;
- no AIME2025 train rows;
- no shared-root mutation or deletion;
- no mutation under `/mnt/cephfs/data/processing/lei.song`;
- no main push, merge, or self-merge.
