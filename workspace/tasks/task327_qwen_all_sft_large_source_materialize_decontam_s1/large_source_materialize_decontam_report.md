# task327 large-source materialize/decontam report

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_2,SESSION=1 -->

## Disposition

`PARTIAL_PASS_WITH_EXACT_BLOCKERS`.

All 10 task322 `EXCLUDED_SIZE_GT_1GB` selected files were materialized in a
task-owned cache, byte counts and sha256 values matched task308/task322
references, row manifests were written, and JSON parse errors were zero.

Only `swe` passed the heldout decontam checks. The other 9 sources remain
fail-closed blockers because task246 AIME2025/HMMT/MATH heldout 13-word n-gram
hits were detected. None of the 9 blocked sources should be treated as eligible
for packing without lead review or a false-positive manifest follow-up.

## Artifact root

- Output root:
  `/work-agents/intern_nemotron_worker_2/outputs/task327_qwen_all_sft_large_source_materialize_decontam_s1/run_20260603T211508Z`
- Latest-run pointer:
  `/work-agents/intern_nemotron_worker_2/outputs/task327_qwen_all_sft_large_source_materialize_decontam_s1/latest_run_root.txt`
- Summary:
  `manifests/large_source_materialize_decontam_summary.json`
  sha256 `61f81d6c7dda8b1ee8a28c517d7a7783de9e2d3efc5829bee10501d282b42e14`
- Matrix:
  `matrices/large_source_materialize_decontam_matrix.tsv`
  sha256 `3f98295c0a71bfc437c985722d1620653f57607db399f3bd84b755779c9418aa`
- Final disposition:
  `manifests/final_disposition.json`
  sha256 `3dd2fe99d31a2f2d807d6ab2e238ce081e6d97dbd4b8b2650c028d638f2c4757`
- Artifact checksum manifest:
  `manifests/artifact_checksums.sha256`
  sha256 `0625cd917fd873e9a10e9d905f9825e56e89b6c7c9fb514abc8191ab755f0989`
- Run log:
  `logs/materialize_large_sources.log`
  sha256 `45836e81a487b41fa57752cf4f70e1226c15d2b5878dccabc4d7999e5a443cda`
- Return-code file:
  `logs/materialize_large_sources.rc`
  sha256 `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3`

## Command and environment

Host: `lg-cmc-b7r201-n09u29-cpu-000191`

Kernel: `Linux lg-cmc-b7r201-n09u29-cpu-000191 5.15.0-119-generic #129-Ubuntu SMP Fri Aug 2 19:25:20 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux`

Command:

```bash
RUN_ROOT=/work-agents/intern_nemotron_worker_2/outputs/task327_qwen_all_sft_large_source_materialize_decontam_s1/run_$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$RUN_ROOT/logs"
echo "$RUN_ROOT" | tee /work-agents/intern_nemotron_worker_2/outputs/task327_qwen_all_sft_large_source_materialize_decontam_s1/latest_run_root.txt
set -o pipefail
HF_HOME="$RUN_ROOT/hf_home" HF_HUB_DISABLE_PROGRESS_BARS=1 \
  python workspace/tasks/task327_qwen_all_sft_large_source_materialize_decontam_s1/materialize_large_sources.py \
  --output-root "$RUN_ROOT" 2>&1 | tee "$RUN_ROOT/logs/materialize_large_sources.log"
rc=${PIPESTATUS[0]}
echo "$rc" > "$RUN_ROOT/logs/materialize_large_sources.rc"
exit "$rc"
```

Environment recorded in `manifests/command_env_manifest.json`:

- `HF_HOME=/work-agents/intern_nemotron_worker_2/outputs/task327_qwen_all_sft_large_source_materialize_decontam_s1/run_20260603T211508Z/hf_home`
- `HF_HUB_CACHE=`
- `CUDA_VISIBLE_DEVICES=`
- `PYTHONPATH=`
- Working directory: `/work-agents/intern_nemotron_worker_2/Nemotron`
- Start: `2026-06-03T21:15:08Z`
- Finish: `2026-06-04T04:43:12Z`
- Return code: `2` (expected for partial pass with exact blockers)

Inputs:

- task322 summary:
  `/work-agents/intern_nemotron_worker_2/outputs/task322_qwen_all_sft_raw_materialize_count_decontam_s1/run_20260603T203100Z/manifests/materialize_count_decontam_summary.json`
