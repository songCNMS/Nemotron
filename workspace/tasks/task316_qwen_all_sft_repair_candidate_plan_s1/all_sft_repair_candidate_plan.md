# task316 all-SFT repair candidate plan

<!-- METADATA:STATUS=ReadyForReview,ASSIGNEE=intern_nemotron_worker_5,SESSION=1 -->

Generated: 2026-06-03T19:20:00Z

## Session 94 current-main refresh

Refreshed against `origin/main`
`4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985` on 2026-06-04 after
#380/task314 and #371/task311 landed. This refresh preserves the original
planning disposition as historical all-SFT repair guidance, but records that
several prerequisites have since moved:

- #371/task311 is now merged at `2026-06-04T13:36:33Z`, merge
  `4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985`, merged head
  `2e0cd5a5c7d788ded67334ff25608f8aaedfeffe`. The benchmark disposition
  remains `APPROVE_EVIDENCE_CLOSEOUT / PERFORMANCE_FAIL_MIXED`: AIME/HMMT
  improved while MMLU-Pro regressed below base.
- #380/task314 is now merged at `2026-06-04T13:36:32Z`, merge
  `4ccedc1a6e30f08b6ab844c0b387714d9ef16063`, merged head
  `fe34e52d19ec9cc9a384588a3e900924280fe16e`. It replaces the original
  "task314 not visible" residual and supports the MMLU-Pro regression finding.
- #385/task323 is merged as the concrete Route A train-only validation-skip
  preflight that follows the validation repair direction in this plan.
- #387/task325, #404/task341, and #405/task342 are merged blocker evidence:
  M1 launcher rows remain runtime-blocked and NemTron/training readiness is
  blocked by SSH/runtime access. These do not authorize task310/task341
  release, export, endpoint, promotion, or further training.

Current disposition for #377 after this refresh:
`APPROVE_PLAN_DOCS / NO_ACTION_RELEASE`, planning provenance only. It is not a
training, packing, eval, export, endpoint, promotion, or task310/task341
release gate.

## Disposition

Recommendation:
`APPROVE_PLAN__REPAIR_DATA_AND_VALIDATION_BEFORE_ANY_MORE_30B_TRAINING`.

Do not promote, export for production, endpoint-promote, or run another
training attempt from the current evidence. Task310 is a valid salvage evidence
record and task311 proves the salvage checkpoint can load and improve AIME/HMMT,
but task311 also proves the corrected Qwen MMLU-Pro row regressed below the
same-route base by 2 rows. That makes the current candidate a fail-closed
performance mixed result, not a training success.

The next repair candidate should be a later lead-gated sequence:

1. Freeze and merge/accept task311 evidence, or stop if task311 evidence is not
   accepted at the reviewed head.
2. Produce a validation/termination repair gate so the next training attempt can
   exit cleanly or intentionally hand off validation to an explicit same-harness
   eval task.
3. Produce a data-blend repair gate that materializes, decontaminates, and
   Qwen-packs the generic `stage1_sft/data_blend_raw` sources or a justified
   subset; the current task299-only seed is too narrow to call all-SFT and has
   already produced an MMLU-Pro regression.
4. Only after those gates pass, consider one bounded 30B repair training task
   with explicit stop rules and a required task311-style same-harness benchmark
   review before any promotion discussion.

## Evidence reviewed

