# task326 next-phase safety review report

## Disposition

Recommendation: `APPROVE_SAFETY_REVIEW`.

This is a read-only safety/runbook review for task322-task325 evidence gates and
sequencing. It approves the fail-closed checklist and next-phase ordering only.
It does not approve any data materialization result, packed contract, optimizer
launch, benchmark/eval row, export, endpoint, promotion, merge, self-merge,
direct main push, task255 reuse, AIME2025 train-data use, or shared deletion.

At this snapshot task323, task324, and task325 have visible PRs with
substantive worker evidence, but no lead gate comments yet. No task322 worker
branch or PR is visible. task322 remains pending substantive evidence.

## Review Snapshot

Observed at `2026-06-03T20:41:50Z`.

| Item | Exact state reviewed |
| --- | --- |
| Worker branch | `intern_nemotron_worker_4/task326_qwen_all_sft_next_phase_safety_review_s1` |
| Branch base | `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` |
| Lead docs | `origin/intern_nemotron_lead/session1-recovery-task-docs` `7055dac63c772ac8a317454bffead4a469a0112f` |
| Task scope | docs/runbook safety review only |

## Accepted Foundation Gates

| Task / PR | Current head | Current state | Gate disposition used |
| --- | --- | --- | --- |
| task320 #381 | `4131915f14acb4ff551ae6cf3f2325a67cf89945` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | `APPROVE_LINKAGE_DOCS / NO_ACTION_RELEASE`. MMLU-Pro `-2` is real data-repair constraint; math `+13` but non-math aggregate `-15`, with 86/92 loss rows outside math. |
| task321 #382 | `a908b81dd6583976b08896c8193ca302909c52ff` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | `APPROVE_RUNBOOK / NO_ACTION_RELEASE`. Accepted order: support docs, #371 evidence closeout, #377 plan, then #384/#383/#381 repair docs by coordinator/authorized non-author merge only. |
| task319 #383 | `802a796d77144a7fdfc56477fdd001b574e90568` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | `APPROVE_FEASIBILITY_DOCS / NO_PACK_OR_TRAIN_RELEASE`; current drift from lead-refreshed `99713578` is task322 handoff metadata only. Twelve raw sources are feasible candidates, but 0/12 have exact local row counts, supervised-token counts, row manifests, decontam output, or split exposure proof. |
| task318 #384 | `1c3048b96301b87e91fbcfa03649220c7a773e61` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | `APPROVE_PREFLIGHT_PLAN_WITH_IMPLEMENTATION_REQUIRED / HOLD_TRAINING`; current drift from lead-refreshed `9689b22b` is task323 handoff metadata only. Future optimizer launch requires Route A validation-skip proof or Route B bounded validation proof. |
| task323 #385 | `edb265351b9f369698f561527cd27f2978f649ba` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | Worker-reported `PASS_ROUTE_A_PREFLIGHT`; no lead gate comment visible. Current PR is substantive worker evidence, pending lead review, not training clearance. |
| task324 #386 | `8c4f7aa72f07e69e400789fced12acb17cf80cb7` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | Worker-reported `APPROVE_BLEND_DESIGN`; no lead gate comment visible. Design is docs-only and depends on task322 materialized/decontaminated sources before any packed contract. |
| task325 #387 | `e07ee3f9268b33658e18881c25a3d221bf2136ee` | `OPEN`, base `main`, non-draft, `CLEAN`, `MERGEABLE` | Worker-reported `BLOCK_RUNTIME_CONFIRMED`; no lead gate comment visible. Current drift from first report head `e6c5e1f` is worker status/history/task_knowledge metadata only and the blocker report is unchanged. It confirms 0/19 M1 rows runnable now and proposes only a later lead-gated eval-only remediation route. |

All reviewed diffs for #381/#382/#383/#384 are limited to worker status plus
task-specific docs/reports and pass `git diff --check`.

## Pending Task Matrix

