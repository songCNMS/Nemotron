# task303 task301 salvage review report

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_4,SESSION=1 -->

## Decision

Decision:
`APPROVE_SALVAGE_CANDIDATE_FOR_LATER_NON_AIME_CANARY_CONSIDERATION_ONLY`.

The task301 `iter_0000035` checkpoint is reviewable enough for lead to consider
assigning a later bounded non-AIME canary task. This is not approval to merge
#362, not a clean training pass, not an export/endpoint/promotion clearance, and
not authorization for AIME/task243 eval or follow-on 30B work.

## Reviewed Inputs

- PR: #362
  `https://github.com/songCNMS/Nemotron/pull/362`
- Exact head:
  `c75c584875afdbdde4130775cbdc83355e7639ea`
- PR state at review: `OPEN`, base `main`, `CLEAN`, mergeable, non-draft.
- Task301 report:
  `workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/30b_full_sft_training_report.md`
- Local artifact root:
  `/work-agents/intern_nemotron_worker_5/outputs/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z`
- Remote artifact root:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z`

## Commands And Checks

Read-only commands included:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs intern_nemotron_worker_5/task301_qwen_aime_v11_30b_full_sft_training_s1
gh pr view 362 --json number,state,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,isDraft,files
git diff --name-status origin/main...c75c584875afdbdde4130775cbdc83355e7639ea
git diff --check origin/main...c75c584875afdbdde4130775cbdc83355e7639ea
git show c75c584875afdbdde4130775cbdc83355e7639ea:workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/30b_full_sft_training_report.md
jq . manifests/preflight_summary.json
sha256sum manifests/preflight_summary.json launch_command.txt logs/train_30b_sft.log manifests/final_pre_termination_snapshot.txt manifests/termination_signal_log.txt manifests/final_post_termination_snapshot.txt manifests/iter_0000035_inventory.tsv manifests/iter_0000035.sha256 manifests/salvage_selected_files.list manifests/salvage_artifact_inventory.tsv manifests/salvage_selected_files.sha256 manifests/salvage_manifest_files.sha256 manifests/train_rc.txt manifests/train_end.txt
sha256sum -c manifests/local_salvage_copied_files.sha256
ssh NemTron '... read-only remote root/file-count/hash checks ...'
ssh NemTron '... sha256sum -c manifests/salvage_selected_files.sha256; sha256sum -c manifests/salvage_manifest_files.sha256 ...'
python - <<'PY'
# parse train_30b_sft.log for iteration metrics, skipped iterations, NaN
# iterations, saved checkpoint, validation marker, and SIGTERM marker
PY
```

No training, canary, corrected AIME/task243 eval, export, endpoint, promotion,
follow-on 30B work, task255 reuse, AIME2025 train data use, shared deletion,
main push, merge, or worker_5 branch rewrite was performed.

## PR And Report Scope

#362 exact head `c75c584875afdbdde4130775cbdc83355e7639ea` contains:

- `workspace/interns/intern_nemotron_worker_5/status.md`
- task301 README/history/task_knowledge
- `workspace/tasks/task301_qwen_aime_v11_30b_full_sft_training_s1/30b_full_sft_training_report.md`

`git diff --check origin/main...c75c584875afdbdde4130775cbdc83355e7639ea`
passed. I found no product-code diff in #362.

## Launch And Preflight Evidence

Launch evidence matches the task301 report:

- Launch main: `e400cea8a1604bc95cc430a194811ff553b99401`.
- Model/tokenizer:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Pretrained checkpoint:
  `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`.
