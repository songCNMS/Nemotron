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
   sha256 `67e3f70389759cb33b4cedd319144c52e4ad5130134bad67cb36ba9f188920f5`.
8. Current upstream V11 evidence is incomplete: task262 and task264 remote
   branches are acceptance/docs only, task263 has no visible remote branch/PR,
   and task265 has no diff from main. Therefore V11 execution remains
   HOLD/NO-GO even though task266 runbook docs are complete.
9. First measurable V11 go/no-go requires base-load/import proof, nonzero-LR
   training evidence, non-AIME canary pass, reviewer-readable artifacts, and
   same-harness AIME25 FT exact-normalized accuracy `>= 11/30`.
