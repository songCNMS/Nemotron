# task321 closeout merge/runbook report

## Disposition

Recommendation: `APPROVE_RUNBOOK`.

This is a read-only sequencing review for #371/#377/#378/#379/#380 and
task318-task320. It does not authorize any worker self-merge, direct main push,
training, evaluation, packing, export, endpoint launch, promotion, task255
reuse, AIME2025 train-data use, or shared deletion.

## Review Snapshot

Observed at `2026-06-03T20:03:39Z`.

| Item | Exact state reviewed |
| --- | --- |
| Worker branch | `intern_nemotron_worker_4/task321_qwen_all_sft_closeout_merge_runbook_s1` |
| Worker PR | #382 |
| Branch base | `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` |
| Lead docs | `origin/intern_nemotron_lead/session1-recovery-task-docs` `48b3a5bc8bd21e15ebd8aa96e9b3bd7a145d5d1c` |
| PR scope | docs/runbook review only |

## PR Matrix

| PR | Current head | State | Scope classification | Review result |
| --- | --- | --- | --- | --- |
| #371 task311 | `fc85b866ede0cdc95f31b6fcd6d61b817ceb2de8` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | task311 evidence/fail-closeout docs plus task-owned task311 scripts | Accept as evidence/fail-closeout docs only if coordinator/authorized non-author merge path is used. Current drift from task317-reviewed `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6` is status/history/task_knowledge-only with diff-check clean. |
| #378 task317 | `df561ea93e696d8e704d4e969e2da83b719185f7` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | independent review of #371 closeout | Mergeable as review docs only. It supports #371 merge-as-evidence/fail-closeout docs and authorizes no promotion or further runtime action. |
| #380 task314 | `6d43e0e7091f42af13a435c882f4ab035ca2c4c5` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | MMLU-Pro regression forensics docs | Lead gate `APPROVE_FORENSICS_DOCS / NO_ACTION_RELEASE` was refreshed through `fc93290a`; current drift to `6d43e0e7` is status/history/task_knowledge/report-session metadata only. It preserves `FAIL_MMLU_PRO_BELOW_BASE_WITH_AIME_HMMT_PASS`; no new eval or promotion. |
| #379 task315 | `89cc7f74a737f174f4b8dbf9129c712fabbafa95` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` on recheck | M1 launcher runtime blocker docs | Mergeable as blocker docs only. It confirms `BLOCK_RUNTIME` for M1 launcher rows; no M1 row execution is authorized. |
| #377 task316 | `c1b053b518137769b9b423d08d9590d8ae481a2e` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | repair candidate plan docs | Lead gate carries forward `APPROVE_PLAN_DOCS / NO_ACTION_RELEASE`. It recommends data plus validation repair before later 30B training and authorizes no action by itself. |
| #384 task318 | `9689b22bf0e198cbf6f7ca7cbdc30f05bdbe751c` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | validation/exit repair preflight docs | Lead gate at `2cdf39fd` is `APPROVE_PREFLIGHT_PLAN_WITH_IMPLEMENTATION_REQUIRED / HOLD_TRAINING`; current drift to `9689b22b` is status/history/task_knowledge gate-recording only and report content is unchanged. This requires later implementation/launch planning before any optimizer launch. |
| #383 task319 | `99713578c19a971683348128d7120f5822801337` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | raw blend/decontam feasibility docs | Lead gate `APPROVE_FEASIBILITY_DOCS / NO_PACK_OR_TRAIN_RELEASE` was posted at `4775bc17`; current drift to `99713578` is status/history/task_knowledge gate-recording only. Twelve raw candidates are feasible for a later task, but row counts, supervised-token counts, decontam scan output, and split exposure proof remain missing; no packing or training is released. |
| #381 task320 | `4131915f14acb4ff551ae6cf3f2325a67cf89945` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | MMLU-Pro data-repair linkage docs | Lead gate `APPROVE_LINKAGE_DOCS / NO_ACTION_RELEASE`. It accepts MMLU-Pro -2 as a data-repair constraint: preserve math gains while adding broad non-math retention coverage. Residual: the report snapshot says no task319 PR was visible, while #383 is now visible and gated; lead called this non-material unless #381 is refreshed. |

All eight PR diffs were checked with `git diff --name-status` and `git diff
--check` against `origin/main` or the relevant previously reviewed head. The
diffs are limited to worker status files, task-specific docs, reports, and
task-owned scripts under their task directories; no product code was modified
by these PRs.

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
3. Merge #377 as the repair-plan docs after the closeout/foundation evidence is
   merged or explicitly accepted by lead. #377 should remain docs-only and must
   not be treated as release for a repair run.
4. Merge #384 and #383 as concrete no-action repair preflight/feasibility docs
   after #377 is accepted or scheduled. They may be ordered independently:
   #384 covers validation/exit implementation requirements and keeps training
   on HOLD; #383 covers raw blend feasibility and keeps packing/training held.
5. Merge #381 as MMLU data-repair linkage after #380 is merged/accepted and,
   preferably, after #383 is merged/accepted so the known task319 visibility
   residual is harmless. If lead wants the #381 text itself to mention #383,
   require a #381 refresh; otherwise lead has accepted the residual as
   non-material linkage evidence.

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
- #380 changes its forensics finding that MMLU-Pro -2 is real answer-choice
  drift under the aligned protocol.