- Packed training data:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/input/task299_packed_qwen_30b_deref_mirror/splits`.
- 8x H200 launch with `CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7`.
- TP `4`, PP `2`, EP `4`, ETP `1`, sequence parallel enabled.
- `train.train_iters=35`, global batch `8`, micro batch `1`.
- LR `5e-7`, min LR `1e-7`, warmup `4`, decay `35`.
- `checkpoint.save_interval=5`, `checkpoint.load=null`, seed `5678`.
- `preflight_rc=0`; `preflight_summary.json` reports `preflight=PASS`.

The task299 packed mirror evidence is internally consistent:

- Source and remote raw manifest hashes match:
  `a5b05d1e3a8ea2724e09058e3e7646ae5c1d499adb93be12d28eca78ce73190b`.
- Source and remote dereferenced manifest hashes match:
  `d80241a9c659c2546591c27941e7c24c32717983250df38c0254113cd28bfc6c`.
- Dereferenced mirror: `391` files, `0` symlinks.

## Training Loop Evidence

The local copied log hash matches the report:
`e832845262135dca009d1373f8eeb04a6f3b18e5079f40a6456f20b999b49863`.

Programmatic log parsing found:

- metric rows: `35`
- first iteration: `1`
- last iteration: `35`
- skipped iteration sum: `0`
- NaN iteration sum: `0`
- non-finite losses: none
- `successfully saved checkpoint from iteration      35`: present
- `[after training is done]`: present
- validation hang markers `Evaluating on 80 samples` and
  `Evaluating iter 1/10`: present
- SIGTERM markers: present

The final training loop is therefore complete through `35/35`, but validation
did not complete.

## Termination And Release Evidence

The final pre-termination snapshot shows:

- `train_rc.txt`: missing
- `train_end.txt`: missing
- log stopped at validation: `Evaluating on 80 samples` /
  `Evaluating iter 1/10`
- `latest_checkpointed_iteration.txt`: `35`
- `iter_0000035`: present, `399G`, `28` files

Termination evidence:

- lead-cleared `SIGTERM` to torchrun parent PID `1258209`
- no SIGKILL recorded
- `train_rc.txt`: `1`
- `train_end.txt`: `2026-06-02T16:58:51Z`

Remote post-check over SSH found:

- remote root present
- `latest_checkpointed_iteration.txt`: `35`
- `train_rc.txt`: `1`
- `train_end.txt`: `2026-06-02T16:58:51Z`
- no matching task301 processes
- eight H200 GPUs at `0 %`, `1 MiB`

This supports process/GPU release after the salvage termination.

## Checkpoint And Manifest Evidence

Remote root verification:

- checkpoint path:
  `/root/task301_qwen_aime_v11_30b_full_sft_training_s1/run_20260602T155725Z/checkpoints/iter_0000035`
- checkpoint file count: `28`
- checkpoint size: `399G`
- `iter_0000035.sha256` lines: `28`
- `iter_0000035_inventory.tsv` lines: `29` including header

Manifest hashes matched the report:

| Artifact | sha256 |
|---|---|
| `manifests/iter_0000035.sha256` | `c3f2d4b4b5d1c26041d96e5eb8799cf591acef346f75ebfdcdce40a12ec09c03` |
| `manifests/iter_0000035_inventory.tsv` | `7c7e60b5bf9a5e747e3115e37701da00b6643cd1c895e3336bef175dc6d13261` |
| `manifests/salvage_selected_files.sha256` | `1b2a767f72c64764cc481735ac1d2ab1825f92adf6e14ec671a61cae01663692` |
| `manifests/salvage_manifest_files.sha256` | `bf44b0a0bf4a779c66bb1da7f0e9833a858816d9af1b5b7086d9b6ded65ba04e` |
| `logs/train_30b_sft.log` | `e832845262135dca009d1373f8eeb04a6f3b18e5079f40a6456f20b999b49863` |
| `train_rc.txt` | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` |
| `train_end.txt` | `42ffcab01712e58025acf93d78b966fe591b16c1f77e58fd24d33f0c3d22ac36` |

Remote selected-file verification passed:

- `sha256sum -c manifests/salvage_selected_files.sha256`: all selected files OK
- `sha256sum -c manifests/salvage_manifest_files.sha256`: all manifest files OK

Local copied salvage bundle verification passed:

- `sha256sum -c manifests/local_salvage_copied_files.sha256`: all local copied
  artifacts OK

I did not recompute the full `iter_0000035.sha256` against all 399G of
checkpoint shards during this review. The review verified the remote checkpoint
presence, file count, size, inventory manifest hash, checksum manifest hash, and
selected salvage file hashes. Actual checkpoint load remains a later canary or
runtime gate.

## Boundary Review

No evidence of the following was found in the reviewed task301 report/artifacts:

- task255 reuse
- AIME2025 prompt/label train rows
- shared deletion
- corrected AIME/task243 eval
- non-AIME canary
- export
- endpoint
- promotion
- direct main push
- merge

The report wording correctly says the artifact is a
`TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`
and not a clean training pass.

## Residual Risks

- `train_rc=1` because the run was terminated by lead-cleared SIGTERM during
  validation.
- Built-in validation did not complete; no validation metric is available.
- The checkpoint has not been loaded by an independent canary or runtime task.
- Full 399G checkpoint data hashes were not independently recomputed in this
  review.
- No eval/export/endpoint/promotion path is cleared.
- Future non-AIME canary must treat `iter_0000035` as a salvage candidate and
  fail closed if checkpoint load, tokenizer/config, or prompt retention checks
  fail.

## Final Verdict

Approve as salvage-candidate evidence only. Lead may consider assigning a later
bounded non-AIME canary task against `iter_0000035`, but #362 should not be
treated as a clean training PASS and no merge/promotion/eval/export/endpoint
clearance is implied.
