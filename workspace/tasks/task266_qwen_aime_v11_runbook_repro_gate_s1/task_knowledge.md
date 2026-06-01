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
