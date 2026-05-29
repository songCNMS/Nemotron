# task151_super3_stage0_pretrain_tiny_blend_contract_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Scope

- Make Super3 Stage0 pretrain data-prep `tiny.yaml` use a Super3-owned small
  blend path.
- Replace the empty Super3 small blend placeholder with a compact non-empty
  Super3-owned blend derived from open-source Phase 1 rows.
- Preserve tokenizer, output_dir, shard counts, sample, force, and config_name
  semantics.
- Do not touch Nano3 files or Stage1 SFT files.

## Boundaries

- Static/config/test-only.
- No live HF download, Stage0 pretrain data prep, tokenization, train/eval,
  endpoint call, W&B run, cluster job, deployment, artifact download, direct
  `main`/`master` push, or self-merge.

## Status

- Branch: `intern_nem_dev_3/task151_super3_stage0_pretrain_tiny_blend_contract_s1`
- Base: `17ed7b0e5195878030ff09118fb79caee200b824`
- PR: https://github.com/songCNMS/Nemotron/pull/257
