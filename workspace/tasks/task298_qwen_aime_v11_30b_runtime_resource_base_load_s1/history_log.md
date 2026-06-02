# task298_qwen_aime_v11_30b_runtime_resource_base_load_s1 - history log

<!-- METADATA:SESSION=3 -->

## Session 76 - 2026-06-02 UTC - assignment

- Created by `intern_nemotron_lead` after coordinator relayed the user request
  to start full 30B Qwen AIME V11 training/testing.
- Assigned to `intern_nemotron_worker_2` as the first fail-closed gate:
  runtime/resource/base-load proof only, no training or testing.
- Candidate path is
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`; current
  main is `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`.

## Session 1 - Accepted by worker_2

- Created worker branch
  `intern_nemotron_worker_2/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1`
  from current `origin/main`
  `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`.
- Imported task docs from
  `origin/intern_nemotron_lead/session1-recovery-task-docs` at
  `676d85563e00dfb665b6a911995bd47b4932c370`.
- Accepted scope: 30B runtime/resource/base-load gate only, including exact
  Qwen3-30B-A3B model path, resource/parallelism proposal, import/load path,
  later training entrypoint, and eval/export route decision.
- Boundaries acknowledged: no training/optimizer steps, corrected AIME scoring,
  non-AIME canary, export for promotion, production endpoint, promotion,
  task255 reuse, AIME2025 train prompts/labels, shared deletion, main push, or
  merge.

## Session 2 - Runtime/resource/base-load evidence

- Ran task-owned NemTron no-training preflight under
  `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z`
  after syncing the worker branch into the run-local `Nemotron` path.
- Verified exact 30B model path:
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`;
  nearby variants exist but were not substituted.
- Captured model inventory: 57G HF checkpoint, 16 safetensor shards, Qwen3-MoE
  config, HF config/tokenizer load pass, and safetensor metadata read pass.
- Built the current-main 30B Qwen3-A3B Bridge recipe with
  `src/nemotron/recipes/super3/stage1_sft/qwen3_30b_a3b_local_train.py`,
  TP=4, PP=2, EP=4, ETP=1, sequence parallel enabled, GBS=8/MBS=1.
- Ran task-owned `AutoBridge.import_ckpt` import from the 30B HF path into
  `/root/task298_qwen_aime_v11_30b_runtime_resource_base_load_s1/run_20260602T143838Z/qwen3_30b_bridge_import_iter0`;
  it returned `BRIDGE_IMPORT_RC=0`, wrote latest iteration `0`, and produced a
  57G torch-dist checkpoint with checksum manifest.
- Disposition recorded in `30b_runtime_resource_base_load_report.md`:
  `PASS_RUNTIME_RESOURCE_BASE_LOAD_GATE_WITH_TRAINING_LAUNCH_RESIDUALS`.
- Opened PR #364 to main with the task298 report and status/task metadata.
- Boundaries held: no SFT training, optimizer step, corrected AIME scoring,
  non-AIME canary, eval run, export, endpoint, promotion, task255 reuse,
  AIME2025 train data, shared deletion, main push, merge, or shared-root
  mutation.

## Session 3 - Exact-head mailbox resend and hold

- Verified PR #364 was `OPEN`, base `main`, `CLEAN`, and at exact head
  `a1bd2af05aeb6554e7d9130076d9b81a3aa95b85`.
- Sent official mailbox report for that exact head with commands/env, artifact
  roots, key checksums, model path, Bridge import proof, resource/parallelism,
  eval-route decision, residual risks, and boundary confirmation.
- Mailbox message id: `59ba26de6bd3468aa61c64a61e2cc840`.
- Holding PR #364 for task302 review and lead gate. No self-merge, training,
  eval, export, endpoint, promotion, shared deletion, main push, or merge.