- task246 heldout corpus:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`
- task246 prompt hashes:
  `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256`
- task311 MMLU-Pro reference:
  `/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/input/mmlu_pro/mmlu_pro_test.jsonl`
- task314 MMLU-Pro transitions reference:
  `/work-agents/intern_nemotron_worker_1/outputs/task314_qwen_all_sft_mmlu_pro_regression_forensics_s1/run_20260603T191500Z/mmlu_pro_row_transitions.jsonl`

Resource evidence:

- `df_before`: overlay 7.0T size, 313G used, 6.3T available, 5% used.
- `df_after`: overlay 7.0T size, 549G used, 6.1T available, 9% used.
- Output root size: `236G`.
- `sha256sum -c manifests/artifact_checksums.sha256`: PASS for 26 listed
  generated artifact files.

## Source matrix

All 10 selected files had matching byte counts and matching sha256 values
against task322/task308 references. Total rows counted: `6097779`.

| Source | Status | Rows | Parse errors | File sha256 | Row manifest sha256 | Decontam hits prompt/norm/ngram |
| --- | --- | ---: | ---: | --- | --- | --- |
| `instruction-following-chat` | `BLOCKED_DECONTAM_HIT` | 426009 | 0 | `37f9ecc3c41dc5e97cfd6fca962a94afbc8713349900ea6f413c040df549ddb8` | `3041bcdced4919c76e457fb5145ba38495e21771fe0c28fa308cedb19d148efe` | 0/0/7 |
| `competitive-cpp-00` | `BLOCKED_DECONTAM_HIT` | 466006 | 0 | `1081e0a650ecdc02df1b4b8b4fecf4b3d39828908874b4bf1a4015e638005c62` | `06417e0445200472fa37889cabd2b93f511471be3f45f49291aef9f420e16a39` | 0/0/842 |
| `competitive-cpp-01` | `BLOCKED_DECONTAM_HIT` | 466006 | 0 | `4500b6db059765aa6146d3c3247fdde1ce8b5cc762a7687ff4355b45e1701afa` | `da40247d1680d0b70d5b8a27221aa64606d7133ecb54dec69bf276d67ae9ffb2` | 0/0/818 |
| `competitive-python-00` | `BLOCKED_DECONTAM_HIT` | 910639 | 0 | `8314b37b7d42b32fb658c3be1fb974eb0814f44a856ccf2d90ec2d38856a7f5d` | `9a82de3e04f810a6e091cca3f71b2653e6d2e70a032334145d0cbe757b216b15` | 0/0/216 |
| `competitive-python-01` | `BLOCKED_DECONTAM_HIT` | 910639 | 0 | `988cc7a00686d6212b3f8fbef95919c8e72bbda81c9f859dd556df789bf44b30` | `14cc371e6feae18bee76f698dc404de59db8254f100f5321badc38f8cc2cb247` | 0/0/196 |
| `swe` | `INCLUDED_PASS` | 51029 | 0 | `1e0fb6d9a8d955fb0f2160e44a4946e5f2c4eb3931e80dadb724ff823cdbc14c` | `998a95f209d2863de50b115704493bc7406ce5f37046732f75ab737bc9fa7ab2` | 0/0/0 |
| `math-proofs-lean` | `BLOCKED_DECONTAM_HIT` | 1376663 | 0 | `b423525d35ad16c791863670cbad76b27d8463e2574770732e2cf5bf70661a2e` | `fdf6f39c6ada67256b28212bd738fe51df7ca9b525679615d4ce76ac64c51137` | 0/0/940 |
| `agentic-tool-calling` | `BLOCKED_DECONTAM_HIT` | 316094 | 0 | `f537a901d38a999627b8fe59e77a1007af0d79d71a892ad9a4a3d80456e5601b` | `ff1be6898b1576fef31ca6ac6ff6cf34bcffb154fcd7c76cea5ec30098ab4db5` | 0/0/1 |
| `infinibyte-00` | `BLOCKED_DECONTAM_HIT` | 587347 | 0 | `7d6cc0943a9264696ba177f152fd12c60cc2e1b042787a205221abcd4059c9e7` | `0b4b2d50c732f38e3478b2d7f9c7ad726b655c531259971311b3d2b09ce32143` | 0/0/164 |
| `infinibyte-01` | `BLOCKED_DECONTAM_HIT` | 587347 | 0 | `0124e374453dce8fa7a6e7ecd75356160f2bde525ba97b246d2b39e8479c4ef3` | `898ff4ab35d5711305463eb8a17e1b571b79ea1aba8e7636ba0ec05642218520` | 0/0/164 |

Split exposure for every source is recorded as
`RAW_SOURCE_FILE_NO_SPLIT_METADATA_TRAIN_ONLY_ASSUMPTION_FOR_LATER_LEAD_REVIEW`.
This is not a packing release; it is an explicit later-review assumption.

## Recommendation

- Carry `swe` as the only task327 large-source candidate with local
  materialize/count/checksum/row-manifest/decontam PASS evidence.
- Keep the other 9 large sources excluded from any all-SFT packing contract
  until lead accepts a false-positive manifest or a follow-up decontam
  adjudication task.
- Do not use generic raw `stage1_sft/data_blend_raw` as eligible all-SFT input
  from this task. This report covers only the 10 task322 `EXCLUDED_SIZE_GT_1GB`
  selected files.
- Later packing remains HOLD because this task did not perform final packing,
  tokenizer packing, supervised-token accounting, training, eval, export,
  endpoint, or promotion.

## Boundary confirmation

No final packing, Qwen chat-template packing, tokenizer-heavy training prep,
optimizer steps, benchmark eval, export, endpoint, promotion, task255 reuse,
AIME2025 prompt/label train rows, shared deletion/mutation, main push, merge, or
self-merge was performed.
