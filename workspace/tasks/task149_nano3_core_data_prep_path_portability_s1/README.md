# task149_nano3_core_data_prep_path_portability_s1

Status: Ready for PM gate
Owner: intern_nem_dev_2
Branch: `intern_nem_dev_2/task149_nano3_core_data_prep_path_portability_s1`
Base: `652534e4865e20b72f4c80bf62b6c0cea5973fd1`
PR: https://github.com/songCNMS/Nemotron/pull/256

## Scope

Make Nano3 Stage0/Stage1/Stage2 core data-prep defaults portable:

- replace checked-in Nano3 `blend_path` defaults with repo-relative `src/nemotron/recipes/nano3/...` paths;
- resolve those checked-in Nano3 source paths to repo-root absolute files from any caller CWD;
- preserve absolute path overrides and arbitrary relative overrides;
- replace PWD/up-level output defaults with `NEMO_RUN_DIR`-relative `output/nano3/...` paths;
- add focused static/OmegaConf/dataclass tests.

## Boundaries

No live HF download, Nano3 data prep, SFT packing, training/eval, endpoint calls, W&B runs, cluster jobs, artifact downloads, deploys, direct main/master push, or self-merge.

## Checks

- PASS: focused Nano3 config/integration/Qwen contract pytest shard (`126 passed, 2 skipped`)
- PASS: py_compile touched product/test Python files
- PASS: Ruff touched product/test Python files
- PASS: structured non-repo-CWD resolver probe
- PASS: static grep found no `${oc.env:PWD}` or `/../output/` in target Nano3 data-prep YAMLs
- PASS: `git diff --check`
- PASS: `git diff --cached --check`
- PASS: added-line live-surface scan showed only static path/default/test/docs/status matches
