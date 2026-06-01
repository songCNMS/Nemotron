# task245_qwen_aime_v10_artifact_runbook_verify_s1 - Task Knowledge

<!-- METADATA:SESSION=3 -->

## Knowledge Entries

1. Remote debug runs happen on `NemTron`, and code must be synced to `/root` before debug.
2. Shared `/mnt/cephfs/data/processing/lei.song` files must never be deleted.
3. Runbook verification must keep 30B/8-GPU scale held until Qwen3-4B pilot evidence satisfies the same-harness non-regression gate.
4. For this workspace, the verified Qwen3-4B base path is `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`; task243 PR #319 head `61a12dd` now points the Qwen AIME gate at this path.
5. FT judgment remains blocked until task243 base artifacts exist with `summary.json`, `results.jsonl`, `command.txt`, and `endpoint_model_manifest.json`, then the FT run uses the identical AIME25 protocol.
6. task241 PR #320 head `5753713` is open/CLEAN and contains the V10 data-prep code/report; it is no longer a missing-publication blocker for task245.
7. task242 PR #321 head `12ee98c` is open/CLEAN and contains the Qwen3-4B V10 planner/smoke report, generated bundle paths, fail-closed decontamination checks, NemTron `/root` sync contract, and 30B hold.
8. Current task245 blockers are limited to: real heldout decontamination corpus/input, missing corrected AIME input/cache, no reachable Qwen3-4B endpoint, no base score artifacts, no candidate FT checkpoint/export/eval, and no 30B/8-GPU permission.