- #381 changes linkage constraints or tries to authorize packing/training/eval.
- #383 changes from feasibility docs into materialization/final packing, or
  claims packing-readiness without exact row counts, supervised-token counts,
  decontam output, and split exposure proof.
- #384 changes the unchanged validation preflight report, loses its
  implementation-required/HOLD-training framing, or implies product-code edits
  or optimizer launch are authorized.

## Next Repair Runbook

At this refreshed snapshot task318-task320 have visible, gated PRs. The next
allowed work remains limited to docs/preflight feasibility and later separate
lead-gated repair tasks:

| Task | Current PR / gate | Allowed next action | Stop conditions |
| --- | --- | --- | --- |
| task318 validation/exit repair preflight | #384 `9689b22b`; gate `APPROVE_PREFLIGHT_PLAN_WITH_IMPLEMENTATION_REQUIRED / HOLD_TRAINING` | Later separate lead-gated implementation/launch planning may choose Route A train-only/dereferenced packed root with valid exposure removed and same-harness eval handoff, or Route B built-in validation with timeout/heartbeat/rc/checkpoint/teardown controls. | Stop if product-code changes, optimizer/eval/export/endpoint action, or runtime mutation would be needed without a new authorized task. Training remains held. |
| task319 raw blend/decontam feasibility | #383 `4775bc17`; gate `APPROVE_FEASIBILITY_DOCS / NO_PACK_OR_TRAIN_RELEASE` | Later separate lead-gated raw materialize/count/decontam task in a task-owned output root. | Stop on missing source identity/revision/counts/checksums/decontam proof, forbidden AIME2025 train-row use, task255 reuse, shared mutation, undefined large downloads, or any final packing/training attempt. |
| task320 MMLU data-repair linkage | #381 `4131915f`; gate `APPROVE_LINKAGE_DOCS / NO_ACTION_RELEASE` | Use linkage constraints in later repair design: MMLU-Pro aggregate must be `>= base` and non-math aggregate `>= 0` if later eval is authorized; preserve math gains while repairing broad non-math retention. | Stop if linkage requires new eval, data materialization, packing, training, export, endpoint, or promotion; optionally refresh #381 if lead wants its text to mention #383. |

No later 30B repair training, packing, export, endpoint, benchmark eval,
promotion, or go/no-go can be inferred from task321 or the closeout/repair docs
PR set. Those require separate lead-gated tasks after these docs are accepted.

## Commands And Checks

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs \
  +pull/371/head:refs/remotes/origin/pr/371 \
  +pull/377/head:refs/remotes/origin/pr/377 \
  +pull/378/head:refs/remotes/origin/pr/378 \
  +pull/379/head:refs/remotes/origin/pr/379 \
  +pull/380/head:refs/remotes/origin/pr/380 \
  +pull/381/head:refs/remotes/origin/pr/381 \
  +pull/383/head:refs/remotes/origin/pr/383 \
  +pull/384/head:refs/remotes/origin/pr/384
git rev-parse origin/main
git rev-parse origin/intern_nemotron_lead/session1-recovery-task-docs
gh pr view 371 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 377 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 378 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 379 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 380 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 381 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 383 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 384 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
git diff --name-status origin/main...origin/pr/371
git diff --name-status origin/main...origin/pr/377
git diff --name-status origin/main...origin/pr/378
git diff --name-status origin/main...origin/pr/379
git diff --name-status origin/main...origin/pr/380
git diff --name-status origin/main...origin/pr/381
git diff --name-status origin/main...origin/pr/383
git diff --name-status origin/main...origin/pr/384
git diff --check origin/main...origin/pr/371
git diff --check origin/main...origin/pr/377
git diff --check origin/main...origin/pr/378
git diff --check origin/main...origin/pr/379
git diff --check origin/main...origin/pr/380
git diff --check origin/main...origin/pr/381
git diff --check origin/main...origin/pr/383
git diff --check origin/main...origin/pr/384
git diff --name-status 9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6..origin/pr/371
git diff --check 9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6..origin/pr/371
git diff --name-status fc93290a58e412eacf3c4371490f88149ad69aa7..origin/pr/380
git diff --check fc93290a58e412eacf3c4371490f88149ad69aa7..origin/pr/380
git diff --name-status 4775bc17f2792430508eb15aa7669ac2562071f6..origin/pr/383
git diff --check 4775bc17f2792430508eb15aa7669ac2562071f6..origin/pr/383
git diff --name-status 2cdf39fd91ae0e6d686f98ff08b175ec10970e53..origin/pr/384
git diff --check 2cdf39fd91ae0e6d686f98ff08b175ec10970e53..origin/pr/384
gh api repos/songCNMS/Nemotron/issues/381/comments --jq '<lead gate filter>'
gh api repos/songCNMS/Nemotron/issues/383/comments --jq '<lead gate filter>'
gh api repos/songCNMS/Nemotron/issues/384/comments --jq '<lead gate filter>'
```

## Boundary Confirmation

I did not merge, self-merge, push main, train, evaluate, pack, export, launch an
endpoint, promote, reuse task255, use AIME2025 train data, or delete shared
files. The task321 output is a docs/runbook review only.
