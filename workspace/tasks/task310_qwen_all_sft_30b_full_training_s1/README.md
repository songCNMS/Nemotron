# task310_qwen_all_sft_30b_full_training_s1 - Qwen all-SFT 30B full training gate

<!-- METADATA:STATUS=Open,ASSIGNEE= -->

## 背景

Coordinator authorized attempting a full all-SFT data->training->testing pipeline, prioritizing current 30B if resource/runtime gates remain valid. This is not a promotion claim.

## 任务目标

Launch full Qwen3-30B-A3B all-SFT training only after task308/task309 data gates and runtime/resource gates pass; otherwise fail closed with exact blocker.

## 实现说明

Use /mnt/cephfs/data/stable/models/Qwen/Qwen3-30B-A3B-Instruct-2507 unless task308/task309/task298-equivalent review blocks. Do not silently downgrade. No AIME2025 train data, task255 reuse, shared deletion, export/endpoint/promotion, main push, merge, or product-code edits.

## 验收标准

- PASS_TRAINING: usable checkpoint, LR/loss/validation evidence, commands/env, resources, logs, checksums, and handoff for canary/benchmark eval are complete.
- BLOCK: resource/runtime/data gates fail, checkpoint is unusable, or safe 30B training cannot be launched without boundary violations.

## 分配信息

- Team：nemotron
- Team lead：intern_nemotron_lead
- Worker：intern_nemotron_worker_5
- 分配方式：team_lead 创建本 task 文档后，通知 worker 接受该 task。
