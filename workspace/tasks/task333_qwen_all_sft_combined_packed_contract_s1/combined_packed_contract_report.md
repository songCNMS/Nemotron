# task333 combined all-SFT packed contract report

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=PASS_COMBINED_PACKED_CONTRACT_READY_FOR_REVIEW,SESSION=99 -->

Generated: 2026-06-04T07:44:20Z

## Disposition

`PASS_COMBINED_PACKED_CONTRACT_READY_FOR_REVIEW`.

Task333 produced a no-training, task-owned combined all-SFT packed-contract
candidate. The candidate combines:

- task299 constrained Qwen3-30B seed packed shards;
- task329 `agentic-interactive` and `instruction-following-structured` shards;
- task331 `swe` shards produced with `tools_field=task331_missing_tools_header`.

The combined root applies task332 split policy
`task332_per_source_shard_holdout_v1`: source-local shard 14 is `valid`, shard
15 is `test`, all other shards are `train`.

No training, optimizer step, nonzero-LR smoke, benchmark eval, export,
endpoint, promotion, task310 release, 30B release, task255 reuse, AIME2025
train rows, shared deletion, main push, merge, or self-merge was performed.

## Artifacts

| Artifact | Path / value |
|---|---|
| Run root | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z` |
| Packed root | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract` |
| Splits root | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract/splits` |
| Blend | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract/blend.json` |
| Split manifest | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract/splits/manifest.json` |
| Metadata | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/packed_qwen_combined_contract/splits/metadata.json` |
| Top manifest | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/manifest.json` |
| Helper | `workspace/tasks/task333_qwen_all_sft_combined_packed_contract_s1/build_task333_combined_packed_contract.py` |

Important hashes:

| File | sha256 |
|---|---|
| `manifest.json` | `b7dc02cfd6fc8fdf7355ab689f5f8df60c8b72427ac8a94040037e2f13958ec0` |
| `manifests/artifact_checksums.sha256` | `f61cbf45f96a278c052b0df56a0f7e075b490bfcc144beeeb8c3a7be34900dd2` |
| `manifests/packed_shard_checksums.sha256` | `d61579f0318a298b133c1ce6149a89099eaa7ac5c37b6ae3a07aea8d2b4c4c54` |
| `splits/metadata.json` | `375b336cfdd2ba7aa394754cd3bc8a1f80b02d6979a33cfbf9e8c10347ae70f5` |
| `splits/manifest.json` | `c4a2018fb1d6ce331f7e934f8ba254fe2ce0e8a83230440d2a28394607b5f73e` |

The packed root exposes 96 split symlinks and `0` broken symlinks.

## Source Provenance

| Source | Included status | Raw rows | Source sha256 | Row manifest sha256 |
|---|---|---:|---|---|
| `m1-agentic-sft-v11-from-m0` | task299 constrained seed | 1,100 | `994166eeb83ffb5ebd213db9cc0d6cdd90208251bd2aab9dbb70cec7bf96691a` | `7562c86407e00c890ba86eb150a28c8c9bfbc1d7d35eb2c43bfbc5a9af878599` |
| `m1-agentic-sft-v11-math-final-answer` | task299 constrained seed | 200 | `0e5485eae86bf716d0c2e04e8e02595564b38a949d71d31a42874d6e87ef1731` | `e466ee7bd8032ff45596073d21c75f482611689edee3a20a9f5ade440a1ac653` |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | task299 constrained seed | 8 | `2039b67b2bcf5cf74b576a640f1f3a198d675e3fbd64a886da4be5753ad515d9` | `89ab29ebe1ab5a11e4467652ff40a855612e1ef4a47d024bbdc02eb9cd965e2f` |
| `agentic-interactive` | task322/task329 included pass | 19,028 | `dcfeda22372fa707c979cab29ddfe896b89a933f15ed4acbb4f16e7e3787d9dd` | `81f558b6cd08b9159402aab073283d9cee2898d0b83b23efd71a3a49e6160fbc` |
| `instruction-following-structured` | task322/task329 included pass | 4,969 | `03e4cc9a657f9f193860d82fe49764acc6b298f6ce6811497412aa5a0181ec77` | `206e27cb006fce1321115dd68732531cf46f6d3eb7e2d385f0eb3a2e7bb4c7a7` |
| `swe` | task331 no-tools-header included pass | 51,029 | `1e0fb6d9a8d955fb0f2160e44a4946e5f2c4eb3931e80dadb724ff823cdbc14c` | `998a95f209d2863de50b115704493bc7406ce5f37046732f75ab737bc9fa7ab2` |

The task333 helper emitted task-owned row manifests for the three task299 seed
source files. Raw task329/task331 sources use their accepted upstream row
manifests.

Excluded sources:

- all nine task327 `BLOCKED_DECONTAM_HIT` sources:
  `instruction-following-chat`, `competitive-cpp-00`,
  `competitive-cpp-01`, `competitive-python-00`,
  `competitive-python-01`, `math-proofs-lean`,
  `agentic-tool-calling`, `infinibyte-00`, `infinibyte-01`;
- task329 zero-supervised SWE shards, replaced by task331
  `task327-swe-no-tools-header`;
- six task332 structured validation-filtered rows;
- task255 artifacts.

## Packed Metrics

Total packed metrics:

| Shards | Rows | Input tokens | Supervised tokens | Bytes |
|---:|---:|---:|---:|---:|
| 96 | 89,325 | 342,875,996 | 38,245,535 | 175,969,867 |

By split:

| Split | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| train | 84 | 78,168 | 300,046,415 | 33,477,337 |
| valid | 6 | 5,561 | 21,365,088 | 2,373,422 |
| test | 6 | 5,596 | 21,464,493 | 2,394,776 |

By source:

| Source | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| `agentic-interactive` | 16 | 35,323 | 122,527,221 | 7,568,103 |
| `instruction-following-structured` | 16 | 2,693 | 10,307,854 | 1,922,762 |
| `m1-agentic-sft-v11-from-m0` | 16 | 244 | 942,062 | 167,555 |
| `m1-agentic-sft-v11-math-final-answer` | 16 | 28 | 75,305 | 54,821 |
| `m1-agentic-sft-v11-math-hard-verified-full-solution` | 16 | 8 | 8,770 | 7,979 |
| `swe` | 16 | 51,029 | 209,014,784 | 28,524,315 |

Each included source exposes one valid shard and one test shard under the
task332 policy. The hard-math source has valid/test shard files with zero rows,
matching the inherited packed shard contents.

## Structured Exclusions

The six task332 structured rows remain fail-closed excluded:

| Shard | Excluded rows |
|---|---:|
| `shard_000002` | 1 |
| `shard_000004` | 1 |
| `shard_000006` | 1 |
| `shard_000008` | 1 |
| `shard_000011` | 1 |
| `shard_000014` | 1 |

Exclusion manifest:
`/work-agents/intern_nemotron_worker_4/outputs/task332_qwen_all_sft_structured_split_policy_remediation_s1/run_20260604T065013Z/manifests/structured_filtered_rows.jsonl`
sha256 `be266834f38ab285775bcaebcc5bf006d6a5cf428d1b6b68a471fc228f28bd4b`.

Task333 did not repair these rows or rerun the structured validator; it used
the accepted task332 exclusion policy.

## Parity And Validators

Intended-vs-exposed multiset parity passed for `train`, `valid`, and `test`.
The split manifest and `blend.json` agree exactly with the 96 exposed shard
symlinks.

Qwen3-30B packed-data contract validation:

- Log:
  `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/logs/qwen30b_contract_validate.log`
- Return code: `0`
- Marker: `TASK333_QWEN30B_PACKED_CONTRACT=PASS`
- Validators:
  `validate_qwen_packed_sft_chat_contract` and
  `validate_qwen_training_pipeline_contract`
- Tokenizer/model:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`

