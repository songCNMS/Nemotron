# task299_qwen_aime_v11_30b_data_packing_contract_s1 - 30B data/packing contract gate

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nemotron_worker_1,SESSION=84 -->

## Background

The 4B V11 pipeline accepted task276 rematerialized packed data and task296/297
current-main equivalence. For 30B, the data can only be adapted or reused if the
Qwen3-30B-A3B chat-template/tokenizer/decontamination contract still holds.

## Goal

Produce a 30B-ready data/packing decision and artifacts: either reuse/adapt
task276 V11 data safely for Qwen3-30B-A3B-Instruct, or block with exact contract
differences.

## Scope

- Inspect task276 V11 split/materialization evidence and current main
  `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`.
- Compare Qwen3-4B and Qwen3-30B-A3B tokenizer/chat-template behavior using
  tokenizer-native APIs, not ad hoc string assumptions.
- Reconfirm decontamination: AIME2025 prompts/labels remain held out for eval
  and decontam only, never train rows.
- If contract holds, produce or identify a 30B-ready packed root with split
  manifest, row/token/supervised-token/shard/source counts, intended-vs-exposed
  parity, checksums, and Qwen packed-data contract proof.
- If contract does not hold, report `BLOCK_DATA_CONTRACT` with exact diffs.

## Boundaries

- No training, optimizer steps, corrected AIME scoring, non-AIME canary, export,
  endpoint, promotion, task255 reuse, AIME2025 train prompts/labels, shared
  deletion, main push, merge, 30B training, or 8-GPU launch.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_1/task299_qwen_aime_v11_30b_data_packing_contract_s1`
- Report:
  `workspace/tasks/task299_qwen_aime_v11_30b_data_packing_contract_s1/30b_data_packing_contract_report.md`
- Artifact root under worker outputs with packed root or blocker logs,
  manifests, counts, checksums, tokenizer/chat-template probes, and
  decontamination proof.
- Mailbox report with branch/head/PR, commands/env, artifact paths, split
  counts, checksum list, decontam result, decision, and blockers.

## Acceptance Criteria

- PASS: 30B data/packing root is ready with task276 V11 split semantics,
  tokenizer-native Qwen3-30B chat contract proof, no AIME2025 train rows, and
  checksum-backed manifests.
- REQUEST-CHANGES: missing counts, checksums, parity proof, tokenizer evidence,
  or decontam proof.
- BLOCK: 30B tokenizer/chat-template/packing contract differs materially or
  AIME2025 train contamination cannot be ruled out.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_1`
- Current main: `31137bc1e28f7d08d4c6b5aa2448487d95aa07d7`
- Related tasks: task262, task276, task277, task296, task297
