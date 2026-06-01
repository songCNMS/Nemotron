# task266_qwen_aime_v11_runbook_repro_gate_s1 - Task Knowledge

<!-- METADATA:SESSION=0 -->

## Knowledge Entries

1. The V11 runbook must make artifact paths and gate dependencies explicit so a
   failed artifact like task255 cannot be promoted by ambiguity.
2. First measurable V11 go/no-go still compares a new valid FT candidate against
   accepted Qwen3-4B base `11/30` under the same corrected AIME harness.
3. `NemTron` debug requires code sync to `/root`; shared
   `/mnt/cephfs/data/processing/lei.song` files must not be deleted.
4. This task is reproducibility/runbook evidence only and cannot authorize
   training, eval, promotion, or 30B/8-GPU.
