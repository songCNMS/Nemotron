# task308 all-SFT pipeline inventory audit report

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_1,SESSION=86 -->

## Decision

Decision: `PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS`.

Current `origin/main` is
`172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`. Product code is unchanged from
baseline `ecb14173a820df377270273b9f7d9d92cb5076d2`; the diff only adds
task310 docs. This audit did not train, pack final data, run eval, export,
launch an endpoint, claim promotion, reuse task255, write AIME2025 train rows,
delete shared files, edit product code, push main, or merge.

The checksum-backed trainable Qwen/M1 V11 sources are ready for task309 as
inputs to a packed-data contract. The generic `stage1_sft/data_blend_raw`
sources are eligible in principle but not task309-ready from current evidence:
their repo/file checksums are known, but exact row counts, no-AIME/decontam
proof, Qwen chat-template packing evidence, and supervised-token counts are not
materialized in this audit.

## Artifact

Task-owned artifact root:
`/work-agents/intern_nemotron_worker_1/outputs/task308_qwen_all_sft_pipeline_inventory_audit_s1/run_20260603T144136Z`

Inventory manifest:
`/work-agents/intern_nemotron_worker_1/outputs/task308_qwen_all_sft_pipeline_inventory_audit_s1/run_20260603T144136Z/all_sft_inventory_manifest.json`

Manifest sha256:
`4f629e015d4e7a8965899f1fb6c1a5e22e4e666fff28c5bfa69d9d9b31f97a61`

## Commands And Environment

Repository:
`/work-agents/intern_nemotron_worker_1/Nemotron`

Lead docs seen:
`5f4167dc819f5313e7db7fc43e57cec113306cc4`

Commands run were read-only except for this report/status and worker-owned
task308 output artifacts:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rev-parse origin/main origin/intern_nemotron_lead/session1-recovery-task-docs
git diff --name-status ecb14173a820df377270273b9f7d9d92cb5076d2 172cd0e7ceaba8ad2b412d1145441dbb4c5fd122
rg/sed over stage1_sft, qwen_chat_contract, M1 planner, training, canary, and eval files
jq over task246/task251/task262/task276/task299 manifests
wc -l and sha256sum over local worker-owned sidecar/heldout files
python3 HfApi.dataset_info(files_metadata=True) for public HF repo/file metadata only
python3 task308 inventory manifest writer
```

No HF source JSONL was downloaded and no final packed data was produced.

## Pipeline Map

| Stage | Current entrypoints | Audit status |
| --- | --- | --- |
| SFT raw source registry | `src/nemotron/recipes/super3/stage1_sft/config/data_prep/data_blend_raw.json`, `default.yaml` | Registry exists; generic HF data is not materialized/count/decontam proven for task309. |
| Qwen M1 data prep / packing | `stage1_sft/data_prep.py`, `config/data_prep/qwen_agentic_v0.yaml`, `qwen_chat_contract.py` | Qwen tokenizer-native contract is proven by task276/task299 artifacts. |
| Training planner / launch | `plan_m1_agentic_sft_training.py`, `m1_agentic_train.yaml`, `qwen3_30b_a3b_local_train.py` | Mapped only; no training launch. |
| Checkpoint load / canary | `qwen_aime2025_base_vs_ft_gate.py`, `qwen_v11_export_load_canary_prompts.yaml` | Mapped only; no canary/export/endpoint. |
| Corrected benchmark eval | `stage3_eval/config/m1_corrected_math_comparison.yaml`, `qwen_aime2025_base_vs_ft_gate.py` | Mapped only; no benchmark eval. |

## Trainable Inventory

### Checksum-backed V11 M1 JSONL sources

| Source | Path | Rows | sha256 | Eligibility |
| --- | --- | ---: | --- | --- |
| `m1-agentic-sft-v11-from-m0` | `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m1_agentic_sft/agentic_sft_v0_train.jsonl` | 1100 | `994166eeb83ffb5ebd213db9cc0d6cdd90208251bd2aab9dbb70cec7bf96691a` | Eligible for task309 packing with task262/task276/task299 decontam contract. |
| `m1-agentic-sft-v11-math-final-answer` | `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m1_agentic_sft/agentic_sft_v0_math_final_answer_train.jsonl` | 200 | `0e5485eae86bf716d0c2e04e8e02595564b38a949d71d31a42874d6e87ef1731` | Eligible; task262 full token 8-gram final-answer scan passed. |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | `/work-agents/intern_nemotron_worker_2/outputs/task251_qwen_aime_v10_hotpotqa_loader_unblock_s1/m1_agentic_sft/agentic_sft_v0_math_hard_verified_full_solution_train.jsonl` | 8 | `2039b67b2bcf5cf74b576a640f1f3a198d675e3fbd64a886da4be5753ad515d9` | Eligible but sparse. |

Environment counts for the 1100-row base source are 100 rows each across
11 environments: code execution, general tool calling, math competition,
math reasoning, multi-turn tool use, grounded QA, multihop QA, structured JSON,
SWE pivot, terminal shell, and tool-call repair.

### M0 math sidecar provenance

Task246 M0 V10 math sidecar:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`

