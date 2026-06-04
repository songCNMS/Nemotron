# task331 SWE supervised formatter unblock report

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=PASS_SWE_SUPERVISED_UNBLOCK,SESSION=83 -->

## Disposition

`PASS_SWE_SUPERVISED_UNBLOCK`.

Task-owned Qwen3-30B packing evidence proves that accepted task327 `swe` rows
can produce nonzero supervised tokens with a minimal formatter/config change:
the Qwen tokenizer-native chat template no longer receives the root-level SWE
tool schema header.

This is not a training, eval, export, endpoint, promotion, or task310 release.
Recommendation: allow SWE to enter a later lead-gated combined packed-contract
task with formatter/config provenance
`tools_field=task331_missing_tools_header`; do not train until that combined
contract and independent review are accepted.

## Root Cause And Remediation

Root cause: the original SWE records include a large root-level `tools` schema.
When passed to Qwen `apply_chat_template`, that schema is rendered before the
assistant content. With `pack_size=4096`, truncation lands before assistant
loss-mask tokens, so task329 packed 51,029 SWE rows with
`supervised_tokens=0`.

Formatter probe over 8 sample rows:

| Rendering | Rows with supervised tokens in first 4096 | Supervised tokens in first 4096 |
|---|---:|---:|
| Original root-level `tools` header | 0 | 0 |
| Task331 no-tools-header config | 8 | 4,423 |

Minimal remediation:

- Task-local config sets `tools_field: task331_missing_tools_header`.
- `messages` are unchanged, including assistant content, tool calls, and tool
  responses.
- No product-code change and no source mutation were made.
- The accepted SWE HF-cache source is exposed through a task-owned `.jsonl`
  hardlink so data-prep does not misclassify the extensionless HF blob as
  parquet.

Task-local helper:
`workspace/tasks/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/build_task331_swe_supervised_formatter_unblock.py`.

## Artifact Root

- Run root:
  `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z`
- Packed root:
  `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/packed_qwen_swe_no_tools_header`
- Splits root:
  `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/packed_qwen_swe_no_tools_header/splits`
- Final summary:
  `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/manifests/final_summary.json`
  sha256 `97bcce302827d892b52fced5d83cbd69bb2cfc8b02eb642b300a7ff4bffe982e`
- Artifact checksum manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/manifests/artifact_checksums.sha256`
  sha256 `5c665e73187f616e62b0d0f190407cf46cec7c94df84c6ec6cb0f0d7e4599c4e`;
  `sha256sum -c` passed for 18 non-recursive entries.
- Packed shard checksum manifest:
  `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/manifests/packed_shard_checksums.sha256`
  sha256 `4d06e726ef238d9102e3258d3d54062b1bcdc27ddd0a68f7057cee612ce10895`;
  `sha256sum -c` passed for 16 shard entries.

The aggregate artifact checksum manifest intentionally excludes itself and
`final_summary.json`; `final_summary.json` records the artifact manifest hash,
so including either file would make checksum evidence recursive.

## Source Provenance

| Field | Value |
|---|---|
| Source | `task327-swe` |
| Dataset snapshot | `nvidia/Nemotron-SWE-v1`, `r2e_gym.jsonl` |
| Revision | `0fe17a965b297a9c943a59050a14c42d5f0083ce` |
| Rows | 51,029 |
| Source sha256 | `1e0fb6d9a8d955fb0f2160e44a4946e5f2c4eb3931e80dadb724ff823cdbc14c` |
| Row manifest sha256 | `998a95f209d2863de50b115704493bc7406ce5f37046732f75ab737bc9fa7ab2` |
| Split exposure note | `RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW` |

Source provenance artifact:
`/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/manifests/source_provenance.json`
sha256 `a5024d13b14e949e7b2877d41e4929ac7b1679553bd2d938d73862dbbbd70abd`.

## Packing Metrics

Qwen3-30B tokenizer/model path:
`/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

Qwen contract validation:

- Log:
  `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/logs/qwen30b_contract_validate.log`
- Result: `TASK331_QWEN30B_PACKED_CONTRACT=PASS`
- Log sha256:
  `e7ec861cc2c191f270a03a81fbf35bdb863a448b2fc4d98ac9c361af5fcb78d0`

Packed Parquet metrics:

| Split | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| train | 14 | 44,651 | 182,890,496 | 24,957,952 |
| valid | 1 | 3,189 | 13,062,144 | 1,780,095 |
| test | 1 | 3,189 | 13,062,144 | 1,786,268 |
| total | 16 | 51,029 | 209,014,784 | 28,524,315 |

