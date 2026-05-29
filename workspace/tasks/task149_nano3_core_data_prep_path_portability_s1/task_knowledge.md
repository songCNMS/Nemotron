<!-- METADATA:SESSION=1 -->

# Task Knowledge

- Actual base for task149 is `652534e4865e20b72f4c80bf62b6c0cea5973fd1` because PR #254 merged before implementation.
- Nano3 source defaults should use repo-relative paths under `src/nemotron/recipes/nano3/...`; dataclasses resolve only that Nano3 prefix to the repo root.
- Absolute blend overrides and arbitrary relative overrides such as `custom/blend.json` must remain unchanged.
- Nano3 data-prep output defaults should live under `${oc.env:NEMO_RUN_DIR,.}/output/nano3/...`.
