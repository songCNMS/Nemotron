# task311 closeout independent review report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=79 -->

Generated: 2026-06-03T19:18:00Z

## Disposition

Recommendation: `APPROVE_DOCS_CLOSEOUT`.

I reviewed #371/task311 at exact head
`9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`. The PR is acceptable to merge as
evidence/fail-closeout documentation only, consistent with lead gate comments
`4615730412` and `4615769907`.

This is not promotion evidence. It does not authorize training, additional
eval, export, endpoint, production serving, task255 reuse, AIME2025 train data,
shared deletion, main push, self-merge, or worker_4 merge of #371.

## PR and Comment Checks

| Item | Result |
|---|---|
| PR | #371 |
| Exact head reviewed | `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6` |
| State | `OPEN`, base `main`, non-draft, `CLEAN/MERGEABLE` |
| Lead comment `4615730412` | `APPROVE_EVIDENCE_CLOSEOUT / PERFORMANCE_FAIL_MIXED` at `2e4482ea` |
| Lead comment `4615769907` | carries approval to current head `9361e6da` after bookkeeping-only drift |
| Worker review PR | #378 |
| Worker_4 decision | `APPROVE_DOCS_CLOSEOUT` with residuals |

Current #371 diff versus `origin/main` contains worker_3 status, task311 docs,
and task-owned task311 scripts only. No product-code files are modified.

## Drift Review

The required drift range
`2e4482ea75e0b5f0223d70b0e4dfcce9388b2de9..9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`
changes only:

- `workspace/interns/intern_nemotron_worker_3/status.md`
- `workspace/tasks/task311_qwen_all_sft_benchmark_eval_s1/history_log.md`
- `workspace/tasks/task311_qwen_all_sft_benchmark_eval_s1/task_knowledge.md`

`git diff --check` for the drift range passed. The task-owned runners are
unchanged across the drift:

- `run_30b_no_export_canary_probe.py` sha:
  `4708b79b97ddefefb85a37839a724eac2ce90118feaff700e657e1cba260b2bb`
- `run_task311_endpoint_benchmark.py` sha:
  `11c080291abb9f1ce06edbe09e3371d61643e76159bb29090133b1503aca8b15`

## Canary Evidence

Reviewed artifact root:

`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z`

Observed canary status:

- `PASS_NON_AIME_CANARY_ONLY`
- 5 prompts requested, 5 completions retained, 5 non-empty responses
- 5 exact expected-answer matches
- empty, mixed-script, and degeneration counts all `0`
- no export and no endpoint route
- checkpoint-load manifest rank0 records load pass for task310 `iter_0000035`

Key hashes matched the task311 report:

- canary summary:
  `5da06d50f23bd581d2de5988f999cc4a2d7bb162f487afef1033c29810ce93b5`
- canary decision:
  `7678a8f8f3445882a1e5ea575169d37aae7f7ad9ead14b4f5d788fa5c5cb3ba5`
- full completions:
  `fd86644308d690340545be0fb308912dac87ddd8c3b499e2af4556635c3409f7`
- prompt manifest:
  `3838d39a779bd28df90ced9a1f9ba99f61bdb3dd747083450be0334cdf52c0b2`
- checksum manifest:
  `cc0f2be1d99e4b1caad4e5eb4e4e7d6f6a3bf99be2d28ff0c9e9b2beb23307d4`

The canary checksum manifest is JSON, not `sha256sum -c` text. I verified its
listed artifact entries with `jq` plus `sha256sum`; all checked entries passed.

## Corrected-Qwen Benchmark Evidence

Reviewed artifact root:

`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z`

The consolidated summary hash matches:

`67998f32982ccf15be7d7eeec55827ec1d5edf658a41ba494d6cb7899e6da828`

Metrics independently read from `session12_benchmark_summary.json` and per-run
`summary.json` files:

| Benchmark | Base | FT | Delta | Disposition |
|---|---:|---:|---:|---|
| AIME2025 | accepted task300 `15/30 = 0.5` | `16/30 = 0.5333333333333333` | `+1` | `PASS_VS_BASE` |
| HMMT Feb 2025 | `9/30 = 0.3` | `11/30 = 0.36666666666666664` | `+2` | `PASS_VS_BASE` |
| MMLU-Pro test | `6758/12032 = 0.5616688829787234` | `6756/12032 = 0.5615026595744681` | `-2` | `FAIL_VS_BASE` |

