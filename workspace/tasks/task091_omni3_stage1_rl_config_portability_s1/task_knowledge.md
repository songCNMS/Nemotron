# task091_omni3_stage1_rl_config_portability_s1 - Task Knowledge

<!-- METADATA:SESSION=19 -->

## Knowledge Entries

1. assignment: fix named-user `/lustre/fs1/portfolios/coreai/users/aroshanghias` fallbacks in runnable Omni3 stage1 RL configs.
2. technical fact: `stage3_vision_rl/config/default.yaml` does not use this named-user fallback block and was intentionally left unchanged.
3. implementation choice: generated roots default to `${oc.env:NEMO_RUN_DIR,.}/output/omni3/...`; `CONTAINER` defaults to the same home-cache path already used by `run.env.container`.
4. test contract: tests should prove env override names remain first-choice, no-env defaults resolve portably, and `stage1_mpo/config/tiny.yaml` keeps `NUM_NODES=1` plus the tiny job-name fallback.
5. session 9 note: task096 work reused the same intern session bookkeeping path
   while implementing a Qwen eval repro gate remote-artifact PM verification
   guard.
6. session 10 note: PR #204 gate can fail on workspace task docs too; always
   run `git diff --check` after bookkeeping file edits before pushing.
7. session 11 note: generic Super3 RL defaults should avoid fixed tokenizer
   artifacts when `policy.model_name` is the selected checkpoint; use
   `${policy.model_name}` to keep model and tokenizer aligned by default.
8. session 12 note: data-quality audits that compute leakage/duplicate counters
   need an explicit fail path for production use; report-only remains useful
   for smoke fixtures, but strict callers should get a nonzero error.
9. session 13 note: Stage2 RL bridge `combined.jsonl` consumers should use the
   bridge manifest's `counts.val` boundary instead of a fixed holdout whenever
   the bridge emits train rows followed by validation rows.
10. session 14 note: RLVR bridge consumers run placeholder resolution before
    final local splitting, so auto holdout must be resolved from the original
    bridge input manifest before the resolved intermediate JSONL is split.
11. session 15 note: data-prep zip extraction should validate every archive
    member before writing any file, reject POSIX absolute paths, Windows drive
    paths, `..` components, and resolved targets outside the extraction root.
12. session 16 note: Stage1 RLVR train loading should fail fast if the
    NeMo-Gym datum converter is unavailable; local empty-datum fallbacks can
    drop bridge payloads and bypass the Qwen `<|im_end|>` stop contract.
13. session 17 note: RLHF preference registry rows can remain candidates while
    still carrying pinned Hugging Face revisions; synthetic unpinned required
    pref fixtures remain informational in the audit.
14. session 18 note: Omni3 RL data-prep source revisions should participate in
    both source materialization and cache identity; optional blend-level
    revision fields keep text RL pins explicit without breaking existing
    `DataBlend` users.
15. session 19 note: when Omni3 text data-prep sets `source_revision`, the
    configured `source_uri` must match at least one blend dataset row; otherwise
    URI drift can bypass the config/blend consistency guard.
