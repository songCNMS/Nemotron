# task147_omni3_text_rl_blend_path_cwd_independence_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Scope

- Make Omni3 text RL data-prep `blend_path` repo-relative instead of
  `${oc.env:PWD}`-relative.
- Resolve checked-in Omni3 data-prep source paths from any caller CWD with an
  Omni3-local helper in `_data_prep_base.py`.
- Preserve absolute `blend_path` overrides and arbitrary relative user
  overrides.
- Do not touch `src/nemotron/kit/train_script.py`.

## Boundaries

- Static/config/unit-test only.
- No live Omni3 data prep, training, eval, W&B, cluster job, deployment,
  artifact download, direct `main`/`master` push, or self-merge.

## Status

- Branch: `intern_nem_dev_3/task147_omni3_text_rl_blend_path_cwd_independence_s1`
- Base: `7145c7de80f03555259a9b5657cc4066812f50d0`
- PR: pending
