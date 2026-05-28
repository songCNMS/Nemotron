# task078_qwen_training_pipeline_contract_s1 - Qwen training pipeline contract

<!-- METADATA:STATUS=PR_OPEN,ASSIGNEE=intern_nem_dev_2 -->

## Background

PM assigned a critical PR-sized lane for Qwen SFT/RL training pipeline consistency.
The seed risk is that direct `m1_agentic_train.yaml` launches can still inherit
Nemotron/Super3 defaults while targeting Qwen packed data or Qwen wrappers.

## Goals

- Add offline validators and profile plumbing so Qwen target training cannot
  silently use mismatched tokenizer, chat-template, model, or entrypoint defaults.
- Compose PR #186 Qwen data-prep/profile guards with PR #185 training-contract
  validation after rebasing on latest `main`.
- Keep Qwen scale-up planner manifests and scripts explicit about data-prep,
  packing, training profile, tokenizer/model, and eval handoff.
- Keep live training and cluster launches out of scope.

## Acceptance Criteria

- [x] Qwen data-prep config/profile guards remain active after rebase.
- [x] Qwen training profile/tokenizer/entrypoint validation rejects direct
  generic Nemotron launches for Qwen packed data.
- [x] Qwen planner scripts pass the Qwen data-prep contract and training profile.
- [x] Focused Qwen contract, planner, RL kwargs/stop strings, compile, and
  whitespace checks pass locally.
- [x] PR #185 updated against latest `main`; no self-merge.

## PR

- https://github.com/songCNMS/Nemotron/pull/185