Receipt totals:

- `num_input_rows=51029`
- `num_output_sequences=51029`
- `num_packed_sequences=51029`
- `num_errors=0`
- `num_filtered=0`
- `num_validation_errors=0`
- `num_truncated_to_pack_size=51029`

All rows are long SWE traces and still truncate to 4096 tokens, but the
task331 condition is satisfied because supervised tokens are now present inside
the pack window.

Metric artifacts:

- `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/manifests/qwen30b_packing_metrics.json`
  sha256 `2dd7db51d313ed20dcc0431615999a9d1c3f0239e8e415683b94f7cfbac654d1`
- `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/manifests/packing_receipt_metrics.json`
  sha256 `0bbd490582e9051419d071071e7c4b3a8898e55c5db6161357ee9e1e0b591e21`

## Parity And Decontam

Intended-vs-exposed parity: `PASS`. Expected shard targets from
`packed_qwen_swe_no_tools_header/blend.json` match exposed split manifest paths
for train, valid, and test with no missing or unexpected shards.

Decontam/no-AIME2025-train proof:
`PASS_NO_AIME2025_TRAIN_ROWS_BY_TASK327_DECONTAM_AND_SOURCE_LIMIT`.

- task327 SWE decontam pass: prompt-hash hits `0`, normalized-prompt hits `0`,
  n-gram hits `0`, parse errors `0`.
- AIME2025 prompt or label train rows: `0`.
- task255 reuse: not used.
- All nine task327 `BLOCKED_DECONTAM_HIT` sources remained excluded:
  `instruction-following-chat`, `competitive-cpp-00`, `competitive-cpp-01`,
  `competitive-python-00`, `competitive-python-01`, `math-proofs-lean`,
  `agentic-tool-calling`, `infinibyte-00`, `infinibyte-01`.

Artifacts:

- `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/manifests/intended_vs_exposed_parity.json`
  sha256 `55e25f62e94a5655c806447e5c1c375f4b6f85766dca20c063109c115efc21f7`
- `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/manifests/decontam_no_aime2025_train_proof.json`
  sha256 `df24e165223e2418f10c21ba5f248d2d146ae47e1358f1f5ef1718afbb636b1c`

## Commands And Environment

Artifact-generation code revision:
`d3f295501ee3b8253e9fe90b493b592d93c92204`.

Branch:
`intern_nemotron_worker_2/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1`.

Base and docs:

- `origin/main` base:
  `410c2247fc5e09e6ad831bdee1628830b97fbd89`
- Lead docs source:
  `bbbf19df7ea7dad3fc644588f1e84240c464febe`

Host and environment:

- Host: `lg-cmc-b7r201-n09u29-cpu-000191`
- Platform: `Linux-5.15.0-119-generic-x86_64-with-glibc2.39`
- `PYTHONPATH=/work-agents/intern_nemotron_worker_2/Nemotron/src:src`
- `WANDB_MODE=offline`
- `WANDB_DISABLED=true`
- `TOKENIZERS_PARALLELISM=false`
- `SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- `SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`
- `CUDA_VISIBLE_DEVICES` unset

Final metadata refresh command, after helper commit:

```bash
PYTHONPATH=src python \
  workspace/tasks/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/build_task331_swe_supervised_formatter_unblock.py \
  --run-root /work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z \
  --skip-data-prep
```

Data-prep command recorded in
`/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/logs/data_prep.log`:

```bash
/usr/bin/python src/nemotron/recipes/super3/stage1_sft/data_prep.py \
  --config /work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z/config/swe_no_tools_header_qwen30b.yaml
```

Validation commands:

```bash
sha256sum -c manifests/artifact_checksums.sha256
sha256sum -c manifests/packed_shard_checksums.sha256
```

Both returned `rc=0` from the run root.

## Residual Risks

- This is a SWE-only formatter/config proof. A later combined packed-contract
  task must decide whether and how to combine this SWE candidate with other
  accepted all-SFT sources.
- task327 recorded the SWE raw source as a single file with no source split
  metadata. The task331 train/valid/test exposure is generated by packing
  ratios, not by an upstream dataset split.
- All 51,029 rows truncate to 4096 tokens. The unblock condition is nonzero
  supervised tokens under Qwen packing, not full-trace preservation.

## Boundary Confirmation

No training, optimizer steps, nonzero-LR smoke, benchmark eval, export,
endpoint, promotion, task255 reuse, AIME2025 train rows, shared deletion,
shared mutation, main push, merge, or self-merge was performed.
