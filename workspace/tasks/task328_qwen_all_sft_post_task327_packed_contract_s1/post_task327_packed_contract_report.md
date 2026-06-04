# task328 post-task327 packed contract report

<!-- METADATA:STATUS=Working,ASSIGNEE=intern_nemotron_worker_2,SESSION=2 -->

## Disposition

`PARTIAL_PASS_WITH_EXACT_BLOCKERS`.

Task328 did not produce a new `packed_qwen` root. The only safe packed-data
contract that can be carried forward is the prior constrained V11/task299 seed.
The post-task327 raw pass sources are excluded before packing because accepted
split exposure/parity and Qwen3-30B supervised-token packing proof are missing.
The nine task327 `BLOCKED_DECONTAM_HIT` sources remain excluded fail-closed.

Task310 recommendation:
`NO_GO_FOR_EXPANDED_POST_TASK327_ALL_SFT`; only the prior constrained task299
seed remains carry-forward evidence pending lead decision.

## Artifact root

- Output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task328_qwen_all_sft_post_task327_packed_contract_s1/run_20260604T051338Z`
- Final disposition:
  `manifests/final_disposition.json`
  sha256 `13885243f46b4e21431b9019ea9cf875cd003e57c6ef1ce31983662f453eec14`
- Preflight manifest:
  `manifests/post_task327_packed_contract_preflight.json`
  sha256 `f9cb7149ab47f6538583d9917508b59727a61615bcb089deb81578375f90d7e6`
- Source inclusion matrix:
  `matrices/source_inclusion_matrix.tsv`
  sha256 `d80277abf1f7a5c93c1e3291a1161cefdaabc927db6b4a8df3be7ce7af210948`
- Artifact checksum manifest:
  `manifests/artifact_checksums.sha256`
  sha256 `4728f2768a3a3caaf07b3471a3951cddc684e44ab6fe352bd2d36ed95f0a48b9`
- Preflight log:
  `logs/preflight.log`
  sha256 `13885243f46b4e21431b9019ea9cf875cd003e57c6ef1ce31983662f453eec14`
- Return-code file:
  `logs/preflight.rc`
  sha256 `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3`

## Command and environment

Command:

```bash
RUN_ROOT=/work-agents/intern_nemotron_worker_2/outputs/task328_qwen_all_sft_post_task327_packed_contract_s1/run_$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$RUN_ROOT/logs"
echo "$RUN_ROOT" > /work-agents/intern_nemotron_worker_2/outputs/task328_qwen_all_sft_post_task327_packed_contract_s1/latest_run_root.txt
set -o pipefail
PYTHONPATH=src python3 workspace/tasks/task328_qwen_all_sft_post_task327_packed_contract_s1/build_post_task327_contract_preflight.py \
  --output-root "$RUN_ROOT" 2>&1 | tee "$RUN_ROOT/logs/preflight.log"
rc=${PIPESTATUS[0]}
echo "$rc" > "$RUN_ROOT/logs/preflight.rc"
```

Result: `rc=2`, expected for `PARTIAL_PASS_WITH_EXACT_BLOCKERS`.

Environment recorded in `logs/command_env.json`:

- Current `origin/main`: `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`
- Product-code baseline: `ecb14173a820df377270273b9f7d9d92cb5076d2`
- Target model: `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- task327/#390 PR head pinned:
  `49c5d748c8c9ecc95d21c69a1bd16af0118cba3d`

Verification:

- `python3 -m py_compile workspace/tasks/task328_qwen_all_sft_post_task327_packed_contract_s1/build_post_task327_contract_preflight.py`: PASS
- `sha256sum -c .../manifests/artifact_checksums.sha256`: PASS for generated artifacts.

## Source inclusion matrix

