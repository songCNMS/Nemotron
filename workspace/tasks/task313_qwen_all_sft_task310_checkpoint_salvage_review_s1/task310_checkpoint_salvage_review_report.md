# task310 checkpoint salvage review report

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nemotron_worker_4,SESSION=80 -->

Generated: 2026-06-03T17:22:00Z

## Disposition

Recommendation:
`APPROVE_SALVAGE_HANDOFF_TO_TASK311_LOAD_CANARY_ONLY`.

I reviewed PR #373 at current exact head
`0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8` and the task310 local/remote
artifacts. The evidence is internally consistent for a checkpoint salvage
candidate handoff to task311 checkpoint-load plus non-AIME canary only.

This is not a clean `PASS_TRAINING`. It does not authorize benchmark eval,
AIME/task243 eval, export, endpoint, promotion, additional training, task255
reuse, AIME2025 train data, shared deletion, main push, or merge of #373 by
worker_4. Task311 should proceed only if lead explicitly releases it after this
review.

## Reviewed heads and drift

| Item | Result |
|---|---|
| Lead docs | `origin/intern_nemotron_lead/session1-recovery-task-docs` `c085e1693a4fca9e4444fb64a85ab0193b03d3ce` |
| Current main | `004870e7d790778b5cdae5cc574257fdc19ec755` |
| Review PR | #373 |
| #373 state | `OPEN`, base `main`, non-draft, `CLEAN/MERGEABLE` |
| #373 exact head reviewed | `0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8` |
| Worker review PR | #376 |
| #376 prior head before this refresh | `1a05dda17a6d1fe6b2ebb85ca7662d5d7d1f4fb7` |

The required drift range
`7561a578f5f624cf1d3b85bef0dd8abb5c787533..0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8`
is bookkeeping-only:

- `workspace/interns/intern_nemotron_worker_5/status.md`
- `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/history_log.md`
- `workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/task_knowledge.md`

`git diff --check` for the drift range returned clean, and
`all_sft_30b_full_training_report.md` is byte-identical across the range:
`e49895ccfa7a815bbf80a60d68d00f8e4e2eccc8ead5948b040581c287068392`.

Current #373 diff versus `origin/main` is docs/status-only for worker_5 status
and task310 README/report/history/task_knowledge. No product code is changed.

## Artifact paths

