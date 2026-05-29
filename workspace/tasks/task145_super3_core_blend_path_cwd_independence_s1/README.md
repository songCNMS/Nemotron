# task145_super3_core_blend_path_cwd_independence_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_2 -->

## Scope

- Make listed Super3 core repo-local source `blend_path` defaults independent
  of the caller CWD.
- Cover Stage0 pretrain core data-prep profiles, Stage1 SFT default/tiny, and
  Stage2 RL generic default/tiny.
- Preserve each referenced blend file identity and absolute/explicit override
  behavior.
- Keep generated M1 agentic SFT blend paths, output dirs, launch configs, and
  live data-prep surfaces out of scope.

## Boundaries

- Static config/test/docs plus focused path-resolution helper only.
- No live HF dataset download, Super3 data prep, SFT packing, RL/SFT/pretrain
  training, eval, endpoint call, W&B run, cluster job, artifact download,
  deployment, direct `main`/`master` push, or self-merge.

## Status

- Branch:
  `intern_nem_dev_2/task145_super3_core_blend_path_cwd_independence_s1`
- Base: `802f7bee98579e5a9647813f5182bb048e1aa44b`
- PR: https://github.com/songCNMS/Nemotron/pull/252