Checksum checks:

| Check | Manifest entries | rc | Log |
|---|---:|---:|---|
| artifact `sha256sum -c` | 15 | 0 | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/logs/artifact_sha256sum_check.log` |
| packed shard `sha256sum -c` | 96 | 0 | `/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/logs/packed_shard_sha256sum_check.log` |

## Decontamination

Combined decontam disposition:
`PASS_NO_AIME2025_TRAIN_ROWS_BY_UPSTREAM_ACCEPTED_DECONTAM_AND_SOURCE_EXCLUSION`.

- AIME2025 prompt or label train rows: `0`.
- task255 reuse: not used.
- task246 heldout prompt hashes: `560`, sha256
  `a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d`.
- task246 heldout corpus sha256:
  `614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`.
- task329 `agentic-interactive` and `instruction-following-structured`:
  prompt-hash hits `0`, normalized-prompt hits `0`, n-gram hits `0`.
- task331 SWE: prompt-hash hits `0`, normalized-prompt hits `0`, n-gram hits
  `0`.
- task299 seed: accepted task299 prompt-hash overlap evidence carried forward;
  task262 final-answer n-gram scan had blocked rows `0` and blocker pairs `0`.

Residual nuance: task333 did not run a fresh decontam scan. It combines
accepted upstream proofs. The task299 seed did not emit a normalized-prompt hit
field; this is carried as a residual in
`manifests/decontam_no_aime2025_train_proof.json` rather than filled in with a
new claim.

## Commands And Environment

Repository:
`/work-agents/intern_nemotron_worker_1/Nemotron_task333`

Branch:
`intern_nemotron_worker_1/task333_qwen_all_sft_combined_packed_contract_s1`

Base:
`origin/main` `ad0c5a7d758d44370695b94c83385591f100c714`

Lead docs:
`origin/intern_nemotron_lead/session1-recovery-task-docs`
`afaad82114ab3cee4295d6950a972dd8ae2ed841`

Commands:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git worktree add -b intern_nemotron_worker_1/task333_qwen_all_sft_combined_packed_contract_s1 /work-agents/intern_nemotron_worker_1/Nemotron_task333 origin/main
git checkout afaad82114ab3cee4295d6950a972dd8ae2ed841 -- workspace/tasks/task333_qwen_all_sft_combined_packed_contract_s1
python3 -m py_compile workspace/tasks/task333_qwen_all_sft_combined_packed_contract_s1/build_task333_combined_packed_contract.py
PYTHONPATH=src python3 workspace/tasks/task333_qwen_all_sft_combined_packed_contract_s1/build_task333_combined_packed_contract.py --run-root /work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z
sha256sum <task333 manifest/checksum/metadata files>
find <task333 splits> -type l
find <task333 splits> -type l -xtype l
```

The helper's offline validator command is recorded in
`/work-agents/intern_nemotron_worker_1/outputs/task333_qwen_all_sft_combined_packed_contract_s1/run_20260604T074500Z/manifests/contract_validation.json`.

Runtime notes:

- No GPU, endpoint, training worker, or optimizer process was launched.
- The packed root is a task-owned symlink/materialization contract over
  accepted upstream packed Parquet shards, not a training release.
- Upstream task299/task329/task331/task332 artifacts were not modified.

## Residual Risks

1. This candidate still needs independent review and lead gate before any
   task310 use.
2. task333 did not run a fresh decontamination scan; it combines accepted
   upstream decontam proofs and carries the task299 normalized-prompt-field
   residual explicitly.
3. The hard-math task299 source has valid/test shard files with zero rows under
   the deterministic shard policy.
4. SWE rows still truncate to 4096 tokens, inherited from task331; the accepted
   unblock condition is nonzero supervised tokens inside the Qwen pack window.
5. The combined packed root must not be treated as task310, 30B release, eval,
   endpoint, or promotion authorization.