| Source | Evidence | Decision | Rows | Decontam hits prompt/norm/ngram | Split exposure | Qwen pack status |
| --- | --- | --- | ---: | --- | --- | --- |
| `constrained-v11-task299-packed-seed` | task299/task276/task309 accepted packed evidence | `CARRY_FORWARD_SAFE_CONSTRAINED_PACKED_SEED_ONLY` | 280 | 0/0/0 | `PASS_INTENDED_VS_EXPOSED_PARITY` | `PASS_QWEN30B_PACKED_CONTRACT` |
| `instruction-following-structured` | task322/#388 | `EXCLUDE_FROM_TASK328_PACKED_CONTRACT` | 4969 | 0/0/0 | `NO_ACCEPTED_SPLIT_EXPOSURE_PROOF` | `NO_QWEN30B_PACKED_SUPERVISED_TOKEN_PROOF_FOR_RAW_SOURCE` |
| `agentic-interactive` | task322/#388 | `EXCLUDE_FROM_TASK328_PACKED_CONTRACT` | 19028 | 0/0/0 | `NO_ACCEPTED_SPLIT_EXPOSURE_PROOF` | `NO_QWEN30B_PACKED_SUPERVISED_TOKEN_PROOF_FOR_RAW_SOURCE` |
| `swe` | task327/#390 | `EXCLUDE_FROM_TASK328_PACKED_CONTRACT` | 51029 | 0/0/0 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NO_QWEN30B_PACKED_SUPERVISED_TOKEN_PROOF_FOR_RAW_SOURCE` |
| `instruction-following-chat` | task327/#390 | `EXCLUDE_DECONTAM_FAIL_CLOSED` | 426009 | 0/0/7 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NOT_EVALUATED_DECONTAM_BLOCKED` |
| `competitive-cpp-00` | task327/#390 | `EXCLUDE_DECONTAM_FAIL_CLOSED` | 466006 | 0/0/842 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NOT_EVALUATED_DECONTAM_BLOCKED` |
| `competitive-cpp-01` | task327/#390 | `EXCLUDE_DECONTAM_FAIL_CLOSED` | 466006 | 0/0/818 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NOT_EVALUATED_DECONTAM_BLOCKED` |
| `competitive-python-00` | task327/#390 | `EXCLUDE_DECONTAM_FAIL_CLOSED` | 910639 | 0/0/216 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NOT_EVALUATED_DECONTAM_BLOCKED` |
| `competitive-python-01` | task327/#390 | `EXCLUDE_DECONTAM_FAIL_CLOSED` | 910639 | 0/0/196 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NOT_EVALUATED_DECONTAM_BLOCKED` |
| `math-proofs-lean` | task327/#390 | `EXCLUDE_DECONTAM_FAIL_CLOSED` | 1376663 | 0/0/940 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NOT_EVALUATED_DECONTAM_BLOCKED` |
| `agentic-tool-calling` | task327/#390 | `EXCLUDE_DECONTAM_FAIL_CLOSED` | 316094 | 0/0/1 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NOT_EVALUATED_DECONTAM_BLOCKED` |
| `infinibyte-00` | task327/#390 | `EXCLUDE_DECONTAM_FAIL_CLOSED` | 587347 | 0/0/164 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NOT_EVALUATED_DECONTAM_BLOCKED` |
| `infinibyte-01` | task327/#390 | `EXCLUDE_DECONTAM_FAIL_CLOSED` | 587347 | 0/0/164 | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` | `NOT_EVALUATED_DECONTAM_BLOCKED` |

## Carry-forward constrained seed

The prior constrained task299 packed root remains the only safe packed root:

`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`

Task299/task276/task309 carried evidence:

| Metric | Value |
| --- | ---: |
| Train rows | 279 |
| Valid rows | 1 |
| Test rows | 0 |
| Train shards | 46 |
| Valid shards | 1 |
| Test shards | 1 |
| Train input tokens | 1024646 |
| Train supervised tokens | 228927 |
| Qwen contract | PASS |
| No AIME2025 train leakage | PASS |

Task299 artifact hashes:

| Artifact | sha256 |
| --- | --- |
| `manifest.json` | `59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d` |
| `contract_validation.json` | `75265f68621676c846551ba12022cb3d6f383b4f65e3bc7fb9773a197434d0b2` |
| `split_counts_parity.json` | `f4c335e651cc7777ecf326ed2fa3e46791c3de7286d7dee86042d941db2be70d` |
| `decontam_proof.json` | `e5b73a79ae8d1cd35b3188bd0f6bda60570f37c21831ac16d126a006d7fd56bc` |
| `tokenizer_chat_template_equivalence_probe.json` | `f31d5229da06ef1ff7c5457acfd66a7b4b4c91e92c61d7ae00f4492b476000ec` |
| `packed_qwen_30b_shard_checksums.json` | `444aef9230129d689c27be295ff054fc1dc4800fae52827280a5c289408fed11` |

## Exact blockers

1. The two task322 raw pass sources and task327 `swe` have row/checksum/decontam
   pass evidence, but no accepted split exposure/parity proof.
2. Those same three raw pass sources have not been packed under the Qwen3-30B
   tokenizer/chat-template path, so they lack supervised-token counts and
   Qwen3-30B contract proof.
3. The nine task327 decontam-hit sources are excluded fail-closed and cannot
   enter any packed contract without separate lead-approved false-positive or
   adjudication evidence.
4. task327/#390 is pinned at head
   `49c5d748c8c9ecc95d21c69a1bd16af0118cba3d`; the PR is still separate from
   current `origin/main`, so task328 records the evidence by exact artifact
   paths and hashes rather than relying on merged docs.

## Boundary confirmation

No packing was run by task328. No training, optimizer steps, benchmark eval,
export, endpoint, promotion, task255 reuse, AIME2025 prompt/label train rows,
shared deletion/mutation, main push, merge, or self-merge was performed.
