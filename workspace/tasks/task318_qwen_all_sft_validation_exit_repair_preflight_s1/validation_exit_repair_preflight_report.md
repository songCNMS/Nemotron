# task318 validation/exit repair preflight report

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

Generated: 2026-06-03T19:45:33Z

## Session 95 post-task316 merge refresh

Refreshed against `origin/main`
`928d9d684b188fc1858914d0de7aef211627f697` after #377/task316 self-merged
through the lead-approved PR path. #377 merged at `2026-06-04T13:57:09Z` from
head `19f8a01f44aa4322635aab374d8ed22795639bda`; the merge commit is
`928d9d684b188fc1858914d0de7aef211627f697`.

#384 remains docs-only validation-exit preflight provenance with disposition
`PASS_PREFLIGHT_PLAN_WITH_IMPLEMENTATION_REQUIRED / HOLD_TRAINING`. Since
#385/task323 is already merged as the concrete Route A train-only
validation-skip proof, #384 can also be closed as superseded by #385 if lead
chooses that sequencing. This refresh does not authorize implementation,
training, optimizer steps, eval rows, export, endpoint, promotion,
task310/task341 release, task255 reuse, AIME2025 train rows, shared deletion,
product-code edits, main push, merge, or self-merge.

## Session 94 current-main refresh

Refreshed against `origin/main`
`4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985` on 2026-06-04 after
#380/task314 and #371/task311 landed. The original task318 conclusion remains
valid as preflight provenance only:
`PASS_PREFLIGHT_PLAN_WITH_IMPLEMENTATION_REQUIRED / HOLD_TRAINING`.

Current downstream state:

- #385/task323 merged at `2026-06-04T13:13:07Z`, merge
  `8a757c323b82f4330b765ee89a6d78f421d9d9be`, merged head
  `de480248b1ad7abe16a620729e62fa397443228d`. It provides the concrete Route A
  train-only validation-skip preflight that task318 recommended as a later
  implementation/preflight step.
- #371/task311 merged at `2026-06-04T13:36:33Z`, merge
  `4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985`, merged head
  `2e0cd5a5c7d788ded67334ff25608f8aaedfeffe`, carrying
  `PERFORMANCE_FAIL_MIXED` benchmark evidence.
- #380/task314 merged at `2026-06-04T13:36:32Z`, merge
  `4ccedc1a6e30f08b6ab844c0b387714d9ef16063`, merged head
  `fe34e52d19ec9cc9a384588a3e900924280fe16e`, carrying MMLU-Pro regression
  forensics.
- #404/task341 and #405/task342 are merged blocker evidence: training readiness
  and NemTron SSH/runtime access remain blocked. Task318 does not release
  task310/task341, training, eval, export, endpoint, promotion, or follow-on
  runtime work.

This makes #384 historical validation-exit preflight provenance. If the lead
chooses to close it as superseded, #385 is the merged current-main Route A proof
and this report's Route B timeout/teardown policy remains referenced by later
runbooks. If kept open, #384 should be treated as docs-only and no-action
release.

## Disposition

Recommendation:
`PASS_PREFLIGHT_PLAN_WITH_IMPLEMENTATION_REQUIRED`.

This task found a concrete no-training repair route for the task310 validation
hang failure mode, but it does not authorize another optimizer run. A later
lead-gated implementation or launch task must prove either `do_validation=false`
with a separate same-harness eval handoff, or a bounded built-in validation path
with timeout, rc, checkpoint, and teardown controls.

No training, optimizer step, eval row, packing, export, endpoint, promotion,
task255 reuse, AIME2025 train data, shared deletion, product-code edit, main
push, merge, or self-merge was performed.

## Inputs reviewed

| Input | Evidence |
|---|---|
| Original current main | `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` |
| Session 94 refresh main | `4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985` |
| Session 95 refresh main | `928d9d684b188fc1858914d0de7aef211627f697` |
| Lead task docs | `origin/intern_nemotron_lead/session1-recovery-task-docs` at assignment commit `724ebecc` |
| Task310 report | `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md` |
| Task313 review | `workspace/tasks/task313_qwen_all_sft_task310_checkpoint_salvage_review_s1/task310_checkpoint_salvage_review_report.md` |
| Task316 plan | #377 merged at `2026-06-04T13:57:09Z`, merge `928d9d684b188fc1858914d0de7aef211627f697`, merged head `19f8a01f44aa4322635aab374d8ed22795639bda` |
| Task311 context | PR #371 is merged at `4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985`; task318 did not re-review benchmark artifacts |
| Task323 follow-up | PR #385 is merged at `8a757c323b82f4330b765ee89a6d78f421d9d9be` and provides the concrete Route A validation-skip preflight proof |

## Failure mode summary

