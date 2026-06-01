# task244_qwen_aime_v10_contam_regression_review_s1 - Task Knowledge

<!-- METADATA:SESSION=6 -->

## Knowledge Entries

1. Review must treat AIME25 prompts and labels as held-out only.
2. V8 failure was real AIME correctness regression on `aime_06`, not parser noise.
3. A 4B pilot that only proves scripts run is insufficient; it must be non-regressing against the same base or identify a concrete fix.
4. Initial task244 review found no reviewable task241/task242/task243 implementation PRs yet; their available remote heads only contain task/status docs.
5. Task245 PR #317 exists but currently contains task docs/status only, so it cannot yet verify artifact paths, runbook commands, or first go/no-go evidence readiness.
6. After the initial matrix, task243 PR #319 appeared with base-vs-FT gate code/protocol, but lead requested correction from `/mnt/3fs` to the required `/mnt/cephfs` Qwen3-4B checkpoint path before task244 should refresh the matrix or approve.
7. PR #319 head `61a12dd8b96e51785a3ece76d5883a419b30dd39` corrects the active Qwen3-4B base checkpoint/tokenizer path to `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507` and encodes a same-harness base-required, FT-at-least-base AIME25 gate. It still has no live base/FT score artifacts.
8. PR #320 head `57537133bed6bdd5773e6678b48086a8fc6a87b4` adds V10 data-prep logic and decontam tests. The AIME25-like prompt with answer `907` is used only as heldout/decontam corpus plus an input row removed from train/sidecar; the clean V10 prompt with answer `441` remains.
9. Task242 remains no-PR/hold, so 4B-first planner enforcement, fail-closed decontam wiring in runnable configs, and 30B/8-GPU hold controls are not yet independently reviewable.
10. PR #317 head `ba3c2a14efc8a710a504cbf601132a5b82d04bf7` has runbook evidence but still describes the old task243 `/mnt/3fs` path blocker, so it needs refresh before being used as current go/no-go guidance.
11. PR #321 head `12ee98ccf7475c2ee77a92b3f1390df06d9edcd0` supersedes the earlier task242 no-PR hold. It statically wires the Qwen3-4B V10 pilot to `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`, rejects missing/empty V10 decontam corpora and skip-flag use, guards placeholder corpus use in the generated local data-prep script, restricts V10 sync cleanup to task-owned `/root` paths, and keeps 30B/8-GPU planning held unless explicitly allowed after the 4B gate.
12. The #321 diff does not add concrete AIME25 heldout prompt text, labels, answer keys, `aime_06`, or answer `907`; it adds only generic heldout corpus strings and placeholder markers for planner tests/report.
13. PR #317 head `b8d3c98237a83008d08abb8e2a39bbe3aa5dc772` corrected the old task243 `/mnt/3fs` blocker to `/mnt/cephfs`, but is now stale on task242 because it still says no PR / old head. It remains hold until refreshed against #321.
14. PR #317 head `2ad67ed2a102e22cdbc65826c431d22bd5728867` now records #319/#320/#321 current state and removes the old task242 no-PR blocker. It is approved as a current static runbook/artifact map, but first Qwen3-4B go/no-go remains no-go/hold until real heldout decontam corpus/input, corrected AIME input/cache, endpoint, base artifacts, candidate FT checkpoint/export/eval, and 30B permission are available.
15. PR #318 was lead-approved and merged at `86fd05fbb1bb0b1c918a72c6680c10ea170d2798` after verifying exact head `e1bb5413d5ffc050e209a371122e2923ea2f322b`, base `main`, and CLEAN state. It is the merged independent static contamination/regression review artifact for #319/#320/#321/#317.