| Task | Visibility | Required output before downstream use | Current safety disposition |
| --- | --- | --- | --- |
| task322 raw materialize/count/decontam | No branch or PR visible | Source-by-source materialization matrix, exact local row counts, file and row-manifest checksums, parse status, heldout/decontam results, split exposure proof, no task255 reuse, no AIME2025 prompt/label train rows. | `HOLD_PENDING_TASK322_EVIDENCE`. No raw source can enter a packed contract yet. |
| task323 validation-skip preflight | PR #385 visible at `edb26535`, no lead gate visible | Train-only/dereferenced root proof, `valid` exposure count `0`, `do_validation=false`, `packed_val_data_path=null`, source checksums, no shared mutation, explicit same-harness eval handoff, rc/checkpoint/timeout/teardown policy. Worker report claims these pass on constrained task299/task310 seed. | `HOLD_PENDING_TASK323_LEAD_GATE`. No optimizer launch can use Route A until lead accepts #385 and a later launch task is assigned. |
| task324 MMLU-aware blend design | PR #386 visible at `8c4f7aa7`, no lead gate visible | Bucket mapping from task319/task322 sources to MMLU retention buckets, source inclusion/exclusion criteria, rows/input tokens/supervised tokens/splits/decontam minimums, later same-harness metrics. Worker report claims design is concrete but still depends on task322. | `HOLD_PENDING_TASK324_LEAD_GATE_AND_TASK322`. No materialized sources can be converted into a packed blend from design alone. |
| task325 M1 launcher remediation route | PR #387 visible at `e07ee3f9`, no lead gate visible | Exact runtime/container/module/credential route or blocker, row-by-row M1 availability matrix, safe import/version probes only, no benchmark row execution. Worker report confirms `BLOCK_RUNTIME_CONFIRMED`. | `HOLD_PENDING_TASK325_LEAD_GATE`. No M1 rows can be run. |

## Evidence Gates

### Raw Sources To Packed Contract

Before any raw source from `stage1_sft/data_blend_raw` can enter a later packed
contract, task322 or a successor must prove all of the following:

- Source identity: dataset/path, subset or file stem, revision, selected split
  or file path, license if applicable, and inclusion/blocker status.
- Materialization: task-owned local path only, bytes, exact row count, parse
  status, source file sha256, row-manifest sha256, and no shared root mutation.
- Decontam: exact prompt-hash and normalized text checks against
  AIME2025/HMMT/MATH heldouts from task246 and MMLU-Pro/task311-task314
  heldout references; overlap counts must be `0` or false positives must be
  reviewed in a manifest.
- Safety exclusions: no AIME2025 prompts or labels as train rows, no task255
  reuse, no shared deletion, and blocked sources explicitly excluded.
- Split exposure: intended-vs-exposed train/valid/test manifest with local
  checksums. Unknown splits must fail closed.
- Packing handoff readiness: per-source input-token and supervised-token
  feasibility under Qwen3-30B tokenizer/chat-template; final packing remains a
  separate later task.

Stop condition: any source lacking exact row count, local checksum, row
manifest, decontam proof, or split exposure proof must be excluded or block the
packed-contract handoff.

### Validation-Skip Root To Optimizer Launch

Before a train-only root can be used for any optimizer launch, task323 or a
successor must prove:

- The root is task-owned or otherwise safely dereferenced; task299/task310 and
  shared roots are not mutated.
- `splits/train/*.parquet` is present with exact count/checksum/source proof.
- `splits/valid/*.parquet` count is `0`; `do_validation=false` and
  `packed_val_data_path=null` are emitted by no-training preflight.
- Test exposure status is explicit, and no hidden symlink points back to a
  mutable shared root.
- `same_harness_eval_handoff_required=true` is recorded before launch.
- `train_rc=0`, `train_end.txt`, final checkpoint marker, timeout policy,
  checkpoint inventory, process teardown, and GPU release requirements are
  part of the launch contract.
- No task255 reuse, no AIME2025 prompt/label train rows, no product-code edit,
  no eval/export/endpoint/promotion is introduced.

