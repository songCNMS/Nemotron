# task242_qwen_aime_v10_planner_smoke_s1 - Task Knowledge

<!-- METADATA:SESSION=2 -->

## Knowledge Entries

1. Qwen3-4B pilot/debug path is `/mnt/cephfs/data/stable/models/Qwen/Qwen3-4B-Instruct-2507`.
2. Any later Qwen3-30B-A3B scale-up must remain held until Qwen3-4B pilot AIME25 is non-regressing or identifies a concrete fix.
3. Project rule: code/debug runs happen on `NemTron`, code syncs to `/root` before debug, and shared `/mnt/cephfs/data/processing/lei.song` files must not be deleted.
4. Task242 generated smoke bundle path is `/work-agents/intern_nemotron_worker_2/outputs/task242_qwen_aime_v10_4b_pilot`; it is intentionally not a completed data/training artifact because the real held-out decontamination corpus and task241 V10 data-prep merge are still required.
