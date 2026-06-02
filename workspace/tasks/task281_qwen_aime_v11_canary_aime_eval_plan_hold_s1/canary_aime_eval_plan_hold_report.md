# task281 Qwen AIME V11 canary and AIME eval plan HOLD report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Summary

- Task: `task281_qwen_aime_v11_canary_aime_eval_plan_hold_s1`.
- Branch:
  `intern_nemotron_worker_3/task281_qwen_aime_v11_canary_aime_eval_plan_hold_s1`.
- Base reviewed: `origin/main` at
  `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`.
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `be45766c6fc127b0ba00e784d84810a378b3e8e4`.
- Disposition: `PLAN_READY_HOLD`.

This report defines the exact future non-AIME canary and corrected AIME2025
same-harness comparison plan for a future Qwen3-4B V11 FT artifact. It is
planning only. No canary, AIME/task243 eval, endpoint, training, export,
promotion, task255 reuse, AIME2025 train-data use, shared deletion, merge, main
push, or 30B/8-GPU action was run or authorized.

## Inputs Reviewed

- task264 canary/retention report:
  `workspace/tasks/task264_qwen_aime_v11_eval_gate_canary_retention_s1/v11_canary_retention_report.md`.
- task273 eval-gate continuity report:
  `workspace/tasks/task273_qwen_aime_v11_eval_gate_continuity_s1/eval_gate_continuity_report.md`.
- task272 post-Bridge readiness plan:
  `workspace/tasks/task272_qwen_aime_v11_post_bridge_pilot_plan_s1/post_bridge_pilot_readiness_plan.md`.
- task274 data safety readiness review:
  `workspace/tasks/task274_qwen_aime_v11_data_safety_ready_review_s1/data_safety_ready_review_report.md`.
- task275 Session 40 runbook update:
  `workspace/tasks/task275_qwen_aime_v11_session40_runbook_update_s1/session40_runbook_update_report.md`.
- task276 rematerialized packed Qwen report:
  `workspace/tasks/task276_qwen_aime_v11_rematerialize_packed_qwen_s1/v11_rematerialized_packed_qwen_report.md`.
- Gate config:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.yaml`
  sha256 `84eb36c62622aa8c6f83e65608f066492881f996c13eece4ba7b73b92733ae96`.
- Gate helper:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_aime2025_base_vs_ft_gate.py`
  sha256 `b84c8c87578b624675e19f6cb97eaf3f927c95ed51988c0372822f71606e67eb`.
- Canary prompt set:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`
  sha256 `150ee11dc6e8efd3c865a8e9ed8a9ab8ce4f5ee032bed383c73a6cea34f52f1c`.
- task276 PR #344 merged at `2026-06-02T04:19:38Z`, head
  `07efab4fa0d8367e96f54af3d2cdc70768d73595`, merge commit
  `793e7dfa73ed1c5bdc8b7b98df5f31ffdd5e38ea`.

## Current Gate State

| Surface | Current evidence | Plan state |
|---|---|---|
| Runtime import route | Session 40 proof recorded by task275; positive Bridge import/preflight markers exist | Runtime route blocker cleared for import/preflight only; not eval clearance |
| Fresh packed Qwen data | task276/#344 produced fresh packed root and evidence manifest | Packed artifact ready for review; not training/eval clearance |
| Future V11 FT candidate | No accepted FT checkpoint/export artifact exists in this task | Missing; canary and AIME must remain HOLD |
| Non-AIME canary | task264 static prompt set and decision rules exist | Plan ready; live canary not authorized |
| AIME comparator | task247/task273 accepted Qwen3-4B base `11/30` | Comparator fixed unless protocol changes |
| Promotion / 30B / 8-GPU | No FT score, no lead release | `NO-GO/HOLD` |

## Fixed Base Comparator

The canonical pilot comparator remains:

- Model and tokenizer path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
- Accepted base artifact root:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/qwen4b_base_aime2025_30x1_20260601T170700Z`.
- Input cache:
  `/work-agents/intern_nemotron_worker_3/outputs/task247_qwen_aime2025_qwen4b_base_smoke_s1/aime2025_input_cache/aime_score_cache.opencompass_a6ad95f.db`.
- Cache sha256:
  `c8b287d9784d1d4ae5d3ea593a70850aea69b289e3d42e05951c5488330eaf74`.
- Source dataset revision:
  `opencompass/AIME2025@a6ad95f611d72cf628a80b58bd0432ef6638f958`.
