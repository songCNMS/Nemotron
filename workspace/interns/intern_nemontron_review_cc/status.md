# intern_nemontron_review_cc - 状态

<!-- METADATA:STATUS=Working,TASK=task068_rlhf_toolcall_pairing_harness -->

| 字段 | 值 |
|------|-----|
| Name | intern_nemontron_review_cc |
| Status | Working |
| Current Task | task068_rlhf_toolcall_pairing_harness |
| PR | pending push |
| Session | 85 |

正在做：task068 Session 1 — design doc for the RLHF tool-call pairing
harness. No code; output is `task068_design.md` capturing the four
strategy parameters Session 2 will implement.

## What's in this PR

`workspace/tasks/task068_rlhf_toolcall_pairing_harness/task068_design.md`
(~440 lines) covering:

1. **Problem statement**: 7K HelpSteer-2 × 30K Hermes = 210M naïve
   pairs; need filters
2. **Relevance filter**: keyword heuristic ("look up", "find out",
   "compute", etc.) + Hermes prompt template match. Cheap +
   deterministic; ~30% pass rate expected
3. **Gold-call sourcing**: **function-name match heuristic** — Hermes
   row whose `function.name` appears in the HelpSteer-2 prompt; tie-
   break by required-arg name overlap. Rejected random-sample (noise)
   and LLM-zero-shot (feedback loop with judge model)
4. **Sampling cap K=1**: one paired row per HelpSteer-2 prompt
5. **Decontamination**: exclude prompts overlapping with BFCL /
   TauBench airline / MCP-Mark / HelpSteer1; reuse task030 Session 7's
   contamination_audit loader

Output corpus estimate: 7K HelpSteer-2 train → ~1,200 paired rows
after 83% drop across filters.

Doc also includes:
- 4 worked examples (clear match / no match / contaminated / kept)
- Reference output-row JSON shape
- Converter interface contract Session 2 will implement
- 3 open questions for product/lead alignment (K=1 vs K=3; future LLM
  gold-call mode; multilingual scope)

No code changes; no test changes (design-only PR). Sandbox baseline
unchanged at 620 passed + 7 skipped.

## task068 状态

- Session 1 ✓ (this PR) — design doc
- Session 2 ☐ — implement `transform_rlhf_toolcall_pairing` converter
  per the design (sandbox-runnable)
- Session 3 ☐ — flip RLHF env registry's tool-call row to active
- Session 4 ☐ — cluster smoke (needs task018 Session 3 judge service)

Roadmap §5b sandbox queue 更新.
