# task309 All-Eligible-SFT Packed Data Contract Report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_2,SESSION=2 -->

## Disposition

`BLOCK_DEPENDENCY_TASK308_INVENTORY_MISSING`.

Task309 is blocked before producing a new all-eligible-SFT `packed_qwen` root.
The required upstream task308 all-SFT source inventory is not available: the
task308 branch exists, but there is no visible PR, no report, and no task308
output root with trainable source eligibility, exclusion, decontam, and blend
decisions. Without that evidence, task309 cannot safely decide which sources are
eligible to pack for task310.

Task310 recommendation: `NO_GO_HOLD`.

## Run Identity

- Worker branch:
  `intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1`
- PR: #372
  `https://github.com/songCNMS/Nemotron/pull/372`
- Evidence source head:
  `d054925b1792a5365738247eeb8bdec462e1e6c6`
- Current branch base:
  `origin/main` `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`
- Product-code baseline:
  `ecb14173a820df377270273b9f7d9d92cb5076d2`
- Refreshed lead docs:
  `5f4167dc819f5313e7db7fc43e57cec113306cc4`
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task309_qwen_all_sft_packed_data_contract_s1/run_20260603T143700Z`

## Commands And Evidence

Commands used were read-only/preparatory:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git fetch origin
git rev-parse origin/main origin/intern_nemotron_lead/session1-recovery-task-docs
git rev-parse origin/intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1
gh pr list --search 'task308_qwen_all_sft_pipeline_inventory_audit_s1' --state all --json ...
find /work-agents -path '*/outputs/task308_qwen_all_sft_pipeline_inventory_audit_s1*' ...
jq '{decision, packed_root, qwen3_30b_a3b_model, current_main, summary, artifact_checksums}' \
  /work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/manifest.json
sha256sum /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507/{config.json,tokenizer.json,tokenizer_config.json,vocab.json,merges.txt}
```

No packing job, training, eval, export, endpoint, promotion, product-code edit,
shared deletion, main push, or merge was run.

## Task308 Dependency State

Task308 branch:

`origin/intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1`

Task308 branch head:

`348cba44c02043cd6310a36ec722a68278288db2`

Task308 PR query:

`[]`

Task308 output probe:

- Visible output count: `0`
- No task308 report, inventory tables, source manifest, or all-SFT blend
  recommendation was found under `/work-agents`.

Required missing evidence:

- Trainable all-eligible-SFT source inventory.
- Per-source eligibility/exclusion decisions.
- Held-out/eval/decontam row exclusions.
- No-AIME2025-train proof over the final source list.
- Concrete task309 blend plan or `PASS_AUDIT` recommendation.

## Available But Insufficient Evidence

Task299 provides a 30B-ready V11/task276 packing contract, but it is not the
all-eligible-SFT source inventory required by task309.

Task299 accepted root:

`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`

Task299 decision:

`PASS_30B_DATA_PACKING_CONTRACT`

Task299 counts:

| Split | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| train | 46 | 279 | 1024646 | 228927 |
| valid | 1 | 1 | 1491 | 1428 |
| test | 1 | 0 | 0 | 0 |

Task299 train source counts:

| Source | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| `m1-agentic-sft-v11-from-m0` | 16 | 244 | 942062 | 167555 |
| `m1-agentic-sft-v11-math-final-answer` | 16 | 28 | 75305 | 54821 |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 14 | 7 | 7279 | 6551 |

Task299 evidence carried forward:

- Qwen packed chat contract: `PASS`
- Qwen training pipeline contract: `PASS`
- Intended-vs-exposed multiset parity: `PASS`
- Decontam/no-AIME2025-train proof: `PASS`
- Task246 heldout prompt hashes: `560`
- task246 prompt hash overlap: `0`
- AIME contest mentions in trainable messages: `0`
- Task255 reuse: `false`

Task299 artifact hashes:

