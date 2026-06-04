# task336 independent review of task335/#398

<!-- METADATA:STATUS=ReadyForPR,DISPOSITION=APPROVE_TASK335_BLOCKER_DOCS_CLOSEOUT,SESSION=1 -->

Generated: 2026-06-04T09:29:39Z

## Decision

`APPROVE_TASK335_BLOCKER_DOCS_CLOSEOUT` for #398 exact head
`0a094483458f01813b50e4fb13e2ddefdbdc4517`.

The reviewed evidence supports accepting #398/task335 as no-training
fail-closed blocker documentation. The data/model/resource/Qwen-contract/
validation-route subchecks are documented and checksum-backed, while the launch
remains blocked by the exact NemTron runtime import failure:

`megatron.bridge.recipes.qwen.qwen3_moe` -> `ModuleNotFoundError("No module named 'megatron.energon'")`.

This approval is blocker-docs closeout only. It does not release task310, 30B
training, optimizer steps, eval, export, endpoint, promotion, task255 reuse,
AIME2025 train rows, shared deletion, main push, merge, or self-merge.

## Target Reviewed

- PR: #398 `https://github.com/songCNMS/Nemotron/pull/398`
- Exact head reviewed: `0a094483458f01813b50e4fb13e2ddefdbdc4517`
- PR state observed: `OPEN`, non-draft, base `main`, `CLEAN`/`MERGEABLE`
- Base observed: `origin/main` `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`
- Local artifact root:
  `/work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z`
- Report reviewed:
  `workspace/tasks/task335_qwen_all_sft_task333_30b_launch_preflight_s1/task333_30b_launch_preflight_report.md`

## Commands And Checks

Commands were run from
`/work-agents/intern_nemotron_worker_4/Nemotron_task336` unless noted.

```bash
git fetch origin main +pull/398/head:refs/remotes/origin/pr/398
gh pr view 398 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url,title
git diff --name-status origin/main...origin/pr/398
git diff --check origin/main...origin/pr/398
tmp=$(mktemp -d)
git show origin/pr/398:workspace/tasks/task335_qwen_all_sft_task333_30b_launch_preflight_s1/build_task335_30b_launch_preflight.py > "$tmp/build_task335_30b_launch_preflight.py"
PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile "$tmp/build_task335_30b_launch_preflight.py"
rm -rf "$tmp"
cd /work-agents/intern_nemotron_worker_2/outputs/task335_qwen_all_sft_task333_30b_launch_preflight_s1/run_20260604T090300Z
sha256sum -c manifests/artifact_checksums.sha256
sha256sum -c manifests/train_only_shard_checksums.sha256
python3 <read-only JSON manifest and split exposure summary>
tail -n 80 logs/remote_no_training_preflight_probe.log
```

Results:

- #398 exact head is
  `0a094483458f01813b50e4fb13e2ddefdbdc4517`.
- Diff scope is limited to worker_2 status plus task335 README/history/
  task_knowledge, task-local helper, and task335 report.
- `git diff --check origin/main...origin/pr/398`: clean.
- Helper compile from PR head: `PASS`.
- `sha256sum -c manifests/artifact_checksums.sha256`: `PASS`, 16 entries.
- `sha256sum -c manifests/train_only_shard_checksums.sha256`: `PASS`, 84
  train-only shard entries.
- `remote_no_training_preflight_probe` log ends with
  `TASK335_REMOTE_PREFLIGHT=BLOCK`.

## Artifact And Checksum Verdict

Important artifact checksums match the task335 report and local manifests:

- `manifests/final_summary.json`:
  `80a4ddce65f43af87ff269b760db73e5520644b9c528530f2e0df267b9968b6d`.
- `manifests/artifact_checksums.sha256`:
  `fedeea0f279cd716ed24d7c352a464b010e7577876d75bb5d156ade292665297`.
- `manifests/remote_no_training_preflight_probe.json`:
  `cf0cacc2a42c3e13a8677edcdfd804f27f97e5b7b1cc2b57a5369304409560d8`.
- `manifests/later_launch_contract.json`:
  `476b28337526d2057278f82de8e0917b9b33e418d75ac15adda8a8a81c860d6b`.
- `logs/remote_no_training_preflight_probe.log`:
  `8fa6724d984d38402324f6a3e91e2ba53a95fd11fcb3eb46b9a3dd925616a210`.
