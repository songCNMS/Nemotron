# task028_m2_long_context_s1 - M2 Long-Context Session 1 Scaffold

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_1 -->

## Background

M2 expands long-context coverage beyond the existing M0
`long_context_qa_smoke` path toward RULER 512K / 1M, AA-LCR, and
long-document QA.

## Goal

Add sandbox-runnable record contracts, environment-registry rows, and a
small span-aware `long_context_qa` verifier scaffold.

## Acceptance

- RULER / AA-LCR / long-doc QA scaffold environments exist.
- Converter emits NeMo-Gym-style records from small synthetic rows.
- `long_context_qa` verifies answer match plus evidence-span match when
  spans are provided.
- Full 512K / 1M execution, benchmark source pins, and cluster runs stay
  explicit follow-ups.
