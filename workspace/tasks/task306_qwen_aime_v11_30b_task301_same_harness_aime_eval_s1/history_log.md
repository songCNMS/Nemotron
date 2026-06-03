# task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1 - history log

<!-- METADATA:SESSION=1 -->

## Session 88 - 2026-06-02 UTC - assignment

- Created by `intern_nemotron_lead` after #367/task304 merged and worker_3
  final closeout mailbox `eb40f945d1134bb2be2fa8f82cb8b93a` was processed.
- Assigned to `intern_nemotron_worker_3`.
- Purpose: corrected AIME2025 same-harness FT-vs-base comparison for task301
  Qwen3-30B-A3B salvage checkpoint `iter_0000035`.
- Current main: `7a93a6cea16e45284a58287b91c0069b7416fa99`.
- Accepted base comparator: task300 Qwen3-30B-A3B base `15/30 = 0.5` with
  artifact root
  `/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T152008Z`.
- Required disposition: PASS only if FT corrected AIME exact-normalized score
  is `>= 15/30`; FAIL if below base; HOLD if same-harness proof or artifacts
  are incomplete; BLOCK if boundaries would be violated.
- Boundaries: no training, no AIME2025 train prompts/labels, no task255 reuse,
  no shared deletion, no promotion, no production endpoint, no direct main
  push/merge, and no export/endpoint unless the worker stops and reports a
  lead-authorized eval-only need.

## Session 1 - 2026-06-02 UTC - accepted by worker

- Accepted by `intern_nemotron_worker_3` on branch
  `intern_nemotron_worker_3/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1`
  from `origin/main` `7a93a6cea16e45284a58287b91c0069b7416fa99`.
- Imported task docs from
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  `a9c380e97f9d05fa3dc05a6f4977bbe7f3ce270a`.
- Initial plan: prove or fail same-harness equivalence against task300, prefer
  the no-export/no-endpoint task304 MCore route for task301 `iter_0000035`,
  and run or precisely block corrected AIME2025 FT-vs-base evaluation.
- Boundaries reaffirmed: no training/optimizer, no AIME train data, no task255,
  no shared deletion, no promotion, no production endpoint, no main push, no
  merge/self-merge, and no export/endpoint unless stopped for lead
  authorization.

## Session 1 - 2026-06-03 UTC - evaluation complete

- Added no-export/no-endpoint MCore static-engine corrected AIME2025 runner and
  executed the task301 Qwen3-30B-A3B `iter_0000035` checkpoint on NemTron with
  8x H200, `TP=4`, `PP=2`, `EP=4`, `ETP=1`, `CP=1`.
- Run root:
  `/work-agents/intern_nemotron_worker_3/outputs/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`;
  remote root:
  `/root/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/run_20260602T190432Z`.
- Remote return code: `0`.
- Result: `FAIL` versus accepted task300 base. FT exact-normalized AIME2025
  score was `14/30 = 0.4666666666666667` versus base `15/30 = 0.5`.
- Retained `30/30` results, full completions, and parser diagnostics. Parsed
  rows: `17/30`; finish reasons: `stop=17`, `length=13`.
- Protocol proof: same corrected AIME cache, same original prompts, same
  30-row all-request denominator, same parser/normalizer, same max tokens,
  prompt token mismatch count `0`. Residual:
  `sampling_exact_parameter_match=false` for no-export MCore greedy route
  versus task300 SGLang endpoint transport.
- Boundaries upheld: no training/optimizer, no AIME train data, no task255, no
  export/conversion, no endpoint, no promotion, no shared deletion, no main
  push, and no merge/self-merge.
