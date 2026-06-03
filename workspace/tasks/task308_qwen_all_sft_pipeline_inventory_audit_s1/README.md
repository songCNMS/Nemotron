# task308_qwen_all_sft_pipeline_inventory_audit_s1 - Qwen all-SFT pipeline and trainable data inventory audit

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_1,SESSION=89 -->

## Background

Coordinator requested a new gate-driven all-SFT pipeline review/run from current
`origin/main` after the 30B AIME V11 fail closeout. The original coordinator
baseline was `ecb14173a820df377270273b9f7d9d92cb5076d2`; current `origin/main`
is `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`, which lead verified as a
docs-only task310 task-doc commit. Treat `172cd0e7` as the branch base and
`ecb14173` as the product-code baseline unless newer product-code changes
appear.

- task300 accepted Qwen3-30B-A3B base AIME2025 score: `15/30 = 0.5`.
- task306 evaluated task301 FT checkpoint `iter_0000035` at `14/30 =
  0.4666666666666667`, below base.
- task307 approved the fail closeout only; no promotion/export/endpoint/further
  30B authorization came from that result.

This new work is an attempted full all-SFT pipeline, not a promotion claim.

## Goal

Audit the current main Qwen data-prep, packing, training, and eval stages and
produce the exact trainable all-eligible-SFT inventory for the next pipeline
attempt.

## Scope

- Inspect current `origin/main` `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`;
  product code is unchanged from `ecb14173a820df377270273b9f7d9d92cb5076d2`.
- Map current pipeline stages and entrypoints:
  - data prep and source registry;
  - packing / `packed_qwen` materialization;
  - training planner / launch scripts;
  - checkpoint load / canary route;
  - benchmark eval launchers and corrected Qwen evaluators.
- Inventory trainable SFT sources, including:
  - `stage1_sft` `data_blend_raw`;
  - task276 rematerialized V11 packed data;
  - task299 30B packed-data contract artifacts;
  - M1 agentic/math sidecars;
  - any other current-main eligible SFT data.
- Explicitly exclude:
  - held-out/eval/decontam rows;
  - AIME2025 prompts and labels;
  - task255 artifacts;
  - benchmark-only or leakage-risk sources.
- For each source, report path, revision/source id, split, row count,
  token/supervised-token count if available, checksum or manifest path,
  eligibility decision, and blocker if not eligible.
- Recommend the all-eligible-SFT blend plan for task309, or return an exact
  blocker.

## Boundaries

- Do not train, pack final data, run benchmark eval, export, launch endpoint, or
  claim promotion.
- Do not modify product/source code.
- Do not reuse task255.
- Do not use AIME2025 prompts or labels as training rows.
- Do not delete or mutate shared files, especially under
  `/mnt/cephfs/data/processing/lei.song`.
- Do not push main, merge, or direct any worker merge.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1`.
- Report:
  `workspace/tasks/task308_qwen_all_sft_pipeline_inventory_audit_s1/all_sft_pipeline_inventory_audit_report.md`.
- Artifact/output root with inventory tables, source manifests, commands/env,
  checksums, and blocker logs if any.
- Mailbox report with branch/head/PR or blocker, commands/env, exact source
  inventory, exclusion/decontam proof, recommended task309 input plan, and
  residual risks.

## Acceptance Criteria

- `PASS_AUDIT`: current pipeline stages and all trainable SFT sources are
  inventoried with counts, checksums/manifests, exclusions, blockers, and a
  concrete all-SFT blend recommendation.
- `REQUEST_CHANGES`: source inventory or exclusion proof is incomplete but
  likely repairable.
- `BLOCK`: the all-SFT inventory or pipeline route cannot be established without
  violating held-out/AIME/task255/shared-deletion boundaries.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Current main: `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`
- Product-code baseline: `ecb14173a820df377270273b9f7d9d92cb5076d2`
- Downstream tasks: task309, task310, task311, task312
- Gate state: no training starts until task308 and task309 produce acceptable
  evidence.
