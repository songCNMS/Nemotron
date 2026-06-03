# task309_qwen_all_sft_packed_data_contract_s1 - Qwen all-eligible-SFT packed data contract

<!-- METADATA:STATUS=Assigned,ASSIGNEE=intern_nemotron_worker_2,SESSION=77 -->

## Background

The coordinator requested a full all-SFT data -> training -> evaluation
attempt. Training is blocked until a fresh all-eligible-SFT packed-data
contract exists from current main and excludes held-out/eval/decontam rows.

## Goal

Produce all-eligible-SFT `packed_qwen` artifacts for Qwen3-30B-A3B training, or
return an exact fail-closed blocker.

## Scope

- Use current `origin/main` `ecb14173a820df377270273b9f7d9d92cb5076d2`.
- Consume task308 inventory when available; before that, perform preparatory
  static/data-source checks only.
- Build or identify the all-eligible-SFT blend using only sources task308 marks
  trainable.
- Preserve tokenizer-native Qwen chat-template packing for
  `/mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507`.
- Prove decontamination and exclusions:
  - no AIME2025 prompt/label training rows;
  - no held-out/eval/decontam rows;
  - no task255 reuse.
- Produce split manifest, row counts, token counts, supervised-token counts,
  shard counts, source counts, intended-vs-exposed multiset parity, checksums,
  and Qwen packed-data contract proof.
- If sparse valid/test risk remains, state exact impact and whether it blocks
  task310.

## Boundaries

- No training, optimizer steps, benchmark eval, export, endpoint, promotion, or
  source-code modification.
- Do not silently change target model family or downgrade to 4B.
- Do not use AIME2025 prompts/labels as train rows.
- Do not reuse task255.
- Do not delete shared files under `/mnt/cephfs/data/processing/lei.song`.
- Do not push main or merge.

## Expected Output

- Worker branch:
  `intern_nemotron_worker_2/task309_qwen_all_sft_packed_data_contract_s1`.
- Report:
  `workspace/tasks/task309_qwen_all_sft_packed_data_contract_s1/all_sft_packed_data_contract_report.md`.
- Task-owned output root containing `packed_qwen`, split manifest, source
  inventory, decontam evidence, parity report, checksum manifest, commands/env,
  and logs; or a blocker report with the exact failed contract.
- Mailbox report with branch/head/PR or blocker, artifact paths, commands/env,
  counts, checksums, decontam proof, Qwen chat-template/tokenizer proof, and
  task310 go/no-go recommendation.

## Acceptance Criteria

- `PASS_PACKED_CONTRACT`: all-eligible-SFT packed root is complete, checksummed,
  decontaminated, Qwen3-30B-compatible, and ready for task310.
- `REQUEST_CHANGES`: counts, checksums, parity, source provenance, or decontam
  evidence is incomplete but repairable.
- `BLOCK`: packing, decontam, tokenizer/chat-template, source eligibility, or
  artifact generation cannot be proven safely.

## Assignment

- Team: `nemotron`
- Team lead: `intern_nemotron_lead`
- Worker: `intern_nemotron_worker_2`
- Current main: `ecb14173a820df377270273b9f7d9d92cb5076d2`
- Upstream dependency: task308
- Downstream tasks: task310, task311, task312
- Gate state: task310 full training remains HOLD until task309 is accepted.
