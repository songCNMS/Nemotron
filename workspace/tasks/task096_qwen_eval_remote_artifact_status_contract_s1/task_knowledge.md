# task096_qwen_eval_remote_artifact_status_contract_s1 - Task Knowledge

<!-- METADATA:SESSION=9 -->

## Knowledge Entries

1. assignment: remote qwen eval repro gate raw artifact references using
   `vm4vpn:` or `vpn:` must be verified by PM, not only by a local workspace
   check.
2. technical fact: `qwen_eval_repro_gate.py` already centralizes remote prefix
   detection in `is_remote_artifact_reference()` with
   `REMOTE_ARTIFACT_PREFIXES = ("vm4vpn:", "vpn:")`.
3. implementation choice: keep `VALID_ARTIFACT_CHECK_STATUSES` unchanged and
   add a contextual `requires_pm_verified` check only when raw artifact paths
   are remote.
4. test contract: focused tests must reject `local_workspace_verified` for both
   remote prefixes while accepting it for a real existing local artifact path.
