# task315_qwen_all_sft_m1_launcher_runtime_unblock_s1 - Task Knowledge

<!-- METADATA:SESSION=4 -->

## Knowledge Entries

1. Task311 corrected-Qwen endpoint evidence is not equivalent to M1 launcher
   harness evidence.
2. Current reported blockers include missing launcher CLI, missing evaluator
   package, no Docker/Slurm on NemTron, and missing benchmark modules.
3. The next useful output is an exact runtime route or blocker, not ad hoc
   benchmark execution.
4. Full M1 rows require a later lead release after route review.
5. Task315 probe output root is
   `/work-agents/intern_nemotron_worker_2/outputs/task315_qwen_all_sft_m1_launcher_runtime_unblock_s1/run_20260603T190821Z`.
6. Current task315 disposition is `BLOCK_RUNTIME`: no local/NemTron/LTP
   launcher route is runnable now. Default Python lacks
   `nemo_evaluator_launcher`, `nemo_evaluator`, and benchmark modules;
   `/work-agents/.venv/bin/python` is missing; Docker daemon access fails; and
   `sbatch`/`srun`/`singularity`/`apptainer`/`enroot` are missing.
7. Historical task225 runtime at
   `/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv`
   has `nemo-evaluator-launcher==0.2.5` and `nemo-evaluator==0.2.8`, but is not
   a runnable task315 route because benchmark modules are missing and no
   working container/scheduler route is proven.
8. Task315 row matrix keeps task231/task071 mapping interpretation: 14 exact
   launcher mappings exist, while `multichallenge`, `terminalbench`,
   `mcp_mark`, `tool_decathlon`, and `swe_bench_verified` remain exact-task
   unavailable. Do not substitute MT-Bench, codec contamination checks,
   ToolTalk, or BFCL variants for those rows.
9. Lead gate for task315/#379 accepted `APPROVE_BLOCKER_DOCS / BLOCK_RUNTIME`
   at head `bd0f3202d8597189048cb84b5edcc3c19ddd3519` with comment
   `issuecomment-4615943606`; this approves blocker documentation only and
   authorizes no benchmark execution or new action.
10. Do not self-merge #379 unless a coordinator/authorized non-author path is
    explicitly provided.
11. Session 4 received new task319 assignment; task315 remains open/unmerged
    and no additional task315 action is authorized.
