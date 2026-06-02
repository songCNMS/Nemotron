# task302 30B independent review runbook

<!-- METADATA:STATUS=Hold,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Decision

- Overall disposition: `HOLD_WAITING_TASK298_TASK301_EVIDENCE`
- Current branch:
  `intern_nemotron_worker_4/task302_qwen_aime_v11_30b_independent_review_runbook_s1`
- Base main:
  `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`
- Lead docs source:
  `origin/intern_nemotron_lead/session1-recovery-task-docs`
  exact requested commit `676d8556`

No 30B gate can be approved from assignment docs alone. The initial review state
is HOLD until exact task298-task301 heads, PRs, artifact roots, commands, logs,
checksums, metrics, and residuals are available for independent review.

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

## Gate Matrix

| Gate | Upstream task | Required evidence | Current evidence | Disposition |
|---|---|---|---|---|
| Runtime/base-load | task298 | Exact head/PR, artifact root, commands/env, logs, checksums, 30B path, import/load proof or precise blocker | Not visible | `HOLD` |
| Data/packing | task299 | Exact head/PR, source manifests, split/row/token counts, checksums, no AIME2025 train leakage, no task255 reuse | Not visible | `HOLD` |
| Testing/eval | task300 | Exact head/PR, same-harness base-vs-FT metrics, command/env, checksums, denominator, residuals | Not visible | `HOLD` |
| Training | task301 | Exact head/PR, command/env, checkpoint/artifact roots, checksums, metrics, fail-closed boundaries | Not visible | `HOLD` |

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

This acceptance pass was review/runbook only. I did not edit product code, run
training, run testing, score AIME, run a canary, export, launch an endpoint,
promote, reuse task255, use AIME2025 train data, delete shared files, push main,
merge, or make a release/scale claim.
