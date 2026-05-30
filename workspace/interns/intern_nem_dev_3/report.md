# intern_nem_dev_3 Report

## 2026-05-30 19:50:00 UTC - task217_mamba_causal_conv_train_stack_unblock_probe_s1

- Status: No-launch diagnostic evidence complete / ready for PM review
- Branch:
  `intern_nem_dev_3/task217_mamba_causal_conv_train_stack_unblock_probe_s1`
- Base: `1d037329f5a02cdc04f2a09a16e7342721be4c87`
- Artifact root:
  `/mnt/cephfs/data/processing/nemotron-live-validation/task217`
- Root cause:
  - Task216 used `/usr/local/bin/torchrun`, shebang `/usr/bin/python3`, with
    task209 Session 5 mamba `pip_target`, task209 Session 4 venv
    site-packages, and task216 repo `src` in `PYTHONPATH`.
  - In that exact context, `mamba_ssm==2.3.2.post1` and
    `selective_scan_cuda` import successfully.
  - `causal-conv1d` package metadata is missing; `causal_conv1d`,
    `causal_conv1d.causal_conv1d_interface`, and `causal_conv1d_cuda` are not
    importable.
  - `mamba_ssm.ops.triton.ssd_combined.causal_conv1d_fwd_function` is `None`,
    matching task216's `TypeError: 'NoneType' object is not callable`.
- Unblock recommendation:
  - Build/install compatible `causal-conv1d` into a task-owned contained target
    and prepend it to the task216 `PYTHONPATH`.
  - Candidate: `causal-conv1d==1.6.2.post1`; mamba metadata requires
    `causal-conv1d>=1.2.0`, README recommends `>=1.4.0`.
  - PM assigned dev_1 task218 to own the contained build/probe; task217 did not
    duplicate package build/install work.
