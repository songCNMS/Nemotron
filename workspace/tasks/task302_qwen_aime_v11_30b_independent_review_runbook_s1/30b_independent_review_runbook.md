# task302 30B independent review runbook

<!-- METADATA:STATUS=Hold,ASSIGNEE=intern_nemotron_worker_4,SESSION=3 -->

## Decision

- Overall disposition: `HOLD_REQUEST_CHANGES_MISSING_UPSTREAM_ARTIFACT_EVIDENCE`
- Current branch:
  `intern_nemotron_worker_4/task302_qwen_aime_v11_30b_independent_review_runbook_s1`
- Base main:
  `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  exact requested commit `676d8556`

No 30B gate is approved. Current visibility now includes exact upstream branch
heads for task298-task300 and task301 PR #362, but the required official
artifact-root, command/env, log, checksum, metric, and residual evidence is not
complete enough for any gate approval.

## Initial Visibility Scan

Commands:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rev-parse origin/main
git rev-parse origin/intern_nemotron_lead/session1-recovery-task-docs
git cat-file -t 676d8556
gh pr list --state all --search "task298 OR task299 OR task300 OR task301" --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,isDraft,title,url --limit 20
git ls-remote --heads origin '*task298*' '*task299*' '*task300*' '*task301*'
```

Observed:

- `origin/main` is
  `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`.
- The exact requested lead docs commit `676d8556` exists locally.
- Current lead docs branch has advanced to
  `be6bcc9baa7901ad898cb62e4d3add3dd5945c27`; task302 docs for this branch
  were pinned to the requested `676d8556`.
- GitHub PR search returned `[]` for task298-task301.
- Remote branch search returned no task298-task301 heads.

## Session 3 Visibility Refresh

Commands:

```bash
git ls-remote --heads origin '*task298*' '*task299*' '*task300*' '*task301*'
git fetch origin intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1 intern_nemotron_worker_1/task299_qwen_aime_v11_30b_data_packing_contract_s1 intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1 intern_nemotron_worker_5/task301_qwen_aime_v11_30b_full_sft_training_s1
gh pr view 362 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,isDraft,url,files
gh pr view 361 --json number,state,headRefOid,baseRefName,mergeStateStatus,isDraft,url
git ls-tree --name-only -r <task298-head> workspace/tasks/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1 workspace/interns/intern_nemotron_worker_2/status.md
git ls-tree --name-only -r <task299-head> workspace/tasks/task299_qwen_aime_v11_30b_data_packing_contract_s1 workspace/interns/intern_nemotron_worker_1/status.md
git ls-tree --name-only -r <task300-head> workspace/tasks/task300_qwen_aime_v11_30b_same_harness_testing_s1 workspace/interns/intern_nemotron_worker_3/status.md
git ls-tree --name-only -r <task301-head> workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1 workspace/interns/intern_nemotron_worker_5/status.md
git diff --name-status origin/main...<task298-head>
git diff --name-status origin/main...<task299-head>
git diff --name-status origin/main...<task300-head>
git diff --name-status origin/main...<task301-head>
find /work-agents/intern_nemotron_worker_{1,2,3,5}/outputs ... task298-task301 names
```

Observed current upstream visibility:

