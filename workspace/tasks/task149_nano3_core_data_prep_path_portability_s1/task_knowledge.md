<!-- METADATA:SESSION=2 -->

# Task Knowledge

- Actual base for task149 is `652534e4865e20b72f4c80bf62b6c0cea5973fd1` because PR #254 merged before implementation.
- Nano3 source defaults should use repo-relative paths under `src/nemotron/recipes/nano3/...`; dataclasses resolve only that Nano3 prefix to the repo root.
- Absolute blend overrides and arbitrary relative overrides such as `custom/blend.json` must remain unchanged.
- Nano3 data-prep output defaults should live under `${oc.env:NEMO_RUN_DIR,.}/output/nano3/...`.
- Current `nemo_runspec` artifact resolvers preserve numeric metadata values, so refreshed integration tests should assert integer `pack_size` instead of stringified values.
- Current `HFPlaceholderResolver` is table-backed (`tables`, `configs`) and Skywork records keep the raw `question` field while putting the template-applied prompt into `responses_create_params.input[0].content`.
