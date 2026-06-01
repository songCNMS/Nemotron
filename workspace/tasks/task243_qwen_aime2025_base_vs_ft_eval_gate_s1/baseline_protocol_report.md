# task243 baseline protocol report

<!-- METADATA:STATUS=Draft,ASSIGNEE=intern_nemotron_worker_3,SESSION=1 -->

## Summary

The corrected AIME2025 base-vs-FT gate requires a same-harness base score
before any fine-tuned Qwen checkpoint can be judged. The gate must compare
exact-normalized AIME2025 accuracy, not parsed rate or finish-rate proxies.

No live base score was produced in Session 1. The implementation is ready to
score and compare artifacts once a Qwen3-4B base endpoint and matching FT
endpoint are available under the same corrected protocol.

Session 1 read-only probe result: base score is currently blocked in this
worktree because the configured Qwen3-4B base checkpoint path is missing, the
corrected AIME score-cache input is missing, and no local Qwen chat endpoint is
listening on the checked ports.

## Base Checkpoint

- Model id: `Qwen/Qwen3-4B-Instruct-2507`
- Base checkpoint path:
  `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`
- Tokenizer/chat template path:
  `/mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507`
- Chat template kwargs:
  `enable_thinking=false`, `truncate_history_thinking=false`

## Pilot Smoke Protocol

- Benchmark: AIME 2025
- Scope: 30 AIME 2025 problems x 1 repeat
- Endpoint route: `/v1/chat/completions`
- Prompt set: corrected AIME2025 original prompts
- Max tokens: `8192`
- Sampling: `temperature=0.0`, `top_p=1e-5`
- Parser: boxed answer or symbolic final-answer parser
- Scorer: exact-normalized boxed/symbolic answer match
- Denominator: all request rows, including unparsed, length-capped, and error
  rows
- Gate: a FT pilot can proceed only if FT exact-normalized accuracy is greater
  than or equal to the base pilot score under this same protocol.

## Final Full Protocol

- Benchmark: AIME 2025
- Scope: 30 AIME 2025 problems x 10 repeats, 300 request rows
- Endpoint route: `/v1/chat/completions`
- Prompt set: corrected AIME2025 original prompts
- Max tokens: `8192`
- Sampling: `temperature=0.0`, `top_p=1e-5`
- Parser: boxed answer or symbolic final-answer parser
- Scorer: exact-normalized boxed/symbolic answer match
- Denominator: all request rows, including unparsed, length-capped, and error
  rows
- Gate: FT full AIME2025 promotion fails if FT exact-normalized accuracy is
  lower than the same-harness base score.

## Score Normalization Schema

For each base or FT run, persist:

- `numerator`: exact-normalized correct request rows
- `denominator`: all request rows
- `exact_normalized_accuracy`: `numerator / denominator`
- `parsed_count` and `parsed_rate`
- `finish_reason_counts`
- `status_counts`
- `per_problem_rows`: problem id to rows, correct rows, parsed rows, finish
  reasons, and sample ids
- `artifact_paths`: at minimum `summary.json`, `results.jsonl`, `command.txt`,
  and endpoint model manifest

Parsed rate and finish reasons are diagnostics only. A shorter FT output that
parses more often still fails if exact-normalized accuracy is lower than base.

## Required Artifact Paths

Base run:

- `<base_output_dir>/summary.json`
- `<base_output_dir>/results.jsonl`
- `<base_output_dir>/command.txt`
- `<base_output_dir>/endpoint_model_manifest.json`

FT run:

- `<ft_output_dir>/summary.json`
- `<ft_output_dir>/results.jsonl`
- `<ft_output_dir>/command.txt`
- `<ft_output_dir>/endpoint_model_manifest.json`

Comparison output:

- `<comparison_output_dir>/base_vs_ft_gate_decision.json`
- `<comparison_output_dir>/base_vs_ft_gate_report.md`

## Verification Command Shape

Use the corrected runner equivalent to:

```bash
PYTHONPATH=src /work-agents/.venv/bin/python \
  workspace/tasks/task071_m1_agentic_qwen_scaleup_train_exec/run_corrected_math_full_eval.py \
  --aime-score-cache <corrected_aime_score_cache.db> \
  --hmmt-output-jsonl <hmmt_output.jsonl> \
  --output-dir <base_or_ft_output_dir> \
  --endpoint-url http://127.0.0.1:13000/v1/chat/completions \
  --model-id <served-model-id> \
  --tasks aime25 \
  --aime-prompt-variant original \
  --aime-max-tokens 8192 \
  --aime-limit-rows 30 \
  --parallelism 4 \
  --timeout 900
```

For the final full protocol, omit `--aime-limit-rows 30` or use an equivalent
300-row corrected AIME25 run with 10 repeats per problem. The same command
shape, prompt set, max tokens, sampling policy, parser, and scorer must be used
for both base and FT.

## Session 1 Read-Only Probe Evidence

Commands run from this worker branch:

```bash
test -d /mnt/3fs/data/lei.song/models/Qwen/Qwen3-4B-Instruct-2507
test -f /work-agents/intern_nemontron_code_reading/debug/task071_eval_logic_debug/math_artifact_audit_session36/aime_score_cache.db
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:13000/v1/models
curl -sS --connect-timeout 2 --max-time 4 http://127.0.0.1:30001/v1/models
```

Observed:

- `base_path=missing`
- `aime_score_cache=missing`
- `127.0.0.1:13000`: connection refused
- `127.0.0.1:30001`: connection refused

Current blocker to first base score:

- Need a reachable Qwen3-4B base endpoint using the checkpoint/tokenizer above
  or an approved corrected replacement path.
- Need the corrected AIME2025 score-cache/input artifact visible to this worker
  or a PM-provided equivalent path.
- Once those are available, run the pilot smoke command above for the base
  model first, persist the required base artifacts, then run the identical
  command shape for FT. Do not judge FT until the base artifacts exist.
