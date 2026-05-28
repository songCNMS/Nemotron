# task084_stage2_rl_runspec_default_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=6 -->

## Knowledge Entries

1. supervisor request: PM assigned a static config/test/docs fix for generic `stage2_rl` runspec default drift after PR #190.
2. technical fact: generic `stage2_rl/train.py` runspec declares `tool.runspec.config.default = "tiny"`, while direct script execution falls back to `config/default.yaml`.
3. technical fact: stage-specific small/smoke configs already use `defaults: "default.yaml"` and override only small-footprint fields.
4. implementation choice: make generic `config/tiny.yaml` follow that local inheritance pattern and add a static resolver test to prove the resolved default path carries the Qwen RL chat/parser/stop contract.
5. scope note: generic `config/test.yaml` remains unchanged because it points at `test_train.py` and is a parsing/preflight config rather than the generic RL training path.
6. PM gate fact: tests must exercise the production `nemo_runspec.config.parse_config()` / `load_config()` path; a test-local defaults resolver can produce a false pass while the CLI/runspec path still bypasses `default.yaml`.
7. loader contract: `load_config()` now resolves only repo-local string defaults such as `defaults: "default.yaml"` recursively and strips the resolved key; non-string defaults, including Hydra-style lists, are left on the existing `OmegaConf.load()` behavior.