| Artifact | sha256 |
|---|---|
| `manifest.json` | `59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d` |
| `contract_validation.json` | `75265f68621676c846551ba12022cb3d6f383b4f65e3bc7fb9773a197434d0b2` |
| `split_counts_parity.json` | `f4c335e651cc7777ecf326ed2fa3e46791c3de7286d7dee86042d941db2be70d` |
| `decontam_proof.json` | `e5b73a79ae8d1cd35b3188bd0f6bda60570f37c21831ac16d126a006d7fd56bc` |
| `tokenizer_chat_template_equivalence_probe.json` | `f31d5229da06ef1ff7c5457acfd66a7b4b4c91e92c61d7ae00f4492b476000ec` |
| `packed_qwen_30b_shard_checksums.json` | `444aef9230129d689c27be295ff054fc1dc4800fae52827280a5c289408fed11` |
| `packed_qwen_30b_shard_checksums.sha256` | `ff592c935f09037d81a2aceb9dc394189c871623cebf1a1d92dd9b4233d493fa` |

Reason this does not satisfy task309:

Task299 adapts task276 V11 packed data to Qwen3-30B-A3B. It does not inventory
all current-main eligible SFT sources and does not authorize the final
all-eligible-SFT blend for task310.

## Qwen3-30B Tokenizer/Model Proof

Target model path:

`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

Asset hashes:

| File | sha256 |
|---|---|
| `config.json` | `a1ee086a68d0cbfc87316da00ba4b8507bd1292978108e2496201a30a450f438` |
| `tokenizer.json` | `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` |
| `tokenizer_config.json` | `a62ff0a2472a0fa1b8eaabcb57c59b58afa42a22831dc141400b6e0cf2b65ce3` |
| `vocab.json` | `ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910` |
| `merges.txt` | `599bab54075088774b1733fde865d5bd747cbcc7a547c5bc12610e874e26f5e3` |

Task299 already proved tokenizer-native chat-template equivalence for this
30B target, but task309 did not produce new packed shards because the source
eligibility dependency is missing.

## Task-Owned Artifacts

Key task309 artifacts:

| Artifact | sha256 |
|---|---|
| `manifests/task309_blocker_manifest.json` | `0864222b7f0d3edde825b2a7c397a9888bc9b59687e0b05e79736077cb425a7d` |
| `manifests/task299_summary.json` | `2801dd6b8b76cc1cf5cb43bc7554af862b0c3a192fe1758059bee9ec0966c1d0` |
| `manifests/task299_decontam_proof.json` | `e5b73a79ae8d1cd35b3188bd0f6bda60570f37c21831ac16d126a006d7fd56bc` |
| `manifests/qwen30b_asset_hashes.sha256` | `6757f82a5c790f32bebb4e987c2ce207033f81b205ad229b69a23ba9a5d8c1a1` |
| `logs/task308_pr_query.json` | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |
| `logs/task308_output_probe.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Full checksum manifest:

`/work-agents/intern_nemotron_worker_2/outputs/task309_qwen_all_sft_packed_data_contract_s1/run_20260603T143700Z/manifests/task309_artifact_checksums.sha256`

## Recommendation

Task310 should remain `NO_GO_HOLD`.

Smallest unblock path:

1. Complete task308 with `PASS_AUDIT` or an exact blocker.
2. If task308 passes, rerun/update task309 using only task308 trainable
   all-eligible-SFT sources.
3. Produce a fresh task309 packed root with split manifest, counts,
   token/supervised-token counts, shard/source counts, intended-vs-exposed
   parity, checksums, tokenizer-native Qwen chat-template proof, and no-AIME2025
   train decontam proof.

## Boundary Confirmation

Confirmed:

- No training or optimizer steps.
- No benchmark eval.
- No export.
- No endpoint.
- No promotion or go/no-go claim beyond `NO_GO_HOLD`.
- No task255 reuse.
- No AIME2025 prompts or labels used as train rows.
- No product/source-code edits.
- No shared deletion, including under `/mnt/cephfs/data/processing/lei.song`.
- No main push.
- No merge.
