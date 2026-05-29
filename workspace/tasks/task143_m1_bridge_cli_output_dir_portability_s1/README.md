# task143_m1_bridge_cli_output_dir_portability_s1

<!-- METADATA:STATUS=InProgress,ASSIGNEE=intern_nem_dev_3 -->

## Scope

- Align M1 bridge/prep CLI default output directories with the run-directory
  contract by defaulting under `Path(os.environ.get("NEMO_RUN_DIR", ".")) /
  "output/super3/..."`.
- Cover RLHF, RLVR, SWE1, SWE2, Agentic SFT prep, and Agentic SFT training
  planner defaults.
- Preserve explicit `--output-dir` and `--save-dir` CLI overrides and all
  existing suffixes.
- Add focused static/import tests plus structured probes.

## Boundaries

- Static/import/config-only.
- No live HF dataset download, M0/M1 data prep, SFT packing, training, eval,
  endpoint call, W&B run, cluster job, artifact download, deployment, direct
  `main`/`master` push, or self-merge.

## Status

- Branch:
  `intern_nem_dev_3/task143_m1_bridge_cli_output_dir_portability_s1`
- Base: `802f7bee98579e5a9647813f5182bb048e1aa44b`
- PR: pending