- Score: `11/30 = 0.36666666666666664`.
- Request status: `30/30 ok`.
- Parsed count: `23/30`.
- Finish reasons: `stop=21`, `length=9`.
- Base artifact hashes:
  `summary.json`
  `376f189c69a8b13fc7752f2f8c362a734154d43fe717209dedf6d0d1649d8639`,
  `results.jsonl`
  `c24ce2bd4b798b0f5913df1a86a34684315a6ac38e3b19764d0dd75889d43961`,
  `command.txt`
  `bd60cbb4b0ae65ba7cf549e5cde65142d55f9b2dc62181103e75657a937eff40`,
  and `endpoint_model_manifest.json`
  `4f17b1b5880e0cfc5697f99df942f31270e9ce5539212cc5494e9034c86ff354`.

If any future FT comparison changes the cache, runner, prompt variant,
endpoint route, response shape, parser, tokenizer template, sampling, or
denominator policy, the base must be rerun under that exact changed protocol
before the FT can be judged.

## Future Canary Launch Preconditions

Do not request or launch the non-AIME canary until all of the following are
true:

1. Lead explicitly releases a live canary task for a specific candidate.
2. A reviewer-readable Qwen3-4B V11 FT candidate exists with exact model path,
   model id, config/tokenizer files, checkpoint or export hashes, provenance,
   launch command, and manifest.
3. The candidate does not reuse task255/V10 failed artifacts.
4. The candidate was not trained with AIME2025 prompts or labels.
5. Data/artifact review for the exact candidate is not blocking.
6. The endpoint route and response shape are known to return
   `message.content`; a reasoning-content-only response is a canary failure.
7. The run can write to a task-owned output root without overwriting shared or
   historical artifacts.

## Non-AIME Canary Plan

Prompt source:

- File:
  `src/nemotron/recipes/super3/milestones/m1_eval_basket/qwen_v11_export_load_canary_prompts.yaml`.
- Prompt set id: `qwen_v11_non_aime_export_load_canary_v1`.
- Prompt count: 5.
- Prompt ids and expected answers:
  - `synthetic_arithmetic_sum_37_58`: `95`.
  - `synthetic_counting_pens_6_9`: `15`.
  - `synthetic_linear_expression_2x_plus_y`: `29`.
  - `synthetic_next_integer_246`: `247`.
  - `synthetic_word_completion_ready_set`: `go`.
- Source proof: synthetic prompts only, excludes AIME2025, excludes training
  rows, review-only and not trainable, no AIME2025 prompt or label text.

Generation contract:

- Endpoint type: OpenAI chat completions.
- Route: `/v1/chat/completions`.
- Tokenizer chat template: Qwen checkpoint tokenizer.
- Chat template kwargs: `enable_thinking=false`,
  `truncate_history_thinking=false`.
- `max_tokens=256`.
- `temperature=0.0`.
- `top_p=1e-5`.
- Response contract: concise coherent text plus a final-answer marker such as
  `Final Answer: ...` or `\boxed{...}`.

Required future canary artifact files:

- `canary_summary.json`.
- `canary_results.jsonl`.
- `canary_command.txt`.
- `canary_endpoint_model_manifest.json`.
- `canary_full_completions.jsonl`.
- `canary_completion_retention_manifest.json`.

Required canary row fields:

- `prompt_id`, `status`, `finish_reason`, `expected_answer`,
  `extracted_answer`, `correct`, `response_text_sha256`, `response_text_ref`,
  `response_chars`, `response_tail`, and `usage`.

Canary PASS requires all of the following:

- `5/5` prompt rows return `status=ok`.
- Every row has non-empty `message.content` or retained `response_text`.
- No row is reasoning-content-only.
- Every row has a short final-answer marker.
- Every extracted answer exactly matches the expected answer after simple
  normalization.
- No row has a mixed-script or code-token degeneration signature.
- No row is length-capped, errored, or missing completion token accounting.
- Full completions are retained as review-only evidence and marked not
  trainable data.

Canary FAIL conditions:

- Any prompt answer is incorrect or unparseable.
- Any row returns only reasoning content.
- Any row shows mixed-script/code-token degeneration.
- Any request errors, times out, or length-caps.

Canary HOLD conditions:

- Candidate artifact, endpoint route, manifest, or lead release is missing.
- Output retention cannot be written safely.
- The canary prompt source differs from the task264 prompt set without an
  approved replacement.

## Future Corrected AIME2025 Plan

Do not request or launch AIME/task243 until:

1. The exact candidate has a passing non-AIME canary under the plan above.
2. The canary outputs and candidate manifest are reviewer-readable.
3. Lead explicitly releases live corrected AIME2025 evaluation.
4. No task265/task274-style data, contamination, artifact, or provenance review
   is blocking the exact candidate.