- `manifests/train_only_shard_checksums.sha256`:
  `e5abfbdfebe341b8f346c17f33f4b95ff8fe5750411a40efac1b079fa66bb937`.

The checksum manifests validate the files and train-only shards in the assigned
artifact root. I did not modify task335 artifacts.

## Passing Subchecks

The final summary and probe manifests support these pass conditions:

- Final disposition: `BLOCK_LAUNCH_PREFLIGHT`.
- Remote probe disposition: `BLOCK_RUNTIME_MISSING_IMPORT`.
- Qwen3-30B model path exists:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Model metadata: `model_type=qwen3_moe`,
  architecture `Qwen3MoeForCausalLM`.
- Tokenizer chat template present; tokenizer/model probing used
  `trust_remote_code=false`.
- task333 full packed root exists and exposes train/valid/test as 84/6/6.
- task333 artifact checksum rc `0`, packed shard checksum rc `0`, and accepted
  Qwen3-30B packed contract pass are carried in the local probe.
- Task-owned train-only launch view exposes 84 train parquet files and 0
  valid/test parquet files.
- Train-only metrics: 78,168 rows, 300,046,415 input tokens,
  33,477,337 supervised tokens, 154,008,682 bytes.
- Remote Qwen packed/training contract status: `PASS`.
- Validation route: `valid_parquet_count=0`,
  `do_validation_expected=false`, source contains the `has_validation_data =
  False` route and returns `do_validation=has_validation_data`.
- GPU resource probe: 8 NVIDIA H200 GPUs, each 143,771 MiB, 0% observed
  utilization during the probe.
- Later launch contract is no-training preflight only and keeps required
  placeholders unset for train iters, LR/min LR/warmup/save interval, and
  lead-approved Bridge checkpoint path.

## Blocker Verdict

The exact blocker is correctly classified:

- `megatron`: `PASS`
- `megatron.bridge`: `PASS`
- `megatron.bridge.training.config`: `PASS`
- `torch`: `PASS`
- `omegaconf`: `PASS`
- `nemotron.recipes.super3.stage1_sft.qwen3_30b_a3b_local_train`: `PASS`
- `nemotron.recipes.super3.stage1_sft.qwen_chat_contract`: `PASS`
- `megatron.bridge.recipes.qwen.qwen3_moe`: `FAIL`

Failure:
`ModuleNotFoundError("No module named 'megatron.energon'")`.

This supports `BLOCK_LAUNCH_PREFLIGHT` and keeps task310/all-SFT 30B launch on
HOLD until a later lead-approved runtime remediation makes the Qwen3 MoE Bridge
recipe import successfully in the same task-owned NemTron `/root` sync route.

## Consistency Notes

- The artifact command-env manifest records worker_2 branch head
  `76227ae1ccf483579f19a3288778ced2f32262c6`, while #398 exact head is
  `0a094483458f01813b50e4fb13e2ddefdbdc4517`.
- I checked `76227ae1..0a094483`: the drift is task335 docs/status/report/
  helper publication, and `git diff --check` is clean.
- The remote synced repo used for runtime debug is current main
  `76b9ebf98e623cb85075378ca9980ba6ee11c8ed`, matching the task335 report.

## Residual Risks

- This is blocker evidence only; no actual optimizer/training launch happened.
- The later launch template is intentionally not runnable without lead-supplied
  placeholders and a lead-approved imported Bridge checkpoint path.
- The task-owned train-only view intentionally omits valid/test shards to keep
  validation disabled; future training must preserve that fail-closed route or
  rerun an equivalent no-training preflight.
- The runtime remains unusable for launch until `megatron.energon` is available
  in the NemTron route and `megatron.bridge.recipes.qwen.qwen3_moe` imports.
- Any future checkpoint, canary, or same-harness eval requires separate lead
  assignment and independent review.

## Boundary Confirmation

Confirmed from the report/manifests and my own actions:

- No task335 artifact or worker_2 branch mutation.
- No optimizer steps or training loop.
- No benchmark eval, AIME eval, or task243 eval.
- No export, endpoint, promotion, 30B release, or task310 release.
- No task255 reuse and no AIME2025 train rows.
- No shared deletion/mutation.
- No main push, merge, or self-merge.