| Area | Evidence | Current result |
|---|---|---|
| task308 inventory | #374 merged at `2026-06-03T15:28:23Z`, merge `eb05e6b324c3159b01070cb575c2be363e773cac`, head `a238cacb1f28fb96df58d3a10641a2b7325f61b7`; report `PASS_AUDIT_WITH_TASK309_FAIL_CLOSED_CONSTRAINTS`; inventory manifest sha256 `4f629e015d4e7a8965899f1fb6c1a5e22e4e666fff28c5bfa69d9d9b31f97a61`. | V11/task299 seed is checksum-backed; generic raw all-SFT registry is not task-ready. |
| task309 packed contract | #372 merged at `2026-06-03T15:32:36Z`, merge `af388ea858cd0b7582a37397188b03f69e8927b4`, head `6c3c79092ea551f0094d78f0097e2bd76a23438f`; disposition `PASS_CONSTRAINED_V11_TASK299_PACKED_CONTRACT_WITH_RAW_STAGE1_EXCLUSIONS`. | Only constrained task299 seed is accepted; generic raw stage remains excluded. |
| task310 training | #373 merged at `2026-06-03T17:30:08Z`, merge `292c5bfabf1f5b14e3330e0be72b4ef9abdc4aeb`, head `0cbcb3c56df5f097a0fd63ebfa1a3c7cdb36f9b8`; disposition `TRAINING_LOOP_COMPLETE__VALIDATION_HANG_TERMINATED__CHECKPOINT_SALVAGE_CANDIDATE`. | Reached train iter 35/35 and saved checkpoint, but validation hung and wrapper rc is 1. |
| task313 salvage review | #376 merged at `2026-06-03T17:27:38Z`, merge `cb36dcab1aae10ec12991433bfddfeeeb02d3d46`, head `3f5db4059260dd4b90e204c3f553b07d83edc7f4`; recommendation `APPROVE_SALVAGE_HANDOFF_TO_TASK311_LOAD_CANARY_ONLY`. | Checkpoint can be handed to load/canary only; not clean training or promotion. |
| task311 benchmark evidence | #371 merged at `2026-06-04T13:36:33Z`, merge `4fbb4eecfbe9db6402b1b627dd20c0d7d0b2e985`, merged head `2e0cd5a5c7d788ded67334ff25608f8aaedfeffe`; lead carried `APPROVE_EVIDENCE_CLOSEOUT / PERFORMANCE_FAIL_MIXED`. | AIME and HMMT pass vs base; MMLU-Pro fails vs base; M1 launcher rows remain blocked by later #387/task325 evidence. |
| task314 findings | #380 merged at `2026-06-04T13:36:32Z`, merge `4ccedc1a6e30f08b6ab844c0b387714d9ef16063`, merged head `fe34e52d19ec9cc9a384588a3e900924280fe16e`. | Current main now contains the MMLU-Pro regression forensics evidence that was not visible during the original task316 review. |

## Key artifact paths and hashes

### Data gates

Task308 artifact root:
`/work-agents/intern_nemotron_worker_1/outputs/task308_qwen_all_sft_pipeline_inventory_audit_s1/run_20260603T144136Z`

Task309 packed contract root:
`/work-agents/intern_nemotron_worker_2/outputs/task309_qwen_all_sft_packed_data_contract_s1/run_20260603T145300Z`

Constrained packed root used by task310:
`/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`

Task299 packed evidence carried by task309:

| Artifact | sha256 |
|---|---|
| `manifest.json` | `59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d` |
| `contract_validation.json` | `75265f68621676c846551ba12022cb3d6f383b4f65e3bc7fb9773a197434d0b2` |
| `split_counts_parity.json` | `f4c335e651cc7777ecf326ed2fa3e46791c3de7286d7dee86042d941db2be70d` |
| `decontam_proof.json` | `e5b73a79ae8d1cd35b3188bd0f6bda60570f37c21831ac16d126a006d7fd56bc` |
| `packed_qwen_30b_shard_checksums.json` | `444aef9230129d689c27be295ff054fc1dc4800fae52827280a5c289408fed11` |

Accepted constrained split counts:

| Split | Shards | Rows | Input tokens | Supervised tokens |
|---|---:|---:|---:|---:|
| train | 46 | 279 | 1024646 | 228927 |
| valid | 1 | 1 | 1491 | 1428 |
| test | 1 | 0 | 0 | 0 |

These counts are adequate for the constrained V11 seed, but they are not a
complete all-SFT blend and they leave sparse validation/test residual risk.

### Task310 salvage candidate

Remote run root:
`/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z`

Local evidence root:
`/work-agents/intern_nemotron_worker_5/outputs/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z`

Checkpoint candidate:
`/root/task310_qwen_all_sft_30b_full_training_s1/run_20260603T154206Z/checkpoints/iter_0000035`

| Evidence | Value |
|---|---|
| Checkpoint size/files | `399G`, `28` files |
| Checkpoint inventory manifest sha256 | `b30d83f641118da8d7a24438e6c379ba9a5e8e03793ef5ff26514d751d9fa676` |
| Checkpoint payload manifest sha256 | `8cb4e7856f379bc7f1d63d407582bd63981b61c9f346455aa40fb389ef73cbe8` |
| Preflight summary sha256 | `cff95dc1c07325b9192677670d68fe3b64a54759919879c5ce5db0b82d1b10b3` |
| Launch command sha256 | `c50bdeca383359aa6656884df707089321813efbf36bd01933e2b58389910777` |
| Training log sha256 | `e74eeec901731a7417e8151f04d1c9f67099906772eae611f2a027b7f48f5858` |
| `train_rc.txt` | `1` |
| `train_end.txt` | `2026-06-03T16:36:36Z` |