| File | Rows | sha256 |
| --- | ---: | --- |
| `math_competition_numeric/train-split.jsonl` | 8 | `01ac5d1c8571dc956bbae12b7f1a00a4e759d59e503abbf2ddfba3b85aa324e3` |
| `math_competition_numeric/val-split.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `manifest.json` | n/a | `ca7864ce5ddbec20c0e0b1e67fdaefb2b09ef884f430b68fe7158c5b62951477` |

Source dataset: `AI-MO/NuminaMath-CoT`, revision
`9d8d210c9f6a36c8f3cd84045668c9b7800ef517`; task246 scanned 859494 source
rows, selected 8 V10 candidate train rows, and blocked 0 rows by decontam.

### Packed Qwen roots

Task276 Qwen3-4B packed root:
`/work-agents/intern_nemotron_worker_2/outputs/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/run_20260602T034648Z/packed_qwen`

Task299 Qwen3-30B-ready packed root:
`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`

Packed split counts are identical:

| Split | Shards | Rows | Input tokens | Supervised tokens |
| --- | ---: | ---: | ---: | ---: |
| train | 46 | 279 | 1024646 | 228927 |
| valid | 1 | 1 | 1491 | 1428 |
| test | 1 | 0 | 0 | 0 |

Train split source counts:

| Source | Shards | Rows | Input tokens | Supervised tokens |
| --- | ---: | ---: | ---: | ---: |
| `m1-agentic-sft-v11-from-m0` | 16 | 244 | 942062 | 167555 |
| `m1-agentic-sft-v11-math-final-answer` | 16 | 28 | 75305 | 54821 |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 14 | 7 | 7279 | 6551 |

Task299 30B top manifest sha256:
`59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d`

Task299 contract status: tokenizer asset/API/chat-template equivalence passed,
split parity passed, Qwen packed/training contract validators passed, decontam
status passed.

## Generic stage1_sft/data_blend_raw Inventory

Config sha256:
`1c76013e66643972cfa1c96aca86571a666c81d7fd6cf95b024e081f0836503d`

The 12 source entries are present in current main and have HF repo/file
metadata. Exact row counts and decontam status were not produced because this
task did not download or materialize those large JSONL files.

| Source | Repo SHA | File sha256 | Exact rows | Task309 status |
| --- | --- | --- | --- | --- |
| `instruction-following-chat` | `83dcd3aded0d289b0bbc018d3f9af4c5dd4005df` | `37f9ecc3c41dc5e97cfd6fca962a94afbc8713349900ea6f413c040df549ddb8` | unknown | Block until materialized/count/decontam scanned. |
| `instruction-following-structured` | `83dcd3aded0d289b0bbc018d3f9af4c5dd4005df` | `03e4cc9a657f9f193860d82fe49764acc6b298f6ce6811497412aa5a0181ec77` | unknown | Block until materialized/count/decontam scanned. |
| `competitive-cpp-00` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `1081e0a650ecdc02df1b4b8b4fecf4b3d39828908874b4bf1a4015e638005c62` | unknown | Block until materialized/count/decontam scanned. |
| `competitive-cpp-01` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `4500b6db059765aa6146d3c3247fdde1ce8b5cc762a7687ff4355b45e1701afa` | unknown | Block until materialized/count/decontam scanned. |
| `competitive-python-00` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `8314b37b7d42b32fb658c3be1fb974eb0814f44a856ccf2d90ec2d38856a7f5d` | unknown | Block until materialized/count/decontam scanned. |
| `competitive-python-01` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `988cc7a00686d6212b3f8fbef95919c8e72bbda81c9f859dd556df789bf44b30` | unknown | Block until materialized/count/decontam scanned. |
| `swe` | `0fe17a965b297a9c943a59050a14c42d5f0083ce` | `1e0fb6d9a8d955fb0f2160e44a4946e5f2c4eb3931e80dadb724ff823cdbc14c` | unknown | Block until materialized/count/decontam scanned. |
| `math-proofs-lean` | `97229c590831adfe96202f5cd071d444d535bf91` | `b423525d35ad16c791863670cbad76b27d8463e2574770732e2cf5bf70661a2e` | unknown | Block until materialized/count/decontam scanned. |
| `agentic-interactive` | `650d590978ca35c8f1ecea2faf136e5fac421b62` | `dcfeda22372fa707c979cab29ddfe896b89a933f15ed4acbb4f16e7e3787d9dd` | unknown | Block until materialized/count/decontam scanned. |
| `agentic-tool-calling` | `650d590978ca35c8f1ecea2faf136e5fac421b62` | `f537a901d38a999627b8fe59e77a1007af0d79d71a892ad9a4a3d80456e5601b` | unknown | Block until materialized/count/decontam scanned. |
| `infinibyte-00` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `7d6cc0943a9264696ba177f152fd12c60cc2e1b042787a205221abcd4059c9e7` | unknown | Block until materialized/count/decontam scanned. |
| `infinibyte-01` | `d6e7c6b404ed5db6e1104b41d0f80a0c7dad7bf8` | `0124e374453dce8fa7a6e7ecd75356160f2bde525ba97b246d2b39e8479c4ef3` | unknown | Block until materialized/count/decontam scanned. |

## Exclusions

- AIME2025 prompts and labels remain held out for eval/decontam only.
- Task246 heldout corpus is excluded from trainable data: 560 rows, corpus
  sha256 `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`.
- Task246 prompt hashes are excluded from trainable data: 560 hashes, sha256
  `a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d`.
- Task251 `agentic_sft_v0_val_shadow.jsonl` is not a train source.
- Task251 `agentic_sft_v0_math_heldout_eval.jsonl` is empty and excluded.
- Task253 stale packed data is excluded because task262 documented split
  materialization mismatch.
- Task255 artifacts are excluded entirely and were not reused.

## Task309 Recommendation

Recommend task309 proceed fail-closed:

1. Use task299 as the immediate checksum-backed Qwen3-30B-ready seed only if
   task309 wants the already proven V11 M1/math set.
2. If task309 must be "all-SFT" including generic `stage1_sft/data_blend_raw`,
   first materialize and count every HF source, run heldout prompt-hash and
   full n-gram decontam against AIME25/HMMT/MATH heldouts where relevant,
   prove no task255 or AIME2025 prompt/label train rows, and then pack with
   `qwen_agentic_v0.yaml` against
   `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
3. Emit split manifest, row/token/supervised-token/source counts,
   intended-vs-exposed parity, shard checksums, Qwen chat-template/tokenizer
   contract proof, and residual valid/test sparsity risk before task310.

Without step 2, generic `stage1_sft/data_blend_raw` should remain excluded
from the next training attempt.
