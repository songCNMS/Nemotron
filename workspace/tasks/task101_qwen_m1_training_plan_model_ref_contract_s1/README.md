# task101_qwen_m1_training_plan_model_ref_contract_s1 - Qwen M1 training plan model ref contract

<!-- METADATA:STATUS=InReview,ASSIGNEE=intern_nem_dev_3,SESSION=12 -->

## Background

The direct M1 Agentic SFT training planner still used the tokenizer path as
Qwen `training_contract.model_ref`, and its generated run script did not export
`SUPER3_M1_QWEN_HF_MODEL`. This can misrecord model lineage when operators use
separate Qwen HF model and tokenizer paths.

## Goals

- Add explicit `--qwen-hf-model` support for Qwen direct M1 training plans.
- Keep `--tokenizer-model` as the tokenizer path and preserve legacy Nemotron
  behavior.
- Use the Qwen HF model path for manifest `training_contract.model_ref` and the
  rendered torchrun override.
- Export `SUPER3_M1_QWEN_HF_MODEL` in generated run scripts for Qwen profiles.
- Add focused coverage for distinct Qwen model and tokenizer paths.

## Out Of Scope

- Live train/eval runs, endpoints, W&B, cluster jobs, deployment, promotion,
  direct `main` or `master` pushes, and self-merge.

## Acceptance Criteria

- [x] Branch created from latest `origin/main` at
  `944483ba510fd4a8b98bf00613127567a499f8dc`.
- [x] Direct planner manifest and rendered command use the Qwen HF model path
  for `training_contract.model_ref`.
- [x] Generated Qwen run script exports `SUPER3_M1_QWEN_HF_MODEL`.
- [x] Focused M1 SFT planner pytest, py_compile, and Ruff pass.
- [x] Static rendered manifest/script probe and whitespace checks pass.
- [x] PR opened to `main`.

## PR

- https://github.com/songCNMS/Nemotron/pull/209
