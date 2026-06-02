# task301 30B Full SFT Training Report

<!-- METADATA:STATUS=Blocked,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

Generated: 2026-06-02T14:42:19Z

## Disposition

Recommendation: `BLOCKED_UPSTREAM_GATES_MISSING`.

Task301 was accepted, but no 30B full SFT training was launched. The task docs
require all of the following before launch:

- task298 PASS runtime/resource/base-load proof;
- task299 PASS 30B data/packing root and decontamination proof;
- task300 30B same-harness base-score artifact before any FT judgment.

At the Session 3 refresh, task298, task299, and task300 branches are visible,
but the required PASS/base-score gate artifacts are not visible. The safe action
is to hold launch and report the blocker.

## Branch And Sources

| Item | Value |
|---|---|
| Worker branch | `intern_nemotron_worker_5/task301_qwen_aime_v11_30b_full_sft_training_s1` |
| PR | #362 `https://github.com/songCNMS/Nemotron/pull/362` |
| Branch base | `origin/main` `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7` |
| Lead docs source | `origin/intern_nemotron_lead/session1-recovery-task-docs` `676d85563e00dfb665b6a911995bd47b4932c370` |
| Task docs path | `workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/` |
| Intended report path | `workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/30b_full_sft_training_report.md` |

## Upstream Gate Visibility

| Gate | Required evidence | Visibility result | Launch decision |
|---|---|---|---|
| task298 | PASS runtime/resource/base-load proof for 30B | Branch visible at `7d24b9295740ef5c21fd443d6399ec9641f8f5c5`; docs `InProgress`; no exact-branch PR and no PASS report visible | BLOCK |
| task299 | PASS 30B data/packing root and decontamination proof | Branch visible at `ff30fad8e6899b9a98d9530006ef49c52c7d72fb`; docs `InProgress`; no exact-branch PR and no PASS report visible | BLOCK |
| task300 | 30B base-score artifact before any FT judgment | Branch visible at `85a5ba134c486ac36f30b63e9bcae97f51fdc1f6`; docs `InProgress`; no exact-branch PR and no base-score report visible | BLOCK |

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
git log --oneline --max-count=20 origin/main
```

These checks were read-only. They did not launch training, allocate 30B
resources, mutate artifacts, or delete shared files.

## Commands And Environment

No training command was executed.

Planned command/env fields remain unbound because the required upstream gates
are absent:

- model path: blocked pending task298;
- 30B packed root: blocked pending task299;
- base comparator artifact: blocked pending task300;
- LR, train steps, optimizer, parallelism, GPU count/type, validation settings,
  seed, resume policy, checkpoint root, and log root: blocked pending the
  upstream gate artifacts and lead review.

## Artifact Status

No checkpoint, loss/LR, validation, checksum, or task300 handoff artifacts were
created by this session.

## Boundary Confirmation

Confirmed for Session 1:

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

1. task298 PASS runtime/resource/base-load proof is not visible; only an
   `InProgress` branch at `7d24b9295740ef5c21fd443d6399ec9641f8f5c5` is
   visible.
2. task299 PASS 30B data/packing/decontamination proof is not visible; only an
   `InProgress` branch at `ff30fad8e6899b9a98d9530006ef49c52c7d72fb` is
   visible.
3. task300 30B base-score artifact is not visible; only an `InProgress` branch
   at `85a5ba134c486ac36f30b63e9bcae97f51fdc1f6` is visible.
4. Without the above exact gate refs and artifacts, training launch would violate
   the task301 fail-closed contract.