| Item | Path |
|---|---|
| Local evidence root | `/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z` |
| Remote run root | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z` |
| Remote checkpoint candidate | `/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035` |
| Training log | `logs/train_30b_sft.log` |
| Termination log | `termination_signal_log.txt` |
| Checkpoint inventory | `manifests/iter_0000035_inventory.tsv` |
| Checkpoint payload manifest | `manifests/iter_0000035.sha256` |

Remote checkpoint candidate exists on host
`lg-cmc-b7r201-f08u26-h200-000126`, is reported by `du -sh` as `399G`, and
contains `28` files. The local evidence root intentionally does not contain a
399G copied checkpoint payload; checkpoint payload validation was performed
read-only on the remote run root.

## Checksum results

| Evidence | Expected / observed sha256 | Result |
|---|---:|---|
| `manifests/preflight_summary.json` | `cff95dc1c07325b9192677670d68fe3b64a54759919879c5ce5db0b82d1b10b3` | PASS local and remote |
| `manifests/launch_command.txt` | `c50bdeca383359aa6656884df707089321813efbf36bd01933e2b58389910777` | PASS local and remote |
| `manifests/iter_0000035_inventory.tsv` | `b30d83f641118da8d7a24438e6c379ba9a5e8e03793ef5ff26514d751d9fa676` | PASS local and remote |
| `manifests/iter_0000035.sha256` | `8cb4e7856f379bc7f1d63d407582bd63981b61c9f346455aa40fb389ef73cbe8` | PASS local and remote |
| `snapshots/final_pre_termination_snapshot_20260603T163524Z.txt` | `700f72dd76ebc1b179da38ed711d7e7651cef862ff2aadaf2d7b722661f20b25` | PASS local copied evidence |
| `termination_signal_log.txt` | `81428d3b12cab8a465344d416e3e818af260deafee4c87cff6bcc6279c761643` | PASS local and remote |
| `manifests/final_local_copied_evidence.sha256` | `ab102b7647ab30498ea7f482dd7a7582d6139f1c8b8ee0709cc2ded12de1f189` | PASS actual manifest hash |
| Remote checkpoint payload files | `manifests/iter_0000035.sha256` | PASS, all 28 files OK from `checkpoints/iter_0000035` |

`sha256sum -c manifests/final_local_copied_evidence.sha256` from the local
evidence root fails on the manifest's self-entry only. The manifest file's
actual sha256 matches the lead-reported `ab102...` value, and all non-self
entries in that manifest pass. I treat this as a residual manifest-construction
quirk, not checkpoint corruption.

## Training and termination review

Training evidence supports a bounded salvage candidate:

- Training log contains exactly `35` optimizer iteration lines through
  iteration `35/35`.
- Parsed LM losses are finite for all 35 iterations.
- Parsed skipped iterations are `0` for all 35 iterations.
- Parsed NaN iterations are `0` for all 35 iterations.
- Iteration 35 logged `learning rate: 1.000000E-07`, finite LM loss
  `8.339980E-01`, and grad norm `9.114`.
- Checkpoint save at iteration 35 logged as successful.
- `markers/latest_checkpointed_iteration.txt` is `35`.
- `train_rc.txt` is `1`.
- `train_end.txt` is `2026-06-03T16:36:36Z`.

Termination evidence is consistent with lead-cleared fail-closed salvage:

- Pre-termination snapshot shows the latest checkpoint as `35` and the log
  stalled after `Evaluating on 80 samples` / `Evaluating iter 1/10`.
- `termination_signal_log.txt` records `signal=SIGTERM`,
  `command=kill -TERM 1389032`, and `kill_rc=0`.
- The final training log records torchrun propagating SIGTERM to ranks
  `1389104` through `1389111` and a SignalException from signal 15.
- Post-termination evidence shows no remaining task310 training process other
  than the termination-log `tee`, and all eight H200s released to `1 MiB` and
  `0%` utilization.
- No accepted validation metric is present.

## Boundary review

Task310 report and artifacts preserve the expected boundaries:

- no clean `PASS_TRAINING` wording;
- no task311 canary or benchmark eval;
- no AIME/task243 eval;
- no export, endpoint, or promotion;
- no generic raw-stage data inclusion;
- no AIME2025 prompt/label train rows claimed;
- no task255 reuse;
- no shared deletion;
- no product-code change in #373;
- no direct main push or merge by worker_4.

## Residual risks

1. `train_rc.txt=1` remains a real residual from lead-cleared SIGTERM during
   built-in validation.
2. Built-in validation did not complete and produced no accepted validation
   metric.
3. The approval is only for checkpoint-load plus non-AIME canary handoff; it is
   not evidence of benchmark, AIME/task243, export, endpoint, promotion, or
   training-pass readiness.
4. The local copied-evidence checksum manifest contains a stale self-entry even
   though its actual file hash matches the reported `ab102...` and all non-self
   entries pass.
5. The 399G checkpoint payload is not copied into the local evidence root; it
   remains at the remote run root and was verified there read-only.

## Commands and environment

Local review host:
`lg-cmc-b7r201-n09u29-cpu-000191`.

Remote artifact host:
`lg-cmc-b7r201-f08u26-h200-000126`.

Read-only checks run:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
gh pr view 373 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url
gh pr view 376 --json number,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus,mergeable,url
git diff --name-status 7561a578f5f624cf1d3b85bef0dd8abb5c787533..0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8
git diff --check 7561a578f5f624cf1d3b85bef0dd8abb5c787533..0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8
git diff --exit-code 7561a578f5f624cf1d3b85bef0dd8abb5c787533..0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8 -- workspace/tasks/task310_qwen_all_sft_30b_full_training_s1/all_sft_30b_full_training_report.md
git diff --name-status origin/main...origin/pr/373
git diff --check origin/main...origin/pr/373
sha256sum <key local manifest/log/snapshot files>
cd "$LOCAL_ROOT" && awk '$2 != "manifests/final_local_copied_evidence.sha256" {print}' manifests/final_local_copied_evidence.sha256 | sha256sum -c -
ssh NemTron 'ROOT=/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z; test -d "$ROOT/checkpoints/iter_0000035"; du -sh "$ROOT/checkpoints/iter_0000035"; find "$ROOT/checkpoints/iter_0000035" -type f | wc -l'
ssh NemTron 'ROOT=/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z; cd "$ROOT/checkpoints/iter_0000035" && sha256sum -c "$ROOT/manifests/iter_0000035.sha256"'
```

No training, eval, export, endpoint, promotion, merge, main push, worker branch
rewrite, shared deletion, AIME2025 train data, or task255 reuse was performed.