| Task | Current head / PR | Visible branch files | Artifact/report status | Disposition |
|---|---|---|---|---|
| task298 runtime/base-load | Branch `intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1` at `7d24b9295740ef5c21fd443d6399ec9641f8f5c5`; no PR found in current search | worker_2 status plus task298 README/history/task_knowledge only | No `30b_runtime_resource_base_load_report.md` in branch. Local output root observed at `/work-agents/intern_nemotron_worker_2/outputs/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z`, but it is not yet bound by a visible official branch report/mailbox in this review. | `REQUEST_CHANGES/HOLD` |
| task299 data/packing | Branch `intern_nemotron_worker_1/task299_qwen_aime_v11_30b_data_packing_contract_s1` at `ff30fad8e6899b9a98d9530006ef49c52c7d72fb`; no PR found in current search | worker_1 status plus task299 README/history/task_knowledge only | No `30b_data_packing_contract_report.md` in branch and no task299 local output root found in the checked path. History records preliminary tokenizer parity findings and a caveat that task276 raw packed metadata names the 4B tokenizer URI; final 30B-ready root/checksums/decontam proof are still missing. | `REQUEST_CHANGES/HOLD` |
| task300 same-harness testing | Branch `intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1` at `85a5ba134c486ac36f30b63e9bcae97f51fdc1f6`; no PR found in current search | worker_3 status plus task300 README/history/task_knowledge only | No base AIME report, canary report, FT-vs-base report, metrics, denominator, completions, or checksum manifest in branch. Local probe logs observed at `/work-agents/intern_nemotron_worker_3/outputs/task300_qwen_aime_v11_30b_same_harness_testing_s1/run_20260602T144005Z`, but no official score artifact is visible. | `REQUEST_CHANGES/HOLD` |
| task301 full SFT training | PR #362 `OPEN`/base `main`/`CLEAN` at `b8e42b3e748c8c80cb3c4a938f2db06c9cb0b6d6` | worker_5 status plus task301 README/history/task_knowledge and `30b_full_sft_training_report.md` | Report disposition is `BLOCKED_UPSTREAM_GATES_MISSING` and states no training command was run and no checkpoint/loss/LR/validation/checksum artifacts were created. The report is stale on branch visibility because task298-task300 branches are now visible, but PASS artifacts remain missing. | `REQUEST_CHANGES/HOLD` |

All reviewed upstream branch diffs against `origin/main` are workspace
status/task-doc/report surfaces only. No product code diff was observed in the
branch file-scope checks.

## Gate Matrix

| Gate | Upstream task | Required evidence | Current evidence | Disposition |
|---|---|---|---|---|
| Runtime/base-load | task298 | Exact head/PR, artifact root, commands/env, logs, checksums, 30B path, import/load proof or precise blocker | Branch visible at `7d24b9295740ef5c21fd443d6399ec9641f8f5c5`; no official report in branch | `REQUEST_CHANGES/HOLD` |
| Data/packing | task299 | Exact head/PR, source manifests, split/row/token counts, checksums, no AIME2025 train leakage, no task255 reuse | Branch visible at `ff30fad8e6899b9a98d9530006ef49c52c7d72fb`; preliminary tokenizer parity notes only, no final 30B-ready root/checksums | `REQUEST_CHANGES/HOLD` |
| Testing/eval | task300 | Exact head/PR, same-harness base-vs-FT metrics, command/env, checksums, denominator, residuals | Branch visible at `85a5ba134c486ac36f30b63e9bcae97f51fdc1f6`; no base score/canary/FT-vs-base metrics | `REQUEST_CHANGES/HOLD` |
| Training | task301 | Exact head/PR, command/env, checkpoint/artifact roots, checksums, metrics, fail-closed boundaries | PR #362 visible at `b8e42b3e748c8c80cb3c4a938f2db06c9cb0b6d6`; blocker report says no training/artifacts, but visibility section is stale | `REQUEST_CHANGES/HOLD` |

## Required Review Order

1. Review task298 runtime/base-load evidence or blocker before accepting any
   downstream 30B execution gate.
2. Review task299 data/packing evidence before accepting task301 training
   artifacts as uncontaminated.
3. Review task301 training only after runtime and data prerequisites are
   concrete and in scope.
4. Review task300 same-harness metrics after base/FT artifacts exist; final 30B
   gate stays HOLD unless task300 proves FT-vs-base non-regression with
   reviewable artifacts and checksums.

## Residuals To Preserve

- No AIME2025 prompt/label train data may appear in trainable rows.
- No task255 reuse is allowed.
- No shared deletion is allowed.
- No export, endpoint, promotion, release, or scale claim is authorized by this
  runbook.
- Missing exact heads, artifact paths, commands/env, checksums, metrics, or
  residuals remain request-changes/blocking conditions for the relevant gate.

## Boundary Confirmation

This refresh was review/runbook only. I did not edit product code, run training,
run testing, score AIME, run a canary, export, launch an endpoint, promote,
reuse task255, use AIME2025 train data, delete shared files, push main, merge,
or make a release/scale claim.