Task310 launch characteristics:
8x H200, TP `4`, PP `2`, EP `4`, ETP `1`, `train_iters=35`,
`global_batch_size=8`, `micro_batch_size=1`, `lr=5e-7`, `min_lr=1e-7`,
`seed=5678`, constrained task299 packed mirror only. Iteration 35 logged
`lr=1.000000E-07`, LM loss `8.339980E-01`, grad norm `9.114`, skipped `0`,
NaN `0`. No accepted validation metric exists.

### Task311 evidence

Task311 PR:
`#371` at head `9361e6da3ee6718c9ec5aa7f97b60a75c8e332b6`, open/CLEAN.

Task311 canary root:
`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T173607Z`

Task311 corrected benchmark root:
`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z`

Corrected benchmark summary:
`/work-agents/intern_nemotron_worker_3/outputs/task311_qwen_all_sft_benchmark_eval_s1/run_20260603T180911Z/manifests/session12_benchmark_summary.json`

Summary sha256:
`67998f32982ccf15be7d7eeec55827ec1d5edf658a41ba494d6cb7899e6da828`

| Benchmark | Base | FT | Delta | Plan interpretation |
|---|---:|---:|---:|---|
| AIME2025 | `15/30 = 0.5` | `16/30 = 0.5333333333333333` | `+1` | Improvement, but held-out eval only. |
| HMMT Feb 2025 | `9/30 = 0.3` | `11/30 = 0.36666666666666664` | `+2` | Improvement under same endpoint route. |
| MMLU-Pro test | `6758/12032 = 0.5616688829787234` | `6756/12032 = 0.5615026595744681` | `-2` | Hard fail for promotion and for repeating the same data recipe. |

M1 launcher rows remain blocked by missing launcher runtime, Docker, Slurm, and
benchmark modules on both local worker and NemTron.

## Repair decision

### Not recommended: direct promotion or more of the same task299-only training

Stop using the current task310 checkpoint as a promotion candidate. It is useful
as evidence that the route can train a bounded run, load, and improve math
benchmarks, but task311 MMLU-Pro failure means the candidate has not passed a
general benchmark non-regression gate.

Repeating the same task299-only packed seed with more steps is not the best next
candidate. The data is only `279` packed train rows from V11/M1/math sources,
with `1` valid row and `0` test rows. Task308 and task309 explicitly exclude
the broader generic all-SFT raw registry. The observed pattern, math up and
MMLU-Pro down, is consistent with an overly narrow repair seed, not a clean
evidence path for more identical training.

### Recommended next repair candidate: R1 data-plus-validation repair

The next candidate should repair both the data contract and the train/validation
exit contract before another 30B optimizer run:

1. `R1A_TASK311_EVIDENCE_FREEZE`: merge or otherwise formally accept task311
   #371 at a reviewed head, retaining corrected benchmark summaries,
   full-completion artifacts, parser diagnostics, endpoint manifests, and
   cleanup proof. Stop if #371 evidence changes materially or loses CLEAN state.
2. `R1B_VALIDATION_EXIT_REPAIR`: produce a no-training or zero-optimizer-step
   runbook/preflight that proves the next task can either complete built-in
   validation or intentionally skip built-in validation with an explicit
   separate same-harness eval handoff. Required evidence: exact config field or
   runner behavior, command/env, timeout policy, log tail, rc, GPU release,
   checkpoint marker policy, and stop rule. Stop if validation still hangs or
   the route can only succeed by hiding rc/log failures.
