# task310 Qwen all-SFT 30B full training report

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=3 -->

## Disposition

`BLOCK_PRETRAINING_GATE`.

No Qwen3-30B-A3B all-SFT training was launched. The task310 launch gate requires
task308 `PASS_AUDIT`, task309 `PASS_PACKED_CONTRACT`, and a valid current 30B
runtime/resource route. Task308 PR #374 now exists with constrained audit
evidence, but task309 PR #372 still needs a refresh from #374 and no accepted
`PASS_PACKED_CONTRACT` is visible, so task310 remains fail-closed before any
training command.

## Checked revisions

- Current `origin/main`: `172cd0e7ceaba8ad2b412d1145441dbb4c5fd122`.
- Product-code baseline carried by lead:
  `ecb14173a820df377270273b9f7d9d92cb5076d2`.
- Lead docs branch:
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `9f838e94feccd0aad4b916dc8f29a6e4d0c80133`; requested task310 refresh
  commit `5f4167dc` is an ancestor and has no further task310 diff at current
  lead head.
- Task310 worker branch:
  `intern_nemotron_worker_5/task310_qwen_all_sft_30b_full_training_s1`.
- Task310 PR #373:
  open/CLEAN at `1cd3eb17fc686b281da7a9a0791ea09fbe614664`.
- Target model path, unchanged and not downgraded:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.

## Upstream gate findings

| Gate | Required state | Observed state | Task310 effect |
|---|---|---|---|
| task308 all-SFT pipeline inventory audit | `PASS_AUDIT` with inventory report and accepted evidence | PR #374 is open/CLEAN at `f57384f6a298500f240a9367c3598cd5f9a59638`; report decision is `PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS`; task308 recommends task309 fail closed for unmaterialized generic `stage1_sft/data_blend_raw` until those sources are materialized, counted, decontam scanned, and Qwen-packed | Does not release training alone |
| task309 all-SFT packed-data contract | `PASS_PACKED_CONTRACT` with packed root, manifests, decontam proof, checksums, and accepted evidence | PR #372 is open/CLEAN at `998ebce439164af2cc0e026575de32cd356acaa0`; report disposition still says `BLOCK_DEPENDENCY_TASK308_INVENTORY_MISSING` and references pre-#374 task308 state, so it must refresh from task308 #374 before task310 can use it | Blocks training |
| task298 30B runtime/resource/base-load | Valid 30B route or refreshed equivalent | Merged evidence on main records `PASS_RUNTIME_RESOURCE_BASE_LOAD_GATE_WITH_TRAINING_LAUNCH_RESIDUALS`, model path exists, host `lg-cmc-b7r201-f08u26-h200-000126`, 8x H200, Bridge import rc `0`, import root `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0` | Carried as prior route evidence, but insufficient without task308/task309 |
| task300 30B base comparator | Accepted base comparator for any future judgment | Merged evidence on main records base `15/30 = 0.5` for `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` | Reference only; not a training launch gate substitute |
| task301/task306 previous 30B FT attempt | Must not be reused as success evidence | task301 was salvage closeout only; task306 measured task301 FT `14/30 = 0.4666666666666667`, below task300 base `15/30 = 0.5`, disposition `FAIL` | Confirms previous checkpoint is not a promotion/training-success basis |
| task311/task312 downstream gates | Wait for task310 handoff/evidence | Branches exist for task311 at `dd59d5448c44ba9d04facd2af2ddc4a02b54f899` and task312 at `21bfe2045ec5270775239eecf9474f6044272e7c` as acceptance/planning docs | No effect until task310 produces a usable checkpoint |

## Commands and checks run

Read-only repository and PR visibility checks:

```bash
git fetch origin main
git fetch origin intern_nemotron_lead/session1-recovery-task-docs
git merge-base --is-ancestor 5f4167dc origin/intern_nemotron_lead/session1-recovery-task-docs
git diff --name-status 5f4167dc origin/intern_nemotron_lead/session1-recovery-task-docs -- workspace/tasks/task310_qwen_all_sft_30b_full_training_s1
git rev-parse origin/main origin/intern_nemotron_lead/session1-recovery-task-docs
git ls-tree -r --name-only origin/main workspace/tasks | rg 'task(298|300|301|306|308|309|310|311|312)'
git ls-remote --heads origin '*task308*' '*task309*' '*task310*' '*task311*' '*task312*'
gh pr list --state all --search 'task308 OR task309 OR task310 OR task311 OR task312' --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,title
gh pr list --state open --limit 200 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,title | jq '.[] | select(.headRefName|test("task30[89]|task31[012]"))'
gh pr view 372 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,isDraft,url,title
gh pr view 373 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,isDraft,url,title
gh pr view 374 --json number,state,headRefName,headRefOid,baseRefName,mergeStateStatus,isDraft,url,title
```

Read-only upstream branch inspections:

```bash
git fetch origin intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1:refs/remotes/origin/intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1
git fetch origin intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1:refs/remotes/origin/intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1
git fetch origin intern_nemotron_worker_3/task311_qwen_all_sft_benchmark_eval_s1:refs/remotes/origin/intern_nemotron_worker_3/task311_qwen_all_sft_benchmark_eval_s1
git fetch origin intern_nemotron_worker_4/task312_qwen_all_sft_independent_review_runbook_s1:refs/remotes/origin/intern_nemotron_worker_4/task312_qwen_all_sft_independent_review_runbook_s1
git ls-tree -r --name-only origin/intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1 workspace/tasks/task308_qwen_all_sft_pipeline_inventory_audit_s1 workspace/interns/intern_nemotron_worker_1/status.md
git ls-tree -r --name-only origin/intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1 workspace/tasks/task309_qwen_all_sft_packed_data_contract_s1 workspace/interns/intern_nemotron_worker_2/status.md
git show origin/intern_nemotron_worker_1/task308_qwen_all_sft_pipeline_inventory_audit_s1:workspace/interns/intern_nemotron_worker_1/status.md
git show origin/intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1:workspace/interns/intern_nemotron_worker_2/status.md
git show origin/main:workspace/tasks/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/30b_runtime_resource_base_load_report.md
git show origin/main:workspace/tasks/task300_qwen_aime_v11_30b_same_harness_testing_s1/30b_base_aime2025_report.md
git show origin/main:workspace/tasks/task306_qwen_aime_v11_30b_task301_same_harness_aime_eval_s1/30b_task301_same_harness_aime_eval_report.md
git show f57384f6a298500f240a9367c3598cd5f9a59638:workspace/tasks/task308_qwen_all_sft_pipeline_inventory_audit_s1/all_sft_pipeline_inventory_audit_report.md
git show 998ebce439164af2cc0e026575de32cd356acaa0:workspace/tasks/task309_qwen_all_sft_packed_data_contract_s1/all_sft_packed_data_contract_report.md
```

## Launch status

No launch was attempted.

| Requested launch field | Value |
|---|---|
| Training command/env | Not applicable because the pretraining gate is blocked |
| GPUs/parallelism | Not allocated |
| LR/steps/seed | Not selected for execution |
| Loss/validation metrics | Not produced |
| Checkpoint/log roots | Not produced |
| Checksums/artifact inventory | This report is the only task310 artifact so far |
| task311 handoff | Blocked until task310 has a usable checkpoint |

## Boundary assessment

- No training, optimizer step, evaluation, canary, export, endpoint, promotion,
  or product-code edit was performed.
- No AIME2025 prompt or label rows were used for training.
- No task255 artifacts were used.
- No files under `/mnt/cephfs/data/processing/lei.song` were deleted or
  overwritten.
- No direct push to main or merge was performed.
- No model-path downgrade or substitution was made.

## Residual risk and unblock conditions

Task310 remains blocked until task308 publishes and receives acceptance for a
complete all-SFT pipeline inventory audit and task309 publishes and receives
acceptance for the packed-data contract. The current additional blocker is that
task309 #372 must refresh from task308 #374 and produce accepted
`PASS_PACKED_CONTRACT` evidence. After those gates pass, task310 should refresh
the 30B runtime/resource assumptions against the current main and exact packed
root before launching.
