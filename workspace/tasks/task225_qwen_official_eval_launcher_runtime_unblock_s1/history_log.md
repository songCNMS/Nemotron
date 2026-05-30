# History Log

## 2026-05-30

- Created branch `intern_nem_dev_2/task225_qwen_official_eval_launcher_runtime_unblock_s1` from exact `origin/main` `1d037329f5a02cdc04f2a09a16e7342721be4c87`.
- Inventoried existing local, VPN, and NemTron environments read-only. None had `nemo-evaluator-launcher` in PATH or importable `nemo_evaluator_launcher`.
- Built local contained venv `/mnt/cephfs/data/processing/nemotron-live-validation/task225/runtime_venv` and installed `nemo-evaluator-launcher==0.2.5`.
- Validated `nemo_evaluator_launcher.api.functional.run_eval` import and signature, CLI `--help`, CLI `--version`, and packaged task listing.
- Probed the 14 `m1_full_basket_launcher_available` task names against the launcher mapping. All 14 resolved with exact packaged task definitions.
- Generated static raw launcher config `/mnt/cephfs/data/processing/nemotron-live-validation/task225/static_check/m1_launcher_available_raw_static_generic.yaml`.
- Ran no-endpoint launcher dry-run using the raw M1 subset config. It returned rc=0 and prepared sequential scripts under `/mnt/cephfs/data/processing/nemotron-live-validation/task225/eval_dry_run`.
- Verified the local product CLI can use the task runtime through `/work-agents/.venv/bin/python` plus the task-owned `sitecustomize.py` overlay. Product CLI dry-run for the task221 command shape returned rc=0.
- Confirmed VPN host `vm4vpn` has Docker access but cannot see `/mnt/cephfs/data/processing/nemotron-live-validation/task225`.
- Built a local wheelhouse with 110 wheels, staged it to `/home/leisong/nemotron-live-validation/task225` on VPN, and copied evidence manifests back to the local artifact root.
- Tried a VPN venv; blocked by missing `ensurepip` / `python3.12-venv`, with no system mutation attempted.
- Installed the staged wheelhouse offline into VPN task-owned `pip_target`; import, CLI version/help, Docker probe, and no-endpoint dry-run all passed.
- No SGLang launch, endpoint call, eval/benchmark run, process kill, model copy, W&B/cluster/deploy/artifact upload, product code edit, main/master push, or self-merge was performed.
