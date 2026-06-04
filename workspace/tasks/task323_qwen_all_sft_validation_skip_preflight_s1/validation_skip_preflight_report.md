# task323 validation-skip preflight report

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

Generated: 2026-06-03T20:45:00Z

## Disposition

Decision: `PASS_ROUTE_A_PREFLIGHT`.

Task323 produced a no-training, no-optimizer, no-eval Route A preflight proof:
a task-owned dereferenced train-only packed root exists, `splits/valid` and
`splits/test` are not exposed, validation auto-detection resolves to
`do_validation=false`, and a later same-harness eval handoff is mandatory.

This is not training clearance. A later lead-gated launch task must still sync
the accepted train-only input root to the target runtime, bind exact LR/steps
and checkpoint paths, and preserve the rc/checkpoint/teardown policy before any
optimizer step.

No training, optimizer steps, benchmark eval, export, endpoint, promotion,
final packing, product-code edit, task255 reuse, AIME2025 train data, shared
deletion, main push, merge, or self-merge was performed.

## Branch and inputs

| Item | Value |
|---|---|
| Worker branch | `intern_nemotron_worker_5/task323_qwen_all_sft_validation_skip_preflight_s1` |
| Base | `origin/main` `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb` |
| Lead docs | `origin/intern_nemotron_lead/session1-recovery-task-docs` `7055dac63c772ac8a317454bffead4a469a0112f` |
| Task322 visibility | no task322 PR found by `gh pr list --search task322`; task323 used task299/task310 constrained root |
| Source packed root | `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b` |
| Task-owned output root | `/work-agents/intern_nemotron_worker_5/outputs/task323_qwen_all_sft_validation_skip_preflight_s1/run_20260603T203404Z` |
| Task-owned train-only root | `/work-agents/intern_nemotron_worker_5/outputs/task323_qwen_all_sft_validation_skip_preflight_s1/run_20260603T203404Z/train_only_packed_root` |

## Preflight result

| Check | Result |
|---|---:|
| Source train parquets | `46` |
| Source valid parquets | `1` |
| Source test parquets | `1` |
| Source train symlinks | `46` |
| Task-owned train parquets | `46` |
| Task-owned valid parquets | `0` |
| Task-owned test parquets | `0` |
| Task-owned symlinks | `0` |
| Source-vs-mirror hash parity | `46/46 PASS` |
| Source-vs-mirror size parity | `46/46 PASS` |
| Train rows | `279` |
| Train input tokens | `1,024,646` |
| Train supervised tokens | `228,927` |
| `do_validation` | `false` |
| `packed_val_data_path` | `null` |
| Same-harness eval handoff | required |

The task-owned root intentionally does not contain `splits/valid` or
`splits/test`. It was built by dereference-copying only the accepted task299
train parquet payloads into `train_only_packed_root/splits/train`; task299 and
shared roots were not mutated.

## Artifact inventory

| Artifact | Path | sha256 |
|---|---|---:|
| Preflight summary | `manifests/preflight_summary.json` | `486426bdc2401f281d67cc7d53b49468d1b14e68c790238c0f17733ebdc5f93e` |
| Later launch contract | `manifests/later_launch_contract.json` | `8c749801b3cca8d5dcf9bbbf7e8598c8d2f5c64acc6f4912141dc2a57d31aef3` |
| Source-vs-mirror parity | `manifests/source_vs_mirror_parity.tsv` | `a8ed486d24e89568bf4eff3f969acc58255566aefb006954ce9024f4886c3b99` |
| Artifact checksum manifest | `manifests/task323_artifact_checksums.tsv` | `6c5ee6317f3ca95dc320e1c6dc97c8ba6efa6db78a6bdb18352cf3e11bb1150a` |
| Mirror train inventory | `manifests/mirror_train_inventory.tsv` | see checksum manifest |
| Source train inventory | `manifests/source_train_inventory.tsv` | see checksum manifest |
| Same-harness eval handoff | `manifests/same_harness_eval_handoff.json` | see checksum manifest |
| Commands run | `manifests/commands_run.txt` | see checksum manifest |

Copied source evidence under `source_evidence/` includes task299
`manifest.json`, `contract_validation.json`, `decontam_proof.json`,
`split_counts_parity.json`, `packed_qwen_30b_shard_checksums.json`,
`packed_qwen_30b_shard_checksums.sha256`,
`tokenizer_chat_template_equivalence_probe.json`, and copied split metadata.

## Validation auto-detection proof

The current training path in
`src/nemotron/recipes/super3/stage1_sft/train.py` sets validation from the
packed root shape:

- train data is required at `${super3_packed_sft_dir}/train/*.parquet`;
- if `${super3_packed_sft_dir}/valid/*.parquet` is missing, it logs that
  validation is skipped and sets `has_validation_data=False`;
- `FinetuningDatasetConfig(... do_validation=has_validation_data, do_test=False)`
  therefore resolves to `do_validation=false` for the task323 root.

The task323 preflight summary records:

