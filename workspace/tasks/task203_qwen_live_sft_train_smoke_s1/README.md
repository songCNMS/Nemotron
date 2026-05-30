# task203_qwen_live_sft_train_smoke_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Goal

Run an evidence-only minimal Qwen SFT train smoke through the intended Super3
Stage1 SFT entrypoint/profile, starting from `main`
`0460c1f0262875fb27ae530d30cd80d805752851`.

## Scope

- Verify packed Qwen input paths and tokenizer/model path availability.
- Run the `m1_agentic_smoke` SFT profile compile dry-run with the Qwen profile.
- Probe Megatron-Bridge, `nemo_run`, and CUDA availability.
- Run a one-iteration local SFT smoke only when required deps and CUDA are
  available.
- Run the listed SFT/Qwen validator pytest shard.
- Report exact commands, pass/fail, runtimes, artifact paths, blockers, and
  small-pilot/full-training estimates.

## Boundaries

- No full training.
- No endpoint evals.
- No W&B, cluster, deploy, artifact upload, direct `main`/`master` push, or
  self-merge.
- No product code edits unless a concrete bug is found; if found, report before
  expanding scope.
