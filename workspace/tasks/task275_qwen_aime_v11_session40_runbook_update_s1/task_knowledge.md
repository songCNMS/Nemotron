# task275_qwen_aime_v11_session40_runbook_update_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. Session 40 clears only the prior runtime-route blocker for positive
   Bridge import/preflight proof.
2. The runbook must keep training, live AIME eval, promotion, task255 reuse,
   AIME2025 train data, and 30B/8-GPU held.
3. Coordinator Session 40 evidence root is
   `/work-agents/intern_nemotron_coordinator/outputs/session40_nemtron_nemo_install_probe_20260602T015146Z`;
   remote run root is
   `/root/task_coordinator_nemotron_coordinator_06b9acba/session40_nemo_install_probe_20260602T015146Z`.
4. Key pass markers are `TASK270_RUNTIME_SYMBOL_PREFLIGHT=PASS`, `IMPORT_DONE`,
   `BRIDGE_IMPORT_RC=0`, and `TASK270_FAIL_CLOSED_PREFLIGHT=PASS`.
5. Session 40 installed `nemo-toolkit==2.7.3` into NemTron user site
   `/root/.local/lib/python3.12/site-packages`, clearing the missing-`nemo`
   route for import/preflight proof only.
6. `artifact_inventory.sha256` has a stale self-entry; use
   `session40_evidence.sha256` plus non-self inventory checks for current proof
   validation unless the coordinator regenerates the inventory.