3. `R1C_DATA_BLEND_REPAIR`: materialize the generic `stage1_sft/data_blend_raw`
   sources or a lead-approved subset, then produce a new task-owned packed root
   for `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
   Required evidence: source file checksums, exact row counts, per-source
   token/supervised-token counts, train/valid/test counts, heldout prompt-hash
   and n-gram decontam including AIME2025/HMMT/MATH where relevant,
   no-task255 proof, no AIME2025 prompt/label train rows, Qwen chat-template
   contract proof, split parity, shard checksums, and non-sparse validation.
   Stop if any source lacks materialized counts or decontam proof.
4. `R1D_BOUND_TRAINING_PLAN`: if R1A-R1C pass, propose one bounded 30B repair
   training run. Use the same model path and runtime route as task310, but do
   not silently downgrade or include generic raw data without the R1C packed
   contract. Start with conservative one-epoch-or-less scheduling computed from
   packed train rows and `global_batch_size`; retain `lr <= 5e-7` unless a
   separate schedule audit justifies otherwise. Required stop rules: any NaN,
   skipped iteration, checkpoint write failure, validation no-progress beyond a
   predeclared threshold, rc nonzero, or GPU/process teardown failure.
5. `R1E_SAME_HARNESS_REVIEW`: before any promotion, run a later lead-gated
   task311-style review with same-harness base-vs-FT comparisons. Minimum rows:
   AIME2025, HMMT, MMLU-Pro, and any M1 launcher rows for which the launcher
   runtime is actually available. Stop if MMLU-Pro remains below base, if
   AIME/HMMT fall below base, or if endpoint/export cleanup cannot be proven.

## Gate matrix for later tasks

| Gate | Required before next 30B training | Exact stop condition |
|---|---|---|
| task311 evidence gate | #371 evidence accepted/merged or explicitly carried by lead with head/hash. | Stop if MMLU-Pro fail evidence is missing, changed materially, or not reviewed. |
| task314 coordination | Incorporate task314 if it appears. | Stop only if task314 contradicts this plan or marks a required artifact invalid. |
| validation repair | Prove clean validation exit or explicit skip plus same-harness eval handoff. | Stop on no-progress validation, rc nonzero without salvage clearance, missing `train_end`, or retained GPU/processes. |
| data repair | New packed root with materialized generic raw/all-SFT sources or an explicitly accepted subset. | Stop on unknown row counts, missing decontam, task255 reuse, AIME2025 train-row contamination, tokenizer mismatch, or sparse/empty validation evidence. |
| runtime repair | 8x H200 route, model path, task298/base import or replacement checkpoint path, TP/PP/EP/ETP, and `/root` sync verified. | Stop on missing Docker/Bridge/Megatron route, missing model path, insufficient GPUs, or unreviewed runtime change. |
| training run | Lead explicit clearance after all gates. | Stop on NaN/skipped iterations, checkpoint failure, validation hang past threshold, nonzero rc, or missing artifact inventory. |
| benchmark review | Same-harness base-vs-FT for each claimed row. | Stop on MMLU-Pro below base, any claimed row without same-harness base, parser/denominator mismatch, or endpoint cleanup failure. |

## Candidate commands and artifact requirements for later tasks

No command below is authorized by task316; these are requirements for later
lead-gated work.

### Data repair task

Required command family:

```bash
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_TOKENIZER_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
python3 src/nemotron/recipes/super3/stage1_sft/data_prep.py \
  src/nemotron/recipes/super3/stage1_sft/config/data_prep/qwen_agentic_v0.yaml \
  blend_path=<materialized-and-reviewed-blend.json> \
  output_dir=<task-owned-output-root>/packed_qwen_30b \
  tokenizer.model=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
  target_model_family=qwen \
  config_name=qwen_agentic_v0
```

Before this command is acceptable, the task must provide a manifest that names
every materialized source path, row count, sha256, decontam proof, and exclusion
decision. If a future implementation uses a different entrypoint or wrapper, it
must still emit the same evidence.

Required output artifacts:

- `source_inventory.json`
- `heldout_decontam_manifest.json`
- `packed_qwen_30b/manifest.json`
- `packed_qwen_30b/contract_validation.json`
- `packed_qwen_30b/split_counts_parity.json`
- `packed_qwen_30b/decontam_proof.json`
- `packed_qwen_30b/packed_qwen_30b_shard_checksums.json`
- command/env manifest and checksum manifest

### Training repair task

Required command family:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 \
SUPER3_M1_QWEN_HF_MODEL=/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 \
SUPER3_M1_AGENTIC_PACKED_DIR=<new-reviewed-packed-root> \
SUPER3_M1_PRETRAINED_CHECKPOINT=<reviewed-base-or-import-checkpoint> \
python3 -m torch.distributed.run --standalone --nnodes=1 --nproc_per_node=8 \
  src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py \
  train.train_iters=<computed-bounded-iters> \
  train.global_batch_size=8 \
  train.micro_batch_size=1 \
  optimizer.lr=<reviewed-lr-at-or-below-5e-7-unless-approved> \
  optimizer.min_lr=<reviewed-min-lr> \
  scheduler.lr_warmup_iters=<reviewed-warmup> \
  scheduler.lr_decay_iters=<reviewed-decay> \
  checkpoint.save=<task-owned-checkpoint-root> \
  checkpoint.save_interval=<reviewed-save-interval>
```

