# task264 V11 canary and retention gate report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Summary

- Task: `task264_qwen_aime_v11_eval_gate_canary_retention_s1`
- Branch:
  `intern_nemotron_worker_3/task264_qwen_aime_v11_eval_gate_canary_retention_s1`
- PR: pending at report-authoring time
- Base commit: `origin/main` at
  `513fefa1f1ace94302b56413769c78fb7224624c`
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `81253415dd3285ce0eb56e69733d210742edcb50`
- Disposition: V11 pre-AIME canary, artifact retention, and same-harness gate
  readiness are implemented statically. No live AIME/task243 eval was run.

## Accepted Base Comparator

- Base model:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`
- Accepted base score: `11/30 = 0.36666666666666664`
- Protocol: corrected AIME25 `30x1`, original prompt, `/v1/chat/completions`,
  max tokens `8192`, temperature `0.0`, top_p `1e-5`, exact-normalized
  all-request denominator.
- Gate rule remains unchanged: future FT exact-normalized AIME25 score must be
  at least the accepted same-harness base before any pass can be claimed.

## Files Changed

- `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`
  - New synthetic non-AIME canary prompt set.
  - sha256:
    `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`
- `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.yaml`
  - Adds required `v11_pre_aime_export_load_canary` and
    `v11_artifact_retention_schema`.
  - sha256:
    `84eb36c62622aa8c6f83e65608f066492881f996c13eece4ba7b73b92733ae96`
- `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.py`
  - Adds prompt-set validation, retention schema validation, and offline
    canary row decision logic. Adds a V11 wrapper that blocks same-harness AIME
    judgment when canary evidence is missing or failed.
  - sha256:
    `b84c8c87578b624675e19f6cb97eaf3f927c95ed51988c0372822f71606e67eb`
- `tests/recipes/super3/test_qwen_aime2025_base_vs_ft_gate.py`
  - Adds task264-focused tests.
  - sha256:
    `3b1775434ec8acf9adc3f62d83dd22e2b57d30cd85f6fe4f9b732081b546fccd`

## Canary Source

- Prompt set id: `qwen_v11_non_aime_export_load_canary_v1`
- Prompt count: 5
- Prompt ids and expected answers:
  - `synthetic_arithmetic_sum_37_58`: `95`
  - `synthetic_counting_pens_6_9`: `15`
  - `synthetic_linear_expression_2x_plus_y`: `29`
  - `synthetic_next_integer_246`: `247`
  - `synthetic_word_completion_ready_set`: `go`
- Source confirmation:
  - synthetic prompts only;
  - excludes AIME2025;
  - excludes training rows;
  - review-only, not trainable;
  - no AIME2025 prompt or label text in any canary prompt body.
- Generation contract:
  - endpoint: OpenAI chat completions;
  - route: `/v1/chat/completions`;
  - Qwen tokenizer chat template;
  - `enable_thinking=false`;
  - `truncate_history_thinking=false`;
  - max tokens `256`;
  - temperature `0.0`;
  - top_p `1e-5`.

Future V11 FT artifacts must pass this canary before an AIME/task243 comparison
is requested. The canary decision helper requires every prompt row to return
`status=ok`, non-empty `message.content`/`response_text`, a short final-answer
marker, matching extracted final answer, valid completion token accounting, and
no mixed-script/code-token degeneration signature.

## Retention Schema

Future V11 AIME eval artifacts must retain enough deterministic evidence to
distinguish parser failures from generation corruption.

Required files:

- `summary.json`
- `results.jsonl`
- `command.txt`
- `endpoint_model_manifest.json`
- `full_completions.jsonl`
- `completion_retention_manifest.json`

Required `results.jsonl` fields now include:

- row identity and scoring fields: `sample_id`, `task`, `status`,
  `finish_reason`, `parsed`, `correct`, `prediction`, `boxed_values`, `usage`;
- retention fields: `response_chars`, `response_tail`, `response_text_sha256`,
  `response_text_ref`.

Required `full_completions.jsonl` fields:

- `sample_id`, `task`, `model_id`, `prompt_sha256`, `response_text`,
  `response_text_sha256`, `finish_reason`, `usage`.

Required retention manifest fields:

- `schema_version`, `retention_policy`, `review_only_not_trainable`,
  `artifact_sha256`, `prompt_set_id`, `model_id`, `model_path`,
  `endpoint_route`, `generation_config`.

The schema states that retained completions/debug transcripts are eval evidence
for review only and must not become trainable AIME2025 data.

## Checks

- `git diff --check`: passed.
- `python3 -m py_compile src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.py`:
  passed.
- `PYTHONPATH=src pytest -q tests/recipes/super3/test_qwen_aime2025_base_vs_ft_gate.py`:
  `13 passed`.
- Non-ASCII scan over changed source/docs:
  no matches.

An initial `pytest` invocation without `PYTHONPATH=src` failed to import the
local `nemotron` package; the corrected focused command above passed.

## Boundary Confirmation

- No live AIME/task243 eval was run.
- No endpoint was launched.
- No training or export was run.
- No promotion or go/no-go pass is claimed.
- No 30B/8-GPU work was launched.
- No AIME2025 prompt/label text was added to trainable artifacts.
- No existing artifact was modified.
- Global Qwen AIME gate remains `NO-GO/HOLD`.
