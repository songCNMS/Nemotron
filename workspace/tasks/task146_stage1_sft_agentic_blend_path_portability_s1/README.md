# task146_stage1_sft_agentic_blend_path_portability_s1

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nem_dev_1 -->

## Scope

- Make Stage1 SFT `agentic_v0` and `qwen_agentic_v0` `blend_path`
  defaults follow the M1 Agentic SFT producer output under
  `${oc.env:NEMO_RUN_DIR,.}/output/super3/m1_agentic_sft_v0`.
- Preserve existing Super3 and Qwen tokenizer/model, chat-template,
  `used_in_filter`, `target_model_family`, `output_dir`, and run/config
  semantics.
- Add focused static and OmegaConf tests for raw and resolved path behavior.

## Boundaries

- Static/config/test/docs-only.
- No live M1 data prep, SFT packing, train/eval, endpoint calls, W&B, cluster,
  deploy, artifact download, direct `main`/`master` push, or self-merge.

## Status

- Branch: `intern_nem_dev_1/task146_stage1_sft_agentic_blend_path_portability_s1`
- Base: `7145c7de80f03555259a9b5657cc4066812f50d0`
- PR: https://github.com/songCNMS/Nemotron/pull/253
- Merged: `311a407294be2de5413de3d300770b3c51afa986`
