# task310 checkpoint salvage review report

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_4,SESSION=79 -->

Generated: 2026-06-03T15:54:00Z

## Disposition

Recommendation: `REQUEST_CHANGES_HEAD_MISMATCH`.

I did not approve the task310 checkpoint salvage handoff because PR #373 is no
longer at the assigned exact head. The task313 assignment and README require
review of PR #373 exact head
`7561a578f5f624cf1d3b85bef0dd8abb5c787533`, but GitHub reports current PR
#373 head `0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8`.

The assigned commit is present locally, and the drift from the assigned commit
to current #373 appears metadata-only:

- `workspace/interns/intern_nemotron_worker_5/status.md`
- `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/history_log.md`
- `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/task_knowledge.md`

`git diff --check 7561a578f5f624cf1d3b85bef0dd8abb5c787533..0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8`
returned clean. I am still treating this as a review HOLD because the scope was
to review an exact PR head, not to infer lead acceptance of a newer head.

Task311 checkpoint-load plus non-AIME canary must remain HOLD until lead
confirms the current exact #373 head for review, or confirms that the
`7561a578..0cbcb3c` drift may be included in the task313 review target.

## PR checks

| Check | Result |
|---|---|
| Target PR | #373 |
| Assigned exact head | `7561a578f5f624cf1d3b85bef0dd8abb5c787533` |
| Current PR head observed | `0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8` |
| PR state | `OPEN` |
| Base | `main` |
| Draft | `false` |
| Merge state | `CLEAN` |
| Mergeable | `MERGEABLE` |
| Current PR diff vs `origin/main` | docs/status-only for task310 and worker_5 status |

Current #373 diff vs `origin/main` includes:

- `workspace/interns/intern_nemotron_worker_5/status.md`
- `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/README.md`
- `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md`
- `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/history_log.md`
- `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/task_knowledge.md`

## Artifact observations

I only performed a presence/layout check before stopping on the exact-head
mismatch. I did not perform a full checksum or salvage approval review.

Observed local artifact root:

`/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z`

The root contains the expected high-level evidence groups:

- `launch_train.sh`
- `logs/preflight.log`
- `logs/train_30b_sft.log`
- `manifests/`
- `markers/latest_checkpointed_iteration.txt`
- `markers/train_end.txt`
- `markers/train_rc.txt`
- `snapshots/`
- `termination_signal_log.txt`

I also read the assigned-head task310 report header and confirmed it states
`TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`,
not a clean `PASS_TRAINING`.

## Commands

All commands were read-only except checking the lead task docs into this
task313 review branch and writing this task313 report/status.

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git worktree add -b intern_nemotron_worker_4/task313_qwen_all_sft_task310_checkpoint_salvage_review_s1 /work-agents/intern_nemotron_worker_4/Nemotron_task313 origin/main
git checkout origin/intern_nemotron_lead/session1-recovery-task-docs -- workspace/tasks/task313_qwen_all_sft_task310_checkpoint_salvage_review_s1
gh pr view 373 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url
git fetch origin pull/373/head:refs/remotes/origin/pr/373
git cat-file -t 7561a578f5f624cf1d3b85bef0dd8abb5c787533
git diff --name-status 7561a578f5f624cf1d3b85bef0dd8abb5c787533..0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8
git diff --check 7561a578f5f624cf1d3b85bef0dd8abb5c787533..0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8
git diff --name-status origin/main...origin/pr/373
find /work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z -maxdepth 2 -type f | sort | head -80
git show 7561a578f5f624cf1d3b85bef0dd8abb5c787533:workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md
```

## Boundary confirmation

I did not train, evaluate, export, create an endpoint, promote, merge, push
main, rewrite worker branches, delete shared files, use AIME2025 train data,
or use task255. I did not approve task311 release.

## Residual risks

- Current #373 head differs from the assigned exact review head.
- No full checksum validation has been performed by task313 yet.
- No checkpoint-load or non-AIME canary should be released from this report.
- The task310 evidence still carries the known `train_rc.txt=1`, validation
  hang, and missing accepted validation metric risks.
