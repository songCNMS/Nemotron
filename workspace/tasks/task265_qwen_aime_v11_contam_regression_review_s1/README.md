# task265_qwen_aime_v11_contam_regression_review_s1 - V11 contamination and regression review

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_4,SESSION=0 -->

## Background

V11 work restarts after task255 failed below base. The next attempt must repair
data/packing, base-load proof, planner schedule, and eval preflight without
weakening the hard rule that AIME2025 is held out and FT must not score below
the same base under the same corrected evaluator.

## Goal

Independently review the V11 task262/task263/task264 surfaces for contamination,
regression, and gate drift before any new Qwen3-4B training/eval clearance.

## Scope

- Start from current `origin/main` after #333 merge commit
  `513fefa1f1ace94302b56413769c78fb7224624c`.
- Review task262 data/packing plan or PR when available:
  - no AIME2025 prompt/label train leakage;
  - decontam corpus and heldout handling;
  - dataset-qualified split materialization and manifest assertions.
- Review task263 planner/base-load plan or PR when available:
  - real Qwen3-4B base-load/import proof;
  - fail-closed random-init/zero-LR checks;
  - no raw-HF-as-Megatron-root silent path.
- Review task264 eval/canary plan or PR when available:
  - canary prompts are non-AIME and not train rows;
  - same-harness base-vs-FT rule remains enforceable;
  - artifact retention does not expose heldout labels to training.
- Produce an approve/request-changes/block matrix. If upstream branches are not
  visible yet, record acceptance and wait for exact branch/head evidence.

## Boundaries

- Read-only review unless lead later explicitly assigns a narrow docs update.
- Do not train, eval, export, launch endpoints, merge, or alter worker branches.
- Do not use or disclose AIME2025 labels beyond heldout gate review.
- Do not clear promotion, task243 comparison, or 30B/8-GPU.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_4/task265_qwen_aime_v11_contam_regression_review_s1`.
- PR only if review docs are committed; mailbox-only interim review is allowed
  while upstream branches are not ready.
- Task-owned output root:
  `/work-agents/intern_nemotron_worker_4/outputs/task265_qwen_aime_v11_contam_regression_review_s1/`.
- Review matrix with:
  - upstream task/branch/head/PR reviewed;
  - contamination verdict;
  - regression/gate verdict;
  - exact commands or read-only checks used;
  - approve/request-changes/block recommendation;
  - residual risks and unreviewed surfaces.

## Acceptance Criteria

- PASS: independent matrix confirms no AIME2025 train leakage and no weakening
  of base-vs-FT non-regression gate for the exact reviewed heads.
- REQUEST-CHANGES/BLOCK: any contamination risk, stale upstream head, missing
  base-load proof, missing split assertion, or canary/gate drift is documented
  with owner and remediation.
- This task cannot authorize training or eval by itself; it is a lead gate input.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_4`
- Related tasks: task262, task263, task264, task260, task261
- First gate: independent contamination/regression matrix for visible V11 heads
  or exact blocker.
