# task266_qwen_aime_v11_runbook_repro_gate_s1 - Task Knowledge

<!-- METADATA:SESSION=1 -->

## Knowledge Entries

1. The V11 runbook must make artifact paths and gate dependencies explicit so a
   failed artifact like task255 cannot be promoted by ambiguity.
2. First measurable V11 go/no-go still compares a new valid FT candidate against
   accepted Qwen3-4B base `11/30` under the same corrected AIME harness.
3. `NemTron` debug requires code sync to `/root`; shared
   `/mnt/cephfs/data/processing/lei.song` files must not be deleted.
4. This task is reproducibility/runbook evidence only and cannot authorize
   training, eval, promotion, or 30B/8-GPU.
5. Session 1 branch is
   `intern_nemotron_worker_5/task266_qwen_aime_v11_runbook_repro_gate_s1`
   from `origin/main` at `513fefa1f1ace94302b56413769c78fb7224624c`.
6. Lead docs source for assignment is
   `origin/intern_nemotron_lead/session1-recovery-task-docs` at
   `81253415dd3285ce0eb56e69733d210742edcb50`.
7. Session 1 report path:
   `workspace/tasks/task266_qwen_aime_v11_runbook_repro_gate_s1/v11_runbook_repro_gate_report.md`;
   output copy:
   `/work-agents/intern_nemotron_worker_5/outputs/task266_qwen_aime_v11_runbook_repro_gate_s1/v11_runbook_repro_gate_report.md`;
   refreshed sha256
   `12f892f98ec57b696619be6615ad2454e6e7889529614af28c1f1f50b4dd933b`.
8. Current upstream V11 evidence remains incomplete: task262 is now #336
   MERGED at head `8fd3ff6065290b850c98db5f7abff91aa6880967`, merge commit
   `2ca6541c275d1eb64068e665af24147a796c818a`; `5e431f4` supplies static
   data/packing repair evidence plus fresh final-answer n-gram decontam PASS
   artifacts and output hashes, while `8fd3ff6` is metadata-only reconciliation;
   task263 is visible at
   `4af57e0e61703a063c1ef42def44119a7eea5cf9` but has no PR or base-load
   proof; task264 is #335 MERGED at
   `9d9285fd77820a5187440fbc2234dc36eb56942d` as
   `98e8aad39af9e705feed581e0ff9f8814073e2d8` with static canary/retention
   evidence, and task265 is visible only as branch
   `ca5ea1c405ef142ee51a43fcbab477a2958e48dc` plus worker_4 mailbox-only
   matrix refresh id `7e718a2c0ea746ed81352db5b5b6fe57`.
9. task262 final-answer n-gram scan evidence at #336 `5e431f4`, carried by
   exact head `8fd3ff6`: 200
   final-answer rows versus 560 heldout prompts, 112000 pair comparisons, 4
   overlap pairs, 1 informational pair, 0 blocker pairs, 0 rows with blocker
   overlap, max score 0.257143, and `decontaminate_math_rows` dropped 0 rows.
10. First measurable V11 go/no-go requires base-load/import proof, nonzero-LR
   training evidence, non-AIME canary pass, reviewer-readable artifacts, and
   same-harness AIME25 FT exact-normalized accuracy `>= 11/30`.
11. Task264 static readiness does not authorize live AIME comparison; same-harness
    AIME remains blocked until task262 data, task263 base-load proof, task265
    review, a V11 candidate artifact, and actual canary pass evidence exist.