Required output artifacts:

- launch command/env manifest
- `/root` repo-sync head
- packed source-vs-remote mirror manifests
- preflight summary and log hashes
- training log
- train rc/end markers
- checkpoint latest marker
- checkpoint inventory and payload checksum manifest
- validation or explicit eval-handoff evidence
- GPU/process teardown snapshot

### Benchmark repair task

The task311 corrected Qwen route is the current evidence route. Any later
benchmark task must retain:

- full completions
- parser diagnostics
- row manifests
- command/env manifests
- endpoint manifests
- cleanup proof
- same-harness base evidence per row unless exact reuse is proven

M1 launcher rows require the missing launcher/container runtime first. Do not
substitute corrected-Qwen rows for unavailable M1 launcher rows.

## Risks

1. Task311 is still an open PR at the reviewed head, not merged into main at
   task316 review time.
2. MMLU-Pro regression is small by count but hard by gate policy: FT
   `6756/12032` is below base `6758/12032`.
3. Task310 checkpoint is remote-only in practice and salvage-derived with
   `train_rc=1`; future use needs explicit lead clearance and artifact review.
4. The current accepted training data is narrow and sparse: 279 packed train
   rows, 1 valid row, and 0 test rows.
5. Generic `stage1_sft/data_blend_raw` sources are large and not currently
   materialized/decontam-proven; careless inclusion would create contamination
   and provenance risk.
6. M1 launcher rows remain blocked by missing launcher/runtime modules, Docker,
   and Slurm on checked hosts.
7. AIME2025 remains held-out eval/decontam only; it must not become train data.

## Stop conditions

Stop and report `BLOCK_REPAIR_PLAN_INPUT_INVALID` if any of these occur:

- task311 #371 evidence is rejected, materially changes, or cannot be reviewed
  at a fixed head;
- task313/task310 checksum evidence for `iter_0000035` is invalidated;
- a future plan requires task255 reuse or AIME2025 prompt/label training rows;
- generic raw sources cannot be materialized with exact row counts, checksums,
  and decontam proof;
- Qwen tokenizer/chat-template contract or split parity fails;
- validation repair cannot prove clean exit or a lead-approved eval handoff;
- a future benchmark claim lacks same-harness base evidence;
- MMLU-Pro remains below base after a repair candidate;
- any step requires shared deletion under `/mnt/cephfs/data/processing/lei.song`
  or a direct main push.

## Task316 commands run

Read-only/report-only commands:

```bash
git fetch origin main intern_nemotron_lead/session1-recovery-task-docs
git checkout -b intern_nemotron_worker_5/task316_qwen_all_sft_repair_candidate_plan_s1 origin/main
git checkout f1f5efab -- workspace/tasks/task316_qwen_all_sft_repair_candidate_plan_s1
find workspace/tasks -maxdepth 1 -type d -name 'task31*'
gh pr view 371 --json number,state,headRefOid,baseRefName,mergeStateStatus,isDraft,url,title,comments,reviews
gh pr view 372 --json number,state,headRefOid,mergedAt,mergeCommit,title,url
gh pr view 373 --json number,state,headRefOid,mergedAt,mergeCommit,title,url
gh pr view 374 --json number,state,headRefOid,mergedAt,mergeCommit,title,url
gh pr view 376 --json number,state,headRefOid,mergedAt,mergeCommit,title,url
git fetch origin pull/371/head:refs/remotes/origin/pr/371
git show origin/pr/371:workspace/tasks/task311_qwen_all_sft_benchmark_eval_s1/all_sft_corrected_qwen_benchmark_report.md
git show origin/pr/371:workspace/tasks/task311_qwen_all_sft_benchmark_eval_s1/all_sft_non_aime_canary_report.md
git show origin/pr/371:workspace/tasks/task311_qwen_all_sft_benchmark_eval_s1/all_sft_m1_benchmark_availability_report.md
sed/rg over task308, task309, task310, task313 reports and stage1_sft config files
```

No training, eval, packing, export, endpoint, promotion, task255 reuse,
AIME2025 train data, shared deletion, product-code edit, main push, merge, or
worker-branch rewrite was performed.
