# task332_qwen_all_sft_structured_split_policy_remediation_s1 - task knowledge

<!-- METADATA:SESSION=83 -->

1. task329/#392 merged evidence shows valid/test splits are agentic-only; this
   is not accepted as an expanded all-SFT training contract.
2. task329 packing receipts show 6 `instruction-following-structured`
   validation-filtered rows; they require exact row-level disposition.
3. A positive task332 result still depends on task331 if SWE remains at zero
   supervised tokens.
4. Any later combined packed contract must be separately lead-gated before
   task310 training or benchmark eval.
5. Worker_4 branch for this task is
   `intern_nemotron_worker_4/task332_qwen_all_sft_structured_split_policy_remediation_s1`
   from `origin/main` `410c2247fc5e09e6ad831bdee1628830b97fbd89`.
6. The six structured rows failing task329 validation are row indices `3714`,
   `276`, `1702`, `2888`, `1579`, and `1566`, in shards `2`, `4`, `6`,
   `8`, `11`, and `14`. Each has `<tool_call>` content with no `# Tools`
   header and must stay fail-closed/excluded unless source data is repaired
   and revalidated.
7. `task332_per_source_shard_holdout_v1` assigns each included source by
   `row_index % 16`: remainder `14` to valid, remainder `15` to test, and
   all other remainders to train. This fixes sparse valid/test exposure as a
   deterministic policy for a later combined-contract task, not by mutating
   task329 artifacts.
8. Task331 is still pending at branch head
   `63b4b992d534bd16120f31345d57d105890d8d55`; visible diff is acceptance
   docs/status only and no PR is visible. SWE supervised tokens therefore
   remain the blocking dependency.
