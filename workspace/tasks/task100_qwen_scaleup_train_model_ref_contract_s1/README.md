# task100_qwen_scaleup_train_model_ref_contract_s1 - Qwen scale-up train model ref contract

<!-- METADATA:STATUS=ReadyForPR,ASSIGNEE=intern_nem_dev_3,SESSION=11 -->

## Background

The Qwen scale-up planner supports separate HF model and tokenizer paths, but
the generated remote train script used the tokenizer path for
`training_contract.model_ref`. When the paths differ, the generated launch
artifact can record tokenizer lineage where downstream checkpoint/eval handoff
expects the train model reference.

## Goals

- Use the selected `qwen_hf_model` for `training_contract.model_ref` in the
  generated remote train script.
- Preserve fallback to `tokenizer_model` for older manifests without an
  explicit Qwen HF model field.
- Add focused coverage for distinct remote model and local tokenizer paths.
- Keep data prep, packed-dir handling, train entrypoint selection, eval script
  generation, and live launch behavior unchanged.

## Out Of Scope

- Live SFT packing, training launch, checkpoint conversion, endpoint calls,
  W&B, cluster jobs, deployment, promotion, direct `main` or `master` pushes,
  and self-merge.

## Acceptance Criteria

- [x] Branch created from `origin/main` at or after
  `9ab5e264b110095c0a1c9ea33c9b49ccd8d44909`.
- [x] Generated remote train script uses the Qwen HF model path for
  `training_contract.model_ref`.
- [x] Focused planner pytest passes.
- [x] py_compile, Ruff, static contract probe, and whitespace checks pass.
- [ ] PR opened to `main`.

## PR

- Pending
