# task302 review of task298 30B runtime/resource/base-load evidence

<!-- METADATA:STATUS=ApprovedWithResiduals,ASSIGNEE=intern_nemotron_worker_4,SESSION=5 -->

## Decision

- Decision: `APPROVE_TASK298_RUNTIME_RESOURCE_BASE_LOAD_PASS_WITH_RESIDUALS`
- Reviewed PR: #364 `https://github.com/songCNMS/Nemotron/pull/364`
- Lead-requested exact head:
  `a1bd2af05aeb6554e7d9130076d9b81a3aa95b85`
- Current #364 head at review time:
  `8f1f7df9d6499eedb150d7e63323df8ee0411f41`
- Current #364 state: `OPEN`, base `main`, `CLEAN`, not draft
- Drift from `a1bd2af0` to `8f1f7df9`: worker_2 status plus task298
  history/task_knowledge only. The task298 runtime report is unchanged and
  `git diff --check` is clean.

I approve the task298 runtime/resource/base-load evidence as sufficient for
lead review of the 30B route. This approval is limited to the runtime,
resource, config/import, and Bridge base-import gate. It does not authorize
training, testing, AIME scoring, canary, export, endpoint, promotion, task255
reuse, AIME2025 train data, shared deletion, merge, release, or scale.

Task300 base AIME remains HOLD until lead separately gates task298 and releases
the testing route.

## Evidence Reviewed

Task298 report:

`workspace/tasks/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/30b_runtime_resource_base_load_report.md`

Local artifact root:

`/work-agents/intern_nemotron_worker_2/outputs/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z`

Remote run root:

`/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z`

Artifact source head recorded by task298:

`7d24b9295740ef5c21fd443d6399ec9641f8f5c5`

This source-head mismatch against PR head is acceptable for this gate because
the task298 branch diff is workspace docs/status/report only; no product code
diff was observed against `origin/main`.

## Checks

Read-only commands included:

```bash
gh pr view 364 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,isDraft,url,files
git fetch origin intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1
git diff --name-status a1bd2af05aeb6554e7d9130076d9b81a3aa95b85..8f1f7df9d6499eedb150d7e63323df8ee0411f41
git diff --check a1bd2af05aeb6554e7d9130076d9b81a3aa95b85..8f1f7df9d6499eedb150d7e63323df8ee0411f41
git diff --name-only a1bd2af05aeb6554e7d9130076d9b81a3aa95b85..8f1f7df9d6499eedb150d7e63323df8ee0411f41 -- workspace/tasks/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/30b_runtime_resource_base_load_report.md
git diff --name-status origin/main...8f1f7df9d6499eedb150d7e63323df8ee0411f41
sha256sum <task298 report-listed artifacts>
jq '.' manifests/no_training_30b_config_import_manifest.json
rg -n 'BRIDGE_IMPORT_RC|IMPORT_DONE|successfully|iteration' logs/bridge_import_30b_iter0.log
rg -n 'NVIDIA H200|143771|Qwen3-30B' logs/runtime_env.log logs/model_path_inventory.log logs/nvidia_smi_after.log
cat manifests/command_rcs.txt manifests/bridge_import_30b_latest_iteration.txt manifests/bridge_import_30b_du.txt
head -40 manifests/bridge_import_30b_inventory.tsv
```

## Verified Facts

- Exact model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Nearby Qwen3-30B-A3B variants were inventoried but not substituted.
- Runtime host: `lg-cmc-b7r201-f08u26-h200-000126`.
- GPU evidence: 8 x `NVIDIA H200`, each `143771 MiB`, visible as
  `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`.
- Preflight manifest disposition:
  `PASS_NO_TRAINING_30B_RUNTIME_CONFIG_IMPORT_PREFLIGHT`.
- Preflight imports passed for `nemo`, `megatron`, `megatron.bridge`,
  `megatron.bridge.training.config`, `megatron.bridge.recipes.qwen.qwen3_moe`,
  `megatron.energon`, and current-main
  `nemotron.recipes.super3.stage1_sft.qwen3_30b_a3b_local_train`.
- HF config/tokenizer proof: `Qwen3MoeConfig`, `Qwen3MoeForCausalLM`,
  `Qwen2TokenizerFast`, chat template present, 16 safetensor shards,
  total metadata bytes `61066575656`.
- Config recommendation built but not executed:
  TP `4`, PP `2`, EP `4`, ETP `1`, sequence parallel `true`,
  global batch `8`, micro batch `1`, train-iters value `1` for preflight only.
- Bridge import proof: `IMPORT_DONE`, `BRIDGE_IMPORT_RC=0`, successfully saved
  checkpoint at iteration `0`.
- Bridge import output size: `57G`; inventory rows: `16`.
- Later route recommendation is one 8 x H200 node with
  `nproc_per_node=8`.
- Eval route decision: base HF model can use eval-only SGLang directly; future
  Megatron SFT checkpoint likely needs eval-only HF export plus SGLang unless a
  separate 30B no-export MCore route is proven.

## Checksum Verification

Recomputed local hashes matched the task298 report:

| Artifact | sha256 |
|---|---|
| `manifests/no_training_30b_config_import_manifest.json` | `3279ed2b1f6383a13954bd43b300ec1f92c847ae409720e563ad8b79a0f04dd7` |
| `logs/no_training_30b_config_import_preflight.log` | `5ec05b25d96462f7fbf95eb922b0e8f922d373fdd19bbad9415e8a05fdd67668` |
| `logs/runtime_env.log` | `80e9efe532133112f04014cfd69c2078bb838d93a053de14d0fc52299a259f7f` |
| `logs/model_path_inventory.log` | `ede2f77f0892380663cccc9a1ca9d39a83bf9af69c291af22945f7723d338ff4` |
| `manifests/key_artifacts.sha256` | `69fe5bb2b7535347fd522d02f47e94654639b578c97998b2bce4e84139461172` |
| `logs/bridge_import_30b_iter0.log` | `0218eea8ab8334ac697bc465edce9e40ade3afa4523825d450ab152cd912629b` |
| `manifests/bridge_import_30b_du.txt` | `8c022da0c8cb109e899503af8565892db79abe5a9dff41265530c38b17d5c4fe` |
| `manifests/bridge_import_30b_inventory.tsv` | `09644a889efa598e8614b60cffa63dbf9ca5be1ed0b2a77ea4cc1120db25c38c` |
| `manifests/bridge_import_30b_latest_iteration.txt` | `5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9` |
| `manifests/bridge_import_30b_checksums.sha256` | `d01f2f4a9440d1b11691abf507f2354ecc0e079c3dbb9cb2a0cbb1f4a8a9649c` |

## Residual Risks

- `pip check` returned rc `1` with dependency warnings. The config/import
  preflight and Bridge import passed despite this, but full training may still
  need scoped runtime remediation.
- Bridge import was single-process `AutoBridge.import_ckpt`, producing
  rank-local torch-dist shards `[t 1/1, p 1/1]`. The TP4/PP2/EP4 training
  launch remains unproven until its own gated task.
- No no-export/no-endpoint 30B MCore generation route is proven. Eval-only HF
  export plus SGLang remains a testing route dependency, not promotion or
  endpoint clearance.
- No task299 data/decontamination approval, task300 base score, task301
  training checkpoint, canary, or FT-vs-base result is created by this approval.

## Boundary Confirmation

This review was static and read-only. I did not run training, testing, corrected
AIME scoring, non-AIME canary, export, endpoint, promotion, task255 reuse,
AIME2025 train data use, shared deletion, main push, merge, release, or scale.
