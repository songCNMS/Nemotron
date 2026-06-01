# task246 Real Decontam Corpus Report

## Summary

Task246 produced a real, non-placeholder heldout prompt corpus and a task-owned
V10 M0 sidecar input path for the Qwen3-4B V10 pilot. No training, eval,
endpoint launch, main push, or shared `/mnt/cephfs/data/processing/lei.song`
deletion was performed.

Output root:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1`

Top manifest:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/manifest.json`

Top manifest sha256:
`9e5bbc62507f893955374bd520dae81601a51bd1e0030c1508f819ad268f6eb5`

## Heldout Corpus

Corpus path:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`

Corpus sha256:
`614b2b347d33c1ec00cfd2c33222c26ad1d99b8b837bd7e48ea11fd4fedae6f9`

Prompt hashes path:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/prompt_hashes.sha256`

Prompt hashes sha256:
`a2a348ee12f962d5dd7ed7cf0e5d034ebea4a76a2287804e97ade331b552a78d`

Rows: `560`

Unique prompt hashes: `560`

Duplicates removed: `0`

Label fields written: `false`

Sources:

| Source | Repo | Revision | Files | Rows | License note |
| --- | --- | --- | --- | ---: | --- |
| AIME25 | `opencompass/AIME2025` | `a6ad95f611d72cf628a80b58bd0432ef6638f958` | `aime2025-I.jsonl`, `aime2025-II.jsonl` | 30 | MIT |
| HMMT Feb 2025 | `PraMamba/HMMT-202502` | `9de5288c84abeb090b162f75e43a96ad971c7b26` | `hmmt_feb_2025.jsonl` | 30 | MIT |
| MATH-500 | `HuggingFaceH4/MATH-500` | `6e4ed1a2a79af7d8630a6b768ec859cb5af4d3be` | `test.jsonl` | 500 | Dataset card did not declare a license in the artifact manifest |

The builder reads answer/solution fields only from source rows when present,
then discards them. Written heldout rows contain prompt/source/hash metadata
only and exclude label-like keys such as `answer`, `solution`, `target`,
`expected_answer`, and `reference_solution`.

## V10 M0 Sidecar Input

M0 sidecar input dir:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`

M0 manifest:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/manifest.json`

M0 manifest sha256:
`ea1b64cbe92f93359f3aa2bdad84072f56dea68b08ffaa2fbe67789bcc5aba45`

Source dataset:
`AI-MO/NuminaMath-CoT`

Source revision:
`9d8d210c9f6a36c8f3cd84045668c9b7800ef517`

Selection strategy:
`hard_math_runlength_dp_v10_candidate_rows_only`

Rows scanned: `859494`

V9 recurrence rows observed: `221`

V10 candidate rows observed: `8`

Decontam-blocked V10 candidates: `0`

Files:

| Split | Path | Rows | sha256 |
| --- | --- | ---: | --- |
| train | `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/math_competition_numeric/train-split.jsonl` | 8 | `01ac5d1c8571dc956bbae12b7f1a00a4e759d59e503abbf2ddfba3b85aa324e3` |
| val | `/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar/math_competition_numeric/val-split.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Task242 Replacement Paths

Replacement path map:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/task242_replacement_paths.json`

Replacement map sha256:
`fb98b4196ab9efc99ed9765277546a6af14f6244cb4578fbecc056ca96cd45a1`

Replace task242 placeholder corpus:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/heldout/aime25_hmmt_math_heldout_decontam_corpus.jsonl`

Replace task242 placeholder M0 sidecar input:
`/work-agents/intern_nemotron_worker_1/outputs/task246_qwen_aime_v10_real_decontam_corpus_s1/m0_v10_math_sidecar`

The replaced task242 placeholder corpus was:
`/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/aime25_hmmt_math_heldout_decontam_corpus.PLACEHOLDER.jsonl`

The replaced task242 placeholder M0 input was:
`/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot/task241_v10_math_sidecar_m0_PENDING`

## Validation

Commands run:

```bash
PYTHONPATH=src python workspace/tasks/task246_qwen_aime_v10_real_decontam_corpus_s1/build_task246_artifacts.py
PYTHONPATH=src python - <<'PY'
# Independent validation loaded the heldout JSONL, checked label-like keys,
# discovered and converted M0 sidecar files through prepare_m1_agentic_sft.py,
# re-ran math decontamination on converted train rows, and checked exact AIME25
# prompt hits against sidecar train JSONL.
PY
```

Independent validation results:

- Heldout rows: `560`
- Unique prompt hashes: `560`
- Heldout label-key leaks: `0`
- M0 train rows discovered: `8`
- M0 val rows discovered: `0`
- Converted train rows: `8`
- Converted val rows: `0`
- M0 conversion errors: `0`
- Decontam dropped train rows: `0`
- Decontam blocker findings: `0`
- AIME25 prompt exact hits in sidecar train JSONL: `0`

## Contamination Status

- AIME25 prompts are heldout/decontamination material only.
- AIME25 labels are not written to heldout artifacts or M0 sidecar input.
- The M0 sidecar train rows are from NuminaMath-CoT, not AIME25/HMMT/MATH-500
  heldout source rows.
- No SFT packed shards, distillation prompts, eval outputs, or model artifacts
  were written by this task.
- The generated sidecar input was scanned against the heldout prompt corpus with
  n-gram size `8` and blocker threshold `0.5`.

## Residual Risk

- The real V10 sidecar input is sparse: only `8` V10 candidate rows were found
  in the fixed NuminaMath-CoT revision. Task248 or worker_2 should either set
  `--math-sidecar-max-records-per-env 8` / `--math-sidecar-max-val-shadow-per-env 0`
  for this pilot input, or treat the low sidecar count as a go/no-go limitation.
- MATH-500 was retained as prompt-only heldout material; its dataset-card license
  was not declared in the manifest. Legal/product policy should decide whether
  that source is acceptable for the final pilot gate.
- This task did not run training, eval, endpoint checks, or generated local data
  prep. It only provides corpus/input artifacts and validation evidence for the
  next prep task.