Stop condition: if validation skip cannot be proven without product-code edits,
shared mutation, final packing, optimizer steps, or eval rows, keep training on
HOLD.

### MMLU-Aware Blend Design To Packed Data

Before task324 design can become packed data, require:

- task322 accepted materialized sources or exact exclusions;
- per-source and per-bucket rows, input tokens, supervised tokens, and splits;
- MMLU retention buckets for physical sciences, bio-health, humanities/social,
  technical/coding, math, and broad instruction/other;
- nonzero, decontaminated coverage for high-priority loss buckets or explicit
  fail-closed blockers;
- MMLU-Pro heldout references carried as decontam inputs, not train data;
- valid/test coverage that is not task299-style sparse (`1` valid, `0` test);
- later same-harness metric requirements: MMLU-Pro aggregate `>= base`,
  non-math aggregate `>= 0`, AIME25 `>= base`, HMMT `>= base`, with parser,
  row, endpoint, and cleanup evidence.

Stop condition: do not pack or train from blend design if task322 evidence is
missing, if any included bucket lacks counts/checksums/decontam proof, or if the
design silently collapses back to math/task299-only data.

### M1 Route To Evaluation

Before any M1 benchmark row can run, task325 or a successor must prove:

- exact row mapping for launcher-available rows and explicit unavailable-row
  documentation for the five exact-missing rows;
- task-owned launcher/evaluator runtime or exact blocker, including
  `nemo-evaluator-launcher`, `nemo-evaluator`, benchmark modules, container or
  scheduler route, credentials, endpoint reachability, and row-specific data;
- safe import/version/config probes only until a later eval task is explicitly
  authorized;
- no benchmark row execution, model eval, export, endpoint, promotion, task255
  reuse, AIME2025 train data, shared mutation/deletion, merge, or main push.

Stop condition: if the runtime route cannot be proven without system package
installs, shared environment mutation, missing credentials, or unreviewed
containers, keep `BLOCK_RUNTIME_CONFIRMED`.

## Sequencing Recommendation

1. Keep #381/#382/#383/#384 as docs/no-action evidence. Merge, if desired,
   only through coordinator/authorized non-author paths and only while exact
   heads remain clean/mergeable.
2. task322 and task324 may proceed as read-only/task-owned data planning work,
   but no final packing can be assigned until task322 passes or blocks with
   exact included/excluded source evidence.
3. task323/#385 now provides worker-reported Route A preflight evidence for
   the accepted constrained task299/task310 packed root, but it still needs
   lead gate review. If any later launch wants to use task322 raw outputs, it
   must wait for an accepted task322 handoff and a later packed contract.
4. task324/#386 now provides worker-reported blend design evidence, but it
   still needs lead gate review and cannot become a packed contract until
   task322 produces accepted source evidence.
5. task325/#387 now provides worker-reported M1 blocker evidence, but it still
   needs lead gate review. It must not run benchmark rows.
6. A later packed-data repair contract requires accepted task322 evidence plus
   task324 blend constraints. It must still be a separate lead-gated task.
7. A later optimizer launch requires accepted packed data plus accepted task323
   validation-skip/exit contract. task318/task323 do not themselves authorize
   training.
8. A later benchmark/eval phase requires a clean checkpoint/canary handoff plus
   accepted same-harness protocol and, for M1 rows, accepted task325 route.

## Residual Risk Matrix

| Risk | Current control | Residual state |
| --- | --- | --- |
| Raw source contamination or unknown counts | task319 feasibility plus task322 required materialization/decontam gate | High until task322 report exists. |
| Repeating task310 validation hang | task318 Route A/Route B requirements plus task323/#385 worker preflight | Medium until lead gates #385; still no optimizer launch without a separate launch task. |
| Math gains masking broad MMLU-Pro regression | task320 linkage and task324/#386 worker blend design | Medium until lead gates #386 and a later packed contract emits bucket counts. |
| Premature packing/training from feasibility docs | Explicit no-pack/no-train gates on #383/#382/#384 | Controlled if lead keeps later tasks separate. |
| M1 rows remain unrunnable | task315 blocker plus task325/#387 worker blocker report | High for M1 eval until lead gates #387 and any later remediation route is separately authorized. |
| Stale metadata heads on #383/#384 | Latest drift checked as handoff metadata only | Low for safety review; recheck exact heads before merge. |

