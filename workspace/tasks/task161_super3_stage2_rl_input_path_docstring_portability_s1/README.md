# task161_super3_stage2_rl_input_path_docstring_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Summary

Replace the remaining Super3 Stage2 RL `/lustre/...` `input_path` docstring
example in `_data_prep_base.py` with portable `NEMO_RUN_DIR`-relative guidance
and add focused static coverage.

## Scope

- `src/nemotron/recipes/super3/stage2_rl/_data_prep_base.py`
- Focused Stage2 RL static/default tests
- Task/status docs for `intern_nem_dev_3`

## Acceptance

- `_data_prep_base.py` contains no `/lustre/` text.
- The `input_path` docstring example uses
  `${NEMO_RUN_DIR:-.}/output/super3/stage2_rl/rlvr1.jsonl`.
- `SubStageDataPrepConfig` runtime defaults for `input_path` and `output_dir`
  remain unchanged.

## Boundaries

- No live Stage2 RL data prep, bridge prep, train/eval, endpoint calls, W&B,
  cluster jobs, deploy, artifact upload/download, direct `main`/`master` push,
  or self-merge.
