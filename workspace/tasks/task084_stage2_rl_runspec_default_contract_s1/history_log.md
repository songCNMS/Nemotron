# task084_stage2_rl_runspec_default_contract_s1 - History Log

<!-- METADATA:SESSION=6 -->

## Session 1 - 2026-05-28

- Received PM assignment after PR #190 merged at `d2f37f7e647bce186922f41da9476fa6e734576c`.
- Preserved pushed task083 branch state and fast-forwarded local `main` to latest `origin/main`.
- Created branch `intern_nem_dev_2/task084_stage2_rl_runspec_default_contract_s1`.
- Audited generic `stage2_rl/train.py` and configs: runspec default is `tiny`, direct script default is `default.yaml`, and `config/tiny.yaml` lacked inheritance from `default.yaml`.
- Added `defaults: "default.yaml"` to generic `config/tiny.yaml` so the runspec default path inherits the Qwen chat-template, parser, and stop-string contract while preserving tiny overrides.
- Expanded focused RL config tests with a static defaults resolver proving the generic runspec default path resolves the Qwen RL contract.
- Left `config/test.yaml` unchanged because it points at `test_train.py` and is documented as a parsing/preflight config, not the generic RL training script path.
- Verified required checks locally: focused RL config tests passed with 29 tests, py_compile passed for touched tests, `/work-agents/.venv/bin/ruff check` passed for touched tests, `git diff --check` passed, and a structured generic runspec default audit passed.
- Opened PR #191 to `main`: https://github.com/songCNMS/Nemotron/pull/191.

## Session 5 - 2026-05-28

- Stop-hook audit required an explicit Session 5 record in this history log for `task084_stage2_rl_runspec_default_contract_s1`.
- Confirmed PR #191 remains the active task084 PR and the implementation scope is unchanged: generic `stage2_rl/config/tiny.yaml` inherits `default.yaml`, with focused tests covering the resolved Qwen RL chat/parser/stop contract.
- Recorded this bookkeeping-only Session 5 entry and kept the validation evidence from Session 1 intact.

## Session 6 - 2026-05-28

- PM gate blocked old PR #191 head `6b19b050df110d54c46764db9d8668e0ddfc0912`: the pytest shard passed, but real `parse_config()` still loaded generic `tiny.yaml` without merging `default.yaml`, leaving tokenizer kwargs, stop strings, parser, and plugin fields unresolved.
- Fixed the production loader path in `nemo_runspec.config.load_config()` so repo-local `defaults: "base.yaml"` overlays are resolved recursively, the final merged config omits the resolved `defaults` key, and cycle errors are explicit.
- Replaced the task084 test-local defaults resolver with a real `parse_config()` helper and added coverage for generic `stage2_rl/config/tiny` plus stage1 RLVR small/smoke/rlvr2/rlvr3, stage2 SWE1 small, and stage3 RLHF small overlays.
- Verified locally: focused RL config shard passed with 36 tests, py_compile passed for touched Python/tests, ruff passed for touched loader/tests, `git diff --check` and `git diff --cached --check` passed, and a structured real `parse_config` audit passed.
