# task245_qwen_aime_v10_artifact_runbook_verify_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. Remote debug runs happen on `NemTron`, and code must be synced to `/root` before debug.
2. Shared `/mnt/cephfs/data/processing/lei.song` files must never be deleted.
3. Runbook verification must keep 30B/8-GPU scale held until Qwen3-4B pilot evidence satisfies the same-harness non-regression gate.
