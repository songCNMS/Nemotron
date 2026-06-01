# task244_qwen_aime_v10_contam_regression_review_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. Review must treat AIME25 prompts and labels as held-out only.
2. V8 failure was real AIME correctness regression on `aime_06`, not parser noise.
3. A 4B pilot that only proves scripts run is insufficient; it must be non-regressing against the same base or identify a concrete fix.
4. Initial task244 review found no reviewable task241/task242/task243 implementation PRs yet; their available remote heads only contain task/status docs.
5. Task245 PR #317 exists but currently contains task docs/status only, so it cannot yet verify artifact paths, runbook commands, or first go/no-go evidence readiness.
6. After the initial matrix, task243 PR #319 appeared with base-vs-FT gate code/protocol, but lead requested correction from `/mnt/3fs` to the required `/mnt/cephfs` Qwen3-4B checkpoint path before task244 should refresh the matrix or approve.