5. The run can use the accepted task247 cache and the same task243/task264
   corrected harness, or else a same-protocol base rerun is planned first.

Pilot command template for a future released task only:

```bash
python3 /root/<future_task>/eval/run_corrected_math_full_eval.py \
  --aime-score-cache /root/task247_qwen_aime2025_qwen4b_base_smoke_s1/input/aime_score_cache.opencompass_a6ad95f.db \
  --hmmt-output-jsonl /root/<future_task>/input/not_used_hmmt.jsonl \
  --output-dir /root/<future_task>/eval/<candidate_ft_aime2025_30x1> \
  --endpoint-url http://127.0.0.1:<port>/v1/chat/completions \
  --model-id <served-v11-ft-model-id> \
  --tasks aime25 \
  --aime-prompt-variant original \
  --aime-max-tokens 8192 \
  --aime-limit-rows 30 \
  --parallelism 4 \
  --timeout 900
```

Required AIME protocol:

- AIME2025 `30 x 1` pilot, one request per problem.
- Original prompt variant.
- OpenAI chat completions route `/v1/chat/completions`.
- Qwen checkpoint tokenizer chat template with `enable_thinking=false` and
  `truncate_history_thinking=false`.
- `max_tokens=8192`.
- `temperature=0.0`.
- `top_p=1e-5`.
- Parser: boxed-answer or symbolic-final-answer parser.
- Scorer: exact-normalized boxed or symbolic answer match.
- Denominator: all request rows, including unparsed, length-capped, errored,
  and timeout rows.

Required AIME artifact files:

- `summary.json`.
- `results.jsonl`.
- `command.txt`.
- `endpoint_model_manifest.json`.
- `full_completions.jsonl`.
- `completion_retention_manifest.json`.
- `base_vs_ft_gate_decision.json`.
- `base_vs_ft_gate_report.md`.

Required AIME metrics:

- numerator;
- denominator;
- exact-normalized accuracy;
- parsed count and parsed rate;
- status counts;
- finish reason counts;
- per-problem rows with `rows`, `correct_rows`, `parsed_rows`,
  `finish_reason_counts`, and `sample_ids`;
- completion token summary;
- artifact hashes for required files.

Decision rules:

- `PASS` for pilot non-regression only if FT exact-normalized score is
  `>= 11/30 = 0.36666666666666664` under the same harness and no upstream gate
  is blocking.
- `FAIL` if FT exact-normalized score is lower than `11/30`.
- `HOLD/BLOCK` if the canary, candidate artifact, endpoint shape, retention
  schema, base parity, or lead release is missing.
- Parsed rate is diagnostic only; it cannot override exact-normalized
  all-request accuracy.
- A full `30 x 10` AIME protocol, promotion, or scale-up requires a separate
  lead gate after pilot evidence exists.

## Current Blockers To Live Evaluation

- No accepted Qwen3-4B V11 FT candidate checkpoint/export exists.
- No lead release for live canary or AIME/task243 eval exists.
- No candidate endpoint, launch command, or model manifest exists.
- No candidate canary pass artifacts exist.
- No same-harness V11 FT AIME artifact exists.
- task276 packed data is merged as evidence but remains a data artifact; it is
  not a candidate model and does not authorize training or eval.

## Stale Or Non-Reusable Inputs

- task255/V10 FT artifact is failed evidence only: task257 scored `0/30`
  below accepted base `11/30`, and task260/task261 attribute the failure to
  generation corruption and likely load/training defects.
- task253 packed Qwen root is stale for V11 training readiness: task274 records
  old train split mismatch of 15 intended shards versus 8 exposed shards.
- Any mailbox-only, local, or unmerged artifact without exact path, hashes, and
  reviewer-readable provenance is not sufficient for the canary or AIME gate.

## Checks

- Current report is docs/status only.
- `sha256sum` verified the current gate config, canary prompt file, and gate
  helper hashes listed above.
- `git diff --check`: passed.
- ASCII scan over task281 docs and worker_3 status: passed.

## Boundary Confirmation

- No live canary was run.
- No AIME/task243 eval was run.
- No endpoint was launched.
- No training, nonzero-LR smoke, export, or model modification was run.
- No promotion or go/no-go pass is claimed.
- No task255 artifact was reused.
- No AIME2025 prompt or label was used as trainable data.
- No shared deletion or overwrite was performed.
- No merge, main push, or 30B/8-GPU action was performed.
