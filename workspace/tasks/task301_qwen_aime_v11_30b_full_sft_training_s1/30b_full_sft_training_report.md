# task301 30B Full SFT Training Report

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=9 -->

Generated: 2026-06-02T15:35:12Z

## Disposition

Recommendation: `BLOCKED_UPSTREAM_GATES_MISSING`.

Task301 was accepted, but no 30B full SFT training was launched. Current lead
gate state requires all of the following before launch:

- task298 runtime route lead approval with residuals carried;
- task299/#365 final 30B data/decontam approval merged and carried;
- task300 30B same-harness base-score artifact before any FT judgment;
- explicit lead sequence clearance.

At the Session 9 refresh, lead reports task299/#365 is merged into `main` at
`205fc919a643b1478964a9e91793247c5e821a38`; runtime and data gates are carried.
Task301 remains HOLD until task300 provides an accepted same-harness 30B base
AIME score artifact and lead gives explicit launch clearance. The safe action is
to hold launch and report the remaining blocker.

## Branch And Sources

| Item | Value |
|---|---|
| Worker branch | `intern_nemotron_worker_5/task301_qwen_aime_v11_30b_full_sft_training_s1` |
| PR | #362 `https://github.com/songCNMS/Nemotron/pull/362` |
| Branch base | `origin/main` `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7` |
| Current observed `origin/main` | `205fc919a643b1478964a9e91793247c5e821a38` after task299/#365 merge |
| Lead docs source | `origin/intern_nemotron_lead/session1-recovery-task-docs` `676d85563e00dfb665b6a911995bd47b4932c370` |
| Task docs path | `workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/` |
| Intended report path | `workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/30b_full_sft_training_report.md` |

## Upstream Gate Visibility

| Gate | Required evidence | Visibility result | Launch decision |
|---|---|---|---|
| task298 | Runtime/resource/base-load route for 30B | Lead update reports runtime route approved with residuals; not an active launch blocker after Session 6 | CARRIED |
| task299 | Lead-approved final 30B data/decontam proof merged or otherwise closed out | PR #365 is MERGED from head `b8b760fb8f46cda8f302adbea106f19cc234e038` with merge commit `205fc919a643b1478964a9e91793247c5e821a38` | CARRIED |
| task300 | Accepted 30B same-harness base AIME score artifact before any FT judgment | PR #363 is OPEN at head `a54fb96e3159ce1a1bc16d2b2c52cf12d553fbe5`; branch report remains blocked and no accepted base-score artifact is available to task301 | BLOCK |
| lead clearance | Explicit sequence clearance for task301 launch | Not granted; lead states full 30B SFT remains HOLD | BLOCK |

## Read-Only Checks

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git rev-parse origin/main origin/intern_nemotron_lead/session1-recovery-task-docs
git ls-tree -r --name-only origin/intern_nemotron_lead/session1-recovery-task-docs workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1
git show origin/intern_nemotron_lead/session1-recovery-task-docs:workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/README.md
git ls-remote --heads origin '*task298*' '*task299*' '*task300*' '*task301*'
git rev-parse origin/intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1 origin/intern_nemotron_worker_1/task299_qwen_aime_v11_30b_data_packing_contract_s1 origin/intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1 origin/main
gh pr list --state all --search task298 --json number,state,headRefName,headRefOid,mergeable,title,url,mergedAt,updatedAt --limit 10
gh pr list --state all --search task299 --json number,state,headRefName,headRefOid,mergeable,title,url,mergedAt,updatedAt --limit 10
gh pr list --state all --search task300 --json number,state,headRefName,headRefOid,mergeable,title,url,mergedAt,updatedAt --limit 10
gh pr list --state all --search task301 --json number,state,headRefName,headRefOid,mergeable,title,url,mergedAt,updatedAt --limit 10
gh pr list --state all --head intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1 --json number,state,headRefName,headRefOid,mergeable,title,url,mergedAt,updatedAt --limit 10
gh pr list --state all --head intern_nemotron_worker_1/task299_qwen_aime_v11_30b_data_packing_contract_s1 --json number,state,headRefName,headRefOid,mergeable,title,url,mergedAt,updatedAt --limit 10
gh pr list --state all --head intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1 --json number,state,headRefName,headRefOid,mergeable,title,url,mergedAt,updatedAt --limit 10
git ls-tree -r --name-only origin/main workspace/tasks | rg 'task(298|299|300|301)'
git ls-tree -r --name-only origin/intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1 workspace/tasks/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1
git ls-tree -r --name-only origin/intern_nemotron_worker_1/task299_qwen_aime_v11_30b_data_packing_contract_s1 workspace/tasks/task299_qwen_aime_v11_30b_data_packing_contract_s1
git ls-tree -r --name-only origin/intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1 workspace/tasks/task300_qwen_aime_v11_30b_same_harness_testing_s1
gh pr view 365 --json state,baseRefName,headRefOid,mergeStateStatus,mergeable,isDraft,url,mergedAt
gh pr list --state all --head intern_nemotron_worker_3/task300_qwen_aime_v11_30b_same_harness_testing_s1 --json number,state,headRefName,headRefOid,mergeable,title,url,mergedAt,updatedAt --limit 10
git log --oneline --max-count=20 origin/main
```

These checks were read-only. They did not launch training, allocate 30B
resources, mutate artifacts, or delete shared files.

## Commands And Environment

No training command was executed.

Planned command/env fields remain unbound because required upstream gates and
lead launch clearance are absent:

- runtime/model route: task298 approved with residuals, but not enough for
  launch by itself;
- 30B packed root: task299/#365 is carried by merge commit
  `205fc919a643b1478964a9e91793247c5e821a38`, but launch command binding still
  waits on task300 and lead clearance;
- base comparator artifact: blocked pending task300;
- LR, train steps, optimizer, parallelism, GPU count/type, validation settings,
  seed, resume policy, checkpoint root, and log root: blocked pending the
  remaining upstream gate artifacts and lead launch clearance.

## Artifact Status

No checkpoint, loss/LR, validation, checksum, or task300 handoff artifacts were
created by this session.

## Boundary Confirmation

Confirmed through Session 9:

- no task255 reuse;
- no AIME2025 prompts or labels as trainable data;
- no deletion under `/mnt/cephfs/data/processing/lei.song`;
- no export for promotion;
- no endpoint launch or endpoint promotion;
- no main push;
- no merge;
- no 30B training launch;
- no 8-GPU execution.

## Blockers

1. task300 30B same-harness base AIME score artifact is not accepted; task300
   PR #363 is open at `a54fb96e3159ce1a1bc16d2b2c52cf12d553fbe5` and its
   branch report remains blocked.
2. Lead has not cleared the task301 launch sequence.
3. Without the above exact gate refs, artifacts, and lead clearance, training
   launch would violate the task301 fail-closed contract.