- Key artifacts:
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/01_runtime_context_probe.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/02_exact_python_import_function_probe.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/03_mamba_source_and_artifact_search.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/04_venv_python_import_function_probe.log`
  - `/mnt/cephfs/data/processing/nemotron-live-validation/task217/logs/05_mamba_metadata_dependency_probe.log`
  - `workspace/tasks/task217_mamba_causal_conv_train_stack_unblock_probe_s1/validation_report.md`
- Boundaries:
  - No training launch, benchmark, endpoint, package install, shared/global env
    mutation, model copy/download, W&B/cluster deploy, artifact upload,
    main/master push, or self-merge.

## 2026-05-21 12:41:52 UTC - task026_m2_swe_multi_harness_s1

- Status: PR ready for PM gate
- Branch: `intern_nem_dev_3/task026_m2_swe_multi_harness_s1`
- Base SHA: `afabdeef959293f9391581b392b6856847362b24`
- Implementation SHA: `d5261f6c79e6aedc85756096dc8c9a0a8deb12b5`
- PR: https://github.com/songCNMS/Nemotron/pull/130
- Scope delivered:
  - Added sandbox-runnable SWE multi-harness registry beside `m1_swe2/openhands_loop.py`.
  - Preserved OpenHands/task070 routing metadata.
  - Declared OpenCode and Codex adapter symbols plus route metadata without importing external harness packages.
  - Registered the new harness registry in the unified data registry schema/index.
- Tests:
  - `PYTHONPATH=src python -m pytest tests/recipes/super3/test_swe_multi_harness.py tests/recipes/super3/test_unified_data_registry.py -q` -> 37 passed
  - `PYTHONPATH=src python -m pytest tests/recipes/super3/test_m1_swe2_data_bridge.py tests/recipes/super3/test_openhands_loop.py tests/recipes/super3/test_swe_multi_harness.py -q` -> 43 passed
  - `PYTHONPATH=src python scripts/validate_data_registries.py --quiet` -> passed
  - `PYTHONPATH=src python -m py_compile src/nemotron/recipes/super3/milestones/m1_swe2/swe_multi_harness.py src/nemotron/recipes/super3/milestones/data_registries/schema.py src/nemotron/recipes/super3/milestones/data_registries/unified_index_loader.py` -> passed
- Not run:
  - `python -m ruff check ...` -> blocked because `ruff` is not installed in this environment.
- Cluster-bound follow-up:
  - Real OpenCode/Codex adapter implementation.
  - Packaged OpenCode/Codex agent configs.
  - SIF/Docker/container-backed smoke for OpenHands/OpenCode/Codex harnesses.

## 2026-05-21 13:24:26 UTC - task027_m2_multilingual_if_code_s1

- Status: PR ready for PM gate
- Branch: `intern_nem_dev_3/task027_m2_multilingual_if_code_s1`
- Base SHA: `fb45b78d8280b04720f937e2a9a1c578f2effa60`
- Implementation SHA: `c350eabf0ed743a721f90a7553604eefcb247d71`
- PR: https://github.com/songCNMS/Nemotron/pull/132
- Scope delivered:
  - Added sandbox-runnable `multilingual_ifeval` and `multilingual_humaneval` environment rows.
  - Added converter/record contracts for multilingual IF and multilingual HumanEval-style rows.
  - Reused `multilingual_exact_or_contains` as the sandbox verifier fallback.
  - Recorded deferred judge-model and code-execution runtime metadata explicitly.
- Tests:
  - `PYTHONPATH=src python -m pytest tests/recipes/super3/test_multilingual_if_code_s1.py -q` -> 11 passed
  - `PYTHONPATH=src python -m pytest tests/recipes/super3/test_multilingual_if_code_s1.py tests/recipes/super3/test_aya_multilingual.py tests/recipes/super3/test_m0_data_env.py -q` -> 69 passed, 2 skipped
  - `PYTHONPATH=src python scripts/validate_data_registries.py --quiet` -> passed
  - `git diff --check` -> passed
  - `PYTHONPATH=src python -m py_compile src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py src/nemotron/recipes/super3/milestones/m0_data_env/run_m0_health_baseline.py` -> passed
- Cluster-bound follow-up:
  - Production multilingual IF judge model scoring.
  - Production multilingual code-execution verifier/runtime.
  - Source selection + revision pins for `m0_multilingual_ifeval` and `m0_multilingual_humaneval`.
  - SIF/Docker/cluster smoke for judge/runtime paths.

## 2026-05-21 14:11:03 UTC - task029_m2_safety_jailbreak_overrefusal_s1

- Status: PR ready for PM gate
- Branch: `intern_nem_dev_3/task029_m2_safety_jailbreak_overrefusal_s1`
- Base SHA: `0bbbd543b092bd54ab309db963b33fd03c62baa9`
- Implementation SHA: `cd32d5921022f700b8b0d979001345550b5ab4ed`
- PR: https://github.com/songCNMS/Nemotron/pull/136
- Scope delivered:
  - Added sandbox-runnable `safety_judge`, `jailbreak_resist`, and `over_refusal` environment rows.
  - Added converter/record contracts for general safety judging, jailbreak resistance, and over-refusal reduction rows.
  - Reused `safety_judge_stub` as the sandbox verifier fallback.
  - Recorded deferred judge-model/runtime metadata explicitly.
- Tests:
  - `PYTHONPATH=src python -m pytest tests/recipes/super3/test_safety_jailbreak_overrefusal_s1.py -q` -> 12 passed
  - `PYTHONPATH=src python -m pytest tests/recipes/super3/test_safety_jailbreak_overrefusal_s1.py tests/recipes/super3/test_nemotron_safety_reasoning.py tests/recipes/super3/test_m0_data_env.py -q` -> 79 passed, 2 skipped
  - `PYTHONPATH=src python scripts/validate_data_registries.py --quiet` -> passed
  - `git diff --check` -> passed
  - `PYTHONPATH=src python -m py_compile src/nemotron/recipes/super3/milestones/m0_data_env/prepare_m0_assets.py src/nemotron/recipes/super3/milestones/m0_data_env/run_m0_health_baseline.py` -> passed
- Judge/cluster blockers:
  - Real safety judge model selection and calibration.
  - Live judge inference path for safety, jailbreak, and over-refusal scoring.
  - Production benchmark source selection and revision pins.
  - SIF/Docker/cluster smoke for judge runtime paths.
