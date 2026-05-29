# task150_super3_stage1_sft_tiny_blend_contract_s1

<!-- METADATA:STATUS=Completed,ASSIGNEE=intern_nem_dev_1 -->

## Scope

- Make generic Super3 Stage1 SFT `tiny.yaml` use a Super3-owned tiny blend
  path instead of Nano3 `data_blend_tiny.json`.
- Replace the placeholder Super3 tiny blend with a small non-empty static blend
  derived from the Super3 Stage1 SFT raw blend.
- Set generic Super3 tiny `used_in_filter` to `null`.
- Preserve tokenizer, chat-template, output_dir, packing, sampling, and
  config_name semantics.

## Boundaries

- Static/config/test/docs-only.
- No live HF download, Stage1 SFT data prep, SFT packing, train/eval, endpoint
  calls, W&B, cluster jobs, deploy, artifact download, direct `main`/`master`
  push, or self-merge.

## Status

- Branch: `intern_nem_dev_1/task150_super3_stage1_sft_tiny_blend_contract_s1`
- Base: `17ed7b0e5195878030ff09118fb79caee200b824`
- Final tested base: `1e00d0f2559dd40c9ce396f5b7d0a539ce509f3a`
- PR: https://github.com/songCNMS/Nemotron/pull/258
- Merged: `6259027561ee158e0762e8b910a312e784aa069c`