Task310 completed the bounded training loop and saved the final checkpoint
candidate, but the run did not cleanly exit:

| Item | Evidence |
|---|---|
| Remote run root | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z` |
| Local evidence root | `/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z` |
| Final checkpoint candidate | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035` |
| Training command hash | `c50bdeca383359aa6656884df707089321813efbf36bd01933e2b58389910777` |
| Launch script hash | `714a0452e5cf938bf91376db5421b2164d386c48547f2bc295bef01122e576b6` |
| Preflight summary hash | `cff95dc1c07325b9192677670d68fe3b64a54759919879c5ce5db0b82d1b10b3` |
| Training log hash | `e74eeec901731a7417e8151f04d1c9f67099906772eae611f2a027b7f48f5858` |
| Latest checkpoint marker | `35` |
| Wrapper rc/end | `train_rc.txt=1`, `train_end.txt=2026-06-03T16:36:36Z` |

The train log reached iteration `35/35` with finite loss, skipped iterations
`0`, NaN iterations `0`, and a successful final checkpoint save. It then
logged `Evaluating on 80 samples` / `Evaluating iter 1/10` and made no further
validation progress before lead-cleared `SIGTERM`. Task313 approved only
`APPROVE_SALVAGE_HANDOFF_TO_TASK311_LOAD_CANARY_ONLY`; this is not a clean
training pass.

## Static validation-control findings

The current 30B entrypoint does not expose a reviewed CLI-only validation
timeout or explicit `do_validation=false` knob.

| Area | Finding |
|---|---|
| Dataset config | `src/nemotron/recipes/super3/stage1_sft/train.py` auto-enables validation when `${super3_packed_sft_dir}/valid/*.parquet` exists. If no valid parquet is present, it logs that validation is skipped and returns `do_validation=False`. |
| Qwen 30B entrypoint | `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py` passes `train.eval_interval` into `_qwen3_moe_finetune_common`, but I found no explicit `do_validation` or validation timeout override in this entrypoint. |
| Base config | `src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml` provides the packed root, train iteration, batch, checkpoint, and tokenizer fields, but no validation timeout policy. |
| Task299 packed root | The accepted constrained packed root exposes `46` train symlinks, `1` valid symlink, and `1` test symlink under `splits/`; the valid symlink is enough for the current auto-detection path. |
| Task310 preflight | `preflight_summary.json` recorded `"do_validation": true` and `packed_val_data_path` pointing at `valid_4096_valid.npy`. |

The task310 wrapper had `set -o pipefail` and wrote `train_rc.txt` plus
`train_end.txt` only after `torchrun` returned. It had no built-in heartbeat or
no-progress timeout. The clean wrapper invariant therefore failed until lead
manually authorized termination.

## Required repair route

### Route A: explicit built-in validation skip plus same-harness handoff

This is the preferred route for the next bounded training attempt unless a
separate implementation task proves built-in validation completion.

Required later-task setup:

1. Create a task-owned, dereferenced training input root; do not mutate task299
   or any shared source root.
2. Expose the reviewed training shards under `splits/train/`.
3. Do not expose `splits/valid/*.parquet` to the training entrypoint. The
   current code path should then set `do_validation=False`.
4. Preserve source-vs-task-owned manifests proving train shard count, row count,
   token counts, checksums, no symlinks if dereferenced, no task255 reuse, no
   AIME2025 prompt/label train rows, and no shared deletion.
5. Before optimizer launch, run a no-training config/root preflight that emits a
   JSON record with:
   - `super3_packed_sft_dir`
   - `train_parquet_count`
   - `valid_parquet_count=0`
   - `do_validation=false`
   - `packed_train_data_path`
   - `packed_val_data_path=null`
   - `same_harness_eval_handoff_required=true`

The training launch may only be considered clean if `train_rc=0`,
`train_end.txt` exists, the expected final checkpoint marker exists, and the
report explicitly states that validation was intentionally skipped and deferred
to a later same-harness benchmark/eval task.

### Route B: built-in validation retained

If the next owner wants built-in validation, a later implementation or runtime
preflight task is required before training. Minimum evidence:

1. A no-optimizer validation/import dry-run or equivalent proof that built-in
   validation can finish in the 30B runtime.
2. A wrapper-level validation no-progress guard:
   `VALIDATION_NO_PROGRESS_SEC=1800`, `SNAPSHOT_INTERVAL_SEC=300`,
   `SIGTERM_GRACE_SEC=300`.
3. The guard must detect no log mtime/size/tail progress after validation
   starts, take a final snapshot, and terminate only the task-owned torchrun
   process tree if the checkpoint marker and final checkpoint candidate are
   already present.
4. `SIGKILL` remains disallowed unless a later lead decision explicitly grants
   it for a specific process tree.