## Commands And Checks

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git checkout origin/intern_nemotron_lead/session1-recovery-task-docs -- workspace/tasks/task326_qwen_all_sft_next_phase_safety_review_s1
git ls-remote --heads origin '*task322*' '*task323*' '*task324*' '*task325*'
gh pr list --state all --search "task322 OR task323 OR task324 OR task325 in:title" --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,title,url
git fetch origin +pull/381/head:refs/remotes/origin/pr/381 +pull/382/head:refs/remotes/origin/pr/382 +pull/383/head:refs/remotes/origin/pr/383 +pull/384/head:refs/remotes/origin/pr/384
for pr in 381 382 383 384; do gh pr view "$pr" --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title; done
gh pr view 385 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 386 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 387 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
for pr in 381 382 383 384; do git diff --name-status origin/main...origin/pr/$pr; git diff --check origin/main...origin/pr/$pr; done
git diff --name-status 99713578c19a971683348128d7120f5822801337..origin/pr/383
git diff --check 99713578c19a971683348128d7120f5822801337..origin/pr/383
git diff --name-status 9689b22bf0e198cbf6f7ca7cbdc30f05bdbe751c..origin/pr/384
git diff --check 9689b22bf0e198cbf6f7ca7cbdc30f05bdbe751c..origin/pr/384
git fetch origin +pull/385/head:refs/remotes/origin/pr/385
git diff --name-status cb177fd997940267d5a9d6a45990d968ba7c2ec0..origin/pr/385
git diff --check cb177fd997940267d5a9d6a45990d968ba7c2ec0..origin/pr/385
gh api repos/songCNMS/Nemotron/issues/385/comments --jq '<lead gate filter>'
gh api repos/songCNMS/Nemotron/issues/386/comments --jq '<lead gate filter>'
gh api repos/songCNMS/Nemotron/issues/387/comments --jq '<lead gate filter>'
gh api repos/songCNMS/Nemotron/issues/381/comments --jq '<lead gate filter>'
gh api repos/songCNMS/Nemotron/issues/382/comments --jq '<lead gate filter>'
gh api repos/songCNMS/Nemotron/issues/383/comments --jq '<lead gate filter>'
gh api repos/songCNMS/Nemotron/issues/384/comments --jq '<lead gate filter>'
git show origin/intern_nemotron_lead/session1-recovery-task-docs:workspace/tasks/task322_qwen_all_sft_raw_materialize_count_decontam_s1/README.md
git show origin/intern_nemotron_lead/session1-recovery-task-docs:workspace/tasks/task323_qwen_all_sft_validation_skip_preflight_s1/README.md
git show origin/intern_nemotron_lead/session1-recovery-task-docs:workspace/tasks/task324_qwen_all_sft_mmlu_aware_blend_design_s1/README.md
git show origin/intern_nemotron_lead/session1-recovery-task-docs:workspace/tasks/task325_qwen_all_sft_m1_launcher_remediation_route_s1/README.md
git show origin/pr/385:workspace/tasks/task323_qwen_all_sft_validation_skip_preflight_s1/validation_skip_preflight_report.md
git show origin/pr/386:workspace/tasks/task324_qwen_all_sft_mmlu_aware_blend_design_s1/mmlu_aware_blend_design_report.md
git show origin/pr/387:workspace/tasks/task325_qwen_all_sft_m1_launcher_remediation_route_s1/m1_launcher_remediation_route_report.md
```

## Boundary Confirmation

I did not merge, self-merge, push main, materialize data, pack, train, run
eval, export, launch endpoint, promote, reuse task255, use AIME2025 train data,
or delete shared files. The task326 output is docs/runbook safety review only.
