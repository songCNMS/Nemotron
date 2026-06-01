# task249_qwen_aime_v10_live_contam_gate_review_s1 - Live gate review

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Background

task244 completed the static contamination/regression review. The next risk is
runtime evidence: real decontam corpus/input, Qwen3-4B base artifacts, pilot
data/training artifacts, FT evaluation artifacts, and the final base-vs-FT gate
decision.

## Goal

Independently review the live evidence from task246, task247, task248, and
task250, and provide approve/request-changes/block decisions for first
Qwen3-4B V10 go/no-go readiness.

## Scope

- Review only; do not modify product code.
- Inspect artifact paths, manifests, hashes, counts, logs, and comparison
  reports.
- Confirm no AIME25/HMMT/MATH heldout prompt or label leakage into trainable
  artifacts.
- Confirm same-harness base and FT protocol match exactly before any FT
  non-regression claim.
- Confirm 30B/8-GPU scale remains held until the Qwen3-4B gate passes and lead
  explicitly grants permission.

## Boundaries

- Do not train, launch eval, start endpoints, merge, push `main`, or rewrite
  worker branches.
- Do not delete shared files.
- Treat missing or indirect evidence as HOLD, not approve.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task249_qwen_aime_v10_live_contam_gate_review_s1`.
- PR to `main` with review artifact if appropriate.
- Task report in this directory named `live_gate_review_matrix.md`.
- Mailbox report with decision per upstream task: task246, task247, task248,
  task250, and the combined go/no-go.

## Acceptance Criteria

- Each runtime evidence surface has a concrete approve/request-changes/block
  disposition.
- The first go/no-go cannot pass unless FT exact-normalized AIME25 accuracy is
  at least the same-harness Qwen3-4B base accuracy.
- Any contamination, protocol mismatch, missing artifact, or stale path keeps
  the gate on HOLD.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Depends on: task244, task246, task247, task248, task250
- First gate: no lead approval of first Qwen3-4B pilot result without this
  independent review.