5. A timeout-terminated run is not `PASS_TRAINING`; it is a fail-closed salvage
   candidate only, with nonzero rc and residual risk.

## Concrete wrapper policy for later launch tasks

The later launch wrapper should record these files under the task-owned remote
run root and sync copies into the local output root:

| Artifact | Required behavior |
|---|---|
| `train_start.txt` | Written before launch. |
| `manifests/launch_command.txt` | Exact command/env, model path, packed root, checkpoint load/save, LR, steps, batch, TP/PP/EP/ETP, seed. |
| `manifests/preflight_summary.json` | Must include validation disposition and packed root counts before optimizer launch. |
| `logs/train_30b_sft.log` | Unbuffered log with heartbeat-compatible mtime/size. |
| `markers/latest_checkpointed_iteration.txt` | Must equal expected final iteration before checkpoint acceptance. |
| `train_rc.txt` | `0` is required for clean training closeout. Nonzero rc is fail-closed only. |
| `train_end.txt` | Always written after process exit. Missing file is a blocker. |
| `snapshots/final_pre_termination_snapshot_*.txt` | Required before any timeout-based signal. |
| `snapshots/final_post_termination_snapshot_*.txt` | Required after signal or natural exit. |
| `manifests/checkpoint_inventory.tsv` | Required for final checkpoint candidate. |
| `manifests/checkpoint_payload.sha256` | Required or explicitly deferred with remote path and reason if payload is too large to copy. |

Clean closeout requires all of the following:

- `train_rc.txt=0`;
- `train_end.txt` exists;
- latest checkpoint marker equals expected `train_iters`;
- final checkpoint directory exists and has inventory/hash evidence;
- no validation hang or timeout occurred;
- no retained task-owned training processes;
- GPUs are released or resource ownership is handed off with evidence;
- no shared files were deleted or overwritten.

Fail-closed stop conditions:

- validation log no progress for `1800` seconds after validation starts;
- missing `train_rc.txt` or `train_end.txt` after process exit;
- nonzero rc;
- NaN or skipped optimizer iteration;
- checkpoint marker missing or not equal to expected final iteration;
- checkpoint inventory/hash missing;
- retained training processes or unreleased GPUs after teardown;
- any attempt to use task255, AIME2025 prompt/label train rows, generic raw
  stage data without a reviewed packed contract, export, endpoint, promotion,
  benchmark eval, shared deletion, main push, or merge.

## Later implementation requirement

Task318 should not directly implement product code. A later lead-gated task is
required to do one of the following before another 30B optimizer launch:

1. Produce a task-owned train-only packed mirror and preflight proof for Route A;
   or
2. Add or wrap validation with the Route B timeout/heartbeat/rc/teardown policy
   and prove it without optimizer steps or eval rows.

Until that later task passes, future 30B training remains HOLD.

## Read-only commands run

Host:
`lg-cmc-b7r201-n09u29-cpu-000191`.

Commands were local/read-only except for writing this task report and status
docs:

```bash
git status --short --branch
git rev-parse HEAD
sed -n '1,220p' workspace/tasks/task318_qwen_all_sft_validation_exit_repair_preflight_s1/README.md
sed -n '1,240p' workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md
sed -n '1,220p' workspace/tasks/task313_qwen_all_sft_task310_checkpoint_salvage_review_s1/task310_checkpoint_salvage_review_report.md
git show origin/intern_nemotron_worker_5/task316_qwen_all_sft_repair_candidate_plan_s1:workspace/tasks/task316_qwen_all_sft_repair_candidate_plan_s1/all_sft_repair_candidate_plan.md
nl -ba src/nemotron/recipes/super3/stage1_sft/train.py | sed -n '430,560p'
nl -ba src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py | sed -n '1,180p'
nl -ba src/nemotron/recipes/super3/stage1_sft/config/m1_agentic_train.yaml | sed -n '1,170p'
cat /work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/manifests/preflight_summary.json
cat /work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/manifests/launch_command.txt
tail -n 90 /work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/logs/train_30b_sft.log
find /work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b/splits -type l -name '*.parquet'
sha256sum /work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/launch_train.sh /work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/manifests/preflight_summary.json /work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/manifests/launch_command.txt /work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/logs/train_30b_sft.log
gh pr view 377 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
gh pr view 371 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
```

## Residual risks

1. Route A intentionally skips built-in validation; the same-harness eval
   handoff must be explicit and lead-gated before any performance claim.
2. Route B is not proven in the current runtime; without an implementation task
   it can repeat the task310 hang.
3. Task311 benchmark evidence was context only in this task and was not
   independently re-reviewed here.
4. The current accepted task299 packed seed is sparse and narrow; task316 still
   recommends a separate data-blend repair before further all-SFT claims.
5. Any future timeout termination produces salvage evidence only, not a clean
   training pass.
