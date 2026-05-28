# task091_omni3_stage1_rl_config_portability_s1 - Task Knowledge

<!-- METADATA:SESSION=9 -->

## Knowledge Entries

1. assignment: fix named-user `/lustre/fs1/portfolios/coreai/users/aroshanghias` fallbacks in runnable Omni3 stage1 RL configs.
2. technical fact: `stage3_vision_rl/config/default.yaml` does not use this named-user fallback block and was intentionally left unchanged.
3. implementation choice: generated roots default to `${oc.env:NEMO_RUN_DIR,.}/output/omni3/...`; `CONTAINER` defaults to the same home-cache path already used by `run.env.container`.
4. test contract: tests should prove env override names remain first-choice, no-env defaults resolve portably, and `stage1_mpo/config/tiny.yaml` keeps `NUM_NODES=1` plus the tiny job-name fallback.
5. session 9 note: task096 work reused the same intern session bookkeeping path
   while implementing a Qwen eval repro gate remote-artifact PM verification
   guard.