Summary hashes matched:

- AIME25 FT:
  `d19713736d34a102ceb8af5aa35d3c05e822d469810f7f63743295ddae21ae47`
- HMMT base:
  `1466e9d29528bb6fbbc4c8b781e9043d1a0239d458e34059fb24fa9616f68843`
- HMMT FT:
  `a4ec85ca9582fc84d135aae4c6db9a3aae40741112be385537bd9cc612c1e94c`
- MMLU-Pro base:
  `fe2247bd2a861f8c327f652211b8d7b52b4ec8a4f4115242cbb839e72975a917`
- MMLU-Pro FT:
  `0d6b12f55e350584fa9f198273173292060bdcef1da3998618eaca354f8d0108`

Protocol checks:

- Endpoint route is eval-only SGLang `/v1/chat/completions`.
- Sampling is `temperature=0.0`, `top_p=1e-5`.
- AIME/HMMT denominator is all 30 requested rows with max tokens `8192`.
- MMLU-Pro denominator is all 12032 requested rows with max tokens `64`.
- HMMT and MMLU-Pro base were rerun under the same endpoint route before FT
  comparison.
- AIME2025 FT reuses accepted task300 base per the report's same-harness
  rationale.

## Export and Endpoint Cleanup

Remote HF export exists with 26 files. The full remote HF export checksum
manifest passed on NemTron. The local copied export root contains only 7 small
metadata/tokenizer/index files, so the full export payload must be verified on
the remote root.

Live read-only endpoint cleanup probe on NemTron at `2026-06-03T19:07:36Z`:

- `port_13231=free`
- no live `sglang.launch_server` match beyond the probe command itself
- all eight H200s reported `1 MiB` memory used and `0%` utilization

## M1 Launcher Blocker

The M1 launcher blocker is still valid:

- local worker environment lacks `nemo-evaluator-launcher`, `nemo-evaluator`,
  and Python modules `nemo_evaluator`, `lm_eval`, `simple_evals`,
  `nemo_skills`, `bfcl_eval`, `tau2_bench`;
- NemTron lacks `nemo-evaluator-launcher`, `nemo-evaluator`, Docker, Slurm, and
  the same benchmark modules;
- corrected-Qwen AIME/HMMT/MMLU-Pro rows were not M1 launcher runs;
- remaining launcher rows stay
  `BLOCK_LAUNCHER_RUNTIME_MISSING_FOR_REMAINING_M1_ROWS`.

## Residuals

1. Overall performance is mixed/failing for promotion: AIME2025 and HMMT pass
   versus base, but MMLU-Pro is below base by 2 rows.
2. AIME/HMMT have length-finish residuals at 8192 max tokens.
3. Corrected benchmark JSON checksum manifests contain stale `logs/run.log`
   entries. The result-bearing files (`summary.json`, `results.jsonl`,
   `full_completions.jsonl`, `parser_diagnostics.jsonl`, command/env manifests,
   endpoint manifests, and row manifests) all matched their JSON manifest
   hashes. The stale run-log hashes should be carried as a docs-closeout
   residual, not as promotion evidence.
4. The full HF export payload is present and hash-verified on the remote root;
   the local copied root is partial.
5. No M1 launcher rows are validly complete because the launcher runtime is
   missing.

## Commands

Representative read-only commands:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs +pull/371/head:refs/remotes/origin/pr/371
gh pr view 371 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url
gh api repos/songCNMS/Nemotron/issues/comments/4615730412
gh api repos/songCNMS/Nemotron/issues/comments/4615769907
git diff --name-status 2e4482ea75e0b5f0223d70b0e4dfcce9388b2de9..9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6
git diff --check 2e4482ea75e0b5f0223d70b0e4dfcce9388b2de9..9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6
git diff --name-status origin/main...origin/pr/371
sha256sum <reported canary and benchmark summary artifacts>
jq <canary, corrected benchmark, and session12 summary JSON>
ssh NemTron '<read-only port/process/GPU cleanup probe>'
ssh NemTron '<read-only HF export checksum verification>'
```

No training, eval rerun, export, endpoint launch, promotion, task255 reuse,
AIME2025 train data, shared deletion, main push, merge, self-merge, or worker
branch rewrite was performed.
