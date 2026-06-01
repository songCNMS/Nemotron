# task244_qwen_aime_v10_contam_regression_review_s1 - Independent contamination and regression review

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Background

Qwen hard-math improvements are high risk because AIME25/HMMT-style prompts overlap with sources such as NuminaMath. Current code already enforces decontamination for V7/V8/V9. The new V10 work must be independently reviewed before any pilot result is trusted.

## Goal

Independently audit the V10 sidecar/planner/eval changes for contamination, regression risk, and protocol drift. This is a review task, not the implementation owner.

## Scope

- Review worker_1, worker_2, and worker_3 branches/PRs when available.
- Compare against task071/task075/task076 evidence, especially V7 pass, V8 `aime_06` regression, and V9 wrong modes.
- Confirm no AIME25 prompts, labels, or answer keys enter training sidecars, distillation prompts, packed train data, or run manifests except as held-out eval/decontam corpus.
- Confirm V10 does not weaken Qwen chat-template packing, data-quality checks, checkpoint-root normalization, or corrected evaluator semantics.
- Produce a review matrix with approve/request-changes/block recommendation for each upstream worker PR.

## Boundaries

- Do not modify product code.
- Do not run training, eval, or implementation tests unless explicitly assigned by lead as tester; this task is primarily independent review.
- Do not push `main`, self-merge, delete shared files, or alter worker branches.

## Expected Output

- Worker branch: `intern_nemotron_worker_4/task244_qwen_aime_v10_contam_regression_review_s1`.
- PR is optional if persistent review docs are useful; otherwise report through mailbox with a review artifact path.
- A contamination/regression matrix in this task directory covering data, planner, eval gate, artifact/runbook, and residual risk.
- Mailbox report with decision for each reviewed PR and exact blockers if any.

## Review Artifacts

- Initial independent review matrix: `workspace/tasks/task244_qwen_aime_v10_contam_regression_review_s1/review_matrix.md`.

## Acceptance Criteria

- Review explicitly checks AIME25/HMMT/MATH heldout decontamination.
- Review states whether the hard non-regression rule is enforceable from the proposed artifacts.
- Review flags any hidden 30B/8-GPU scale path that can bypass the 4B pilot gate.
- Review does not rely on lead-run tests.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Review inputs: worker_1 task241, worker_2 task242, worker_3 task243, worker_5 task245
