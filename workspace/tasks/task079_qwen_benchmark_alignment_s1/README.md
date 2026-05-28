# task079_qwen_benchmark_alignment_s1 - Qwen benchmark alignment ledger

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Background

task072 added a Qwen-first eval reproduction gate, but the repo still needs a
single local ledger that ties countable benchmark-improvement evidence back to
the exact M1/M2 gate suites and corrected AIME25/HMMT/MMLU-Pro protocols.

PM audit context:

- task075/task076 evidence is still in open PR context and is not all present on
  main.
- Legacy launcher metrics for MMLU-Pro, AIME25, and HMMT can be completions-only,
  short-generation capped, or parser-misaligned.
- Missing raw artifacts or missing baseline/current deltas must block a run from
  being counted as benchmark improvement evidence.

## Goals

- Add a repo-local benchmark alignment ledger for M1/M2 gate target suites.
- Record the corrected Qwen evidence protocol for MMLU-Pro, AIME25, and HMMT:
  route, endpoint/model path, parser/final-answer format, max tokens, raw
  artifact paths, and baseline/current deltas.
- Keep task075/task076 sidecar and smoke evidence as context-only until merged,
  artifact-checked, and promoted through the corrected gate protocol.
- Add validators and tests that reject completions-only, short-cap,
  parser-misaligned, or missing-raw-artifact evidence.

## Acceptance

- Focused pytest covers qwen gate, M1 basket, M1 full basket, M2 basket, and eval
  chat-template contract.
- `python -m py_compile` passes for touched Python modules.
- `git diff --check` passes.
- Branch is pushed and PR is opened against `main`.
