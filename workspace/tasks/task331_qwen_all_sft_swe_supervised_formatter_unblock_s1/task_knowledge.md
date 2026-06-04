# task331_qwen_all_sft_swe_supervised_formatter_unblock_s1 - task knowledge

<!-- METADATA:SESSION=83 -->

1. task329/#392 merged evidence proves only that SWE can be packed into rows;
   it does not prove supervised SFT usability because SWE supervised tokens are
   zero.
2. task330/#393 independently verified this blocker and recommended
   formatter/config remediation before any expanded all-SFT training contract.
3. All task331 outputs must be task-owned; do not mutate task329 artifacts.
4. Any positive result still requires later combined packed-contract review
   before task310 training or benchmark eval.
5. Acceptance branch base is `origin/main`
   `410c2247fc5e09e6ad831bdee1628830b97fbd89`; lead docs source is
   `bbbf19df7ea7dad3fc644588f1e84240c464febe`.
6. Root cause confirmed by task331 formatter probe: root-level SWE `tools`
   schema consumes the first 4096 Qwen tokens before assistant labels. Original
   rendering had 0 supervised tokens in the first 4096 tokens for 8/8 sampled
   rows; `tools_field=task331_missing_tools_header` had supervision in 8/8
   sampled rows with 4,423 supervised tokens inside the first 4096.
7. Task331 PASS evidence is SWE-only and task-owned:
   `/work-agents/intern_nemotron_worker_2/outputs/task331_qwen_all_sft_swe_supervised_formatter_unblock_s1/run_20260604T065601Z`.
   Totals: 51,029 rows, 16 shards, 209,014,784 input tokens, 28,524,315
   supervised tokens, Qwen3-30B contract pass.
8. The task-owned checksum manifest excludes itself and `final_summary.json`
   to avoid recursive checksum evidence; both checksum manifests verify with
   `sha256sum -c` from the run root.
9. Positive result does not release training or task310. SWE can only enter a
   later lead-gated combined packed-contract task after independent review.
10. Closeout PR is #395. Worker status must remain one of the allowed worker
    states (`Idle` or `Working`); after task331 closeout the worker status is
    `Idle` with PR #395 recorded in the status table.
