# task309 All-Eligible-SFT Packed Data Contract Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=3 -->

## Disposition

`PASS_CONSTRAINED_V11_TASK299_PACKED_CONTRACT_WITH_RAW_STAGE1_EXCLUSIONS`.

Task309 is refreshed against task308 PR #374 evidence. The checksum-backed
V11/M1 sources that task308 marks task309-ready are covered by the reviewed
task299 Qwen3-30B packed root. Task309 therefore identifies that root as the
constrained packed-data contract for the current release path.

The generic `stage1_sft/data_blend_raw` registry remains excluded from this
contract. Task308 records those 12 HF raw sources as eligible in principle but
not task309-ready because exact row counts, heldout/AIME decontam proof, Qwen
chat-template packing evidence, and supervised-token counts are not
materialized.

Task310 recommendation:
`CONDITIONAL_GO_FOR_CONSTRAINED_V11_TASK299_SEED_ONLY_AFTER_LEAD_ACCEPTS_TASK309; NO_GO_FOR_GENERIC_RAW_STAGE1_SFT_INCLUSION`.

## Run Identity

- Worker branch:
  `intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1`
- PR: #372
  `https://github.com/songCNMS/Nemotron/pull/372`
- Current branch base:
  `origin/main` `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`
- Product-code baseline:
  `ecb14173a820df377270273b9f7d9d92cb5076d2`
- Refreshed lead docs:
  `b2b5d5fb51270ab28e9b947bd744dc9aaebd9899`
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task309_qwen_all_sft_packed_data_contract_s1/run_20260603T145300Z`
- Contract manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task309_qwen_all_sft_packed_data_contract_s1/run_20260603T145300Z/manifests/task309_constrained_packed_contract_manifest.json`
- Contract manifest sha256:
  `f33a14d05ab911779a8f43b5af138c6f4fa815191af3305820480a27fed47a14`
- Full artifact checksum manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task309_qwen_all_sft_packed_data_contract_s1/run_20260603T145300Z/manifests/task309_artifact_checksums.sha256`
- Artifact checksum manifest sha256:
  `b794bf3b96b6811d409b903b4b2ed2d95536b8ed655a4da44d9cf380143d6615`

## Task308 Evidence

Task308 PR #374:
`https://github.com/songCNMS/Nemotron/pull/374`

Lead-cited evidence head:
`4a46c9b5995d5cebe6624a5241d5543d48bee93c`

Current #374 view at refresh:

- State: `OPEN`
- Base: `main`
- Head: `b798fdfcfc3144111dd0a6e0f80505df031bcc5e`
- Merge state: `CLEAN`
- Draft: `false`

The task308 audit report hash is unchanged between the lead-cited head and the
current fetched head:

| Artifact | sha256 |
|---|---|
| task308 report at `4a46c9b` | `001154913dd28ffca20bdbe624ead7bf27c3bf4e27a95475e5f977db5cf97580` |
| task308 report at current #374 head | `001154913dd28ffca20bdbe624ead7bf27c3bf4e27a95475e5f977db5cf97580` |
| task308 inventory manifest | `4f629e015d4e7a8965899f1fb6c1a5e22e4e666fff28c5bfa69d9d9b31f97a61` |

Task308 decision:
`PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS`.

Task308 trainable checksum-backed V11/M1 JSONL sources:

| Source | Raw rows | sha256 |
|---|---:|---|
| `m1-agentic-sft-v11-from-m0` | 1100 | `994166eeb83ffb5ebd213db9cc0d6cdd90208251bd2aab9dbb70cec7bf96691a` |
| `m1-agentic-sft-v11-math-final-answer` | 200 | `0e5485eae86bf716d0c2e04e8e02595564b38a949d71d31a42874d6e87ef1731` |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 8 | `2039b67b2bcf5cf74b576a640f1f3a198d675e3fbd64a886da4be5753ad515d9` |

Raw task308 source total for the constrained seed: `1308` rows.

Generic `stage1_sft/data_blend_raw` status:

- Dataset entries: `12`
- Total bytes from HF metadata: `243316402226`
- Contract status: excluded until materialized, counted, decontam scanned, and
  Qwen-packed with supervised-token proof.

## Packed Contract

Task309 uses the reviewed task299 Qwen3-30B-ready packed root as the constrained
packed contract under task308 constraints:

`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`

Task299 decision:
`PASS_30B_DATA_PACKING_CONTRACT`.

Task299 contract mode in task309:
`identify_and_checksum_existing_reviewed_task299_packed_root_under_task308_constraints_no_new_packing_run`.

Target model:
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

Split counts:

| Split | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| train | 46 | 279 | 1024646 | 228927 |
| valid | 1 | 1 | 1491 | 1428 |
| test | 1 | 0 | 0 | 0 |

Train source counts:

| Source | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| `m1-agentic-sft-v11-from-m0` | 16 | 244 | 942062 | 167555 |
| `m1-agentic-sft-v11-math-final-answer` | 16 | 28 | 75305 | 54821 |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 14 | 7 | 7279 | 6551 |

Contract results:

- Qwen packed/training contract validation: `PASS`
- Intended-vs-exposed multiset parity: `PASS`
- Decontam/no-AIME2025-train proof: `PASS`
- Tokenizer-native Qwen chat-template/API equivalence: `PASS`
- Task255 reuse: `false`

Task299 artifact hashes carried forward:

| Artifact | sha256 |
|---|---|
| `manifest.json` | `59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d` |
| `contract_validation.json` | `75265f68621676c846551ba12022cb3d6f383b4f65e3bc7fb9773a197434d0b2` |
| `split_counts_parity.json` | `f4c335e651cc7777ecf326ed2fa3e46791c3de7286d7dee86042d941db2be70d` |
| `decontam_proof.json` | `e5b73a79ae8d1cd35b3188bd0f6bda60570f37c21831ac16d126a006d7fd56bc` |
| `tokenizer_chat_template_equivalence_probe.json` | `f31d5229da06ef1ff7c5457acfd66a7b4b4c91e92c61d7ae00f4492b476000ec` |
| `packed_qwen_30b_shard_checksums.json` | `444aef9230129d689c27be295ff054fc1dc4800fae52827280a5c289408fed11` |

Qwen3-30B asset hashes:

| File | sha256 |
|---|---|
| `config.json` | `a1ee086a68d0cbfc87316da00ba4b8507bd1292978108e2496201a30a450f438` |
| `tokenizer.json` | `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` |
| `tokenizer_config.json` | `a62ff0a2472a0fa1b8eaabcb57c59b58afa42a22831dc141400b6e0cf2b65ce3` |
| `vocab.json` | `ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910` |
| `merges.txt` | `599bab54075088774b1733fde865d5bd747cbcc7a547c5bc12610e874e26f5e3` |

## Commands And Environment

Commands used were read-only/preparatory except for worker-owned task309
report/status/artifact writes:

```bash
git fetch --all --prune
git fetch origin intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1
gh pr view 372 --json number,state,baseRefName,headRefName,headRefOid,mergeStateStatus,isDraft,url
gh pr view 374 --json number,state,baseRefName,headRefName,headRefOid,mergeStateStatus,isDraft,url,title
git diff --name-status 4a46c9b5995d5cebe6624a5241d5543d48bee93c..origin/intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1
git show 4a46c9b5995d5cebe6624a5241d5543d48bee93c:workspace/tasks/task308_qwen_all_sft_pipeline_inventory_audit_s1/all_sft_pipeline_inventory_audit_report.md
jq over task308 and task299 manifests
sha256sum over Qwen3-30B-A3B tokenizer/config assets
```

No new packing job was run by task309. No training, eval, export, endpoint, or
promotion command was run.

## Residual Risks

- Generic `stage1_sft/data_blend_raw` remains excluded because exact rows,
  decontam proof, Qwen packing proof, and supervised-token counts are not
  materialized.
- Valid split remains sparse at `1` row and test split has `0` rows, inherited
  from task299/task276 packing evidence.
- Task309 identifies a checksum-backed existing task299 packed root; it does
  not claim a new all-raw-SFT materialization.

## Boundary Confirmation

Confirmed:

- No training or optimizer steps.
- No benchmark eval.
- No export.
- No endpoint.
- No promotion or go/no-go claim beyond the constrained task310 recommendation
  above.
- No task255 reuse.
- No AIME2025 prompts or labels used as train rows.
- No product/source-code edits.
- No shared deletion, including under `/mnt/cephfs/data/processing/lei.song`.
- No main push.
- No merge.
