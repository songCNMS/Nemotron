# task321 closeout merge/runbook report

## Disposition

Recommendation: `APPROVE_RUNBOOK`.

This is a read-only sequencing review for #371/#377/#378/#379/#380 and
task318-task320. It does not authorize any worker self-merge, direct main push,
training, evaluation, packing, export, endpoint launch, promotion, task255
reuse, AIME2025 train-data use, or shared deletion.

## Review Snapshot

Observed at `2026-06-03T19:44:34Z`.

| Item | Exact state reviewed |
| --- | --- |
| Worker branch | `intern_nemotron_worker_4/task321_qwen_all_sft_closeout_merge_runbook_s1` |
| Worker PR | #382 |
| Branch base | `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` |
| Lead docs | `origin/intern_nemotron_lead/session1-recovery-task-docs` `479fe4c1df950ad441c2c6431792be06a7cc3ef6` |
| PR scope | docs/runbook review only |

## PR Matrix

| PR | Current head | State | Scope classification | Review result |
| --- | --- | --- | --- | --- |
| #371 task311 | `fc85b866ede0cdc95f31b6fcd6d61b817ceb2de8` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | task311 evidence/fail-closeout docs plus task-owned task311 scripts | Accept as evidence/fail-closeout docs only if coordinator/authorized non-author merge path is used. Current drift from task317-reviewed `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6` is status/history/task_knowledge-only with diff-check clean. |
| #378 task317 | `df561ea93e696d8e704d4e969e2da83b719185f7` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | independent review of #371 closeout | Mergeable as review docs only. It supports #371 merge-as-evidence/fail-closeout docs and authorizes no promotion or further runtime action. |
| #380 task314 | `9e57390bb33365157b73a8c93264b9dd57a2d489` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | MMLU-Pro regression forensics docs | Mergeable as forensics docs only. It preserves `FAIL_MMLU_PRO_BELOW_BASE_WITH_AIME_HMMT_PASS`; no new eval or promotion. |
| #379 task315 | `89cc7f74a737f174f4b8dbf9129c712fabbafa95` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` on recheck | M1 launcher runtime blocker docs | Mergeable as blocker docs only. It confirms `BLOCK_RUNTIME` for M1 launcher rows; no M1 row execution is authorized. |
| #377 task316 | `c1b053b518137769b9b423d08d9590d8ae481a2e` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | repair candidate plan docs | Mergeable only after the closeout/support docs are sequenced or explicitly accepted by lead. It recommends data plus validation repair before any later 30B training and authorizes no action by itself. |

All five PR diffs were checked with `git diff --name-status` and `git diff
--check` against `origin/main`. The diffs are limited to worker status files,
task-specific docs, and task-owned scripts under their task directories; no
product code was modified by these PRs.

## Recommended Merge Sequence

Use coordinator/authorized non-author merge only. Before each merge, recheck
the exact head, base `main`, non-draft state, and `CLEAN`/`MERGEABLE` status.

1. Merge #378, #380, and #379 as supporting review/forensics/blocker docs.
   These may be merged in any order if their exact heads remain unchanged and
   clean. They provide the independent review, MMLU-Pro forensics, and M1
   runtime blocker context for #371.
2. Merge #371 as the task311 evidence/fail-closeout record only after the
   support set is accepted or explicitly scheduled by lead. Current #371 head
   `fc85b866` is acceptable because the drift from reviewed head `9361e6da`
   only updates status/history/task_knowledge and does not change the benchmark
   evidence, scripts, metrics, or artifact claims.
3. Merge #377 last as the repair-plan/runbook docs, once #371/#378/#379/#380
   are merged or lead explicitly accepts the plan against the same evidence
   set. #377 should remain docs-only and must not be treated as release for a
   repair run.

## Hold Conditions

Hold and request refresh if any of the following occur:

- Any PR head changes materially outside status/history/task_knowledge
  bookkeeping.
- Any PR becomes draft, stale, dirty, conflicting, closed unexpectedly, or not
  mergeable.
- #371 changes benchmark evidence, runner scripts, artifact hashes, or metrics
  beyond the verified metadata-only drift.
- #377 changes from a plan into an execution request, or implies immediate
  training, packing, export, endpoint, promotion, or benchmark release.
- #379 loses the `CLEAN`/`MERGEABLE` state or changes its blocker conclusion.
- New task318-task320 evidence contradicts the closeout facts before #377 is
  merged.

## Next Repair Runbook

At this snapshot no remote worker branches or PRs were visible for
task318-task320; only lead assignment docs were visible on the lead branch.
The next allowed work is limited to these no-runtime/no-promotion tasks:

| Task | Allowed next action | Stop conditions |
| --- | --- | --- |
| task318 validation/exit repair preflight | Review task310 configs/logs and propose a no-training validation or explicit-skip handoff route with exact config keys, rc policy, timeout policy, checkpoint marker policy, and teardown proof. Optional import/config dry-run only if it has no optimizer step and no eval. | Stop if product-code changes are required, any optimizer/eval/export/endpoint action would be needed, or rc/timeout/checkpoint policy cannot be made explicit. |
| task319 raw blend/decontam feasibility | Audit `stage1_sft/data_blend_raw` sources, materialization status, counts, checksums, supervised-token feasibility, and heldout/decontam plan. Lightweight task-owned probes only; no final packing. | Stop on missing source identity/revision/counts/checksums/decontam proof, forbidden AIME2025 train-row use, task255 reuse, shared mutation, or undefined large downloads. |
| task320 MMLU data-repair linkage | Map task314 MMLU-Pro row/category drift to concrete data-repair constraints using task314 plus task308/task309 evidence. Coordinate with task319 outputs if available. | Stop if task314/task308/task309 evidence is unavailable or contradictory, or if linkage requires new eval, data materialization, packing, or training. |

No later 30B repair training, packing, export, endpoint, benchmark eval,
promotion, or go/no-go can be inferred from task321 or the closeout PR set.
Those require separate lead-gated tasks after task318-task320 produce accepted
evidence.

## Commands And Checks

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs \
  +pull/371/head:refs/remotes/origin/pr/371 \
  +pull/377/head:refs/remotes/origin/pr/377 \
  +pull/378/head:refs/remotes/origin/pr/378 \
  +pull/379/head:refs/remotes/origin/pr/379 \
  +pull/380/head:refs/remotes/origin/pr/380
git rev-parse origin/main
git rev-parse origin/intern_nemotron_lead/session1-recovery-task-docs
gh pr view 371 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 377 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 378 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 379 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 380 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
git diff --name-status origin/main...origin/pr/371
git diff --name-status origin/main...origin/pr/377
git diff --name-status origin/main...origin/pr/378
git diff --name-status origin/main...origin/pr/379
git diff --name-status origin/main...origin/pr/380
git diff --check origin/main...origin/pr/371
git diff --check origin/main...origin/pr/377
git diff --check origin/main...origin/pr/378
git diff --check origin/main...origin/pr/379
git diff --check origin/main...origin/pr/380
git diff --name-status 9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6..origin/pr/371
git diff --check 9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6..origin/pr/371
git ls-remote --heads origin '*task318*'
git ls-remote --heads origin '*task319*'
git ls-remote --heads origin '*task320*'
gh pr list --state all --search "task318 OR task319 OR task320 in:title" \
  --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,title,url
```

## Boundary Confirmation

I did not merge, self-merge, push main, train, evaluate, pack, export, launch an
endpoint, promote, reuse task255, use AIME2025 train data, or delete shared
files. The task321 output is a docs/runbook review only.