```json
{
  "task_owned_splits_root": "/work-agents/intern_nemotron_worker_5/outputs/task323_qwen_all_sft_validation_skip_preflight_s1/run_20260603T203404Z/train_only_packed_root/splits",
  "train_parquet_count": 46,
  "valid_parquet_count": 0,
  "test_parquet_count": 0,
  "valid_exposure_removed": true,
  "mirror_symlink_count": 0,
  "do_validation": false,
  "packed_train_data_path": "/work-agents/intern_nemotron_worker_5/outputs/task323_qwen_all_sft_validation_skip_preflight_s1/run_20260603T203404Z/train_only_packed_root/splits/train",
  "packed_val_data_path": null,
  "same_harness_eval_handoff_required": true
}
```

No Bridge conversion, final packing, training import, optimizer launch, or eval
row was run.

## Safety proof

Task323 did not re-run decontamination over held-out eval rows. It carries the
accepted task299 proof and preserves the exact task299 train payload hashes:

- task299 decision: `PASS_30B_DATA_PACKING_CONTRACT`;
- task299 decontamination decision: `PASS`;
- task299 source scan found `0` AIME contest mentions, `0` label-like
  top-level keys, `0` task246 user prompt hash overlap, and `0` task246
  system+user hash overlap across the three train sources;
- task262 final-answer n-gram scan carried by task299 had `0` blocked rows,
  `0` blocker pairs, and `0` exact prompt hash overlap;
- task299 explicitly states AIME2025 prompts/labels remain held out and are not
  trainable rows;
- task323 copied only task299 train parquet targets and verified hash parity for
  every copied train shard;
- no task255 path or artifact was used.

## Later launch contract

The exact later training command remains lead-gated and was not executed. The
task323 contract requires:

| Field | Required value |
|---|---|
| Model/tokenizer | `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507` |
| Packed root env | `SUPER3_M1_AGENTIC_PACKED_DIR=<task-owned-train-only-root>/splits` |
| Validation disposition | `do_validation=false`, `packed_val_data_path=null` |
| Eval disposition | `same_harness_eval_handoff_required=true`; no benchmark/eval in training task |
| Checkpoint input | explicit lead-approved 30B pretrained checkpoint/import root |
| LR/steps | lead-approved placeholders; not bound by task323 |
| Save root | task-owned remote run root only |
| Runtime | later task must verify/sync root in runtime before launch |

The synthesized command template is recorded in
`manifests/later_launch_contract.json`. It is a contract artifact only.

## RC, checkpoint, timeout, and teardown policy

Clean closeout for a later training task requires:

- `train_rc.txt=0`;
- `train_end.txt` exists;
- latest checkpoint marker equals expected `train_iters`;
- final checkpoint inventory and payload checksum or remote checksum manifest
  exist;
- no validation timeout or hang occurred;
- no retained task-owned training processes;
- GPU release or explicit resource handoff proof;
- no shared deletion or mutation.

Fail-closed stop conditions:

- `valid_parquet_count` becomes nonzero before launch;
- `do_validation` is not `false` or `packed_val_data_path` is not `null`;
- same-harness eval handoff is not explicitly recorded;
- source-vs-mirror hash parity fails;
- any task255 reuse or AIME2025 prompt/label train-row evidence appears;
- NaN/skipped optimizer iteration in a later launch;
- nonzero rc, missing `train_end`, checkpoint marker mismatch, missing
  checkpoint manifest, retained process/GPU, or shared deletion.

Route A should not enter built-in validation. The wrapper should still carry
the task318 timeout guard as defense in depth:

- `VALIDATION_NO_PROGRESS_SEC=1800`;
- `SNAPSHOT_INTERVAL_SEC=300`;
- `SIGTERM_GRACE_SEC=300`;
- final pre/post snapshots around any signal;
- only task-owned process tree may receive `SIGTERM`;
- no `SIGKILL` unless lead explicitly authorizes it.

## Commands run

All commands were local/read-only or task-owned artifact creation. No product
code or shared root was edited.

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git switch -C intern_nemotron_worker_5/task323_qwen_all_sft_validation_skip_preflight_s1 origin/main
git checkout origin/intern_nemotron_lead/session1-recovery-task-docs -- workspace/tasks/task323_qwen_all_sft_validation_skip_preflight_s1
gh pr list --state all --search 'task322' --json number,state,headRefName,headRefOid,mergeCommit,mergedAt,title --limit 10
du -sh /work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b/splits/{train,valid,test}
python3 <task323 preflight artifact generator>
find <task323 train_only_packed_root>/splits/train -maxdepth 1 -type f -name '*.parquet' | wc -l
find <task323 train_only_packed_root>/splits/valid -maxdepth 1 -type f -name '*.parquet' 2>/dev/null | wc -l
find <task323 train_only_packed_root> -type l | wc -l
sha256sum <task323 key manifests>
awk <task323 parity and row-count checks>
```

## Residual risks

1. The task-owned root is local output evidence. A later training task must sync
   or recreate the train-only root in the actual runtime and re-check
   `valid_parquet_count=0`, `do_validation=false`, and hash parity before
   launch.
2. Task323 intentionally removes built-in validation exposure. Any performance
   claim must come from a later lead-gated same-harness eval task after
   checkpoint artifact review.
3. The data remains the constrained task299/task310 seed, not a repaired raw
   all-SFT blend. This satisfies the task323 Route A preflight but does not
   solve broader data-blend repair residuals.
4. The current code path proves validation skip by directory shape. A later
   product-level explicit `do_validation=false` flag would be clearer, but is
   not required for this preflight.
