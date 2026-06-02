# task299_qwen_aime_v11_30b_data_packing_contract_s1 - history log

<!-- METADATA:SESSION=84 -->

## Session 76 - 2026-06-02 UTC - assignment

- Created by `intern_nemotron_lead` as the 30B data/packing contract gate.
- Assigned to `intern_nemotron_worker_1`.
- Must preserve task276 V11 split/decontam semantics and prove the
  Qwen3-30B-A3B chat-template/tokenizer contract before any 30B training.

## Session 80 - 2026-06-02 UTC - acceptance

- Accepted by `intern_nemotron_worker_1` on branch
  `intern_nemotron_worker_1/task299_qwen_aime_v11_30b_data_packing_contract_s1`
  from current `origin/main` `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`.
- Lead docs source verified at
  `676d85563e00dfb665b6a911995bd47b4932c370`.
- Boundary acknowledged: no training, optimizer steps, corrected AIME scoring,
  non-AIME canary, export, endpoint, promotion, task255 reuse, AIME2025 train
  prompts/labels, shared deletion, main push, merge, 30B training, or 8-GPU
  launch.

## Session 81 - 2026-06-02 UTC - progress mailbox checkpoint

- Lead requested an official progress mailbox while the branch was still at
  acceptance head `9dc8d3949d0d1c562c53e959a61873f4771ef146`.
- Commands already run: fetched `origin/main` and lead docs, read task299 docs,
  inspected `qwen_chat_contract.py`, read task276 `metadata.json`,
  `manifest.json`, and `packed_qwen_evidence_manifest.json`, checked Qwen model
  directories, probed tokenizer-native `AutoTokenizer` properties for 4B and
  30B, and hashed tokenizer assets.
- Current finding: Qwen3-4B-Instruct-2507 and Qwen3-30B-A3B-Instruct-2507
  tokenizer assets match for `tokenizer.json`, `tokenizer_config.json`,
  `vocab.json`, and `merges.txt`; tokenizer-native API reports matching class,
  vocab size, tokenizer length, special tokens, and chat-template length.
- Current caveat: raw task276 packed metadata records the 4B tokenizer URI, so
  direct raw-root reuse with the 30B tokenizer would fail the existing strict
  packed-data contract unless a task-owned 30B-ready adapted root is produced
  after equivalence proof.
- Decontam status so far: task276 evidence carries PASS with zero AIME pattern
  mentions, zero label-like top-level keys, zero task246 prompt-hash overlaps,
  task262 final-answer n-gram blocker rows `0`, and blocker pairs `0`; task299
  will still include a current checksum-backed proof in its final artifacts.
- Boundary maintained: no training, optimizer steps, testing, corrected AIME
  scoring, non-AIME canary, export, endpoint, promotion, task255 reuse,
  AIME2025 train prompts/labels, shared deletion, main push, merge, 30B
  training, or 8-GPU launch.

## Session 82 - 2026-06-02 UTC - final 30B packing contract evidence

- Produced task-owned 30B-ready packed root:
  `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`.
- Decision recorded in `30b_data_packing_contract_report.md`:
  `PASS_30B_DATA_PACKING_CONTRACT`.
- Top manifest sha256:
  `59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d`.
- Proved Qwen3-4B and Qwen3-30B-A3B tokenizer assets/API/chat-template samples
  are equivalent, then adapted the copied metadata tokenizer URI to the 30B
  tokenizer path.
- Offline no-training contract validators passed:
  `validate_qwen_packed_sft_chat_contract` and
  `validate_qwen_training_pipeline_contract`.
- Split parity and counts passed: train `279` rows/`46` shards, valid `1`
  row/`1` shard, test `0` rows/`1` shard.
- Decontam proof passed: zero AIME contest mentions in trainable messages,
  zero label-like top-level keys, zero task246 prompt-hash overlaps, and task262
  final-answer n-gram blocker rows/pairs `0`.
- Boundary maintained: no training, optimizer steps, testing, corrected AIME
  scoring/eval, non-AIME canary, export, endpoint, promotion, task255 reuse,
  AIME2025 train prompts/labels, shared deletion, main push, merge, 30B
  training, or 8-GPU launch.

## Session 83 - 2026-06-02 UTC - final PR/mailbox preparation

- Lead requested final task299 report/PR on the critical path after task298's
  official PASS claim.
- Final evidence remains `PASS_30B_DATA_PACKING_CONTRACT` with task-owned
  30B-ready packed root
  `/work-agents/intern_nemotron_worker_1/outputs/task299_qwen_aime_v11_30b_data_packing_contract_s1/run_20260602T150941Z/packed_qwen_30b`.
- Required evidence is present in `30b_data_packing_contract_report.md`: source
  manifest, root path, counts, checksums, intended-vs-exposed parity,
  tokenizer/chat-template equivalence, no-AIME2025-train proof, no task255
  reuse, no shared deletion, exact commands/env, and boundaries.
- Opened PR #365:
  `https://github.com/songCNMS/Nemotron/pull/365`.
- Top manifest sha256 remains
  `59ee4432b5ddf776f82ee5dff6f45f1a9c1f8f9c7ad99a29d8fcfb96c7e50f3d`.
- Boundary maintained: no training, testing, corrected AIME eval, export,
  endpoint, promotion, task255 reuse, AIME2025 train data, shared deletion,
  main push, merge, 30B training, or 8-GPU launch.

## Session 84 - 2026-06-02 UTC - lead-approved self-merge closeout

- Lead approved task299/#365 for exact head
  `b8b760fb8f46cda8f302adbea106f19cc234e038` after independent review.
- Pre-merge verification found PR #365 `OPEN`, base `main`, non-draft,
  `mergeStateStatus=CLEAN`, API `mergeable=true`, `mergeable_state=clean`,
  and head exactly
  `b8b760fb8f46cda8f302adbea106f19cc234e038`.
- Self-merged PR #365 at `2026-06-02T15:29:15Z`; merge commit:
  `205fc919a643b1478964a9e91793247c5e821a38`.
- Merged head:
  `b8b760fb8f46cda8f302adbea106f19cc234e038`.
- Scope remained data/packing/decontam docs and evidence only. No training,
  testing, corrected AIME eval, export, endpoint, promotion, task255 reuse,
  AIME2025 train data, shared deletion, 30B launch, or 8-GPU use occurred.
