# task325_qwen_all_sft_m1_launcher_remediation_route_s1 - Task Knowledge

<!-- METADATA:SESSION=16 -->

## Knowledge Entries

1. Task315 found no safe current M1 launcher runtime route and 0/19 runnable
   rows.
2. The all-SFT objective still requires runnable M1 basket rows where possible
   and unavailable-row documentation where not possible.
3. This task does not authorize benchmark execution or model eval.
4. Task325 re-probed the current worker host under
   `/work-agents/intern_nemotron_worker_3/outputs/task325_qwen_all_sft_m1_launcher_remediation_route_s1/run_20260603T203449Z`.
   Default Python lacks `nemo_evaluator_launcher`, `nemo_evaluator`,
   `lm_eval`, `simple_evals`, `nemo_skills`, `bfcl_eval`, `tau2_bench`,
   `hle`, `livecodebench`, `scicode`, `ifbench`, and `ruler`.
5. Docker client exists, but `docker ps` cannot connect to
   `/var/run/docker.sock`; `sbatch`, `srun`, `singularity`, `apptainer`,
   `enroot`, and local `ltp` CLI are missing.
6. Historical task225 runtime venv imports `nemo-evaluator-launcher==0.2.5`
   and `nemo-evaluator==0.2.8`, but it remains launcher-only for this purpose
   because benchmark modules are missing and no working container/scheduler
   route is proven.
7. Repo mapping still has 14 exact M1 launcher mappings and 5 exact missing
   rows: `multichallenge`, `terminalbench`, `mcp_mark`, `tool_decathlon`, and
   `swe_bench_verified`. No substitutions are accepted for those missing rows.
8. Task325 disposition is `BLOCK_RUNTIME_CONFIRMED` with a later remediation
   route requiring lead-gated task-owned evaluator runtime plus working
   Docker/Slurm/alternate container backend or revalidated vm4vpn-style route,
   plus row-specific credentials/context proof.
9. Session 15 metadata correction did not change the report findings or
   artifacts. PR #387 remains the task325 docs/report vehicle; worker status
   must use allowed status values only, so the open-PR state is recorded as
   `Working` rather than `ReadyForPR`.
10. Session 16 merged PR #387 after lead release at exact head
    `e07ee3f9268b33658e18881c25a3d221bf2136ee`; merge commit is
    `a612ff4f3f09f55b3b5437e0b3b3a57fde976a3b`, mergedAt
    `2026-06-04T13:03:37Z`. This remains blocker docs only and authorizes no
    M1 row execution or runtime remediation.
